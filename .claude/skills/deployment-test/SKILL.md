---
name: deployment-test
description: Use when verifying an Utkrushta task is production-ready end-to-end on the dev droplet — before assigning the task to candidates, after generating a new task, or when smoke-testing template-repo + run.sh + kill.sh + service connectivity for a task that has `is_shared_infra_required = true`.
---

# Deployment Test

End-to-end lifecycle smoke-test for an Utkrushta task. Mirrors the production candidate journey: pre-flight checks → deploy → readiness wait → candidate-login → verification → 60s soak → kill → final clean. The only input is the task-id (from $ARGUMENTS).

## Overview

This skill is a **read-only smoke-test**. It does NOT:
- Write to Supabase
- Push to GitHub
- Edit files on the droplet
- Iteratively fix and retry (use the `/deployment-test` slash command at `.claude/commands/deployment-test.md` for the fix-loop variant)

If any step fails, the skill stops and reports — that's a real failure the user needs to see.

## When to Use

- Validating a freshly-generated task before pushing it live to candidates
- Smoke-testing after editing a template repo's `run.sh`, `kill.sh`, `docker-compose.yml`, or `init_database.sql`
- Confirming an existing task's infra still deploys cleanly on the dev droplet

**Do NOT use** for tasks where `is_shared_infra_required = false` (PR-review, design-review, non-tech). The pre-flight will reject them.

## Variables

User-provided / runtime-selected:
- `TASK_ID` = $ARGUMENTS (ask the user if not provided)
- `DROPLET_IP` — **dynamically selected** in STEP 3 from prod `task_servers` (any free, active server)
- `LOCAL_SSH_KEYS_DIR` — **required**, no default. Directory on the user's machine that holds the dev SSH keys. Resolved with this priority: (1) `LOCAL_SSH_KEYS_DIR` env var if set, otherwise (2) value of `LOCAL_SSH_KEYS_DIR=` in `/d/Utkrushta_task/.env`. If neither is set, the skill hard-fails — there is no hardcoded fallback, because every developer's machine layout differs.
- `SSH_KEY` — **always a local file path under `$LOCAL_SSH_KEYS_DIR/`**. The skill uses the row's `private_key_master_path` only as a *hint* for which filename to look for (it strips any leading directory, keeping only the basename), then resolves `SSH_KEY = $LOCAL_SSH_KEYS_DIR/<basename>`. The skill **verifies the file exists locally before using it** — if it's missing, the skill hard-fails. Keys are never fetched from S3, env-encoded blobs, or any remote source.
- `TEMPLATE_DIR` = /tmp/deployment_test_$TASK_ID

Read from `.env` at runtime:
- `GH_TOKEN` = `grep ^GITHUB_UTKRUSHTAPPS_TOKEN= /d/Utkrushta_task/.env | cut -d= -f2-`
- `SUPABASE_DEV_URL` = `grep ^SUPABASE_URL_APTITUDETESTSDEV= /d/Utkrushta_task/.env | cut -d= -f2-`
- `SUPABASE_DEV_KEY` = `grep ^SUPABASE_API_KEY_APTITUDETESTSDEV= /d/Utkrushta_task/.env | cut -d= -f2-`
- `SUPABASE_PROD_URL` = `grep ^SUPABASE_URL_APTITUDETESTS= /d/Utkrushta_task/.env | cut -d= -f2-`
- `SUPABASE_PROD_KEY` = `grep ^SUPABASE_API_KEY_APTITUDETESTS= /d/Utkrushta_task/.env | cut -d= -f2-`

> **Note:** Tasks are read from **dev** Supabase (where they are generated). Servers are read from **prod** `task_servers` (where the active droplet pool lives). Both are read-only — the skill never writes.

---

## STEP 1 — Pre-flight: Supabase task definition (read-only)

Query the `tasks` row for `TASK_ID` from **dev** Supabase:

