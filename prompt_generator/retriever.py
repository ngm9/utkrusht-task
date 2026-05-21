"""
Retriever — picks 3-5 most relevant existing prompt files as references.

Uses a 5-level fallback ladder so the system degrades gracefully when no
exact-match prompts exist for the requested (competencies, proficiency).

See docs/research/prompt-generator-agent.md for the design.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from prompt_generator.runtime import Competency, TaskRuntime
from prompt_generator.slugs import (
    COMPETENCY_ALIASES,
    competency_tokens,
    name_tokens,
    slugify,
)


PROMPT_ROOT = Path(__file__).parent.parent / "task_generation_prompts"

# Competency-agnostic last-resort reference prompts. Loaded only at Level 6
# (the 5-level ladder returned nothing). They carry the canonical output JSON
# schema so bootstrap-mode generations don't invent their own key names.
GENERAL_REFERENCE_DIR = PROMPT_ROOT / "_general_reference"

# Map proficiency level → folder under task_generation_prompts/
LEVEL_FOLDERS = {
    "BEGINNER": "Beginner",
    "BASIC": "Basic",
    "INTERMEDIATE": "Intermediate",
    "ADVANCED": "Advanced",
    "EXPERT": "Expert",
}

# Adjacent proficiency lookup for the fallback ladder.
ADJACENT_PROFICIENCY = {
    "BEGINNER": ["BASIC"],
    "BASIC": ["INTERMEDIATE", "BEGINNER"],
    "INTERMEDIATE": ["BASIC", "ADVANCED"],
    "ADVANCED": ["INTERMEDIATE", "EXPERT"],
    "EXPERT": ["ADVANCED"],
}


# Tech-family adjacency — when the exact competency has no prompt,
# these are siblings whose prompts can serve as references.
# Keys are lowercased competency name fragments.
TECH_FAMILY = {
    "langchain":         ["llamaindex", "rag", "python"],
    "llamaindex":        ["langchain", "rag", "python"],
    "rag":               ["langchain", "llamaindex", "vector databases", "python"],
    "vector databases":  ["langchain", "llamaindex", "python"],
    "kafka":             ["rabbitmq", "java", "python", "node"],
    "microservices":     ["java", "spring boot", "node"],
    "spring mvc":        ["spring boot", "spring webservices", "java"],
    "spring webservices": ["spring boot", "spring mvc", "java"],
    "postgresql":        ["sql", "mongodb"],
    "mongodb":           ["postgresql", "sql"],
    "nodejs":            ["expressjs", "javascript"],
    "expressjs":         ["nodejs"],
    "javascript":        ["typescript", "html and css"],
    "typescript":        ["javascript"],
    "docker":            ["kubernetes", "python", "java", "go"],
    "kubernetes":        ["docker"],
    "redis":             ["postgresql", "mongodb", "sql"],
}


# COMPETENCY_ALIASES lives in slugs.py and is re-exported above for callers
# that historically imported it from retriever.


@dataclass
class RetrievalResult:
    """Result of retrieving reference prompt files for a new prompt synthesis."""
    competencies: list[Competency]
    proficiency: str
    runtime: TaskRuntime | None = None
    references: list[Path] = field(default_factory=list)
    bootstrap_mode: bool = False
    fallback_level: int = 1
    notes: list[str] = field(default_factory=list)
    # True when the 5-level ladder found nothing and we fell back to the
    # competency-agnostic general reference (Level 6). Callers should treat
    # such generations as needing extra review.
    used_general_fallback: bool = False

    def has_references(self) -> bool:
        return bool(self.references)


def _general_reference_path(proficiency: str) -> Optional[Path]:
    """Path to the general reference prompt for this proficiency, or None.

    Falls back BASIC→nearest if an exact level file is missing, so a future
    proficiency value never produces a hard miss.
    """
    level = proficiency.upper()
    candidate = GENERAL_REFERENCE_DIR / f"general_{level.lower()}_prompt.py"
    if candidate.exists():
        return candidate
    # Fall back to BASIC, then to whatever general reference exists.
    basic = GENERAL_REFERENCE_DIR / "general_basic_prompt.py"
    if basic.exists():
        return basic
    existing = sorted(GENERAL_REFERENCE_DIR.glob("general_*_prompt.py"))
    return existing[0] if existing else None


# ----------------------------------------------------------------------
# File discovery helpers
# ----------------------------------------------------------------------

def _level_folder(proficiency: str) -> Path:
    folder = LEVEL_FOLDERS.get(proficiency.upper())
    if not folder:
        raise ValueError(f"Unknown proficiency level: {proficiency}")
    return PROMPT_ROOT / folder


def _list_prompt_files(proficiency: str) -> list[Path]:
    """Return curated prompt files at this proficiency level.

    Two layouts are supported under ``<level>/``::

        <level>/<slug>.py                          # flat, legacy
        <level>/<slug>/<slug>.py                   # per-slug folder, canonical

    The canonical per-slug convention is required so that historical originals
    under ``<level>/<slug>/original_temp_prompt/<...>.py`` are skipped — without
    this, retriever results would include both the curated file and its archived
    predecessor.
    """
    folder = _level_folder(proficiency)
    if not folder.exists():
        return []
    out: list[Path] = []
    # Flat layout — direct .py files in the level folder.
    for p in folder.glob("*.py"):
        if p.name.startswith("__"):
            continue
        out.append(p)
    # Per-slug folders — only the canonical <slug>/<slug>.py is treated as
    # curated. Anything else (original_temp_prompt/, tests/, etc.) is ignored.
    for child in folder.iterdir():
        if not child.is_dir() or child.name.startswith("__"):
            continue
        canonical = child / f"{child.name}.py"
        if canonical.exists():
            out.append(canonical)
    return sorted(out)


def _slugify(name: str) -> str:
    """Compatibility shim — delegates to ``slugs.slugify``."""
    return slugify(name)


def _name_tokens(comp: Competency) -> set[str]:
    """Compatibility shim — delegates to ``slugs.competency_tokens``."""
    return competency_tokens(comp.name)


def _filename_tokens(path: Path) -> set[str]:
    """Split the filename stem on common separators for word-boundary matching."""
    return name_tokens(path.stem)


def _file_matches_competency(path: Path, comp: Competency) -> bool:
    """True if any competency token appears as a whole word in the filename.

    Word-boundary matching is required to prevent substring leakage. With plain
    ``tok in fname``, "java" matched "javascript_*.py" and "go" matched
    "mongodb_*.py", polluting every retrieval result.
    """
    return bool(_name_tokens(comp) & _filename_tokens(path))


def _find_exact_match_file(competencies: list[Competency], proficiency: str) -> Optional[Path]:
    """Find a prompt file whose name covers all given competencies at this level."""
    candidates = _list_prompt_files(proficiency)
    for path in candidates:
        if all(_file_matches_competency(path, c) for c in competencies):
            return path
    return None


def _find_per_competency_files(
    competencies: list[Competency],
    proficiency: str,
) -> list[Path]:
    """Find a prompt file matching each individual competency at this level."""
    out = []
    seen: set[str] = set()
    for comp in competencies:
        for path in _list_prompt_files(proficiency):
            if _file_matches_competency(path, comp) and path.name not in seen:
                # Prefer single-competency files (shorter name = more specific)
                out.append(path)
                seen.add(path.name)
                break
    return out


def _find_tech_family_files(comp: Competency, proficiency: str) -> list[Path]:
    """Find prompt files for sibling competencies in the same tech family."""
    siblings = TECH_FAMILY.get(comp.name_lower, [])
    out = []
    seen: set[str] = set()
    for sibling in siblings:
        sib_comp = Competency(name=sibling, proficiency=comp.proficiency)
        for path in _list_prompt_files(proficiency):
            if _file_matches_competency(path, sib_comp) and path.name not in seen:
                out.append(path)
                seen.add(path.name)
                break
    return out


def _find_runtime_examples(runtime: TaskRuntime, proficiency: str, limit: int = 2) -> list[Path]:
    """Find any prompt files at the same level whose filename matches this runtime shape.

    Heuristic file-content check would be more accurate but slow — use filename hints
    based on the structured TaskRuntime fields (runtime + datastores + kind).
    """
    candidates = _list_prompt_files(proficiency)
    out: list[Path] = []
    has_db = bool(runtime.datastores)
    has_msg = bool(runtime.messaging)
    db_tokens = tuple(runtime.datastores) + ("postgres", "mongodb", "mysql") if has_db else ()
    for path in candidates:
        fname = path.name.lower()
        matched = False
        # app/script + DB → filename mentions the datastore
        if has_db and any(tok in fname for tok in db_tokens):
            matched = True
        # script-only (python+SQL style) when explicit datastore not bracketed
        elif runtime.kind == "script" and "sql" in fname and "python" in fname:
            matched = True
        # LLM framework
        elif runtime.kind == "llm" and any(
            tok in fname for tok in ("langchain", "llamaindex", "rag")
        ):
            matched = True
        elif runtime.kind == "vector_db" and "vector" in fname:
            matched = True
        elif has_msg and any(tok in fname for tok in ("kafka", "rabbit")):
            matched = True
        elif runtime.kind == "frontend" and any(
            tok in fname for tok in ("react", "vue", "next", "javascript", "typescript")
        ):
            matched = True
        elif runtime.kind == "mobile" and any(
            tok in fname for tok in ("flutter", "react_native", "dart")
        ):
            matched = True
        elif runtime.kind == "testing" and runtime.needs_browser and any(
            tok in fname for tok in ("playwright", "selenium", "cypress")
        ):
            matched = True
        if matched:
            out.append(path)
        if len(out) >= limit:
            break
    return out


# ----------------------------------------------------------------------
# Public API — the fallback ladder
# ----------------------------------------------------------------------

def retrieve_references(
    competencies: list[Competency],
    proficiency: str,
    max_refs: int = 5,
    exclude_paths: Optional[set[Path]] = None,
    runtime: TaskRuntime | None = None,
) -> RetrievalResult:
    """Retrieve reference prompt files via the 6-level fallback ladder.

    Levels:
      1. Exact-match prompt for this combination at this level.
      2. Same combination at adjacent proficiency.
      3. Per-competency prompts at this level + tech-family siblings.
      4. Per-competency prompts at any level.
      5. Same-category prompts at this level (generic).
      6. Competency-agnostic general reference for this proficiency — the
         last-resort skeleton carrying the canonical output JSON schema.

    Args:
        competencies: list of Competency to look up.
        proficiency: target proficiency level.
        max_refs: cap on the number of references returned.
        exclude_paths: optional set of file paths to skip at every ladder step.
            Use this at compile time to prevent the gold file from appearing in
            its own references (causes metric-score leakage during compilation).
    """
    proficiency = proficiency.upper()
    excluded: set[Path] = set(exclude_paths or ())
    result = RetrievalResult(
        competencies=competencies,
        proficiency=proficiency,
        runtime=runtime,
    )

    def _accept(path: Path) -> bool:
        return path not in excluded and path not in result.references

    # LEVEL 1 — exact match at the requested level
    exact = _find_exact_match_file(competencies, proficiency)
    if exact and _accept(exact):
        result.references.append(exact)
        result.notes.append(f"Level 1 (exact match): {exact.name}")
        result.fallback_level = 1
        # If we have an exact match AND a TaskRuntime was supplied, also pull
        # runtime-shape examples for style. Skip when no runtime is provided
        # (e.g. preflight) — Level 5 fires only with a classified runtime.
        if runtime is not None:
            for p in _find_runtime_examples(runtime, proficiency, limit=max_refs - 1):
                if _accept(p):
                    result.references.append(p)
                    result.notes.append(f"Level 1+ (runtime example): {p.name}")
        if len(result.references) >= max_refs:
            return _trim_and_return(result, max_refs)
    elif exact:
        # exact existed but was excluded — flag bootstrap mode so callers know
        result.bootstrap_mode = True
        result.notes.append(f"Level 1 excluded by caller: {exact.name}")

    # If we get here, we're in bootstrap mode (no usable exact match)
    if not result.has_references():
        result.bootstrap_mode = True

    # LEVEL 2 — adjacent proficiency, same combination
    for adj_level in ADJACENT_PROFICIENCY.get(proficiency, []):
        adj_match = _find_exact_match_file(competencies, adj_level)
        if adj_match and _accept(adj_match):
            result.references.append(adj_match)
            result.notes.append(
                f"Level 2 (adjacent proficiency {adj_level}): {adj_match.name}"
            )
            result.fallback_level = max(result.fallback_level, 2)
            break

    # LEVEL 3 — per-competency prompts at this level
    for path in _find_per_competency_files(competencies, proficiency):
        if _accept(path):
            result.references.append(path)
            result.notes.append(f"Level 3 (per-competency same level): {path.name}")
            result.fallback_level = max(result.fallback_level, 3)

    # LEVEL 3 (continued) — tech-family siblings at this level
    for comp in competencies:
        for path in _find_tech_family_files(comp, proficiency):
            if _accept(path):
                result.references.append(path)
                result.notes.append(f"Level 3 (tech family of '{comp.name}'): {path.name}")
                result.fallback_level = max(result.fallback_level, 3)

    # LEVEL 4 — per-competency prompts at ANY level
    if not result.has_references() or len(result.references) < max_refs:
        for level in LEVEL_FOLDERS:
            if level == proficiency:
                continue
            for path in _find_per_competency_files(competencies, level):
                if _accept(path):
                    result.references.append(path)
                    result.notes.append(f"Level 4 (per-competency at {level}): {path.name}")
                    result.fallback_level = max(result.fallback_level, 4)

    # LEVEL 5 — generic same-shape prompts at this level.
    # Only fires when the caller passed a classified TaskRuntime (Level 5 needs
    # the structured fields for filename matching). Without it, skip to Level 6.
    if runtime is not None and (not result.has_references() or len(result.references) < max_refs):
        for path in _find_runtime_examples(runtime, proficiency, limit=max_refs):
            if _accept(path):
                result.references.append(path)
                result.notes.append(
                    f"Level 5 (runtime example {runtime.runtime}/{runtime.kind}): {path.name}"
                )
                result.fallback_level = max(result.fallback_level, 5)

    # LEVEL 6 — last-resort general reference. Only fires when the ladder found
    # NOTHING. Guarantees the generator always has at least the canonical
    # output JSON schema to copy, so bootstrap-mode combos can't silently
    # invent synonym keys and produce a hollow task.
    if not result.has_references():
        general = _general_reference_path(proficiency)
        if general and general not in excluded:
            result.references.append(general)
            result.notes.append(f"Level 6 (general reference): {general.name}")
            result.fallback_level = max(result.fallback_level, 6)
            result.used_general_fallback = True

    return _trim_and_return(result, max_refs)


def _trim_and_return(result: RetrievalResult, max_refs: int) -> RetrievalResult:
    if len(result.references) > max_refs:
        result.references = result.references[:max_refs]
    return result
