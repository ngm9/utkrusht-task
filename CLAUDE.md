# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Does

Automated system for generating, evaluating, deploying, and managing technical coding assessment tasks. Uses OpenAI (via Portkey gateway) to generate realistic coding challenges across 15+ technology stacks, deploys them to DigitalOcean droplets, and manages the lifecycle via GitHub repos/gists and Supabase.

Part of the Utkrushta workspace — see the parent `dev/CLAUDE.md` for cross-repo context.

## Common Commands

### Install dependencies
```bash
pip install -r requirements.txt
```

### Generate assessment tasks (main workflow)
```bash
python multiagent.py generate-tasks \
  -c path/to/competency.json \
  -b path/to/background.json \
  -s path/to/task_scenarios.json
```

### Deploy a task to a droplet
```bash
python multiagent.py deploy-task --task-id <UUID> --droplet-ip <IP>
```

### Reset/undeploy a task
```bash
python multiagent.py reset-task --task-id <UUID> --droplet-ip <IP> --script-path /root/task/kill.sh
```

### Unified pipeline (generate input files + scenarios in one step)
```bash
python -m pipeline --name "Java, Kafka" --proficiency BASIC --count 6 --append
python -m pipeline --name "React" --proficiency BASIC --dry-run
```

### Generate input files only
```bash
python -m generate_input_files --name "Java" --proficiency BASIC
```

### Generate task scenarios only
```bash
python -m scenario_generator --competency-file path/to/competency.json --count 6 --append
```

### PR Review task generation
```bash
python -m pr_review_flow \
  -c path/to/competency.json \
  -b path/to/background.json \
  -s path/to/task_scenarios_pr_review.json
```

### Design review task generation
```bash
# Generate flaw spec + brief + rubric
python -m design_review_flow generate \
  -c path/to/competency.json \
  -p INTERMEDIATE \
  -s "SaaS onboarding redesign" \
  -l lib-001

# Store task in Supabase (after Figma plugin step)
python -m design_review_flow store \
  -f path/to/design_task_spec.json \
  -u "https://figma.com/file/...?duplicate" \
  --env dev
```

### Gist management
```bash
python gist_manager.py sync-prod-to-dev
python gist_manager.py create-prod-missing-gists
python gist_manager.py create --task-ids <ID1> <ID2> --env dev
python gist_manager.py sync-is-enabled
```

## Architecture

### Core Flow: `multiagent.py`

The main orchestrator. Three Click CLI commands: `generate-tasks`, `deploy-task`, `reset-task`.

**Task generation pipeline:**
1. Read competency + background + scenario JSON inputs
2. Select tech-specific prompt from `task_generation_prompts/{level}/`
3. Call OpenAI (via Portkey) to generate task description + code files
4. Run LLM evaluations (`evals.py`) — task eval + code eval with retry loop
5. Create GitHub template repo + answer repo (`github_utils.py`)
6. Create GitHub Gist for task distribution
7. Store metadata in Supabase (dev or prod)
8. Optionally deploy to DigitalOcean droplet (`droplet_utils.py`)

### Module Responsibilities

| Module | Purpose |
|--------|---------|
| `multiagent.py` | Main CLI orchestrator — generate, deploy, reset tasks |
| `utils.py` | Task generation helpers: prompt formatting, JSON parsing, file I/O, gist creation |
| `evals.py` | LLM-based evaluation of generated tasks and code quality |
| `schemas.py` | JSON schemas for OpenAI structured outputs |
| `github_utils.py` | GitHub repo creation, template repos, batch file uploads |
| `droplet_utils.py` | DigitalOcean SSH/SFTP operations, droplet management |
| `gist_manager.py` | Standalone CLI for GitHub Gist lifecycle (sync, create, enable) |
| `logger_config.py` | Centralized logging |

### Sub-packages

| Package | Purpose |
|---------|---------|
| `pipeline/` | Unified CLI chaining `generate_input_files` + `scenario_generator` |
| `generate_input_files/` | Fetches competencies from Supabase DB, generates input JSON files |
| `scenario_generator/` | LLM-generated real-world scenarios for competencies |
| `pr_review_flow/` | Separate flow for PR review assessment tasks (own prompts, schemas, evals) |
| `design_review_flow/` | UI/UX design review assessments with Figma flaw injection |
| `non_tech_flow/` | Separate pipeline for non-technical AI/ML assessment challenges |
| `task_generation_prompts/` | Technology-specific prompt templates organized by level (Beginner/Basic/Intermediate) |
| `task_input_files/` | Input JSON files per technology (competencies, backgrounds, scenarios) |

### External Services

- **OpenAI API** (via Portkey gateway) — task + code generation, evaluations
- **Supabase** — task metadata storage (dev and prod environments)
- **GitHub** — template repos, answer repos, gists (via PyGithub)
- **DigitalOcean** — droplet deployment via SSH/paramiko

### Environment Variables

Required in `.env` — see `TASK_MANAGEMENT_GUIDE.md` for full list. Key ones:
- `OPENAI_API_KEY`, `PORTKEY_API_KEY` — LLM access
- `GITHUB_UTKRUSHTAPPS_TOKEN`, `GITHUB_GIST_TOKEN`, `REPO_OWNER` — GitHub
- `SUPABASE_URL_APTITUDETESTSDEV`, `SUPABASE_API_KEY_APTITUDETESTSDEV` — Supabase dev
- `SUPABASE_URL_APTITUDETESTS`, `SUPABASE_API_KEY_APTITUDETESTS` — Supabase prod
- `DIGITALOCEAN_API_PAT`, `AVAILABLE_IPS`, `SSH_PRIVATE_KEY_PATH` — droplet ops

## Key Patterns

- All CLI interfaces use **Click**. `multiagent.py` has top-level commands; sub-packages use `__main__.py` entry points.
- OpenAI calls go through **Portkey gateway** (`PORTKEY_GATEWAY_URL`) with provider headers — never call OpenAI directly.
- Task generation prompts are Python files exporting prompt strings, organized by `{level}/{tech_stack}_prompt.py`.
- Two Supabase environments (dev/prod) controlled by `--env` flags throughout.
- LLM evaluations have a retry loop (`MAX_EVAL_RETRIES` in `evals.py`) — tasks that fail eval are regenerated.
