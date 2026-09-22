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
from flows.tech.stages.prompts.db_queries import (
    TaskExample,
    fetch_competency_scope,
    fetch_similar_tasks,
    init_supabase,
)
from flows.tech.stages.prompts.input_files import build_detailed_skill_signal
from flows.tech.stages.prompts.retriever import retrieve_references, RetrievalResult
from flows.tech.stages.prompts.shape_classifier import ShapeDecision, classify_task_shape
from flows.tech.stages.prompts.validator import ValidationResult, validate_prompt_file
from flows.tech.stages.generate.runtime_resolver import resolve_plan

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
# The advisory verify step is evaluative, not creative — run it on a cheap model
# (nano) instead of the strong runtime model. Override via PROMPT_VERIFIER_MODEL.
DEFAULT_VERIFY_MODEL = os.getenv("PROMPT_VERIFIER_MODEL", "openai/gpt-5.4-nano")


def _build_lm(model: str) -> "dspy.LM":
    """Build a DSPy LM for ``model`` with the right provider routing.

    Routing logic:
      - Models prefixed `openrouter/...`  → OpenRouter direct (uses OPENROUTER_API_KEY)
      - All other models                  → Portkey gateway (uses OPENAI_API_KEY)

    OpenRouter is for cheap/free open-source models (DeepSeek, Qwen, Gemma).
    Portkey is for OpenAI/Anthropic models routed through our existing gateway.
    """
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
        return dspy.LM(
            model=f"openrouter/{bare_model}",
            api_key=or_key,
            api_base="https://openrouter.ai/api/v1",
            max_tokens=16000,
            temperature=temperature,
        )

    api_key = os.getenv("OPENAI_API_KEY")
    portkey_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY in environment.")

    from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders

    provider = "anthropic" if "anthropic/" in model or "claude" in model else "openai"
    return dspy.LM(
        model=model,
        api_key=api_key,
        api_base=PORTKEY_GATEWAY_URL,
        extra_headers=createHeaders(provider=provider, api_key=portkey_key),
        max_tokens=16000,
        temperature=temperature,
    )


def build_verify_lm() -> "dspy.LM":
    """LM for the advisory prompt-VERIFY step. Verification is evaluative, not
    creative, so it runs on a cheap model (``gpt-5.4-nano`` by default) instead
    of the strong runtime model — override via ``PROMPT_VERIFIER_MODEL``."""
    return _build_lm(DEFAULT_VERIFY_MODEL)


