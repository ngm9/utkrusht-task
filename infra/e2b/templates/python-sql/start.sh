#!/usr/bin/env bash
# Sandbox boot script: bring up dockerd + browser terminal + browser IDE
# in the background, then exec the E2B sandbox entrypoint so the SDK can
# connect.
set -e

# Start the Docker daemon detached. dockerd writes its own logs into
# /var/log/docker.log; tail it from inside the sandbox if you need to debug.
mkdir -p /var/log
nohup dockerd > /var/log/docker.log 2>&1 &

# Wait briefly for the daemon to come up so the first `docker compose up`
# inside run.sh does not race the socket. ~10s is plenty in practice.
for _ in $(seq 1 20); do
    if docker info >/dev/null 2>&1; then
        break
    fi
    sleep 0.5
done

# Browser terminal on :7681. `-W` allows browser-side input (otherwise
# read-only). Spawning bash directly gives the candidate a root shell,
# matching the SDK exec semantics. No auth — see template.py note.
nohup ttyd -W -p 7681 bash > /var/log/ttyd.log 2>&1 &

# Browser VS Code on :8443. Opens at /home/user so the candidate can
# navigate into /home/user/task once it's cloned. `--auth none` is fine
# for the PoC (sandbox host is the security boundary).
mkdir -p /root/.config/code-server
nohup code-server \
    --bind-addr 0.0.0.0:8443 \
    --auth none \
    --disable-telemetry \
    /home/user > /var/log/code-server.log 2>&1 &

# Adminer browser DB GUI on :8080. PHP's built-in CLI server is the
# right size for a single-candidate sandbox. Adminer connects to the
# task's DB over localhost — the candidate compose file is responsible
# for mapping the DB port to host (which python-sql tasks already do).
nohup php -S 0.0.0.0:8080 -t /opt/adminer > /var/log/adminer.log 2>&1 &

# Hand off to the standard E2B entrypoint (overridden in the base image).
# If the base image already started its own supervisor, this script just
# returns and the existing one keeps running.
if [ -x /root/.jupyter/start-up.sh ]; then
    exec /root/.jupyter/start-up.sh
fi

# Fallback: keep the container alive.
exec tail -f /dev/null
