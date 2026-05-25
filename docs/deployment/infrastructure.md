# Deployment Infrastructure: Research & Decisions

> **Status**: Phase 1 PoC validated end-to-end on hosted E2B; Phase 2 design captured.
> **Author**: Naman + Claude
> **Audience**: Utkrushta engineering team

---

## TL;DR

Today, candidate task environments live on a small fixed pool of DigitalOcean droplets. State drifts across five places (Supabase, GitHub, droplet filesystem, droplet docker state, the IP pool). The dominant operational pain is **stale state from abandoned tasks**: a candidate walks away, the droplet stays "occupied," the next deploy fails, a human has to clean up.

We evaluated multi-tenant Docker, Fargate, Fly Machines, Kata Containers, Kubernetes, and agent-sandbox platforms (E2B, Daytona, Coder). We chose **agent sandboxes (hosted E2B for Phase 1)** because they collapse the system to a single source of truth (the sandbox handle), self-clean abandoned sessions via idle-timeout, and let our existing `run.sh` / `kill.sh` task content survive unchanged.

This document captures the framing, the alternatives, the costs, and what the full implementation looks like end-to-end (infra, candidate UX, frontend, backend, state).

**Phase 1 PoC headline findings** (drawn from a working `python-sql` template + a real Python+SQL task deployed to a hosted E2B sandbox):

- **DinD inside Firecracker works cleanly** — `docker compose up`, postgres image pull, container networking, init SQL all pass on the canonical test (§29 closes that risk).
- **Cold start is ~25–35 s** (sandbox boot + clone + `compose up` + DB seed) — well inside the 60–90 s droplet baseline.
- **E2B's port forwarder is HTTPS-only.** Raw-TCP from the candidate's laptop does **not** work — `psql -h <port>-<id>.e2b.app:5432` times out at the L7 proxy. We resolve this with **per-stack web consoles baked into each template** (§13b).
- **Browser-native candidate UX is achievable today**: `ttyd` (terminal) + `code-server` (IDE) + Adminer-class GUI (DB) all work as iframe-able HTTPS surfaces from inside the sandbox. EC2-Session-Manager-style "click to open" UX is *not* shipped by E2B, but is cheap to build on top.
- **Candidate repo model**: per-attempt repo provisioned at task start via GitHub's "template repository" feature, dual-credential (SSH deploy key in sandbox + fine-grained PAT for laptop), no GitHub account required of the candidate, optional ownership transfer post-submit (§22a).

---

## Part 1 — Problem & decision

### 1. Current state

The deploy path today (`multiagent.py deploy-task` → `droplet_utils.py`):

1. Read `tasks` row from Supabase, get the GitHub repo URL.
2. `select_best_droplet_ip()` polls each IP in `AVAILABLE_IPS` over SSH, counts running containers, picks the first idle droplet.
3. Clone the repo to a local temp dir, SFTP-upload to `/root/task` on the droplet.
4. SSH in, `chmod +x *.sh`, run `bash /root/task/run.sh` (Compose-up).
5. Mark `is_deployed=true` in Supabase, with a `deployment_info` JSON capturing `droplet_ip`, `deployed_at`, etc.

The reset path (`multiagent.py reset-task`) SSHes back, runs `kill.sh` (`docker compose down -v`, `docker system prune -a`, `rm -rf /root/task`), and clears the Supabase row.

### 2. Where the state lives

| Source of truth (?) | What it claims to know | Drift risk |
|---|---|---|
| `tasks.is_deployed` + `deployment_info` (Supabase) | "This task is deployed on droplet X" | High — set on success, only cleared on a successful `reset-task` |
| GitHub repo | "These are the task files" | Low — append-only |
| `/root/task/` on the droplet | "The current task's files" | High — only one task fits per droplet |
| Droplet Docker state (`docker ps`, volumes, networks) | "What's actually running" | High — kill.sh failures leave orphans |
| `AVAILABLE_IPS` env var | "These droplets exist" | Manual; updated by humans |

There is no single authoritative answer to *"what is running where right now?"*. Every check requires SSH + `docker ps` against each droplet and cross-reference with Supabase.

### 3. The actual pain

- **Abandoned tasks become stale droplets.** A candidate stops mid-test (closes laptop, network drops, gives up). `kill.sh` is never invoked. The droplet has containers + volumes + a `/root/task` directory. Future deploys see "non-zero containers" and skip it. Eventually the pool fills.
- **Pool exhaustion is operational, not architectural.** A human notices, SSHes in, runs cleanup. This is toil.
- **Cold start is ~60–90s on a clean droplet** (SFTP + `compose up` + DB readiness wait). On a stale-occupied pool, a deploy might fail and have to retry against a different droplet, doubling the time before a candidate sees their environment.
- **Compose project naming collides** when run.sh is re-run on partial state — Compose default project name is the directory name, so the second `up` reuses or conflicts with the first.

### 4. What we want from a replacement

- **Single source of truth** for "what is running." Whoever runs the task should be the inventory, not Supabase + droplets + IPs.
- **Self-cleaning abandonment.** No human involvement when a candidate walks away.
- **No fixed pool.** Capacity should scale on demand; no `AVAILABLE_IPS`.
- **Idempotent deploy/reset.** Re-running a deploy or reset on partial state should converge, not error.
- **Existing task content survives.** `run.sh`, `kill.sh`, `docker-compose.yml`, `init_database.sql` should not be rewritten per task.
- **Heterogeneous stacks still work.** Compose, DinD, Kubernetes scenarios, multi-service production-shaped stacks.
- **Future traffic generators tie cleanly to lifecycle.** Spinning up traffic against a candidate's API and tearing it down with the rest should be one mechanism, not two.

### 5. Options considered (one-liners)

| Option | Verdict | Why |
|---|---|---|
| Multi-tenant Docker on existing droplets | ❌ Doesn't fix the core problem | Still stateful; orphan containers still possible; just shifts the inventory problem from per-droplet to per-host |
| Kubernetes (self-hosted or GKE Autopilot / EKS Auto) | ⏸ Deferred | Right answer at much higher volume; over-engineered for current scale |
| AWS Fargate / Cloud Run | ❌ Rejected | 30–60s cold start; no Docker daemon → DinD scenarios break; no nesting for K8s tasks |
| Fly.io Machines | ⚪ Viable runner-up | API-driven Firecracker microVMs, fast boot, real DinD inside; but you still write the session lifecycle yourself |
| Kata Containers + own infra | ⚪ Viable runner-up | OCI-only (fine for our scenarios); operationally heavier; you write the orchestration |
| **Agent sandboxes (E2B / Daytona)** | ✅ **Selected** | Sandbox handle = source of truth; idle-timeout = auto-cleanup; SDK-driven lifecycle; templates replace per-deploy `run.sh` re-installs; same primitives as Fly Machines but with the lifecycle abstraction we'd otherwise have to build ourselves |

### 6. Why agent sandboxes specifically

Agent sandboxes (E2B, Daytona, Modal, Northflank, Coder) emerged from the AI-agent ecosystem to solve a problem that maps almost 1:1 to ours: *"spin up an isolated Linux box, run untrusted code, capture results, tear down — programmatically."*

What we get:

- **The sandbox handle *is* the inventory.** `Sandbox.list()` from the SDK is the canonical answer to "what's running." No separate `AVAILABLE_IPS`, no `docker ps` polling.
- **Idle timeout is built in.** Set it once at creation; abandonment becomes a no-op.
- **`run.sh` and `kill.sh` survive unchanged.** The sandbox is a Linux box; whatever ran on a droplet runs in a sandbox.
- **No pool to manage.** Each `Sandbox.create()` is independent.
- **Per-second billing.** No idle droplet cost.
- **Pause / resume.** A candidate stepping away gets a full snapshot (disk + memory) for free; resumes instantly without losing work.
- **Atomic teardown.** `sb.kill()` removes the entire VM. No `rm -rf /root/task`, no orphaned containers, no partial cleanup.

What we give up:

- **Vendor coupling** (mitigated: `e2b-dev/infra` is Apache-2 self-hostable; Daytona OSS is too).
- **Direct host access for ops debugging.** Becomes SDK calls instead of SSH.
- **Some control over networking** (port exposure shapes are platform-specific; see Part 2).

