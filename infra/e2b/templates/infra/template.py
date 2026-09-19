"""E2B v2 template: ``utkrusht-infra`` — the infrastructure / DevOps runtime.

Provides a general-purpose infrastructure engineering sandbox suitable for
tasks involving Terraform, Ansible, Kubernetes (kubectl/helm), cloud CLIs,
and container orchestration. The image is deliberately runtime-agnostic at
the application layer: the primary payload is *tooling* rather than an
application SDK.

Key pre-installed tools:

* ``terraform``        — IaC provisioning (primary for infra tasks)
* ``ansible``          — configuration management / playbook execution
* ``kubectl``          — Kubernetes cluster control
* ``helm``             — Kubernetes package manager
* ``aws-cli`` (v2)     — AWS cloud CLI
* ``azure-cli``        — Azure cloud CLI
* ``gcloud``           — Google Cloud SDK CLI
* ``docker`` / DinD    — container build + compose (task DBs / services)
* ``packer``           — machine-image builds
* ``vault``            — HashiCorp Vault CLI
* ``consul``           — HashiCorp Consul CLI
* ``jq`` / ``yq``      — JSON/YAML processing
* ``shellspec``        — BDD shell-script test framework (primary eval harness)
* ``bats-core``        — Bash Automated Testing System (secondary harness)
* ``ttyd``             — browser terminal at :7681
* ``code-server``      — browser VS Code at :8443

Python 3 is kept as a scripting substrate (Ansible requires it; many infra
utility scripts are Python). No application-level Python frameworks are
installed — those live in the python-* family.

Two module-level exports:

* ``template``  — the imperative :class:`AsyncTemplate` build pipeline.
* ``manifest``  — the declarative capability sheet read by the LLM
  classifier and the ``templates`` SQL table.

Build:
    cd infra/e2b/templates/infra
    python build_dev.py     # -> utkrusht-infra-dev
    python build_prod.py    # -> utkrusht-infra   (once verified)
"""
from __future__ import annotations

from e2b import AsyncTemplate

# ---------------------------------------------------------------------------
# Manifest — declarative capability sheet
# ---------------------------------------------------------------------------
manifest = {
    "template_id": "utkrusht-infra",
    "status": "built",
    "primary_runtime": "infra",
    "personas": ["devops_engineer", "platform_engineer", "sre", "cloud_engineer"],
    "eval_methods": ["test_suite"],
    "capabilities": {
        # There is no single application SDK version here; Python 3 is the
        # scripting substrate (Ansible dependency). Terraform and other tools
        # are not "language versions" in the traditional sense but we record
        # the primary IaC tool version so the classifier can match infra tasks.
        "language_versions": {
            "python": "3.12",
            "terraform": "1.9",
            "ansible": "2.17",
        },
        "frameworks": [
            # IaC
            "terraform",
            "ansible",
            "packer",
            # Container / Kubernetes
            "docker",
            "docker-compose",
            "kubectl",
            "helm",
            # Secret / service mesh tooling
            "vault",
            "consul",
            # Shell testing harnesses (eval)
            "shellspec",
            "bats-core",
        ],
        "datastores": ["postgres", "mysql", "mongo", "redis", "elasticsearch"],
        "protocols": ["rest", "grpc", "websocket"],
        "tools": [
            # Core Unix utilities
            "git",
            "curl",
            "wget",
            "jq",
            "yq",
            "unzip",
            "zip",
            "make",
            "build-essential",
            "ca-certificates",
            "gnupg",
            "lsb-release",
            "netcat-openbsd",
            "openssh-client",
            "rsync",
            # Container toolchain
            "docker-ce",
            "docker-ce-cli",
            "containerd.io",
            "docker-buildx-plugin",
            "docker-compose-plugin",
            "docker-compose",          # shim → docker compose
            # IaC / cloud
            "terraform",
            "packer",
            "ansible",
            "aws-cli",
            "azure-cli",
            "google-cloud-sdk",
            # Kubernetes
            "kubectl",
            "helm",
            # HashiCorp service tools
            "vault",
            "consul",
            # YAML / data processing
            "yq",
            # Shell testing
            "shellspec",
            "bats-core",
            # Scripting substrate
            "python3",
            "python3-pip",
            # Candidate-facing browser surfaces
            "ttyd",
            "code-server",
        ],
        "requires": {"browser": False, "gpu": False},
        "tags": ["infra", "devops", "terraform", "ansible", "kubernetes", "cloud"],
    },
    "build_cmd": "terraform init",
    "test_cmd": "shellspec --format progress",
    "compile_cmd": "terraform validate",
    "install_cmd": (
        "apt-get install -y gnupg software-properties-common curl "
        "&& curl -fsSL https://apt.releases.hashicorp.com/gpg "
        "| gpg --dearmor > /usr/share/keyrings/hashicorp-archive-keyring.gpg "
        "&& echo \"deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] "
        "https://apt.releases.hashicorp.com $(lsb_release -cs) main\" "
        "> /etc/apt/sources.list.d/hashicorp.list "
        "&& apt-get update && apt-get install -y terraform"
    ),
    "install_verify": "terraform version",
    "install_seconds": 60,
    "description": (
        "Infrastructure / DevOps runtime with Terraform, Ansible, kubectl, "
        "Helm, AWS/Azure/GCP CLIs, HashiCorp Vault & Consul, Docker-in-Docker, "
        "and shell testing harnesses (shellspec, bats-core); browser terminal "
        "via ttyd and browser IDE via code-server."
    ),
}

