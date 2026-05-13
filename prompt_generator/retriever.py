"""
Retriever — picks 3-5 most relevant existing prompt files as references.

Uses a 5-level fallback ladder so the system degrades gracefully when no
exact-match prompts exist for the requested (competencies, proficiency).

See docs/research/prompt-generator-agent.md for the design.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from prompt_generator.classifier import Competency, TaskCategory, classify_task_category


PROMPT_ROOT = Path(__file__).parent.parent / "task_generation_prompts"

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


# Alias map — competencies whose canonical slug differs from how they appear in
# filenames. Tokens listed here are the set of names the retriever will look for
# when matching a filename, replacing the default slug-only behaviour. Without
# this, a "Go" competency (slug "go") cannot match "golang_docker_prompt.py".
COMPETENCY_ALIASES: dict[str, set[str]] = {
    "go":         {"go", "golang"},
    "golang":     {"go", "golang"},
    "nodejs":     {"node", "nodejs"},
    "node":       {"node", "nodejs"},
    "javascript": {"javascript", "js"},
    "typescript": {"typescript", "ts"},
    "postgres":   {"postgres", "postgresql"},
    "postgresql": {"postgres", "postgresql"},
    "mongo":      {"mongo", "mongodb"},
    "mongodb":    {"mongo", "mongodb"},
    "k8s":        {"k8s", "kubernetes"},
    "kubernetes": {"k8s", "kubernetes"},
}


@dataclass
class RetrievalResult:
    """Result of retrieving reference prompt files for a new prompt synthesis."""
    competencies: list[Competency]
    proficiency: str
    category: TaskCategory
    references: list[Path] = field(default_factory=list)
    bootstrap_mode: bool = False
    fallback_level: int = 1
    notes: list[str] = field(default_factory=list)

    def has_references(self) -> bool:
        return bool(self.references)


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
    """Match how prompt filenames are typically formed from competency names."""
    s = name.lower()
    s = re.sub(r"\.js\b", "js", s)            # node.js -> nodejs
    s = re.sub(r"\s*[-/&]\s*", "_", s)        # "Java - Spring" -> java_spring
    s = re.sub(r"[\s.]+", "_", s)
    s = re.sub(r"[^a-z0-9_]", "", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


# Filename-token splitter — same boundaries we expect prompt files to use.
_FILENAME_TOKEN_RE = re.compile(r"[_\-.]+")


def _name_tokens(comp: Competency) -> set[str]:
    """Tokens we look for in prompt filenames to spot a competency match.

    Returns a set so callers can do constant-time membership tests against
    tokenised filenames. Includes the slug, its underscore parts (so
    "java_spring_mvc" matches a "spring_mvc" filename), and any known aliases
    (e.g. "Go" expands to both "go" and "golang").
    """
    slug = _slugify(comp.name)
    parts: set[str] = {slug}
    parts.update(slug.split("_"))
    if slug in COMPETENCY_ALIASES:
        parts.update(COMPETENCY_ALIASES[slug])
    return {p for p in parts if p and len(p) > 1}


def _filename_tokens(path: Path) -> set[str]:
    """Split the filename stem on common separators for word-boundary matching."""
    return {t for t in _FILENAME_TOKEN_RE.split(path.stem.lower()) if t}


def _file_matches_competency(path: Path, comp: Competency) -> bool:
    """True if any competency token appears as a whole word in the filename.

    Word-boundary matching is required to prevent substring leakage. With plain
    ``tok in fname``, "java" matched "javascript_*.py" and "go" matched
    "mongodb_*.py", polluting every retrieval result.
    """
    file_tokens = _filename_tokens(path)
    return any(tok in file_tokens for tok in _name_tokens(comp))


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


def _find_category_examples(category: TaskCategory, proficiency: str, limit: int = 2) -> list[Path]:
    """Find any prompt files at the same level that match the same category."""
    candidates = _list_prompt_files(proficiency)
    out = []
    for path in candidates:
        # Heuristic — file content category check would be more accurate but slow.
        # Use filename hints instead.
        fname = path.name.lower()
        if category == TaskCategory.APP_AND_DB and any(
            tok in fname for tok in ("postgres", "mongodb", "mysql")
        ):
            out.append(path)
        elif category == TaskCategory.SCRIPT_AND_DB and "sql" in fname and "python" in fname:
            out.append(path)
        elif category == TaskCategory.LLM_FRAMEWORK and any(
            tok in fname for tok in ("langchain", "llamaindex", "rag")
        ):
            out.append(path)
        elif category == TaskCategory.VECTOR_DB and "vector" in fname:
            out.append(path)
        elif category == TaskCategory.MESSAGING and any(
            tok in fname for tok in ("kafka", "rabbit")
        ):
            out.append(path)
        elif category == TaskCategory.FRONTEND and any(
            tok in fname for tok in ("react", "vue", "next", "javascript", "typescript")
        ):
            out.append(path)
        elif category == TaskCategory.CONTAINERIZED_APP and any(
            tok in fname for tok in ("docker", "kubernetes", "k8s")
        ):
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
) -> RetrievalResult:
    """Retrieve reference prompt files via the 5-level fallback ladder.

    Levels:
      1. Exact-match prompt for this combination at this level.
      2. Same combination at adjacent proficiency.
      3. Per-competency prompts at this level + tech-family siblings.
      4. Per-competency prompts at any level.
      5. Same-category prompts at this level (generic).

    Args:
        competencies: list of Competency to look up.
        proficiency: target proficiency level.
        max_refs: cap on the number of references returned.
        exclude_paths: optional set of file paths to skip at every ladder step.
            Use this at compile time to prevent the gold file from appearing in
            its own references (causes metric-score leakage during compilation).
    """
    proficiency = proficiency.upper()
    category = classify_task_category(competencies)
    excluded: set[Path] = set(exclude_paths or ())
    result = RetrievalResult(
        competencies=competencies,
        proficiency=proficiency,
        category=category,
    )

    def _accept(path: Path) -> bool:
        return path not in excluded and path not in result.references

    # LEVEL 1 — exact match at the requested level
    exact = _find_exact_match_file(competencies, proficiency)
    if exact and _accept(exact):
        result.references.append(exact)
        result.notes.append(f"Level 1 (exact match): {exact.name}")
        result.fallback_level = 1
        # If we have an exact match, also pull category examples for style.
        for p in _find_category_examples(category, proficiency, limit=max_refs - 1):
            if _accept(p):
                result.references.append(p)
                result.notes.append(f"Level 1+ (category example): {p.name}")
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

    # LEVEL 5 — generic same-category prompts at this level
    if not result.has_references() or len(result.references) < max_refs:
        for path in _find_category_examples(category, proficiency, limit=max_refs):
            if _accept(path):
                result.references.append(path)
                result.notes.append(f"Level 5 (category example {category.value}): {path.name}")
                result.fallback_level = max(result.fallback_level, 5)

    return _trim_and_return(result, max_refs)


def _trim_and_return(result: RetrievalResult, max_refs: int) -> RetrievalResult:
    if len(result.references) > max_refs:
        result.references = result.references[:max_refs]
    return result
