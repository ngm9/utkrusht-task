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
    delete_github_repo,
    fetch_existing_task_titles,
    init_supabase,
    insert_draft_task,
    mark_task_failed,
    mark_task_ready,
    upload_answer_files_to_repo,
    upload_files_to_github,
)
from generators.task.runtime_resolver import resolve_plan
from task_quality import run_quality_for_attempt
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
# Scenario resolution
# ---------------------------------------------------------------------------

def resolve_scenarios(
    competencies: List[Dict],
    scenarios_file: Path,
    *,
    env: str = "dev",
) -> List[str]:
    """Load the candidate scenario pool for a competency combo.

    DB-first (``generated_scenarios`` keyed by combo + proficiency), falling
    back to the JSON file for combos not yet backfilled into the DB. Shared
    by :func:`create_task` (to feed the generator) and the orchestrator's
    scenario stage (to surface the selectable list to the human).
    """
    from generators.scenarios import repository as scenario_repo
    from infra.utils import build_scenario_key

    combo_key = build_scenario_key(competencies)
    proficiency = (
        competencies[0].get("proficiency", "BASIC").upper()
        if competencies else "BASIC"
    )
    scenarios = scenario_repo.load_scenarios_for_combo(
        env=env, combo_key=combo_key, proficiency=proficiency,
    )
    if scenarios:
        logger.info(
            "Loaded %d scenarios from DB for key=%r prof=%s",
            len(scenarios), combo_key, proficiency,
        )
    else:
        logger.info(f"DB returned no scenarios; falling back to JSON: {scenarios_file}")
        scenarios = load_relevant_scenarios(competencies, scenarios_file)
        logger.info(f"Loaded {len(scenarios)} relevant scenarios from JSON")
    return scenarios


# ---------------------------------------------------------------------------
# The main orchestration
# ---------------------------------------------------------------------------

