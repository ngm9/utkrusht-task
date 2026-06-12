import json
import os
import re

import httpx
import openai
from openai import OpenAI
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders

from infra.logger_config import logger
from infra.schemas import EVAL_RESPONSE_SCHEMA
from infra.tracing.client import trace_client

# Model configuration for evaluations.
# Routed via Portkey → OpenAI because EVAL_MODEL is an OpenAI model name and
# the openai_client passed in from multiagent.py points at Portkey → Anthropic
# (which 404s on this model name).
EVAL_MODEL = os.getenv("EVAL_MODEL", "gpt-5-nano-2025-08-07")

eval_openai_client = trace_client(
    openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=PORTKEY_GATEWAY_URL,
        default_headers=createHeaders(
            provider="openai",
            api_key=os.environ.get("PORTKEY_API_KEY"),
        ),
        timeout=httpx.Timeout(None),
    ),
    provider="openai",
)

def clean_llm_json_response(response: str) -> str:
    """Clean LLM response to extract valid JSON"""
    try:
        response = response.strip()
        start = response.find('{')
        end = response.rfind('}') + 1
        
        if start != -1 and end > start:
            return response[start:end]
        
        return response
    except Exception as e:
        logger.error(f"Error cleaning LLM response: {str(e)}")
        return response

MAX_EVAL_RETRIES = 2


class EvalGateError(Exception):
    """Raised when the eval gate rejects a generated task after all retries.

    Carries the last evaluator verdicts so the caller can surface them. The
    presence of this exception means the task was NOT persisted to GitHub or
    Supabase — callers must NOT swallow it as success.
    """

    def __init__(self, attempts: int, last_eval_info: dict | None) -> None:
        self.attempts = attempts
        self.last_eval_info = last_eval_info or {}
        task_pass = self.last_eval_info.get("task_eval", {}).get("pass")
        code_pass = self.last_eval_info.get("code_eval", {}).get("pass")
        super().__init__(
            f"eval gate rejected after {attempts} attempt(s) "
            f"(last verdicts: task_eval.pass={task_pass}, code_eval.pass={code_pass})"
        )


class LLMOutputTruncated(Exception):
    """Raised when the generation LLM hit its max_tokens cap mid-output.

    Distinct from a generic parse error because the cause + fix are specific:
    the JSON is partial because we ran out of completion-token budget, not
    because the LLM produced malformed output. Caller (multiagent.create_task)
    catches this in its retry loop and feeds back "your last reply was cut off
    — keep the response shorter and close all braces".
    """

    def __init__(self, partial_text: str, attempt: int) -> None:
        self.partial_text = partial_text
        self.attempt = attempt
        super().__init__(
            f"LLM output truncated at attempt {attempt} "
            f"(partial response length: {len(partial_text)} chars)"
        )


# ----------------------------------------------------------------------
# Persona prompts — keyed by TaskTemplateMatch.persona
# ----------------------------------------------------------------------
#
# The eval critic gets a domain-specific "reviewer persona" prepended to its
# generic checklist. A senior DBA notices a missing NOT NULL on a junction-
# table FK that a generic reviewer skims past; a senior MLE catches a chunking
# strategy that conflicts with the retrieval question; an SDET notices test
# isolation problems that look fine to a backend reviewer.
#
# Same prompt model (gpt-5-nano), same JSON schema, same call shape — the only
# delta is the persona block prepended before the generic TASK_EVAL_PROMPT /
# CODE_EVAL_PROMPT body.
#
# Keys must match values in the matched template's ``personas`` array — the
# classifier guarantees ``match.persona`` is one of those strings. Add new
# entries here when a new template introduces a new persona name.

