"""
DSPy module — the Generator → Verifier → Refiner loop.

The runtime "intelligence" lives here. Plain Python (classifier, retriever,
db_queries, validator) feeds context into the DSPy module which then makes the
LLM calls.

For the first iteration we run the agent UNCOMPILED — just calling Predict /
ChainOfThought directly with hand-written instructions in the signatures.
DSPy compilation (MIPROv2) can be added later once we have a training set.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Optional

import dspy
from dotenv import load_dotenv

logger = logging.getLogger("prompt_generator")

from infra.classifier.runtime import Competency
from infra.llm_provider import resolve_dspy_model
from generators.prompts.db_queries import (
    TaskExample,
    fetch_competency_scope,
    fetch_similar_tasks,
    init_supabase,
)
from generators.prompts.input_files import build_detailed_skill_signal
from generators.prompts.retriever import retrieve_references, RetrievalResult
from generators.prompts.shape_classifier import ShapeDecision, classify_task_shape
from generators.prompts.validator import ValidationResult, validate_prompt_file

load_dotenv()


# ----------------------------------------------------------------------
# DSPy LM configuration — uses Portkey gateway like the rest of the codebase
# ----------------------------------------------------------------------

# Model strategy:
# - RUNTIME (generation/verification of new prompts): use a strong model. Default
#   Sonnet 4.6 — quality matters at runtime since the output is committed code.
# - COMPILATION (BootstrapFewShot/MIPROv2 search loop): use a cheaper model.
#   Compilation runs many calls in a tight loop, so Haiku 4.5 saves ~5-10x cost
#   while still being competent enough to score candidate prompts.
# Runtime model is OpenAI (gpt-5.5) and stays OpenAI — out of scope for the GLM
# switch. The COMPILE model is the only Claude call here, so it's provider-aware:
# anthropic/claude-haiku-4-5 by default, openrouter/<glm> when LLM_PROVIDER=glm.
DEFAULT_RUNTIME_MODEL = os.getenv("PROMPT_GENERATOR_MODEL", "openai/gpt-5.5")
DEFAULT_COMPILE_MODEL = os.getenv("PROMPT_GENERATOR_COMPILE_MODEL") or resolve_dspy_model("prompt_compile")


def configure_dspy(model: Optional[str] = None, mode: str = "runtime") -> None:
    """Wire DSPy to the right LLM provider.

    Routing logic:
      - Models prefixed `openrouter/...`  → OpenRouter direct (uses OPENROUTER_API_KEY)
      - All other models                  → Portkey gateway (uses OPENAI_API_KEY)

    OpenRouter is for cheap/free open-source models (DeepSeek, Qwen, Gemma).
    Portkey is for OpenAI/Anthropic models routed through our existing gateway.

    Args:
        model: explicit model override; takes precedence over `mode` defaults.
        mode:  "runtime" (default, strong model) or "compile" (cheap model).
    """
    if model is None:
        model = DEFAULT_COMPILE_MODEL if mode == "compile" else DEFAULT_RUNTIME_MODEL

    # GPT-5 family (gpt-5, gpt-5.4, gpt-5-codex, ...) only accepts
    # temperature=1 — litellm rejects any other value. Detect by substring
    # so future point-releases (gpt-5.5 etc.) are handled automatically.
    is_gpt5_family = "gpt-5" in model.lower()
    temperature = 1.0 if is_gpt5_family else 0.2

    if model.startswith("openrouter/"):
        # Strip the openrouter/ prefix; pass the rest as the model id.
        or_key = os.getenv("OPENROUTER_API_KEY")
        if not or_key:
            raise RuntimeError(
                "Missing OPENROUTER_API_KEY for openrouter/* model. "
                "Get a key at https://openrouter.ai/keys"
            )
        bare_model = model[len("openrouter/"):]
        lm = dspy.LM(
            model=f"openrouter/{bare_model}",
            api_key=or_key,
            api_base="https://openrouter.ai/api/v1",
            max_tokens=16000,
            temperature=temperature,
        )
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        portkey_key = os.getenv("PORTKEY_API_KEY")
        if not api_key:
            raise RuntimeError("Missing OPENAI_API_KEY in environment.")

        from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders

        provider = "anthropic" if "anthropic/" in model or "claude" in model else "openai"
        lm = dspy.LM(
            model=model,
            api_key=api_key,
            api_base=PORTKEY_GATEWAY_URL,
            extra_headers=createHeaders(provider=provider, api_key=portkey_key),
            max_tokens=16000,
            temperature=temperature,
        )

    dspy.settings.configure(lm=lm)

    # Capture the DSPy/litellm completions into the pipeline trace sink (no-op
    # unless PIPELINE_TRACING_ENABLED). DSPy bypasses the OpenAI-SDK trace_client
    # wrapper, so this litellm callback is how the prompt stage gets traced.
    from infra.tracing import register_litellm_tracing

    register_litellm_tracing()


# ----------------------------------------------------------------------
# DSPy signatures
# ----------------------------------------------------------------------

class GeneratePromptSignature(dspy.Signature):
    """Generate a complete Python file containing a PROMPT_REGISTRY entry for a
    new (competencies, proficiency) combination.

    The generated prompt MUST look and feel like the curated prompt files in
    `reference_prompts`. The curated files (e.g. PostgreSQL_intermediate_prompt.py,
    python_redis_intermediate.py, PostgreSQL_basic_prompt.py) follow a single
    canonical blueprint. Your job is to reproduce that blueprint — its section
    ordering, its tone, its recurring phrases, its README section names, its
    verbose per-field JSON schema descriptions — adapted to the target
    competencies. Do NOT invent your own section structure.

    ─────────────────────────────────────────────────────────────────────────
    HARD CONSTRAINT #0 — primary_directive is AUTHORITATIVE (overrides all)
    ─────────────────────────────────────────────────────────────────────────
    The `primary_directive` input MAY BE EMPTY. When it is non-empty it is an
    AUTHORITATIVE human instruction for THIS run and is the PRIMARY thing that
    shapes the generated prompt. You MUST mold the generated task to satisfy
    every requirement it states — its requested topic, sub-topic emphasis,
    artifacts (e.g. "include deployment: Dockerfile + docker-compose + run.sh"),
    and framing. Where the directive conflicts with the soft style of
    `reference_prompts` or `detailed_skill_signal`, the directive WINS — but you
    must still obey the canonical structure (HARD CONSTRAINTS #1–#7) and the
    output JSON contract.

    The ONE thing the directive may NOT override is `competency_scopes` (HARD
    CONSTRAINT #4): the directive cannot push the task beyond the competency's
    allowed scope/proficiency. If the directive asks for something out of scope,
    honor the directive's intent as far as the scope permits and stay within
    scope — do not generate out-of-proficiency requirements.

    When `primary_directive` is empty, ignore it entirely and generate exactly
    as you otherwise would from scopes + references + signal.

    ─────────────────────────────────────────────────────────────────────────
    HARD CONSTRAINT #1 — STRUCTURAL MIMICRY (most important)
    ─────────────────────────────────────────────────────────────────────────
    The INSTRUCTIONS string MUST follow the exact section ordering used by
    the curated reference prompts. Use these top-level section headings, in
    this order, with these EXACT names:

      ## GOAL
      ## CONTEXT & CANDIDATE EXPECTATION
      ## INSTRUCTIONS
          ### Nature of the Task
      ## AI AND EXTERNAL RESOURCE POLICY
      ## <Code or Database> Generation Instructions
      ## Infrastructure Requirements
          ### Docker-compose Instructions
          ### <init_database.sql / Redis Configuration / etc.> Instructions
          ### Run.sh Instructions
      ## kill.sh file instructions
      ### Dockerfile Instructions          (omit if no app container)
      <"The output should be a valid json schema:" bullet list of files>
      ## Code file requirements
      ## .gitignore INSTRUCTIONS
      ## README.md INSTRUCTIONS
          ### Task Overview
          ### Objectives
          ### Helpful Tips
          ### How to Verify
          <exclusion directive — an INSTRUCTION about what to omit, NOT a
           README output section; see HARD CONSTRAINT #2>
      ## REQUIRED OUTPUT JSON STRUCTURE
      ## CRITICAL REMINDERS                  (or "## CRITICAL NOTES")

    DO NOT introduce new top-level sections that don't appear in the
    references — specifically, do NOT add `## SCENARIO LOCK`,
    `## PROFICIENCY BOUNDARY`, `## TASK SHAPE`, `## QUALITY BAR`,
    `## RECOMMENDED TASK THEMES`, or `## HARD CONSTRAINTS FROM TEMPLATE
    CAPABILITIES`. Those don't exist in any curated prompt. Their content
    belongs INLINE inside the canonical sections above (proficiency notes
    inside `### Nature of the Task`, scenario sourcing inside
    `INPUT_AND_ASK` and `## INSTRUCTIONS`, etc.).

    Recurring phrases the curated prompts use — reuse them verbatim or
    near-verbatim:
      - "As a [database architect / technical architect] super experienced in
        <stack>, you are given a list of real world scenarios and proficiency
        levels for <stack>."
      - "**CRITICAL**:" callouts on important rules (use liberally inside
        `### Nature of the Task`)
      - "FULLY FUNCTIONAL" / "FULLY POPULATED" when describing the candidate's
        starting environment
      - "**FILE LOCATION**: All code and scripts must reference /root/task as
        the base directory"
      - "If you include diagrams, ensure they are written in mermaid format,
        properly indented and also in code blocks"
      - "**MUST NOT include any version specification**" in docker-compose
      - For a datastore service, REQUIRE the standard init env vars inline in
        `environment:` — postgres MUST set
        `POSTGRES_USER`/`POSTGRES_PASSWORD`/`POSTGRES_DB`, mysql the `MYSQL_*`
        equivalents — because the image will NOT initialize without them (the
        container exits, so the DB and its healthcheck never come up). Forbid
        only `.env` files / `${VAR}` host indirection, NOT inline service env
        values. The init SQL, healthcheck, and connection string must use the
        same user/database.
      - "**SECURITY-CRITICAL**: ports MUST be bound to localhost only using
        `127.0.0.1:<port>:<port>`" — for every datastore exposed to the host
      - The 9-numbered-step `## kill.sh file instructions` block — copy its
        shape (stop containers, remove volumes, remove networks, force-remove
        images, `docker system prune -a --volumes -f`, `rm -rf /root/task`,
        "|| true" for idempotency, print logs at every step, final
        "Cleanup completed successfully!" message)
      - "Candidates are permitted and encouraged to use any external resources
        they find helpful, including but not limited to Google, Stack Overflow,
        <stack> documentation, and AI-powered tools, agentic IDEs, or Large
        Language Models (LLMs)" — the standard AI policy 4-bullet block

    ─────────────────────────────────────────────────────────────────────────
    HARD CONSTRAINT #2 — README section names
    ─────────────────────────────────────────────────────────────────────────
    Inside `## README.md INSTRUCTIONS`, the candidate-facing README has EXACTLY
    these output sections, in this order — and NO others:

      1. Task Overview
      2. Objectives
      3. Helpful Tips
      4. How to Verify

    CRITICAL — "NOT TO INCLUDE" is an INSTRUCTION, NOT a section. The exclusion
    guidance below is a directive to the task-gen LLM about what to OMIT from the
    README. The generated prompt MUST NOT list "NOT TO INCLUDE in README" (or any
    "NOT TO INCLUDE"/"do not include" heading) as a README output section, and
    the produced README.md MUST NOT contain a heading named "NOT TO INCLUDE …".
    Render the exclusion guidance as a clearly-labelled directive block (e.g.
    "## CONTENT TO EXCLUDE FROM THE README (instruction — do not emit as a
    section)"), kept OUT of the numbered output-section list above.

    Do NOT rename "Helpful Tips" to "Guidance", "Tips", "Hints", or
    "Recommendations". Do NOT add `Database Schema Overview`, `Database
    Access`, or `Performance Issues` as separate sections. The README must
    NOT contain `<DROPLET_IP>` placeholders or any database-connection
    details (host, port, username, password, client-tool suggestions).

    Section size + framing rules — the generated prompt's README.md
    INSTRUCTIONS section MUST embed ALL of the following so the downstream
    task-gen LLM produces concise, non-revealing READMEs (these come
    verbatim from curated references like
    `task_generation_prompts/Intermediate/javascript_intermediate_prompt.py`):

      • A top-of-section preamble that states:
          – "The README must be concise and open-ended. Each section should
            have only the essential points needed to understand the task.
            Do NOT overload with too many bullets — quality over quantity.
            The candidate should figure out the implementation approach on
            their own."
          – "Do NOT directly tell candidates what to implement — provide
            direction and guidance to help them discover solutions."

      • Per-section size caps the generated prompt MUST include:
          – Task Overview: 3-4 meaningful sentences. No bullet list.
            Describes the business scenario, current state, and why the
            problem matters. NEVER empty. NO bold time-budget callouts.
          – Objectives:    4-6 bullets max.
          – Helpful Tips:  4-5 bullets max.
          – How to Verify: 4-6 bullets max.

      • Per-section framing rules the generated prompt MUST include:
          – Objectives: "Frame objectives around outcomes rather than
            specific technical implementations. Objectives describe the
            'what' and 'why', never the 'how'." Each bullet states an
            observable end-state, not a step or an API/library to use.
          – Helpful Tips: "Provide practical guidance without revealing
            specific implementations." Each bullet starts with an action
            word: "Consider", "Think about", "Explore", "Review",
            "Analyze". Tips guide discovery — they MUST NOT name the
            specific API, library, function, pattern, data structure, or
            algorithm that solves the task.
          – How to Verify: "Frame verification in terms of observable
            outcomes. Describe WHAT to verify and the expected behavior,
            not the specific implementation to write." Each bullet is a
            check the candidate can run (test output, response shape,
            latency observation, log line, memory reading).
            For tasks that call a real LLM (a `.env.example` declaring
            OPENAI_API_KEY / ANTHROPIC_API_KEY), How to Verify MUST open with a
            GitHub note admonition embedded INSIDE the section as a `>`
            blockquote (NEVER a new `##` heading — that breaks readme parsing):
            a "> [!NOTE]" line, then "> Copy `.env.example` to `.env` and set
            your provider key. The invariant tests run offline and need no key;
            only the end-to-end run does."

      • A CONTENT-TO-EXCLUDE directive in the generated prompt (a clearly-
        labelled instruction about what to keep OUT of the README — NOT a
        README output section, and never emitted as a README heading)
        listing at minimum:
          – Setup commands (e.g. `npm install`, `pip install`,
            `docker compose up`, `mvn test`, etc.)
          – Direct solutions or architectural decisions
          – Step-by-step implementation guides
          – Specific APIs, method names, library names, pattern names, or
            data-structure names that reveal the solution
          – Code snippets that give away the answer
          – Directive phrases like "you should implement", "add this
            middleware", "create this class", "use <specific API>"

    ─────────────────────────────────────────────────────────────────────────
    HARD CONSTRAINT #3 — REQUIRED OUTPUT JSON STRUCTURE must be VERBOSE
    ─────────────────────────────────────────────────────────────────────────
    The INSTRUCTIONS prompt's `## REQUIRED OUTPUT JSON STRUCTURE` block tells
    the downstream task-generation LLM what JSON to emit. Each field's value
    in that schema MUST be a one-sentence DESCRIPTION of what to fill in —
    NOT a placeholder example like `["outcome 1"]` or `{{"term_1": "..."}}`.

    Required canonical keys (multiagent.py reads exactly these names — synonyms
    like `task_title` / `files` / `context` produce a hollow, unusable task):

      "name"           — kebab-case GitHub repo name (under 50 chars)
      "title"          — human-readable display name, "<action verb> <subject>"
                         format, 50-80 chars. Different from `name`.
      "question"       — full candidate-facing task description
      "code_files"     — object mapping filepath → file contents (verbose
                         per-file descriptions; see references)
      "answer"         — evaluator-facing high-level solution approach
      "definitions"    — object of term → definition pairs
      "hints"          — single line nudging investigation WITHOUT revealing
                         the fix
      "outcomes"       — 2-3 lines on measurable expected results
      "pre_requisites" — bullet list of ASSUMED PRIOR KNOWLEDGE / skills the
                         candidate already brings. DECLARATIVE capability phrases
                         ONLY ("Python 3.11 proficiency", "Comfort with…",
                         "Familiarity with…", "Understanding of…", "A provider
                         key via .env"). NEVER imperative setup/verify steps
                         ("Run…", "Use…", "Test…", "Configure…", "Install…") —
                         those are README How-to-Verify content, not prerequisites.
      "short_overview" — bullet list summarising business problem + technical
                         focus + expected outcome

    GOOD (matches curated style):
      "outcomes": "Expected results after completion in 2-3 lines focusing on
                   measurable performance improvements and optimized database
                   operations. Use simple english."
      "hints": "A single line hint on what a good intermediate-level approach
                to analyze and optimize could include. These hints must NOT
                give away the specific optimizations needed."
      "pre_requisites": ["Python 3.11 proficiency; able to run pytest locally",
                "Comfort with Docker-backed PostgreSQL and parameterized SQL",
                "Understanding of tool-calling agents and structured outputs"]

    BAD (drift):
      "outcomes": ["outcome 1", "outcome 2"]
      "hints": ["hint 1"]
      "definitions": {{"term_1": "definition", "term_2": "definition"}}
      "pre_requisites": ["Run the readiness script and ensure Postgres starts",
                "Configure the LLM key in .env", "Test via curl to POST /endpoint"]

    ─────────────────────────────────────────────────────────────────────────
    HARD CONSTRAINT #4 — competency_scopes is the source of truth
    ─────────────────────────────────────────────────────────────────────────
    The `competency_scopes` field describes EXACTLY what each competency
    covers at this proficiency level. The generated prompt MUST:
      - Only ask the candidate to use concepts that appear (or could be
        naturally derived from) the scope text.
      - Never require concepts the scope says are out of scope.
      - When the scope says "limited understanding of X" or "not yet
        expected to do Y", the generated task must NOT require X or Y as
        primary skills.
    Bake proficiency calibration INLINE inside `### Nature of the Task`
    (e.g. "(3-5 years experience)", "intermediate-level optimization") —
    do NOT add a separate `## PROFICIENCY BOUNDARY` section.

    ─────────────────────────────────────────────────────────────────────────
    HARD CONSTRAINT #5 — Python module structure
    ─────────────────────────────────────────────────────────────────────────
    Output a valid Python module that:
      - Defines three triple-quoted strings: a CONTEXT prompt, an
        INPUT_AND_ASK prompt, and an INSTRUCTIONS prompt. Use names like
        PROMPT_<TECH>_<LEVEL>_CONTEXT, _INPUT_AND_ASK, _INSTRUCTIONS.
      - Contains placeholders {organization_background}, {role_context},
        {competencies}, {real_world_task_scenarios}, {minutes_range}.
      - Defines PROMPT_REGISTRY = { "<key>": [CONTEXT, INPUT_AND_ASK, INSTRUCTIONS] }
        where <key> is exactly: 'Name1 (LEVEL), Name2 (LEVEL)' — alphabetically
        sorted competency names with proficiency in parentheses.

    ─────────────────────────────────────────────────────────────────────────
    HARD CONSTRAINT #6 — Brace escaping
    ─────────────────────────────────────────────────────────────────────────
    Every `{` and `}` inside the prompt strings is passed through Python
    `str.format(**fmt_args)` downstream. Only the following are valid
    single-brace placeholders: `{organization_background}`, `{role_context}`,
    `{competencies}`, `{real_world_task_scenarios}`, `{minutes_range}`,
    `{question_prompt}`. Any OTHER `{` or `}` (JSON example, dict literal,
    f-string snippet, set notation) MUST be doubled (`{{` and `}}`). For
    example, when embedding an output schema example, write
    `{{"title": "...", "code_files": {{"a.py": "..."}}}}`, NOT
    `{"title": "...", "code_files": {"a.py": "..."}}`. A single unescaped
    JSON example causes downstream `KeyError: '\\n  "title"'` and no task is
    ever generated.

    ─────────────────────────────────────────────────────────────────────────
    HARD CONSTRAINT #7 — Infrastructure shape comes from `task_shape`
    ─────────────────────────────────────────────────────────────────────────
    The `task_shape` input field is the AUTHORITATIVE decision for whether
    the generated prompt produces an infra-shaped task or a pure-runtime
    local task. It was decided up-front by the prompt-generator's shape
    classifier from competency_scopes + scenarios. DO NOT second-guess it.
    The two values + their requirements:

      (a) `task_shape == "infra"` → the scenario needs an external service
          (DB / cache / queue / broker / search). The generated prompt MUST
          include `docker-compose.yml` for the datastore(s) the scenario
          actually exercises, `run.sh` using `docker compose up -d`, and
          `kill.sh` using `docker compose down`. Decide the specific
          datastores by READING the scenario text in `detailed_skill_signal`
          — do not invent extras. The `datastores` input list (if provided)
          is informational only. `run.sh` is a READINESS/self-check, NOT the
          grader: it brings the datastore(s) up, waits for health, verifies the
          starter compiles/loads with the runtime's BUILD command (e.g.
          `cargo build`, `go build`, `npm ci && npm run build`, an import
          smoke), then exits 0 — on the UNSOLVED starter. It MUST NOT run the
          grader test suite (designed to fail until the candidate solves the
          task); the candidate/grader runs the tests separately.

      (b) `task_shape == "non_infra"` → pure-runtime / language-level /
          algorithmic / async-concurrency / in-process / UI / frontend
          work. The generated prompt MUST NOT include `docker-compose.yml`,
          `init_database.sql`, `kill.sh`, or any datastore configuration.
          Ship the task as a local project using the runtime's native
          package manifest (e.g. `package.json`, `pyproject.toml`,
          `pom.xml`, `Cargo.toml`, `build.gradle`) plus source + tests,
          runnable via the runtime's native test command. Use your
          knowledge of the stack to pick the right manifest filename and
          test command.

          RUN.SH DEPLOYABILITY CONTRACT (when this task ships a TEST SUITE
          the candidate must make pass — i.e. red/failing tests are the
          deliverable, the candidate's job is to turn them green): if the
          generated prompt includes a `run.sh`, that `run.sh` is a
          DEPLOYABILITY probe, NOT a pass/fail gate. It MUST exit 0 when the
          test runner COLLECTED AND EXECUTED the suite — EVEN IF tests fail
          (failing-as-designed is the expected state of a fresh checkout) —
          and exit non-zero ONLY when the project can't boot or the runner
          can't run: import error, missing dependency, or collection /
          config / usage error. Concretely for pytest, mirror these exit
          codes: 0 (all passed) and 1 (ran, some failed) → run.sh exits 0;
          >= 2 (interrupted / internal / usage error) and 5 (no tests
          collected) → run.sh exits non-zero. Capture the runner's exit code
          and branch on it — do NOT wrap the test command in a bare `set -e`,
          which conflates a designed test failure with a broken scaffold and
          makes a perfectly deployable task look un-deployable. Example shape
          (adapt the runner per stack):
              python -m pytest -q; rc=$?
              if [ "$rc" -le 1 ]; then exit 0; else exit "$rc"; fi
          The `### Run.sh Instructions` section of the generated prompt MUST
          spell this contract out so the produced `run.sh` follows it.

    Common-library/install rules (apply in BOTH shapes):
      • The `primary_runtime` itself is PRE-INSTALLED by the E2B template — do
        NOT `apt-get`/system-install the runtime. BUT the task's OWN third-party
        deps are NOT pre-installed, so `run.sh`'s FIRST step MUST install them:
        `pip install -q -r requirements.txt` (Python) / the runtime's manifest
        install (npm ci, go mod download, …). Skipping it fails the readiness
        gate on the first attempt with ModuleNotFoundError.
      • `persona="mobile"` → no Dockerfile, no compose; run the runtime's
        native test command for that platform.
      • `persona="dba"` / `persona="data"` → `init_database.sql` + Compose;
        no app code.
      • `persona="pm"` → data files only (CSV / JSON); no `run.sh`.
      • `persona="frontend"` → runtime-native manifest, no Docker,
        browser-side only.
      • `persona="backend"` + scenario does NOT need an external service
        (per the rule above) → no Docker, no compose, no `kill.sh`. `run.sh`
        is optional — the candidate runs the task locally with the runtime's
        native test command against the runtime's native manifest.
      • `persona="sdet"` → test suite shape; template ships the runner.

    ─────────────────────────────────────────────────────────────────────────
    HARD CONSTRAINT #8 — AGENT REALNESS (agent-engineering competencies only)
    ─────────────────────────────────────────────────────────────────────────
    When the competencies are agent-engineering competencies — Multi-Agent
    Systems, Production Agent Engineering, Tool Use for Agents, Context
    Engineering, or any LLM/agent-orchestration competency — the generated task
    MUST exercise a REAL LLM/agent loop:

      - The candidate's code MUST call a REAL model through the runtime's SDK or
        a router (e.g. litellm, the OpenAI / Anthropic SDK). The candidate
        supplies their own provider key at runtime via .env.
      - The candidate-filled stubs ARE the agent logic — context construction,
        tool selection/dispatch, retry/timeout handling, output parsing,
        memory/state. They are NOT a fake model.
      - FORBIDDEN: a `FakeLLM` / `StubLLM` / regex or keyword "intent parser"
        standing in for the model; `time.sleep()` / `asyncio.sleep()` used to
        SIMULATE an agent or tool "thinking"; any "deterministic stand-in for the
        LLM". Those produce tasks that test plumbing, not agent engineering.
      - Determinism for GRADING is NOT required: production grades the candidate's
        diff with an LLM judge and never runs the code, so a real
        (non-deterministic) model is fine. Use fixtures only to make tool INPUTS /
        retrieval corpora deterministic — never to replace the model.
      - "LLM-free" / "no API key" applies ONLY to the generation-time READINESS
        GATE (which imports the package + validates fixtures/schemas without a
        key). It MUST NOT be generalized to the task itself.

    ─────────────────────────────────────────────────────────────────────────
    SOFT GUIDANCE — Scenario sourcing
    ─────────────────────────────────────────────────────────────────────────
    The candidate's EMPLOYER is described in `organization_background`. The
    employer is administering the assessment — it is NOT necessarily the task
    domain. The task's business domain should come from one of the scenarios
    in `real_world_task_scenarios`.

    Use the SAME LANGUAGE the curated references use inside `INPUT_AND_ASK`:

      - "You MUST draw inspiration from ONE of the real-world scenarios
        provided above to create the task"
      - "Use the provided real-world scenario as the basis for this task -
        do not invent a different domain. When multiple scenarios are listed,
        pick the one whose technical surface area best fits the candidate level"
      - "The task scenario should closely align with the business context,
        technical requirements, and domain described in the selected real-world
        scenario"

    Do NOT escalate this into a heavy-handed `## SCENARIO LOCK (mandatory)`
    top-level section — no curated prompt has one. The soft language above
    is what works in practice.

    ─────────────────────────────────────────────────────────────────────────
    INPUT FIELDS reminder
    ─────────────────────────────────────────────────────────────────────────
    `reference_prompts` is your PRIMARY structural template — read at least
    one same-stack reference end-to-end before drafting, mimic its skeleton.
    `similar_tasks` calibrates question complexity and file count.
    `detailed_skill_signal` calibrates question difficulty and scenario mix;
    MAY BE EMPTY (when empty, fall back to scopes + references alone, do not
    flag empty as a constraint).
    """

    primary_directive: str = dspy.InputField(
        desc="AUTHORITATIVE free-text user directive for this run, or empty. When "
             "non-empty it is the PRIMARY shaping input — the generated prompt MUST "
             "satisfy every requirement it states (topic, emphasis, artifacts like "
             "'include deployment'), and it overrides the soft style of "
             "reference_prompts / detailed_skill_signal where they conflict. It may "
             "NOT exceed competency_scopes. Empty → ignore it (generate as usual)."
    )
    competencies: str = dspy.InputField(
        desc="Comma-separated competency names with proficiency (e.g. 'Python (BASIC), SQL (BASIC)')"
    )
    proficiency: str = dspy.InputField(desc="Target proficiency level (BASIC/BEGINNER/INTERMEDIATE)")
    task_shape: str = dspy.InputField(
        desc='Authoritative infra decision: exactly "infra" or "non_infra". '
             '"infra" → MUST include docker-compose / kill.sh / run.sh for the '
             "scenario's datastores. \"non_infra\" → MUST NOT include any "
             "docker-compose / init_database.sql / kill.sh — ship a pure local "
             "project using the runtime's native manifest + test command. "
             "See HARD CONSTRAINT #7 for the full rules."
    )
    runtime: str = dspy.InputField(
        desc="Primary language runtime of the matched template (e.g. python, node)"
    )
    frameworks: str = dspy.InputField(
        desc="JSON list of framework names the template advertises in capabilities.frameworks, e.g. '[\"fastapi\"]' or '[]'"
    )
    datastores: str = dspy.InputField(
        desc="JSON list of datastore names the template makes AVAILABLE, not requirements. Decide which (if any) the task needs by reading the scenarios and scope, not this list. Pure-runtime tasks should include no datastore configuration even when this list is non-empty."
    )
    persona: str = dspy.InputField(
        desc="Reviewer persona for this combo (one of the matched template's "
             "personas, e.g. backend|data|mle|sdet|frontend|mobile|dba|pm)"
    )
    competency_scopes: str = dspy.InputField(
        desc="AUTHORITATIVE scope text from Supabase competencies table — defines what is "
             "in/out of scope. The generated prompt MUST stay within these bounds."
    )
    reference_prompts: str = dspy.InputField(
        desc="Source of 2-5 existing prompt files. Use as structural template only — "
             "DO NOT copy content; adapt to the target."
    )
    similar_tasks: str = dspy.InputField(
        desc="Summaries of successful tasks for similar competencies — use to calibrate "
             "complexity and style."
    )
    detailed_skill_signal: str = dspy.InputField(
        desc="Bundled calibration signal from task_input_files/: sub-skill checklist "
             "(questions_prompt), candidate role context (role_context), and up to 3 "
             "example scenarios. Use to calibrate question difficulty, complexity, and "
             "scenario domain mix. MAY BE EMPTY for brand-new combos — when empty, fall "
             "back to scopes + references alone without flagging it as a constraint."
    )
    feedback_from_previous_attempt: str = dspy.InputField(
        desc="Verifier feedback from prior iteration (empty on first attempt). When "
             "non-empty, every issue mentioned MUST be addressed in the new output."
    )
    new_prompt_file: str = dspy.OutputField(
        desc="Complete Python file source with PROMPT_REGISTRY definition. Output ONLY "
             "the Python source — no markdown fences, no commentary."
    )


class VerifyPromptSignature(dspy.Signature):
    """Senior reviewer judges whether a generated prompt file meets quality bars.

    PASS BAR — be PRACTICAL. The goal is to ship a usable prompt that looks
    and feels like the curated `reference_prompts`. Pass if the prompt is
    structurally faithful to the curated style, scope-respecting, and would
    plausibly produce a deployable task. Do NOT block on minor stylistic issues.

    HARD-FAIL conditions (must reject):
      0. DIRECTIVE IGNORED: if `primary_directive` is non-empty and the prompt
         fails to honor it — it omits a requested artifact (e.g. the directive
         asks to "include deployment" but there is no docker-compose / run.sh),
         ignores the requested topic/emphasis, or contradicts the directive —
         REJECT, and say exactly which part of the directive was not satisfied.
         (When `primary_directive` is empty, skip this check entirely.) The
         directive does NOT excuse a scope violation — condition 1 still applies.
      1. SCOPE VIOLATION: Required candidate skills exceed competency_scopes.
         Example: BASIC scope says "limited async understanding" but the prompt
         requires async/await throughout — REJECT.
      2. STRUCTURE MISMATCH (infrastructure): the code_files shape does not
         match the authoritative `task_shape` decision.

         When `task_shape == "non_infra"`:
           - REJECT if the prompt ships a `docker-compose.yml`,
             `init_database.sql`, `kill.sh`, or any datastore service
             definition. Non-infra tasks MUST be pure local projects using
             the runtime's native manifest + test command.

         When `task_shape == "infra"`:
           - REJECT if the prompt is missing a `docker-compose.yml` for the
             datastore(s) the scenario clearly exercises. The scenario text
             is the source of truth for which datastores are needed; pick
             the ones it actually uses, not extras from the `datastores`
             list.

         Persona-specific shape rules (apply on top of `task_shape`):
           - persona="data" / script-style: no Flask/FastAPI app file.
           - persona="mobile": no Dockerfile.
      3. STRUCTURAL DAMAGE: missing PROMPT_REGISTRY, missing format vars
         ({organization_background}, {role_context}, {competencies},
         {real_world_task_scenarios}), or wrong registry key format.
      4. SOLUTION LEAK: starter code or comments give away the solution.
      5. STRUCTURAL DRIFT FROM CURATED REFERENCES: The INSTRUCTIONS prompt
         introduces invented top-level sections that don't appear in any
         curated reference, OR misses the canonical sections, OR uses wrong
         README section names. Concretely REJECT when ANY of these is true:
           a. The prompt contains an invented top-level section like
              `## SCENARIO LOCK`, `## PROFICIENCY BOUNDARY`, `## TASK SHAPE`,
              `## QUALITY BAR`, `## RECOMMENDED TASK THEMES`, or
              `## HARD CONSTRAINTS FROM TEMPLATE CAPABILITIES` — none of
              these exist in any curated reference.
           b. The prompt is missing one of the SHAPE-INDEPENDENT canonical
              sections (required for BOTH task_shape values):
                `## GOAL`, `## CONTEXT & CANDIDATE EXPECTATION`,
                `## AI AND EXTERNAL RESOURCE POLICY`,
                `## README.md INSTRUCTIONS`,
                `## REQUIRED OUTPUT JSON STRUCTURE`,
                `## CRITICAL REMINDERS` (or `## CRITICAL NOTES`).
              The INFRA-ONLY sections `## Infrastructure Requirements` and
              `## kill.sh file instructions` are REQUIRED only when
              `task_shape == "infra"`. For `task_shape == "non_infra"` these
              two sections MUST be ABSENT — a non-infra prompt that includes
              them is a violation of HARD CONSTRAINT #7 (no docker-compose,
              no kill.sh for pure-local projects). Do not flag their absence
              on the non_infra path.
           c. The README uses a drift name like "Guidance", "Tips" (without
              "Helpful"), "Hints", or "Recommendations" instead of the
              canonical `Helpful Tips`.
           c2. The README's output-section list includes "NOT TO INCLUDE in
              README" (or any "NOT TO INCLUDE"/"do not include" heading) as a
              candidate-facing section. That guidance is an INSTRUCTION about
              what to omit — it must be a clearly-labelled directive block, NOT
              a numbered README output section. Listing it as a section makes the
              task-gen LLM render a literal "## NOT TO INCLUDE" heading into the
              candidate README. The README output sections are EXACTLY, in order:
              Task Overview, Objectives, Helpful Tips, How to Verify.
           d. The `## REQUIRED OUTPUT JSON STRUCTURE` block uses placeholder
              arrays/objects like `"outcomes": ["outcome 1", "outcome 2"]` or
              `"definitions": {{"term_1": "definition"}}` instead of the
              curated style of one-sentence descriptions per field.
           e. The JSON schema is missing the `"title"` field alongside `"name"`
              (curated prompts include both — name is kebab-case repo name,
              title is "<action verb> <subject>" display name).

    PASS conditions (accept even if not perfect):
      - All five hard-fail checks above pass.
      - INSTRUCTIONS prompt section ordering loosely matches the curated
        references — minor reordering of subsections is OK, but the canonical
        top-level sections must all be present.
      - Time constraint matches proficiency (BEGINNER: 20-30 min, BASIC: 30-45
        min, INTERMEDIATE: 45-60 min) — baked INLINE inside `### Nature of
        the Task`, not in a separate boundary section.
      - Scenario sourcing uses the soft curated language ("draw inspiration
        from ONE of the real-world scenarios", "Select a different real-world
        scenario each time") — NOT a heavy-handed SCENARIO LOCK section.

    Output `passes=true` if all hard-fail checks pass.
    Output specific, actionable `feedback` listing each issue if rejecting. Be
    concise — the generator will use this to fix the prompt.
    """

    new_prompt_file: str = dspy.InputField(desc="The candidate prompt file source")
    primary_directive: str = dspy.InputField(
        desc="AUTHORITATIVE user directive for this run, or empty. When non-empty, "
             "verify the candidate prompt actually honors it (HARD-FAIL condition 0). "
             "Empty → skip the directive check."
    )
    competencies: str = dspy.InputField(desc="Target competencies + proficiency")
    task_shape: str = dspy.InputField(
        desc='Authoritative infra decision: "infra" or "non_infra". Gate the '
             "STRUCTURE MISMATCH check on this value — non_infra must NOT ship "
             "docker-compose/kill.sh, infra MUST include docker-compose for the "
             "scenario's datastores."
    )
    runtime: str = dspy.InputField(
        desc="Primary language runtime of the matched template (e.g. python, node)"
    )
    frameworks: str = dspy.InputField(
        desc="JSON list of expected framework strings (template capabilities.frameworks), e.g. '[\"fastapi\"]'"
    )
    datastores: str = dspy.InputField(
        desc="JSON list of expected datastore names (template capabilities.datastores), e.g. '[\"postgres\"]'"
    )
    persona: str = dspy.InputField(
        desc="Reviewer persona for this combo (backend|data|mle|sdet|frontend|mobile|dba|pm|…)"
    )
    reference_prompts: str = dspy.InputField(desc="Source of similar reference prompts (for style calibration)")
    similar_tasks: str = dspy.InputField(desc="Summaries of tasks the prompt should produce")
    competency_scopes: str = dspy.InputField(
        desc="AUTHORITATIVE scope text — required skills must stay within these bounds."
    )
    detailed_skill_signal: str = dspy.InputField(
        desc="Same calibration signal Generate received: sub-skill checklist, role "
             "context, example scenarios. MAY BE EMPTY. When non-empty, use it as an "
             "additional check — does the candidate prompt's question style and "
             "complexity match what these signals suggest is appropriate? Treat large "
             "mismatches as a soft-fail (mention in feedback) but do not hard-fail on "
             "this alone — hard-fails are still the 4 conditions in the docstring."
    )
    passes: bool = dspy.OutputField(
        desc="True iff all 5 HARD-FAIL conditions are clear (scope, infra structure, "
             "structural damage, no leaks, no curated-style drift)"
    )
    feedback: str = dspy.OutputField(
        desc="Empty if passing. Otherwise: numbered list of specific issues to fix, "
             "each tied to a HARD-FAIL category. Keep under 500 chars."
    )


# ----------------------------------------------------------------------
# Agent module — generate ↔ verify loop
# ----------------------------------------------------------------------

@dataclass
class GenerationResult:
    new_prompt_file: str
    passes_verifier: bool
    verifier_feedback: str
    iterations: int
    bootstrap_mode: bool
    fallback_level: int
    references: list[Path] = field(default_factory=list)
    similar_tasks_count: int = 0
    validation: Optional[ValidationResult] = None
    input_files_metadata: dict = field(default_factory=dict)
    # Output of the shape classifier (STEP 1 of forward()). "infra" means the
    # generated prompt produces a docker-compose-shaped task; "non_infra" means
    # a pure-runtime local project. Surfaced so callers + the CLI banner can
    # show the decision.
    task_shape: str = "non_infra"
    task_shape_reason: str = ""


class PromptGeneratorAgent(dspy.Module):
    """The agent that synthesizes new prompt files."""

    def __init__(self, max_iterations: int = 5, verifier_enabled: bool | None = None):
        super().__init__()
        self.generate = dspy.ChainOfThought(GeneratePromptSignature)
        self.verify = dspy.ChainOfThought(VerifyPromptSignature)
        self.max_iterations = max_iterations
        # The LLM verifier (VerifyPromptSignature) is a STYLE/consistency
        # reviewer — advisory, non-blocking. The deterministic validator
        # (validate_prompt_file) is the CORRECTNESS gate (syntax, registry key,
        # str.format dry-run). When the verifier is disabled the loop gates on
        # the validator alone: no per-iteration verify LLM call, no churn
        # chasing canonical-style nits the prompt ships with anyway.
        # Default ON to preserve existing behaviour; set PROMPT_VERIFIER_ENABLED
        # to false/0/no/off to turn it off.
        if verifier_enabled is None:
            verifier_enabled = os.getenv(
                "PROMPT_VERIFIER_ENABLED", "true"
            ).strip().lower() not in ("false", "0", "no", "off")
        self.verifier_enabled = verifier_enabled

    def load_compiled_demos(self, compiled_path: str) -> int:
        """Load few-shot demos from a compile.py output JSON into the generator.

        The compiled file's `generate.predict.demos` list is bound to a
        TrainingSubset.generate signature; we copy those demos onto our
        Generator's underlying Predict module so they're injected into prompts
        at runtime.

        Returns number of demos loaded.
        """
        import json
        with open(compiled_path) as f:
            data = json.load(f)
        compiled_demos = data.get("generate.predict", {}).get("demos", [])

        # The compiled demos already match our GeneratePromptSignature input
        # fields (competencies, proficiency, ..., new_prompt_file). DSPy's
        # ChainOfThought wraps a Predict — assign demos to its `demos` attr.
        if hasattr(self.generate, "demos"):
            self.generate.demos = compiled_demos
        elif hasattr(self.generate, "predict") and hasattr(self.generate.predict, "demos"):
            self.generate.predict.demos = compiled_demos
        return len(compiled_demos)

    def forward(
        self,
        competencies: list[Competency],
        proficiency: str,
        env: str = "dev",
        directive: str = "",
        task_shape_override: str | None = None,
        infra_kind: str | None = None,
    ) -> GenerationResult:
        proficiency = proficiency.upper()
        directive = (directive or "").strip()
        comp_str = ", ".join(f"{c.name} ({proficiency})" for c in competencies)

        logger.info("=" * 72)
        logger.info("AGENT START — competencies=%s  proficiency=%s  env=%s  directive=%dc",
                    [c.name for c in competencies], proficiency, env, len(directive))
        if directive:
            logger.info("AGENT START — primary_directive ACTIVE: %s",
                        directive[:300].replace("\n", " "))
        logger.info("=" * 72)

        # ─── STEP 1: detailed_skill_signal from input files ───────────
        # Built FIRST because the shape classifier (STEP 3) needs the scenarios
        # + role_context + sub-skill checklist to make an informed call.
        logger.info("STEP 1 / input_files.py — building detailed_skill_signal")
        skill_signal, skill_meta = build_detailed_skill_signal(competencies, proficiency, env=env)
        logger.info("  → background_found  = %s", skill_meta.get("background_found"))
        logger.info("  → questions_prompt  = %d chars", skill_meta.get("questions_chars", 0))
        logger.info("  → role_context      = %d chars", skill_meta.get("role_context_chars", 0))
        logger.info("  → scenarios         = %d items", skill_meta.get("scenarios_count", 0))
        logger.info("  → total signal      = %d chars", skill_meta.get("signal_chars", 0))

        # ─── STEP 2: fetch competency scopes (input to the shape classifier) ─
        # Similar-tasks fetch is deferred to STEP 5 — only the infra path needs
        # it, so we skip the call entirely for non-infra to avoid burning a
        # Supabase round-trip on data the LLM will never see.
        logger.info("STEP 2 / db_queries.py — fetching competency scopes (env=%s)", env)
        supabase = init_supabase(env)
        scopes_text: list[str] = []
        for comp in competencies:
            scope = fetch_competency_scope(supabase, comp.name, proficiency)
            if scope and scope.get("scope"):
                scopes_text.append(f"[{comp.name} ({proficiency})]\n{scope['scope']}")
                logger.info("  → scope %s (%s): %d chars",
                            comp.name, proficiency, len(scope["scope"]))
            else:
                logger.warning("  → NO SCOPE for %s (%s) in Supabase",
                               comp.name, proficiency)
        scopes_str = "\n\n---\n\n".join(scopes_text) if scopes_text else "(no scopes available)"

        # ─── STEP 3: SHAPE CLASSIFIER (infra vs non-infra) ────────────
        # The first real decision. Drives the rest of the pipeline:
        #   non_infra → skip similar_tasks fetch, skip the e2b template
        #               resolver entirely; references + generate is all we need
        #   infra     → fetch similar_tasks, future template resolver, etc.
        logger.info("STEP 3 / shape_classifier.py — classifying task shape")
        # `task_shape_override` ("infra"/"non_infra") forces the shape and SKIPS the
        # classifier. The trace_ui / run_pipeline knobs for this were removed — shape
        # is AUTO-classified and the free-text `directive` (instructions) steers it —
        # but the override path is kept so a direct caller can still force a shape.
        _forced = task_shape_override if task_shape_override in ("infra", "non_infra") else None
        _infra_service = None
        if _forced:
            from generators.prompts.infra_kinds import resolve as _resolve_infra_kind
            _ik = _resolve_infra_kind(infra_kind)
            if _forced == "infra":
                _infra_service = _ik.get("service")
            reason = (f"forced by override (infra_kind={_ik['slug']})"
                      if _forced == "infra" else "forced by override")
            shape_decision = ShapeDecision(task_shape=_forced, reason=reason, raw_response="")
            logger.info("  → task_shape = %s (FORCED — classifier skipped)", _forced)
            logger.info("  → reason     = %s", reason)
        else:
            # Single classify call — the directive (instructions) is passed so it can
            # steer the infra/non-infra verdict (replacing the old force toggle).
            shape_decision = classify_task_shape(
                competencies_str=comp_str,
                competency_scopes=scopes_str,
                detailed_skill_signal=skill_signal,
                user_directive=directive,
            )
            logger.info("  → task_shape = %s", shape_decision.task_shape)
            logger.info("  → reason     = %s", shape_decision.reason)
        task_shape = shape_decision.task_shape

        # Resolver is still a no-op at prompt-gen time. The LLM honours
        # `task_shape` directly (HARD CONSTRAINT #7), so runtime / persona /
        # frameworks stay empty. For a FORCED infra task we DO seed `datastores`
        # with the chosen service so the generated prompt boots it.
        template = None
        persona = ""
        runtime = ""
        cap_frameworks: list[str] = []
        cap_datastores: list[str] = [_infra_service] if _infra_service else []
        if _infra_service:
            logger.info("  → forced-infra service hint: datastores=%s", cap_datastores)

        # ─── STEP 4: retriever (reference prompts) ────────────────────
        logger.info("STEP 4 / retriever.py — running fallback ladder "
                    "(task_shape=%s)", task_shape)
        retrieval = retrieve_references(competencies, proficiency, template=template)
        logger.info("  → bootstrap_mode = %s", retrieval.bootstrap_mode)
        logger.info("  → fallback_level = %d", retrieval.fallback_level)
        logger.info("  → references found: %d", len(retrieval.references))
        for path in retrieval.references:
            logger.info("      • %s", path.name)
        for note in retrieval.notes:
            logger.debug("      ladder: %s", note)

        # ─── STEP 5: similar tasks (infra path only) ──────────────────
        # Non-infra goes straight from references to generate, per the
        # streamlined non-infra contract: pick reference, generate.
        comp_names = [c.name for c in competencies]
        if task_shape == "infra":
            logger.info("STEP 5 / db_queries.py — fetching similar tasks "
                        "(infra path) for %s ...", comp_names)
            similar = fetch_similar_tasks(supabase, comp_names, proficiency)
            logger.info("  → similar tasks fetched: %d", len(similar))
            for t in similar[:5]:
                logger.debug("      • task_id=%s title=%r",
                             getattr(t, "task_id", "?"),
                             (getattr(t, "title", "") or "")[:60])
        else:
            logger.info("STEP 5 — skipping similar_tasks fetch "
                        "(non_infra path: references → generate)")
            similar = []

        # ─── STEP 6: assemble context strings ─────────────────────────
        refs_text = self._build_references_text(retrieval)
        tasks_text = self._build_similar_tasks_text(similar)

        logger.info("STEP 6 — context payload sizes for the LLM call")
        logger.info("  task_shape                %s", task_shape)
        logger.info("  competencies              %6d chars  %r", len(comp_str), comp_str)
        logger.info("  proficiency               %6d chars  %r", len(proficiency), proficiency)
        frameworks_json = json.dumps(cap_frameworks)
        datastores_json = json.dumps(cap_datastores)
        logger.info("  runtime                   %6d chars  %r",
                    len(runtime), runtime)
        logger.info("  persona                   %6d chars  %r", len(persona), persona)
        logger.info("  frameworks                %6d chars  %r", len(frameworks_json), cap_frameworks)
        logger.info("  datastores                %6d chars  %r", len(datastores_json), cap_datastores)
        logger.info("  competency_scopes         %6d chars", len(scopes_str))
        logger.info("  reference_prompts         %6d chars", len(refs_text))
        logger.info("  similar_tasks             %6d chars", len(tasks_text))
        logger.info("  detailed_skill_signal     %6d chars", len(skill_signal))

        demo_count = 0
        if hasattr(self.generate, "demos"):
            demo_count = len(self.generate.demos or [])
        elif hasattr(self.generate, "predict") and hasattr(self.generate.predict, "demos"):
            demo_count = len(self.generate.predict.demos or [])
        logger.info("  compiled demos loaded     %d", demo_count)

        # ─── STEP 7: Generate ⇄ Verify ⇄ Validate loop ───────────────
        logger.info("STEP 7 — Generate ⇄ Review ⇄ Validate loop "
                    "(max_iterations=%d, task_shape=%s)",
                    self.max_iterations, task_shape)
        comp_dicts = [{"name": c.name, "proficiency": proficiency} for c in competencies]
        feedback = ""
        last_result = None
        for attempt in range(1, self.max_iterations + 1):
            logger.info("  ── attempt %d / %d ──", attempt, self.max_iterations)

            logger.info("  calling Generate (ChainOfThought)...")
            gen_out = self.generate(
                primary_directive=directive,
                competencies=comp_str,
                proficiency=proficiency,
                task_shape=task_shape,
                runtime=runtime,
                frameworks=frameworks_json,
                datastores=datastores_json,
                persona=persona,
                competency_scopes=scopes_str,
                reference_prompts=refs_text,
                similar_tasks=tasks_text,
                detailed_skill_signal=skill_signal,
                feedback_from_previous_attempt=feedback,
            )
            new_prompt = self._strip_code_fence(gen_out.new_prompt_file)
            rationale_preview = (getattr(gen_out, "reasoning", "")
                                 or getattr(gen_out, "rationale", "") or "")
            logger.info("    Generate done — new_prompt_file: %d chars, "
                        "rationale: %d chars",
                        len(new_prompt), len(rationale_preview))
            if rationale_preview:
                logger.debug("    rationale preview: %s",
                             rationale_preview[:400].replace("\n", " "))

            if self.verifier_enabled:
                logger.info("  calling Review (ChainOfThought)...")
                verify_out = self.verify(
                    new_prompt_file=new_prompt,
                    primary_directive=directive,
                    competencies=comp_str,
                    task_shape=task_shape,
                    runtime=runtime,
                    frameworks=frameworks_json,
                    datastores=datastores_json,
                    persona=persona,
                    reference_prompts=refs_text,
                    similar_tasks=tasks_text,
                    competency_scopes=scopes_str,
                    detailed_skill_signal=skill_signal,
                )
                logger.info("    Review done — passes=%s feedback=%d chars",
                            verify_out.passes, len(verify_out.feedback or ""))
                if verify_out.feedback:
                    logger.info("    review feedback: %s",
                                (verify_out.feedback or "")[:400].replace("\n", " "))
            else:
                # Review step disabled — advisory pass so the loop gates on the
                # deterministic validator alone (no extra LLM call).
                verify_out = SimpleNamespace(passes=True, feedback="")

            logger.info("  calling validator.py (deterministic AST + registry "
                        "+ format-var checks)...")
            validation = validate_prompt_file(new_prompt, comp_dicts, proficiency)
            logger.info("    validator passed=%s registry_key=%r",
                        validation.passed, validation.registry_key)
            for issue in validation.issues:
                logger.warning("    validator issue: %s", issue)
            for warn in validation.warnings:
                logger.info("    validator warning: %s", warn)

            last_result = (new_prompt, verify_out, validation, attempt)
            if verify_out.passes and validation.passed:
                logger.info("  ✓ generated prompt accepted at attempt %d "
                            "— exiting loop", attempt)
                break

            parts = []
            if not verify_out.passes and verify_out.feedback:
                parts.append(f"Reviewer feedback:\n{verify_out.feedback}")
            if not validation.passed and validation.issues:
                parts.append(
                    "Deterministic validator issues (MUST fix):\n- "
                    + "\n- ".join(validation.issues)
                )
                # Concrete rewrite shape for the most common false-positive trap:
                # the agent-realness guard now flags AFFIRMATIVE fake-mandates
                # (e.g. "use a FakeLLM"), not bare prohibitions. If the validator
                # tripped on that, give the LLM a working rewrite template so the
                # next attempt converges instead of looping on the same prose.
                if any("COMMANDS a FAKE LLM/agent" in i for i in validation.issues):
                    parts.append(
                        "Rewrite shape that will pass:\n"
                        "- State the affirmative requirement first: 'The agent "
                        "calls a REAL model via litellm (or the anthropic/openai "
                        "SDK) on the candidate's key.'\n"
                        "- Then list prohibitions, ONE banned term per short "
                        "sentence, each starting with 'NEVER':\n"
                        "    NEVER use a FakeLLM.\n"
                        "    NEVER use a regex / keyword intent parser as the "
                        "agent's reasoning.\n"
                        "    NEVER use a deterministic stand-in for the model.\n"
                        "    NEVER use time.sleep / asyncio.sleep to simulate the "
                        "agent.\n"
                        "- Make clear: fixtures may make local tool INPUTS "
                        "deterministic; they must NOT replace the model's "
                        "reasoning."
                    )
            feedback = "\n\n".join(parts)
            logger.info("  next iteration will receive feedback (%d chars)",
                        len(feedback))

        new_prompt, verify_out, validation, iterations = last_result
        logger.info("AGENT DONE — generated %d chars over %d iteration(s)",
                    len(new_prompt), iterations)

        return GenerationResult(
            new_prompt_file=new_prompt,
            passes_verifier=verify_out.passes,
            verifier_feedback=verify_out.feedback,
            iterations=iterations,
            bootstrap_mode=retrieval.bootstrap_mode,
            fallback_level=retrieval.fallback_level,
            references=retrieval.references,
            similar_tasks_count=len(similar),
            validation=validation,
            input_files_metadata=skill_meta,
            task_shape=task_shape,
            task_shape_reason=shape_decision.reason,
        )

    @staticmethod
    def _build_references_text(retrieval: RetrievalResult) -> str:
        """Concatenate reference prompt sources with headers."""
        parts = []
        for path in retrieval.references:
            try:
                content = path.read_text(encoding="utf-8")
            except Exception as e:
                parts.append(f"# === {path.name} (could not read: {e}) ===")
                continue
            parts.append(
                f"# ===== Reference: {path.name} =====\n"
                f"# Path: {path.relative_to(Path.cwd()) if path.is_absolute() else path}\n\n"
                f"{content}"
            )
        if not parts:
            parts.append("(no reference prompts found — bootstrap mode using scopes only)")
        return "\n\n".join(parts)

    @staticmethod
    def _build_similar_tasks_text(tasks: list[TaskExample]) -> str:
        if not tasks:
            return "(no similar tasks in DB — bootstrap mode)"
        return "\n\n---\n\n".join(t.summary() for t in tasks[:5])

    @staticmethod
    def _strip_code_fence(text: str) -> str:
        """Remove ```python ... ``` wrappers if the LLM added them."""
        text = text.strip()
        if text.startswith("```"):
            # Strip first line (```python) and last line (```)
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)
        return text
