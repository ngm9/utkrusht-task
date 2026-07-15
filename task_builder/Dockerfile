# Dockerfile for the task_builder FastAPI service — the BACKEND API only.
# The web UI is a separate frontend service (its own repo); this image serves
# JSON at /api/* and streams pipeline progress over SSE. No static assets.
#
# Build context = repo root. The image carries the WHOLE repo because the
# service runs the generation pipeline stages (flows/, infra/,
# task_generation_prompts/, ...) as in-process subprocesses.
#
# Runtime env vars: see .env.example at the repo root. Values are populated
# per environment in Coolify — never baked into the image.

FROM python:3.13-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# git: PyGithub push targets + pipeline repo ops. build-essential: wheels
# that lack a manylinux build. curl: container healthcheck.
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
        ca-certificates git build-essential curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 10001 utkrusht-app-user

# Dependency layer — cached until requirements.txt changes.
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Pipeline stages write run artifacts under the repo tree, so the app user
# must own it.
RUN chown -R utkrusht-app-user:utkrusht-app-user /app

# Deploy-time configuration — override per environment in Coolify.
# CORS_ALLOW_ORIGINS: comma-separated allow-list of frontend origins ("*" ok
# since /api/* is gated by INTERNAL_PROXY_TOKEN); set it to the frontend URL
# in prod if you want to lock it down.
ENV PORT=8000 \
    TASK_BUILDER_HOST=0.0.0.0 \
    TASK_BUILDER_ENV=dev \
    INTERNAL_PROXY_TOKEN="" \
    CORS_ALLOW_ORIGINS="*" \
    BETTERSTACK_SOURCE_TOKEN="" \
    BETTERSTACK_INGESTING_HOST=""

EXPOSE 8000

# /api/health bypasses the access-token middleware, so the probe works even
# on locked-down deployments.
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
    CMD curl -fsS "http://127.0.0.1:${PORT}/api/health" || exit 1

ENV HOME=/home/utkrusht-app-user
USER utkrusht-app-user
STOPSIGNAL SIGTERM

CMD ["python", "-m", "task_builder"]
