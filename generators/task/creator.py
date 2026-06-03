"""Task creator — orchestrates the full task creation flow.

Pulls the focused modules together: load inputs, classify, run the retry
loop with eval critics + the E2B gate, generate solution code, persist to
GitHub + Supabase.

Lifted from ``multiagent.py.create_task`` unchanged in behaviour; the only
structural diff is that helpers come from focused modules
(``task_generation.evaluator``, ``.gate``, ``.persistence``,
``.runtime_resolver``, ``._clients``) instead of multiagent's module
globals.

Public surface:

* :func:`create_task` — the full create-task orchestration
* :func:`determine_task_type` — heuristic ``backend``/``frontend`` classifier
  used for the ``tasks.task_type`` text[] column
* :func:`generate_answer_code_and_steps` — generates the solution-code +
  step-by-step guide via the answer-code LLM
"""
from __future__ import annotations

import datetime
import json
import shutil
import traceback
from pathlib import Path
from typing import Dict, List

from infra.evals import MAX_EVAL_RETRIES, EvalGateError, LLMOutputTruncated
from infra.github_utils import create_github_template_repo, slugify
from infra.logger_config import logger
from infra.classifier.runtime import Competency
from infra.schemas import ANSWER_CODE_SCHEMA
from infra.utils import (
    create_gist_from_template,
    format_outcomes,
    format_pre_requisites,
    generate_task_with_code,
    has_shared_infra_files,
    load_relevant_scenarios,
    parse_markdown_to_json,
    read_json_file_robust,
    save_files_locally,
)

from generators.task._clients import (
    ANSWER_CODE_MODEL,
    openai_client,
    openai_via_portkey,
)
from generators.task.evaluator import (
    build_retry_feedback,
    is_task_hollow,
    run_evaluations,
)
from generators.task.gate import GateOutcome, run_gate_for_attempt
from generators.task.persistence import (
    GITHUB_GIST_TOKEN,
    GITHUB_UTKRUSHTAPPS_TOKEN,
    REPO_OWNER,
    create_answer_github_repo,
    init_supabase,
    upload_answer_files_to_repo,
    upload_files_to_github,
)
from generators.task.runtime_resolver import resolve_plan
from task_validation import BaseTaskDAO, TaskValidationError, TaskWriteError


# ---------------------------------------------------------------------------
# Heuristics + answer-code generation
# ---------------------------------------------------------------------------

_BACKEND_KEYWORDS = (
    "api", "database", "sql", "postgresql", "fastapi", "backend", "server",
    "orm", "authentication", "authorization", "rest", "microservice", "docker",
    "container", "deployment", "infrastructure", "security", "middleware",
)

_FRONTEND_KEYWORDS = (
    "react", "nextjs", "next.js", "typescript", "javascript", "frontend",
    "ui", "ux", "component", "routing", "client", "browser", "dom", "css",
    "html", "responsive", "seo", "accessibility", "state management",
)


def determine_task_type(competencies: List[Dict], task_data: Dict) -> str:
    """Keyword-score the competencies + task content to label the task
    ``"backend"`` or ``"frontend"``.

    Drives the ``tasks.task_type`` text[] column which the backend's
    ``/end_task_session`` handler consumes; defaults to ``"backend"`` on
    error or ties. Likely to be subsumed by the combo cache's structured
    fields in a follow-up phase.
    """
    try:
        text_to_check: list[str] = []
        for comp in competencies:
            text_to_check.append(comp.get("name", "").lower())
            text_to_check.append(comp.get("description", "").lower())
        text_to_check.extend([
            task_data.get("name", "").lower(),
            task_data.get("description", "").lower(),
            task_data.get("question", "").lower(),
        ])
        combined_text = " ".join(text_to_check)

        backend_score = sum(1 for k in _BACKEND_KEYWORDS if k in combined_text)
        frontend_score = sum(1 for k in _FRONTEND_KEYWORDS if k in combined_text)
        logger.info(
            f"Task type scoring - Backend: {backend_score}, Frontend: {frontend_score}"
        )

        return "frontend" if frontend_score > backend_score else "backend"

    except Exception as e:
        logger.error(f"Error determining task type: {str(e)}")
        return "backend"


