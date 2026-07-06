"""E2B v2 template definition: ``utkrusht-dotnet-base`` — the .NET 8 runtime.

One template covering every .NET lane the classifier emits (``runtime=dotnet_base``
across ``kind`` = app / api / worker / console): the full .NET 8 SDK, xUnit test
framework, ASP.NET Core, and Entity Framework Core are all pre-installed.

Docker-in-Docker is included so a task can bring its own ``docker-compose.yml``
for service containers (SQL Server / PostgreSQL / Redis / MySQL) — the template
stays DB-agnostic; the task provides the compose file.

Browser surfaces (ttyd / code-server) are kept so the SAME template serves both
the eval gate and candidate-facing deployment (one lineage).

Two module-level exports:

* ``template``  — the imperative :class:`AsyncTemplate` build pipeline.
* ``manifest``  — the declarative capability sheet read by the LLM classifier
  and the ``templates`` SQL table. Phase 0 of
  ``docs/plans/2026-05-27-unified-classifier-template-schema.md``.

The manifest is intentionally hand-aligned with what ``template`` installs —
keep them in sync.

Build:
    cd infra/e2b/templates/dotnet-base
    python build_dev.py     # -> utkrusht-dotnet-base-dev
    python build_prod.py    # -> utkrusht-dotnet-base   (once verified)
"""

from e2b import AsyncTemplate

# Capability sheet — the "menu" of what this template offers.
#
# SYNC NOTE — Two categories have DIFFERENT semantics:
#   capabilities.tools: packages PRE-INSTALLED in the image. Adding a dotnet
#     global tool or apt package to the run_cmd chain (below) requires a
#     matching addition here, and vice versa. The presence in this list is a
#     contract.
#   capabilities.frameworks / datastores / protocols: the UNIVERSE the LLM
#     classifier may match against — NOT all pre-installed; ASP.NET Core and
#     EF Core ARE pre-installed (as NuGet packages via dotnet tool restore /
#     project templates) but DB servers (sqlserver, postgres, mysql, redis)
#     come from the task's own docker-compose.yml, not the template.
#
# Nothing in CI enforces this alignment today (CI gate is deferred — see
# docs/plans/2026-05-27-unified-classifier-template-schema.md §Phase 0).
# Drift between this dict and the run_cmd chain is currently honor-system.
#
# install_cmd / install_verify / install_seconds describe how to install THIS
# template's primary runtime as a SECONDARY in another sandbox (the polyglot
# install-at-boot mechanism from e2b-templates.md#polyglot). They do NOT
# describe what THIS template's build pipeline does — that's the run_cmd
# chain below.
manifest = {
    "template_id": "utkrusht-dotnet-base",
    "status": "built",
    "primary_runtime": "dotnet_base",
    "personas": ["backend_engineer"],
    "eval_methods": ["test_suite"],
    "capabilities": {
        "language_versions": {"dotnet": "8"},
        "frameworks": [
            "aspnetcore",
            "entityframework",
            "xunit",
            "nunit",
            "mstest",
            "minimal-api",
        ],
        "datastores": ["sqlserver", "postgres", "mysql", "redis", "sqlite"],
        "protocols": ["rest", "websocket", "grpc"],
        "tools": [
            "dotnet-sdk",
            "dotnet-ef",
            "dotnet-aspnet-codegenerator",
            "nuget",
            "docker",
            "docker-compose",
            "git",
            "jq",
            "curl",
            "ca-certificates",
            "netcat-openbsd",
        ],
        "requires": {"browser": False, "gpu": False},
        "tags": ["dotnet", "csharp", "aspnetcore", "xunit"],
    },
    "build_cmd": "dotnet build --configuration Release",
    "test_cmd": "dotnet test --configuration Release --no-build --logger trx",
    "compile_cmd": "dotnet build --configuration Release --no-restore",
    "install_cmd": (
        "apt-get install -y dotnet-sdk-8.0 || "
        "curl -fsSL https://dot.net/v1/dotnet-install.sh | bash -s -- --channel 8.0"
    ),
    "install_verify": "dotnet --version",
    "install_seconds": 45,
    "description": (
        ".NET 8 SDK base. Pre-installed: ASP.NET Core, Entity Framework Core, "
        "xUnit, NUnit, MSTest, dotnet-ef global tool. Browser tools: ttyd, "
        "code-server. DinD via docker-ce."
    ),
}

