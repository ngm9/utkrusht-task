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

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import dspy
from dotenv import load_dotenv

from prompt_generator.classifier import (
    Competency,
    TaskCategory,
    classify_task_category,
)
from prompt_generator.db_queries import (
    TaskExample,
    fetch_competency_scope,
    fetch_similar_tasks,
    init_supabase,
)
from prompt_generator.retriever import retrieve_references, RetrievalResult
from prompt_generator.validator import ValidationResult, validate_prompt_file

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

    HARD CONSTRAINT — infrastructure category:
    The `task_category` field determines the file structure. Match it exactly:
      - PURE_CODE: no Docker, just source + requirements.txt or package.json
      - DB_ONLY: Docker + PostgreSQL + init_database.sql, NO app code
      - SCRIPT_AND_DB: Docker + DB + a script in the language (no web framework)
      - APP_AND_DB: Docker + DB + web framework (FastAPI/Flask/Express/Spring)
      - FRONTEND: package.json, no Docker, browser-side only
      - LLM_FRAMEWORK: Python + LLM library (Langchain, Llamaindex)
      - VECTOR_DB: Python + vector store (Milvus/Chroma/Pinecone)
      - MESSAGING: backend + Kafka/queue infrastructure (broker container)
      - MICROSERVICES: multi-service Docker setup
      - NON_CODE: data files only (CSV/JSON), no executable code

    HARD CONSTRAINT — proficiency level boundaries:
      - BEGINNER (0-1 yrs, 20-30 min): single concept, syntax fixes, basic logic.
        Forbidden: async/await, design patterns, performance optimization, testing.
      - BASIC (1-2 yrs, 30-45 min): 2-3 concepts combined, well-scoped feature.
        Forbidden: system design, microservices, advanced concurrency, security
        hardening, advanced caching, complex partitioning.
      - INTERMEDIATE (3-5 yrs, 45-60 min): 4-5 concepts, optimization, architecture,
        proper testing, error handling, performance tuning.

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
    task_category: str = dspy.InputField(desc="Infrastructure category (e.g. script_and_db, app_and_db)")
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
      2. CATEGORY MISMATCH: code_files don't match task_category.
         Example: script_and_db with a Flask/FastAPI app — REJECT.
         Example: app_and_db without web framework files — REJECT.
      3. STRUCTURAL DAMAGE: missing PROMPT_REGISTRY, missing format vars
         ({organization_background}, {role_context}, {competencies},
         {real_world_task_scenarios}), or wrong registry key format.
      4. SOLUTION LEAK: starter code or comments give away the solution.

    PASS conditions (accept even if not perfect):
      - All four hard-fail checks above pass.
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
    task_category: str = dspy.InputField(desc="Expected infrastructure category")
    reference_prompts: str = dspy.InputField(desc="Source of similar reference prompts (for style calibration)")
    similar_tasks: str = dspy.InputField(desc="Summaries of tasks the prompt should produce")
    competency_scopes: str = dspy.InputField(
        desc="AUTHORITATIVE scope text — required skills must stay within these bounds."
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

        # 1. Classify the task category
        category = classify_task_category(competencies)

        # 2. Retrieve reference prompts via the fallback ladder
        retrieval = retrieve_references(competencies, proficiency)

        # 3. Pull similar tasks + competency scopes from Supabase
        supabase = init_supabase(env)
        comp_names = [c.name for c in competencies]
        similar = fetch_similar_tasks(supabase, comp_names, proficiency)

        scopes_text = []
        for comp in competencies:
            scope = fetch_competency_scope(supabase, comp.name, proficiency)
            if scope and scope.get("scope"):
                scopes_text.append(f"[{comp.name} ({proficiency})]\n{scope['scope']}")

        # 4. Build context strings for the LLM
        comp_str = ", ".join(f"{c.name} ({proficiency})" for c in competencies)
        refs_text = self._build_references_text(retrieval)
        tasks_text = self._build_similar_tasks_text(similar)
        scopes_str = "\n\n---\n\n".join(scopes_text) if scopes_text else "(no scopes available)"

        # 5. Generate ↔ verify loop
        feedback = ""
        last_result = None
        for attempt in range(1, self.max_iterations + 1):
            gen_out = self.generate(
                competencies=comp_str,
                proficiency=proficiency,
                task_category=category.value,
                competency_scopes=scopes_str,
                reference_prompts=refs_text,
                similar_tasks=tasks_text,
                feedback_from_previous_attempt=feedback,
            )
            new_prompt = gen_out.new_prompt_file

            # Strip any markdown code-fence wrappers the LLM may add
            new_prompt = self._strip_code_fence(new_prompt)

            verify_out = self.verify(
                new_prompt_file=new_prompt,
                competencies=comp_str,
                task_category=category.value,
                reference_prompts=refs_text,
                similar_tasks=tasks_text,
                competency_scopes=scopes_str,
            )

            last_result = (new_prompt, verify_out, attempt)
            if verify_out.passes:
                break
            feedback = verify_out.feedback

        new_prompt, verify_out, iterations = last_result

        # 6. Final deterministic validation
        comp_dicts = [{"name": c.name, "proficiency": proficiency} for c in competencies]
        validation = validate_prompt_file(new_prompt, comp_dicts, proficiency)

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