PERSONA_PROMPTS: dict[str, str] = {
    "backend": (
        "You are a senior backend engineer with 10+ years of experience shipping "
        "production services. Focus your review on: correctness of the request "
        "lifecycle, input validation, error handling at I/O boundaries, status-code "
        "semantics, and whether the candidate is asked to do realistic backend work "
        "(not toy CRUD)."
    ),
    "data": (
        "You are a senior backend / data engineer who writes one-off scripts and "
        "batch jobs in production. Focus your review on: data-flow correctness, "
        "transactional boundaries when DBs are involved, retries on transient "
        "failures, and idempotency. Reject toy examples that don't reflect real "
        "operational work."
    ),
    "mobile": (
        "You are a senior mobile engineer (Flutter, React Native, native iOS/"
        "Android). Focus your review on: UI lifecycle (rebuild costs, controller "
        "disposal), state management (Riverpod/Provider/Redux), offline-first "
        "behaviour and cache TTL, and concurrency around network calls. Reject "
        "tasks that ignore the offline/poor-connectivity reality of mobile."
    ),
    "frontend": (
        "You are a senior UX engineer. Focus your review on: accessibility "
        "(semantic HTML, ARIA, keyboard navigation), responsive layout behaviour, "
        "focus management, and whether the candidate is asked to write user-facing "
        "code rather than just style boilerplate."
    ),
    "sdet": (
        "You are a senior SDET. Focus your review on: test isolation (no shared "
        "state between tests), assertion quality (testing visible behaviour vs "
        "implementation details), fixture hygiene, deterministic timing (no fixed "
        "sleeps), and whether the test would actually catch the bug being asked "
        "about."
    ),
    "dba": (
        "You are a senior database administrator. Focus your review on: schema "
        "normalisation (3NF unless denormalisation is deliberate), NOT NULL "
        "discipline on FK columns, index coverage for the predicates the queries "
        "actually use, query-plan implications, and whether the task rewards good "
        "schema design over rote SQL writing."
    ),
    "mle": (
        "You are a senior ML engineer specialising in retrieval-augmented systems "
        "and LLM application design. Focus your review on: retrieval setup "
        "(chunking strategy, embedding model fit, top-k), prompt design and "
        "prompt-injection surface, eval methodology, and whether the task tests "
        "judgment about LLM behaviour rather than just glue-code wiring."
    ),
    "vector_engineer": (
        "You are a senior ML engineer focused on vector indexes. Focus your "
        "review on: embedding-model fit for the data, dimensionality choices, "
        "distance metric appropriateness (cosine / L2 / inner-product), metadata "
        "filtering correctness, and recall@k vs latency tradeoffs."
    ),
    "pm": (
        "You are a senior product manager and evaluation engineer. Focus your "
        "review on: rubric clarity (what does a good answer look like?), anchor "
        "quality (specific metrics and thresholds, not vague adjectives), "
        "observable behaviours rather than feelings, and whether the task rewards "
        "judgment under realistic product constraints (cost, time, data "
        "availability)."
    ),
}


def _persona_prefix(persona: str | None) -> str:
    """Return the persona block to prepend, or '' when no persona is supplied
    or when the persona doesn't have a dedicated prompt (in which case the
    eval runs with just the generic checklist — the prior behaviour).
    """
    if not persona:
        return ""
    prompt = PERSONA_PROMPTS.get(persona)
    if not prompt:
        return ""
    return prompt.strip() + "\n\n"


# ─────────────────────────────────────────────────────────────────────
# Helpers for the blocking_issues / suggestions schema (Layer B of the
# code-eval stability fix in docs/plans/2026-05-27-unified-classifier-
# template-schema.md). Both critics now return a dict with both the new
# and legacy keys so retry-loop code that hasn't migrated keeps working.
# ─────────────────────────────────────────────────────────────────────


