"""`strip_not_to_include` removes a leaked 'NOT TO INCLUDE …' section (a
meta-instruction some prompts list as a README section) from the candidate
README, without touching real content or ordinary bullets.
"""
from generators.task.creator import strip_not_to_include


def test_removes_trailing_section():
    md = "## Task Overview\nfoo\n\n## NOT TO INCLUDE in README\n(internal note)\n- no setup\n"
    out = strip_not_to_include(md)
    assert "NOT TO INCLUDE" not in out
    assert "Task Overview" in out and "foo" in out


def test_stops_at_next_heading():
    md = "## NOT TO INCLUDE\nsecret line\n## Real Section\nkeep me\n"
    out = strip_not_to_include(md)
    assert "secret line" not in out
    assert "Real Section" in out and "keep me" in out


def test_handles_h3_and_colon_variants():
    md = "## How to Verify\nv\n### NOT TO INCLUDE in README:\ndrop this\n"
    out = strip_not_to_include(md)
    assert "drop this" not in out
    assert "How to Verify" in out


def test_noop_when_absent():
    md = "## Task Overview\nall good\n"
    assert strip_not_to_include(md) == md


def test_leaves_ordinary_bullets():
    # a bullet that merely mentions "do not include" is NOT a heading → kept
    md = "## Helpful Tips\n- do not include secrets in code\n"
    assert "do not include secrets in code" in strip_not_to_include(md)


def test_empty_input():
    assert strip_not_to_include("") == ""
    assert strip_not_to_include(None) is None
