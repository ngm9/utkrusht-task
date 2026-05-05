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
    folder = _level_folder(proficiency)
    if not folder.exists():
        return []
    return sorted(p for p in folder.glob("*.py") if not p.name.startswith("__"))


def _slugify(name: str) -> str:
    """Match how prompt filenames are typically formed from competency names."""
    s = name.lower()
    s = re.sub(r"\.js\b", "js", s)            # node.js -> nodejs
    s = re.sub(r"\s*[-/&]\s*", "_", s)        # "Java - Spring" -> java_spring
    s = re.sub(r"[\s.]+", "_", s)
    s = re.sub(r"[^a-z0-9_]", "", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def _name_tokens(comp: Competency) -> list[str]:
    """Tokens we look for in prompt filenames to spot a competency match."""
    slug = _slugify(comp.name)
    parts = [slug]
    # Also split on underscore so "java_spring_mvc" matches a "spring_mvc" filename
    parts.extend(slug.split("_"))
    return [p for p in parts if p and len(p) > 1]


def _file_matches_competency(path: Path, comp: Competency) -> bool:
    fname = path.name.lower()
    for tok in _name_tokens(comp):
        if tok in fname:
            return True
    return False


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
) -> RetrievalResult:
    """Retrieve reference prompt files via the 5-level fallback ladder.

    Levels:
      1. Exact-match prompt for this combination at this level.
      2. Same combination at adjacent proficiency.
      3. Per-competency prompts at this level + tech-family siblings.
      4. Per-competency prompts at any level.
      5. Same-category prompts at this level (generic).
    """
    proficiency = proficiency.upper()
    category = classify_task_category(competencies)
    result = RetrievalResult(
        competencies=competencies,
        proficiency=proficiency,
        category=category,
    )

    # LEVEL 1 — exact match at the requested level
    exact = _find_exact_match_file(competencies, proficiency)
    if exact:
        result.references.append(exact)
        result.notes.append(f"Level 1 (exact match): {exact.name}")
        result.fallback_level = 1
        # If we have an exact match, also pull category examples for style.
        result.references.extend(
            p for p in _find_category_examples(category, proficiency, limit=max_refs - 1)
            if p != exact
        )
        return _trim_and_return(result, max_refs)

    # If we get here, we're in bootstrap mode (no exact match exists)
    result.bootstrap_mode = True

    # LEVEL 2 — adjacent proficiency, same combination
    for adj_level in ADJACENT_PROFICIENCY.get(proficiency, []):
        adj_match = _find_exact_match_file(competencies, adj_level)
        if adj_match:
            result.references.append(adj_match)
            result.notes.append(
                f"Level 2 (adjacent proficiency {adj_level}): {adj_match.name}"
            )
            result.fallback_level = 2
            break

    # LEVEL 3 — per-competency prompts at this level
    per_comp = _find_per_competency_files(competencies, proficiency)
    for path in per_comp:
        if path not in result.references:
            result.references.append(path)
            result.notes.append(f"Level 3 (per-competency same level): {path.name}")
            result.fallback_level = max(result.fallback_level, 3)

    # LEVEL 3 (continued) — tech-family siblings at this level
    for comp in competencies:
        for path in _find_tech_family_files(comp, proficiency):
            if path not in result.references:
                result.references.append(path)
                result.notes.append(f"Level 3 (tech family of '{comp.name}'): {path.name}")
                result.fallback_level = max(result.fallback_level, 3)

    # LEVEL 4 — per-competency prompts at ANY level
    if not result.has_references() or len(result.references) < max_refs:
        for level in LEVEL_FOLDERS:
            if level == proficiency:
                continue
            for path in _find_per_competency_files(competencies, level):
                if path not in result.references:
                    result.references.append(path)
                    result.notes.append(f"Level 4 (per-competency at {level}): {path.name}")
                    result.fallback_level = max(result.fallback_level, 4)

    # LEVEL 5 — generic same-category prompts at this level
    if not result.has_references() or len(result.references) < max_refs:
        for path in _find_category_examples(category, proficiency, limit=max_refs):
            if path not in result.references:
                result.references.append(path)
                result.notes.append(f"Level 5 (category example {category.value}): {path.name}")
                result.fallback_level = max(result.fallback_level, 5)

    return _trim_and_return(result, max_refs)


def _trim_and_return(result: RetrievalResult, max_refs: int) -> RetrievalResult:
    if len(result.references) > max_refs:
        result.references = result.references[:max_refs]
    return result