def create_task(
    competency_file: Path,
    background_file: Path,
    scenarios_file: Path | None = None,
    env: str = "dev",
    selected_scenarios: List[str] | None = None,
) -> Dict:
    """Generate an intelligent assessment task.

    Loads inputs → resolves the plan → runs the generate / eval / gate retry
    loop → on first passing attempt: generates the answer code, creates the
    GitHub template + answer repos, creates the gist, stores the row in
    Supabase. Raises :class:`EvalGateError` when every attempt fails (no
    external artifacts are created in that case).

    Args:
        env: Supabase environment to store the task in — ``"dev"`` or ``"prod"``.
        selected_scenarios: When provided (the scenario(s) a human picked in
            the UI), the generator uses exactly these and skips the pool
            lookup. A single entry hard-locks generation to that scenario.
            When ``None``/empty, the full candidate pool is resolved and the
            scenario-lock prompt picks one.
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

        # Human-in-the-loop: when the caller passes an explicit selection
        # (the scenario the user picked in the UI), use exactly that and skip
        # the pool lookup — the generator is then hard-locked to it. Otherwise
        # resolve the candidate pool (DB-first, JSON fallback) and let the
        # scenario-lock prompt pick one.
        if selected_scenarios:
            scenarios = list(selected_scenarios)
            logger.info(
                "Using %d human-selected scenario(s); skipping pool lookup",
                len(scenarios),
            )
        else:
            scenarios = resolve_scenarios(competencies, scenarios_file, env=env)
        logger.info(f"Scenarios: {scenarios}")

        existing_titles = fetch_existing_task_titles(competencies, env=env)
        if existing_titles:
            logger.info(
                f"Found {len(existing_titles)} existing tasks for this competency — "
                f"will instruct LLM to avoid duplicating: {existing_titles}"
            )

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
            "existing_task_titles": existing_titles,
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
        # retry loop. The plan carries (a) the match decision (template_id
        # + persona — persona routes the eval-critic personas) and (b) the
        # hydrated template (gate boot target).
        runtime_comps = [
            Competency(
                name=c.get("name"),
                proficiency=(c.get("proficiency") or "BASIC"),
            )
            for c in competencies if c.get("name")
        ]
        plan = resolve_plan(runtime_comps) if runtime_comps else None
        match = plan.match if plan else None
        template = plan.template if plan else None
        if match:
            logger.info(
                f"resolve_plan matched: template_id={match.template_id} "
                f"persona={match.persona} confidence={match.confidence:.2f}"
            )
            if match.no_match_reason:
                logger.info(
                    f"  no_match: {match.no_match_reason} "
                    f"missing={match.missing_capabilities} "
                    f"suggested={match.suggested_template}"
                )
        eval_persona = match.persona if match else None

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
                # Hollow candidates have nothing useful to patch — feed the
                # canonical-keys reminder only; don't echo the empty JSON.
                feedback = build_retry_feedback(reasons, None)
                continue

            logger.info("Running task evaluations")
            # Thread `scenarios` into the eval critic so Criterion 6
            # (DOMAIN ALIGNMENT) can detect drift — task invented a new
            # domain not present in the scenarios pool.
            candidate_eval = run_evaluations(
                candidate, persona=eval_persona, scenarios=scenarios,
            )
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

                # Content-quality eval (spec 003) — single LLM call judges
                # the candidate AND rewrites every failing field in place
                # (title shape, short_overview shape + count, bullet
                # hygiene, question length, framing + relevance). Autofix,
                # not a retry-gate: the (possibly-patched) candidate moves
                # straight to persistence. Infra errors during the call
                # propagate up and abort the attempt without artifacts.
                candidate, quality_report = run_quality_for_attempt(
                    candidate, attempt,
                )
                if quality_report.rewrites_applied:
                    logger.info(
                        f"Attempt {attempt}: quality eval autofixed "
                        f"{len(quality_report.rewrites_applied)} field(s): "
                        f"{sorted(quality_report.rewrites_applied.keys())}"
                    )

                task_data = candidate
                eval_info = candidate_eval
                logger.info(
                    f"Attempt {attempt}: evals + gate passed (quality applied) - proceeding to storage"
                )
                break

            logger.warning(
                f"Attempt {attempt}: evals failed "
                f"(task_eval.pass={t_pass}, code_eval.pass={c_pass}); "
                f"will retry with feedback if budget remains"
            )
            # Pass the failing candidate JSON so the next attempt patches
            # this concrete output instead of regenerating a fresh task with
            # a different scenario / different bugs.
            feedback = build_retry_feedback([], candidate_eval,
                                            prior_candidate=candidate)

        if task_data is None or eval_info is None:
            raise EvalGateError(max_attempts, last_failure)

        # ────────────────────────── persistence (B5) ─────────────────────────
        # New lifecycle: INSERT draft → build GitHub artifacts → UPDATE ready.
        # Any failure between INSERT and UPDATE leaves the row marked 'failed'
        # and best-effort cleans up the partial GitHub repos so the reconciler
        # has a clear surface to scan.
        task_type = determine_task_type(competencies, task_data)
        logger.info(f"Determined task type: {task_type}")

        logger.info("Generating solution code and steps")
        solutions_data = generate_answer_code_and_steps(task_data)

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

        # Step 1 — INSERT the minimal draft row, get task_id BEFORE any
        # external side effect.
        draft_payload = {
            "created_at": created_at.isoformat(),
            "pre_requisites": format_pre_requisites(task_data.get("pre_requisites", "")),
            "answer": task_data.get("answer", ""),
            "criterias": task_data["criterias"],
            "is_deployed": False,
            "task_blob": {
                "title": task_data.get("title", "") or task_data.get("name", ""),
                "definitions": task_data.get("definitions", {}),
                "hints": task_data.get("hints", ""),
                # resources patched in by mark_task_ready once repos exist.
                "resources": {},
                "outcomes": format_outcomes(task_data.get("outcomes", "")),
                "question": task_data.get("question", ""),
                "short_overview": format_outcomes(task_data.get("short_overview", "")),
            },
            "is_shared_infra_required": is_shared_infra_required,
            "task_type": ["BUILD"],
        }
        # Draft→ready lifecycle (branch design): insert a draft row first so a
        # row survives partial artifact-build failure; mark_task_ready patches
        # resources later. main's BaseTaskDAO.validate_and_insert (single,
        # strict insert) is brought in by this merge but wired in separately
        # (stage 2: validation layered into the draft→ready path).
        task_id = insert_draft_task(draft_payload, env=env)
        task_data["task_id"] = task_id

        # Step 2 — build the GitHub artifacts under a try/except that
        # marks the row failed + cleans up partial repos.
        repo_name: str | None = None
        answer_repo_name: str | None = None
        local_task_dir = None
        try:
            repo_name_base = (
                task_data.get("resources", {}).get("github_repo", "").split("/")[-1]
            )
            if not repo_name_base:
                repo_name_base = slugify(task_data.get("name", "assessment-task"))
            if len(repo_name_base) > 50:
                repo_name_base = repo_name_base[:50].rstrip("-")

            logger.info("Creating public GitHub template repository")
            repo_name = create_github_template_repo(repo_name_base, is_private=True)
            github_repo_url = f"https://github.com/{REPO_OWNER}/{repo_name}"

            logger.info("Creating answer repository")
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

            task_data.setdefault("resources", {})
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

            # Step 3 — flip the row to ready with the final payload.
            ready_task_blob = {
                "title": draft_payload["task_blob"]["title"],
                "definitions": draft_payload["task_blob"]["definitions"],
                "hints": draft_payload["task_blob"]["hints"],
                "resources": dict(
                    {"github_repo": github_repo_url},
                    **({"github_gist": gist_url} if gist_url else {}),
                ),
                "outcomes": draft_payload["task_blob"]["outcomes"],
                "question": draft_payload["task_blob"]["question"],
                "short_overview": draft_payload["task_blob"]["short_overview"],
            }

            ready_row = mark_task_ready(
                task_id,
                env=env,
                task_blob=ready_task_blob,
                solutions=solutions_for_db,
                eval_info=eval_info,
                readme_content=parse_markdown_to_json(code_data.get("README.md", "")),
                is_shared_infra_required=is_shared_infra_required,
            )

            # task_competencies junction — non-fatal on individual failure.
            sb = init_supabase(env)
            for criteria in task_data["criterias"]:
                competency_id = criteria.get("competency_id")
                if competency_id:
                    try:
                        sb.table("task_competencies").insert({
                            "task_id": task_id,
                            "competency_id": competency_id,
                        }).execute()
                    except Exception as e:
                        logger.error(
                            f"Failed to insert task-competency relationship: {str(e)}"
                        )

            task_data.update(ready_row)
            task_data["task_id"] = task_id

            # Optionally rename local directory to use actual task ID.
            if local_task_dir is not None:
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
        except Exception as build_exc:
            logger.error(
                "Mid-flight failure after draft INSERT for task %s: %s",
                task_id, build_exc,
            )
            mark_task_failed(task_id, env=env, error=str(build_exc))
            for partial in (repo_name, answer_repo_name):
                if partial:
                    delete_github_repo(partial)
            raise

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
