"""
Supabase queries — pulls reference tasks for the verifier and training data
for DSPy compilation.

The verifier uses these to compare a candidate prompt against tasks that were
actually generated and passed quality gates (eval_info.passed, is_enabled).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()


# Fields we pull from the tasks table for verifier context.
# Keep this lean — verifier needs the shape, not the full code_files blob.
TASK_SELECT_FIELDS = (
    "task_id, criterias, task_blob, eval_info, is_enabled, task_type"
)


@dataclass
class TaskExample:
    """A simplified view of a task — enough for the verifier to learn the pattern."""
    task_id: str
    competencies: list[dict]   # list of {name, proficiency, competency_id}
    title: Optional[str]
    question: Optional[str]
    code_file_names: list[str] = field(default_factory=list)
    eval_passed: Optional[bool] = None
    is_enabled: bool = False
    task_type: list[str] = field(default_factory=list)

    @classmethod
    def from_row(cls, row: dict) -> "TaskExample":
        blob = row.get("task_blob") or {}
        code_files = blob.get("code_files") or {}
        eval_info = row.get("eval_info") or {}
        return cls(
            task_id=row["task_id"],
            competencies=row.get("criterias") or [],
            title=blob.get("title") or blob.get("name"),
            question=blob.get("question"),
            code_file_names=list(code_files.keys()) if isinstance(code_files, dict) else [],
            eval_passed=eval_info.get("passed") if isinstance(eval_info, dict) else None,
            is_enabled=bool(row.get("is_enabled")),
            task_type=row.get("task_type") or [],
        )

    def summary(self, max_q_chars: int = 280) -> str:
        """Compact text representation for putting in LLM context."""
        comp_names = ", ".join(
            f"{c.get('name')} ({c.get('proficiency', '')})" for c in self.competencies
        )
        q = (self.question or "")[:max_q_chars]
        if self.question and len(self.question) > max_q_chars:
            q += "..."
        return (
            f"Title: {self.title}\n"
            f"Competencies: {comp_names}\n"
            f"Eval passed: {self.eval_passed} | Enabled: {self.is_enabled}\n"
            f"Files: {', '.join(self.code_file_names)}\n"
            f"Question: {q}"
        )


# ----------------------------------------------------------------------
# Supabase client init
# ----------------------------------------------------------------------

def init_supabase(env: str = "dev") -> Client:
    """Initialize Supabase client for the given environment.

    Mirrors the pattern in generate_input_files/generator.py.
    """
    if env == "dev":
        url = os.getenv("SUPABASE_URL_APTITUDETESTSDEV")
        key = os.getenv("SUPABASE_API_KEY_APTITUDETESTSDEV")
    else:
        url = os.getenv("SUPABASE_URL_APTITUDETESTS")
        key = os.getenv("SUPABASE_API_KEY_APTITUDETESTS")

    if not url or not key:
        raise RuntimeError(
            f"Missing Supabase credentials for env '{env}'. "
            f"Check SUPABASE_URL_APTITUDETESTS{'DEV' if env == 'dev' else ''} in .env."
        )
    return create_client(url, key)


# ----------------------------------------------------------------------
# Query helpers
# ----------------------------------------------------------------------

def _criterias_contains(comp_name: str, proficiency: Optional[str] = None) -> str:
    """Build a JSONB containment filter value for the criterias array."""
    import json
    if proficiency:
        return json.dumps([{"name": comp_name, "proficiency": proficiency}])
    return json.dumps([{"name": comp_name}])


def fetch_tasks_for_competency(
    supabase: Client,
    competency_name: str,
    proficiency: Optional[str] = None,
    only_quality: bool = True,
    limit: int = 10,
) -> list[TaskExample]:
    """Fetch tasks whose criterias contain the given competency.

    only_quality=True filters to is_enabled=True (production-ready tasks).
    """
    query = supabase.table("tasks").select(TASK_SELECT_FIELDS)
    query = query.contains("criterias", _criterias_contains(competency_name, proficiency))
    if only_quality:
        query = query.eq("is_enabled", True)
    query = query.order("created_at", desc=True).limit(limit)
    result = query.execute()
    return [TaskExample.from_row(r) for r in (result.data or [])]


def fetch_tasks_for_combination(
    supabase: Client,
    competency_names: list[str],
    proficiency: str,
    only_quality: bool = True,
    limit: int = 5,
) -> list[TaskExample]:
    """Fetch tasks whose criterias contain ALL given competencies at this level."""
    # Supabase contains() with multiple items in a single call uses jsonb @> array
    # which requires every element to be present.
    import json
    needle = json.dumps([
        {"name": name, "proficiency": proficiency} for name in competency_names
    ])
    query = supabase.table("tasks").select(TASK_SELECT_FIELDS)
    query = query.contains("criterias", needle)
    if only_quality:
        query = query.eq("is_enabled", True)
    query = query.order("created_at", desc=True).limit(limit)
    result = query.execute()
    return [TaskExample.from_row(r) for r in (result.data or [])]


def fetch_similar_tasks(
    supabase: Client,
    competency_names: list[str],
    proficiency: str,
    limit_per_query: int = 3,
) -> list[TaskExample]:
    """Pull a useful mix of tasks for the verifier:
       1. Tasks for the exact combination (best signal)
       2. Tasks for each competency individually (if combo is empty)
    """
    seen: set[str] = set()
    out: list[TaskExample] = []

    # 1. Combination tasks
    combo = fetch_tasks_for_combination(
        supabase, competency_names, proficiency, only_quality=True, limit=limit_per_query
    )
    for t in combo:
        if t.task_id not in seen:
            out.append(t)
            seen.add(t.task_id)

    # 2. Per-competency tasks (cap to limit_per_query each)
    for name in competency_names:
        per = fetch_tasks_for_competency(
            supabase, name, proficiency, only_quality=True, limit=limit_per_query
        )
        for t in per:
            if t.task_id not in seen:
                out.append(t)
                seen.add(t.task_id)

    return out


def fetch_competency_scope(
    supabase: Client,
    competency_name: str,
    proficiency: str,
) -> Optional[dict]:
    """Pull the competency record (name, scope, long_scope) for use in
    bootstrap mode where DB tasks don't exist yet.
    """
    result = (
        supabase.table("competencies")
        .select("competency_id, name, proficiency, scope, long_scope")
        .ilike("name", competency_name)
        .eq("proficiency", proficiency)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None