def generate_answer_code_and_steps(task_data: Dict) -> Dict:
    """Generate fully-implemented solution files + a step-by-step guide.

    Returns ``{"files": {path: content, ...}, "steps": [...]}``. On any
    error returns an empty structure so the main task-creation flow can
    decide to ship a task without an answer rather than fail outright.
    """
    try:
        task_description = task_data.get("description", "")
        task_question = task_data.get("question", "")
        task_name = task_data.get("name", "")
        task_outcomes = task_data.get("outcomes", "")
        criterias = task_data.get("criterias", [])

        if criterias and isinstance(criterias, list):
            competency_names = [c.get("name", "") for c in criterias]
            competency_info = f"Competencies: {', '.join(competency_names)}"
        else:
            competency_info = "No specific competencies"

        # Build a starter-code section so the LLM knows which files exist in
        # the candidate template and writes a complete solution for every
        # one. Skip files that don't need a solution.
        code_files = task_data.get("code_files", {}) or {}
        skip_prefixes = (".env", ".gitignore", "README")
        skip_dirs = ("data/",)
        starter_blocks = []
        for path, content in code_files.items():
            if any(path.startswith(p) for p in skip_prefixes):
                continue
            if any(path.startswith(d) for d in skip_dirs):
                continue
            body = content if isinstance(content, str) else json.dumps(content)
            starter_blocks.append(f"### {path}\n```\n{body}\n```")
        starter_section = (
            "STARTER CODE FILES (the candidate sees these — produce a fully "
            "working solution for every listed path; do NOT invent unrelated "
            "files):\n\n" + "\n\n".join(starter_blocks)
            if starter_blocks
            else "STARTER CODE: (not provided — infer from the question)"
        )

        system_prompt = (
            "You are an expert engineer. Given the following assessment task, "
            "generate the fully implemented solution code files (with correct "
            "implementation) for all files the candidate is supposed to "
            "complete. Also, provide a step-by-step solution guide (as an "
            "array of strings) that explains how to implement the solution. "
            "The 'files' field must be an array of {path, content} objects "
            "covering EVERY non-trivial file in the starter code (skip "
            "README, .gitignore, .env.example, sample data). Each path must "
            "match the path used in the starter code, and content must be a "
            "full, correct, runnable implementation. The 'steps' field must "
            "be an array of clear, high-level, step-by-step instructions "
            "for a human to follow to implement the solution."
        )

        user_prompt = (
            f"TASK NAME: {task_name}\n"
            f"TASK TITLE: {task_data.get('title', '')}\n"
            f"TASK DESCRIPTION: {task_description}\n"
            f"QUESTION: {task_question}\n"
            f"EXPECTED OUTCOMES: {task_outcomes}\n"
            f"{competency_info}\n"
            "---\n"
            f"{starter_section}\n"
            "---\n"
            "Generate the fully implemented code files (one entry per starter "
            "file path that needs a solution), and a step-by-step solution guide."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Route via Portkey to OpenAI: schemas.py is Anthropic-compatible too,
        # but OpenAI's structured-output validator is more forgiving for the
        # array-of-{path,content} shape, and going via Portkey keeps
        # billing/observability consistent.
        response = openai_via_portkey.responses.create(
            model=ANSWER_CODE_MODEL,
            input=messages,
            reasoning={"effort": "medium"},
            text={
                "verbosity": "medium",
                "format": {
                    "type": "json_schema",
                    "name": ANSWER_CODE_SCHEMA["name"],
                    "schema": ANSWER_CODE_SCHEMA["schema"],
                    "strict": ANSWER_CODE_SCHEMA["strict"],
                },
            },
        )

        response_text = getattr(response, "output_text", None)
        if not response_text:
            logger.error("No output_text received from OpenAI Responses API")
            raise RuntimeError(
                "Failed to get output_text from OpenAI Responses API"
            )

        answer_data = json.loads(response_text)

        # Schema returns files as an array of {path, content}; convert to
        # the dict shape the rest of the pipeline expects.
        raw_files = answer_data.get("files", [])
        if isinstance(raw_files, list):
            files_dict: Dict[str, str] = {}
            for item in raw_files:
                if isinstance(item, dict) and "path" in item and "content" in item:
                    files_dict[item["path"]] = item["content"]
            answer_data["files"] = files_dict

        logger.info(
            f"Generated solution with {len(answer_data.get('files', {}))} "
            f"files and {len(answer_data.get('steps', []))} steps"
        )
        return answer_data

    except Exception as e:
        logger.error(f"Error generating answer code and steps: {str(e)}")
        return {"files": {}, "steps": []}


# ---------------------------------------------------------------------------
# The main orchestration
# ---------------------------------------------------------------------------

def create_task(
    competency_file: Path,
    background_file: Path,
    scenarios_file: Path | None = None,
    env: str = "dev",
) -> Dict:
    """Generate an intelligent assessment task.

    Loads inputs → resolves the plan → runs the generate / eval / gate retry
    loop → on first passing attempt: generates the answer code, creates the
    GitHub template + answer repos, creates the gist, stores the row in
    Supabase. Raises :class:`EvalGateError` when every attempt fails (no
    external artifacts are created in that case).

    Args:
        env: Supabase environment to store the task in — ``"dev"`` or ``"prod"``.
    """
    try:
        if scenarios_file is None:
            scenarios_file = (
                Path(__file__).parent.parent.parent / "utilities"
                / "input_collection" / "task_scenarios.json"
            )

        logger.info(f"Reading competencies from {competency_file}")
        competency_data = read_json_file_robust(competency_file)
        competencies = (
            competency_data if isinstance(competency_data, list)
            else [competency_data]
        )
        logger.info(f"Successfully loaded {len(competencies)} competencies")
        logger.info(f"Competency details: {competencies}")

        logger.info(f"Reading background from {background_file}")
        background = read_json_file_robust(background_file)

        created_at = datetime.datetime.now(datetime.timezone.utc)

        logger.info(f"Loading scenarios from: {scenarios_file}")
        scenarios = load_relevant_scenarios(competencies, scenarios_file)
        logger.info(f"Loaded {len(scenarios)} relevant scenarios")
        logger.info(f"Scenarios: {scenarios}")

        input_data = {
            "competencies": [
                {
                    "name": comp.get("name"),
                    "scope": comp.get("scope"),
                    "proficiency": comp.get("proficiency"),
                }
                for comp in competencies
            ],
            "background": background,
            "scenarios": scenarios,
        }
        # Retry loop gates everything downstream — GitHub repo / Gist /
        # Supabase row are only created when an attempt produces a
        # non-hollow candidate that clears both LLM eval critics AND the
        # E2B build/test gate.
        criterias = [{
            "name": comp.get("name"),
            "proficiency": comp.get("proficiency"),
            "competency_id": comp.get("competency_id") or comp.get("id"),
        } for comp in competencies]

        # Resolve the competency-set into a ResolvedPlan once, before the
        # retry loop. The plan carries (a) the classified TaskRuntime
        # (``kind`` routes the eval-critic personas) and (b) the resolved
        # template (gate boot target). Phase B1 of the plan plugs the combo
        # cache in behind resolve_plan(); this call site does not change.
        runtime_comps = [
            Competency(
                name=c.get("name"),
                proficiency=(c.get("proficiency") or "BASIC"),
            )
            for c in competencies if c.get("name")
        ]
        plan = resolve_plan(runtime_comps) if runtime_comps else None
        task_runtime = plan.task_runtime if plan else None
        if task_runtime:
            logger.info(
                f"task_runtime classified: runtime={task_runtime.runtime} "
                f"kind={task_runtime.kind} frameworks={task_runtime.frameworks} "
                f"datastores={task_runtime.datastores}"
            )
        eval_kind = task_runtime.kind if task_runtime else None

        max_attempts = MAX_EVAL_RETRIES + 1
        task_data = None
        eval_info = None
        last_failure: Dict = {}
        feedback = ""
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Task generation attempt {attempt}/{max_attempts}")
            try:
                candidate = generate_task_with_code(
                    openai_client, input_data, feedback=feedback,
                )
            except LLMOutputTruncated as exc:
                # F11: the model hit max_tokens mid-output. Feed back a tight
                # corrective message and retry.
                logger.warning(
                    f"Attempt {attempt}: LLM output truncated "
                    f"(partial length={len(exc.partial_text)}); retrying with "
                    f"shorter-response feedback"
                )
                last_failure = {
                    "task_eval": {"pass": False, "issues": ["LLM output truncated by max_tokens"]},
                    "code_eval": {"pass": False, "issues": ["no code generated — response cut off"]},
                }
                feedback = (
                    "PREVIOUS ATTEMPT WAS CUT OFF mid-JSON because the response "
                    "exceeded the token budget. Produce the SAME corrected task "
                    "JSON but keep the response shorter: trim verbose comments, "
                    "condense the README, prefer concise code over exhaustive "
                    "examples. The output MUST end with a valid closing brace "
                    "for the top-level JSON object."
                )
                continue
            candidate.setdefault("code_files", {})
            candidate["criterias"] = criterias

            hollow, reasons = is_task_hollow(candidate)
            if hollow:
                logger.warning(
                    f"Attempt {attempt}: hollow output ({', '.join(reasons)}); "
                    f"regenerating with corrective feedback"
                )
                last_failure = {
                    "task_eval": {"pass": False, "issues": reasons},
                    "code_eval": {"pass": False, "issues": ["task_data hollow before eval"]},
                }
                feedback = build_retry_feedback(reasons, None)
                continue

            logger.info("Running task evaluations")
            candidate_eval = run_evaluations(candidate, kind=eval_kind)
            last_failure = candidate_eval
            t_pass = candidate_eval["task_eval"]["pass"]
            c_pass = candidate_eval["code_eval"]["pass"]
            if t_pass and c_pass:
                # Deterministic E2B build/test gate (F12). run_gate_for_attempt
                # encapsulates the policy; the loop just acts on the outcome.
                gate_outcome, gate_feedback = run_gate_for_attempt(
                    plan, candidate, candidate_eval, attempt,
                )
                if gate_outcome == GateOutcome.RETRY:
                    last_failure = candidate_eval
                    feedback = gate_feedback
                    continue
                task_data = candidate
                eval_info = candidate_eval
                logger.info(
                    f"Attempt {attempt}: evals passed - proceeding to storage"
                )
                break

            logger.warning(
                f"Attempt {attempt}: evals failed "
                f"(task_eval.pass={t_pass}, code_eval.pass={c_pass}); "
                f"will retry with feedback if budget remains"
            )
            feedback = build_retry_feedback([], candidate_eval)

        if task_data is None or eval_info is None:
            raise EvalGateError(max_attempts, last_failure)

        # ────────────────────────── persistence ─────────────────────────────
        task_type = determine_task_type(competencies, task_data)
        logger.info(f"Determined task type: {task_type}")

        logger.info("Generating solution code and steps")
        solutions_data = generate_answer_code_and_steps(task_data)

        repo_name_base = (
            task_data.get("resources", {}).get("github_repo", "").split("/")[-1]
        )
        if not repo_name_base:
            repo_name_base = slugify(task_data.get("name", "assessment-task"))
        # GitHub repo names cap at ~100 chars; keep well below that.
        if len(repo_name_base) > 50:
            repo_name_base = repo_name_base[:50].rstrip("-")

        logger.info("Creating public GitHub template repository")
        repo_name = create_github_template_repo(repo_name_base, is_private=True)
        github_repo_url = f"https://github.com/{REPO_OWNER}/{repo_name}"

        logger.info("Creating answer repository")
        # ``-answers`` (8 chars) gets appended — keep the base ≤42.
        answer_base_name = task_data.get("name", "assessment-task")
        if len(answer_base_name) > 42:
            answer_base_name = answer_base_name[:42].rstrip("-")
        answer_repo_name = create_answer_github_repo(answer_base_name)
        answer_repo_url = f"https://github.com/{REPO_OWNER}/{answer_repo_name}"

        logger.info("Uploading solution files to answer repository")
        upload_answer_files_to_repo(answer_repo_name, solutions_data)

        solutions_for_db = {
            "steps": solutions_data.get("steps", []),
            "answer_repo": answer_repo_url,
        }

        if "resources" not in task_data:
            task_data["resources"] = {}
        task_data["resources"]["github_repo"] = github_repo_url

        logger.info("Saving files locally...")
        local_task_dir = save_files_locally(repo_name, task_data)
        logger.info(f"Files saved locally to: {local_task_dir}")

        logger.info("Uploading files to GitHub repository...")
        upload_files_to_github(repo_name, task_data)

        gist_url = None
        if GITHUB_GIST_TOKEN:
            try:
                gist_url = create_gist_from_template(
                    repo_url=github_repo_url,
                    repo_token=GITHUB_UTKRUSHTAPPS_TOKEN,
                    gist_token=GITHUB_GIST_TOKEN,
                    description=task_data.get("name", repo_name),
                    public=False,
                )
                if gist_url:
                    task_data["resources"]["gist_url"] = gist_url
                    logger.info(f"Gist created: {gist_url}")
            except Exception as e:
                logger.warning(f"Gist creation skipped or failed: {e}")
        else:
            logger.warning("No GITHUB_GIST_TOKEN for gist; skipping gist creation")

        logger.info("Storing task in Supabase...")
        # Drive is_shared_infra_required purely from whether the generated
        # repo carries Docker / docker-compose artifacts. The previous
        # heuristic marked every "backend" task True regardless of Docker,
        # which flagged library-only tasks (LangChain / LlamaIndex /
        # pure-Python) as needing a sandbox they can't actually use.
        code_data = task_data.get("code_files", {})
        has_docker = has_shared_infra_files(code_data)
        is_shared_infra_required = bool(has_docker)
        logger.info(
            f"Setting is_shared_infra_required to {is_shared_infra_required} "
            f"(task_type: {task_type}, has_docker: {has_docker})"
        )

        task_data_for_db = {
            "created_at": created_at.isoformat(),
            "pre_requisites": format_pre_requisites(task_data.get("pre_requisites", "")),
            "answer": task_data.get("answer", ""),
            "criterias": task_data["criterias"],
            "is_deployed": False,
            "task_blob": {
                "title": task_data.get("title", "") or task_data.get("name", ""),
                "definitions": task_data.get("definitions", {}),
                "hints": task_data.get("hints", ""),
                "resources": dict(
                    {"github_repo": github_repo_url},
                    **({"github_gist": gist_url} if gist_url else {}),
                ),
                "outcomes": format_outcomes(task_data.get("outcomes", "")),
                "question": task_data.get("question", ""),
                "short_overview": format_outcomes(task_data.get("short_overview", "")),
            },
            "is_shared_infra_required": is_shared_infra_required,
            "readme_content": parse_markdown_to_json(code_data.get("README.md", "")),
            "eval_info": eval_info,
            "solutions": solutions_for_db,
            # ``task_type`` is a text[] consumed by the backend's
            # /end_task_session handler — if it's empty/missing the handler
            # 400s before queueing kill.sh / repo cleanup, leaving droplets
            # dirty. Default to ['BUILD']; PR-review and design-review flows
            # set their own values.
            "task_type": ["BUILD"],
        }

        supabase = init_supabase(env)
        try:
            supabase_task = BaseTaskDAO(supabase).validate_and_insert(
                task_data_for_db, env=env
            )
        except (TaskValidationError, TaskWriteError) as e:
            logger.error(str(e))
            raise

        task_id = supabase_task.get("task_id") or supabase_task.get("id")
        task_data.update(supabase_task)
        task_data["task_id"] = task_id

        # Optionally rename local directory to use actual task ID.
        try:
            new_local_task_dir = local_task_dir.parent / str(task_id)
            if local_task_dir != new_local_task_dir:
                shutil.move(str(local_task_dir), str(new_local_task_dir))
                logger.info(
                    f"Renamed local directory to use task ID: {new_local_task_dir}"
                )
        except Exception as e:
            logger.info(f"Could not rename local directory to task ID: {str(e)}")

        return task_data

    except EvalGateError:
        # Distinct from generic failures — nothing was committed; the caller
        # can decide whether to skip the combo or schedule manual review.
        logger.error(
            "Eval gate rejected the task — no GitHub repo or Supabase row was created."
        )
        raise
    except Exception as e:
        logger.error(f"Error in create_task function: {str(e)}")
        logger.error(traceback.format_exc())
        raise Exception(f"Task creation failed: {str(e)}")