---

## Part 2 — How different infrastructure scenarios work

### 7. Scenario taxonomy

The current task catalog (per `task_input_files/` + `task_generation_prompts/Basic|Beginner|Intermediate/`) breaks down by infra shape:

| Shape | Examples | Inside-sandbox model |
|---|---|---|
| Single-service | `python_basic`, `Python_Fastapi`, `expressjs_basic`, `ReactJs_basic`, `GO_basic` | One process; expose one port |
| Compose stacks | `python_fastapi_docker`, `nodejs_postgres`, `nodejs_mongodb`, `mongodb_react_node`, `Java_spring_boot` | DinD; `docker compose up` |
| Cache / DB centerpiece | `PostgreSQL_basic`, `SQL_basic`, `python_redis`, `golang_redis` | Compose with one DB service; candidate connects to it |
| Docker-the-skill | `Java_docker_basic`, `golang_docker_prompt` | Candidate uses `docker` directly inside the sandbox |
| Kubernetes scenarios | (future) | k3d in sandbox, see §11 |
| Multi-service production | `Java_distributed_systems_basic`, `apache_camel_prompt` | Heavier Compose; same model |

The good news: **the first four categories are all variations of "Docker / Compose inside a Linux box."** One template per stack handles them all.

### 8. Postgres / MySQL / Mongo: disk and lifecycle

The pattern (taken straight from `task_generation_prompts/Basic/SQL_basic_prompt.py`):

- `docker-compose.yml` defines a DB service with hardcoded credentials, port 5432 exposed, `init_database.sql` mounted at `/docker-entrypoint-initdb.d/`.
- `run.sh` runs `docker compose up -d`, waits for the DB to accept connections.
- `init_database.sql` creates schema + seed data deterministically.

This pattern translates directly:

- **Disk during the session.** The DB's data lives in a Docker named volume on the sandbox FS. Survives every interaction inside the session (terminal commands, candidate edits, etc.).
- **Disk across pause/resume.** E2B's pause snapshots disk + memory. A candidate who pauses and resumes 30 minutes later sees their DB exactly as they left it — including in-flight transactions if any.
- **Disk across kill.** Gone. *This is intentional for assessments.* The next session re-seeds from `init_database.sql`. No "candidate B sees candidate A's data" risk.
- **Snapshot for grading.** On submit, before kill, optionally:
  ```bash
  docker exec <db> pg_dump -U postgres ... > /tmp/final.sql
  ```
  Upload to S3 via the SDK, attach the S3 path to the session row. Grading pipelines read the dump.
- **Sizing.** Default sandbox: 2 vCPU / 2 GB RAM. For large-dataset SQL tasks (`SQL_large_scale_datasets_prompt.py`): bump to 4 vCPU / 8 GB. Configured per template.

### 9. Redis (and other in-memory stores)

Same model:

- Redis container inside the sandbox on the internal Docker network at `redis:6379`.
- Candidate uses `redis-cli -h localhost` from the in-sandbox terminal.
- For external access from candidate's laptop, expose port 6379 via `sb.get_host(6379)`. (See §12 caveat about raw-TCP exposure.)
- Pause/resume preserves keys; kill destroys them; reset re-seeds from any seed script.

### 10. Multi-service production-shaped stacks

A typical Apache Camel or distributed-systems task involves 3–5 services, often a DB, often a message broker:

```yaml
services:
  api:        ...
  worker:     ...
  postgres:   ...
  redis:      ...
  rabbitmq:   ...
```

Compose handles all of this inside a single Docker network. The sandbox just hosts the daemon. Candidate's interaction surface is whichever ports the task exposes externally (usually just the API on `:8000` or `:3000`).

Sizing: bump RAM to 4–8 GB. Most multi-service stacks fit comfortably; the few that don't (heavy Java + Postgres + Kafka + Camel) might need 8–16 GB. Configured per template.

### 11. Kubernetes — three patterns and the recommendation

Three viable patterns, in increasing weight:

#### Option A — k3d / kind inside the sandbox

Run k3d (real K8s in containers) inside the sandbox VM. Boots in 30–60s. Fully isolated per candidate.

- ✅ Real `kubectl`, real K8s API, full feature set.
- ✅ Single-substrate story (everything lives in the sandbox).
- ✅ Per-candidate cluster, no shared cluster ops.
- ⚠️ Slightly slower cold-start than Compose-only stacks.
- ⚠️ Storage: k3d uses `local-path-provisioner`; PVCs live on the sandbox FS.

#### Option B — vCluster on a shared host cluster

Lightweight virtual Kubernetes clusters running on top of a single host cluster. Per-candidate cluster as a namespace + control plane pod. ~100 MB, boots in seconds.

- ✅ Lightweight, fast.
- ❌ Requires a shared K8s cluster (back to ops).
- ❌ Adds a control plane to maintain.

#### Option C — full hosted cluster per candidate (EKS Auto, GKE Autopilot)

Provision a real cluster per candidate.

- ❌ 3–5 minute provision time.
- ❌ Expensive at any volume.
- ❌ Overkill for assessment fidelity.

#### Recommendation: **Option A (k3d-in-sandbox)**

For the foreseeable future:

- Single substrate (sandbox is the unit, K8s tasks are just sandboxes with k3d preinstalled in the template).
- No shared cluster ops burden.
- Real K8s feel for candidates.
- Migration to Option B later is incremental if volume warrants.

#### Networking that "feels normal" for K8s

Sandbox template provisions a kubeconfig pointing at `https://localhost:6443` (the in-sandbox k3d apiserver). Candidate runs `kubectl get pods` in the in-sandbox terminal and it just works. For browser-based UI access to services running on the cluster:

```bash
kubectl port-forward svc/my-app 8080:80
# then sb.get_host(8080) → public HTTPS URL
```

The candidate's mental model is identical to a cloud K8s cluster.

### 12. Networking model — what "feels normal" to candidates

Three access modes:

#### Inside the sandbox (the default)

Localhost-everything. Compose services on a private Docker network. K8s services via cluster DNS or `kubectl port-forward`. This is how production looks in real life. Most candidates do everything from the in-sandbox terminal and never need anything else.

#### From candidate's laptop browser

Every meaningful HTTP/HTTPS port gets a public HTTPS URL via `sb.get_host(port)`:

```
FastAPI on :8000  →  https://8000-<sandbox-id>.e2b.dev
React on :3000    →  https://3000-<sandbox-id>.e2b.dev
```

The candidate clicks a link in the test UI (or follows a URL we render in the panel) and sees their app. This is the AWS-EC2-Session-Manager-but-better experience.

#### From candidate's laptop CLI (e.g., `psql -h <host> -p 5432`)

**PoC finding (Phase 1, validated empirically):** raw TCP exposure is **not supported** on hosted E2B. The `<port>-<id>.e2b.app` URL is hostname-routed but L7-terminated:

- The proxy listens only on TLS port 443 externally; the "5432-" prefix is a routing label, not a port forward.
- The proxy parses incoming requests as HTTP. PostgreSQL's binary StartupMessage is rejected as malformed, the connection drops.
- A `psql -h 5432-<id>.e2b.app -p 5432 ...` from a candidate's laptop times out at the proxy with no listener on :5432.

This applies to every binary-protocol service: Postgres, Redis, Kafka, MongoDB, raw gRPC, K8s API on :6443. The proxy *only* speaks HTTP/HTTPS (with WebSocket upgrade) — that's why ttyd, code-server, Flask, Jupyter all work.

The resolution is **per-stack web consoles baked into each template** (§13b) — Adminer for Postgres/MySQL, RedisInsight for Redis, kafka-ui for Kafka, K8s Dashboard for k3d, etc. Each is HTTP/HTTPS by design, ships inside the sandbox, connects to the service over localhost, and is reached from the candidate's laptop via `<port>-<id>.e2b.app`. The ecosystem already produces a canonical web GUI for every popular service we need to support, so this is a "ship the right tool" problem rather than a "build a generic bridge" problem.

Ranked workarounds for the few cases where a candidate genuinely needs their own laptop CLI tooling:

