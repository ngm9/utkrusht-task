"""Deterministic trace-fixture consistency check (static; no execution).

Agent tasks may ship a captured "trace" fixture (e.g. ``fixtures/sample_trace.json``
or a ``*.jsonl``) so a candidate can see the agent's tool calls -> tool results ->
final output before touching code. These traces are invented by the task-gen LLM
and drift: a fabricated trace can be malformed, or reference a tool name / entity
id that the actual repo never produces -- "plausible but impossible vs the code",
which a knowledgeable candidate spots and stops trusting the task over.

``check_trace_consistency`` cross-checks a shipped trace against the SAME repo it
ships with -- the declared tool schemas and the seed data -- reading only
``code_files`` (no execution, no provider key, no E2B gate). It SELF-SCOPES:
returns empty results when the task ships no trace fixture, so non-agent tasks and
trace-less agent tasks are unaffected.

Severity routing keeps false positives from forcing expensive regenerations:
  * syntax (a trace that won't parse)                 -> blocking
  * a tool name absent from the repo's tool set       -> blocking, but ONLY when a
    non-empty tool set was confidently extracted
  * an id-like arg value absent from the seed         -> suggestion (seed
    extraction is fuzzier, so advisory only)

Every extractor errs toward OVER-collecting the "known" sets (tools / ids): a
larger known set is more permissive, so an imperfect heuristic skips a check
rather than flagging a valid trace.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Tuple


# ── locating the trace fixtures ─────────────────────────────────────────────

def _trace_files(code_files: Dict[str, str]) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    for path, body in (code_files or {}).items():
        low = path.lower()
        if "trace" in low and low.endswith((".json", ".jsonl")) and isinstance(body, str):
            out.append((path, body))
    return out


# ── parsing a trace (dict-with-steps OR JSONL OR list) ──────────────────────

def _parse_trace(body: str) -> Tuple[Any, str | None]:
    """Return ``(parsed, error)``. Tries whole-file JSON first, then JSONL."""
    body = (body or "").strip()
    if not body:
        return None, "empty trace file"
    try:
        return json.loads(body), None
    except json.JSONDecodeError:
        pass
    rows: List[Any] = []
    for i, line in enumerate(body.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            return None, f"line {i} is not valid JSON ({exc.msg})"
    if not rows:
        return None, "no valid JSON content"
    return rows, None


# ── walking a parsed trace for tool names + id-like arg values ──────────────

_ID_KEY_RE = re.compile(r"(^|_)id$", re.I)  # id, device_id, gateway_id, merchant_id…


def _walk(node: Any):
    """Yield every dict found anywhere in the parsed structure."""
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from _walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from _walk(v)


def _tool_calls_in(parsed: Any) -> List[Dict[str, Any]]:
    """Collect ``{name, arguments}`` tool-call records from a parsed trace.

    Handles both shapes seen in the wild: items inside any ``tool_calls`` list
    (flat ``{name, arguments}`` or OpenAI-nested ``{function: {name, arguments}}``)
    and ``role: "tool"`` step objects that carry a ``name``.
    """
    calls: List[Dict[str, Any]] = []
    for d in _walk(parsed):
        tcs = d.get("tool_calls")
        if isinstance(tcs, list):
            for tc in tcs:
                if not isinstance(tc, dict):
                    continue
                name = tc.get("name")
                args = tc.get("arguments")
                if not isinstance(name, str):
                    fn = tc.get("function")
                    if isinstance(fn, dict):
                        name = fn.get("name")
                        args = fn.get("arguments", args)
                if isinstance(name, str):
                    calls.append({"name": name,
                                  "arguments": args if isinstance(args, dict) else {}})
        if str(d.get("role", "")).lower() == "tool" and isinstance(d.get("name"), str):
            calls.append({"name": d["name"], "arguments": {}})
    return calls


# ── extracting the repo's "truth" sets from code_files ──────────────────────

def _declared_tool_names(code_files: Dict[str, str]) -> set[str]:
    """Tool names the repo actually declares (tool-schema ``"name"`` values +
    ``*_REGISTRY`` dict keys). Over-collects on purpose — a bigger set is safer."""
    names: set[str] = set()
    for path, body in (code_files or {}).items():
        if not isinstance(body, str):
            continue
        low = path.lower()
        if "tool" in low or "schema" in low:
            names.update(re.findall(r'"name"\s*:\s*"([A-Za-z_][\w\-]*)"', body))
        for block in re.finditer(r"\b\w*REGISTRY\s*=\s*\{(.*?)\}", body, re.S):
            names.update(re.findall(r'"([A-Za-z_][\w\-]*)"\s*:', block.group(1)))
    names.discard("name")
    return names


def _seed_ids(code_files: Dict[str, str]) -> set[str]:
    """Entity ids present in the seed (SQL INSERT literals + ``*_id`` fixture
    fields). Over-collects on purpose."""
    ids: set[str] = set()
    for path, body in (code_files or {}).items():
        if not isinstance(body, str):
            continue
        low = path.lower()
        if "trace" in low:
            continue  # never let a trace self-validate its own ids
        if low.endswith(".sql"):
            for stmt in re.findall(r"insert\s+into.*?;", body, re.S | re.I):
                ids.update(re.findall(r"'([^']{1,64})'", stmt))
        elif "fixtures/" in low or low.endswith((".json", ".jsonl")):
            ids.update(re.findall(r'"\w*id"\s*:\s*"([^"]{1,64})"', body, re.I))
    return ids


# ── public entry point ──────────────────────────────────────────────────────

def check_trace_consistency(code_files: Dict[str, str]) -> Dict[str, List[str]]:
    """Cross-check shipped trace fixtures against the repo's tools + seed.

    Returns ``{"blocking": [...], "suggestions": [...]}``. Empty (no-op) when the
    task ships no trace fixture. Reads only ``code_files`` — no execution.
    """
    traces = _trace_files(code_files)
    if not traces:
        return {"blocking": [], "suggestions": []}

    tool_names = _declared_tool_names(code_files)
    seed_ids = _seed_ids(code_files)
    blocking: List[str] = []
    suggestions: List[str] = []

    for path, body in traces:
        parsed, err = _parse_trace(body)
        if err:
            blocking.append(f"trace {path}: not parseable ({err})")
            continue
        calls = _tool_calls_in(parsed)
        if tool_names:  # only when we confidently know the repo's tool set
            for call in calls:
                if call["name"] not in tool_names:
                    blocking.append(
                        f"trace {path}: tool '{call['name']}' is not declared in the "
                        f"repo's tool schemas/registry {sorted(tool_names)}"
                    )
        if seed_ids:  # advisory — seed extraction is fuzzier
            for call in calls:
                for key, val in (call.get("arguments") or {}).items():
                    if _ID_KEY_RE.search(key) and isinstance(val, str) and val not in seed_ids:
                        suggestions.append(
                            f"trace {path}: {key}='{val}' not found in seed data — "
                            f"verify it is a real seeded entity"
                        )

    def _dedupe(items: List[str]) -> List[str]:
        seen: set[str] = set()
        out: List[str] = []
        for item in items:
            if item not in seen:
                seen.add(item)
                out.append(item)
        return out

    return {"blocking": _dedupe(blocking), "suggestions": _dedupe(suggestions)}
