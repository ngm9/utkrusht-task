# PR Review Task Category — Design Spec

## Overview

A new assessment task category where candidates review a GitHub Pull Request against an existing codebase. The candidate receives a GitHub repo with a clean `main` branch and an open PR containing intentional flaws. They review using GitHub's native PR review UI — leaving line comments, approving, or requesting changes.

This tests real-world code review skills: spotting logic bugs, pattern violations, hygiene issues, and structural problems — not just theoretical knowledge.

## Key Decisions

- **Candidate interaction**: Native GitHub PR review UI (no custom platform UI needed)
- **Base repo strategy**: LLM generates a clean base repo, then generates flawed PRs against it (option C — one base can yield multiple PR tasks)
- **Generation approach**: Three-phase with evaluation gates (Phase 1: base repo, Phase 2: flawed PR + answer key)
- **Pipeline structure**: Separate module (`pr_review_flow/`), following the `non_tech_flow/` precedent
- **No deployment needed**: No DigitalOcean droplets — the deliverable is a GitHub repo + open PR
- **Flaw specifics driven by scenarios**: Scenarios define what flaws to inject, calibrated to proficiency during scenario generation. Generation prompts follow the scenario literally.

## Directory Structure

```
pr_review_flow/
├── __init__.py
├── __main__.py                  # CLI: python -m pr_review_flow
├── pr_review_multiagent.py      # Main orchestrator
├── pr_review_utils.py           # PR-review-specific helpers
├── pr_review_evals.py           # Two eval gates: base repo quality, PR + answer key
├── pr_review_github.py          # GitHub ops: create branch, open PR
├── prompts/
│   ├── __init__.py
│   ├── base_repo_prompts.py     # Generic prompt template for clean base repos
│   ├── pr_generation_prompts.py # Generic prompt template for flawed PRs + answer key
│   └── eval_prompts.py          # Prompts for evaluation gates
└── schemas.py                   # JSON schemas for structured LLM output
```

Shared modules reused from root: `github_utils.py`, `logger_config.py`, `scenario_generator/`, `generate_input_files/`.

New scenario files: `task_input_files/task_scenarios/task_scenarios_pr_review.json` (and `_intermediate` variant).

## Generation Pipeline

### Phase 1: Base Repo Generation

**Input:** competencies with scopes + scenario `**Project Context:**`

**LLM prompt:** Generic template (works across tech stacks). Unlike the existing `PROMPT_REGISTRY` pattern that has per-tech-stack prompt files, PR Review uses a single template because the scenario's `**Project Context:**` already provides all tech-specific guidance. The competency scopes add further detail. This avoids maintaining 30+ prompt files for a task type where the scenario carries the tech context.

**Output (structured JSON):**
```json
{
  "code_files": {
    "README.md": "...",
    "src/main.py": "...",
    "src/api/products.py": "...",
    ...
  }
}
```

**Evaluation gate:** Is the code clean, well-structured, realistic? Does it follow best practices for the tech stack? Are patterns consistent throughout?

**Evaluation minimum thresholds:** Base repo must have at least 3 files (excluding README and .gitignore) to provide enough surface area for a meaningful PR review.

**On eval failure:** Retry once with eval feedback explaining why it failed. If retry also fails, stop and surface error. No GitHub resources are created during Phase 1 — GitHub operations only happen after both phases pass — so there is nothing to clean up on failure.

### Phase 2: Flawed PR + Answer Key Generation

**Input:** base repo files (from Phase 1) + scenario `**PR Intent:**` + scenario `**Injected Flaws:**`

**LLM prompt:** Generic template. Flaw specifics come entirely from the scenario.

**Output (structured JSON):**
```json
{
  "pr_title": "Add restock endpoint for inventory management",
  "pr_description": "Implements PUT /products/{id}/restock ...",
  "modified_files": {
    "src/api/products.py": "...modified content..."
  },
  "added_files": {
    "src/api/audit.py": "...new file content..."
  },
  "deleted_files": [],
  "answer_key": {
    "flaws": [
      {
        "file": "src/api/products.py",
        "line_range": "23-31",
        "category": "logic_error",
        "severity": "critical",
        "description": "No validation that quantity is positive, allowing negative restocks",
        "correct_approach": "Add check: if quantity <= 0 raise HTTPException(400)"
      }
    ],
    "overall_verdict": "request_changes",
    "pr_description_issues": [
      {
        "issue": "No mention of audit logging side effect",
        "suggestion": "PR description should document that restock events are logged to audit table"
      }
    ]
  }
}
```

**Evaluation gate:** Are flaws realistic (not contrived)? Is the answer key complete — does it cover all intentional flaws? Are severity ratings appropriate?

