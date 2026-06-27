"""E2B v2 template definition: Rust + SQL (Postgres-via-Compose).

The first member of a Rust template family. Carries the apt + Docker
+ Rust toolchain + DB client + candidate-surface set a Rust assessment
task needs. The structural analog of ``python-sql``: a standalone build
chain (no shared ``_base`` helper yet — there is only one Rust template
today; a helper is the right refactor when a second member appears).

Built via ``python build_dev.py`` (or ``build_prod.py``) from this
directory.

Two module-level exports:

* ``template``  — the imperative :class:`AsyncTemplate` build pipeline.
* ``manifest``  — the declarative capability sheet read by the LLM
  classifier and the ``templates`` SQL table.

The image is the official ``rust:1-bookworm`` (Debian 12, based on
``buildpack-deps`` — ships cargo/rustc/rustfmt/clippy + build-essential
+ libssl-dev + pkg-config). Docker-in-Docker is layered on for tasks
whose ``run.sh`` does ``docker compose up`` (e.g. a ``postgres:16``
service); the candidate browser surfaces (ttyd / code-server / adminer)
mirror the Python lineage so one template serves both the eval gate and
candidate deployment.

The manifest is intentionally hand-aligned with what ``template``
installs — keep them in sync.

Build:
    cd infra/e2b/templates/rust-base
    python build_dev.py     # -> utkrusht-rust-dev
    python build_prod.py    # -> utkrusht-rust   (once verified)
"""
from __future__ import annotations

from e2b import AsyncTemplate

# Capability sheet — the "menu" of what this template offers.
#
# SYNC NOTE — Two categories have DIFFERENT semantics:
#   capabilities.tools: packages PRE-INSTALLED in the image. Adding an apt
#     package to the run_cmd chain below requires a matching addition here,
#     and vice versa. The presence in this list is a contract.
#   capabilities.frameworks / datastores / protocols: the UNIVERSE the LLM
#     classifier may match against — NOT all pre-installed. Rust crates are
#     fetched + compiled per-project by ``cargo build``; DB servers are stood
#     up at task boot by the task's own run.sh + docker-compose. No run_cmd
#     change is required for these.
#
# install_cmd / install_verify / install_seconds describe how to install
# THIS template's primary runtime as a SECONDARY in another sandbox (the
# polyglot install-at-boot mechanism). They do NOT describe what THIS
# template's build pipeline does — that's the run_cmd chain below.
manifest = {
    "template_id": "utkrusht-rust",
    "status": "built",
    "primary_runtime": "rust",
    "personas": ["backend"],
    "eval_methods": ["test_suite"],
    "capabilities": {
        # rust:1-bookworm tracks the latest stable 1.x at image build time
        # (1.96 as of this build). The major-pin "1" keeps the manifest
        # stable across patch bumps on rebuild.
        "language_versions": {"rust": "1.96"},
        # Crate ecosystems the classifier may match — fetched per-project by
        # cargo, NOT pre-installed.
        "frameworks": ["tokio", "sqlx", "serde", "axum", "actix-web", "diesel"],
        # DB clients/drivers reachable from the sandbox. DB servers themselves
        # come from the task's docker-compose.yml (DinD lets a task bring its
        # own postgres / mysql / redis containers).
        "datastores": ["postgres", "mysql", "redis"],
        "protocols": ["rest", "websocket"],
        "tools": [
            "cargo",
            "rustc",
            "rustfmt",
            "clippy",
            "docker",
            "docker-compose",
            "git",
            "jq",
            "postgresql-client",
            "netcat-openbsd",
            "ttyd",
            "code-server",
            "adminer",
        ],
        "requires": {"browser": False, "gpu": False},
        "tags": ["rust-base", "family-root"],
    },
    "build_cmd": "cargo build",
    "test_cmd": "cargo test",
    "compile_cmd": "cargo build",
    # Secondary-install recipe (rustup) for the polyglot install-at-boot path.
    "install_cmd": (
        "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs "
        "| sh -s -- -y --default-toolchain stable"
    ),
    "install_verify": "cargo --version",
    "install_seconds": 90,
    "description": (
        "Rust (stable, Debian bookworm) base. Pre-installed: cargo, rustc, "
        "rustfmt, clippy, build-essential, libssl-dev, pkg-config, "
        "postgresql-client. DinD via docker-ce for tasks that bring a "
        "docker-compose datastore. Browser tools: ttyd, code-server, adminer."
    ),
}

