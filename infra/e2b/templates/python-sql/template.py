"""E2B v2 template definition: Python + SQL (Postgres-via-Compose).

Built via ``python build_dev.py`` (or ``build_prod.py``) from this directory.
The generated ``template.py`` from ``e2b template migrate`` is rewritten
here as one ``run_cmd`` per logical step — both for readability and to
sidestep a Python-level quoting bug in the migration output (the
``echo "deb [...]"`` apt-source line had unescaped double quotes).
"""

from e2b import AsyncTemplate

template = (
    AsyncTemplate()
    .from_image("e2bdev/code-interpreter:latest")
    .set_user("root")
    .set_workdir("/")
    # Base packages + Docker apt repo prerequisites.
    # `netcat-openbsd` is included because many task `run.sh` files use
    # `nc -z host port` as a service-readiness probe.
    .run_cmd(
        "apt-get update && apt-get install -y --no-install-recommends "
        "ca-certificates curl gnupg lsb-release git jq postgresql-client "
        "netcat-openbsd"
    )
    .run_cmd("install -m 0755 -d /etc/apt/keyrings")
    .run_cmd(
        "curl -fsSL https://download.docker.com/linux/debian/gpg "
        "| gpg --dearmor -o /etc/apt/keyrings/docker.gpg "
        "&& chmod a+r /etc/apt/keyrings/docker.gpg"
    )
    # Single-quoted Python string so the inner shell double quotes survive
    # to bash, where $(dpkg ...) and $(lsb_release -cs) still expand.
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
    # The e2b code-interpreter base image ships Python 3.13 with a working
    # pip. The PoC's task is authored against 3.13-compatible package
    # versions, so we use the base interpreter directly. `--break-system-
    # packages` covers PEP 668 markers if the base image ever flips on the
    # externally-managed flag in a future revision.
    .run_cmd(
        "pip install --no-cache-dir --break-system-packages "
        "psycopg2-binary sqlalchemy pandas"
    )
    # Compatibility shim: existing task `run.sh` files call `docker-compose`
    # (v1 binary name) which the v2 plugin doesn't provide. This wrapper
    # makes `docker-compose ...` resolve to `docker compose ...` so we
    # don't have to rewrite task content.
    .run_cmd(
        "printf '#!/bin/sh\\nexec docker compose \"$@\"\\n' "
        "> /usr/local/bin/docker-compose && "
        "chmod +x /usr/local/bin/docker-compose"
    )
    # Candidate-facing surfaces:
    #   ttyd         → browser terminal at https://7681-<sandbox>.e2b.app
    #   code-server  → browser VS Code at  https://8443-<sandbox>.e2b.app
    # Both run unauthenticated for the PoC — the URL is only reachable via
    # the sandbox's signed E2B host, so this is "obscurity at the platform
    # edge" rather than real auth. Production candidate flow must front-
    # end these with a per-session token (Phase 3 of the research doc).
    #
    # Versions are pinned (not :latest) so a template rebuild is
    # reproducible and supply-chain-auditable. Bump deliberately.
    .run_cmd(
        "curl -fsSL -o /usr/local/bin/ttyd "
        "https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.x86_64 "
        "&& chmod +x /usr/local/bin/ttyd "
        "&& curl -fsSL -o /tmp/code-server.deb "
        "https://github.com/coder/code-server/releases/download/v4.96.4/code-server_4.96.4_amd64.deb "
        "&& dpkg -i /tmp/code-server.deb "
        "&& rm /tmp/code-server.deb"
    )
    # Adminer — web DB GUI on :8080. Single-file PHP app served by
    # PHP's built-in CLI server. This is the SQL-stack analog of
    # ttyd: candidates can browse tables / run queries / view EXPLAINs
    # in a browser without local psql. Required because E2B's port
    # forwarder is HTTPS-only — see deployment-infrastructure.md §12.
    # `php-pgsql` + `php-mysql` cover the drivers Adminer needs for
    # the DB stacks this template will host.
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
    # First arg: start command. Second arg: ready-check (E2B waits for it
    # to succeed before considering the sandbox up). 20s gives dockerd
    # time to come online.
    .set_start_cmd("sudo /usr/local/bin/start.sh", "sleep 20")
)