1. **Run DB / CLI tools inside the sandbox terminal.** Browser terminal (ttyd) is one click away; `psql -h localhost` / `redis-cli` / `kubectl` all work there. **Recommended default for assessments.**
2. **Use the per-stack web console.** Adminer / RedisInsight / etc. covers ~95% of "I want to look at the data" workflows from the candidate's browser, no install.
3. **WebSocket TCP tunnel** (`wstunnel` / `websocat`) installed in the template + a small client the candidate runs locally. Power-user opt-in. Skipped in Phase 1; revisit if usage data shows demand.

For K8s API access from laptop, same caveat applies: kubeconfig with `localhost:6443` works inside the sandbox; external access requires the in-sandbox terminal (k9s / kubectl) or the K8s Dashboard / Headlamp web UI.

### 13. Templates — one per stack, not per task

Target catalog (~6–8 templates total):

| Template | Stack | Sizing |
|---|---|---|
| `utkrusht-python-sql` | Python + Postgres (Compose) | small (2 vCPU / 2 GB) |
| `utkrusht-python-fastapi` | Python + FastAPI + Compose | small |
| `utkrusht-node-mongo` | Node + Mongo (Compose) | small |
| `utkrusht-node-postgres` | Node + Postgres (Compose) | small |
| `utkrusht-mern` | Mongo + Express + React + Node | medium (4 vCPU / 4 GB) |
| `utkrusht-react` | React frontend tasks | small |
| `utkrusht-java-spring` | Java + Spring Boot + DB | medium |
| `utkrusht-k8s-base` | k3d preinstalled + tooling | medium |

Each template is a Dockerfile + setup script, version-controlled in `e2b_flow/templates/`. CI rebuilds and registers on PR merge. New tech stack = new template + new prompt in `task_generation_prompts/`.

Templates are rebuilt rarely. Per-task generation produces files (`run.sh`, Compose, init SQL) that drop into the template at session start; templates do not need to know about individual tasks.

### 13b. Per-stack candidate consoles (the HTTPS-only workaround)

E2B's port forwarder accepts only HTTP/HTTPS — see §12 for the validated finding. To preserve a "look at the data from your browser" UX without building a generic TCP-to-HTTPS bridge, every template ships the canonical **web GUI** for the service under test. Each is a mature, free, browser-based tool that already speaks HTTP and connects to its service over localhost inside the sandbox.

This is a clean answer because for every popular TCP service, the ecosystem already maintains the right tool — we adopt rather than build.

Standardised template surfaces (universal across all stacks):