def configure_dspy(model: Optional[str] = None, mode: str = "runtime") -> None:
    """Wire DSPy to the right LLM provider (see :func:`_build_lm`).

    Args:
        model: explicit model override; takes precedence over `mode` defaults.
        mode:  "runtime" (default, strong model) or "compile" (cheap model).
    """
    if model is None:
        model = DEFAULT_COMPILE_MODEL if mode == "compile" else DEFAULT_RUNTIME_MODEL

    dspy.settings.configure(lm=_build_lm(model))

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
      - "**CRITICAL — entrypoint/command must not mix forms**: if `entrypoint:`
        is overridden as a LIST (exec form, e.g. `['/bin/bash', '-lc']`),
        `command:` MUST ALSO be a LIST with exactly one element holding the
        full shell script string. NEVER pair a list `entrypoint:` with a
        STRING `command:` — Compose shell-splits the string into separate
        tokens before appending them to entrypoint, so only the first word
        reaches `bash -c` as the script and everything else (flags, paths,
        `&&`, the rest of the pipeline) becomes bash's positional parameters
        and is silently dropped (e.g. `mkdir -p /a && tail -f /dev/null`
        breaks into `mkdir: missing operand`). Simplest safe pattern: omit
        `entrypoint:` and put the whole invocation as a LIST in `command:`."
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

    Each of the four MUST be emitted as an actual markdown heading (`## Task
    Overview`, `## Objectives`, `## Helpful Tips`, `## How to Verify` — `##`
    or `#`, consistently). The generated prompt's REQUIRED OUTPUT JSON
    STRUCTURE description for the "README.md" key MUST say so explicitly,
    e.g. "...containing exactly Task Overview, Objectives, Helpful Tips, and
    How to Verify in that order, each written as a markdown heading (##
    Task Overview, ## Objectives, ## Helpful Tips, ## How to Verify) — a
    plain unmarked text line with the section name is INVALID and counts as
    a missing section." Without this, the downstream task-gen LLM sometimes
    emits the four names as bare plain-text lines with no `##`, which renders
    as an unstructured wall of text with no visual section breaks in the
    product UI.

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
    Anywhere connection details DO legitimately appear (docker-compose
    healthchecks, run.sh readiness probes, How to Verify commands), the host
    must use `localhost` — the task runs inside an E2B sandbox where
    datastore ports are bound to `127.0.0.1` and the candidate connects from
    the sandbox terminal (e.g. `redis-cli -h localhost -p 6379`,
    `psql -h localhost -p 5432`). Never use a droplet IP or any remote-host
    placeholder — there is no droplet.

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
            PLAIN LANGUAGE (reviewer decision 2026-09-18): short sentences a
            non-specialist can follow — no semicolon run-ons chaining three
            clauses. Introduce each domain term in plain English the first
            time ('when someone has a health problem during it, that gets
            written up as an adverse-event report'), prefer everyday verbs
            ('check', 'look it up', 'hands each report to') over formal ones
            ('consult', 'delegates'), and never name internal machinery the
            candidate hasn't met yet — 'the automated checks stayed green'
            beats 'readiness and the invariant checks stayed green'.
            Splitting into two short paragraphs at the natural break (what
            the system is / what the teams reported) is preferred over one
            dense paragraph.
          – Objectives:    BASIC/BEGINNER 4-6 bullets max; INTERMEDIATE/ADVANCED
            3-4 bullets max (fewer, tighter is better).
          – Helpful Tips:  4-5 bullets max.
          – How to Verify: 3-5 bullets max.

      • Per-section framing rules the generated prompt MUST include:
          – Objectives (PROFICIENCY-CONDITIONAL — branch on the `proficiency`
            input; the two levels are deliberately different):

              · BASIC / BEGINNER — objectives MAY be explicit and directive.
                Each is a full, context-rich sentence stating what is broken or
                missing, its observable impact, and what a resolved state looks
                like. Being concrete about WHAT to achieve is fine and expected
                at this level (still don't paste the literal answer). This is
                the correct style for BASIC — do not make BASIC open-ended.
                GOOD (basic): 'The product search endpoint returns results in
                4-6 seconds under normal load; after your changes it should
                respond in under 500ms for typical query patterns.'

              · INTERMEDIATE / ADVANCED — objectives are PLAIN GOAL
                STATEMENTS, whatever the task's shape (repair or design/build;
                reviewer decisions 2026-09-15 and 2026-09-18). Each objective
                is ONE SHORT PLAIN SENTENCE (roughly 5-15 words; shorter is
                better) naming the outcome the system must achieve — no
                stakeholder framing ('The on-call engineer expects…'), no
                'because' clause, no mechanism. Imperative mood is correct
                and expected. One concern per bullet; split a bullet that
                bundles two separable concerns.
                Describe the 'what', NEVER the 'how': do NOT name the API,
                library, framework, pattern, algorithm, or config knob — and
                do NOT name any file, file path, directory, function, method,
                class, variable, table, or ANY other direct code reference.
                Do NOT describe the CURRENT broken behaviour or use phrasing
                like "currently does X" / "after your changes" — state the
                desired end-state as a standing requirement, not a
                before/after diff. The candidate must discover both the
                mechanism AND where to change it.
                Approved reference set (repair, ADVANCED — the target shape
                at both levels):
                  'Keep decisions with the people who should make them.'
                  'Make triage timely and reliable for every team that
                   depends on it.'
                  'Keep case records consistent.'
                  'Make every decision auditable.'
                Short, verb-led, one class word each, similar length and
                weight — plus one judgment bullet ('Surface whatever else a
                safety physician would refuse to sign off on.').
                BAD (too terse, bare label): 'Improve query performance.'
                BAD (describes current-vs-after, not standing outcome): 'The
                product search endpoint returns results in 4-6 seconds under
                normal load; after your changes it should respond in under
                500ms for typical queries.'
                BAD (names a file / code): 'Fix the lifecycle rule in main.tf so
                transitions apply to closed objects.'
                BAD (stakeholder-framed — forces the rule out): 'An on-call
                engineer should be able to trust that a retried message never
                causes a customer to see the same side effect twice.'
                GOOD (plain goal statement of the same requirement): 'Keep
                repeated deliveries from ever producing a duplicate outcome.'

                Still DECIDE THE TASK'S SHAPE first — the objective style no
                longer branches on it, but How to Verify does (see below):
                  · REPAIR task — something exists and is broken; the candidate
                    finds the cause and fixes it.
                  · DESIGN / BUILD task — nothing is broken in a reportable way;
                    the candidate builds or reworks something to reach a
                    standard (greenfield builds, pipeline/architecture design,
                    "rework X so it is trustworthy").

                THE THIRD LEAK — ENUMERATED INSTANCES. Beyond naming a
                mechanism or stating the rule, an objective leaks by LISTING
                THE SPECIFIC THINGS the candidate is supposed to discover.
                Name the CLASS of concern; never enumerate its instances. The
                list of instances is the investigation answer key: it tells
                the candidate exactly which N things to go and check, and
                finding those N things by reading the code and the data IS
                the skill being assessed. Two real bullets from a shipped
                task, and their corrected forms:
                  BAD:  'Communicate invalid date or lifecycle choices clearly
                        to users.'
                        (enumerates the two inputs that need validation)
                  GOOD: 'Communicate errors in user inputs clearly.'
                  BAD:  'Preserve accurate money, status, and deletion
                        semantics in displayed rows.'
                        (enumerates the three data traps to look for)
                  GOOD: 'Preserve data semantics in the rows displayed.'
                The GOOD forms are not vaguer about the OUTCOME — the rows
                must still be semantically correct, the inputs must still be
                validated — they only withhold WHICH inputs and WHICH
                semantics, because working that out from the schema, the seed
                data and the existing code is the task.

                THE AGENT-PASTE TEST — apply it to EVERY objective. Imagine
                the bullet is pasted, on its own, into an AI coding agent that
                has NOT been given the repository. If that agent could already
                tell you what to implement, the bullet is too specific and
                must be rewritten. A correct objective leaves the agent unable
                to act until a person has read the codebase and the data and
                turned the objective into concrete work — that reading is
                what separates a candidate who understands the task from one
                who forwards it. 'Communicate invalid date or lifecycle
                choices clearly' fails the test (the agent knows: validate
                date, validate lifecycle). 'Communicate errors in user inputs
                clearly' passes (the agent cannot know which inputs exist).

                ONE SHARED CLASS VOCABULARY (reviewer decision 2026-09-18) —
                the objective set is written on a small shared vocabulary of
                class words (e.g. bounded, consistent, timely, clear,
                auditable, private, reliable), one class word per bullet:
                keep the verb, land the bullet on its class word, keep the
                bullets similar in length and weight so they read as one
                list. The SAME class words are then reused verbatim in
                `question` and in `short_overview` bullet 2, so every
                candidate-facing surface reads as one system rather than
                three paraphrases of it. Approved set (repair, ADVANCED):
                  'Uploaded context should stay bounded by the study's
                   rules, never override them.'
                  'Participant privacy should hold everywhere the assistant
                   responds or keeps a record.'
                  'Refusals should be clear, and point people to the right
                   next step.'
                  'Every intervention should stay auditable, without
                   exposing private details.'
                — and the matching short_overview bullet 2: 'This repair
                needs to keep the assistant's behavior bounded by the
                study's rules, protect participant privacy throughout, and
                make every refusal and intervention clear and auditable.'

                QUESTION-FORM OBJECTIVES are allowed and encouraged for
                design/build tasks. An open-ended ask may be phrased as a
                genuine question that invites the candidate to reason beyond
                the stated scope:
                  GOOD: 'What other filters can you think of that may be
                        appropriate for the use case?'
                This form is inherently open — it has no single correct
                completion — and it rewards judgment, which is exactly what a
                closed instruction cannot measure. Use it for the objective
                where you most want the candidate to extend the design rather
                than execute it.

                PROFICIENCY SCALING for these three rules:
                  · INTERMEDIATE — objectives stay at class level. At most
                    ONE objective in the whole README may name a specific
                    instance, and only if the task is genuinely unscopable
                    without it.
                  · ADVANCED — STRICT. ZERO enumerated instances anywhere in
                    the Objectives. EVERY objective must pass the agent-paste
                    test. Include AT LEAST ONE question-form objective. The
                    standard at ADVANCED is that a candidate must be able to
                    derive what needs doing ONLY by reading the objectives,
                    the code and the data together — the objectives alone
                    must never be a sufficient instruction to anyone,
                    human or agent.
                GOOD (design/build): 'Build a pipeline that makes the overall
                build process as efficient as possible.'
                GOOD (design/build): 'Make deployments easy to identify,
                understand, and recover when needed.'
                GOOD (design/build): 'Keep services aligned with the shared
                code they depend on throughout the development process.'
                GOOD (design/build): 'Ensure deployment configuration is
                handled securely and reliably.'
                BAD (design/build, states the rule not the goal): 'A change to
                one service should create a new image only for that service.'
                BAD (design/build, stakeholder framing forces the rule out):
                'The on-call engineer needs deployed images traceable to the
                exact commit that produced them, because rollback depends on
                it.'
                The test is the same at both levels and both shapes: mood is
                not the lever, SPECIFICITY is. A vague instruction hides more
                than a precise observation. If a bullet could be pasted into
                the codebase as the change description, it is too specific.
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
            DESIGN / BUILD tasks (see the shape decision in the Objectives
            rules above) invert
            this: the bullets name an EXPERIMENT TO RUN and where to look, and
            MUST NOT state what the correct result is — the candidate judges
            that against the Objectives. This is the rule most easily got
            wrong, and getting it wrong silently undoes the whole open-ended
            README: on a design/build task the pass condition IS the
            specification the Objectives deliberately withheld, and the
            candidate reads both sections. Pattern: "<make this change>, and
            <where to look>", one probe per Objective, in the same order.
            GOOD (design/build probe): 'Change a single service, run the
            pipeline, and look at what it actually produced.'
            GOOD (design/build probe): 'Change only the shared code, and check
            which services end up affected.'
            GOOD (design/build probe): 'Make a change that touches no service
            at all, and see what the pipeline decides to do.'
            BAD (design/build, states the pass condition): 'A change confined
            to one service should result in exactly one new image for that
            service.'
            BAD (design/build, states the pass condition): 'Each image produced
            should carry the exact commit identity that produced it.'
            At most ONE bullet may reference the task environment directly.
            Before emitting, read the Objectives and How to Verify TOGETHER as
            a candidate would: between them they must still not give away any
            rule the candidate is meant to derive.
            PROBES MUST NOT RESTORE WHAT THE OBJECTIVES WITHHELD. Naming the
            scenario in a probe is allowed, but if an Objective deliberately
            says 'preserve data semantics' (withholding money / status /
            deletion), a probe that says 'compare money values and confirm
            soft-deleted rows are excluded' has handed the withheld list
            straight back. Keep probes at the same instance-level as the
            Objectives: 'compare a few displayed rows with the stored
            records, and review consistency' names WHERE to look without
            naming WHICH semantics to check. At ADVANCED this is strict —
            no probe may enumerate instances the Objectives left for the
            candidate to discover.
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
      "question"       — full candidate-facing task description, written as a
                         scenario paragraph + a direct imperative ask. MUST
                         NOT leak the answer: no file names or paths (e.g.
                         `services/api/Dockerfile`), no function/method
                         references (e.g. `calculateTotal()`), no directory
                         paths, and no direct solution statements ("the bug
                         is in...", "you should change...", "change line
                         42"). The candidate must diagnose WHERE and WHAT is
                         wrong from the scenario — never be told.
                         ALTITUDE (applies to every task, and is the rule most
                         often broken here): `question` is the PRIMARY
                         candidate-facing description, so a `question` that
                         enumerates the required behaviours undoes an
                         open-ended README on its own. State the expectations
                         at the SAME altitude as the README Objectives, using
                         the same words — the SAME class words the Objectives
                         land on (see ONE SHARED CLASS VOCABULARY in the
                         Objectives rules) — never the mechanisms that satisfy
                         them. Three moves, plain prose, no bullets: (a) who
                         the candidate is and what the system is; (b) the
                         situation — something exists and runs but is not
                         trusted / not working as needed, and NOTHING about why
                         or in what way; (c) what the work must achieve, as
                         outcomes.
                         GOOD: "...Your job is to rework and extend it so that
                         the overall build process becomes as efficient as
                         possible, deployments are easy to identify,
                         understand, and recover when needed, and services can
                         progress through the build process independently
                         wherever possible."
                         BAD (enumerates the mechanisms): "Build only the
                         services truly affected by a source change, tag
                         container images with the exact commit, run unrelated
                         affected builds concurrently, and perform
                         main-line-only releases where the deployment target
                         comes from the secret store."
                         `question` and the README Objectives must be written
                         TOGETHER and checked against each other — this is the
                         field most likely to drift back down into mechanisms.
                         The ENUMERATED-INSTANCES rule and the AGENT-PASTE
                         TEST from the Objectives section apply here in full:
                         `question` names classes of concern ('errors in user
                         inputs', 'data semantics'), never the instances
                         ('date or lifecycle', 'money, status, and deletion').
                         At ADVANCED, `question` must also pass the
                         agent-paste test — pasted alone into an AI coding
                         agent without the repo, it must not be a sufficient
                         instruction to implement anything.
      "code_files"     — object mapping filepath → file contents (verbose
                         per-file descriptions; see references). Every key the
                         generated prompt lists in its REQUIRED OUTPUT JSON
                         STRUCTURE's code_files example MUST be a REAL, concrete
                         file path with a real extension appropriate to the
                         selected stack (e.g. `services/api/main.go`,
                         `src/spark_task/main.py`) — NEVER a placeholder-style
                         key like `additional_files_as_needed`,
                         `selected_stack_manifest_and_source`,
                         `local_config_files`, `supporting_scripts`, or
                         `or_verify_files`. The downstream task-gen LLM copies
                         example keys literally into the repo it produces — a
                         placeholder-style key becomes an actual file with that
                         literal (nonsensical) name in the candidate's repo. If
                         the exact file set genuinely cannot be known ahead of
                         time (e.g. "one file per selected host stack"), mark
                         that key's line "EXAMPLE ENTRY ONLY — emit the REAL
                         file(s) for the selected stack using their true names"
                         and require the downstream LLM to substitute real
                         names, never emit the placeholder text itself.
      "answer"         — evaluator-facing high-level solution approach
      "definitions"    — object of term → definition pairs
      "hints"          — single line nudging investigation WITHOUT revealing
                         the fix. Name a starting EXPERIENCE, never a
                         component: 'Start with one request whose answer needs
                         two sources, and follow it from the question to the
                         final wording' — not 'Trace how evidence scope,
                         provenance, and cache identity move through the
                         layers' (each noun there is a pointer to a file).
      "outcomes"       — 2-3 lines on measurable expected results, written at
                         the SAME altitude as the README Objectives (one line
                         per objective's class of concern, plus the standing
                         code-quality line) — never a list that enumerates the
                         seeded contexts or instances the candidate is meant
                         to discover.
      "pre_requisites" — bullet list of ASSUMED PRIOR KNOWLEDGE / skills the
                         candidate already brings. DECLARATIVE capability phrases
                         ONLY ("Python 3.11 proficiency", "Comfort with…",
                         "Familiarity with…", "Understanding of…", "A provider
                         key via .env"). NEVER imperative setup/verify steps
                         ("Run…", "Use…", "Test…", "Configure…", "Install…") —
                         those are README How-to-Verify content, not prerequisites.
      "short_overview" — EXACTLY three bullets, one sentence each, in plain
                         non-technical business English. This is the "Problem
                         Statement" card the candidate reads BEFORE opening the
                         task, so it must never out-specify the README.
                           1. What the SYSTEM is — what it does, for whom, and
                              the one-line situation with it today. Context,
                              not a defect list.
                           2. What the WORK must achieve, opening "This rework
                              needs to ..." / "This redesign needs to ..." /
                              "This repair needs to ..." / "This calls for ...".
                              Written on the SAME class words as the README
                              Objectives (see ONE SHARED CLASS VOCABULARY in
                              the Objectives rules) — the card and the README
                              must sound like one system, not two paraphrases.
                           3. What separates a strong submission — the
                              dimensions someone would actually grade on,
                              closing on whether the design reasoning is sound.
                              Vary the opener ("A strong submission is judged
                              on ...", "The quality of a submission is measured
                              by ...", "What separates a strong submission
                              is ..."). It must read as EVALUATION CRITERIA,
                              not a restatement of bullet 2 — the approved
                              pattern is 'whether these guarantees hold across
                              <the harder contexts: later turns, failure
                              paths, bursts> — not just the first request —
                              and whether the reasoning behind the fix is
                              sound.'
                         VOICE — none of the three may be an instruction to the
                         candidate. If a bullet opens with an imperative verb
                         ("Rework...", "Make...", "Ensure...", "Build...") or
                         reads naturally with "You" or "The candidate" inserted
                         at the front, it is WRONG — restate it as a fact about
                         the system or the work.
                         ALTITUDE — bullet 2 states OUTCOMES, never the rules
                         that achieve them. The voice rule alone does NOT catch
                         this: a correctly-voiced bullet that simply lists every
                         requirement is the common failure, and it hands over
                         the specification on the preview screen.
                         GOOD (bullet 2): "This rework needs to make the build
                         process efficient, keep what gets deployed easy to
                         identify and recover, let unrelated services progress
                         independently while staying consistent with the shared
                         code they depend on, and make sure only sound code is
                         released with its deployment configuration handled
                         securely."
                         BAD (right voice, wrong altitude — lists the rules):
                         "The delivery workflow needs to rebuild only the
                         services a commit actually affects, produce images
                         traceable to the exact commit that built them, refresh
                         every service when shared code changes, and release
                         only from the main line."
                         BAD (candidate-directed): "Rework the CI delivery
                         pipeline for the monorepo."
                         No backticks, no file paths, no mechanism names, and no
                         enumeration of the seeded defects.

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

    Code complexity + starter-code VOLUME MUST scale with proficiency. The
    generated prompt MUST instruct the task-gen LLM accordingly (branch on the
    `proficiency` input):
      - BASIC / BEGINNER — a small, focused starter codebase is appropriate:
        a handful of files with one clear area to fix. Keep the surface area
        small and the reasoning shallow.
      - INTERMEDIATE / ADVANCED — the starter codebase MUST be substantial and
        realistic, NOT a toy snippet. Require MULTIPLE interacting modules /
        files in a real project layout, with non-trivial existing logic the
        candidate must read and reason about before changing, and changes that
        span MORE THAN ONE file. Do NOT ship only a small set of code or a
        single short file at these levels — the volume and intricacy of the
        starter code should reflect the level's real seniority (INTERMEDIATE:
        3-5 years; ADVANCED: 6+ years — never write "3-5+" for ADVANCED). Higher
        proficiency means a LARGER, more interconnected codebase and deeper
        reasoning, never merely a trickier one-liner. The candidate should have
        to navigate a meaningful codebase, not just edit one obvious spot.

    PRODUCTION REALISM at INTERMEDIATE / ADVANCED (the generated prompt MUST
    embed these as requirements on the task-gen LLM). A candidate at these
    levels has years of hands-on time in this stack; the task must feel like
    an afternoon inside a real production repository, not an exercise. Three
    dimensions, all required:

      (a) DATA — schema and seed content the candidate must actually
          investigate. This is the most commonly under-built part and the one
          that most cheapens a task.
            · Schema: SEVERAL related tables with real foreign keys, indexes,
              constraints, status/enum columns and audit columns (created_at,
              updated_at, soft-delete/archived flags) — never one flat table.
              Name things the way the domain would.
            · Volume: seed enough rows that the answer CANNOT be seen by
              eyeballing the seed file — the candidate must query, filter,
              aggregate or explain-plan to find it. Hundreds to a few thousand
              rows is the right order of magnitude.
            · Content: real data is messy, and the mess is where the signal
              is. Include the awkward cases a production table actually
              carries — NULLs in nullable columns, duplicate-looking rows that
              differ in one field, soft-deleted/archived rows that must be
              excluded, unicode and apostrophes in names, timestamps that span
              timezone and day boundaries, money as exact decimal (never
              float), out-of-order or back-dated sequences, and a few rows at
              the boundary of whatever rule the task is about.
            · The seeded data must be internally CONSISTENT: foreign keys
              resolve, totals reconcile, statuses follow a legal lifecycle. A
              candidate who investigates must find a coherent world, not
              noise.
            · Generate the seed programmatically where volume calls for it
              (a loop/generator in the init script), not by hand-writing
              thousands of literal INSERT rows.

      (b) SETUP — the project must be configured the way a real one is:
          dependency manifests with pinned versions, environment/config
          handling with sane defaults, database init/migration files, service
          healthchecks, and the conventional project layout for the stack.

      (c) PRODUCTION CONCERNS — pick only the ones the chosen scenario
          genuinely exercises, and weave them into the existing code rather
          than bolting them on: pagination over large result sets, N+1 access
          patterns, transaction boundaries and isolation, partial failure and
          retry, idempotency, validation at the trust boundary, tenancy or
          authorization scoping, cache invalidation, timezone and locale
          handling, money precision, index usage under volume, and migration
          safety.

      HARD BOUND — realism must not break the readiness gate. Everything above
      must still install, build, seed and start INSIDE run.sh's time budget on
      a small sandbox (2 vCPU, ~2 GB RAM). Do NOT actually seed millions of
      rows, pull heavyweight images, or add dependencies that take minutes to
      install. A scenario's PROSE may describe a table as having 50M rows in
      production — that is fictional context for the narrative — but the DB
      the task actually creates must be seeded in seconds. Realistic SHAPE and
      realistic MESS are what matter, not raw volume.

    ADVANCED SYSTEM COMPLEXITY (ADVANCED only — applies to EVERY stack, not
    just AI). PRODUCTION REALISM above makes the code and data feel real; this
    rule makes the PROBLEM hard in the way a senior engineer's problems are
    hard. An ADVANCED task must be a real system whose difficulty comes from
    the interaction of concerns, not from a trickier version of one concern.
    The generated prompt MUST require the task-gen LLM to build in ALL FIVE
    of the following, each instantiated for the chosen stack:

      (1) REAL INFRASTRUCTURE, NOT A STAND-IN. The component the task is
          about must genuinely run: a real vector database, a real message
          broker with real consumer groups, a real relational database whose
          query plans can be read, a real CI runner, a real cluster. Never an
          in-memory dict standing in for the store, a list standing in for
          the queue, a stubbed model call, or a "simulated" pipeline. This
          extends the existing no-FakeLLM rule to every kind of
          infrastructure: if the candidate is being assessed on X, X must be
          real. Use the datastores and tools the resolved template actually
          provides — do not invent infrastructure the sandbox lacks.

      (2) A SCOPING AXIS THAT A NAIVE SOLUTION IGNORES. The data or state has
          a dimension — version, tenant, region, environment, time window,
          partition, lineage — such that an implementation which ignores it
          still RUNS and still returns PLAUSIBLE results, but returns the
          WRONG ones. This is the heart of ADVANCED difficulty: the failure
          is silent and semantic, not a crash. The candidate must discover
          the axis exists and design isolation/attribution around it.

      (3) TRACEABILITY. Every output the system produces must be attributable
          back to the exact inputs it was built from, precisely enough that
          an auditor could re-derive it: which passages, which offsets, which
          upstream events, which commit, which manifest. Not "logs exist" —
          a resolvable, exact provenance chain.

      (4) THE QUALITY GATE IS ITSELF A DELIVERABLE. The task ships (or asks
          for) an evaluation / verification layer that the candidate must
          make TRUSTWORTHY, and the task judges that layer as a first-class
          artefact: it must report distinct failure dimensions SEPARATELY
          (not one blended score), it must catch a DELIBERATE regression in
          each dimension, and it must tell a genuine regression from noise.
          A gate that only says "pass/fail" is a BASIC-level gate.
          NOTE: this is the task's OWN eval harness that the candidate
          improves — it is distinct from the pipeline's grading tests
          (invariants/ + hidden grading/), which remain as specified in the
          ADVANCED test-split rule.

      (5) REPRODUCIBILITY UNDER RE-RUN. Running the system, and its quality
          gate, on unchanged code and unchanged data must give the identical
          verdict. Any source of nondeterminism the stack introduces — model
          sampling, unordered iteration, wall-clock defaults, unpinned
          versions, race-prone consumers — is something the candidate must
          find and control.

      HOW THIS INSTANTIATES — the same five properties, four stacks. Use
      these as the pattern; pick the stack's own concrete forms:
        · RAG / Vector DB / AI Evaluation: (1) real vector DB (Qdrant or
          pgvector) + real embedding + real answer synthesis; (2) documents
          exist in many VERSIONS across many TENANTS (trials, products,
          jurisdictions) and each question is scoped to one version in force
          on a date — retrieval that ignores version/tenant returns fluent,
          cited, wrong answers; (3) citations resolve to the exact chunk and
          character span used; (4) an eval suite over a curated question set
          that reports groundedness and version-attribution as SEPARATE
          metrics and catches a planted regression in each; (5) same corpus +
          same code = same scores, so sampling temperature, chunk ordering
          and embedding version are all pinned.
        · Event streaming / Kafka: (1) real broker, real consumer groups;
          (2) events arrive out of order across PARTITIONS and a consumer that
          ignores partition/offset semantics produces plausible aggregates
          that are wrong; (3) every derived record carries the offsets it was
          folded from; (4) a replay harness that separately reports ordering
          violations vs duplicate-processing vs data loss; (5) replaying the
          same log yields byte-identical output.
        · Data platform / PostgreSQL: (1) real database, real EXPLAIN plans;
          (2) SOFT-DELETED / BACK-DATED / MULTI-TENANT rows that a naive join
          silently includes or double-counts; (3) every reported total is
          decomposable to the row ids that produced it; (4) a reconciliation
          suite reporting row-multiplication vs precision loss vs tenant
          leakage separately; (5) same seed = same totals, to the cent.
        · CI/CD / platform: (1) real pipeline runner, real deploy target;
          (2) a MONOREPO where shared-dependency changes must invalidate every
          consumer — a pipeline that ignores the dependency graph still goes
          green while shipping stale builds; (3) every deployed artefact is
          traceable to the exact commit and inputs; (4) a verification stage
          reporting build-scope correctness vs traceability vs gating as
          separate checks; (5) same commit range = same set of built
          artefacts.

      SCENARIO-STAGE LINK: the ADVANCED scenario guardrail already demands
      "cross-cutting production-grade work woven into ONE coherent problem".
      Properties (2)-(5) are HOW that coherence is achieved — they are the
      threads that tie the concerns together, so a scenario missing them
      tends to degrade into a checklist of unrelated hardening items. The
      README still obeys every open-endedness rule above: the five
      properties are what the SYSTEM must have, and the generated prompt must
      express them as outcomes at class level (see THE THIRD LEAK), never as
      the enumerated instances that make them true.

      STILL BOUNDED by the readiness gate: "real infrastructure" means the
      template's Qdrant/Postgres/broker actually running with a small,
      internally-consistent, fast-to-seed dataset — never a large corpus,
      never a heavyweight model download at run.sh time.

      FOCUS — ONE AXIS, NOT A PILE (the generated prompt MUST carry this):
      the five properties are five ASPECTS of one problem, not five problems,
      and the scenario stage now enforces exactly that (one scoping axis,
      3 "Your Task" bullets, 4 at most). The generated prompt must NOT
      re-expand the scenario at task time. Concretely, the prompt module:
        - MUST say the task is built around the ONE scoping axis the selected
          scenario names; traceability is traceability OF that axis, the
          quality gate measures correctness ALONG it, reproducibility is of
          that gate. Do not write "combine several concepts" or offer a menu
          of unrelated failure modes as "suitable combinations".
        - MUST NOT introduce concerns the scenario does not name: cost /
          token budgets, latency or p95 targets, canary or blue/green rollout
          mechanics, prompt-injection hardening, PII redaction, hybrid-search
          calibration, fail-closed refusal policy, observability dashboards.
          Each is a separate ADVANCED task. Do not list "latency" or "cost"
          among the quality-gate dimensions unless the axis IS a measurement.
        - MUST NOT mandate a fixed file inventory that presupposes those
          concerns (a rerank module, a cache module, a sparse/hybrid module,
          a rollout module). The layout follows the scenario: list only the
          files the selected axis needs, and say so.
        - Success criteria / outcomes are observable results of the one axis,
          never SLA-style numeric thresholds — thresholds are policy the
          candidate chooses and defends.
      Calibration: a clinical-protocol RAG task is "answers use only the
      amendment in force for the site on the date; every answer cites the
      exact passages; the eval reports groundedness and version-attribution
      separately and catches a planted regression; re-run is identical". It
      is NOT that plus cost caps, p95, canary, injection and PII. Same rule
      for Kafka, Postgres, CI/CD and every other stack.

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
        where <key> is exactly: 'Name1 (LEVEL), Name2 (LEVEL)' — competency
        names with proficiency in parentheses, joined by ", " and sorted.

        THE SORT IS PYTHON `sorted()` — CODEPOINT ORDER, NOT CASE-INSENSITIVE
        ALPHABETICAL. Every uppercase letter sorts BEFORE every lowercase one
        ('E' is 0x45, 'e' is 0x65). Getting this wrong produces a key that
        never matches at lookup time, and the whole module is dead on arrival
        — this is the single most common failure in generated modules.
        WORKED EXAMPLE (this exact pair has failed repeatedly): comparing
        "REST APIs" with "ReactJs" — both start "R", then 'E' vs 'e', and
        'E' < 'e', so "REST APIs" comes FIRST.
          CORRECT: "NodeJs (INTERMEDIATE), PostgreSQL (INTERMEDIATE), REST APIs (INTERMEDIATE), ReactJs (INTERMEDIATE), TypeScript (INTERMEDIATE)"
          WRONG:   "NodeJs (INTERMEDIATE), PostgreSQL (INTERMEDIATE), ReactJs (INTERMEDIATE), REST APIs (INTERMEDIATE), TypeScript (INTERMEDIATE)"
        Do not "fix" this into human alphabetical order — sort the full
        "Name (LEVEL)" strings exactly as Python's `sorted()` would.

        Use the competency names EXACTLY as given in the input, including
        casing. Several near-duplicate competencies exist as SEPARATE rows and
        differ only by case — "TypeScript" vs "Typescript", "MongoDB" vs
        "MongoDb". Copy the spelling you were given; never normalise it.

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
          actually exercises and `run.sh` using `docker compose up -d`.
          No `kill.sh` is needed — E2B sandboxes are destroyed as a whole
          when the session ends, so container cleanup is automatic.
          Decide the specific datastores by READING the scenario text in
          `detailed_skill_signal` — do not invent extras. The `datastores`
          input list (if provided) is informational only. `run.sh` is a
          READINESS/self-check, NOT the grader: it brings the datastore(s)
          up, waits for health, verifies the starter compiles/loads with the
          runtime's BUILD command (e.g. `cargo build`, `go build`,
          `npm ci && npm run build`, an import smoke), then exits 0 — on the
          UNSOLVED starter. It MUST NOT run the grader test suite (designed
          to fail until the candidate solves the task); the candidate/grader
          runs the tests separately.

          THE TWO WAYS run.sh ACTUALLY FAILS THE GATE — both observed on real
          runs, both must be designed out:

            1. A DEPENDENCY THAT IS IMPORTED BUT NOT DECLARED. Every module
               referenced anywhere — application code, and especially BUILD
               CONFIG files like `vite.config.ts`, `jest.config.ts`,
               `tsconfig` `types`, `next.config.js` — MUST appear in the
               dependency manifest that installs it. A real failure was
               `vite.config.ts` importing `@vitejs/plugin-react` while
               package.json never listed it: install succeeded, the config
               then failed to resolve, run.sh exited non-zero, and the whole
               task was thrown away. Before emitting, cross-check EVERY import
               and plugin reference against the manifests, including workspace
               packages and `@types/*`.

            2. A STRICT TYPECHECK/BUILD THAT THE UNSOLVED STARTER CANNOT PASS.
               This is the subtler one. If the starter ships stubs the
               candidate must implement, and run.sh runs `npm run typecheck` /
               `tsc --noEmit` / a full build, the stubs fail the compiler and
               run.sh exits non-zero ON THE STARTER — which is exactly what the
               gate rejects. Resolve it by making the stubs TYPE-COMPLETE BUT
               BEHAVIOURALLY INCOMPLETE: they must satisfy the compiler
               (correct signatures and return types; return an empty
               collection, a placeholder value, or throw a "not implemented"
               error) while leaving the actual behaviour for the candidate.
               That keeps the starter compiling AND keeps the task unsolved.
               If a strict check still cannot pass on the starter, run.sh must
               not run that check at all — prefer an install + import/load
               smoke plus service health over a full typecheck.

          The rule that resolves both: run.sh must exit 0 on the UNSOLVED
          starter, WITHOUT any candidate stub being filled in. Design the
          starter so that is true by construction, and say so explicitly in
          the generated prompt.

      (b) `task_shape == "non_infra"` → pure-runtime / language-level /
          algorithmic / async-concurrency / in-process / UI / frontend
          work. The generated prompt MUST NOT include `docker-compose.yml`,
          `init_database.sql`, or any datastore configuration.
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
        (per the rule above) → no Docker, no compose. `run.sh` is optional —
        the candidate runs the task locally with the runtime's native test
        command against the runtime's native manifest.
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
    HARD CONSTRAINT #9 — OPEN-ENDEDNESS scales with `proficiency`
    (agent-engineering competencies only — same scope as #8)
    ─────────────────────────────────────────────────────────────────────────
    For agent-engineering competencies, how much of the SOLUTION the task hands
    over is decided by the `proficiency` input alone — there is no separate
    flag, mirroring how the README Objectives rules in #2 already branch on
    proficiency.

    GOLDEN RULE (applies at every level): underspecify the SOLUTION, never the
    PROBLEM. The Task Overview / symptom stays crisp, fair, and reproducible.
    Only the "how" — objectives-as-steps, solution-shaped tips, the exact
    verify cases, return shapes, enum vocabularies, thresholds — is what higher
    proficiency withholds. Stripping detail off the PROBLEM makes a task
    ambiguous and unfair, which is NOT the goal.

      (a) BASIC / BEGINNER → SPECIFIED / closed. Today's baseline: the README
          still obeys #2, but the task MAY hand over the contract —
          starter-stub docstrings MAY state the expected return shape / enum
          values, Objectives MAY read as an explicit checklist, Helpful Tips
          MAY nudge toward the solution shape, How to Verify MAY name the
          exact cases, and policy constants (thresholds, retry/timeout
          budgets, state/status enums) MAY be pre-set in config. The scenario
          MAY have a single intended solution.

      (b) INTERMEDIATE / ADVANCED → OPEN / underspecified. The generated
          prompt MUST instruct the downstream task-gen LLM to WITHHOLD the
          solution on every channel, STRICTER than the #2 baseline:

            • Starter stubs: emit a BARE signature + a one-line purpose that
              names the SYMPTOM only. NO "Expected shape:" block, NO dict
              keys, NO enum vocabulary ("ok"/"stale"/"missing"), NO
              return-type contract, NO reference to a named config constant.
              The candidate DESIGNS the data shape.
            • Policy constants: do NOT pre-set the decision values (confidence
              floors, retry/timeout budgets, freshness windows, state/status
              enums). The candidate CHOOSES and DEFENDS them. The scaffold and
              fixtures MUST NOT bake in a single "expected shape".
            • Objectives: state the symptom + how to reproduce it — NOT a
              step checklist of what to build.
            • Helpful Tips: few or none; orient to the symptom / where to
              look, NEVER the shape of the fix.
            • How to Verify: describe the observable end-state only, NOT the
              exact fixtures / cases to feed.
            • Definitions / hints: OMIT the solution's concepts; a hint may
              point at the symptom, never name the building blocks of the fix.
            • Problem design space: shape a scenario that admits SEVERAL
              defensible architectures — the candidate's chosen tradeoff is
              the signal, so do not pre-decide it for them.

    Scope note: this constraint governs whether the generated prompt NARRATES
    the answer. The candidate ALWAYS receives a runnable `invariants/` suite —
    never emit a task the candidate cannot self-check.

    At ADVANCED only, the test suite is SPLIT (see the "SPLITTING THE TESTS"
    section of the ADVANCED agent reference): checks that can be derived from
    the fixtures stay in `invariants/` (shipped), while checks that would hand
    over a decision the stub deliberately left open — which operational fields
    must survive, exact status strings, boundary thresholds — move to
    `grading/` under the optional `hidden_tests` envelope key, which the
    pipeline strips from the candidate repo and uploads to the answer repo.
    A candidate-facing test that hard-codes the answer cancels every other
    withholding rule here, which is why the split exists. INTERMEDIATE and
    below ship a single visible suite — do NOT split below ADVANCED.

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
             '"infra" → MUST include docker-compose + run.sh for the scenario\'s '
             'datastores (no kill.sh — E2B sandboxes are destroyed as a whole). '
             '"non_infra" → MUST NOT include docker-compose or init_database.sql — '
             "ship a pure local project using the runtime's native manifest + test command. "
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
             `init_database.sql`, or any datastore service definition.
             Non-infra tasks MUST be pure local projects using the
             runtime's native manifest + test command.

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
              The INFRA-ONLY section `## Infrastructure Requirements` is
              REQUIRED only when `task_shape == "infra"`. For
              `task_shape == "non_infra"` this section MUST be ABSENT — a
              non-infra prompt that includes it is a violation of HARD
              CONSTRAINT #7 (no docker-compose for pure-local projects).
              Do not flag its absence on the non_infra path.
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
             "docker-compose/init_database.sql, infra MUST include docker-compose "
             "for the scenario's datastores (no kill.sh required in either case)."
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
        # The verify step runs on a cheap model (nano) via a per-call
        # dspy.context override, so it doesn't share the strong runtime LM.
        # Built lazily on first use so construction never triggers an LM build
        # (and never fails when the verifier is disabled).
        self._verify_lm = None

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
            from infra.infra_kinds import resolve as _resolve_infra_kind
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

        # Runtime / persona / frameworks stay empty for non-infra tasks — the
        # LLM honours `task_shape` directly (HARD CONSTRAINT #7). For infra
        # tasks STEP 3.5 resolves the template so the prompt LLM gets real
        # values. For a FORCED infra task we seed `datastores` with the chosen
        # service so the generated prompt boots it.
        template = None
        persona = ""
        runtime = ""
        cap_frameworks: list[str] = []
        cap_datastores: list[str] = [_infra_service] if _infra_service else []
        if _infra_service:
            logger.info("  → forced-infra service hint: datastores=%s", cap_datastores)

        if task_shape == "infra":
            logger.info("STEP 3.5 — resolving template plan for infra task")
            try:
                _plan = resolve_plan(competencies)
                if _plan.template is not None:
                    runtime = _plan.template.primary_runtime
                    persona = _plan.match.persona or ""
                    cap_frameworks = _plan.template.capabilities.get("frameworks", [])
                    # keep the forced-infra service hint if the template
                    # declares no datastores of its own
                    _tpl_datastores = _plan.template.capabilities.get("datastores", [])
                    cap_datastores = _tpl_datastores or cap_datastores
                    template = _plan.template
                    logger.info(
                        "  → template resolved: runtime=%s persona=%s "
                        "frameworks=%s datastores=%s",
                        runtime, persona, cap_frameworks, cap_datastores,
                    )
                else:
                    logger.info(
                        "  → no template resolved for infra task "
                        "(no_match or build failed) — runtime/frameworks stay empty"
                    )
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "STEP 3.5: resolve_plan raised unexpectedly: %s "
                    "— continuing with empty template info", exc
                )

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
                if self._verify_lm is None:
                    self._verify_lm = build_verify_lm()
                logger.info("  calling Review (ChainOfThought) on %s...",
                            DEFAULT_VERIFY_MODEL)
                # Run the advisory verify on the cheap model, leaving the strong
                # runtime LM configured for generate.
                with dspy.context(lm=self._verify_lm):
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
        cwd = Path.cwd()
        for path in retrieval.references:
            try:
                content = path.read_text(encoding="utf-8")
            except Exception as e:
                parts.append(f"# === {path.name} (could not read: {e}) ===")
                continue
            # References from the prompt-corpus cache live in a temp dir outside
            # the repo; relative_to() raises there, so fall back to the bare path.
            try:
                shown = path.relative_to(cwd) if path.is_absolute() else path
            except ValueError:
                shown = path
            parts.append(
                f"# ===== Reference: {path.name} =====\n"
                f"# Path: {shown}\n\n"
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
