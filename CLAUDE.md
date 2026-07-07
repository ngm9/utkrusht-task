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
python -m apps.cli generate_tasks \
  -c path/to/competency.json \
  -b path/to/background.json \
  -s path/to/task_scenarios.json
```

### Deploy a task to an E2B sandbox
```bash
python -m infra.e2b deploy-task --task-id <UUID> --env dev
```

### Reset/undeploy a task
```bash
python -m infra.e2b reset-task --task-id <UUID> --env dev
```

> The legacy `multiagent.py deploy-task` / `reset-task` (DigitalOcean droplets
> + SSH) were removed on 2026-05-25. E2B is the only live deploy path.

### Full tech pipeline (preflight → input_files → scenarios → prompts → generate)
```bash
python -m flows.tech --name "Java, Kafka" --proficiency BASIC --count 6
python -m flows.tech --name "React" --proficiency BASIC --skip-preflight
```

### Generate input files only (stage 1)
```bash
python -m flows.tech.stages.input_files --competency-name "Java" --proficiency BASIC
```

### Generate task scenarios only (stage 2)
```bash
python -m flows.tech.stages.scenarios --competency-file path/to/competency.json --background-file path/to/background.json --count 6 --append
```

### PR Review task generation
```bash
python -m flows.pr_review \
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
python -m apps.cli gist sync-prod-to-dev
python -m apps.cli gist create-prod-missing-gists
python -m apps.cli gist create --task-ids <ID1> <ID2> --env dev
python -m apps.cli gist sync-is-enabled
```

## Architecture

> **Authoritative layout: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).** Entrypoints in
> `apps/`, one package per flow in `flows/`, shared libs in `infra/` +
> `task_generation_prompts/`. The old `multiagent.py` shim, top-level `cli/`, and
> `run_pipeline.py` were replaced by `apps/cli` + `flows/tech` on 2026-07-07
> (flows-restructure). The tables below are a summary; ARCHITECTURE.md is the source of truth.

### Core Flow: `flows/tech/` (run via `python -m flows.tech`)

The main pipeline lives in `flows/tech/`: `pipeline.py` orchestrates the stages
under `flows/tech/stages/{preflight,input_files,scenarios,prompts,generate}`,
driven by the manifest in `flows/_base/registry.py`. Each stage runs as its own
`python -m` subprocess. Deploy + reset live in `infra/e2b`.

**Task generation pipeline:**
1. Read competency + background + scenario JSON inputs
2. Select tech-specific prompt from `task_generation_prompts/{level}/`
3. Call OpenAI (via Portkey) to generate task description + code files
4. Run LLM evaluations (`infra/evals.py`) — task eval + code eval with retry loop
5. Run the E2B build/test gate (`infra/e2b/sandbox_eval.py`)
6. Create GitHub template repo + answer repo (`infra/github_utils.py`)
7. Create GitHub Gist for task distribution
8. Store metadata in Supabase (dev or prod)
9. Live deploy (separate step): `python -m infra.e2b deploy-task`

### Module map

| Path | Purpose |
|------|---------|
| `apps/cli/` | The one human CLI — `python -m apps.cli` (`generate_tasks` + `gist`) |
| `flows/_base/` | Shared pipeline machinery: `StageSpec`, stage registry, subprocess runner |
| `flows/tech/` | Main flow: `pipeline.py` + `stages/{preflight,input_files,scenarios,prompts,generate}` |
| `flows/pr_review/`, `flows/non_tech/` | Secondary flows (own prompts, evals, `__main__`) |
| `flows/design_review/` | Reserved (code removed) — see its README |
| `infra/` | Shared libs: `supabase`, `github_utils`, `evals`, `schemas`, `utils`, `pricing`, `infra_kinds`, `logger_config`, `e2b/`, `tracing/`, `classifier/`, `storage/` |
| `task_generation_prompts/` | Shared prompt-template reference data (by level); consumed by infra + flows |
| `task_input_parser/`, `task_quality/`, `task_validation/` | Shared input parsing / quality / validation |
| `task_builder/` | Conversational FastAPI front-end that runs the pipeline with live progress |
| `trace_ui/` | Trace/log viewer over pipeline runs |

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

- All CLI interfaces use **Click** (gist uses argparse). `apps/cli` is the top-level CLI (`python -m apps.cli` → `generate_tasks` + `gist`); flows and stages expose `__main__.py` entry points (`python -m flows.tech`, `python -m flows.tech.stages.<stage>`).
- OpenAI calls go through **Portkey gateway** (`PORTKEY_GATEWAY_URL`) with provider headers — never call OpenAI directly.
- Task generation prompts are Python files exporting prompt strings, organized by `{level}/{tech_stack}_prompt.py`.
- Two Supabase environments (dev/prod) controlled by `--env` flags throughout.
- LLM evaluations have a retry loop (`MAX_EVAL_RETRIES` in `evals.py`) — tasks that fail eval are regenerated.

## illuminate: required pre-write step

Before writing or modifying any source file in this repository, invoke the
`illuminate_audit` MCP tool with your plan, the files you intend to modify,
and your rationale. Surface the response to the user before proceeding.

If `status` is `block`, do not proceed without explicit user approval.
If `status` is `warn`, surface the warnings to the user before writing.
