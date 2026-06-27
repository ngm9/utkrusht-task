"""Deterministic candidate-facing resource guards in ``creator.py``.

Covers the two post-generation normalizers that keep agent tasks honest:

* ``_ensure_readme_env_note`` — guarantees provider-key (real-LLM) tasks carry a
  ``> [!NOTE]`` env-setup admonition in the README.
* ``_imperative_prereq_items`` — flags prerequisites written as imperative task
  steps instead of declarative assumed-knowledge.

These are pure functions, so they import without the heavy generation stack —
but ``creator`` constructs an OpenAI client at import, so a dummy key is set
before import (no network calls happen here).
"""
from __future__ import annotations

import os

os.environ.setdefault("OPENAI_API_KEY", "dummy-test-key")

from generators.task.creator import (  # noqa: E402 — must follow the env default
    _ensure_readme_env_note,
    _imperative_prereq_items,
)


# ── _imperative_prereq_items ────────────────────────────────────────────────

IMPERATIVE = [
    "Run the readiness script and ensure Postgres starts",
    "Use Docker Compose to run local PostgreSQL",
    "Configure the LLM provider key in .env",
    "Test behavior changes via HTTP requests",
]

DECLARATIVE = [
    "Python 3.11 proficiency; able to run pytest locally",
    "Comfort with a Docker-backed PostgreSQL instance",
    "Familiarity with FastAPI endpoints",
    "A real LLM provider key (e.g., OpenAI) supplied via a local .env file",
    "Understanding of tool-calling agents",
]


def test_flags_every_imperative_item():
    assert _imperative_prereq_items(IMPERATIVE) == IMPERATIVE


def test_passes_declarative_items():
    assert _imperative_prereq_items(DECLARATIVE) == []


def test_strips_bullet_prefix_before_checking():
    assert _imperative_prereq_items(["- Run the script"]) == ["- Run the script"]


def test_non_list_returns_empty():
    assert _imperative_prereq_items("not a list") == []
    assert _imperative_prereq_items(None) == []


def test_blank_and_non_string_entries_skipped():
    assert _imperative_prereq_items(["", "  ", 5]) == []


def test_mixed_returns_only_imperative():
    assert _imperative_prereq_items([DECLARATIVE[0], IMPERATIVE[0]]) == [IMPERATIVE[0]]


# ── _ensure_readme_env_note ─────────────────────────────────────────────────

README = (
    "## Task Overview\nA thing.\n\n"
    "## How to Verify\n- Run the tests\n\n"
    "## Helpful Tips\n- Look around\n"
)


def _files(readme=README, env=".env.example", env_body="OPENAI_API_KEY=\n"):
    files = {"README.md": readme, "agent/main.py": "..."}
    if env is not None:
        files[env] = env_body
    return files


def test_note_injected_under_how_to_verify():
    files = _files()
    _ensure_readme_env_note(files)
    r = files["README.md"]
    assert "[!NOTE]" in r and ".env.example" in r
    # Inside How to Verify, before the next section, and adds no new heading.
    assert r.index("## How to Verify") < r.index("[!NOTE]") < r.index("## Helpful Tips")
    assert r.count("## ") == README.count("## ")


def test_injection_is_idempotent():
    files = _files()
    _ensure_readme_env_note(files)
    once = files["README.md"]
    _ensure_readme_env_note(files)
    assert files["README.md"] == once


def test_no_op_without_provider_key():
    files = _files(env_body="DATABASE_URL=\n")
    _ensure_readme_env_note(files)
    assert "[!NOTE]" not in files["README.md"]


def test_no_op_without_env_example():
    files = _files(env=None)
    _ensure_readme_env_note(files)
    assert "[!NOTE]" not in files["README.md"]


def test_falls_back_to_first_heading_when_no_how_to_verify():
    readme = "## Task Overview\nA thing.\n\n## Objectives\n- Do it\n"
    files = _files(readme=readme, env_body="ANTHROPIC_API_KEY=\n")
    _ensure_readme_env_note(files)
    r = files["README.md"]
    assert "[!NOTE]" in r and r.index("## Task Overview") < r.index("[!NOTE]")


def test_no_op_when_no_headed_section():
    files = _files(readme="just text, no headers\n")
    _ensure_readme_env_note(files)
    assert "[!NOTE]" not in files["README.md"]
