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
from typing import Optional

import dspy
from dotenv import load_dotenv

logger = logging.getLogger("prompt_generator")

from infra.classifier.runtime import Competency
from generators.task.runtime_resolver import TemplateSpec, resolve_plan
from generators.prompts.db_queries import (
    TaskExample,
    fetch_competency_scope,
    fetch_similar_tasks,
    init_supabase,
)
from generators.prompts.input_files import build_detailed_skill_signal
from generators.prompts.retriever import retrieve_references, RetrievalResult
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
DEFAULT_RUNTIME_MODEL = os.getenv("PROMPT_GENERATOR_MODEL", "openai/gpt-5.4")
DEFAULT_COMPILE_MODEL = os.getenv("PROMPT_GENERATOR_COMPILE_MODEL", "anthropic/claude-haiku-4-5")


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
            temperature=0.2,
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
            temperature=0.2,
        )

    dspy.settings.configure(lm=lm)


# ----------------------------------------------------------------------
# DSPy signatures
# ----------------------------------------------------------------------

class GeneratePromptSignature(dspy.Signature):
    """Generate a complete Python file containing PROMPT_REGISTRY entry for a
    new (competencies, proficiency) combination.

    HARD CONSTRAINT — competency_scopes is the source of truth:
    The `competency_scopes` field describes EXACTLY what each competency covers
    at this proficiency level. The generated prompt MUST:
      - Only ask the candidate to use concepts that appear (or could be naturally
        derived from) the scope text.
      - Never require concepts the scope says are out of scope.
      - When the scope says "limited understanding of X" or "not yet expected to
        do Y", the generated task must NOT require X or Y as primary skills.
    Read every scope line carefully before designing the task.

    HARD CONSTRAINT — output structure:
    The output MUST be a valid Python module that:
      - Defines three triple-quoted strings: a CONTEXT prompt, an INPUT_AND_ASK
        prompt, and an INSTRUCTIONS prompt. Use names like
        PROMPT_<TECH>_<LEVEL>_CONTEXT, _INPUT_AND_ASK, _INSTRUCTIONS.
      - Contains placeholders {organization_background}, {role_context},
        {competencies}, {real_world_task_scenarios}, {minutes_range}.
      - Defines PROMPT_REGISTRY = { "<key>": [CONTEXT, INPUT_AND_ASK, INSTRUCTIONS] }
        where <key> is exactly: 'Name1 (LEVEL), Name2 (LEVEL)' (alphabetically
        sorted competency names with proficiency in parentheses).

    HARD CONSTRAINT — brace escaping:
    Every `{` and `}` inside the prompt strings is passed through
    Python `str.format(**fmt_args)` downstream. Only the following are valid
    single-brace placeholders: `{organization_background}`, `{role_context}`,
    `{competencies}`, `{real_world_task_scenarios}`, `{minutes_range}`,
    `{question_prompt}`. Any OTHER `{` or `}` (JSON example, dict literal,
    f-string snippet, set notation) MUST be doubled (`{{` and `}}`). For
    example, when embedding an output schema example, write
    `{{"title": "...", "code_files": {{"a.py": "..."}}}}`, NOT
    `{"title": "...", "code_files": {"a.py": "..."}}`. A single unescaped
    JSON example causes downstream `KeyError: '\\n  "title"'` and no task is
    ever generated.

    HARD CONSTRAINT — derive structure from the matched template's capabilities, NOT a single label:
      • `primary_runtime` and the capability `frameworks` (and their common
        libraries) are PRE-INSTALLED by the E2B template. Do NOT include
        `apt-get install`, `pip install`, or `npm install` for the runtime or
        its common libs in run.sh.
      • `datastores` non-empty → emit a `docker-compose.yml` that brings up those
        service containers (postgres, redis, mongo, mysql, …). `run.sh` does
        `docker compose up -d`; `kill.sh` does `docker compose down`.
      • `persona="mobile"` → no Dockerfile, no compose; run the runtime's native
        test command (e.g. `flutter test`, `npx react-native test`).
      • `persona="dba"` → just an `init_database.sql` + Compose; no app code.
      • `persona="pm"` → data files only (CSV / JSON); no `run.sh`.
      • `persona="frontend"` → `package.json`, no Docker, browser-side only.
      • `persona="sdet"` → test suite shape; the template ships the runner
        (pytest, jest, playwright, …); the task ships the spec files.

    HARD CONSTRAINT — generated-task output JSON schema (CANONICAL KEYS):
    The INSTRUCTIONS prompt you produce tells a downstream LLM to emit a JSON
    object describing the assessment task. multiagent.py reads SPECIFIC top-level
    keys off that JSON. You MUST instruct the downstream LLM to use exactly these
    canonical key names — NOT synonyms:
      - "name"          (string) — the task title. NOT "task_title", NOT "title".
      - "question"      (string) — the full candidate-facing task description.
                          NOT "context", NOT "candidate_instructions".
      - "code_files"    (object) — maps each filepath to its full contents.
                          NOT "files", NOT "repository_structure".
      - "answer"        (object) — the evaluator-facing canonical solution summary.
      - "definitions", "hints", "outcomes", "pre_requisites", "short_overview"
                          — supporting fields stored in the candidate task_blob.
    A prompt that instructs ANY other key name (task_title / files / context /
    repository_structure / acceptance_criteria) causes multiagent.py to read
    every field as empty and produce a HOLLOW task that is rejected by the eval
    gate. When `reference_prompts` is empty (bootstrap mode), you MUST still use
    these exact canonical keys — do not invent your own schema.

    HARD CONSTRAINT — proficiency level boundaries:
      - BEGINNER (0-1 yrs, 20-30 min): single concept, syntax fixes, basic logic.
        Forbidden: async/await, design patterns, performance optimization, testing.
      - BASIC (1-2 yrs, 30-45 min): 2-3 concepts combined, well-scoped feature.
        Forbidden: system design, microservices, advanced concurrency, security
        hardening, advanced caching, complex partitioning.
      - INTERMEDIATE (3-5 yrs, 45-60 min): 4-5 concepts, optimization, architecture,
        proper testing, error handling, performance tuning.

    HARD CONSTRAINT — scenario locking (the task domain MUST come from the
    scenarios, NOT the org context):
    Downstream task-generation LLMs see TWO competing signals — the
    organization context (e.g. "Utkrusht builds proof-of-skills assessments")
    AND the real-world scenarios (e.g. e-commerce dashboards, healthcare
    APIs, logistics tools). Without an explicit lock, the LLM blends them
    and invents tasks in the org's domain that aren't in the scenarios list
    — e.g. generating an "AssessmentAttemptViewSet" task when every
    scenario was about e-commerce / healthcare / real-estate.

    The INSTRUCTIONS prompt you generate MUST contain a section like this,
    verbatim or paraphrased with the same force:

      ## SCENARIO LOCK (mandatory)
      - You MUST pick EXACTLY ONE scenario from `real_world_task_scenarios`.
      - The generated task's BUSINESS DOMAIN must match the chosen
        scenario's domain (e-commerce, healthcare, logistics, real-estate,
        etc.). DO NOT invent a new domain.
      - The generated task's CURRENT IMPLEMENTATION problem and YOUR TASK
        bullet list must be the chosen scenario's, adapted to the
        target competency. You may rename variables and adjust minor
        details, but the SHAPE and the DOMAIN must come from the scenario.
      - The candidate's EMPLOYER is described in `organization_background`.
        The EMPLOYER is who is administering the assessment — it is NOT
        the domain of the task. The task domain comes from the scenarios.
      - If you find yourself writing about a domain that does NOT appear
        in `real_world_task_scenarios` (e.g. "assessments", "leaderboards",
        "proof-of-skills platforms" when no scenario mentions those), STOP
        — that's domain hallucination. Restart with one of the listed
        scenarios.
      - When `real_world_task_scenarios` is empty or "(none provided)",
        explicitly state which generic domain you picked (e.g. "I picked
        e-commerce because the competency is web-framework-backend") and
        why; do not silently default to the org's domain.

    Place this section near the top of the INSTRUCTIONS prompt, before
    the technical / file-layout requirements, so it anchors the LLM
    before it starts drafting.

    Also: when drafting the INPUT_AND_ASK prompt, replace soft language
    like "draw inspiration from" with "PICK EXACTLY ONE". Soft language
    is the failure mode that lets the LLM drift.

    REFERENCE PROMPTS (knowledge base):
    Use `reference_prompts` for the structural template — section ordering, tone,
    output JSON shape, README sections. Do NOT copy reference content verbatim;
    adapt it to the target competencies and category.

    SIMILAR TASKS (calibration):
    `similar_tasks` shows what successful tasks for related competencies actually
    look like. Use them to calibrate complexity, file count, and question style.
    """

    competencies: str = dspy.InputField(
        desc="Comma-separated competency names with proficiency (e.g. 'Python (BASIC), SQL (BASIC)')"
    )
    proficiency: str = dspy.InputField(desc="Target proficiency level (BASIC/BEGINNER/INTERMEDIATE)")
    runtime: str = dspy.InputField(
        desc="Primary language runtime of the matched template (e.g. python, node)"
    )
    frameworks: str = dspy.InputField(
        desc="JSON list of framework names the template advertises in capabilities.frameworks, e.g. '[\"fastapi\"]' or '[]'"
    )
    datastores: str = dspy.InputField(
        desc="JSON list of datastore names the template supports, brought up via docker-compose if used, e.g. '[\"postgres\"]' or '[]'"
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

    PASS BAR — be PRACTICAL. The goal is to ship a usable prompt, not perfection.
    Pass if the prompt is structurally correct, scope-respecting, and would
    plausibly produce a deployable task. Do NOT block on minor stylistic issues.

    HARD-FAIL conditions (must reject):
      1. SCOPE VIOLATION: Required candidate skills exceed competency_scopes.
         Example: BASIC scope says "limited async understanding" but the prompt
         requires async/await throughout — REJECT.
      2. STRUCTURE MISMATCH: code_files don't match the template's
         capabilities + persona.
         Example: persona="data" / script-style task with a Flask/FastAPI app
         file present — REJECT.
         Example: datastores=["postgres"] but no docker-compose.yml — REJECT.
         Example: persona="mobile" with a Dockerfile present — REJECT.
      3. STRUCTURAL DAMAGE: missing PROMPT_REGISTRY, missing format vars
         ({organization_background}, {role_context}, {competencies},
         {real_world_task_scenarios}), or wrong registry key format.
      4. SOLUTION LEAK: starter code or comments give away the solution.
      5. MISSING SCENARIO LOCK: the INSTRUCTIONS prompt does NOT contain a
         section forcing the downstream LLM to pick exactly ONE scenario
         from real_world_task_scenarios and stay in that scenario's
         business domain. Concretely, reject when ANY of these are true:
           - The prompt uses soft language ("draw inspiration from",
             "loosely based on", "feel free to combine") instead of a
             hard pick ("PICK EXACTLY ONE", "MUST come from", "do NOT
             invent a new domain").
           - The prompt does not warn the downstream LLM against using
             the employer's domain as the task domain.
           - The prompt has no anti-hallucination clause for the case
             where the LLM finds itself in a domain not in the scenarios.
         Without this lock, generated tasks drift into the org context's
         domain (e.g. "assessments", "leaderboards") and ignore the
         provided scenarios. The lock must be near the TOP of the
         INSTRUCTIONS prompt so it anchors the downstream LLM before
         it starts drafting.

    PASS conditions (accept even if not perfect):
      - All five hard-fail checks above pass.
      - INSTRUCTIONS prompt has GOAL, infrastructure spec, REQUIRED OUTPUT
        JSON STRUCTURE, and README structure sections (in some recognizable form).
      - Time constraint matches proficiency (BEGINNER: 20-30 min, BASIC: 30-45 min,
        INTERMEDIATE: 45-60 min).

    Output `passes=true` if all hard-fail checks pass.
    Output specific, actionable `feedback` listing each issue if rejecting. Be
    concise — the generator will use this to fix the prompt.
    """

    new_prompt_file: str = dspy.InputField(desc="The candidate prompt file source")
    competencies: str = dspy.InputField(desc="Target competencies + proficiency")
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
        desc="True iff all 4 HARD-FAIL conditions are clear (scope, category, structure, no leaks)"
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


class PromptGeneratorAgent(dspy.Module):
    """The agent that synthesizes new prompt files."""

    def __init__(self, max_iterations: int = 5):
        super().__init__()
        self.generate = dspy.ChainOfThought(GeneratePromptSignature)
        self.verify = dspy.ChainOfThought(VerifyPromptSignature)
        self.max_iterations = max_iterations

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
    ) -> GenerationResult:
        proficiency = proficiency.upper()
        comp_str = ", ".join(f"{c.name} ({proficiency})" for c in competencies)

        logger.info("=" * 72)
        logger.info("AGENT START — competencies=%s  proficiency=%s  env=%s",
                    [c.name for c in competencies], proficiency, env)
        logger.info("=" * 72)

        # ─── STEP 1: resolver (task_template_match cache + classifier) ─
        # Routes through resolve_plan so we hit the task_template_match cache
        # instead of re-classifying on every prompt-generator run.
        logger.info("STEP 1 / runtime_resolver.py — matching template via combo cache")
        plan = resolve_plan(competencies)
        if plan.match is None or plan.template is None:
            raise RuntimeError(
                f"resolve_plan returned no usable match for combo={plan.combo_key!r} — "
                f"match={plan.match!r} template={plan.template!r}; "
                "cannot generate a prompt without a matched built template"
            )
        template = plan.template
        persona = plan.match.persona or (template.personas[0] if template.personas else "")
        caps = template.capabilities or {}
        cap_frameworks = list(caps.get("frameworks") or [])
        cap_datastores = list(caps.get("datastores") or [])
        logger.info("  → template_id=%s primary_runtime=%s persona=%s "
                    "frameworks=%s datastores=%s",
                    template.template_id, template.primary_runtime, persona,
                    cap_frameworks, cap_datastores)

        # ─── STEP 2: retriever (5-level fallback) ─────────────────────
        logger.info("STEP 2 / retriever.py — running 5-level fallback ladder")
        retrieval = retrieve_references(competencies, proficiency, template=template)
        logger.info("  → bootstrap_mode = %s", retrieval.bootstrap_mode)
        logger.info("  → fallback_level = %d", retrieval.fallback_level)
        logger.info("  → references found: %d", len(retrieval.references))
        for path in retrieval.references:
            logger.info("      • %s", path.name)
        for note in retrieval.notes:
            logger.debug("      ladder: %s", note)

        # ─── STEP 3: Supabase queries ─────────────────────────────────
        logger.info("STEP 3 / db_queries.py — Supabase env=%s", env)
        supabase = init_supabase(env)
        comp_names = [c.name for c in competencies]

        logger.info("  fetching similar tasks for %s ...", comp_names)
        similar = fetch_similar_tasks(supabase, comp_names, proficiency)
        logger.info("  → similar tasks fetched: %d", len(similar))
        for t in similar[:5]:
            logger.debug("      • task_id=%s title=%r",
                         getattr(t, "task_id", "?"),
                         (getattr(t, "title", "") or "")[:60])

        scopes_text = []
        for comp in competencies:
            logger.info("  fetching competency.scope for %s (%s) ...", comp.name, proficiency)
            scope = fetch_competency_scope(supabase, comp.name, proficiency)
            if scope and scope.get("scope"):
                scopes_text.append(f"[{comp.name} ({proficiency})]\n{scope['scope']}")
                logger.info("    → scope text: %d chars", len(scope["scope"]))
            else:
                logger.warning("    → NO SCOPE found in Supabase for %s (%s)",
                               comp.name, proficiency)

        # ─── STEP 4: detailed_skill_signal from input files ───────────
        logger.info("STEP 4 / input_files.py — building detailed_skill_signal")
        skill_signal, skill_meta = build_detailed_skill_signal(competencies, proficiency)
        logger.info("  → background_found  = %s", skill_meta.get("background_found"))
        logger.info("  → questions_prompt  = %d chars", skill_meta.get("questions_chars", 0))
        logger.info("  → role_context      = %d chars", skill_meta.get("role_context_chars", 0))
        logger.info("  → scenarios         = %d items", skill_meta.get("scenarios_count", 0))
        logger.info("  → total signal      = %d chars", skill_meta.get("signal_chars", 0))

        # ─── STEP 5: assemble context strings ─────────────────────────
        refs_text = self._build_references_text(retrieval)
        tasks_text = self._build_similar_tasks_text(similar)
        scopes_str = "\n\n---\n\n".join(scopes_text) if scopes_text else "(no scopes available)"

        logger.info("STEP 5 — context payload sizes for the LLM call")
        logger.info("  competencies              %6d chars  %r", len(comp_str), comp_str)
        logger.info("  proficiency               %6d chars  %r", len(proficiency), proficiency)
        frameworks_json = json.dumps(cap_frameworks)
        datastores_json = json.dumps(cap_datastores)
        logger.info("  runtime                   %6d chars  %r",
                    len(template.primary_runtime), template.primary_runtime)
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

        # ─── STEP 6: Generate ⇄ Verify ⇄ Validate loop ───────────────
        logger.info("STEP 6 — Generate ⇄ Verify ⇄ Validate loop "
                    "(max_iterations=%d)", self.max_iterations)
        comp_dicts = [{"name": c.name, "proficiency": proficiency} for c in competencies]
        feedback = ""
        last_result = None
        for attempt in range(1, self.max_iterations + 1):
            logger.info("  ── attempt %d / %d ──", attempt, self.max_iterations)

            logger.info("  calling Generate (ChainOfThought)...")
            gen_out = self.generate(
                competencies=comp_str,
                proficiency=proficiency,
                runtime=template.primary_runtime,
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

            logger.info("  calling Verify (ChainOfThought)...")
            verify_out = self.verify(
                new_prompt_file=new_prompt,
                competencies=comp_str,
                runtime=template.primary_runtime,
                frameworks=frameworks_json,
                datastores=datastores_json,
                persona=persona,
                reference_prompts=refs_text,
                similar_tasks=tasks_text,
                competency_scopes=scopes_str,
                detailed_skill_signal=skill_signal,
            )
            logger.info("    Verify done — passes=%s feedback=%d chars",
                        verify_out.passes, len(verify_out.feedback or ""))
            if verify_out.feedback:
                logger.info("    verifier feedback: %s",
                            (verify_out.feedback or "")[:400].replace("\n", " "))

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
                logger.info("  ✓ both verifier and validator passed at attempt %d "
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