def _normalize_eval_response(data: dict) -> dict:
    """Ensure every eval response carries both legacy + new field names.

    The schema requires ``blocking_issues`` + ``suggestions``, but legacy
    callers read ``issues`` + ``feedback``. We mirror blocking_issues into
    issues so both work, and drop the ``pass`` value to ``blocking_issues
    is empty`` defensively (in case the model gets the boolean wrong).
    """
    if not isinstance(data, dict):
        return _eval_failure("eval response was not a JSON object")

    blockers = list(data.get("blocking_issues") or [])
    suggestions = list(data.get("suggestions") or [])
    issues = list(data.get("issues") or [])

    # Legacy mirror — if the critic only populated `issues` (e.g. a
    # mocked test response), treat it as blockers.
    if not blockers and issues:
        blockers = issues
    # Forward mirror — keep `issues` aligned for legacy readers.
    if blockers and not issues:
        issues = list(blockers)

    # Drive `pass` from blocking_issues so a critic that says
    # `pass=true` but lists blockers can't slip through.
    pass_val = bool(data.get("pass", False)) and not blockers

    return {
        "pass": pass_val,
        "blocking_issues": blockers,
        "suggestions": suggestions,
        "validated_criteria": list(data.get("validated_criteria") or []),
        "issues": issues,
        "feedback": str(data.get("feedback") or ""),
    }


def _eval_failure(reason: str) -> dict:
    """Construct a uniform failure shape carrying both legacy + new fields."""
    return {
        "pass": False,
        "blocking_issues": [reason],
        "suggestions": [],
        "validated_criteria": [],
        "issues": [reason],
        "feedback": reason,
    }


# Eval response key (pass + blocking_issues) ordering in EVAL_RESPONSE_SCHEMA is
# fixed: pass, then blocking_issues, THEN the long suggestions array. So a
# response truncated by a reasoning-model output cap typically loses
# `suggestions` but keeps `pass` + `blocking_issues`. F11: such a truncation
# made `json.loads` raise and the whole eval defaulted to FAIL — silently
# failing genuinely-passing tasks. _salvage_eval_fields recovers the verdict.
def _salvage_eval_fields(raw: str | None) -> dict | None:
    """Best-effort recovery of pass + blocking_issues from a truncated/partial
    eval response. Conservative: only salvages a PASS when blocking_issues is
    clearly empty; if blockers are present (or unparseable) it returns a fail so
    a real blocker is never silently dropped. Returns None when even `pass`
    can't be located (caller then falls back to a hard failure)."""
    if not raw:
        return None
    m = re.search(r'"pass"\s*:\s*(true|false)', raw)
    if not m:
        return None
    pass_v = m.group(1) == "true"
    bm = re.search(r'"blocking_issues"\s*:\s*\[([^\]]*)', raw)
    blockers_text = bm.group(1).strip() if bm else ""
    if blockers_text:
        return {
            "pass": False,
            "blocking_issues": ["eval flagged blocking issue(s); response truncated"],
            "suggestions": [],
        }
    return {"pass": pass_v, "blocking_issues": [], "suggestions": []}


def _parse_eval_response(raw_response: str | None, response, kind: str) -> dict:
    """Parse + normalize an eval response, robust to reasoning-model truncation.

    Logs the response status, length, and the PARSED verdict (pass + blocker
    count) so a flaky verdict is diagnosable from the log alone. On a JSON parse
    failure, attempts :func:`_salvage_eval_fields` before giving up."""
    status = getattr(response, "status", None)
    if status and status != "completed":
        logger.warning(
            "%s eval response status=%s incomplete_details=%s len=%d",
            kind, status, getattr(response, "incomplete_details", None),
            len(raw_response or ""),
        )
    try:
        result = _normalize_eval_response(json.loads(raw_response))
        logger.info(
            "%s eval parsed: pass=%s blockers=%d (len=%d)",
            kind, result["pass"], len(result["blocking_issues"]),
            len(raw_response or ""),
        )
        return result
    except json.JSONDecodeError as e:
        logger.error(
            "%s eval JSON parse failed: %s | len=%d | full=%r",
            kind, e, len(raw_response or ""), raw_response,
        )
        salvaged = _salvage_eval_fields(raw_response)
        if salvaged is not None:
            logger.warning(
                "%s eval: salvaged pass=%s from truncated/partial response",
                kind, salvaged["pass"],
            )
            return _normalize_eval_response(salvaged)
        return _eval_failure(f"Failed to parse {kind} evaluation response")