| Surface | Port | Tool | Purpose |
|---|---|---|---|
| Browser terminal | 7681 | `ttyd` | Root bash shell in the browser; the EC2-Session-Manager analog. |
| Browser IDE | 8443 | `code-server` | VS Code in browser, file edit + integrated terminal. |
| Service preview | task-defined | (the candidate's app) | The HTTP service the candidate is building / fixing. |

Stack-specific consoles (one per template):

| Stack | Service protocol | Console | Port | Notes |
|---|---|---|---|---|
| Postgres / MySQL / MariaDB | binary | **Adminer** | 8080 | Single-PHP-file multi-DB GUI. Phase 1 PoC default. |
| Redis | RESP | **RedisInsight** (Redis Inc.) | 5540 | Connection form + key browser + CLI panel + slowlog. |
| MongoDB | BSON | **mongo-express** | 8081 | Collection browser + query UI. |
| Kafka | binary | **kafka-ui** (Provectus) or **AKHQ** | 8080 | Topic browser, message tail, consumer-group lag. |
| RabbitMQ | AMQP | **built-in management plugin** | 15672 | Ships with RabbitMQ; just enable. |
| Elasticsearch / OpenSearch | already HTTP | n/a — direct via `get_host(9200)` | 9200 | Proxy passes through natively. |
| Docker (host-level) | sock | **Portainer** | 9000 | Visual `docker ps` / logs / exec. |
| Kubernetes (k3d-in-sandbox) | HTTPS API w/ certs | **Kubernetes Dashboard** or **Headlamp** | 8001 / 4466 | Dashboard is the official one; Headlamp is faster. Pair with `k9s` inside ttyd. |
| gRPC services | HTTP/2 | **grpcui** | 8080 | Reflective web UI for gRPC services. |

Implications for templates:

- Each `templates/<stack>/` ships its console inside `start.sh` (or `template.py`'s `run_cmd` chain). No central bridge to maintain.
- Console connects to the service over `localhost` inside the sandbox; the candidate's compose file is responsible for mapping the service port to host (which our task generators already do for Postgres / Redis / etc.).
- New stack = new template + pick the canonical tool + add to `start.sh`.
- Probe ports list (`DEFAULT_PROBE_PORTS` in `e2b_flow/sandbox_manager.py`) includes the console port so deploy output surfaces it automatically. Eventually replaced by `tasks.expected_ports` (§20) at the per-task level.

Open questions / deferred:

- **Power-user opt-in for laptop tooling** (DBeaver / Lens / etc.). WebSocket TCP tunnel via `wstunnel`-class tools. Not in Phase 1; revisit if telemetry shows the in-sandbox + web-console combo is insufficient.
- **Console auth.** All consoles run unauthenticated for the PoC because the sandbox's E2B-issued URL is the security boundary. Production layering: per-session token in front of each console (Phase 3, §22).

---

## Part 3 — Candidate interaction surfaces

### 14. Interaction modes available

Six surfaces, layered on top of the sandbox:

1. **Web terminal (default).** An iframe of the sandbox's xterm-style web terminal. One click from the test UI. Most candidates do everything here.
2. **Web code editor.** VS Code in browser via `code-server` (or E2B's code-interpreter mode). Files in the sandbox FS edited live; the editor's terminal panel and the standalone terminal share the sandbox. Replaces "candidate clones repo locally."
3. **Local terminal SSH (opt-in).** `e2b sandbox ssh <sandbox_id>` for power users who prefer their own editor (Vim, JetBrains, Neovim setups). Requires the candidate install the E2B CLI — friction. Make it optional.
4. **Service preview URL.** `sb.get_host(<port>)` exposes a service the candidate is running. Embedded as a panel in the test UI. They click to see their app.
5. **Embedded admin consoles.** For DB tasks, ship Adminer / pgAdmin in the template on a side port; "Open DB console" tab. For K8s, ship the Kubernetes Dashboard or k9s-in-a-web-shell. Optional per template, makes inspection easier for non-CLI-native candidates.
6. **Programmatic CLIs** (`kubectl`, `psql`, `redis-cli`, `mongosh`). Preinstalled in templates; available in any terminal mode.

### 15. Recommended default candidate UX

A tabbed/split layout in the test UI:

```
┌──────────────────────────────────────────────────────────┐
│  Task: Fix the slow query on `orders` table             │
│  ⏱ 1h 47m left   ⏸ Pause for break   ✅ Submit         │
├───────────┬───────────┬───────────────┬──────────────────┤
│  Terminal │  Editor   │  App Preview  │  DB Console     │
├───────────┴───────────┴───────────────┴──────────────────┤
│                                                           │
│  $ psql -h localhost -U postgres                         │
│  postgres=# \dt                                          │
│   ...                                                     │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

- **Terminal**: the workhorse.
- **Editor**: file edits with live save.
- **App preview**: only shown if the task exposes a UI port.
- **DB / K8s console**: only shown for relevant templates.
- **Submit**: freezes state, snapshots, kills sandbox.
- **Pause for break**: explicit pause; resume preserves everything.
- **Heartbeat**: while the tab is visible, the frontend pings backend every 30s. Heartbeat stops → backend pauses sandbox at +5min, kills at +30min. Tunable.

### 16. Comparison to the AWS EC2 console mental model

Candidates familiar with cloud UIs already know this pattern:

- AWS console → click EC2 instance → "Connect" → Session Manager terminal in browser.
- GCP console → click VM → "SSH" → terminal in browser.
- Our test UI → click "Start task" → terminal + editor + preview tabs.

For candidates new to cloud: this is *easier* than today's flow because there's no SSH key juggling, no local Docker install, no "works on my machine" disputes. Everyone gets the same environment.

---

## Part 4 — Frontend changes

### 17. `utkrushta-assessment` (candidate frontend, port 3001)

The candidate-facing app. Stack per parent CLAUDE: Next.js, pnpm, custom JWT, SWR, Zustand. Architecture: directory-based.

**New components:**

| Component | Responsibility |
|---|---|
| `<SandboxTerminalPanel>` | iframe wrapper around sandbox terminal URL; reconnect on socket drop |
| `<SandboxEditorPanel>` | iframe wrapper for VS Code-in-browser; persists open files in Zustand |
| `<SandboxPreviewPanel>` | iframe for exposed service URL; "open in new tab" affordance |
| `<SandboxConsolePanel>` | generic panel for DB / K8s consoles |
| `<SandboxStatusBar>` | sandbox state (active / paused / expiring soon), heartbeat indicator, time remaining |
| `<SandboxLayout>` | orchestrates which panels to render based on the manifest from backend |

**New hooks / state:**

- `useSandboxSession(taskId)` — built on SWR. Lifecycle: `start session → poll URLs → maintain heartbeat → submit/end`.
- Heartbeat: `POST /sessions/<id>/heartbeat` every 30s while the page is visible. Pauses on tab blur > 5 min → triggers backend pause.
- Zustand store: open files, terminal scrollback (optional), last seen URLs.

**Routing:**

The existing test-taking route gains a `/sandbox` mode that renders `<SandboxLayout>` instead of the legacy view.

**Backwards compat (during migration):**

The route inspects `deployment_method` from the session response:

- `droplet` → render the legacy view (existing UI showing droplet IP / SSH key).
- `e2b_sandbox` → render `<SandboxLayout>`.

Single route, two render paths. The legacy path is removed once all task templates exist and old in-flight sessions drain.

### 18. `recruiter-utkrusht` (recruiter frontend, port 3000)

Smaller change. Recruiters need:

- A **"Preview as candidate"** button that spins up a sandbox via the same backend endpoint but flagged as preview (no scoring, shorter idle-timeout).
- In task management UI, show the `template_id` field and a **"Test deploy"** button that triggers the admin path (used for verifying new templates / new tasks before assigning).
- No deeper architectural change.

### 19. What candidates lose / gain

| | Lose | Gain |
|---|---|---|
| Local environment control | Can't run on own laptop with own tools by default | Zero local setup; no Docker / Postgres / Node install |
| Editor preference | VS Code-in-browser is the default | SSH opt-in restores own-editor workflow |
| Network model | Direct droplet IP gone | Public HTTPS URLs for services; same UX as cloud |
| Persistence | (unchanged) | Pause/resume preserves state without losing work |
| Reliability | (unchanged) | Identical environment for everyone; no "works on my machine" |

The default UX is strictly better for candidates who don't have a strong local setup. Power-users can SSH if they want. Net positive.

---

## Part 5 — Backend & state changes

### 20. Supabase schema

**`tasks` table — minimal additions:**

| Column | Type | Purpose |
|---|---|---|
| `template_id` | text, nullable | Sandbox template name (e.g. `utkrusht-python-sql`). NULL = legacy droplet flow. |
| `default_sandbox_size` | text | `small` / `medium` / `large`; informs CPU/RAM at create time |
| `expected_ports` | JSON array | `[{port: 5432, label: "postgres", public: false}, {port: 8000, label: "api", public: true}]`. Tells the frontend which panels to render. |

The existing `is_deployed` + `deployment_info` fields apply only to admin/test deploys (engineering verification), not candidate sessions. Mentally rename to `is_admin_deployed`.

**New `sandbox_sessions` table** — separates "task definition" from "candidate session instance":

```sql
CREATE TABLE sandbox_sessions (
  session_id            UUID PRIMARY KEY,
  task_id               UUID REFERENCES tasks(task_id),
  candidate_id          UUID REFERENCES candidates(id) NULL,  -- null for admin/preview
  sandbox_id            TEXT NOT NULL,          -- E2B handle, source of truth
  template_id           TEXT NOT NULL,
  status                TEXT NOT NULL,          -- provisioning|active|paused|killed|expired|failed
  interaction_surfaces  JSONB,                  -- {terminal_url, editor_url, ports:[...], ssh:{...}}
  idle_timeout_seconds  INT DEFAULT 7200,
  created_at            TIMESTAMPTZ DEFAULT now(),
  last_heartbeat        TIMESTAMPTZ,
  paused_at             TIMESTAMPTZ NULL,
  killed_at             TIMESTAMPTZ NULL,
  snapshot_uri          TEXT NULL,              -- S3 path of pre-kill snapshot for grading
  deployment_method     TEXT DEFAULT 'e2b_sandbox'
);

CREATE INDEX idx_sandbox_sessions_status     ON sandbox_sessions(status);
CREATE INDEX idx_sandbox_sessions_task_id    ON sandbox_sessions(task_id);
CREATE INDEX idx_sandbox_sessions_heartbeat  ON sandbox_sessions(last_heartbeat) WHERE status IN ('active','paused');
```

**Why a separate table:**

Today, "task is deployed" and "candidate has a working environment" are conflated 1:1. They aren't. A task definition is shared across many candidates; a session is per-attempt. The new model makes this explicit and supports re-attempts cleanly. Multiple candidates can have sessions for the same task simultaneously — impossible under today's droplet pool.

**Migration:**

- Phase 2: legacy droplet deploys remain on `tasks.is_deployed` / `deployment_info`. New flow uses `sandbox_sessions`.
- Phase 5: collapse droplet flow into `sandbox_sessions` (or remove entirely).

### 21. Backend — `utkrushta-backend` (FastAPI :9000)

**New endpoints:**

| Endpoint | Body | Behavior |
|---|---|---|
| `POST /sessions/start` | `{task_id, candidate_id?}` | Look up template, call E2B SDK, run task setup, insert row. Returns `{session_id, interaction_surfaces, expires_at}`. |
| `POST /sessions/{id}/heartbeat` | `{}` | Bumps `last_heartbeat`. If sandbox was paused, resumes it. |
| `POST /sessions/{id}/pause` | `{}` | Explicit pause (candidate clicks "take a break"). |
| `POST /sessions/{id}/submit` | `{}` | Run grading hooks (`pg_dump` to S3, capture file diffs), kill sandbox, mark `killed`, return grading result handle. |
| `POST /sessions/{id}/end` | `{}` | Explicit kill without grading (candidate cancels). |
| `GET /sessions/{id}` | — | Current state, refreshed URLs (URLs may rotate after resume). |

**Background reconciler** (new, runs every 60s):

```
for sandbox in e2b.list():
    if not session_row_exists(sandbox.id):
        sandbox.kill()                         # orphan: kill
        log("orphan sandbox killed", id=sandbox.id)

for session in sessions_where(status in ['provisioning','active','paused']):
    sandbox = e2b.get(session.sandbox_id)
    if sandbox is None:
        mark_session(session, 'expired')       # gone from E2B
        continue
    if session.status == 'paused' and now() > session.paused_at + GRACE:
        sandbox.kill()
        mark_session(session, 'expired')
    if session.status == 'active' and now() > session.last_heartbeat + IDLE:
        sandbox.pause()
        mark_session(session, 'paused')
```

This is the safety net. Even if every other layer mis-reports state, the reconciler converges within 60s.

**Auth/ACL:**

- Session endpoints require either candidate JWT (existing `utkrushta-assessment` auth) or recruiter JWT (preview mode).
- Sandbox URLs are signed/scoped — only the assigned candidate can access. E2B supports access tokens per sandbox; surface those in interaction URLs, never expose the org-level API key to the frontend.

### 22. Secrets and credentials

- `E2B_API_KEY` lives in backend env, never reaches the frontend.
- The candidate's frontend gets *signed iframe URLs* (E2B sandbox-scoped tokens), not the raw key.
- For SSH access (opt-in), backend generates a per-session keypair, returns the private key to the candidate once (download), public key injected into the sandbox at boot via the SDK.
- Snapshot uploads to S3 use a backend-only IAM role; the frontend never touches S3 directly.
- **Per-attempt GitHub credentials** (deploy key + fine-grained PAT) are scoped to a single attempt repo, encrypted at rest in Supabase, and revoked at submit time (§22a).

### 22a. Candidate repo & GitHub auth model

#### Why per-attempt repos

Today's PoC clones the canonical template repo (`UtkrushtApps/<task>-template`) directly using an org-level token injected into the clone URL, then scrubs the token from `.git/config`. Push fails-auth because no credential remains. This is the right security posture for engineering deploys but wrong for candidates because:

1. The candidate's `git remote -v` reveals the template path (`UtkrushtApps/...`), leaking ownership.
2. Their work doesn't survive sandbox death — there's no canonical artifact.
3. We have no grading-ready snapshot tied to a specific attempt.
4. The candidate can't take their work with them as a portfolio piece.

The fix: **provision a fresh, per-attempt repo at task start.** It exists for exactly one candidate's attempt at exactly one task. Fully isolated.

#### Repo provisioning

For each attempt, backend creates a fresh repo via GitHub's **template repository** feature:

```
gh repo create UtkrushtAttempts/<candidate-id>-<task-slug>-<attempt-id> \
   --private \
   --template UtkrushtApps/<task>-template
```

Why "template repository" rather than fork:

- No fork relationship → no "forked from UtkrushtApps/..." badge → no upstream visibility.
- Clean independent ownership → can be transferred to a candidate cleanly.
- Forks of private repos in GitHub orgs have policy edge cases; templates are policy-clean.

The source repo (`UtkrushtApps/<task>-template`) must be flagged as a "template repository" once in repo settings.

Naming convention: `UtkrushtAttempts/<candidate-id>-<task-slug>-<attempt-id>` (private, kept in a dedicated `UtkrushtAttempts` org separate from the templates org `UtkrushtApps`).

#### Auth model — Option 2 (chosen): read+write at both surfaces

Two credentials are minted per attempt, each scoped to that one repo:

| Credential | Lives where | Permission | Used for |
|---|---|---|---|
| **SSH keypair (Ed25519)** | Private key written to `/root/.ssh/id_ed25519` inside the sandbox; public key registered as a deploy key on the attempt repo (`read_only=false`) | Read + **write** | Sandbox `git clone` + `git push` (transparent — `git push` "just works" inside the terminal/IDE) |
| **Fine-grained PAT** scoped to the attempt repo | Surfaced to candidate via the test UI as a one-line clone command | Read + **write** | Laptop `git clone https://x-access-token:gho_<...>@github.com/UtkrushtAttempts/<id>.git` and any subsequent push from laptop |

**Neither credential is tied to a GitHub user account.** The candidate never logs into GitHub, never accepts a collaborator invite, never even discovers GitHub is involved unless they want to.

Key candidate-experience consequences:

- The sandbox is one valid work surface among multiple, not the only one. They can do the entire task from their laptop with their own IDE, push from their laptop, and never open the sandbox terminal — and that's an explicit allowed outcome.
- Where the assessment requires "we know they used the sandbox" (proctored mode, traffic-gen integrations, behavioural signals), Option 1 is the alternative — laptop credential downgraded to read-only PAT. Same backend code, flag at task or assessment level.

| | Option 1 (laptop read-only) | **Option 2 (laptop read+write — default)** |
|---|---|---|
| Sandbox push | yes | yes |
| Laptop push | no — token is read-only | **yes** |
| Audit trail of "candidate used the sandbox" | strong | weak (final code only) |
| Candidate flexibility | constrained to sandbox tooling | unconstrained |
| Default for | proctored / behavioural-signal-heavy assessments | code-quality-only assessments |

Sandbox-only (Option 1) becomes a *vector* for harder/proctored variants of the same task — the candidate is forced to do everything in the sandbox, and that itself is the stricter test of skill.

#### End-to-end flow

```python
# Task assignment time (backend; no candidate interaction)
priv_key, pub_key = ssh_keygen_ed25519()
attempt_repo = gh.create_repo_from_template(
    template="UtkrushtApps/fintech-spend-summary-optimizer",
    target_org="UtkrushtAttempts",
    target_name=f"{candidate_id}-fintech-spend-summary-{attempt_id}",
    private=True,
)
deploy_key = gh.add_deploy_key(
    repo=attempt_repo.full_name,
    title=f"sandbox-attempt-{attempt_id}",
    key=pub_key,
    read_only=False,                       # Option 2: write
)
laptop_pat = gh.create_fine_grained_pat(
    repos=[attempt_repo.full_name],
    permissions={"contents": "write"},     # Option 2: write
    expires_at=now() + 30.days,
)
attempts.insert(
    attempt_id, repo_full_name, ssh_clone_url,
    encrypted_priv_key, deploy_key_id,
    encrypted_laptop_pat, pat_id,
)

# Sandbox start time (sandbox_manager.create_and_setup, modified)
sb.commands.run(f"""
mkdir -p /root/.ssh
cat > /root/.ssh/id_ed25519 <<'EOF'
{priv_key}
EOF
chmod 600 /root/.ssh/id_ed25519
ssh-keyscan github.com >> /root/.ssh/known_hosts
""")
sb.commands.run(f"git clone {ssh_clone_url} /home/user/task")
sb.commands.run("""
cd /home/user/task &&
git config user.name "Candidate" &&
git config user.email "candidate-{attempt_id}@utkrusht.ai"
""")

# Candidate UX (in the test UI)
# ─────────────────────────────────────────────────────────────────
# Your task repository:
#   In the sandbox terminal:   /home/user/task   (already cloned)
#   On your laptop:            git clone https://x-access-token:gho_<…>@github.com/UtkrushtAttempts/<id>.git task
# ─────────────────────────────────────────────────────────────────

# Submit time
final_sha = sb.commands.run("cd /home/user/task && git rev-parse HEAD").stdout.strip()
attempts.update(attempt_id, final_sha=final_sha, status='submitted')
gh.delete_deploy_key(repo=attempt_repo.full_name, key_id=deploy_key.id)
gh.delete_fine_grained_pat(pat_id=laptop_pat.id)
sb.kill()
# Sandbox dies; both credentials revoked; repo lives on as the grading artifact.

# Optional: candidate provides their GitHub username post-submit
gh.transfer_repo(repo=attempt_repo.full_name, new_owner=candidate_github_username)
# Repo moves to the candidate's account; we lose admin (intentional).
# Candidate now owns the repo permanently as a portfolio piece.
```

#### Security model

- **Per-attempt isolation.** Fresh keypair + fresh PAT per attempt. No shared credentials, no cross-attempt blast radius.
- **Both credentials revoked at submit.** Even if a candidate exfiltrated the SSH key from `/root/.ssh/id_ed25519` (they have root inside the sandbox, so they can), the deploy key entry is deleted on GitHub and the leaked key becomes inert.
- **Credentials scoped to the one attempt repo.** Neither has org admin, access to other attempts, or access to the templates org.
- **No long-lived org-level token in the sandbox.** Improvement over the PoC's `GITHUB_UTKRUSHTAPPS_TOKEN` clone-URL injection.
- **Post-submit transfer.** Ownership moves; we lose admin. We may keep a fork of submitted attempts in `UtkrushtAttempts` (or an `UtkrushtArchive` org) as a long-term grading artifact if compliance / re-grading needs it.
- **Commit identity.** Default `user.email = candidate-<attempt>@utkrusht.ai`. No PII in the commit graph. Candidates who want their real identity on the history can `git filter-repo` after transfer.

#### Backend surface needed (Phase 2)

- A separate GitHub org (`UtkrushtAttempts`) for attempt repos.
- A bot account (or GitHub App) with `repo` + `admin:org` on that org. GitHub App is the longer-term right answer; bot PAT is fine to start.
- New helper module (`github_attempts.py` in `utkrushta-backend`):
  - `provision_attempt(task_id, candidate_id) -> AttemptHandle`
  - `revoke_attempt_credentials(attempt_id)`
  - `transfer_attempt_to_user(attempt_id, github_username)`
- Schema additions to `sandbox_sessions` (or sister `attempts` table):
  - `repo_full_name TEXT`, `ssh_clone_url TEXT`, `https_clone_url TEXT`
  - `deploy_key_id BIGINT`, `pat_id BIGINT` (GitHub IDs, for revocation)
  - `encrypted_ssh_priv_key TEXT`, `encrypted_laptop_pat TEXT`
  - `credentials_revoked_at TIMESTAMPTZ NULL`
  - `transferred_to_github_username TEXT NULL`, `transferred_at TIMESTAMPTZ NULL`
- Modify the candidate-facing equivalent of `e2b_flow deploy-task` to take an `attempt_id`, inject the SSH key, and use the SSH clone URL.

#### What changes in `utkrusht-task` (this repo)

- The current `e2b_flow deploy-task` HTTPS+org-token clone path stays as the **engineering verification path** — useful for template debugging without provisioning attempts. Same as today.
- Candidate-flow code (Phase 2) lives backend-side, not in this repo. The CLI here is operator tooling, not candidate tooling.

#### Subtleties

- Template-vs-fork distinction is load-bearing: GitHub's "template repository" feature is what gives clean, transferable copies. Forks would carry the upstream relationship.
- Fine-grained PATs have a 1-year max lifetime; we revoke at submit so this doesn't matter. GitHub Apps with installation tokens are cleaner long-term but installation tokens expire in 1 hour, awkward for the "show clone URL once at session start" UX.
- Multi-machine concern: with both credentials write, a candidate can clone+push from any number of laptops. That's a feature for Option 2 (their attempt, their work, their device). Revoke at submit closes the window.
- If the candidate edits on laptop and we want it to land in the sandbox: they push from laptop, the sandbox can `git pull` to sync. Bidirectional sync is naturally supported.

### 23. Changes to the deployment process (this repo, `utkrusht-task`)

- `multiagent.py generate-tasks` continues to generate `run.sh`, `kill.sh`, Compose files, init SQL — **same task content**.
- **New step in generation:** emit `template_id`, `expected_ports`, and `default_sandbox_size` into the `tasks` row at creation time.
- **No more deploy-on-generation:** the generation step does not call `deploy_task_impl`. Tasks are deployed *per session* by the backend, not pre-deployed. **This eliminates the "occupied droplet" problem at the source — there's no persistent deployment to occupy.**
- **Admin / manual deploys** (this PoC's CLI) are kept for engineering verification: `python -m e2b_flow deploy-task --task-id ...`. Useful for debugging templates and validating new tasks. Not the candidate path.
- **Template management** lives here: `e2b_flow/templates/<stack>/` with a CI workflow that rebuilds and registers templates on PR merge. New tech stack = new template + new prompt in `task_generation_prompts/`.

### 24. End-to-end flow (full implementation, post-PoC)

```
[Recruiter creates test, picks tasks]
       │
       ▼
[Candidate starts test in utkrushta-assessment]
       │
       ▼
Frontend → POST /sessions/start (utkrushta-backend)
       │
       ▼
Backend looks up tasks.template_id, calls E2B SDK:
  • Sandbox.create(template, timeout=2h)
  • git clone task repo into sandbox
  • bash run.sh
  • probe expected_ports, collect URLs
  • insert sandbox_sessions row (status=active)
       │
       ▼
Returns { session_id, interaction_surfaces } to frontend
       │
       ▼
Frontend renders <SandboxLayout> (terminal / editor / preview tabs)
Heartbeat every 30s while tab visible
       │
       ▼
[Candidate works on the task; may pause/resume]
       │
       ▼
Candidate clicks Submit
       │
       ▼
Backend:
  • Run task-defined grading hooks inside sandbox
  • Snapshot relevant state to S3 (DB dump, file diffs)
  • sandbox.kill()
  • Update sandbox_sessions.status = killed, store snapshot_uri
  • Trigger downstream grading pipeline
       │
       ▼
Frontend shows submission confirmation
```

### 25. Reconciliation matrix — failure modes & recovery

| Failure | Symptom | Recovery |
|---|---|---|
| Frontend crashes mid-test | Heartbeat stops | Backend reconciler pauses at +5min, kills at +30min. Candidate can resume within the pause window. |
| Backend crashes | Sandboxes keep running on E2B | On recovery, reconciler reads E2B state and rebuilds session rows. No data loss. |
| E2B outage | Existing paused sessions inaccessible | New sessions queued or fall back to legacy droplet path during transition window. (Phase 5+: alternate provider or self-hosted Infra.) |
| Sandbox boot fails | `provisioning` row, no usable URLs | Backend retries with exponential backoff (2x), then surfaces error to frontend with "regenerate environment" button. |
| Idle-timeout fires mid-test | Sandbox killed unexpectedly | Re-create + replay grading-relevant state from snapshot. Edge case; mitigated by tuning heartbeat + pause grace. |
| Candidate browser disconnects briefly | Heartbeat blip | No-op; heartbeat resumes when reconnected. |

The reconciler is the load-bearing piece. Everything else is best-effort; the reconciler converges to truth within 60s.

---

## Part 6 — Implementation phasing & risks

### 26. Implementation phases

| Phase | Scope | Surface area |
|---|---|---|
| **1 (this PoC)** | Hosted E2B; single template (`python-sql`); CLI-driven deploy/reset; manual verification | `utkrusht-task` repo only (`e2b_flow/`); no FE/BE changes |
| 2 | Backend integration: `sandbox_sessions` table, `/sessions/*` endpoints, reconciler. Tested via API calls. | `utkrushta-backend` |
| 3 | Frontend integration: `<SandboxLayout>` and friends, behind a feature flag, on a single template type. | `utkrushta-assessment` |
| 4 | Template expansion: 6–8 templates total. Migrate task generation to emit `template_id`. Sandbox flow alongside legacy droplets. | `utkrusht-task`, `utkrushta-backend` |
| 5 | Decommission droplets. Remove `multiagent.py deploy-task` / `reset-task` and the droplet pool. | All repos |
| 6 (optional) | Self-host `e2b-dev/infra` on Hetzner if volume justifies (~1500–2500 sandbox-hrs/mo). | Infra |

### 27. Parallel workstream: task idempotence

Independent of infra choice; *enabled* by it but not solved by it.

- `run.sh` and `kill.sh` should be re-runnable on partial state — no errors on second invocation.
- Compose project names should include a unique session ID (`COMPOSE_PROJECT_NAME=task-${SESSION_ID}`) so concurrent re-runs never collide. Default Compose uses the directory name, which collides.
- Redeploy on partial state should converge, not fail.

This is task-content work, tracked separately. The doc flags it; the PoC does not change task generation.

### 28. Cost analysis

#### Hosted (per-session, ballpark)

For a typical 2 vCPU / 2–4 GB sandbox running 1–2 hours, ~5 GB disk:

| Platform | Pricing model | Per 2h session | Free tier | Notes |
|---|---|---|---|---|
| **E2B** | ~$0.000014/vCPU·s + $0.0000045/GB·s | ~$0.20–0.50 | ~100 hrs/mo | Cleanest sandbox SDK; Firecracker |
| **Daytona Cloud** | Per-hour, tiered | ~$0.10–0.30 / hr | Limited | Workspace-flavored, moving toward sandbox API |
| **Modal Sandboxes** | ~$0.000038/CPU·s + memory | ~$0.30–0.60 | $30/mo credits | Python-first SDK |
| **Northflank Sandboxes** | Per-resource per-hour | ~$0.08–0.20 / hr | Limited | Newer; integrates with broader platform |
| **Codesandbox SDK** | Per-VM-hour | ~$0.05–0.15 / hr | Limited | Dev-environment-focused |

**Back-of-envelope monthly cost:**

| Volume (sessions/mo, 2h each) | Total sandbox-hours | E2B (high) | Daytona / NF |
|---|---|---|---|
| 500 | 1000 | ~$200–500 | ~$100–300 |
| 2000 | 4000 | ~$800–2000 | ~$400–1200 |
| 10000 | 20000 | ~$4000–10000 | ~$2000–6000 |

#### Self-hosting (Phase 6)

`e2b-dev/infra` on Hetzner bare-metal (`AX52`, ~€60/month, 16-core Ryzen, 64 GB RAM, NVMe, **nested-virt-capable**):

- One box comfortably hosts 30–60 concurrent sandboxes at our sizing.
- Two boxes + a small control-plane VM ≈ **€150–200/month** all-in.
- Capacity: thousands of sessions/month.

**Break-even: ~1500–2500 sandbox-hours/month.** Below that, hosted wins. Above that, self-host pays for itself in 1–2 months.

**Engineering cost** to set up `e2b-dev/infra`: realistically **2–4 weeks of focused work** (Nomad + Consul + Firecracker + networking + monitoring), plus ~5–10% of someone's time ongoing. Daytona OSS self-host is lighter: ~1–2 weeks.

### 29. Open risks

| Risk | Mitigation |
|---|---|
| ~~**DinD per template**~~ — `docker compose up` inside a Firecracker microVM may have edge cases | **Resolved (Phase 1 PoC):** validated end-to-end with `python-sql` template — image pull, network create, volume create, container start, postgres init SQL all clean. Re-verify per new template as catalog grows. |
| ~~**Raw TCP exposure**~~ for Postgres/Redis from candidate's laptop | **Resolved (Phase 1 PoC, validated empirically):** not supported on hosted E2B. The `<port>-<id>.e2b.app` URL is L7-terminated HTTPS-only on :443. **Mitigation:** per-stack web consoles baked into each template (§13b), in-sandbox terminal `psql`/`redis-cli`/etc. as default, WebSocket TCP tunnel as deferred power-user opt-in. |
| **Idle-timeout tuning** | Empirical; instrument heartbeat + pause/grace and adjust |
| **Vendor coupling** | `e2b-dev/infra` (Apache 2.0) is the escape valve; Daytona OSS is a second option |
| **Observability shift** | `ssh + docker logs` becomes SDK calls; build a small support-debug tool that wraps `sandbox.commands.run("docker logs ...")` for ops |
| **Snapshot reliability for grading** | Test snapshot-then-kill with intentional failures; ensure grading pipeline handles missing snapshots gracefully |
| **Security model for candidate-exposed URLs** | Use sandbox-scoped tokens, never raw API keys; audit URL exposure during Phase 3 |
| **No audit trail post-sandbox-death** (Phase 1 PoC finding) | Today, when a sandbox dies its filesystem + DB state + commit graph are gone with the microVM. Phase 2 adds: (i) per-attempt repo retains the candidate's commit history (§22a), (ii) pre-kill `pg_dump` + `git diff` snapshot to S3 referenced from `sandbox_sessions.snapshot_uri` (§20–§21). Without these, the only persistent state is the Supabase row + local CLI logs. |
| **Sandbox idempotence on redeploy** (PoC finding) | Today, redeploying without first calling `reset-task` orphans the prior sandbox until idle-timeout fires. Phase 2 fix: at `deploy`, look up any existing `e2b_sandbox` recorded for the attempt and `kill()` it before creating the new one. |
| **Per-stack web console auth** | All consoles ship unauthenticated in Phase 1 (sandbox URL is the security boundary). Phase 3: front-end with per-session token / OAuth-proxy / E2B sandbox-scoped tokens before opening to real candidates. |

---

## Appendix A — Translation example: a Python+SQL task

A typical SQL/Python+SQL task has this shape (per `task_generation_prompts/Basic/SQL_basic_prompt.py`):

```
task_repo/
├── docker-compose.yml      # Postgres only, hardcoded creds
├── init_database.sql       # schema + seed
├── run.sh                  # docker compose up -d; wait for ready
├── kill.sh                 # compose down -v; rm -rf /root/task
└── (Python+SQL flavor adds: requirements.txt, main.py, README.md)
```

### Today (droplet)

```
[deploy CLI]
  multiagent.py deploy-task --task-id X
   │
   ├─ Supabase: lookup repo_url
   ├─ select_best_droplet_ip()  ← polls AVAILABLE_IPS, counts docker ps
   ├─ git clone <repo> /tmp/temp_deploy_X
   ├─ SFTP upload to /root/task on droplet (~5–15s)
   ├─ ssh: chmod +x *.sh
   ├─ ssh: bash /root/task/run.sh   (~30–60s for compose up + DB ready)
   └─ Supabase: is_deployed=true, droplet_ip=...

Total: ~60–90s, 5 sources of truth, manual pool management.
```

### With E2B (as actually implemented in Phase 1 PoC)

```python
def deploy_task(task_id):
    repo_url = supabase.get_repo_url(task_id)
    template = supabase.get_template_for(task_id)   # "utkrusht-python-sql"

    sb = Sandbox.create(template=template, timeout=2*3600)
    sb.commands.run(f"git clone {repo_url} /home/user/task")
    sb.commands.run("cd /home/user/task && bash run.sh", timeout=180)

    # Candidate-facing surfaces — all auto-baked into the template, all
    # HTTPS-fronted by E2B's port forwarder, all reached as iframe-able URLs:
    surfaces = {
        "terminal":   f"https://7681-{sb.sandbox_id}.e2b.app",   # ttyd
        "editor":     f"https://8443-{sb.sandbox_id}.e2b.app",   # code-server
        "db_console": f"https://8080-{sb.sandbox_id}.e2b.app",   # Adminer
        "app":        f"https://5000-{sb.sandbox_id}.e2b.app",   # candidate's Flask app
    }
    # Note: no `sb.get_terminal_url()` — the v2 SDK doesn't ship a built-in
    # web terminal URL; we run our own ttyd inside the template (§13b).

    supabase.mark_deployed(task_id, sandbox_id=sb.sandbox_id, urls=surfaces)
    return {"sandbox_id": sb.sandbox_id, "urls": surfaces}

def reset_task(task_id):
    sb = Sandbox.connect(supabase.get_sandbox_id(task_id))
    sb.kill()                              # atomic
    supabase.mark_undeployed(task_id)
```

**Measured cold start (PoC, python-sql, fintech-spend-summary task): ~25–35s end-to-end.** Breakdown: sandbox boot 1–2s, `git clone` 2–5s, `bash run.sh` (which does `docker pull postgres:15` + `compose up` + 159k-row seed via `psql -f`) 20–25s. Comparable to the droplet baseline despite spinning a fresh microVM each time.

**Teardown: ~1s** (`sb.kill()`).

**No pool. No SFTP. No SSH from our side. No `kill.sh` scripting.** `run.sh` and `kill.sh` content from the existing droplet flow ports unchanged — the sandbox is a Linux box.

When the candidate walks away: idle-timeout fires → sandbox auto-destroys. No orphan, no human cleanup. The droplet flow's signature failure mode does not exist here.

---

## Appendix B — References

- `e2b-dev/infra` (self-host runtime, Apache 2.0): https://github.com/e2b-dev/infra
- `daytonaio/daytona` (OSS sandbox + workspace platform): https://github.com/daytonaio/daytona
- `coder/coder` (OSS workspace platform): https://github.com/coder/coder
- E2B docs: https://e2b.dev/docs
- Fly Machines: https://fly.io/docs/machines/
- Kata Containers: https://katacontainers.io
- vCluster: https://www.vcluster.com/
- k3d: https://k3d.io

---

## Appendix C — Phase 1 PoC: implementation tidbits

Things we learned the hard way during the PoC build. Captured here so future-us doesn't relearn them.

### Base image is Python 3.13, not 3.11

`e2bdev/code-interpreter:latest` ships Python 3.13. Our original PoC tried to install 3.11 via `uv` because legacy droplet tasks pinned `psycopg2-binary==2.9.9`, which has no 3.13 wheel and won't compile against 3.13's headers (the `_PyInterpreterState_Get` symbol moved). The 3.11 layer hit several sharp edges:

- Debian trixie doesn't ship `python3.11` in apt → forced to use `uv` standalone CPython.
- uv's standalone Python carries an `EXTERNALLY-MANAGED` (PEP 668) marker that blocks `pip install`. Deleting it via `find` is fragile because the file location varies by uv version.
- `ln -sfn /usr/local/bin/pip /usr/local/bin/pip3` fails with `"are the same file"` when `pip3` is already a symlink to `pip` in the base image. GNU `ln` refuses even with `-f`.

**Simplification:** drop the 3.11 layer entirely; use base 3.13 directly. New tasks pin `psycopg2-binary>=2.9.10` (3.13 wheels). Existing droplet-era tasks need a one-line bump per task repo. We bumped the PoC's task repo (`UtkrushtApps/fintech-spend-summary-optimizer`) as part of the work.

### Pinned versions for supply-chain hygiene

Avoid `:latest` and `curl … | sh` in template build steps — both are mutable/opaque and fail review. Pin to specific release tags, fetched as concrete files:

- `ttyd@1.7.7` from `tsl0922/ttyd` GitHub releases (`ttyd.x86_64` static binary)
- `code-server@v4.96.4` as `code-server_4.96.4_amd64.deb` installed via `dpkg -i`
- `Adminer@4.8.1` as `adminer-4.8.1.php`
- `psycopg2-binary==2.9.10`, `sqlalchemy`, `pandas` (3.13-wheel-compatible) installed via `pip install --break-system-packages`

Bump deliberately. Each version is a code-review change, not a silent drift.

### `ttyd` is not in Debian trixie main

`apt-get install ttyd` fails with `"Unable to locate package ttyd"`. Use the upstream static binary directly. Same trick applies to any tool in this position — many Debian package-availability gaps are easier to bypass than to fix.

### E2B v2 SDK gotchas

The v2 SDK is structurally different from v1. Things that bit us:

- **`Sandbox(sandbox_id=...)` constructor doesn't work for "attach to existing".** Needs `envd_version`, `envd_access_token`, `sandbox_domain`, `connection_config` — caller doesn't have these. Use `Sandbox.connect(sandbox_id)` instead. (Our `sandbox_manager.kill()` helper still has this bug — see Appendix D.)
- **`sb.commands.run(...)` raises `CommandExitException` on non-zero exit.** It does not return a result for the caller to inspect. The pattern `result = sb.commands.run(...); if result.exit_code != 0: sb.kill()` is dead code — the call raises before the check runs. Wrap each `commands.run` in try/except + explicit cleanup.
- **No built-in `sb.get_terminal_url()`.** v1 shipped one; v2 doesn't. We run our own `ttyd` inside the template and surface `https://7681-<id>.e2b.app` instead (§13b).
- **Templates are SDK-built, not Dockerfile-built.** v2 expects an `e2b.AsyncTemplate(...)` Python object. Builds are triggered by `python build_dev.py` (which calls `AsyncTemplate.build(...)`), not `e2b template build`. The `e2b template migrate` command auto-converts a v1 Dockerfile to a `template.py`, but ships a Python-level quoting bug in the `echo "deb …"` apt-source line — we rewrote the migrated output as one `run_cmd` per logical step.
- **`Sandbox.list()` returns a paginator**, not a list. Iterate via `paginator.next_items()` and `paginator.has_next` until exhausted.

### HTTPS-only port forwarder (the big one)

`<port>-<id>.e2b.app` is an L7 reverse proxy on TLS port 443. The "5432-" prefix is a routing label, not a port forward. Raw-TCP services (Postgres, Redis, Kafka, raw gRPC, K8s API on :6443) are unreachable from outside the sandbox. Resolution: per-stack web consoles baked into each template (§13b). See §12 for the full finding.

### Compose v1 binary is gone, shim it

Modern Debian only ships `docker compose` (v2 plugin). Legacy task `run.sh` files call `docker-compose` (v1 binary). We ship a wrapper at `/usr/local/bin/docker-compose` that `exec`s `docker compose "$@"`. Same shim pattern works for any binary that got renamed.

### `/root/task` is a load-bearing path for legacy tasks

Several existing task `docker-compose.yml` and init scripts hardcode `/root/task` (the droplet's task path). The sandbox flow clones into `/home/user/task` and symlinks `/root/task → /home/user/task` so unchanged task content keeps working. New tasks (Phase 2+) should default to `/home/user/task` and drop the symlink.

### Postgres init: `/docker-entrypoint-initdb.d` vs runtime `psql -f`

Whether `init_database.sql` runs as part of postgres' init pipeline depends on whether the task's compose file mounts it into `/docker-entrypoint-initdb.d/`. If not, `run.sh` runs it manually via `psql -f` after the container is up. The PoC's fintech task does the latter — visible in the postgres log as `ignoring /docker-entrypoint-initdb.d/*`. Grading hooks that snapshot DB state should not assume one path vs the other.

### `--timeout-hours` should be `float`, not `int`

Click's `type=int` rejects `0.1`. We need fractional hours for abandonment tests (e.g. `--timeout-hours 0.1` ≈ 6 min). Switched to `type=float`.

### `pip3` and `pip` may be the same inode in the base image

In `e2bdev/code-interpreter:latest`, `/usr/local/bin/pip3` is a symlink to `/usr/local/bin/pip`. Overwriting `pip` with a wrapper script auto-redirects `pip3` for free. Re-linking `pip3 → pip` afterwards fails with `"are the same file"` even with `ln -sfn`. Skip the second link.

---

## Appendix D — Open tactical items (Phase 1 PoC)

Bugs and TODOs we know about but haven't fixed yet. Tracked here so they don't drift out of mind.

### Bugs in `e2b_flow/`

| Item | Severity | Fix sketch |
|---|---|---|
| `sandbox_manager.kill(sandbox_id)` uses `Sandbox(sandbox_id=...)` | Crashes every kill call | Swap to `Sandbox.connect(sandbox_id).kill()` or `Sandbox._cls_kill(sandbox_id)` |
| `if result.exit_code != 0: sb.kill()` branches in `create_and_setup` are dead | Orphan sandbox on every failed deploy | Wrap each `sb.commands.run(...)` in try/except + explicit cleanup, drop the dead branches |
| `deploy-task` is not idempotent | Redeploy without reset orphans the prior sandbox | Look up `tasks.deployment_info.sandbox_id`, kill if present, then create new |
| `SandboxHandle.terminal_url` is hardcoded `None` | Misleading API surface | Replace with structured `surfaces` dict (`terminal_url`, `editor_url`, `db_console_url`, `app_preview_url`) — pre-build the canonical `https://<port>-<id>.e2b.app` strings |

### Polish / dev quality-of-life

| Item | Notes |
|---|---|
| `e2b_flow exec <sandbox-id> <cmd>` | Wraps `Sandbox.connect(...).commands.run(cmd)` for one-shot debugging |
| `e2b_flow shell <sandbox-id>` | Passthrough to `e2b sandbox connect` so `python -m e2b_flow` is the only entrypoint |
| `e2b_flow status <sandbox-id>` | One-call dump: uptime, free, df, docker ps, compose ps |
| Surface all candidate URLs in deploy JSON | Today only `exposed_ports` is shown — should be `terminal_url` / `editor_url` / `db_console_url` / `app_preview_url` |
| Wire Adminer URL into deploy output | Currently appears only because `8080` is in `DEFAULT_PROBE_PORTS` |

### Task-content changes (other repos)

| Item | Where | Notes |
|---|---|---|
| Drop `Host: <DROPLET_IP>` placeholder from task READMEs | per-task template repos | Replace with sandbox-aware language: "open the DB Console tab" or `psql -h localhost` from the in-sandbox terminal |
| Bump `psycopg2-binary` to `>=2.9.10` in legacy SQL tasks | per-task template repos | One-line `requirements.txt` change; needed for Python 3.13 wheels |
| Mark `UtkrushtApps/<task>-template` repos as "template repository" | GitHub repo settings | Required for §22a's `gh repo create --template ...` flow |

### Phase 2 backend work (not in this repo)

| Item | Where | Notes |
|---|---|---|
| Per-attempt repo provisioning (§22a) | `utkrushta-backend` | `provision_attempt`, `revoke_attempt_credentials`, `transfer_attempt_to_user` helpers + `UtkrushtAttempts` org + bot/GitHub App |
| `sandbox_sessions` table + reconciler (§20-§21) | `utkrushta-backend` | Replaces `tasks.deployment_info` for per-session state; safety-net cleanup for orphans |
| Pre-kill snapshot to S3 (`pg_dump` + `git diff` + tar) | `utkrushta-backend` | Required for grading and audit trail (§29 risk row) |
| Per-session token in front of consoles | `utkrushta-backend` + frontend | Production candidate flow can't ship unauthenticated ttyd / code-server / Adminer |

### Investigations deferred

| Item | Notes |
|---|---|
| WebSocket TCP tunnel (`wstunnel`) for power-user laptop tooling | Skipped Phase 1; revisit if telemetry shows the in-sandbox + web-console combo is insufficient |
| Self-host `e2b-dev/infra` on Hetzner | Phase 6 — only worthwhile above ~1500–2500 sandbox-hrs/month (§28) |
| GitHub App vs fine-grained PAT for laptop credential | Both work; App is the cleaner long-term answer; PAT is fine to ship first |
