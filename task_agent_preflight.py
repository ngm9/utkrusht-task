"""Pre-flight checks for any task-generation run.

Runs cheap checks BEFORE the expensive multi-stage pipeline kicks off, so we
fail fast on environment problems instead of discovering them 10 minutes into
a real run.

Two suites:

  - ``run_global_checks()``    once per run    — required imports + env vars
  - ``run_combo_checks(...)``  once per combo  — competency presence in
                                                  Supabase + retriever depth

Both return ``PreflightReport`` objects with explicit ``passed`` / ``issues``
lists. Callers (CLI, autonomous agent's Coordinator) inspect them and decide
whether to proceed, retry, or escalate to a human.

CLI usage:

    python task_agent_preflight.py                       # global only
    python task_agent_preflight.py --combo "Rust:BASIC"  # global + one combo
"""

from __future__ import annotations

import importlib
import os
import sys
from dataclasses import dataclass, field


# Module names that MUST import cleanly before any pipeline stage runs.
# Adding new imports here is cheap insurance; an ImportError discovered here
# costs ~1 second, vs ~10 minutes if it shows up mid-stage-4.
_REQUIRED_IMPORTS: tuple[str, ...] = (
    "openai",
    "portkey_ai",
    "paramiko",
    "github",       # PyGithub
    "supabase",
    "dotenv",
    "click",
    "dspy",
    "pydantic",
)

# Required env vars to actually run the pipeline against `dev` Supabase.
# These are checked for presence only; we don't validate the values.
_REQUIRED_ENV: tuple[str, ...] = (
    "OPENAI_API_KEY",
    "PORTKEY_API_KEY",
    "GITHUB_UTKRUSHTAPPS_TOKEN",
    "GITHUB_GIST_TOKEN",
    "REPO_OWNER",
    "SUPABASE_URL_APTITUDETESTSDEV",
    "SUPABASE_API_KEY_APTITUDETESTSDEV",
)


# ---------------------------------------------------------------------------
# Report shape
# ---------------------------------------------------------------------------