# ---------------------------------------------------------------------------
# Template build pipeline
# ---------------------------------------------------------------------------
template = (
    AsyncTemplate()
    # Debian Bookworm slim gives us a clean apt base with a minimal footprint.
    # We deliberately avoid a language-specific base image (e.g. python:3.12)
    # because the primary payload here is CLI tooling, not an SDK.
    .from_image("debian:bookworm-slim")
    .set_user("root")
    .set_workdir("/")
    # ── 1. Core apt prerequisites ────────────────────────────────────────────
    .run_cmd(
        "apt-get update && apt-get install -y --no-install-recommends "
        "ca-certificates curl gnupg lsb-release git jq unzip zip wget make "
        "build-essential openssh-client rsync netcat-openbsd sudo "
        "python3 python3-pip python3-venv "
        "&& rm -rf /var/lib/apt/lists/* "
        "&& mkdir -p /home/user"
    )
    # ── 2. Docker CE (DinD — tasks spin up DB / service containers) ──────────
    .run_cmd("install -m 0755 -d /etc/apt/keyrings")
    .run_cmd(
        "curl -fsSL https://download.docker.com/linux/debian/gpg "
        "| gpg --dearmor -o /etc/apt/keyrings/docker.gpg "
        "&& chmod a+r /etc/apt/keyrings/docker.gpg"
    )
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
    # v1-style `docker-compose` shim so task run.sh files don't need updates.
    .run_cmd(
        "printf '#!/bin/sh\\nexec docker compose \"$@\"\\n' "
        "> /usr/local/bin/docker-compose && "
        "chmod +x /usr/local/bin/docker-compose"
    )
    # ── 3. HashiCorp apt repo → Terraform + Packer + Vault + Consul ─────────
    .run_cmd(
        "curl -fsSL https://apt.releases.hashicorp.com/gpg "
        "| gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg"
    )
    .run_cmd(
        'echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] '
        'https://apt.releases.hashicorp.com $(lsb_release -cs) main" '
        '> /etc/apt/sources.list.d/hashicorp.list'
    )
    .run_cmd(
        "apt-get update && apt-get install -y --no-install-recommends "
        "terraform packer vault consul "
        "&& rm -rf /var/lib/apt/lists/*"
    )
    # ── 4. Ansible (via pip — apt version often lags significantly) ──────────
    .run_cmd(
        "pip install --no-cache-dir --break-system-packages "
        "ansible==10.4.0 ansible-lint==24.9.2"
    )
    # ── 5. kubectl ───────────────────────────────────────────────────────────
    .run_cmd(
        "curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key "
        "| gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg"
    )
    .run_cmd(
        'echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] '
        'https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /" '
        '> /etc/apt/sources.list.d/kubernetes.list'
    )
    .run_cmd(
        "apt-get update && apt-get install -y --no-install-recommends kubectl "
        "&& rm -rf /var/lib/apt/lists/*"
    )
    # ── 6. Helm ──────────────────────────────────────────────────────────────
    .run_cmd(
        "curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 "
        "| bash"
    )
    # ── 7. AWS CLI v2 ────────────────────────────────────────────────────────
    .run_cmd(
        "curl -fsSL 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' "
        "-o /tmp/awscliv2.zip "
        "&& unzip -q /tmp/awscliv2.zip -d /tmp "
        "&& /tmp/aws/install "
        "&& rm -rf /tmp/awscliv2.zip /tmp/aws"
    )
    # ── 8. Azure CLI ─────────────────────────────────────────────────────────
    .run_cmd(
        "curl -fsSL https://aka.ms/InstallAzureCLIDeb | bash "
        "&& rm -rf /var/lib/apt/lists/*"
    )
    # ── 9. Google Cloud SDK ──────────────────────────────────────────────────
    .run_cmd(
        "curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg "
        "| gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg"
    )
    .run_cmd(
        'echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] '
        'https://packages.cloud.google.com/apt cloud-sdk main" '
        '> /etc/apt/sources.list.d/google-cloud-sdk.list'
    )
    .run_cmd(
        "apt-get update && apt-get install -y --no-install-recommends "
        "google-cloud-cli && rm -rf /var/lib/apt/lists/*"
    )
    # ── 10. yq (YAML processor — mikefarah edition) ──────────────────────────
    .run_cmd(
        "curl -fsSL "
        "https://github.com/mikefarah/yq/releases/download/v4.44.3/yq_linux_amd64 "
        "-o /usr/local/bin/yq && chmod +x /usr/local/bin/yq"
    )
    # ── 11. shellspec (BDD shell testing framework — primary eval harness) ───
    .run_cmd(
        "curl -fsSL https://git.io/shellspec | sh -s -- --yes "
        "&& ln -sf /root/.local/share/shellspec/shellspec /usr/local/bin/shellspec"
    )
    # ── 12. bats-core (secondary shell testing harness) ──────────────────────
    .run_cmd(
        "git clone --depth 1 --branch v1.11.0 "
        "https://github.com/bats-core/bats-core.git /tmp/bats-core "
        "&& /tmp/bats-core/install.sh /usr/local "
        "&& rm -rf /tmp/bats-core"
    )
    # ── 13. ttyd — browser terminal at :7681 ─────────────────────────────────
    .run_cmd(
        "curl -fsSL -o /usr/local/bin/ttyd "
        "https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.x86_64 "
        "&& chmod +x /usr/local/bin/ttyd "
        "&& curl -fsSL -o /tmp/code-server.deb "
        "https://github.com/coder/code-server/releases/download/v4.96.4/code-server_4.96.4_amd64.deb "
        "&& dpkg -i /tmp/code-server.deb "
        "&& rm /tmp/code-server.deb"
    )
    # ── 14. Start script ─────────────────────────────────────────────────────
    .copy("start.sh", "/usr/local/bin/start.sh")
    .run_cmd("chmod +x /usr/local/bin/start.sh")
    .set_workdir("/home/user")
    .set_start_cmd("sudo /usr/local/bin/start.sh", "sleep 5")
)