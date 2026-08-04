"""E2B v2 template: ``utkrusht-node-base`` — Node.js 20 LTS substrate.

Pre-installs Node.js 20, npm, TypeScript, NestJS CLI, Jest, ts-jest, and
the candidate-facing browser surfaces (ttyd, code-server). No dockerd —
node-base tasks are pure in-process (non_infra shape); docker-compose is
not needed.

Build:
    cd infra/e2b/templates/node-base
    python build_dev.py     # -> utkrusht-node-base-dev
    python build_prod.py    # -> utkrusht-node-base   (once verified)
"""
from __future__ import annotations

from e2b import AsyncTemplate

manifest = {
    "template_id": "utkrusht-node-base",
    "status": "built",
    "primary_runtime": "node",
    "personas": ["backend_engineer"],
    "eval_methods": ["test_suite"],
    "capabilities": {
        "language_versions": {"node": "20"},
        "frameworks": ["nestjs", "express", "fastify"],
        "datastores": [],
        "protocols": ["rest"],
        "tools": [
            "npm",
            "typescript",
            "ts-node",
            "ts-jest",
            "jest",
            "@nestjs/cli",
            "@nestjs/testing",
            "supertest",
            "git",
            "ttyd",
            "code-server",
        ],
        "requires": {"browser": False, "gpu": False},
        "tags": ["node", "nestjs", "typescript"],
    },
    "build_cmd": "npm install",
    "test_cmd": "npm test",
    "compile_cmd": "npx tsc --noEmit",
    "install_cmd": "apt-get install -y nodejs npm",
    "install_verify": "node --version",
    "install_seconds": 10,
    "description": (
        "Node.js 20 LTS. Pre-installed: TypeScript, ts-node, ts-jest, Jest, "
        "@nestjs/cli, @nestjs/testing, supertest. Browser tools: ttyd, "
        "code-server. Pure in-process — no Docker, no docker-compose."
    ),
}

template = (
    AsyncTemplate()
    .from_node_image("20")
    .set_user("root")
    .set_workdir("/")
    .run_cmd(
        "apt-get update && apt-get install -y --no-install-recommends "
        "git curl ca-certificates && rm -rf /var/lib/apt/lists/*"
    )
    # Global npm packages every Node task needs pre-installed so npm install
    # inside the task only installs task-specific deps (faster gate).
    .run_cmd(
        "npm install -g "
        "typescript ts-node ts-jest jest "
        "@nestjs/cli @types/node @types/jest "
        "supertest @types/supertest"
    )
    # Browser terminal on :7681
    .run_cmd(
        "curl -fsSL -o /usr/local/bin/ttyd "
        "https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.x86_64 "
        "&& chmod +x /usr/local/bin/ttyd"
    )
    # Browser VS Code on :8443
    .run_cmd(
        "curl -fsSL -o /tmp/code-server.deb "
        "https://github.com/coder/code-server/releases/download/v4.96.4/"
        "code-server_4.96.4_amd64.deb "
        "&& dpkg -i /tmp/code-server.deb "
        "&& rm /tmp/code-server.deb"
    )
    .copy("start.sh", "/usr/local/bin/start.sh")
    .run_cmd("chmod +x /usr/local/bin/start.sh")
    .set_workdir("/home/user")
    .set_start_cmd("sudo /usr/local/bin/start.sh", "sleep 5")
)