# Cap on how much scenarios text we feed into the eval critic. The full
# scenarios list can be quite long (7 scenarios × ~600 chars each ≈ 4 KB);
# trim to keep the eval prompt bounded. Each scenario gets truncated to
# its first ~500 chars (enough for the LLM to identify the domain).
_SCENARIO_PREVIEW_CHARS = 500
_SCENARIO_BLOCK_CHAR_CAP = 6000


def _render_scenarios_block(scenarios: list[str] | None) -> str:
    """Render the input scenarios as a labelled block for Criterion 6.

    Each scenario is truncated to its first ~500 chars (enough for the
    eval LLM to identify the BUSINESS DOMAIN — which is usually clear in
    the first sentence) so the eval prompt stays bounded even with 7+
    long scenarios. Total block is capped to ~6 KB.
    """
    if not scenarios:
        return "(none provided — Criterion 6 passes vacuously)"

    lines = []
    total = 0
    for i, raw in enumerate(scenarios, 1):
        text = (raw or "").strip()
        if not text:
            continue
        snippet = text[:_SCENARIO_PREVIEW_CHARS]
        if len(text) > _SCENARIO_PREVIEW_CHARS:
            snippet += "…[truncated]"
        entry = f"  #{i}: {snippet}"
        if total + len(entry) > _SCENARIO_BLOCK_CHAR_CAP:
            lines.append(
                f"  …[remaining {len(scenarios) - i + 1} scenario(s) "
                f"omitted to fit the eval prompt's char budget]"
            )
            break
        lines.append(entry)
        total += len(entry)

    if not lines:
        return "(none provided — Criterion 6 passes vacuously)"
    return "\n".join(lines)

TASK_EVAL_PROMPT = """
You are an expert technical assessment reviewer. Evaluate the task JSON below against EXACTLY THESE SIX CRITERIA — do NOT invent additional ones:

1. SCENARIO REALISM — The scenario maps to a believable production situation, not a textbook contrivance.
2. PROFICIENCY FIT — Complexity matches {proficiency} level (years of experience: {yoe}, time constraint: {time_constraint} minutes).
3. SCOPE COHERENCE — The task description, outcomes, and acceptance criteria reference the same surface area (no orphaned requirements).
4. CANDIDATE-FACING CLARITY — The question text alone (without reading code) tells the candidate what they must produce.
5. CRITERIA COVERAGE — The criterias array references the competencies declared in the input.
6. DOMAIN ALIGNMENT — The task's business domain matches AT LEAST ONE of the
   real-world scenarios provided as INPUT below. If the input scenarios are
   about e-commerce / healthcare / real-estate / logistics, the generated
   task MUST be in one of those domains. If the task invents a new domain
   not present in the scenarios (e.g. "assessment platform", "leaderboards",
   "proof-of-skills marketplace") when those weren't in the scenarios list,
   that is FAIL the criterion — the task drifted into the employer's domain
   instead of using the provided scenarios.

   PASS if the task's domain (inferred from model names, route paths,
   business context, README) matches one of the scenarios' domains.
   FAIL if it invents a new domain not in the scenarios.

   When the INPUT SCENARIOS block below is empty / says "(none provided)",
   skip this criterion (it passes vacuously) — only enforce when scenarios
   were actually provided.

INPUT SCENARIOS (the legal task-domain set):
{scenarios_block}

OUTPUT FORMAT (strict JSON):
{{
  "pass": true|false,                     # true iff blocking_issues is empty
  "blocking_issues": [                    # ONLY items that fail one of the 6 criteria above
    "Criterion N: <specific concrete failure>"
  ],
  "suggestions": [                        # Nice-to-haves; do NOT block on these
    "<improvement that is not a blocker>"
  ],
  "validated_criteria": ["..."],
  "issues": [...],                        # LEGACY — mirror blocking_issues exactly
  "feedback": ""                          # short summary if pass=false, else ""
}}

CRITICAL GUARDRAIL — DO NOT INVENT REQUIREMENTS:
If you find yourself wanting to write a blocking_issue about anything not
covered by the 6 criteria above (e.g. "could be more challenging",
"should test more concepts", "missing X feature"), that is a SUGGESTION,
not a BLOCKER. Put it in suggestions. The task ships when the 6 criteria
are met, even if it is not the "best possible" version of itself.

CRITICAL GUARDRAIL — STUBS ARE THE TASK (the repo SHIPS incomplete BY DESIGN):
This is a "build-it" assessment: the repo is intentionally unfinished. Candidate
stub functions that `raise NotImplementedError`, invariant tests that fail until
those stubs are filled, and a graph/agent that errors when invoked because a stub
sits on the execution path are ALL INTENTIONAL — they ARE the task, not defects.
NEVER write a blocking_issue such as "X raises NotImplementedError", "this
prevents completion", "the invariant tests cannot run", or "the graph crashes on
invoke" — a candidate implementing the stubs is precisely the assessment, and
multi-stub tasks (e.g. a supervisor + a router + an arbitrator) are fine at this
level when they form ONE coherent senior decision. Judge the task as if the
candidate's work were done: it is correct when the scaffold loads (readiness /
--selfcheck passes by IMPORTING, not calling, the stubs) AND a correct
implementation of the stub(s) WOULD satisfy the invariants. Do not penalize a
task for being unsolved — that is the candidate's job.

TASK JSON:
{task_json}
"""

