"""Human-facing CLI for the template remediation queue.

Usage:
    .venv/bin/python scripts/template_remediation_cli.py list
    .venv/bin/python scripts/template_remediation_cli.py show <slug>
    .venv/bin/python scripts/template_remediation_cli.py approve <slug>

A thin wrapper, not a copy: it only loads .env before importing anything, then
delegates straight to flows.tech.stages.generate.template_remediation._cli().

Why this file exists instead of `python -m flows.tech.stages.generate.template_remediation`:
that package's __init__.py eagerly imports creator.py, which eagerly
instantiates an OpenAI client at import time — before .env would be loaded by
the submodule itself. Loading .env here, first, sidesteps that without
touching the shared eager-init behavior other stages rely on.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv()

from flows.tech.stages.generate.template_remediation import _cli

if __name__ == "__main__":
    sys.exit(_cli())
