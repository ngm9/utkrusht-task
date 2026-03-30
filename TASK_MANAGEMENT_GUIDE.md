# Task Management Guide

This guide covers the complete workflow for **generating**, **deploying**, **testing**, and **resetting** assessment tasks using the Utkrushta Infrastructure Assessment System.

---

## Environment Setup

### Python Executable

```bash
PYEXE="/c/Users/Meet/AppData/Local/Programs/Python/Python310/python.exe"
```

### Required Environment Variables (`.env`)

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | OpenAI API access |
| `PORTKEY_API_KEY` | Portkey gateway (routes OpenAI calls) |
| `GITHUB_UTKRUSHTAPPS_TOKEN` | GitHub push access to UtkrushtApps org |
| `REPO_OWNER` | GitHub org name (`UtkrushtApps`) |
| `SUPABASE_URL_APTITUDETESTSDEV` | Dev Supabase URL |
| `SUPABASE_API_KEY_APTITUDETESTSDEV` | Dev Supabase key |
| `SUPABASE_URL_APTITUDETESTS` | Prod Supabase URL |
| `SUPABASE_API_KEY_APTITUDETESTS` | Prod Supabase key |
| `DIGITALOCEAN_API_PAT` | DigitalOcean API token (optional — for droplet info) |
| `AVAILABLE_IPS` | Comma-separated droplet IPs for auto-select (e.g. `159.65.53.87`) |
| `SSH_PRIVATE_KEY_PATH` | Path to SSH key (e.g. `/c/ssh-keys/dutkrusht-dev-do`) |
| `GITHUB_GIST_TOKEN` | GitHub Gist token (optional — enables Gist creation on task generation) |

### Infrastructure

| Resource | Value |
|----------|-------|
| Droplet 2 (primary) | `159.65.53.87` — `uktrusht-task-droplet-2` |
| Droplet 1 | `64.227.178.86` — `uktrusht-task-droplet-1` |
| SSH Key | `/c/ssh-keys/dutkrusht-dev-do` |
| Deploy path on droplet | `/root/task/` |
| GitHub Org | `UtkrushtApps` |

---

## Project Structure

```
C:\Utkrushta_task\
├── multiagent.py                  # CLI: generate_tasks, deploy_task, reset_task
├── utils.py                       # Core task generation helpers
├── evals.py                       # LLM-based task + code evaluations
├── schemas.py                     # JSON schema definitions for structured LLM outputs
├── droplet_utils.py               # SSH/SFTP + DigitalOcean droplet operations
├── github_utils.py                # GitHub repo creation, template repos, batch file upload
├── gist_manager.py                # GitHub Gist lifecycle management CLI
├── logger_config.py               # Centralized logging
│
├── pipeline/                      # Unified pipeline: input files + scenarios in one command
│   ├── __main__.py                # Entry point: python -m pipeline
│   └── pipeline.py                # Core pipeline logic
│
├── generate_input_files/          # Generates competency + background JSON from Supabase
│   ├── __main__.py
│   └── generator.py
│
├── scenario_generator/            # Standalone scenario generator
│   ├── __main__.py                # Entry point: python -m scenario_generator
│   ├── generator.py               # Classification, LLM calls, validation pipeline
│   └── prompts.py                 # LLM prompt templates
│
├── non_tech_flow/                 # Non-technical (AI/ML) assessment pipeline
│   ├── non_tech_multiagent.py
│   ├── models.py
│   ├── non_tech_utils.py
│   └── non_tech_evals.py
│
├── task_generation_prompts/       # Technology-specific LLM prompt templates
│   ├── Basic/                     # BASIC proficiency prompts
│   ├── Intermediate/              # INTERMEDIATE proficiency prompts
│   └── Beginner/                  # BEGINNER proficiency prompts
│
├── task_input_files/              # Input JSON files for task generation
│   ├── input_<tech>/<level>/      # Per-tech, per-level competency + background files
│   └── task_scenarios/
│       ├── task_scenarios.json              # BEGINNER + BASIC scenarios
│       ├── task_scenarios_intermediate.json # INTERMEDIATE + ADVANCED scenarios
│       └── task_sceanrio_no_code.json       # NON_CODE scenarios
│
└── infra_assets/tasks/<uuid>/     # Generated task artifacts
    ├── task.json                  # Full task definition (includes GitHub repo URL)
    ├── docker-compose.yml         # Container setup
    ├── run.sh                     # Deployment script
    ├── kill.sh                    # Cleanup script
    └── init_database.sql          # DB seed data (if applicable)
```

