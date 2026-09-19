#!/usr/bin/env bash
# Sandbox boot script for utkrusht-node-base: browser terminal + browser IDE.
# No dockerd — node-base tasks are pure in-process (no docker-compose).
set -e

mkdir -p /var/log

# Browser terminal on :7681
nohup ttyd -W -p 7681 bash > /var/log/ttyd.log 2>&1 &

# Browser VS Code on :8443
mkdir -p /root/.config/code-server
nohup code-server \
    --bind-addr 0.0.0.0:8443 \
    --auth none \
    --disable-telemetry \
    /home/user > /var/log/code-server.log 2>&1 &

exec tail -f /dev/null