**Pre-validation (before eval):** Verify that all keys in `modified_files` exist in the Phase 1 base repo output. Reject and retry if any reference a nonexistent file.

**On eval failure:** Retry once with eval feedback. If retry also fails, stop and surface error. No GitHub resources exist at this point — GitHub operations only run after both phases pass.

### Retry Policy

Both phases: `MAX_RETRIES = 1`. On eval failure, the eval feedback (failure reasons) is passed back to the LLM in the retry prompt so it can correct specific issues.

### Execution Order

GitHub and Supabase operations only happen AFTER both Phase 1 and Phase 2 pass their evaluation gates. This means:
- If Phase 1 fails after retry, nothing is created — clean exit
- If Phase 2 fails after retry, nothing is created — clean exit
- GitHub repo, branch, and PR are created only when both phases have validated outputs
- If GitHub operations fail mid-way (e.g., branch created but PR creation fails), retry the failed GitHub API call up to 2 times before surfacing the error

## Scenario Format

PR Review scenarios use a different three-section format from regular task scenarios:

```
**Project Context:** [1-2 sentences describing the base repo — what the application does,
tech stack, current state. Drives Phase 1 generation.]

**PR Intent:** [1-2 sentences describing what the PR claims to do — the feature/fix/refactor
being submitted. This is the "story" of the PR.]

**Injected Flaws:** [Bullet list of specific flaws to introduce. These are instructions to
the LLM, NOT shown to the candidate.]
```

### Example (Python FastAPI, BASIC)

```
**Project Context:** A FastAPI inventory management API for a warehouse company with
endpoints for products, stock levels, and suppliers. Uses SQLAlchemy ORM with
repository pattern, Pydantic schemas for validation, and structured error handling.

**PR Intent:** Add a new PUT /products/{id}/restock endpoint that accepts a quantity,
updates stock levels, and logs the restock event to an audit table.

**Injected Flaws:**
- Logic: restock endpoint doesn't validate that quantity is positive, allowing negative restocks
- Pattern violation: PR uses raw SQL queries instead of the repository pattern used everywhere else
- Hygiene: introduces a utility function that duplicates existing helper in utils.py
- Missing: no error handling for product not found, unlike other endpoints in the codebase
```

### Flaw Category Reference Palette

Scenarios can draw from these categories (not exhaustive — scenario authors can define any flaw):

**Correctness:** logic bugs, incorrect error handling, race conditions, security issues
**Design & structure:** breaking existing patterns, wrong abstraction level, poor separation of concerns, breaking API contracts
**Code hygiene:** naming inconsistencies, dead code, magic numbers, misleading comments, copy-pasted code
**Operational:** missing logging, no input validation, performance issues, missing/meaningless tests

### Scenario Storage

Stored in `task_input_files/task_scenarios/task_scenarios_pr_review.json` (and `task_scenarios_pr_review_intermediate.json`), keyed the same way as regular scenarios: `"Python - FastAPI (BASIC)"`.

### Scenario Validation

PR Review scenarios use different headers from regular scenarios (`**Project Context:**`, `**PR Intent:**`, `**Injected Flaws:**` instead of `**Current Implementation:**`, `**Your Task:**`, `**Success Criteria:**`). The existing `validate_scenario_structure()` checks for the regular headers and will reject PR review scenarios. A new `validate_pr_review_scenario_structure()` function will be added to `scenario_generator/generator.py` (or `pr_review_utils.py`), checking for the PR-review-specific headers. The scenario generator will call the appropriate validator based on scenario type.

## GitHub Operations

Performed by `pr_review_github.py`, reusing `github_utils.py` internals:

1. **Create repo** via `github_utils.create_github_repo()` with `auto_init=True` (creates an initial commit on `main` so that branch refs exist for subsequent operations)
2. **Push base files to `main`** via `github_utils.upload_files_batch()` (overwrites the auto-init README with the LLM-generated base repo files including its own README.md)
3. **Create branch from `main`** — get main SHA, create ref `refs/heads/{branch_name}`
4. **Push PR files to branch** via a new `upload_pr_files_to_branch()` function in `pr_review_github.py` that handles modified files (overwrite), added files (create), and deleted files (tree entries with `sha=None`). The existing `upload_files_batch()` does not support deletions, so this is a PR-review-specific function.
5. **Open PR** via GitHub API `POST /repos/{owner}/{repo}/pulls` with `base="main"`, `head=branch_name`, and the generated title + description
6. **Return both URLs:**
   - `repo_url`: `https://github.com/{owner}/{task-slug}` (base repo, main branch)
   - `pr_url`: `https://github.com/{owner}/{task-slug}/pull/1` (the open PR)