---

## Full Workflow Overview

```
[pipeline] → generates input files + scenarios
     ↓
[generate-task] → generates task (GitHub repo, Supabase record, local files)
     ↓
[test-task] → deploy → verify → kill → verify clean
     ↓
[reset-task] → clean the droplet when needed
```

---

## Step 1 — Pipeline: Generate Input Files + Scenarios

The pipeline fetches competency definitions from Supabase, generates background context via LLM, writes input files locally, and generates + saves task scenarios — all in one command.

### Command

```bash
PYEXE="/c/Users/Meet/AppData/Local/Programs/Python/Python310/python.exe"
cd /c/Utkrushta_task

$PYEXE -m pipeline \
  --name "<tech1>,<tech2>" \
  --proficiency BASIC \
  --count 6 \
  --append
```

### Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--name`, `-n` | Yes | — | Tech name(s), comma-separated or multiple flags |
| `--proficiency`, `-p` | Yes | — | BEGINNER \| BASIC \| INTERMEDIATE \| ADVANCED |
| `--count`, `-c` | No | 6 | Number of scenarios to generate per proficiency run |
| `--append` | No | False | Merge into existing scenario file instead of overwriting |
| `--folder-name`, `-f` | No | Auto | Override the auto-generated input files subfolder name |
| `--force` | No | False | Overwrite existing input files |
| `--dry-run` | No | False | LLM runs and output is previewed — no files written |
| `--env` | No | `prod` | Supabase environment: `dev` or `prod` |
| `--scenario-output` | No | Auto | Override scenario output file path |

### Examples

```bash
# Single tech, single level
$PYEXE -m pipeline --name "Java, Kafka" --proficiency BASIC --count 6 --append

# Multiple techs, multiple levels (runs once per level)
$PYEXE -m pipeline --name "Pandas,Numpy" --proficiency BASIC,INTERMEDIATE --count 2 --append

# Dry run to preview without writing files
$PYEXE -m pipeline --name "ReactJS" --proficiency BASIC --count 3 --dry-run
```

### What It Generates

The pipeline runs once per proficiency level:

1. **Fetches competencies** from Supabase for each named tech
2. **Generates background** (role_context + questions_prompt) via LLM
3. **Writes input files** to `task_input_files/input_<tech>/<level>/`:
   - `competency_<tech>_<level>_Utkrusht.json`
   - `background_forQuestions_utkrusht_<tech>_<level>.json`
4. **Generates scenarios** and saves to the appropriate scenario file

### Scenario Output File Mapping

| Proficiency | Target File |
|-------------|-------------|
| BEGINNER | `task_input_files/task_scenarios/task_scenarios.json` |
| BASIC | `task_input_files/task_scenarios/task_scenarios.json` |
| INTERMEDIATE | `task_input_files/task_scenarios/task_scenarios_intermediate.json` |
| ADVANCED | `task_input_files/task_scenarios/task_scenarios_intermediate.json` |
| NON_CODE | `task_input_files/task_scenarios/task_sceanrio_no_code.json` |

---

## Step 2 — Generate Task

Generates an assessment task from pre-built input files. The LLM creates the task description, code files, Docker infrastructure, README, and solution. Everything is pushed to GitHub and saved in Supabase and locally.

### Command

