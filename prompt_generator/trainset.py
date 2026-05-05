"""
Build a DSPy training set from existing prompt files + Supabase tasks.

Each training example is:
    Input:  competencies + proficiency
    Output: the existing prompt file source (the "good answer")

Quality filter — only include prompts that have produced eval-passing tasks
in Supabase, OR prompts that have at least an `is_enabled=True` task. Prompts
that have never produced any deployed/passing tasks are filtered out.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import dspy
from supabase import Client

from prompt_generator.classifier import Competency
from prompt_generator.db_queries import init_supabase
from prompt_generator.retriever import LEVEL_FOLDERS, PROMPT_ROOT


@dataclass
class TrainingPair:
    """One (competencies, proficiency) → prompt_file_source pair."""
    competency_names: list[str]
    proficiency: str
    prompt_path: Path
    prompt_source: str
    has_quality_signal: bool   # True if at least one enabled+eval-passed task exists
    db_task_count: int


# Some prompt filenames don't follow the python_sql_basic pattern cleanly.
# This regex handles the common cases.
_FILENAME_RE = re.compile(
    r"^(?P<slug>[a-z0-9_]+)_(?P<level>basic|beginner|intermediate|advanced)(?:_prompt)?\.py$",
    re.IGNORECASE,
)

# Map common slug fragments → canonical competency names. Keys are slug tokens
# as they appear in filenames (lowercase, underscore-separated).
_SLUG_TO_COMPETENCY = {
    "python":          "Python",
    "java":            "Java",
    "go":              "Go",
    "golang":          "Go",
    "node":            "NodeJs",
    "nodejs":          "NodeJs",
    "react":           "React",
    "reactjs":         "React",
    "react_native":    "React Native",
    "next":            "Next.js",
    "nextjs":          "Next.js",
    "typescript":      "Typescript",
    "javascript":      "Javascript",
    "html_css":        "HTML and CSS",
    "expressjs":       "ExpressJS",
    "express":         "ExpressJS",
    "fastapi":         "Python - FastAPI",
    "spring_boot":     "Java - Spring Boot",
    "spring_mvc":      "Java - Spring MVC",
    "spring_webservices": "Java - Spring Webservices",
    "kafka":           "Kafka",
    "redis":           "Redis",
    "mongodb":         "MongoDB",
    "postgres":        "PostgreSQL",
    "postgresql":      "PostgreSQL",
    "sql":             "SQL",
    "docker":          "Docker",
    "firebase":        "Firebase",
    "langchain":       "Langchain",
    "rag":             "RAG",
    "llamaindex":      "Llamaindex",
    "vector_databases": "Vector Databases",
    "microservices":   "Microservices",
    "shell":           "Shell scripting",
    "rest_apis":       "REST APIs",
    "apache_camel":    "Apache Camel",
    "pandas":          "Python - Pandas",
    "numpy":           "Python - Numpy",
    "voice_agent_eval": "Voice Agent Evaluation",
    "ai_evals_for_product_managers": "AI Evals for Product Managers",
    "prompt":          "Prompt Engineering",
}


def _parse_filename(path: Path) -> Optional[tuple[list[str], str]]:
    """Parse a prompt filename into (competency names, proficiency).

    Returns None if we can't confidently parse the filename.

    Examples:
      python_basic_prompt.py        → (['Python'], 'BASIC')
      python_sql_basic_prompt.py    → (['Python', 'SQL'], 'BASIC')
      Python_Fastapi_prompt.py      → (['Python - FastAPI'], 'BASIC')  (default to BASIC)
      nodejs_mongodb_intermediate_prompt.py → (['NodeJs', 'MongoDB'], 'INTERMEDIATE')
    """
    fname = path.name.lower()
    # Strip .py
    if fname.endswith(".py"):
        fname = fname[:-3]
    # Strip trailing _prompt
    if fname.endswith("_prompt"):
        fname = fname[:-7]

    # Detect proficiency from the filename
    parts = fname.split("_")
    proficiency = None
    for level in ("beginner", "basic", "intermediate", "advanced"):
        if level in parts:
            proficiency = level.upper()
            parts = [p for p in parts if p != level]
            break
    if not proficiency:
        # Fall back to BASIC for files in the Basic/ folder, etc.
        proficiency = path.parent.name.upper()
        if proficiency not in LEVEL_FOLDERS:
            return None

    # Greedy match longest slug first — handles "spring_mvc" before "spring"
    slug = "_".join(parts)
    matched: list[str] = []
    remaining = slug

    # Try compound matches first
    sorted_keys = sorted(_SLUG_TO_COMPETENCY.keys(), key=len, reverse=True)
    while remaining:
        hit = False
        for key in sorted_keys:
            # Match at start, ensuring we land on an underscore boundary
            if remaining == key or remaining.startswith(key + "_"):
                matched.append(_SLUG_TO_COMPETENCY[key])
                remaining = remaining[len(key):].lstrip("_")
                hit = True
                break
        if not hit:
            return None  # Unparseable — bail

    if not matched:
        return None
    return matched, proficiency


def _has_quality_signal(supabase: Client, competency_names: list[str], proficiency: str) -> tuple[bool, int]:
    """Check Supabase for tasks matching this prompt that are enabled.

    Returns (has_quality_signal, task_count).
    """
    import json
    needle = json.dumps([
        {"name": name, "proficiency": proficiency} for name in competency_names
    ])
    try:
        result = (
            supabase.table("tasks")
            .select("task_id, eval_info, is_enabled")
            .contains("criterias", needle)
            .execute()
        )
    except Exception:
        return False, 0

    rows = result.data or []
    if not rows:
        return False, 0

    quality = sum(
        1 for r in rows
        if r.get("is_enabled") and (r.get("eval_info") or {}).get("passed", True)
    )
    return quality > 0, len(rows)


def collect_training_pairs(
    env: str = "dev",
    require_quality_signal: bool = False,
    levels: Optional[list[str]] = None,
) -> list[TrainingPair]:
    """Walk the prompt directory and build a training set.

    Args:
        env: Supabase env to use for quality filtering.
        require_quality_signal: If True, drop pairs with no enabled DB tasks.
        levels: Restrict to these proficiency levels (defaults to all).
    """
    if levels is None:
        levels = ["BASIC", "BEGINNER", "INTERMEDIATE"]
    supabase = init_supabase(env)

    pairs: list[TrainingPair] = []
    for level in levels:
        folder = PROMPT_ROOT / LEVEL_FOLDERS[level]
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.py")):
            if path.name.startswith("__"):
                continue
            parsed = _parse_filename(path)
            if not parsed:
                continue
            comp_names, parsed_level = parsed
            # Trust the folder-derived level over filename if they differ
            level_to_use = level

            try:
                source = path.read_text(encoding="utf-8")
            except Exception:
                continue
            if "PROMPT_REGISTRY" not in source:
                continue

            has_quality, task_count = _has_quality_signal(
                supabase, comp_names, level_to_use,
            )
            if require_quality_signal and not has_quality:
                continue

            pairs.append(TrainingPair(
                competency_names=comp_names,
                proficiency=level_to_use,
                prompt_path=path,
                prompt_source=source,
                has_quality_signal=has_quality,
                db_task_count=task_count,
            ))

    return pairs


def to_dspy_examples(pairs: list[TrainingPair]) -> list[dspy.Example]:
    """Convert TrainingPair objects to dspy.Example objects.

    The Examples have inputs (competencies, proficiency) and the gold output
    is the existing prompt file source — the agent should produce something
    structurally similar.
    """
    examples = []
    for p in pairs:
        comp_str = ", ".join(f"{n} ({p.proficiency})" for n in p.competency_names)
        ex = dspy.Example(
            competencies=comp_str,
            proficiency=p.proficiency,
            new_prompt_file=p.prompt_source,
        ).with_inputs("competencies", "proficiency")
        examples.append(ex)
    return examples


if __name__ == "__main__":
    # Quick stat dump
    pairs = collect_training_pairs(require_quality_signal=False)
    print(f"Found {len(pairs)} training pairs total:")
    quality = [p for p in pairs if p.has_quality_signal]
    print(f"  - With quality signal (enabled DB task): {len(quality)}")
    print(f"  - With any DB task:                       {len([p for p in pairs if p.db_task_count > 0])}")
    print(f"  - With no DB tasks:                       {len([p for p in pairs if p.db_task_count == 0])}")
    print()
    print("By level:")
    for level in ("BEGINNER", "BASIC", "INTERMEDIATE"):
        n = sum(1 for p in pairs if p.proficiency == level)
        print(f"  - {level}: {n}")
    print()
    print("Sample (first 5 with quality signal):")
    for p in [p for p in pairs if p.has_quality_signal][:5]:
        names = " + ".join(p.competency_names)
        print(f"  - {names} ({p.proficiency}) — {p.db_task_count} DB tasks → {p.prompt_path.name}")
