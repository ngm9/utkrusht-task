# Implementation Plan: Customer Doc → Per-Task Markdown Extractor

**Branch**: `001-doc-to-task-extractor` | **Date**: 2026-05-12 | **Spec**: [./spec.md](./spec.md)
**Input**: Feature specification from `specs/001-doc-to-task-extractor/spec.md`

This is the **tech-lead cover sheet**. It captures scope, constitution
alignment, module layout, and roadmap. For deeper reading:

- **WHAT** we're building → [`spec.md`](./spec.md)
- **HOW** it works (architecture, agent loop, tools) → [`flow.md`](./flow.md)
- **WHY** this approach (decisions, alternatives rejected) → [`research.md`](./research.md)
- **Current state** (manual workflow we're replacing) → [`current-state.md`](./current-state.md)

## Summary

A new CLI sub-package `task_input_parser/` (invoked as `python -m task_input_parser <brief-path>`)
that converts a customer assessment brief (`.docx` / `.txt` / `.md`) into
one self-contained markdown file per task, ready for downstream
consumption by `multiagent.py generate_tasks`. The technical core is an
LLM agent loop (Claude Sonnet via Portkey, function-calling) with three
tools: `process_image`, `fetch_external_code`, `emit_task`.
Output lands in `tmp/extract_<timestamp>/`; no writes to
`task_input_files/`, Supabase, GitHub, or any shared state.

## Technical Context

**Language/Version**: Python 3.10 (matches the existing repo)

**Primary Dependencies** (all already in `requirements.txt`):
- `python-docx` — `.docx` parsing
- `portkey-ai` — all LLM calls (the agent's orchestration loop)
- (no browser-automation runtime dep — `undetected-chromedriver` is intentionally NOT used; per constitution Principle V the parser does not bypass bot protection)
- `google-api-python-client` — Drive uploads via `non_tech_flow/google_utils.py`
- `click` — CLI surface
- `pydantic` — tool I/O schemas

**Storage**: filesystem only. Outputs in `tmp/extract_<timestamp>/`; cache in
`tmp/parser_cache/`. No DB writes in scope.

**Target Platform**: developer workstations with Chrome installed. Headless
CI is supported (no browser required — `fetch_external_code` is pure HTTP for Gist; CodePen and other bot-protected platforms return a `bot_protected` status without any browser launch).

**Project Type**: CLI sub-package, sibling to `generate_input_files/`,
`scenario_generator/`, `pr_review_flow/`, `non_tech_flow/`.

**Performance Goals**:
- End-to-end run time for a 2-task brief with 1 image + 1 bot-protected URL:
  **under 60 seconds** (spec SC-009).
- LLM token usage: **under $2/brief** (constitution Principle X).

**Scale/Scope**: ~800 lines of Python + ~200 lines of system prompt. Initial
usage ≤10 briefs/day; per-brief cost is the binding constraint.

## Constitution Check

*GATE: Must pass before implementation begins.*

| Principle | How this plan honours it |
|---|---|
| **I. Small Correct Thing First** | US1 (single-task extraction) ships as a complete cut before US2-US5 are built on top. |
| **II. CLI-First with Plugin Registry** | `python -m task_input_parser` matches the existing sub-package convention. No new top-level CLI. |
| **III. Portkey Gateway Only** | The agent's LLM call goes through Portkey with the correct provider header. |
| **IV. Database Safety** | **N/A for this feature** — no Supabase reads or writes in scope. Recorded so future specs that introduce DB writes own the FK-check requirement. |
| **V. Local-First Artifact Saving** | All outputs go to `tmp/extract_<timestamp>/`. No writes to `task_input_files/`, `task_generation_prompts/`, `infra_assets/`, GitHub, or Supabase. |
| **VI. Determinism & Idempotency** | Output dir keyed by run timestamp; resource fetches content-addressed in `tmp/parser_cache/`. Within-run idempotency is the v1 promise; cross-run is deferred (research §8). |
| **VII. Pre-Flight Validation & Schema Discipline** | Every tool I/O is a Pydantic schema. `emit_task` runs the leak-check regex before writing. `fetch_external_code` validates response parses as expected types. |
| **VIII. No Customer-Source Leakage** | `emit_task` rejects markdown that contains a banned code-hosting domain. Regex list co-located with `fetch_external_code`. |
| **IX. Manual Preview Gate** | The feature **is** the preview gate — output lands in `tmp/`, never in shared state. Downstream commit is a separate human-driven step (spec 002). |
| **X. Cost Discipline** | $2.00/brief cap enforced via `task_input_parser/cost.py`; cap check after every LLM response; abort with clear error on overrun. |
| **XI. DRY (with judgment)** | One `fetch_external_code` tool with internal dispatch — not five separate scraper tools. Drive upload reuses `non_tech_flow/google_utils.py`. |
| **XII. Security by Default** | **Does NOT bypass bot protection (Cloudflare, CAPTCHA, etc.)** — see Decision 5 + new constitution bullet. Brief content sanitised before passing to Portkey. Secrets in `.env`. |
| **XIII. Continuous Process Improvement** | Bugs discovered during build land in `docs/known_pipeline_pitfalls.md`. |

**Result**: PASS — no violations, no exceptions to justify.

## Project Structure

### Documentation (this feature)

```text
specs/001-doc-to-task-extractor/
├── spec.md            (WHAT — user stories, requirements, success criteria)
├── current-state.md   (manual workflow today)
├── flow.md            (HOW — architecture, agent loop, tools)
├── research.md        (WHY — decisions, rejected alternatives)
├── plan.md            (this file — scope, constitution, roadmap)
└── tasks.md           (NOT YET — generated by /speckit.tasks next)
```

### Source code (new sub-package at repository root)

```text
task_input_parser/
├── __init__.py
├── __main__.py                 # python -m task_input_parser <brief-path>
├── cli.py                      # Click @command definition
├── ast.py                      # .docx / .md / .txt → BriefAST
├── agent.py                    # LLM loop + tool dispatch
├── cost.py                     # cost accumulator with cap-and-abort
├── leak_check.py               # source-URL leak regex
├── prompts/
│   └── system.md               # the agent's system prompt
└── tools/
    ├── __init__.py             # tool registry exposed to the agent
    ├── image.py                # process_image (extract + Drive upload only — no vision)
    ├── fetch.py                # fetch_external_code (platform dispatch)
    ├── scrape/
    │   ├── __init__.py         # URL-regex platform detection
    │   ├── base.py             # shared cache + validation
    │   └── gist.py             # plain HTTP scraper (the only fully-fetchable platform in v1)
    └── emit.py                 # emit_task (with leak check + inline-note count)
```

No `tests/` directory in this design phase — test scaffolding lives
with the implementation, scoped per atomic task in `tasks.md` once
generated.

## Roadmap

The user stories from `spec.md` map to five sequential ships, each
delivering a complete, deployable slice of value (constitution Principle I).

| Ship | Story | Adds | Stop-point value |
|---|---|---|---|
| **1** | Foundations + US1 | `task_input_parser/` skeleton: `ast.py`, `cli.py`, `cost.py`, `agent.py`, `prompts/system.md` v1, `tools/emit.py`, `leak_check.py`. Agent loop wired with only `emit_task`. | Single-task `.docx` briefs are extracted into one markdown file per brief. Saves ~30 min/brief. |
| **2** | US2 | Extend system prompt to handle multi-task briefs. | Multi-task briefs (the realistic case) are extracted into N markdown files per brief. Saves ~75 min/brief. |
| **3** | US3 | `tools/image.py` (extract + Drive upload only — no vision); extend system prompt. | Image-bearing briefs are handled without manual Drive upload. |
| **4** | US4 | `tools/fetch.py` + `tools/scrape/gist.py`; extend system prompt. | Gist briefs are auto-fetched; CodePen and other bot-protected briefs surface a clear "paste manually" `**Note:**` (no bypass attempted). |
| **5** | US5 | System prompt + emit-format updates so the LLM populates an optional `## Role Description` section when the brief contains role-introducing prose. No new code. | Role context surfaces in each task's markdown when present in the brief. |

The team can stop after any ship and have something useful.

## Complexity Tracking

No constitution violations. No deliberate complexity exceptions to justify.

## Next steps

1. Read [`flow.md`](./flow.md) for the architectural detail.
2. Read [`research.md`](./research.md) for the decisions behind the design.
3. Run `/speckit.tasks` next — it produces `tasks.md` with atomic
   implementation work items derived from this plan.
4. Then `/speckit.implement T001` to begin Ship 1.
