"""E2B v2 template definition: ``utkrusht-python`` — the fat Python runtime.

One template covering every Python lane the classifier emits (``runtime=python``
across ``kind`` = app / script / llm / vector_db): web frameworks, ORMs + DB
clients, the LLM ecosystem, and data libs are all pre-installed.

Docker-in-Docker is included so a task can bring its own ``docker-compose.yml``
for service containers (Postgres / Redis / Mongo) — the template stays
DB-agnostic; the task provides the compose file.

Browser surfaces (ttyd / code-server / adminer) are kept so the SAME template
serves both the eval gate and candidate-facing deployment (one lineage).

Supersedes the narrower ``python-sql`` template once the eval gate cuts over.

Build:
    cd e2b_flow/templates/python
    python build_dev.py     # -> utkrusht-python-dev
    python build_prod.py    # -> utkrusht-python   (once verified)
"""

from e2b import AsyncTemplate

template = (
    AsyncTemplate()
    # Lean Python base — the verified-idiomatic choice (vs python-sql's heavier
    # code-interpreter base, which ships Jupyter we don't need).
    .from_python_image("3.12")
    .set_user("root")
    .set_workdir("/")
    # Base packages + Docker apt-repo prerequisites. `netcat-openbsd` because
    # many task run.sh files use `nc -z host port` as a readiness probe;
    # postgresql-client / default-mysql-client give candidates a CLI to the
    # DB their compose file brings up.
    .run_cmd(
        "apt-get update && apt-get install -y --no-install-recommends "
        "ca-certificates curl gnupg lsb-release git jq "
        "postgresql-client default-mysql-client netcat-openbsd"
    )
    .run_cmd("install -m 0755 -d /etc/apt/keyrings")
    .run_cmd(
        "curl -fsSL https://download.docker.com/linux/debian/gpg "
        "| gpg --dearmor -o /etc/apt/keyrings/docker.gpg "
        "&& chmod a+r /etc/apt/keyrings/docker.gpg"
    )
    # Single-quoted Python string so the inner shell double quotes survive to
    # bash, where $(dpkg ...) and $(lsb_release -cs) still expand.
    .run_cmd(
        'echo "deb [arch=$(dpkg --print-architecture) '
        'signed-by=/etc/apt/keyrings/docker.gpg] '
        'https://download.docker.com/linux/debian $(lsb_release -cs) stable" '
        '> /etc/apt/sources.list.d/docker.list'
    )
    .run_cmd(
        "apt-get update && apt-get install -y --no-install-recommends "
        "docker-ce docker-ce-cli containerd.io docker-buildx-plugin "
        "docker-compose-plugin && rm -rf /var/lib/apt/lists/*"
    )
    # The fat Python lane — every framework / ORM / DB-client / LLM / data lib
    # a python task can ask for, pre-installed so the eval sandbox boots ready
    # and task run.sh files never pip-install at runtime.
    # `--break-system-packages` covers PEP 668 markers defensively.
    .run_cmd(
        "pip install --no-cache-dir --break-system-packages "
        # web frameworks + servers + HTTP clients
        "fastapi flask django 'uvicorn[standard]' gunicorn httpx requests "
        # ORMs + DB clients
        "sqlalchemy psycopg2-binary pymongo redis "
        # LLM ecosystem  (pinecone — the package was renamed from pinecone-client)
        "langchain llama-index openai anthropic pinecone chromadb "
        # data libs
        "pandas numpy "
        # test runner
        "pytest pytest-asyncio"
    )
    # Compatibility shim: existing task run.sh files call the v1 `docker-compose`
    # binary, which the v2 plugin doesn't provide. Resolve it to `docker compose`.
    .run_cmd(
        "printf '#!/bin/sh\\nexec docker compose \"$@\"\\n' "
        "> /usr/local/bin/docker-compose && "
        "chmod +x /usr/local/bin/docker-compose"
    )
    # Candidate-facing browser surfaces — one template lineage for both the
    # eval gate and candidate deployment:
    #   ttyd         -> browser terminal at https://7681-<sandbox>.e2b.app
    #   code-server  -> browser VS Code at  https://8443-<sandbox>.e2b.app
    # Versions pinned (not :latest) so a rebuild is reproducible.
    .run_cmd(
        "curl -fsSL -o /usr/local/bin/ttyd "
        "https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.x86_64 "
        "&& chmod +x /usr/local/bin/ttyd "
        "&& curl -fsSL -o /tmp/code-server.deb "
        "https://github.com/coder/code-server/releases/download/v4.96.4/code-server_4.96.4_amd64.deb "
        "&& dpkg -i /tmp/code-server.deb "
        "&& rm /tmp/code-server.deb"
    )
    # Adminer — single-file PHP web DB GUI on :8080. php-pgsql + php-mysql
    # cover the drivers it needs for the DB stacks python tasks host.
    .run_cmd(
        "apt-get update && apt-get install -y --no-install-recommends "
        "php-cli php-pgsql php-mysql "
        "&& mkdir -p /opt/adminer "
        "&& curl -fsSL -o /opt/adminer/index.php "
        "https://github.com/vrana/adminer/releases/download/v4.8.1/adminer-4.8.1.php "
        "&& rm -rf /var/lib/apt/lists/*"
    )
    .copy("start.sh", "/usr/local/bin/start.sh")
    .run_cmd("chmod +x /usr/local/bin/start.sh")
    .set_workdir("/home/user")
    # First arg: start command. Second arg: ready-check (E2B waits for it to
    # succeed before considering the sandbox up). 20s gives dockerd time.
    .set_start_cmd("sudo /usr/local/bin/start.sh", "sleep 20")
)
