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
    require_validator_pass: bool = True,
) -> list[TrainingPair]:
    """Walk the prompt directory and build a training set.

    Args:
        env: Supabase env to use for quality filtering.
        require_quality_signal: If True, drop pairs with no enabled DB tasks.
        levels: Restrict to these proficiency levels (defaults to all).
        require_validator_pass: If True (default), drop pairs whose gold file
            does not pass ``validator.validate_prompt_file``. Gold files that
            would never pass the validator can't be useful demos and would
            inflate ``metric.py`` failures during compile.
    """
    from prompt_generator.validator import validate_prompt_file
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

            if require_validator_pass:
                comp_dicts = [
                    {"name": n, "proficiency": level_to_use} for n in comp_names
                ]
                v = validate_prompt_file(source, comp_dicts, level_to_use)
                if not v.passed:
                    # Pre-existing data bug in the gold file — skip silently so
                    # compile doesn't poison demos with a structurally broken
                    # gold. Use trainset.__main__ to see which files were dropped.
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
    """Convert TrainingPair objects to MINIMAL dspy.Example objects.

    The Examples have only (competencies, proficiency) as inputs and the gold
    output. Useful only when the training-time module computes the other 6
    inputs internally (live I/O during compile). For most compile runs prefer
    ``to_dspy_examples_rich`` which pre-computes the full 8-input shape and
    prevents gold-file leakage.
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


# ----------------------------------------------------------------------
# Rich training-pair builder — pre-computes the full 8-input shape
# ----------------------------------------------------------------------

def _format_references_text(paths: list[Path]) -> str:
    """Concatenate reference prompt sources with headers (mirrors agent.py)."""
    parts: list[str] = []
    for path in paths:
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as e:
            parts.append(f"# === {path.name} (could not read: {e}) ===")
            continue
        rel = path
        try:
            rel = path.relative_to(Path.cwd())
        except ValueError:
            rel = path
        parts.append(
            f"# ===== Reference: {path.name} =====\n"
            f"# Path: {rel}\n\n"
            f"{content}"
        )
    if not parts:
        return "(no reference prompts found — bootstrap mode using scopes only)"
    return "\n\n".join(parts)


def _format_similar_tasks_text(tasks: list) -> str:
    """Concatenate similar-task summaries (mirrors agent.py)."""
    if not tasks:
        return "(no similar tasks in DB — bootstrap mode)"
    return "\n\n---\n\n".join(t.summary() for t in tasks[:5])


def to_dspy_examples_rich(
    pairs: list[TrainingPair],
    env: str = "dev",
    exclude_self_from_references: bool = True,
) -> list[dspy.Example]:
    """Build full-input-shape training Examples (8 inputs + gold output).

    Pre-computes ``task_category``, ``competency_scopes``, ``reference_prompts``,
    ``similar_tasks``, and ``detailed_skill_signal`` for each pair so the
    compile-time module does not have to do live I/O on every demo trial.

    Crucial: when ``exclude_self_from_references=True`` (default), the gold
    prompt file is excluded from its own ``reference_prompts``. Without this
    filter the agent would see the gold file as a reference and trivially copy
    it, inflating the metric score with leakage.

    Returns a list of ``dspy.Example`` whose ``.with_inputs(...)`` declares the
    full set of 8 input fields the agent's signature expects.
    """
    from prompt_generator.classifier import Competency, classify_task_category
    from prompt_generator.db_queries import (
        fetch_competency_scope,
        fetch_similar_tasks,
        init_supabase,
    )
    from prompt_generator.input_files import build_detailed_skill_signal
    from prompt_generator.retriever import retrieve_references

    supabase = init_supabase(env)
    examples: list[dspy.Example] = []

    for p in pairs:
        comps = [
            Competency(name=n, proficiency=p.proficiency)
            for n in p.competency_names
        ]
        comp_str = ", ".join(f"{c.name} ({p.proficiency})" for c in comps)

        # Classifier — deterministic, no I/O
        category = classify_task_category(comps)

        # Retriever — exclude the gold path so the ladder reaches down for
        # genuinely sibling references rather than handing back the gold itself
        # (which would inflate metric scores via leakage).
        excluded = {p.prompt_path} if exclude_self_from_references else None
        retrieval = retrieve_references(comps, p.proficiency, exclude_paths=excluded)
        refs_paths = list(retrieval.references)
        refs_text = _format_references_text(refs_paths)

        # Scopes — Supabase
        scopes_text: list[str] = []
        for c in comps:
            scope = fetch_competency_scope(supabase, c.name, p.proficiency)
            if scope and scope.get("scope"):
                scopes_text.append(
                    f"[{c.name} ({p.proficiency})]\n{scope['scope']}"
                )
        scopes_str = (
            "\n\n---\n\n".join(scopes_text) if scopes_text else "(no scopes available)"
        )

        # Similar tasks — Supabase (representative of runtime; no leakage filter)
        similar = fetch_similar_tasks(supabase, p.competency_names, p.proficiency)
        tasks_text = _format_similar_tasks_text(similar)

        # Skill signal — task_input_files + task_scenarios.json
        skill_signal, _meta = build_detailed_skill_signal(comps, p.proficiency)

        ex = dspy.Example(
            competencies=comp_str,
            proficiency=p.proficiency,
            task_category=category.value,
            competency_scopes=scopes_str,
            reference_prompts=refs_text,
            similar_tasks=tasks_text,
            detailed_skill_signal=skill_signal,
            feedback_from_previous_attempt="",
            new_prompt_file=p.prompt_source,
        ).with_inputs(
            "competencies",
            "proficiency",
            "task_category",
            "competency_scopes",
            "reference_prompts",
            "similar_tasks",
            "detailed_skill_signal",
            "feedback_from_previous_attempt",
        )
        examples.append(ex)

    return examples


if __name__ == "__main__":
    # Quick stat dump — compare pre/post validator filter
    pairs_all = collect_training_pairs(
        require_quality_signal=False, require_validator_pass=False,
    )
    pairs_clean = collect_training_pairs(
        require_quality_signal=False, require_validator_pass=True,
    )
    dropped = len(pairs_all) - len(pairs_clean)

    print(f"Parseable .py files:                    {len(pairs_all)}")
    print(f"  - dropped by validator check:         {dropped}")
    print(f"  - kept (gold passes validator):       {len(pairs_clean)}")
    print()
    quality = [p for p in pairs_clean if p.has_quality_signal]
    print(f"Among kept pairs:")
    print(f"  - With quality signal (enabled DB task): {len(quality)}")
    print(f"  - With any DB task:                       {len([p for p in pairs_clean if p.db_task_count > 0])}")
    print(f"  - With no DB tasks:                       {len([p for p in pairs_clean if p.db_task_count == 0])}")
    print()
    print("By level (kept):")
    for level in ("BEGINNER", "BASIC", "INTERMEDIATE"):
        n = sum(1 for p in pairs_clean if p.proficiency == level)
        print(f"  - {level}: {n}")
    print()
    if dropped:
        kept_paths = {p.prompt_path for p in pairs_clean}
        print("Dropped by validator (review these — registry key likely malformed):")
        for p in pairs_all:
            if p.prompt_path not in kept_paths:
                names = " + ".join(p.competency_names)
                print(f"  - {names} ({p.proficiency}) → {p.prompt_path.name}")
        print()
    print("Sample (first 5 quality-signal pairs):")
    for p in quality[:5]:
        names = " + ".join(p.competency_names)
        print(f"  - {names} ({p.proficiency}) — {p.db_task_count} DB tasks → {p.prompt_path.name}")
