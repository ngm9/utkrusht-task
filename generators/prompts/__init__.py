"""
Prompt Generator package — agent that synthesizes new task generation prompt files.

------------------------------------------------------------------------------
Where this fits in utkrusht-task
------------------------------------------------------------------------------
utkrusht-task is the automated pipeline that generates, evaluates, deploys,
and manages technical coding assessment tasks. The top-level flow lives in
multiagent.py and runs:

    competency JSON + background JSON + scenario JSON
        → pick task_generation_prompts/{level}/{tech}_prompt.py
        → OpenAI (via Portkey gateway) generates task + code files
        → evals.py LLM-judges the task with a retry loop
        → github_utils.py creates template + answer repos and a gist
        → Supabase (dev/prod) stores the task metadata
        → optionally e2b_flow deploys to an E2B sandbox

Each technology stack has a hand-tuned prompt file under
task_generation_prompts/{Beginner,Basic,Intermediate}/ — e.g.
python_sql_basic_prompt.py, python_llamaindex_basic_prompt.py. These files
export a PROMPT_REGISTRY dict that multiagent.py consumes.

This package writes those prompt files. It is the meta-agent that authors
the per-(competencies, proficiency) prompt template instead of a human.

------------------------------------------------------------------------------
How the agent works
------------------------------------------------------------------------------
A DSPy Generator ⇄ Verifier loop produces a new .py file that registers a
PROMPT_REGISTRY entry for the given (competencies, proficiency) combination.
The Generator receives five context sources:

  1. competency_scopes        — authoritative skill bounds (Supabase)
  2. reference_prompts        — 3-5 existing prompt files (5-level fallback
                                ladder in retriever.py: exact match →
                                adjacent proficiency → per-competency →
                                tech-family siblings → category examples)
  3. similar_tasks            — past enabled + eval-passed tasks (Supabase)
  4. detailed_skill_signal    — bundled role_context + questions_prompt + 3
                                example scenarios from task_input_files/
                                (graceful empty for brand-new combos)
  5. feedback_from_previous_attempt — verifier + validator output, only in loop

The Verifier hard-fails on four conditions: scope violation, category
mismatch, structural damage, or solution leak. validator.py adds
deterministic checks. The loop merges both feedback streams and re-generates
until pass or max_iterations.

Infrastructure shape comes from the matched ``templates`` row + the
classifier's persona pick. ``generators.task.runtime_resolver.resolve_plan``
returns a ``ResolvedPlan(match, template)`` carrying both. Downstream code
reads the template's capabilities (frameworks, datastores, protocols) and
the match's persona to decide Docker/file layout and reviewer routing.

------------------------------------------------------------------------------
Usage
------------------------------------------------------------------------------
Usage as CLI:
    python -m prompt_generator --name "Python, SQL" --proficiency BASIC

Usage as module:
    from infra.classifier.classifier import Competency, to_competencies
    from generators.task.runtime_resolver import resolve_plan
    from generators.prompts.retriever import retrieve_references
    from generators.prompts.input_files import build_detailed_skill_signal

See docs/plans/2026-05-27-unified-classifier-template-schema.md for the
unified classifier+template architecture.
"""
from infra.classifier.classifier import to_competencies
from infra.classifier.runtime import Competency

__all__ = [
    "Competency",
    "to_competencies",
]