CODE_EVAL_PROMPT = """
You are evaluating a STARTER CODE BUNDLE that a candidate will receive.
Your ONLY job is to verify the bundle is shippable per the 5 criteria
below. DO NOT evaluate production-readiness. DO NOT demand features that
are not in the TASK DESCRIPTION.

THE BUG IS THE TASK
The starter code is INTENTIONALLY incomplete or buggy in the specific
way the TASK DESCRIPTION asks the candidate to fix. The route that
crashes on empty results, the view that lacks 404 handling, the query
that's missing an index, the test body containing only `pass` — these
are FEATURES of a well-formed task, not defects. The whole point of
the assessment is that the candidate fixes them. If you flag the
deliberate bug as a blocking issue under ANY criterion, you have
misread the task — that bug belongs to the candidate, not to you.
This rule supersedes every criterion below.

TASK DESCRIPTION (the contract — evaluate AGAINST this, not general principles):
{task_description}

STARTER CODE FILES (what the candidate sees on day one):
{code_files}

EVALUATE EXACTLY THESE FIVE CRITERIA — no others:

1. SCAFFOLD COMPLETENESS — Every file the TASK DESCRIPTION implies the
   candidate will modify is present and non-empty. (PASS if all
   description-referenced files exist; FAIL if a critical file is
   missing.)
   This criterion is ONLY about FILE PRESENCE — not about whether the
   code in those files is correct, bug-free, efficient, or complete.
   If you want to flag a bug, inefficiency, or missing handler in an
   existing file, that does NOT belong here — that is the task itself
   (handled by Criterion 2.b: BUGGY-CODE SHAPE). Do not shoehorn a
   "the code is buggy" complaint under Criterion 1.

2. STUB QUALITY — There must be SOMETHING for the candidate to do. One
   of these two shapes is required:
     (a) STUB SHAPE: functions / methods / test bodies the candidate is
         expected to complete contain `pass`, `TODO`, `...`, or
         `raise NotImplementedError`.
     (b) BUGGY-CODE SHAPE: the code is present and runs, but contains
         the specific bug / inefficiency / missing-handler that the
         TASK DESCRIPTION asks the candidate to fix (e.g., a route that
         lacks 404-handling for a fix-this-bug task, or an unindexed
         query for a fix-this-perf task).
   PASS if either shape is present. FAIL only if BOTH are absent —
   i.e. the starter code is a complete, correct solution with nothing
   for the candidate to do. Do NOT require shape (a) when shape (b) is
   the natural fit (fix-this-bug / fix-this-perf tasks). Do NOT require
   shape (b) when shape (a) is the natural fit (implement-this-feature
   tasks).

3. SOLUTION CONFIDENTIALITY — Comments and docstrings AVOID revealing
   the step-by-step answer. (PASS if comments describe WHAT, not HOW;
   FAIL if any comment block IS the answer.)

4. SCAFFOLD SUFFICIENCY — A candidate with this scaffold could
   plausibly REACH the outcomes stated in the TASK DESCRIPTION above by
   doing the work the task asks them to do. CHECK that the *structural*
   prerequisites are present: framework set up, models / routes /
   fixtures / imports / test infrastructure in place, entry points
   wired. (PASS if the candidate has a plausible path from this
   scaffold to the stated outcomes; FAIL only if the scaffold is
   mismatched — e.g., the task says "fix the Flask route" but no Flask
   app exists, or "optimize the query" but the relevant view is
   missing entirely.)
   IMPORTANT: it is NOT a failure that the outcomes are not yet
   implemented in the starter code. Of course they aren't — that's
   what the candidate is being asked to do. The bug, gap, missing
   handler, slow query, or empty test body IS the task; do not flag
   its absence as a Criterion 4 failure. That is goalpost drift.

5. RUNTIME REASONABLENESS — File paths, imports, and syntactic
   structure are correct for the declared runtime. (PASS if it would
   plausibly compile / parse on the target runtime; FAIL if there are
   obvious syntax / import errors.)
   This criterion is ONLY about whether the code would be ACCEPTED by
   the language/runtime — Python syntax valid, imports resolvable,
   indentation correct. A buggy-but-syntactically-valid line
   (e.g. `readings[-1]` on an empty list, or `request.args.get('x')`
   when the test posts a form) is NOT a Criterion 5 failure — that is
   the task itself (Criterion 2.b). The candidate's job is to fix the
   bug; the critic's job is not to do it for them.

OUTPUT FORMAT (strict JSON):
{{
  "pass": true|false,                     # true iff blocking_issues is empty
  "blocking_issues": [                    # ONLY items that fail one of the 5 criteria above
    "Criterion N: <specific concrete failure>"
  ],
  "suggestions": [                        # Improvements you noticed; do NOT block
    "<nice-to-have>"
  ],
  "validated_criteria": ["..."],
  "issues": [...],                        # LEGACY — mirror blocking_issues exactly
  "feedback": ""                          # short summary if pass=false, else ""
}}

CRITICAL GUARDRAIL — DO NOT INVENT REQUIREMENTS:
If you want to add a blocking_issue about caching, observability,
monitoring, security hardening, production-readiness, test coverage
breadth, error-handling depth, "missing X field/utility/helper", or
ANY feature that is NOT explicitly mentioned in the TASK DESCRIPTION
above, that is a SUGGESTION, not a BLOCKER. Put it in suggestions.

The most common failure mode of this critic is GOALPOST DRIFT —
demanding a new feature each attempt that the previous attempt could
not have known to include. To prevent that: the TASK DESCRIPTION above
is the COMPLETE specification. Anything outside it is a suggestion.
"""

