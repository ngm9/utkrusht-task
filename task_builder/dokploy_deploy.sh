#!/usr/bin/env bash
# Deploy the Utkrusht Task Builder to a Dokploy instance via its API.
#
# Run this from a machine that can reach your Dokploy instance (your laptop or
# the Dokploy host). Nothing here is secret — all config comes from env vars
# and an env file you keep out of git. Requires: bash, curl, jq.
#
# Usage:
#   export DOKPLOY_URL="http://<host>:3000"
#   export DOKPLOY_API_KEY="<token>"          # rotate after deploying
#   export DOMAIN="taskbuilder.example.com"   # or leave unset to publish a port
#   export APP_ENV_FILE="./.env.dokploy"      # app secrets (see .env.example)
#   ./task_builder/dokploy_deploy.sh
#
# IMPORTANT: Dokploy's API field names drift between versions. If a step 4xx's,
# open  $DOKPLOY_URL/swagger  and adjust the JSON key for that one call — the
# flow (project → app → git → build → env → domain → deploy) is stable.
set -euo pipefail

: "${DOKPLOY_URL:?set DOKPLOY_URL, e.g. http://187.0.0.1:3000}"
: "${DOKPLOY_API_KEY:?set DOKPLOY_API_KEY}"
BRANCH="${BRANCH:-claude/task-builder-backend-deploy-jeccvk}"
REPO_OWNER_GH="${REPO_OWNER_GH:-ngm9}"
REPO_NAME="${REPO_NAME:-utkrusht-task}"
APP_ENV_FILE="${APP_ENV_FILE:-./.env.dokploy}"

API="$DOKPLOY_URL/api"
H=(-H "x-api-key: $DOKPLOY_API_KEY" -H "Content-Type: application/json")
say() { printf '\n=== %s ===\n' "$1"; }

command -v jq >/dev/null || { echo "jq is required"; exit 1; }
[ -f "$APP_ENV_FILE" ] || { echo "APP_ENV_FILE not found: $APP_ENV_FILE (copy .env.example and fill it)"; exit 1; }

say "0. sanity — validate key + reachability"
curl -fsS "${H[@]}" "$API/project.all" >/dev/null \
  || { echo "Cannot reach or authenticate to Dokploy. Check URL/key/network."; exit 1; }
echo "ok"

say "1. create project"
PROJECT_ID=$(curl -fsS "${H[@]}" -X POST "$API/project.create" \
  -d '{"name":"task-builder","description":"Utkrusht Task Builder"}' | jq -r '.projectId // .id')
echo "projectId=$PROJECT_ID"

say "2. create application"
APP_ID=$(curl -fsS "${H[@]}" -X POST "$API/application.create" \
  -d "$(jq -n --arg p "$PROJECT_ID" '{name:"task-builder",appName:"task-builder",description:"Conversational task generator + UI",projectId:$p}')" \
  | jq -r '.applicationId // .id')
echo "applicationId=$APP_ID"

say "3. point at the GitHub repo/branch"
# Requires a GitHub connection in Dokploy (Settings → Git). For a raw git URL
# use application.saveGitProvider (customGitUrl + sshKeyId) instead.
curl -fsS "${H[@]}" -X POST "$API/application.saveGithubProvider" \
  -d "$(jq -n --arg id "$APP_ID" --arg o "$REPO_OWNER_GH" --arg r "$REPO_NAME" --arg b "$BRANCH" \
        '{applicationId:$id,owner:$o,repository:$r,branch:$b,buildPath:"/"}')" >/dev/null
echo "ok"

say "4. build from the Dockerfile (context = repo root)"
curl -fsS "${H[@]}" -X POST "$API/application.saveBuildType" \
  -d "$(jq -n --arg id "$APP_ID" \
        '{applicationId:$id,buildType:"dockerfile",dockerfile:"task_builder/Dockerfile",dockerContextPath:".",dockerBuildStage:""}')" >/dev/null
echo "ok"

say "5. environment variables (from $APP_ENV_FILE)"
ENV_BLOCK="$(cat "$APP_ENV_FILE")"
curl -fsS "${H[@]}" -X POST "$API/application.saveEnvironment" \
  -d "$(jq -n --arg id "$APP_ID" --arg env "$ENV_BLOCK" '{applicationId:$id, env:$env}')" >/dev/null
echo "ok"

if [ -n "${DOMAIN:-}" ]; then
  say "6. domain → container port 8000"
  curl -fsS "${H[@]}" -X POST "$API/domain.create" \
    -d "$(jq -n --arg id "$APP_ID" --arg h "$DOMAIN" \
          '{applicationId:$id,host:$h,port:8000,https:false,certificateType:"none"}')" >/dev/null
  echo "mapped $DOMAIN → :8000"
else
  say "6. no DOMAIN set — skipping; publish a host port in the UI (Advanced → Ports, e.g. 8080→8000)"
fi

say "7. deploy (build runs on the Dokploy host)"
curl -fsS "${H[@]}" -X POST "$API/application.deploy" \
  -d "$(jq -n --arg id "$APP_ID" '{applicationId:$id}')" >/dev/null
echo "deploy triggered — watch the Deployments tab in the Dokploy dashboard."

cat <<EOF

------------------------------------------------------------------
When the build finishes and /api/health goes green, the app is at:
  ${DOMAIN:+http://$DOMAIN}${DOMAIN:-http://<host>:<published-port>}
Open it and enter your INTERNAL_PROXY_TOKEN when prompted.
------------------------------------------------------------------
EOF