### Branch Naming

Branch name is derived from `pr_title` using a `slugify_branch_name()` function in `pr_review_utils.py`:
- Lowercase, replace spaces with hyphens, strip non-alphanumeric (except `/` and `-`)
- Prefix with `feature/` if no prefix present
- Append 4-char random suffix to avoid collisions (e.g., `feature/add-restock-endpoint-a3f2`)

### GitHub Error Handling

Each GitHub API call is retried up to 2 times on transient failures (5xx, network errors). If a step fails permanently after retries, the error is surfaced with context about which step failed and what resources were already created (for manual cleanup if needed).

## Supabase Storage

Fits into the existing `tasks` table with no schema changes:

```json
{
  "created_at": "2026-03-16T12:00:00Z",
  "task_blob": {
    "title": "PR Review: Add Restock Endpoint",
    "task_type": "pr_review",
    "question": "Review the open PR and provide feedback",
    "short_overview": "...",
    "outcomes": "...",
    "resources": {
      "github_repo": "https://github.com/org/inventory-api-review",
      "github_pr": "https://github.com/org/inventory-api-review/pull/1"
    },
    "hints": "...",
    "definitions": {}
  },
  "readme_content": {},
  "pre_requisites": "GitHub account, familiarity with PR review workflow",
  "answer": "",
  "criterias": [{"competency_id": "...", "name": "Python - FastAPI", "proficiency": "BASIC"}],
  "solutions": {
    "steps": [
      {
        "file": "src/api/products.py",
        "line_range": "23-31",
        "category": "logic_error",
        "severity": "critical",
        "description": "No validation that quantity is positive",
        "correct_approach": "Add check: if quantity <= 0 raise HTTPException(400)"
      }
    ],
    "overall_verdict": "request_changes",
    "pr_description_issues": [
      {"issue": "No mention of audit logging", "suggestion": "..."}
    ]
  },
  "eval_info": {},
  "is_deployed": false,
  "is_shared_infra_required": false
}
```

After inserting into `tasks`, also insert into `task_competencies` junction table for each competency (same pattern as `multiagent.py` lines 471-480).

Key differences from regular tasks:
- `task_blob.task_type` = `"pr_review"` (new field — existing tasks implicitly have type `"backend"` or `"frontend"` but don't store it; this is the first task type to set it explicitly)
- `task_blob.resources` includes `github_pr` field
- `solutions.steps` contains flaw objects instead of solution step strings. Downstream consumers must check `task_blob.task_type == "pr_review"` before interpreting the `solutions` structure.
- `solutions` has `overall_verdict` and `pr_description_issues` fields
- `answer` is empty string (no solution code — the answer key is in `solutions`)
- `is_deployed` always `false`
- `is_shared_infra_required` always `false`

## CLI Interface

```bash
# Generate a PR review task from pre-existing input files
python -m pr_review_flow \
  --competency-file path/to/competency.json \
  --background-file path/to/background.json \
  --scenarios-file path/to/task_scenarios_pr_review.json

# Options
--env dev|prod          # Supabase environment (default: dev)
--dry-run               # LLM calls still run, output previewed, no GitHub repos or DB records created
```

### Dry-Run Behavior

When `--dry-run` is set:
- LLM generation calls still execute (both phases)
- Evaluation gates still run
- Generated base repo structure and PR files are printed to console for review
- No GitHub repos, branches, or PRs are created
- No Supabase records are inserted
- Generated files are saved locally for inspection

### Local File Saving

All generated content is saved locally under `infra_assets/pr_review_tasks/{task_name}/` with:
- `base_repo/` — all base repo files
- `pr_files/` — PR modified/added files
- `answer_key.json` — the answer key
- `metadata.json` — PR title, description, eval results

This follows the existing pattern in `multiagent.py` (`save_files_locally`) and aids manual review.

### Cost Tracking

LLM token usage is tracked per model across all calls (2 generation + 2 eval) using the same pattern as `scenario_generator/generator.py` (`extract_usage`, `calculate_cost`, `format_cost_summary`). A cost summary is printed at the end of each run.

## What's New vs Reused

| Component | Status |
|-----------|--------|
| `generate_input_files/` | Reused unchanged |
| `scenario_generator/` | Reused — new PR review scenario prompts added to `prompts.py` |
| `pipeline/` | Extended — `--task-type pr_review` option |
| `github_utils.py` | Reused — repo creation, batch uploads |
| `logger_config.py` | Reused |
| `pr_review_flow/` | **New** — orchestrator, prompts, evals, GitHub PR ops, schemas |
| Supabase schema | Unchanged — fits existing `tasks` table |
