# Dockerfile for the task-builder worker (separate from web container).
#
# Same base image + deps as task_builder/Dockerfile; entrypoint is the
# Postgres-backed job worker loop. Restart-safe by design — claims jobs via
# SELECT FOR UPDATE SKIP LOCKED, watchdog requeues stuck rows.
#
# Runs alongside task_builder-web; uses the same env file. The worker does NOT
# expose a port and does NOT need INTERNAL_PROXY_TOKEN.

FROM python:3.13-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        git build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

# Per-run workspace lives in /tmp/utkrusht-runs/<job_id>/; the worker cleans
# its own directories. No volume needed.

CMD ["python", "-m", "infra.jobs.worker"]
