"""E2B v2 template: ``utkrusht-python-base`` — the lean Python substrate.

The common base of the Python template family. Carries the apt + Docker
+ Python + DB client + pytest set every member needs. No web frameworks
(those are in ``python-web``); no LLM ecosystem (those are in
``python-ai-agent``). Independent rebuilds for CVE patches; flat
rebuild graph (sibling-FROM approach per the AI-engineering plan).

Two module-level exports:

* ``template``  — the imperative :class:`AsyncTemplate` build pipeline.
* ``manifest``  — the declarative capability sheet read by the LLM
  classifier and the ``templates`` SQL table.

The manifest lists what the BASE image alone can host — members
(``python-web``, ``python-ai-agent``) compose the base's capability
sheet at their own build time. The stored ``templates`` rows are
self-contained (no ``parent_template_id`` column); the classifier reads
a fully-resolved sheet per row.

Build:
    cd infra/e2b/templates/python-base
    python build_dev.py     # -> utkrusht-python-base-dev
    python build_prod.py    # -> utkrusht-python-base   (once verified)
"""
from __future__ import annotations

from infra.e2b.templates._base.python_common import base_python_template

# The base image's capability sheet — what this template alone provides.
# Members (python-web, python-ai-agent) add to this at their own build
# time; the stored `templates` rows are self-contained capability sheets.
#
# SYNC NOTE — ``capabilities.tools`` is a CONTRACT: any pip package
# installed by ``base_python_template()`` must appear here, and
# vice versa. CI gate (template-manifest-check) catches drift.
manifest = {
    "template_id": "utkrusht-python-base",
    "status": "built",
    "primary_runtime": "python",
    "personas": [],  # base has no personas; members declare theirs
    "eval_methods": ["test_suite"],
    "capabilities": {
        "language_versions": {"python": "3.12"},
        # Frameworks that the base alone supports: NONE of the
        # web/agent frameworks. The base is intentionally lean — every
        # member layers its own.
        "frameworks": [],
        # DB clients/drivers installed. DB servers themselves come from
        # the task's docker-compose.yml (DinD lets a task bring its own
        # postgres / redis / mongo / mysql containers).
        "datastores": ["postgres", "mysql", "mongo", "redis"],
        "protocols": ["rest"],  # base only; members add websocket/etc.
        "tools": [
            "pytest",
            "pytest-asyncio",
            "docker",
            "docker-compose",
            "git",
            "jq",
            "postgresql-client",
            "default-mysql-client",
            "psycopg2-binary",
            "pymongo",
            "redis",
            "httpx",
            "requests",
            "pandas",
            "numpy",
            "ttyd",
            "code-server",
            "adminer",
        ],
        "requires": {"browser": False, "gpu": False},
        "tags": ["python-base", "family-root"],
    },
    "build_cmd": "pip install --break-system-packages -r requirements.txt",
    "test_cmd": "python -m pytest -q --tb=short",
    "compile_cmd": "python -m compileall -q .",
    "install_cmd": "apt-get install -y python3 python3-pip",
    "install_verify": "python3 --version",
    "install_seconds": 15,
    "description": (
        "Lean Python 3.12 base — apt + Docker + DB clients + pytest. "
        "No web frameworks, no LLM ecosystem. Substrate for the Python "
        "template family (python-web, python-ai-agent, ...). Each "
        "member layers its own framework set on this base via the "
        "shared ``base_python_template()`` helper."
    ),
}

template = (
    base_python_template()
    .copy("start.sh", "/usr/local/bin/start.sh")
    .run_cmd("chmod +x /usr/local/bin/start.sh")
    .set_workdir("/home/user")
    # First arg: start command. Second arg: ready-check (E2B waits for
    # it to succeed before considering the sandbox up). 20s gives
    # dockerd time.
    .set_start_cmd("sudo /usr/local/bin/start.sh", "sleep 20")
)