template = (
    AsyncTemplate()
    # Official Microsoft .NET 8 SDK image — Debian-based, gives us apt and the
    # full SDK (compiler, runtime, NuGet, dotnet CLI) out of the box.
    .from_image("mcr.microsoft.com/dotnet/sdk:8.0")
    .set_user("root")
    .set_workdir("/")
    # Base packages + Docker apt-repo prerequisites. `netcat-openbsd` because
    # many task run.sh files use `nc -z host port` as a readiness probe.
    .run_cmd(
        "apt-get update && apt-get install -y --no-install-recommends "
        "ca-certificates curl gnupg lsb-release git jq netcat-openbsd"
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
    # Install dotnet-ef (Entity Framework Core CLI tool) and
    # dotnet-aspnet-codegenerator globally — both are referenced by many
    # ASP.NET Core task scaffolds. Pinned to the .NET 8 compatible versions.
    # `--tool-path` is avoided in favour of `dotnet tool install -g` so the
    # tools appear on PATH automatically via ~/.dotnet/tools (already on PATH
    # in the SDK image).
    # Use --tool-path (not --global) so the install has an explicit target and
    # does not depend on $HOME being set in the E2B build environment.
    # Symlink into /usr/local/bin so both tools are on PATH for all users.
    .run_cmd(
        "mkdir -p /usr/local/dotnet-tools "
        "&& dotnet tool install --tool-path /usr/local/dotnet-tools dotnet-ef "
        "&& ln -sf /usr/local/dotnet-tools/dotnet-ef /usr/local/bin/dotnet-ef"
    )
    .run_cmd(
        "dotnet tool install --tool-path /usr/local/dotnet-tools dotnet-aspnet-codegenerator "
        "&& ln -sf /usr/local/dotnet-tools/dotnet-aspnet-codegenerator /usr/local/bin/dotnet-aspnet-codegenerator "
        "|| echo 'dotnet-aspnet-codegenerator install skipped (non-fatal)'"
    )
    # Warm the NuGet package cache with the most common packages so task
    # `dotnet restore` steps complete quickly (no network round-trips for
    # these). We create a throwaway console project, add the packages, then
    # delete the project — the packages land in /root/.nuget/packages.
    .run_cmd(
        "mkdir -p /tmp/nuget-warmup && cd /tmp/nuget-warmup "
        "&& dotnet new console -n warmup --no-restore "
        "&& cd warmup "
        "&& dotnet add package Microsoft.AspNetCore.App "
        "   --version 8.0.* 2>/dev/null || true "
        "&& dotnet add package Microsoft.EntityFrameworkCore "
        "   --version 8.0.* "
        "&& dotnet add package Microsoft.EntityFrameworkCore.SqlServer "
        "   --version 8.0.* "
        "&& dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL "
        "   --version 8.0.* "
        "&& dotnet add package Pomelo.EntityFrameworkCore.MySql "
        "   --version 8.0.* "
        "&& dotnet add package StackExchange.Redis "
        "   --version 2.7.* "
        "&& dotnet add package xunit "
        "&& dotnet add package xunit.runner.visualstudio "
        "&& dotnet add package NUnit "
        "&& dotnet add package MSTest.TestFramework "
        "&& dotnet add package Swashbuckle.AspNetCore "
        "&& dotnet restore "
        "&& cd / && rm -rf /tmp/nuget-warmup"
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
    .copy("start.sh", "/usr/local/bin/start.sh")
    .run_cmd("chmod +x /usr/local/bin/start.sh")
    .set_workdir("/home/user")
    # First arg: start command. Second arg: ready-check (E2B waits for it to
    # succeed before considering the sandbox up). 5s is sufficient for .NET —
    # there is no long-lived daemon to wait for beyond dockerd (which start.sh
    # handles internally).
    .set_start_cmd("/usr/local/bin/start.sh", "sleep 5")
)