def llm_task_eval(task_json, proficiency, yoe, time_constraint, openai_client, model,
                  persona: str | None = None,
                  scenarios: list[str] | None = None):
    """
    Evaluate task using the Responses API with gpt-5-nano for efficient evaluation.
    Note: model parameter is ignored, using EVAL_MODEL constant for evals.

    When ``persona`` is supplied (one of the matched template's personas, e.g.
    ``"backend"`` / ``"data"`` / ``"mle"``), the matching persona prompt is
    prepended to the generic checklist. When None or unrecognised, the eval
    falls back to the plain prompt (prior behaviour).

    ``scenarios`` is the list of real-world scenarios that were provided to the
    task-generation LLM. Used by Criterion 6 (DOMAIN ALIGNMENT) to detect
    domain drift — task invented "assessment leaderboard" when every scenario
    was e-commerce / healthcare / real-estate. When None / empty, Criterion 6
    passes vacuously.
    """
    task_json_str = json.dumps(task_json, indent=2)
    prompt = _persona_prefix(persona) + TASK_EVAL_PROMPT.format(
        task_json=task_json_str,
        proficiency=proficiency,
        yoe=yoe,
        time_constraint=time_constraint,
        scenarios_block=_render_scenarios_block(scenarios),
    )
    
    # Build messages for Responses API
    messages = [{"role": "user", "content": prompt}]
    
    try:
        # Use configured eval model for efficient evaluations.
        # reasoning.effort dropped from "medium" → "low" for determinism —
        # eval critics judge against a bounded checklist (5 criteria), not
        # an open-ended judgement, so lower reasoning effort gives
        # consistent verdicts across repeat calls. Higher effort = more
        # variance in what the model "happens to notice", which manifests
        # as goalpost drift in the retry loop.
        response = eval_openai_client.responses.create(
            model=EVAL_MODEL,
            input=messages,
            reasoning={"effort": "low"},
            max_output_tokens=16000,
            text={
                "format": {
                    "type": "json_schema",
                    "name": EVAL_RESPONSE_SCHEMA["name"],
                    "schema": EVAL_RESPONSE_SCHEMA["schema"],
                    "strict": EVAL_RESPONSE_SCHEMA["strict"]
                }
            }
        )

        # Extract output_text from response
        raw_response = getattr(response, "output_text", None)
        if not raw_response:
            logger.error("No output_text received from OpenAI Responses API for task eval")
            return _eval_failure("No response from evaluation API")

        logger.info(f"Raw LLM task eval response: {raw_response[:200]}...")

        return _parse_eval_response(raw_response, response, "task")
    except Exception as e:
        logger.error(f"Unexpected error in task evaluation: {str(e)}")
        return _eval_failure(f"Evaluation error: {str(e)}")

