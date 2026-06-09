"""Persistence helpers — Supabase + GitHub + gist writes.

Owns the side-effecting writes that complete a task:

* :func:`init_supabase` — Supabase client init for dev/prod
* :func:`upload_files_to_github` — push starter files into the template repo
* :func:`create_answer_github_repo` — create the (public) answer/solution repo
* :func:`upload_answer_files_to_repo` — push solution files + SOLUTION.md

B5 transactional-create lifecycle helpers:

* :func:`insert_draft_task`   — INSERT minimal draft row, return ``task_id``
* :func:`mark_task_ready`     — UPDATE status='ready' once artifacts exist
* :func:`mark_task_failed`    — UPDATE status='failed' on mid-flight failure
* :func:`delete_github_repo`  — best-effort cleanup of an orphaned repo

Module-level GitHub credentials are read once at import time.
"""
from __future__ import annotations

import json
import os
from typing import Dict

from github import Github
from supabase import Client, create_client

from infra.github_utils import create_github_repo, slugify, upload_files_batch
from infra.logger_config import logger


# GitHub credentials — read once at import. The rest of the package imports
# these constants instead of re-reading the environment per call.
GITHUB_UTKRUSHTAPPS_TOKEN = os.getenv("GITHUB_UTKRUSHTAPPS_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
GITHUB_GIST_TOKEN = os.getenv("GITHUB_GIST_TOKEN")


def init_supabase(env: str = "dev") -> Client:
    """Initialise a Supabase client for the dev or prod environment.

    Prefers the ``service_role`` key when present — it bypasses RLS, which
    is needed for the v1 task-builder tables (``conversations``,
    ``generation_jobs``, ``generated_scenarios``, ``templates``,
    ``task_template_match``) that carry ``service_role_all`` policies.
    Falls back to the anon key for environments where the service-role key
    isn't provisioned (CI smoke tests, contributors without prod access).
    """
    suffix = "DEV" if env == "dev" else ""
    url = os.getenv(f"SUPABASE_URL_APTITUDETESTS{suffix}")
    key = (
        os.getenv(f"SUPABASE_SERVICE_ROLE_KEY_APTITUDETESTS{suffix}")
        or os.getenv(f"SUPABASE_API_KEY_APTITUDETESTS{suffix}")
    )

    if not url or not key:
        raise ValueError(f"Missing Supabase credentials for environment: {env}")

    return create_client(url, key)


def fetch_existing_task_titles(
    competencies: list[dict],
    env: str = "dev",
    limit: int = 25,
) -> list[str]:
    """Return titles of existing tasks that share AT LEAST ONE
    (competency name, proficiency) with the input.

    Used by the task-generation prompt to tell the LLM which scenarios /
    domains have already been used, so it picks a different one.
    Filtering happens client-side because ``criterias`` is a jsonb
    array — Supabase's ``contains()`` operator on jsonb arrays is
    awkward across schema variants. The volume of tasks per competency
    is small (low hundreds), so the client-side filter is cheap.

    Returns:
        List of task titles (most recent first), capped at ``limit``.
        Returns ``[]`` on any Supabase error — the caller should treat
        an empty list as "no prior tasks to avoid".
    """
    try:
        sb = init_supabase(env)
        wanted = {
            (c.get("name"), (c.get("proficiency") or "").upper())
            for c in competencies
            if c.get("name")
        }
        if not wanted:
            return []

        rows = (
            sb.table("tasks")
            .select("task_blob, criterias, created_at")
            .order("created_at", desc=True)
            .limit(500)
            .execute()
        )
        titles: list[str] = []
        for row in rows.data or []:
            crits = row.get("criterias") or []
            row_pairs = {
                (c.get("name"), (c.get("proficiency") or "").upper())
                for c in crits
            }
            if not (wanted & row_pairs):
                continue
            blob = row.get("task_blob") or {}
            title = blob.get("title") or blob.get("name")
            if title:
                titles.append(title)
            if len(titles) >= limit:
                break
        return titles
    except Exception as exc:
        logger.warning(f"fetch_existing_task_titles failed (env={env}): {exc}")
        return []


def insert_draft_task(
    task_data_for_db: Dict,
    env: str = "dev",
) -> str:
    """B5 — INSERT the draft row before any GitHub call.

    The row is marked ``status='draft'``. Once GitHub artifacts exist, call
    :func:`mark_task_ready` to flip it to ``ready`` and patch in the resources.

    Returns:
        The newly-created ``task_id`` (uuid as string).

    Raises:
        Exception: when Supabase returns no row — fatal, caller aborts.
    """
    sb = init_supabase(env)
    draft = dict(task_data_for_db)
    draft["status"] = "draft"
    # Resources / gist are not known yet; default to whatever the caller
    # has so far. mark_task_ready will overwrite these.
    result = sb.table("tasks").insert(draft).execute()
    if not result.data:
        raise Exception("Failed to insert draft task row into Supabase")
    row = result.data[0]
    task_id = row.get("id") or row.get("task_id")
    if not task_id:
        raise Exception("Draft task row missing id/task_id field")
    logger.info("Inserted draft task row id=%s", task_id)
    return str(task_id)


def mark_task_ready(
    task_id: str,
    *,
    env: str = "dev",
    task_blob: Dict | None = None,
    solutions: Dict | None = None,
    eval_info: Dict | None = None,
    readme_content: Dict | None = None,
    is_shared_infra_required: bool | None = None,
) -> Dict:
    """B5 — flip a draft row to ``ready`` once all artifacts exist.

    Only patches the fields supplied; anything ``None`` is left untouched.
    The status flip happens atomically with the artifact fields so a reader
    never sees a ``ready`` row missing its ``task_blob.resources``.
    """
    update: Dict = {"status": "ready"}
    if task_blob is not None:
        update["task_blob"] = task_blob
    if solutions is not None:
        update["solutions"] = solutions
    if eval_info is not None:
        update["eval_info"] = eval_info
    if readme_content is not None:
        update["readme_content"] = readme_content
    if is_shared_infra_required is not None:
        update["is_shared_infra_required"] = is_shared_infra_required

    sb = init_supabase(env)
    result = sb.table("tasks").update(update).eq("task_id", task_id).execute()
    if not result.data:
        raise Exception(f"Failed to mark task {task_id} ready — row missing or unchanged")
    logger.info("Marked task %s ready", task_id)
    return result.data[0]


def mark_task_failed(
    task_id: str,
    *,
    env: str = "dev",
    error: str | None = None,
) -> None:
    """B5 — flip a draft / running row to ``failed`` on mid-flight error.

    ``error`` is stored on ``task_blob.error`` so the existing schema doesn't
    need an extra column. Best-effort: a failure here is logged and swallowed
    because we're already in an error path.
    """
    try:
        sb = init_supabase(env)
        update: Dict = {"status": "failed"}
        if error:
            update["task_blob"] = {"error": error[:2000]}
        sb.table("tasks").update(update).eq("task_id", task_id).execute()
        logger.info("Marked task %s failed", task_id)
    except Exception as exc:
        logger.error("Failed to mark task %s failed: %s", task_id, exc)


def delete_github_repo(repo_name: str) -> None:
    """B5 — best-effort cleanup. Used during mid-flight failure to delete
    a repo that was created but never had its starter files uploaded.

    Errors are logged and swallowed — the caller is already failing.
    """
    if not repo_name or not GITHUB_UTKRUSHTAPPS_TOKEN:
        return
    try:
        github = Github(GITHUB_UTKRUSHTAPPS_TOKEN)
        try:
            repo_obj = github.get_user().get_repo(repo_name)
        except Exception:
            if not REPO_OWNER:
                return
            repo_obj = github.get_repo(f"{REPO_OWNER}/{repo_name}")
        repo_obj.delete()
        logger.info("Cleaned up partial GitHub repo %s", repo_name)
    except Exception as exc:
        logger.warning("Could not delete partial GitHub repo %s: %s", repo_name, exc)


def upload_files_to_github(repo: str, code_data: Dict) -> None:
    """Upload the candidate's starter files to the GitHub template repo
    in a single commit.

    Failure mode: if the batch upload fails the repo is **deleted** to avoid
    leaving a half-populated repo on the org. (Phase B5 of the plan moves
    this clean-up to a structured ``draft → ready → failed`` lifecycle.)
    """
    try:
        github = Github(GITHUB_UTKRUSHTAPPS_TOKEN)
        try:
            repo_obj = github.get_user().get_repo(repo)
        except Exception:
            if REPO_OWNER:
                repo_obj = github.get_repo(f"{REPO_OWNER}/{repo}")
            else:
                raise Exception(
                    f"Could not find repository {repo}. "
                    "Please set REPO_OWNER environment variable."
                )

        main_branch = "main"
        files_to_upload = code_data.get("code_files", {})

        if not files_to_upload:
            logger.warning(f"No files to upload to repository {repo}")
            return

        success = upload_files_batch(
            repo_obj, files_to_upload, "Initial commit", main_branch,
        )

        if not success:
            logger.error(f"Failed to upload files in batch. Deleting repo {repo}...")
            try:
                repo_obj.delete()
                logger.info(f"Deleted repo {repo} due to upload failures.")
            except Exception as e:
                logger.error(f"Failed to delete repo {repo}: {str(e)}")
            raise Exception("Failed to upload files to GitHub in batch")

        logger.info(
            f"Successfully uploaded all {len(files_to_upload)} files to "
            f"repository {repo} in a single commit"
        )

    except Exception as e:
        logger.error(f"Error uploading LLM-generated files: {str(e)}")
        raise


def create_answer_github_repo(base_name: str) -> str:
    """Create a new GitHub repository for the answer/solution files.

    Public repo so the solution can be referenced; named ``<base>-answers``.
    """
    slugified_base = slugify(base_name)
    return create_github_repo(slugified_base + "-answers", is_public=True)


def upload_answer_files_to_repo(repo_name: str, answer_code_data: Dict) -> None:
    """Upload solution files + a generated ``SOLUTION.md`` to the answer repo.

    Empty/whitespace-only files are filtered out. Errors here do **not**
    propagate — they're logged and the main task creation continues, since
    the candidate-facing template repo + the DB row are the canonical
    deliverables; the answer repo is a side artifact.
    """
    try:
        if not answer_code_data or "files" not in answer_code_data:
            logger.info("No files provided in answer_code_data")
            return

        files = answer_code_data["files"]

        def is_empty_content(content) -> bool:
            if not content:
                return True
            if isinstance(content, str):
                return not content.strip()
            if isinstance(content, dict):
                return not any(content.values())
            return False

        empty_files = [p for p, c in files.items() if is_empty_content(c)]
        if empty_files:
            logger.info(f"Empty content found for files: {empty_files}")
            files = {p: c for p, c in files.items() if not is_empty_content(c)}

        processed_files: Dict[str, str] = {}
        for path, content in files.items():
            # GitHub API doesn't allow paths starting with /.
            clean_path = path.lstrip("/")
            if isinstance(content, dict):
                processed_files[clean_path] = json.dumps(content, indent=2)
            else:
                processed_files[clean_path] = content

        # Generated SOLUTION.md from the structured steps.
        if "steps" in answer_code_data and answer_code_data["steps"]:
            solution_md_content = "# Solution Steps\n\n"
            steps = answer_code_data["steps"]
            if isinstance(steps, list):
                for i, step in enumerate(steps, 1):
                    solution_md_content += f"{i}. {step}\n\n"
            else:
                solution_md_content += str(steps)
            processed_files["SOLUTION.md"] = solution_md_content

        logger.info(
            f"Uploading {len(processed_files)} files to answer repository: "
            f"{repo_name} in a single commit"
        )
        upload_files_to_github(repo_name, {"code_files": processed_files})

    except Exception as e:
        logger.error(f"Error uploading answer files to repo {repo_name}: {str(e)}")
        # Don't re-raise — main task creation must continue.