@dataclass
class PreflightReport:
    """Outcome of one preflight pass. ``warnings`` and ``info`` contain
    diagnostic findings even on success — call sites can opt into stricter
    pass criteria by inspecting them.
    """

    name: str
    passed: bool = True
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)

    def fail(self, msg: str) -> None:
        self.issues.append(msg)
        self.passed = False

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def note(self, msg: str) -> None:
        self.info.append(msg)

    def render(self) -> str:
        lines = [f"=== Preflight: {self.name} === {'PASS' if self.passed else 'FAIL'}"]
        for label, items in (("FAIL", self.issues), ("WARN", self.warnings), ("INFO", self.info)):
            for it in items:
                lines.append(f"  [{label}] {it}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Global checks
# ---------------------------------------------------------------------------


def _check_imports(report: PreflightReport) -> None:
    for mod in _REQUIRED_IMPORTS:
        try:
            importlib.import_module(mod)
        except Exception as e:  # noqa: BLE001 — we want to report any failure
            report.fail(f"import {mod!r} failed: {type(e).__name__}: {e}")


def _check_env(report: PreflightReport) -> None:
    missing = [k for k in _REQUIRED_ENV if not os.environ.get(k)]
    if missing:
        report.fail(f"Missing required env vars: {missing}")


def run_global_checks() -> PreflightReport:
    """Run all global (per-run, not per-combo) checks."""
    report = PreflightReport(name="global")
    _check_imports(report)
    _check_env(report)
    return report


# ---------------------------------------------------------------------------
# Per-combo checks
# ---------------------------------------------------------------------------


def _check_competencies_in_supabase(
    report: PreflightReport,
    competency_names: list[str],
    proficiency: str,
    env: str,
) -> None:
    """Confirm every competency name exists in Supabase at this proficiency.

    Catches typos before we burn 9 minutes generating prompts for a competency
    that doesn't actually exist (or has a different canonical name).
    """
    try:
        from supabase import create_client
    except Exception as e:
        report.fail(f"could not import supabase client: {e}")
        return
    url_key = "SUPABASE_URL_APTITUDETESTSDEV" if env == "dev" else "SUPABASE_URL_APTITUDETESTS"
    key_key = "SUPABASE_API_KEY_APTITUDETESTSDEV" if env == "dev" else "SUPABASE_API_KEY_APTITUDETESTS"
    url, key = os.environ.get(url_key), os.environ.get(key_key)
    if not url or not key:
        report.fail(f"Missing {url_key} / {key_key}; cannot probe Supabase")
        return
    sb = create_client(url, key)
    for name in competency_names:
        rows = (
            sb.table("competencies")
            .select("name")
            .eq("name", name)
            .eq("proficiency", proficiency.upper())
            .limit(1)
            .execute()
            .data
        )
        if not rows:
            report.fail(
                f"competency {name!r} at {proficiency.upper()} not found in Supabase "
                f"({env}); check spelling against the canonical list"
            )


def _check_retriever_has_references(
    report: PreflightReport,
    competency_names: list[str],
    proficiency: str,
) -> None:
    """Run the retriever for this combo and surface its reference count.

    Coordinator finding from combo 5 (PHP+Laravel): when the retriever returns
    zero references at every fallback level AND we're at INTERMEDIATE+, the
    downstream multiagent stage tends to produce hollow output. This check
    flags such combos as HIGH-RISK before we burn ~15 min generating.
    """
    try:
        from infra.classifier.classifier import Competency
        from generators.prompts.retriever import retrieve_references
    except Exception as e:
        report.fail(f"could not import retriever: {e}")
        return
    comps = [Competency(name=n, proficiency=proficiency.upper()) for n in competency_names]
    # No TaskRuntime supplied here — preflight is a diagnostic and runs before any
    # classifier call. The retriever skips Level 5 in that case (Levels 1-4 + 6 still fire).
    result = retrieve_references(comps, proficiency.upper())
    n = len(result.references)
    report.note(
        f"retriever: "
        f"bootstrap={result.bootstrap_mode} "
        f"fallback_level={result.fallback_level} "
        f"references={n}"
    )
    if n == 0:
        # HIGH-RISK signal — surfaced as a warning, not a hard fail, because
        # some combos (Rust BASIC) succeed even with 0 references because the
        # LLM has the knowledge baked in.
        report.warn(
            f"retriever returned 0 references for {competency_names} {proficiency.upper()} "
            f"— combo is full-bootstrap and may produce low-quality / hollow output. "
            f"Consider adding at least one curated sibling prompt before generating."
        )


def run_combo_checks(
    competency_names: list[str],
    proficiency: str,
    env: str = "dev",
) -> PreflightReport:
    """Run per-combo checks. Should be called AFTER ``run_global_checks`` passes."""
    label = f"combo {competency_names} {proficiency.upper()} (env={env})"
    report = PreflightReport(name=label)
    _check_competencies_in_supabase(report, competency_names, proficiency, env)
    _check_retriever_has_references(report, competency_names, proficiency)
    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_combo_arg(raw: str) -> tuple[list[str], str]:
    """Parse a CLI ``--combo`` string like ``"Python,SQL:BASIC"`` into
    ``(["Python", "SQL"], "BASIC")``.
    """
    if ":" not in raw:
        raise ValueError(
            "combo must be 'Name1,Name2:LEVEL' — got: " + raw
        )
    names_part, level = raw.rsplit(":", 1)
    names = [n.strip() for n in names_part.split(",") if n.strip()]
    return names, level.strip()


def main() -> int:
    import argparse
    p = argparse.ArgumentParser(description="Pre-flight checks for task-generation runs.")
    p.add_argument(
        "--combo", action="append", default=[],
        help='Per-combo check, e.g. --combo "Rust:BASIC" --combo "Python,Pinecone:INTERMEDIATE"',
    )
    p.add_argument("--env", default="dev", choices=("dev", "prod"))
    args = p.parse_args()

    overall_ok = True

    g = run_global_checks()
    print(g.render())
    overall_ok = overall_ok and g.passed

    for raw in args.combo:
        try:
            names, level = _parse_combo_arg(raw)
        except ValueError as e:
            print(f"\nbad --combo value: {e}", file=sys.stderr)
            overall_ok = False
            continue
        r = run_combo_checks(names, level, env=args.env)
        print("\n" + r.render())
        overall_ok = overall_ok and r.passed

    if not overall_ok:
        print("\nPreflight FAILED — fix the issues above before running the pipeline.")
        return 1
    print("\nPreflight PASS — safe to run the pipeline.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
