"""Persistence helpers — Supabase + GitHub + gist writes.

Owns the side-effecting writes that complete a task:

* :func:`init_supabase` — Supabase client init for dev/prod
* :func:`upload_files_to_github` — push starter files into the template repo
* :func:`create_answer_github_repo` — create the (public) answer/solution repo
* :func:`upload_answer_files_to_repo` — push solution files + SOLUTION.md

Module-level GitHub credentials are read once at import time.

The transactional-create + reconciler from plan phase B5 (insert row first,
then artifacts, then mark ready; cleanup on failure) lands here in a
follow-up step.
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
    """Initialise a Supabase client for the dev or prod environment."""
    if env == "dev":
        url = os.getenv("SUPABASE_URL_APTITUDETESTSDEV")
        key = os.getenv("SUPABASE_API_KEY_APTITUDETESTSDEV")
    else:
        url = os.getenv("SUPABASE_URL_APTITUDETESTS")
        key = os.getenv("SUPABASE_API_KEY_APTITUDETESTS")

    if not url or not key:
        raise ValueError(f"Missing Supabase credentials for environment: {env}")

    return create_client(url, key)


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
