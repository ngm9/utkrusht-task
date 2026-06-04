"""Shared E2B template chain — the Python ``python-base`` substrate.

The Python template family is split by framework family (per
``docs/plans/2026-05-27-ai-engineering-task-category.html`` §"The
sandbox: the python-ai-agent template" + ``docs/task-classifier/
classifier.md`` §"Template inheritance is a build-time concern"):

    python-base       # this module — apt + Docker + Python + DB clients + pytest
      ├─ python-web         # + fastapi/flask/django/sqlalchemy/uvicorn/gunicorn
      └─ python-ai-agent    # + langgraph/crewai/mem0/langfuse + LiteLLM/tiktoken

E2B v2's ``AsyncTemplate`` has no first-class inheritance primitive (a
sibling-from-base layer mechanism) — every template is built from a
public base image. The doc's "sibling FROM common base" recommendation
is realised at the Python level: each member's ``template.py`` imports
``base_python_template()`` and chains its own ``.run_cmd(...)`` calls
on top. Each member's image is independently rebuildable for CVE
patches; the shared code is what makes the three stay in sync.

Adding a new member (e.g. ``python-data``) means importing this helper
and chaining pandas/polars/numpy on top. No shared Docker layer
cascades; no ``from_template()`` rebuild graph coupling.
"""
from __future__ import annotations

from e2b import AsyncTemplate


# The common bash setup every Python member of the family carries.
# Apt + Docker + Python + the DB clients + pytest + the compatibility
# shims + the browser surfaces. Per the doc, agent frameworks are NOT
# in the base — they live in ``python-ai-agent``; web frameworks are
# NOT in the base — they live in ``python-web``. The base is the lean
# common substrate.
_BASE_RUN_CMDS: tuple[str, ...] = (
    # Base packages + Docker apt-repo prerequisites. ``netcat-openbsd``
    # is here because many task run.sh files use ``nc -z host port`` as
    # a readiness probe; ``postgresql-client`` / ``default-mysql-client``
    # give candidates a CLI to the DB their compose file brings up.
    "apt-get update && apt-get install -y --no-install-recommends "
    "ca-certificates curl gnupg lsb-release git jq "
    "postgresql-client default-mysql-client netcat-openbsd",
    "install -m 0755 -d /etc/apt/keyrings",
    "curl -fsSL https://download.docker.com/linux/debian/gpg "
    "| gpg --dearmor -o /etc/apt/keyrings/docker.gpg "
    "&& chmod a+r /etc/apt/keyrings/docker.gpg",
    # Single-quoted Python string so the inner shell double quotes survive
    # to bash, where $(dpkg ...) and $(lsb_release -cs) still expand.
    'echo "deb [arch=$(dpkg --print-architecture) '
    'signed-by=/etc/apt/keyrings/docker.gpg] '
    'https://download.docker.com/linux/debian $(lsb_release -cs) stable" '
    '> /etc/apt/sources.list.d/docker.list',
    "apt-get update && apt-get install -y --no-install-recommends "
    "docker-ce docker-ce-cli containerd.io docker-buildx-plugin "
    "docker-compose-plugin && rm -rf /var/lib/apt/lists/*",
    # The common Python lane: ORM/DB clients, data libs, test runner. NOT
    # the LLM ecosystem (those are LLM-stack dependents in python-ai-agent)
    # and NOT the web frameworks (those are in python-web).
    # ``--break-system-packages`` covers PEP 668 markers defensively.
    "pip install --no-cache-dir --break-system-packages "
    # ORMs + DB clients
    "sqlalchemy psycopg2-binary pymongo redis "
    # data libs (light — pandas/numpy only; ML stack stays in -ai-agent)
    "pandas numpy "
    # test runner
    "pytest pytest-asyncio "
    # HTTP client (needed by every member; lightweight + ubiquitous)
    "httpx requests",
    # Compatibility shim: existing task run.sh files call the v1
    # ``docker-compose`` binary, which the v2 plugin doesn't provide.
    'printf \'#!/bin/sh\\nexec docker compose "$@"\\n\' '
    "> /usr/local/bin/docker-compose && "
    "chmod +x /usr/local/bin/docker-compose",
    # Candidate-facing browser surfaces — one template lineage for both
    # the eval gate and candidate deployment:
    #   ttyd         -> browser terminal at https://7681-<sandbox>.e2b.app
    #   code-server  -> browser VS Code at  https://8443-<sandbox>.e2b.app
    # Versions pinned (not :latest) so a rebuild is reproducible.
    "curl -fsSL -o /usr/local/bin/ttyd "
    "https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.x86_64 "
    "&& chmod +x /usr/local/bin/ttyd "
    "&& curl -fsSL -o /tmp/code-server.deb "
    "https://github.com/coder/code-server/releases/download/v4.96.4/code-server_4.96.4_amd64.deb "
    "&& dpkg -i /tmp/code-server.deb "
    "&& rm /tmp/code-server.deb",
    # Adminer — single-file PHP web DB GUI on :8080. php-pgsql + php-mysql
    # cover the drivers it needs for the DB stacks python tasks host.
    "apt-get update && apt-get install -y --no-install-recommends "
    "php-cli php-pgsql php-mysql "
    "&& mkdir -p /opt/adminer "
    "&& curl -fsSL -o /opt/adminer/index.php "
    "https://github.com/vrana/adminer/releases/download/v4.8.1/adminer-4.8.1.php "
    "&& rm -rf /var/lib/apt/lists/*",
)


def base_python_template() -> AsyncTemplate:
    """Return the shared Python base — lean Python 3.12 + Docker + DB clients.

    Members of the family chain on top:

        from infra.e2b.templates._base.python_common import base_python_template
        template = (
            base_python_template()
            .run_cmd("pip install ... fastapi flask django ...")
            ...
        )

    The returned ``AsyncTemplate`` is in its canonical state (lean base,
    ``set_user("root")``/``set_workdir("/")``) — the caller can keep
    chaining ``.run_cmd(...)`` calls without re-doing the base setup.
    """
    tmpl = (
        AsyncTemplate()
        .from_python_image("3.12")
        .set_user("root")
        .set_workdir("/")
    )
    for cmd in _BASE_RUN_CMDS:
        tmpl = tmpl.run_cmd(cmd)
    return tmpl
