"""Thin wrappers around the E2B SDK for the assessment deploy/reset flow.

Keeps the SDK surface small and explicit so the rest of the flow does not
import from ``e2b`` directly. If we ever swap providers (Daytona,
self-hosted ``e2b-dev/infra``), this is the only file that changes.

Targets the E2B v2 SDK:
    - ``Sandbox.create(template=..., timeout=...)`` to provision
    - ``Sandbox(sandbox_id=...)`` to attach to an existing sandbox
    - ``Sandbox.list()`` returns a paginator
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from e2b import Sandbox

from infra.logger_config import logger

DEFAULT_PROBE_PORTS = (
    5432, 8000, 3000, 6379, 27017, 8080, 6443,
    5000,           # Flask preview (the python-sql task's app port)
    7681,           # ttyd browser terminal (template.py)
    8443,           # code-server browser IDE (template.py)
)
# Generous default for run.sh — first-run image pulls (e.g. pgvector,
# qdrant) can take a few minutes before compose-up even begins. Override
# via E2B_RUN_SH_TIMEOUT env var if a task needs more.
DEFAULT_RUN_SH_TIMEOUT = int(os.getenv("E2B_RUN_SH_TIMEOUT", "600"))


@dataclass
class SandboxHandle:
    sandbox_id: str
    template: str
    terminal_url: Optional[str]
    exposed_ports: Dict[str, str] = field(default_factory=dict)
    timeout_seconds: int = 7200


def create_and_setup(
    template: str,
    repo_url: str,
    timeout_hours: int = 2,
    probe_ports: tuple = DEFAULT_PROBE_PORTS,
) -> SandboxHandle:
    """Create a sandbox, clone the task repo, run setup, collect URLs."""
    timeout_seconds = int(timeout_hours * 3600)
    logger.info(f"Creating E2B sandbox (template={template}, timeout={timeout_seconds}s)")
    sb = Sandbox.create(template=template, timeout=timeout_seconds)

    logger.info(f"Cloning {repo_url} into sandbox {sb.sandbox_id}")
    authed_url = _authed_clone_url(repo_url)
    # Run as a single shell so the token stays in shell-arg memory and the
    # logged command never sees it. Rewrite the remote afterward so the
    # token does not persist in .git/config.
    clone_script = (
        f"git clone {authed_url} /home/user/task && "
        f"cd /home/user/task && "
        f"git remote set-url origin {repo_url}"
    )
    result = sb.commands.run(clone_script, timeout=60)
    if result.exit_code != 0:
        # Sanitize stderr in case git echoed the URL on failure.
        safe_err = _redact(result.stderr or "")
        logger.error(f"git clone failed: {safe_err}")
        sb.kill()
        raise RuntimeError(f"git clone failed: {safe_err}")

    # Match the droplet's `/root/task` convention so any task that
    # hardcodes that path (in compose volume mounts, init scripts, etc.)
    # keeps working.
    _symlink_root_task(sb)

    # Compatibility shim: many existing tasks call the legacy `docker-compose`
    # binary, but the template ships only the v2 plugin (`docker compose`).
    # This is also baked into template.py so future builds carry it natively;
    # the runtime install here keeps already-built templates working.
    _install_compose_shim(sb)

    # Some `run.sh` files use `nc -z host port` to wait for a service.
    # postgresql-client is in the template but netcat is not; install on
    # the fly until the next template rebuild bakes it in.
    _ensure_netcat(sb)

    # Don't fire run.sh until dockerd is actually accepting connections.
    if not _wait_for_dockerd(sb, timeout_seconds=30):
        sb.kill()
        raise RuntimeError("dockerd did not become ready within 30s")

    logger.info(f"Running setup in sandbox {sb.sandbox_id} (run.sh)")
    # `sudo -E` matches the droplet's root-everywhere semantics while
    # preserving env so PATH-derived lookups still work.
    setup = sb.commands.run(
        "cd /home/user/task && sudo chmod +x *.sh 2>/dev/null; "
        "sudo -E bash run.sh",
        timeout=DEFAULT_RUN_SH_TIMEOUT,
    )
    if setup.exit_code != 0:
        logger.error(f"run.sh failed: stdout={setup.stdout[-2000:]} stderr={setup.stderr[-2000:]}")
        sb.kill()
        raise RuntimeError(f"run.sh failed (exit {setup.exit_code})")

    exposed_ports: Dict[str, str] = {}
    for port in probe_ports:
        if _port_listening(sb, port):
            try:
                host = sb.get_host(port)
                # get_host returns just the hostname; HTTP consumers should
                # prefix with https://, raw-TCP consumers (psql, redis-cli)
                # need to read the host as-is and dial the port directly.
                exposed_ports[str(port)] = host
            except Exception as exc:
                logger.warning(f"Could not expose port {port}: {exc}")

    handle = SandboxHandle(
        sandbox_id=sb.sandbox_id,
        template=template,
        terminal_url=None,  # v2 SDK has no built-in web terminal URL
        exposed_ports=exposed_ports,
        timeout_seconds=timeout_seconds,
    )
    logger.info(f"Sandbox ready: {handle}")
    return handle


def kill(sandbox_id: str) -> bool:
    try:
        sb = Sandbox.connect(sandbox_id)
        sb.kill()
        logger.info(f"Killed sandbox {sandbox_id}")
        return True
    except Exception as exc:
        logger.error(f"Failed to kill sandbox {sandbox_id}: {exc}")
        return False


def list_active() -> List[Dict]:
    try:
        paginator = Sandbox.list()
        rows = []
        # SandboxPaginator: iterate via has_next() / next_items()
        while True:
            batch = paginator.next_items()
            if not batch:
                break
            rows.extend(batch)
            if not paginator.has_next:
                break
    except Exception as exc:
        logger.error(f"Could not list sandboxes: {exc}")
        return []

    out: List[Dict] = []
    for row in rows:
        out.append(
            {
                "sandbox_id": getattr(row, "sandbox_id", None),
                "template_id": getattr(row, "template_id", None),
                "started_at": str(getattr(row, "started_at", "")),
                "end_at": str(getattr(row, "end_at", "")),
            }
        )
    return out


def _install_compose_shim(sb: Sandbox) -> None:
    """Make `docker-compose <args>` resolve to `docker compose <args>`."""
    script = (
        "if ! command -v docker-compose >/dev/null 2>&1; then "
        "printf '#!/bin/sh\\nexec docker compose \"$@\"\\n' "
        "| sudo tee /usr/local/bin/docker-compose > /dev/null && "
        "sudo chmod +x /usr/local/bin/docker-compose; fi"
    )
    try:
        sb.commands.run(script, timeout=15)
    except Exception as exc:
        logger.warning(f"Could not install docker-compose shim: {exc}")


def _symlink_root_task(sb: Sandbox) -> None:
    """Make /root/task an alias for /home/user/task.

    Several existing tasks hardcode /root/task (the droplet path) in
    docker-compose volume mounts or init scripts. Mirroring it here means
    we don't have to rewrite task content.
    """
    try:
        sb.commands.run(
            "sudo ln -sfn /home/user/task /root/task",
            timeout=10,
        )
    except Exception as exc:
        logger.warning(f"Could not symlink /root/task: {exc}")


def _ensure_netcat(sb: Sandbox) -> None:
    """Ensure `nc` is available — many run.sh files use it as a port waiter."""
    script = (
        "if ! command -v nc >/dev/null 2>&1; then "
        "sudo apt-get update -qq >/dev/null && "
        "sudo apt-get install -y -qq netcat-openbsd >/dev/null; fi"
    )
    try:
        sb.commands.run(script, timeout=60)
    except Exception as exc:
        logger.warning(f"Could not install netcat: {exc}")


def _wait_for_dockerd(sb: Sandbox, timeout_seconds: int = 30) -> bool:
    """Block until `docker info` succeeds (dockerd accepting connections)."""
    script = (
        f"end=$(( $(date +%s) + {timeout_seconds} )); "
        "while [ $(date +%s) -lt $end ]; do "
        "  if sudo docker info >/dev/null 2>&1; then exit 0; fi; "
        "  sleep 0.5; "
        "done; exit 1"
    )
    try:
        result = sb.commands.run(script, timeout=timeout_seconds + 10)
        return result.exit_code == 0
    except Exception as exc:
        logger.warning(f"dockerd readiness check failed: {exc}")
        return False


def _authed_clone_url(repo_url: str) -> str:
    """Inject GITHUB_UTKRUSHTAPPS_TOKEN into a github.com HTTPS clone URL.

    Returns the URL unchanged if the token is unset or the URL is not a
    github.com HTTPS URL.
    """
    token = os.getenv("GITHUB_UTKRUSHTAPPS_TOKEN")
    if not token:
        return repo_url
    prefix = "https://github.com/"
    if not repo_url.startswith(prefix):
        return repo_url
    return repo_url.replace(prefix, f"https://x-access-token:{token}@github.com/", 1)


def _redact(text: str) -> str:
    token = os.getenv("GITHUB_UTKRUSHTAPPS_TOKEN")
    if token and token in text:
        return text.replace(token, "<REDACTED>")
    return text


def _port_listening(sb: Sandbox, port: int) -> bool:
    cmd = f"ss -ltn 'sport = :{port}' 2>/dev/null | grep -q LISTEN"
    try:
        result = sb.commands.run(cmd, timeout=10)
        return result.exit_code == 0
    except Exception:
        return False