```bash
PYEXE="/c/Users/Meet/AppData/Local/Programs/Python/Python310/python.exe"
cd /c/Utkrushta_task

$PYEXE multiagent.py generate_tasks \
  --competency-file task_input_files/input_<tech>/<level>/competency_<tech>_<level>_Utkrusht.json \
  --background-file task_input_files/input_<tech>/<level>/background_forQuestions_utkrusht_<tech>_<level>.json \
  --scenarios-file task_input_files/task_scenarios/task_scenarios.json
```

Use `task_scenarios_intermediate.json` for INTERMEDIATE/ADVANCED tasks.

### Generation Process

1. Loads competency + background + scenario files
2. Calls LLM (`gpt-5.1`) to generate task description, code files, Docker infrastructure
3. Runs evaluations: LLM task eval + LLM code eval
4. Determines task type (backend/frontend) based on competency keywords
5. Generates answer code + solution steps
6. Creates public GitHub template repo + private answer repo under `UtkrushtApps`
7. Uploads all code files to GitHub in a single batch commit
8. Creates a GitHub Gist (if `GITHUB_GIST_TOKEN` is set)
9. Stores task record in Supabase `tasks` table + `task_competencies` table
10. Saves all files locally to `infra_assets/tasks/<uuid>/`
11. Renames local directory from temp repo name to actual task UUID

### Generated Outputs

- `infra_assets/tasks/<uuid>/task.json` — Full task definition; `resources.github_repo` has the repo URL
- `infra_assets/tasks/<uuid>/docker-compose.yml` — Container setup
- `infra_assets/tasks/<uuid>/run.sh` — Deployment script
- `infra_assets/tasks/<uuid>/kill.sh` — Cleanup script
- `infra_assets/tasks/<uuid>/init_database.sql` — DB seed data (if applicable)
- GitHub template repo under `UtkrushtApps/<repo-name>`
- Answer repo under `UtkrushtApps/<repo-name>-answers`
- Supabase record in `tasks` + `task_competencies` tables

---

## Step 3 — Test Task (Deploy → Verify → Kill → Verify Clean)

### STEP 3.1 — Check Droplet is Clean

```bash
SSH_KEY="/c/ssh-keys/dutkrusht-dev-do"
DROPLET_IP="159.65.53.87"

ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$DROPLET_IP \
  "docker ps -a && echo '---IMAGES---' && docker images && echo '---VOLUMES---' && docker volume ls && echo '---TASK_DIR---' && ls /root/task 2>&1 || echo 'folder not found'"
```

The droplet is NOT clean if any of these exist: running/stopped containers, Docker images, Docker volumes, `/root/task` directory.

If not clean, run:

```bash
ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$DROPLET_IP "cd /root/task && bash kill.sh"
```

Or manual cleanup if `kill.sh` is missing:

```bash
ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$DROPLET_IP "
  docker stop \$(docker ps -q) 2>/dev/null || true
  docker rm \$(docker ps -aq) 2>/dev/null || true
  docker volume prune -f || true
  docker image prune -a -f || true
  docker system prune -a --volumes -f || true
  rm -rf /root/task || true
"
```

### STEP 3.2 — Pre-Deploy Fixes (Before Uploading)

**Read task files first:**

```bash
TASK_DIR="/c/Utkrushta_task/infra_assets/tasks/<task-id>"
```

- `task.json` — GitHub repo URL, task description, tech stack
- `docker-compose.yml` — services, ports, volumes
- `run.sh` — check it waits for services to be ready
- `kill.sh` — understand what cleanup it does
- `init_database.sql` — if present, verify timestamps use `NOW()` not hardcoded dates

**If init_database.sql has hardcoded dates**, fix them to relative (`NOW() - INTERVAL '30 days'`) and push the fix to GitHub:

```bash
GH_TOKEN=$(grep GITHUB_UTKRUSHTAPPS_TOKEN /c/Utkrushta_task/.env | cut -d= -f2)
git clone "https://${GH_TOKEN}@github.com/UtkrushtApps/<repo-name>.git" /tmp/fix_<repo-name>
cd /tmp/fix_<repo-name>
git config user.email "naman@utkrushta.co.in" && git config user.name "Utkrushta Bot"
# edit files
git add -A
git commit -m "fix: use relative timestamps"
git push origin main
rm -rf /tmp/fix_<repo-name>
```

