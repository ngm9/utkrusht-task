"""Architectural guard: no flow package imports a *sibling* flow.

Each ``flows/<x>`` may import only from ``flows._base`` and ``infra/`` (and its
own subpackages) — never from another flow. Enforced statically over source.
"""
import pathlib
import re

FLOWS = pathlib.Path(__file__).resolve().parents[1] / "flows"
SIBLINGS = {"tech", "pr_review", "non_tech", "design_review"}
_IMPORT_RE = re.compile(r"(?:from|import)\s+flows\.([a-z_]+)")


def test_no_flow_imports_a_sibling_flow():
    offenders = []
    for py in FLOWS.rglob("*.py"):
        parts = py.relative_to(FLOWS).parts
        if not parts or parts[0] not in SIBLINGS:
            continue
        own = parts[0]
        src = py.read_text(encoding="utf-8", errors="replace")
        for match in _IMPORT_RE.finditer(src):
            other = match.group(1)
            if other in SIBLINGS and other != own:
                offenders.append(f"{py.relative_to(FLOWS.parent)}: imports flows.{other}")
    assert not offenders, "sibling-flow imports found:\n" + "\n".join(offenders)
