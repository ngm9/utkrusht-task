#!/usr/bin/env bash
# Sandbox boot script for utkrusht-python: bring up dockerd + browser terminal
# + browser IDE + DB GUI in the background, then keep the VM alive so the E2B
# SDK can connect. Same shape as templates/python-sql/start.sh — these services
# are runtime-agnostic.
set -e

# Start the Docker daemon detached. dockerd writes its own logs to
# /var/log/docker.log; tail it from inside the sandbox to debug.
mkdir -p /var/log
nohup dockerd > /var/log/docker.log 2>&1 &

# Wait briefly for the daemon so the first `docker compose up` inside a task's
# run.sh does not race the socket. ~10s is plenty in practice.
for _ in $(seq 1 20); do
    if docker info >/dev/null 2>&1; then
        break
    fi
    sleep 0.5
done

# Browser terminal on :7681. `-W` allows browser-side input; bash gives the
# candidate a root shell. No auth — the sandbox's signed E2B host is the
# security boundary.
nohup ttyd -W -p 7681 bash > /var/log/ttyd.log 2>&1 &

# Browser VS Code on :8443, opened at /home/user.
mkdir -p /root/.config/code-server
nohup code-server \
    --bind-addr 0.0.0.0:8443 \
    --auth none \
    --disable-telemetry \
    /home/user > /var/log/code-server.log 2>&1 &

# Adminer browser DB GUI on :8080. PHP's built-in CLI server is the right size
# for a single-candidate sandbox.
nohup php -S 0.0.0.0:8080 -t /opt/adminer > /var/log/adminer.log 2>&1 &

# Hand off to the standard E2B entrypoint if the base image provides one;
# otherwise keep the VM alive so the SDK stays connected.
if [ -x /root/.jupyter/start-up.sh ]; then
    exec /root/.jupyter/start-up.sh
fi
exec tail -f /dev/null