### STEP 3.3 — Upload and Deploy

```bash
SSH_KEY="/c/ssh-keys/dutkrusht-dev-do"
DROPLET_IP="159.65.53.87"
TASK_DIR="/c/Utkrushta_task/infra_assets/tasks/<task-id>"

ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$DROPLET_IP "rm -rf /root/task && mkdir -p /root/task"

scp -i $SSH_KEY -o StrictHostKeyChecking=no \
  $TASK_DIR/docker-compose.yml \
  $TASK_DIR/run.sh \
  $TASK_DIR/kill.sh \
  root@$DROPLET_IP:/root/task/
# Add init_database.sql to scp if it exists

ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$DROPLET_IP \
  "cd /root/task && bash run.sh"
```

### STEP 3.4 — Verify Deployment

**Check containers are running:**

```bash
ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$DROPLET_IP "docker ps -a"
```

All containers should be in "Up" status.

**If the task has a database** — validate data inside the DB container:
- Row counts for all tables
- Timestamp range check (MIN/MAX of date columns — confirm recent data exists)
- Run sample query if `sample_queries.sql` exists

**If the task has an API** — test endpoints:
- Health/root: `curl -s http://$DROPLET_IP:<port>/` or `/health`
- GET/list endpoints that should work out of the box
- For endpoints the candidate must implement — only verify they return any response; do NOT fix them

### What is and is NOT OK to Fix

**OK to fix (infra issues):**
- Container won't start (wrong port, missing env var, broken Dockerfile)
- DB not seeding (init_database.sql not loading, wrong volume path)
- `run.sh` / `kill.sh` broken (CRLF, wrong commands)
- Health endpoint returning 500 due to missing DB connection

