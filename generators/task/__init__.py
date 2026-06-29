"""Task generation domain — the refactor of multiagent.py.

One module per responsibility:

* ``_clients``         — shared LLM clients (Portkey/Anthropic + Portkey/OpenAI)
* ``runtime_resolver`` — match a competency combo to a template via the
                         classifier + ``task_template_match`` cache, return
                         a ``ResolvedPlan(match, template)``
* ``evaluator``        — LLM eval critics + retry-feedback helpers
* ``gate``             — E2B build/test gate invocation for the retry loop
* ``persistence``      — Supabase + GitHub + gist writes
* ``creator``          — ``create_task`` orchestration + answer-code helpers

Tracking: ``docs/plans/2026-05-27-unified-classifier-template-schema.md``
"""
from generators.task.creator import (
    create_task,
    determine_task_type,
    generate_answer_code_and_steps,
)
from generators.task.evaluator import (
    blockers_are_deterministic_only,
    build_retry_feedback,
    is_task_hollow,
    proficiency_profile,
    run_evaluations,
)
from generators.task.gate import GateOutcome, run_gate_for_attempt
from generators.task.persistence import (
    create_answer_github_repo,
    delete_github_repo,
    init_supabase,
    insert_draft_task,
    mark_task_failed,
    mark_task_ready,
    upload_answer_files_to_repo,
    upload_files_to_github,
)
from generators.task.runtime_resolver import (
    InfraTemplateMissingError,
    ResolvedPlan,
    TemplateSpec,
    make_combo_key,
    require_infra_template,
    resolve_plan,
)

__all__ = [
    # runtime_resolver
    "InfraTemplateMissingError",
    "ResolvedPlan",
    "TemplateSpec",
    "make_combo_key",
    "require_infra_template",
    "resolve_plan",
    # evaluator
    "blockers_are_deterministic_only",
    "build_retry_feedback",
    "is_task_hollow",
    "proficiency_profile",
    "run_evaluations",
    # gate
    "GateOutcome",
    "run_gate_for_attempt",
    # persistence
    "create_answer_github_repo",
    "delete_github_repo",
    "init_supabase",
    "insert_draft_task",
    "mark_task_failed",
    "mark_task_ready",
    "upload_answer_files_to_repo",
    "upload_files_to_github",
    # creator
    "create_task",
    "determine_task_type",
    "generate_answer_code_and_steps",
]