```bash
curl -s "$SUPABASE_DEV_URL/rest/v1/tasks?task_id=eq.$TASK_ID&select=task_id,is_shared_infra_required,task_blob,is_deployed" \
  -H "apikey: $SUPABASE_DEV_KEY" \
  -H "Authorization: Bearer $SUPABASE_DEV_KEY"
```

**Hard-fail conditions (abort with clear reason):**
- Row not found → "task_id $TASK_ID does not exist in dev Supabase"
- `is_shared_infra_required != true` → "task is not a deployment task; production /start_task_infra_deployment would reject it"
- `task_blob.resources.github_repo` missing or empty → "no template repo URL on this task"

Extract `GITHUB_REPO_URL` from `task_blob.resources.github_repo`.

---

## STEP 2 — Pre-flight: Clone GitHub template

Always read task source from the GitHub template repo, not from any local `infra_assets/` folder (which may not exist).

```bash
rm -rf $TEMPLATE_DIR
REPO_PATH=$(echo "$GITHUB_REPO_URL" | sed 's|https://github.com/||' | sed 's|/tree/.*||')
git clone "https://${GH_TOKEN}@github.com/${REPO_PATH}.git" $TEMPLATE_DIR
```

**Hard-fail conditions:**
- Clone fails → "template repo $GITHUB_REPO_URL is not accessible"
- `$TEMPLATE_DIR/run.sh` missing → "template is missing run.sh"
- `$TEMPLATE_DIR/kill.sh` missing → "template is missing kill.sh"
- `$TEMPLATE_DIR/docker-compose.yml` missing → "template is missing docker-compose.yml"

