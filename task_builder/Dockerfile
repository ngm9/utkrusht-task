# Dockerfile for the task_builder FastAPI service (admin-panel backend).
#
# Build context = repo root (../). The compose file sets this.
#
# Runtime env vars expected (see .env.example):
#   PORT, TASK_BUILDER_HOST, TASK_BUILDER_ENV
#   INTERNAL_PROXY_TOKEN — required in prod
#   SUPABASE_URL_APTITUDETESTSDEV / SUPABASE_API_KEY_APTITUDETESTSDEV
#   (and PROD variants for prod runs)
#   OPENAI_API_KEY, PORTKEY_API_KEY
#   GITHUB_UTKRUSHTAPPS_TOKEN, GITHUB_GIST_TOKEN, REPO_OWNER
#   E2B_API_KEY, SANDBOX_EVAL_ENABLED

FROM python:3.13-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System deps: git for PyGithub push targets, build-essential for any wheel
# that lacks a manylinux build.
RUN apt-get update && apt-get install -y --no-install-recommends \
        git build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy only what the web tier needs. Worker image extends this file (see
# infra/jobs/Dockerfile) and brings the same source — no duplication.
COPY . .

# Default port; override via PORT env.
ENV PORT=8000
EXPOSE 8000

# Health check at the public path that bypasses the token middleware.
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request,sys; \
        sys.exit(0) if urllib.request.urlopen(f'http://127.0.0.1:{__import__(\"os\").environ.get(\"PORT\",\"8000\")}/api/health', timeout=3).status==200 else sys.exit(1)" \
    || exit 1

CMD ["python", "-m", "task_builder"]
