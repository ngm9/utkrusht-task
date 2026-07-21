#!/usr/bin/env python3
"""Append one task-solvability run to the local task_audits CSV.

Mirrors the Supabase `task_audits` table column-for-column (audit_id, task_id,
verdict, findings, solvable, solved_by, failure_reason, trace_url, detail,
content_hash, harness, cost_usd, duration_s, created_at), with `detail`
carrying the run's FULL result.json verbatim (compact JSON). Creates the CSV
with a header when absent, appends one row per run when present.

Usage:
  python log_csv.py --result solvability_runs/<slug>/result.json \
      [--csv solvability_runs/task_audits.csv] \
      [--solved-by claude-fable-5:claude-code] [--duration-s 409.7] [--cost-usd 0]
"""

import argparse
import csv
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

COLUMNS = [
    "audit_id", "task_id", "verdict", "findings", "solvable", "solved_by",
    "failure_reason", "trace_url", "detail", "content_hash", "harness",
    "cost_usd", "duration_s", "created_at",
]


def collect_findings(res: dict) -> list[str]:
    """One human-readable string per finding, task_audits style ('field: problem')."""
    out: list[str] = []
    audit = res.get("audit") or {}
    for f in audit.get("failures") or []:
        out.append(f"{f.get('field', '?')}: {f.get('detail', '')}")
    for w in audit.get("warnings") or []:
        out.append(f"{w.get('field', '?')}: {w.get('detail', '')} (warn)")
    tour = res.get("tour") or {}
    for step in tour.get("steps") or []:
        if step.get("result") in ("warn", "fail"):
            out.append(f"tour[{step.get('label', '?')}]: {step.get('note', '')} ({step.get('result')})")
    notes = res.get("notes") or {}
    for q in notes.get("task_quality") or []:
        out.append(f"quality: {q.get('summary', '')}")
    return out


def combined_verdict(res: dict, findings: list[str]) -> str:
    """Same convention as the existing task_audits rows / task-verify matrix."""
    v = res.get("verdict")
    if v in ("unsolvable", "broken"):
        return "FAIL"
    if v == "unverified":
        return "INCONCLUSIVE"
    return "PASS_WITH_FINDINGS" if findings else "PASS"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--result", required=True, help="path to the run's result.json")
    ap.add_argument("--csv", default="solvability_runs/task_audits.csv",
                    help="CSV to create/append (default: solvability_runs/task_audits.csv)")
    ap.add_argument("--solved-by", default="claude-fable-5:claude-code",
                    help="solver identity for the solved_by column")
    ap.add_argument("--harness", default="claude-code",
                    help="harness name for the harness column")
    ap.add_argument("--duration-s", default="", help="run duration in seconds (optional)")
    ap.add_argument("--cost-usd", default="", help="run cost in USD (optional)")
    a = ap.parse_args()

    result_path = Path(a.result)
    raw = result_path.read_bytes()
    res = json.loads(raw)

    findings = collect_findings(res)
    verdict = combined_verdict(res, findings)
    solvable = res.get("verdict") == "solvable"
    failure_reason = ""
    if verdict in ("FAIL", "INCONCLUSIVE"):
        failure_reason = (res.get("summary") or {}).get("verdict_note") or res.get("verdict") or ""

    row = {
        "audit_id": str(uuid.uuid4()),
        "task_id": res.get("task_id", ""),
        "verdict": verdict,
        "findings": json.dumps(findings, ensure_ascii=False),
        "solvable": "true" if solvable else "false",
        "solved_by": a.solved_by,
        "failure_reason": failure_reason,
        "trace_url": str(result_path.parent),
        "detail": json.dumps(res, ensure_ascii=False, separators=(",", ":")),
        "content_hash": hashlib.sha256(raw).hexdigest(),
        "harness": a.harness,
        "cost_usd": a.cost_usd,
        "duration_s": a.duration_s,
        "created_at": res.get("ts") or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    csv_path = Path(a.csv)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not csv_path.exists() or csv_path.stat().st_size == 0
    with csv_path.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        if write_header:
            w.writeheader()
        w.writerow(row)

    print(f"appended {row['task_id']} verdict={verdict} findings={len(findings)} -> {csv_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