**Soft-warn (don't fail):**
- If `init_database.sql` exists and contains hardcoded `timestamp '20\d\d-` literals — warn that recent-date queries may return empty.

Parse `docker-compose.yml` to extract:
- Service names
- Container names (if defined)
- Exposed ports (left-side of `ports:` mappings)
- Environment variables that look like DB credentials (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `MYSQL_*`, `MONGO_*`, `REDIS_PASSWORD`)

Read `$TEMPLATE_DIR/README.md` (if present) and extract any documented HTTP endpoints. These drive STEP 6.

---

## STEP 3 — Pre-flight: Pick a free droplet from prod `task_servers`

Don't hardcode a droplet IP — query the prod server pool and pick any row that's idle and active.

```bash
curl -s "$SUPABASE_PROD_URL/rest/v1/task_servers?is_active=eq.true&tasksession_id=is.null&select=server_id,ip_address,private_key_master_path&limit=1" \
  -H "apikey: $SUPABASE_PROD_KEY" \
  -H "Authorization: Bearer $SUPABASE_PROD_KEY"
```

Response shape (from the actual table):

```json
[{
  "server_id": "0f8122d5-...",
  "ip_address": "64.227.178.86",
  "private_key_master_path": "ssh-keys/dutkrusht-dev-do"
}]
```

**Hard-fail if the response is `[]`** → "no free + active droplet in prod task_servers; either every server is mid-deployment or none are marked active. Cannot run deployment test now."

**Set runtime variables from the row:**
- `DROPLET_IP` = the row's `ip_address`
- `SERVER_ID` = the row's `server_id` (for the final report)
- `KEY_HINT` = the row's `private_key_master_path` (e.g., `ssh-keys/dutkrusht-dev-do`)

**Resolve `LOCAL_SSH_KEYS_DIR` (per-machine, REQUIRED — no hardcoded default):**

```bash
# Priority 1: shell env var
if [ -n "$LOCAL_SSH_KEYS_DIR" ]; then
  KEYS_DIR="$LOCAL_SSH_KEYS_DIR"
# Priority 2: value in /d/Utkrushta_task/.env
elif grep -q '^LOCAL_SSH_KEYS_DIR=' /d/Utkrushta_task/.env 2>/dev/null; then
  KEYS_DIR=$(grep '^LOCAL_SSH_KEYS_DIR=' /d/Utkrushta_task/.env | cut -d= -f2-)
else
  echo "FATAL: LOCAL_SSH_KEYS_DIR is not set."
  echo "       Add LOCAL_SSH_KEYS_DIR=/path/to/your/ssh-keys to /d/Utkrushta_task/.env"
  echo "       (or export it in your shell). Every developer's path differs, so there is no default."
  exit 1
fi

if [ ! -d "$KEYS_DIR" ]; then
  echo "FATAL: LOCAL_SSH_KEYS_DIR is set to '$KEYS_DIR' but that directory does not exist."
  exit 1
fi
```

**Resolve and verify the SSH key file locally** — strip any directory portion from the DB hint, keep only the basename, then look it up in `$KEYS_DIR`:

```bash
KEY_FILENAME=$(basename "$KEY_HINT")        # "ssh-keys/dutkrusht-dev-do" → "dutkrusht-dev-do"
SSH_KEY="${KEYS_DIR}/${KEY_FILENAME}"

if [ ! -f "$SSH_KEY" ]; then
  echo "FATAL: expected local SSH key at $SSH_KEY but it does not exist."
  echo "       Place the dev SSH key file '$KEY_FILENAME' under $KEYS_DIR."
  exit 1
fi
```

Hard-fail with the message above if the local file is missing — do NOT attempt to fetch the key from anywhere else.

**Important caveat — the skill does NOT claim the row.** Since we don't write to Supabase, there's a small race window where a real candidate deployment could grab this server while we're testing on it. Mitigation: tell the user when the test starts which server we picked, and recommend running off-hours if prod is actively assigning sessions. If you want zero risk, you can manually flip the chosen row's `is_active` to false in the dashboard before running, then back to true after.

Verify SSH access with the local key + IP before proceeding:

```bash
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no -o ConnectTimeout=10 root@$DROPLET_IP "echo ok"
```

Hard-fail with the SSH error if `echo ok` doesn't return.

---

## STEP 4 — Pre-flight: Verify droplet is clean

```bash
ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$DROPLET_IP \
  "docker ps -a && echo '---IMAGES---' && docker images && echo '---VOLUMES---' && docker volume ls && echo '---TASK_DIR---' && ls /root/task 2>&1 || echo 'folder not found'"
```

**Hard-fail if any of:**
- Containers exist (running or stopped)
- Docker images exist
- Docker volumes exist
- `/root/task` exists

Report output and tell the user to clean the droplet manually before re-running. Do NOT auto-clean — that's a fix-loop behavior we deliberately avoid here. Suggested command:

```
ssh -i $SSH_KEY root@$DROPLET_IP "cd /root/task && bash kill.sh 2>/dev/null; docker system prune -a --volumes -f; rm -rf /root/task"
```

---

## STEP 5 — Deploy

Upload from the cloned template (NOT from any local task folder):

```bash
ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$DROPLET_IP "mkdir -p /root/task"

scp -i $SSH_KEY -o StrictHostKeyChecking=no \
  $TEMPLATE_DIR/docker-compose.yml \
  $TEMPLATE_DIR/run.sh \
  $TEMPLATE_DIR/kill.sh \
  root@$DROPLET_IP:/root/task/

# Include init_database.sql if present
if [ -f "$TEMPLATE_DIR/init_database.sql" ]; then
  scp -i $SSH_KEY $TEMPLATE_DIR/init_database.sql root@$DROPLET_IP:/root/task/
fi

# Copy any other files the template includes (config files, seed scripts) defensively:
scp -i $SSH_KEY -r $TEMPLATE_DIR/* root@$DROPLET_IP:/root/task/

ssh -i $SSH_KEY root@$DROPLET_IP \
  "cd /root/task && sed -i 's/\r//' run.sh kill.sh && bash run.sh"
```

**Hard-fail if `bash run.sh` exits non-zero.** Capture and report:
- The error output
- Last 50 lines of `docker-compose logs` from the droplet
- Output of `docker ps -a` to show what state things are in

Do NOT edit anything on the droplet. Do NOT retry.

---

## STEP 6 — Wait for readiness ("get ready for candidate login")

The candidate's environment expects services to be fully up before they connect. Don't trust `bash run.sh` exit code alone — actively poll.

**6a. Container readiness (max 90s):**

```bash
ssh -i $SSH_KEY root@$DROPLET_IP "docker ps -a --format '{{.Names}}\t{{.Status}}'"
```

Loop with 5s pauses until every service from docker-compose.yml shows `Up` (and `healthy` if a healthcheck is defined). Hard-fail at 90s with the last status snapshot.

**6b. Port readiness (max 60s per port):**

For each exposed port from docker-compose.yml:

```bash
timeout 60 bash -c "until nc -z $DROPLET_IP <PORT>; do sleep 2; done"
```

Hard-fail if any port doesn't open in 60s. Report which port and which service.

---

## STEP 7 — Candidate-login simulation (service-discovery-driven)

The candidate's environment can expose **any combination** of services — Postgres, MySQL, MongoDB, Redis, Kafka, RabbitMQ, Elasticsearch, an HTTP API, a gRPC server, a k8s/k3s control plane, MinIO, ClickHouse, anything. Don't assume what's there. **Discover, then validate.**

Connect from the **host** (over the public droplet IP), not by ssh'ing into the droplet — candidates access services over the network, not from inside the box.

### 7a. Discover what's actually running

For every service in `docker-compose.yml`, gather:
- `image:` — the registry image tells you the service kind (e.g. `postgres:15`, `redis:7`, `confluentinc/cp-kafka`, `bitnami/kubectl`, `quay.io/minio/minio`)
- `ports:` — which host ports map to which container ports
- `environment:` — credentials, bootstrap configs (`POSTGRES_*`, `MYSQL_*`, `MONGO_*`, `REDIS_PASSWORD`, `KAFKA_*`, etc.)
- `volumes:` and `command:` — clues about init scripts, configs
- `healthcheck:` — if defined, the project itself documented how to know it's healthy

Also read every `Dockerfile`, `init_*.sql`, `*.conf`, and the `README.md` in the cloned template. The README is the contract with the candidate — whatever it tells the candidate to do is what we need to verify works.

Build a dynamic checklist: `[(service_name, kind, host:port, credentials, what_to_verify)]`. **Kind** is inferred from the image name — don't hardcode the list of supported kinds; if you see an unknown image, fall back to a generic TCP/HTTP probe and document the limitation in the report.

### 7b. For each discovered service, run the appropriate validation

Pick the validation based on `kind`:

| Kind (inferred from image) | Validation |
|---|---|
| Postgres / MySQL / MariaDB / MS SQL | Connect with detected creds → list tables → `SELECT count(*)` per table → MIN/MAX of timestamp columns → run `sample_queries.sql` if present |
| MongoDB | Connect → list collections → count docs per collection |
| Redis / KeyDB | `PING` → `INFO keyspace` → `DBSIZE` (require non-zero only if the task pre-seeds data) |
| Kafka / Redpanda | List brokers → list topics → for each topic README documents, `kafka-console-consumer` with `--max-messages 1 --timeout-ms 5000` to confirm messages exist |
| RabbitMQ | Hit management API `/api/queues` → confirm queues from README exist with expected message counts |
| Elasticsearch / OpenSearch | `GET /_cluster/health` → `GET /_cat/indices` → confirm indices from README exist |
| MinIO / S3-compatible | List buckets → list objects in each bucket → confirm bucket-name from README is present |
| HTTP API (FastAPI/Flask/Express/Django/Spring/etc.) | `curl /` or `/health` → curl each GET endpoint listed in the README that should work out-of-the-box |
| k8s / k3s / kind | `kubectl get nodes` → `kubectl get pods -A` → confirm all pods Running; for any Deployment in README, `kubectl get deploy` and check ready replicas |
| ClickHouse | `SELECT 1` → `SHOW TABLES` → row counts |
| gRPC | `grpcurl -plaintext <host>:<port> list` → confirm services |
| **Anything else / unknown image** | Generic check: TCP connect to each exposed port; if the port speaks HTTP, `curl -I` and confirm a response; flag the service as "unknown kind — generic probe only" in the report |

**For every service**, also:
- Capture `docker logs <container>` last 30 lines and scan for `ERROR`, `FATAL`, `panic`, `Exception` — surface any matches in the report (a service can be "Up" but throwing errors)
- Note the running image name + tag in the report so the user can see what was actually exercised

### 7c. Fail conditions

**Hard-fail if:**
- A service from docker-compose isn't reachable on its declared port from the host
- A discoverable validation step returns an error (auth fail, bad protocol, connection reset)
- A piece the README says works out-of-the-box returns empty/4xx/5xx
- Logs show `ERROR`/`FATAL`/`panic` for any service

**Don't fail on** (just record):
- Endpoints/handlers the README says are for the candidate to implement (404/501 expected)
- Services with `kind = unknown` where the generic TCP probe succeeded

The principle: we are not checking that *we* know how to drive every service — we are checking that *the candidate's environment* lets them drive it. If we can't even establish a connection or list its top-level state, the candidate also can't.

---

## STEP 8 — Verify deployment matches expectations

Lightweight sanity checks against what the README promises:

- DB row counts are non-zero (and within ranges if README declares any)
- Timestamp columns have at least some recent data (within last 30 days) if the task is "recent X" themed
- API endpoints documented as working return the field shape the README describes

Report each assertion as ✅/❌ with the actual value.

---

## STEP 9 — Sleep 60s (simulate candidate working)

Print one line so the user knows we're waiting on purpose:

```
[deployment-test] sleeping 60s to simulate candidate session...
```

Then `sleep 60`.

---

## STEP 10 — Run kill.sh (simulate candidate completing)

Run the task's own `kill.sh` as-is, exactly the way `/end_task_session` triggers it in production:

```bash
ssh -i $SSH_KEY root@$DROPLET_IP "cd /root/task && bash kill.sh"
```

Capture exit code and full output.

---

## STEP 11 — Verify droplet is fully clean

```bash
ssh -i $SSH_KEY root@$DROPLET_IP \
  "docker ps -a && echo '---IMAGES---' && docker images && echo '---VOLUMES---' && docker volume ls && echo '---TASK_DIR---' && ls /root/task 2>&1 || echo 'folder removed'"
```

**ALL of these must hold for kill.sh to pass:**
- Zero containers (running or stopped)
- Zero Docker images
- Zero Docker volumes
- `/root/task` does not exist

Hard-fail with a clear list of what's left if any check fails. Do NOT fix kill.sh — report the gap and stop.

---

## STEP 12 — Cleanup local temp clone

```bash
rm -rf $TEMPLATE_DIR
```

---

## Final Report

Print a single block summarizing every step. Format:

```
=== Deployment Test Report — task_id: <id> ===

Picked server (from prod task_servers)
  server_id                   <uuid>
  ip_address                  <ip>
  ssh_key                     /c/<private_key_master_path>

Pre-flight
  Supabase definition         ✅
  GitHub template clone       ✅  (<repo>)
  SSH reachability            ✅
  Droplet clean before        ✅

Deploy
  bash run.sh                 ✅  (<duration>s)

Readiness
  Containers up               ✅  (<n> services in <duration>s)
  Ports open                  ✅  (5432, 6379, 8000)

Candidate-login
  Postgres                    ✅  (4 tables, 1,250 rows)
  Redis                       ✅  (PONG, 32 keys)
  API /health                 ✅  (200)
  API /v1/users               ✅  (200, 50 results)

Verification
  Recent-data timestamps      ✅  (max within 7d)
  Sample query rows           ✅  (returns 12)

Soak
  60s sleep                   ✅

Kill
  bash kill.sh                ✅  (<duration>s)
  Droplet clean after         ✅

Result: PASS
```

On any failure, mark Result: FAIL and include the failing step's diagnostic output (logs, stderr, last container status, etc.). Do NOT push, commit, or edit anything.