def llm_code_eval(code_data, task_description, openai_client, model,
                  persona: str | None = None):
    """
    Evaluate code files using the Responses API with gpt-5-nano for efficient evaluation.
    Note: model parameter is ignored, using EVAL_MODEL constant for evals.

    When ``persona`` is supplied, the matching persona prompt is prepended to
    the generic checklist (see ``llm_task_eval`` for details).
    """
    # Handle both possible structures: direct files dict or nested under 'files' key
    if isinstance(code_data, dict):
        if 'files' in code_data:
            files_content = code_data.get('files', {})
        else:
            # Assume code_data is the files dict directly
            files_content = code_data
    else:
        files_content = {}

    prompt = _persona_prefix(persona) + CODE_EVAL_PROMPT.format(
        code_files=json.dumps(files_content, indent=2),
        task_description=task_description,
    )
    
    # Build messages for Responses API
    messages = [{"role": "user", "content": prompt}]
    
    try:
        # Use configured eval model for efficient evaluations.
        # See llm_task_eval for the reasoning.effort=low rationale.
        response = eval_openai_client.responses.create(
            model=EVAL_MODEL,
            input=messages,
            reasoning={"effort": "low"},
            max_output_tokens=16000,
            text={
                "format": {
                    "type": "json_schema",
                    "name": EVAL_RESPONSE_SCHEMA["name"],
                    "schema": EVAL_RESPONSE_SCHEMA["schema"],
                    "strict": EVAL_RESPONSE_SCHEMA["strict"]
                }
            }
        )

        # Extract output_text from response
        raw_response = getattr(response, "output_text", None)
        if not raw_response:
            logger.error("No output_text received from OpenAI Responses API for code eval")
            return _eval_failure("No response from evaluation API")

        logger.info(f"Raw LLM code eval response: {raw_response[:200]}...")

        return _parse_eval_response(raw_response, response, "code")
    except Exception as e:
        logger.error(f"Unexpected error in code evaluation: {str(e)}")
        return _eval_failure(f"Code evaluation error: {str(e)}")
