"""Task generation domain — the refactor of multiagent.py.

One module per responsibility:

* ``_clients``         — shared LLM clients (Portkey/Anthropic + Portkey/OpenAI)
* ``runtime_resolver`` — classify a competency combo into a ``ResolvedPlan``
* ``evaluator``        — LLM eval critics + retry-feedback helpers
* ``gate``             — E2B build/test gate invocation for the retry loop
* ``persistence``      — Supabase + GitHub + gist writes
* ``creator``          — ``create_task`` orchestration + answer-code helpers

Tracking: ``docs/superpowers/plans/2026-05-22-task-generator-production-readiness.md``
"""
from generators.task.creator import (
    create_task,
    determine_task_type,
    generate_answer_code_and_steps,
)
from generators.task.evaluator import (
    build_retry_feedback,
    is_task_hollow,
    run_evaluations,
)
from generators.task.gate import GateOutcome, run_gate_for_attempt
from generators.task.persistence import (
    create_answer_github_repo,
    init_supabase,
    upload_answer_files_to_repo,
    upload_files_to_github,
)
from generators.task.runtime_resolver import (
    ResolvedPlan,
    TemplateSpec,
    make_combo_key,
    resolve_plan,
)

__all__ = [
    # runtime_resolver
    "ResolvedPlan",
    "TemplateSpec",
    "make_combo_key",
    "resolve_plan",
    # evaluator
    "build_retry_feedback",
    "is_task_hollow",
    "run_evaluations",
    # gate
    "GateOutcome",
    "run_gate_for_attempt",
    # persistence
    "create_answer_github_repo",
    "init_supabase",
    "upload_answer_files_to_repo",
    "upload_files_to_github",
    # creator
    "create_task",
    "determine_task_type",
    "generate_answer_code_and_steps",
]
