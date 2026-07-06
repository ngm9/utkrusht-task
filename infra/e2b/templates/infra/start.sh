#!/usr/bin/env bash
# Sandbox boot script for utkrusht-infra: bring up dockerd + browser terminal
# + browser IDE in the background, then keep the VM alive so the E2B SDK can
# connect. No Adminer — infra tasks don't need a DB GUI (PHP not installed).
set -e

mkdir -p /var/log

# Start Docker daemon (DinD) — tasks use docker compose to spin up LocalStack
# or other service containers needed by the Terraform scenario.
nohup dockerd > /var/log/docker.log 2>&1 &

# Wait for the daemon socket before any task run.sh races it.
for _ in $(seq 1 20); do
    if docker info >/dev/null 2>&1; then
        break
    fi
    sleep 0.5
done

# Browser terminal on :7681 — candidate gets a root shell with all IaC tooling.
nohup ttyd -W -p 7681 bash > /var/log/ttyd.log 2>&1 &

# Browser VS Code on :8443.
mkdir -p /root/.config/code-server
nohup code-server \
    --bind-addr 0.0.0.0:8443 \
    --auth none \
    --disable-telemetry \
    /home/user > /var/log/code-server.log 2>&1 &

if [ -x /root/.jupyter/start-up.sh ]; then
    exec /root/.jupyter/start-up.sh
fi
exec tail -f /dev/null
