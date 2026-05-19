"""Shared slug + token utilities for retriever and input_files.

Single source of truth for:
  - Slugifying competency names to filename/dir tokens.
  - ``COMPETENCY_ALIASES`` — spelling-variant expansion (Go/Golang, Node/NodeJs,
    React/ReactJs, MongoDB/Mongo, ...).
  - Tokenisation helpers for matching against filenames and directory names.

Previously this logic was duplicated in ``retriever.py`` and ``input_files.py``
with subtle drift: ``retriever`` had aliases, ``input_files`` did a strict
prefix glob. That meant a ``MongoDB + NodeJs + React Framework`` lookup found
prompt-file references via the retriever, but missed the ``input_files``
directory ``input_mongodb_node_react_task_intermediate`` (different word order,
different naming convention) and so the agent saw an empty
``detailed_skill_signal``.
"""

from __future__ import annotations

import re


# Tokens that should expand to a wider set so filename/dir matching is robust
# to spelling variants. Keys are the slugified form of a competency name (or a
# part of one). Both sides of every pair are listed for symmetry.
COMPETENCY_ALIASES: dict[str, set[str]] = {
    "go":              {"go", "golang"},
    "golang":          {"go", "golang"},
    "nodejs":          {"node", "nodejs"},
    "node":            {"node", "nodejs"},
    "javascript":      {"javascript", "js"},
    "typescript":      {"typescript", "ts"},
    "postgres":        {"postgres", "postgresql"},
    "postgresql":      {"postgres", "postgresql"},
    "mongo":           {"mongo", "mongodb"},
    "mongodb":         {"mongo", "mongodb"},
    "k8s":             {"k8s", "kubernetes"},
    "kubernetes":      {"k8s", "kubernetes"},
    # "React Framework" slugifies to "react_framework"; alias both the full
    # slug and the bare "react" part so a directory named ``input_..._react_...``
    # is recognised.
    "react":           {"react", "reactjs"},
    "reactjs":         {"react", "reactjs"},
    "react_framework": {"react", "reactjs", "react_framework"},
}


# Generic words produced by slug splits that should NOT be treated as
# distinguishing tokens. "Framework" matching every file containing that word
# is noise; same for the directory-name connective words.
STOP_TOKENS: frozenset[str] = frozenset({
    "framework", "language", "library",
    "input", "task", "tasks", "background",
})


_TOKEN_SPLIT_RE = re.compile(r"[_\-.]+")


def slugify(name: str) -> str:
    """Lowercase, separator-normalised slug. Used to match against filenames."""
    s = name.lower()
    s = re.sub(r"\.js\b", "js", s)            # node.js -> nodejs
    s = re.sub(r"\s*[-/&]\s*", "_", s)        # "Java - Spring" -> java_spring
    s = re.sub(r"[\s.]+", "_", s)
    s = re.sub(r"[^a-z0-9_]", "", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def competency_tokens(comp_name: str) -> set[str]:
    """Tokens that mark a competency in a filename or directory name.

    Includes the slug, its underscore parts, and aliases for the full slug AND
    for individual parts. Stop tokens are stripped so "Framework" (from
    "React Framework") doesn't match every file with that word.
    """
    slug = slugify(comp_name)
    parts: set[str] = {slug}
    parts.update(slug.split("_"))
    # Expand aliases on every token we've collected so far (full slug + parts).
    for token in list(parts):
        if token in COMPETENCY_ALIASES:
            parts.update(COMPETENCY_ALIASES[token])
    return {p for p in parts if p and len(p) > 1 and p not in STOP_TOKENS}


def name_tokens(text: str) -> set[str]:
    """Split a filename or directory name into matchable tokens (lowercase)."""
    return {t for t in _TOKEN_SPLIT_RE.split(text.lower()) if t}


def name_matches_competency(name: str, comp_name: str) -> bool:
    """True if any competency token appears as a whole token in ``name``."""
    return bool(competency_tokens(comp_name) & name_tokens(name))