template = (
    AsyncTemplate()
    # Official Rust image: Debian 12 (bookworm) with cargo/rustc/rustfmt/
    # clippy + build-essential + libssl-dev + pkg-config already present.
    .from_image("rust:1-bookworm")
    .set_user("root")
    .set_workdir("/")
    # The rust image installs the toolchain under /usr/local/{cargo,rustup}
    # and exposes it via the image's Docker ``ENV PATH`` — but E2B's
    # ``commands.run`` inherits NEITHER the image ENV nor the template's
    # ``set_envs`` (verified: PATH stays the envd default and RUSTUP_HOME is
    # unset, so ``cargo``→``rustup`` proxies are off-PATH AND can't locate the
    # installed toolchain). ``set_envs`` is kept for the start command + any
    # login shell, but the GUARANTEE comes from the wrapper scripts below.
    .set_envs(
        {
            "RUSTUP_HOME": "/usr/local/rustup",
            "CARGO_HOME": "/usr/local/cargo",
            "PATH": (
                "/usr/local/cargo/bin:/usr/local/sbin:/usr/local/bin:"
                "/usr/sbin:/usr/bin:/sbin:/bin"
            ),
        }
    )
    # Bulletproof toolchain exposure: for every rustup proxy in
    # /usr/local/cargo/bin, drop a self-contained wrapper in /usr/local/bin
    # (which IS on the envd default PATH) that exports the two HOME vars and
    # exec's the proxy. This makes ``cargo``/``rustc``/``rustfmt``/``clippy``
    # resolve for run.sh, the eval gate, and the candidate's browser shell
    # without anyone having to pass per-command ``envs=``.
    .run_cmd(
        r'''for f in /usr/local/cargo/bin/*; do n=$(basename "$f"); '''
        r'''printf '#!/bin/sh\nexport RUSTUP_HOME=/usr/local/rustup '''
        r'''CARGO_HOME=/usr/local/cargo\nexec /usr/local/cargo/bin/%s "$@"\n' '''
        r'''"$n" > /usr/local/bin/"$n"; chmod +x /usr/local/bin/"$n"; done'''
    )
    # Base packages + Docker apt repo prerequisites. `buildpack-deps` already
    # carries curl/git/gnupg/ca-certificates; we add what's missing.
    # `netcat-openbsd` is included because many task `run.sh` files use
    # `nc -z host port` as a service-readiness probe; `postgresql-client`
    # gives candidates a `psql` CLI to the DB their compose file brings up.
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
    # Compatibility shim: existing task `run.sh` files call `docker-compose`
    # (v1 binary name) which the v2 plugin doesn't provide. This wrapper
    # makes `docker-compose ...` resolve to `docker compose ...` so we don't
    # have to rewrite task content.
    .run_cmd(
        "printf '#!/bin/sh\\nexec docker compose \"$@\"\\n' "
        "> /usr/local/bin/docker-compose && "
        "chmod +x /usr/local/bin/docker-compose"
    )
    # Candidate-facing surfaces:
    #   ttyd         -> browser terminal at https://7681-<sandbox>.e2b.app
    #   code-server  -> browser VS Code at  https://8443-<sandbox>.e2b.app
    # Versions pinned (not :latest) so a template rebuild is reproducible.
    .run_cmd(
        "curl -fsSL -o /usr/local/bin/ttyd "
        "https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.x86_64 "
        "&& chmod +x /usr/local/bin/ttyd "
        "&& curl -fsSL -o /tmp/code-server.deb "
        "https://github.com/coder/code-server/releases/download/v4.96.4/code-server_4.96.4_amd64.deb "
        "&& dpkg -i /tmp/code-server.deb "
        "&& rm /tmp/code-server.deb"
    )
    # Adminer — web DB GUI on :8080. Single-file PHP app served by PHP's
    # built-in CLI server. `php-pgsql` + `php-mysql` cover the drivers it
    # needs for the DB stacks this template will host.
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
    # succeed before considering the sandbox up). 20s gives dockerd time to
    # come online.
    .set_start_cmd("sudo /usr/local/bin/start.sh", "sleep 20")
)