**NOT OK to fix (candidate's problem):**
- Missing or incomplete API endpoints the task requires the candidate to implement
- Business logic errors (filtering, sorting, aggregation)
- Missing validations described in the task README
- Any code the README says the candidate should write

### STEP 3.5 — Test kill.sh

```bash
ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$DROPLET_IP "cd /root/task && bash kill.sh"
```

### STEP 3.6 — Verify Droplet is Fully Clean

```bash
ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$DROPLET_IP \
  "docker ps -a && echo '---IMAGES---' && docker images && echo '---VOLUMES---' && docker volume ls && echo '---TASK_DIR---' && ls /root/task 2>&1 || echo 'folder removed'"
```

All must be true for kill.sh to pass:
- No containers (running or stopped)
- No Docker images
- No Docker volumes
- `/root/task` directory does not exist

**If kill.sh fails**, fix it (see Standard kill.sh Template below), push to GitHub, re-deploy, re-verify, re-run kill.sh. Do NOT leave the droplet deployed after testing.

---

## Step 4 — Reset Task

### Standard Reset (via SSH directly)

```bash
SSH_KEY="/c/ssh-keys/dutkrusht-dev-do"
DROPLET_IP="159.65.53.87"

ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$DROPLET_IP "cd /root/task && bash kill.sh"
```

### Verify Cleanup

```bash
ssh -i $SSH_KEY -o StrictHostKeyChecking=no root@$DROPLET_IP \
  "docker ps -a && docker images && ls /root/task 2>&1 || echo 'folder removed'"
```

Expected: no containers, no images, `/root/task` removed.

### Via multiagent.py (updates Supabase `is_deployed` status)

```bash
$PYEXE multiagent.py reset_task \
  --task-id <uuid> \
  --droplet-ip 159.65.53.87 \
  --script-path /root/task/kill.sh
```

---

## Standard kill.sh Template

```bash
#!/usr/bin/env bash
set -e

echo "Stopping and removing Docker containers and volumes..."
docker-compose down -v || true

echo "Removing Docker images..."
docker image prune -a -f || true

echo "Running Docker system prune..."
docker system prune -f || true

echo "Removing task directory at /root/task if it exists..."
rm -rf /root/task || true

echo "Cleanup completed"
```

> **Note:** For tasks where the standard template is insufficient (e.g., named volumes or specific images remain), build a custom kill.sh that specifically undoes everything `run.sh` and `docker-compose.yml` set up.

---

## Standalone Scenario Generation

Use this when you need scenarios for a tech stack without regenerating input files.

### Command

```bash
PYEXE="/c/Users/Meet/AppData/Local/Programs/Python/Python310/python.exe"
cd /c/Utkrushta_task

$PYEXE -m scenario_generator \
  --competency-file task_input_files/input_<tech>/<level>/competency_<tech>_<level>_Utkrusht.json \
  --count 6 \
  --append
```

### CLI Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--competency-file` | Yes | — | Path to competency JSON file |
| `--count` | No | 6 | Number of scenarios to generate |
| `--output` | No | Auto-detect | Output file path (auto-selects based on proficiency) |
| `--append` | No | False | Merge into existing file instead of overwriting |
| `--background-file` | No | None | Optional background JSON for additional context |
| `--dry-run` | No | False | Preview without saving |

### Quality Pipeline

Every generated batch goes through:

1. **Structural Validation** — 200–3,000 characters, narrative paragraph format
2. **Deduplication** — text similarity check against existing scenarios (threshold: 0.6)
3. **LLM Evaluation** — checks realism, complexity calibration, technical detail, completeness

Failed scenarios are auto-regenerated (up to 2 retry attempts).

### Scenario Format

```
**Current Implementation:** [1-2 sentences: existing system, tech stack, what is broken/missing]

**Your Task:** [Clear deliverables, bullet points for multiple items]

**Success Criteria:** [Expected outcome with measurable targets]
```

### Technology Categories

| Category | Competencies | Scenario Focus |
|----------|-------------|----------------|
| BACKEND | Java, Python, FastAPI, Go, Node.js, Express, Kafka, Redis, Docker | API endpoints, concurrency, data integrity |
| FRONTEND | ReactJs, React Native, NextJs, TypeScript | Components, state management, rendering |
| DATABASE | SQL, PostgreSQL, MongoDB | Schema design, query optimization, transactions |
| MIXED_STACK | Any cross-category combination | Integration patterns, data flow between layers |
| NON_CODE | Prompt Engineering, AI Literacy | LLM artifacts, evaluation datasets |

---

## Deploy via multiagent.py (with Supabase update)

For deploying tasks with automatic Supabase status update:

```bash
# Deploy by task ID
$PYEXE multiagent.py deploy_task --task-id <uuid> --droplet-ip 159.65.53.87

# Deploy all undeployed tasks for a competency
$PYEXE multiagent.py deploy_task --competency-id <competency-uuid>

# Auto-select droplet from AVAILABLE_IPS
$PYEXE multiagent.py deploy_task --task-id <uuid>
```

> **Preferred deploy method for testing is direct SSH** (see Step 3) — it gives more control and doesn't require Supabase to be updated.

---

## Scenario Key Format

Scenarios in `task_scenarios.json` are keyed by competency name + proficiency:

- Single: `"Java (BASIC)"`, `"ReactJs (BEGINNER)"`
- Multi: alphabetically sorted, joined: `"Java (BASIC), Kafka (BASIC)"`

Keys must match exactly for `load_relevant_scenarios()` to find them during task generation.

---

## Supported Tech Stacks

Python, Python-FastAPI, Python-Pandas/Numpy, Python-Redis, ReactJS, NextJS-TypeScript,
NodeJS-MongoDB, NodeJS-PostgreSQL, ExpressJS, Java, Java-SpringBoot, Java-Kafka,
Java-Docker, Go, Go-Docker, Go-Redis, SQL, PostgreSQL, MongoDB-React-Node,
Shell Script, Apache Camel, Docker, RAG
