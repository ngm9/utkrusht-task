"""Deterministic trace-fixture consistency check (``generators.task.trace_check``).

Pure stdlib module, so these import without the generation stack.
"""
from __future__ import annotations

import json

from generators.task.trace_check import check_trace_consistency


# A realistic agent repo: two declared tools, a seed, and a telemetry-shaped trace.
TOOL_SCHEMAS = (
    'GET_SENSOR_STATUS = {"type": "function", "function": {"name": '
    '"get_sensor_status", "parameters": {"properties": {"device_id": {}}}}}\n'
    'GET_GATEWAY_STATUS = {"type": "function", "function": {"name": '
    '"get_gateway_status", "parameters": {"properties": {"gateway_id": {}}}}}\n'
)
TOOLS = (
    'TOOL_REGISTRY = {\n'
    '    "get_sensor_status": get_sensor_status,\n'
    '    "get_gateway_status": get_gateway_status,\n'
    '}\n'
)
SEED = "INSERT INTO devices (device_id, gateway_id) VALUES ('dev-200', 'gw-002');\n"

GOOD_TRACE = {
    "device_id": "dev-200",
    "steps": [
        {"role": "assistant", "tool_calls": [
            {"name": "get_sensor_status", "arguments": {"device_id": "dev-200"}},
            {"name": "get_gateway_status", "arguments": {"gateway_id": "gw-002"}}]},
        {"role": "tool", "name": "get_sensor_status", "content": {"available": True}},
        {"role": "tool", "name": "get_gateway_status", "content": {"status": "offline"}},
        {"role": "assistant_observed_output", "content": "operating normally"},
    ],
}


def _repo(trace, *, schemas=TOOL_SCHEMAS, tools=TOOLS, seed=SEED, trace_name="fixtures/sample_trace.json"):
    files = {
        "agent/tool_schemas.py": schemas,
        "agent/tools.py": tools,
        "init_database.sql": seed,
        trace_name: trace if isinstance(trace, str) else json.dumps(trace),
    }
    return {k: v for k, v in files.items() if v is not None}


def test_no_trace_file_is_noop():
    files = {"agent/tool_schemas.py": TOOL_SCHEMAS, "init_database.sql": SEED}
    assert check_trace_consistency(files) == {"blocking": [], "suggestions": []}


def test_good_trace_is_clean():
    res = check_trace_consistency(_repo(GOOD_TRACE))
    assert res["blocking"] == []
    assert res["suggestions"] == []


def test_unknown_tool_name_blocks():
    bad = {"steps": [
        {"role": "assistant", "tool_calls": [{"name": "fetch_gateway", "arguments": {}}]},
        {"role": "tool", "name": "fetch_gateway", "content": {}}]}
    res = check_trace_consistency(_repo(bad))
    assert any("fetch_gateway" in b for b in res["blocking"])
    # name appears twice in the trace (tool_call + tool step) but is de-duped
    assert sum("fetch_gateway" in b for b in res["blocking"]) == 1


def test_unknown_entity_id_is_advisory_only():
    bad = {"steps": [{"role": "assistant", "tool_calls": [
        {"name": "get_gateway_status", "arguments": {"gateway_id": "gw-999"}}]}]}
    res = check_trace_consistency(_repo(bad))
    assert res["blocking"] == []                       # tool is valid
    assert any("gw-999" in s for s in res["suggestions"])


def test_malformed_json_blocks():
    res = check_trace_consistency(_repo("{ not valid json"))
    assert any("not parseable" in b for b in res["blocking"])


def test_valid_jsonl_trace_is_clean():
    lines = "\n".join(json.dumps(s) for s in GOOD_TRACE["steps"])
    res = check_trace_consistency(_repo(lines, trace_name="fixtures/run.trace.jsonl"))
    assert res["blocking"] == []


def test_broken_jsonl_line_blocks():
    lines = json.dumps(GOOD_TRACE["steps"][0]) + "\n{ broken\n"
    res = check_trace_consistency(_repo(lines, trace_name="fixtures/run.trace.jsonl"))
    assert any("line 2" in b for b in res["blocking"])


def test_tool_check_skipped_when_no_tool_set():
    # A trace ships, but the repo declares no tools we can extract -> never flag
    # tool names (avoids false positives), and with no seed, no suggestions.
    bad = {"steps": [{"role": "assistant", "tool_calls": [{"name": "totally_made_up", "arguments": {}}]}]}
    files = {"fixtures/sample_trace.json": json.dumps(bad)}
    assert check_trace_consistency(files) == {"blocking": [], "suggestions": []}


def test_openai_nested_function_tool_calls():
    bad = {"steps": [{"role": "assistant", "tool_calls": [
        {"id": "1", "type": "function", "function": {"name": "ghost_tool", "arguments": "{}"}}]}]}
    res = check_trace_consistency(_repo(bad))
    assert any("ghost_tool" in b for b in res["blocking"])
