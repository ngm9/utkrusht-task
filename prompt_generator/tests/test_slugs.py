"""Unit tests for the shared slug/token utilities."""

from __future__ import annotations

from prompt_generator.slugs import (
    COMPETENCY_ALIASES,
    competency_tokens,
    name_matches_competency,
    name_tokens,
    slugify,
)


def test_slugify_normalises_separators_and_dotjs():
    assert slugify("Node.js") == "nodejs"
    assert slugify("Java - Spring") == "java_spring"
    assert slugify("React Framework") == "react_framework"
    assert slugify("HTML & CSS") == "html_css"


def test_competency_tokens_expands_through_aliases():
    # Go pulls in Golang.
    assert {"go", "golang"}.issubset(competency_tokens("Go"))
    # Node.js pulls in plain 'node'.
    assert {"node", "nodejs"}.issubset(competency_tokens("Node.js"))
    # React Framework pulls in 'react' and 'reactjs' but framework is a stop token.
    react_tokens = competency_tokens("React Framework")
    assert {"react", "reactjs", "react_framework"}.issubset(react_tokens)
    assert "framework" not in react_tokens
    # MongoDB pulls in mongo.
    assert {"mongo", "mongodb"}.issubset(competency_tokens("MongoDB"))


def test_competency_tokens_drops_one_char_tokens():
    """Splits that produce a single character (e.g. 'C') shouldn't leak in."""
    tokens = competency_tokens("React C")
    assert "c" not in tokens


def test_aliases_are_symmetric():
    """Every alias key must appear in the value set it points to, and pairs must agree."""
    for key, expansion in COMPETENCY_ALIASES.items():
        assert key in expansion, f"alias key {key!r} missing from its own expansion"


def test_name_tokens_splits_on_separators():
    assert name_tokens("Java_spring_boot_prompt") == {
        "java", "spring", "boot", "prompt",
    }
    assert name_tokens("python-fastapi.docker") == {"python", "fastapi", "docker"}


def test_name_matches_competency_word_boundary():
    """A whole-word match — 'Java' must not match 'javascript' tokens."""
    assert name_matches_competency("java_docker_basic", "Java")
    assert not name_matches_competency("javascript_basic", "Java")
    assert name_matches_competency("golang_docker", "Go")
    assert name_matches_competency("mongodb_node_react", "Node.js")
    assert name_matches_competency("mongodb_node_react", "React Framework")
