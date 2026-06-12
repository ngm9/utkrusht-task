# Pipeline Tracing & Training-Data Capture

- **Date:** 2026-06-11
- **Branch:** `feat/pipeline-tracing`
- **Status:** IMPLEMENTED (Steps 0–4 done, uncommitted on branch; pending only a live `run_pipeline` verification + user review). Portkey metadata-tag + litellm/DSPy tracing deferred.
- **Author:** generation pipeline work (session continuation)

## Goal

Capture, for every pipeline run, a complete structured trace of each stage —
and especially each LLM call (full input + output + metadata) — durably stored
in a form directly usable as **future training data** (SFT / eval / distillation).

This is an observability + dataset-capture problem, not just logging: the
primary consumer is a future model-training corpus of `(input, output)` pairs
across the task-generation pipeline, filterable by stage / model / success.

## Decisions (locked)

| Decision | Choice |
|---|---|
| Durable store | **S3** (partitioned JSONL) + **local JSONL always** + Portkey metadata tags |
| Phase-1 scope | **Task-gen pipeline only** (stages below); other flows deferred |
| Capture strategy | Instrument a **shared traced-client factory** (auto-capture every LLM call) — not per-call-site logging |

## Trace-point inventory (WHERE) — every LLM call routes through Portkey

| # | Stage | Module | I/O captured | Model |
|---|---|---|---|---|
| 1 | Input-file gen | `generators/input_files/generator.py` (×3) | competency → input JSON | gpt-* |
| 2 | Scenario gen + eval | `generators/scenarios/generator.py` (×3) | competency → scenarios; eval verdict | gpt-5.4 |
| 3 | Prompt gen | `generators/prompts/agent.py` (litellm) | scenario → agent prompt | (litellm) |
| 4 | **Classifier** | `infra/classifier/llm_classifier.py` | competencies → `TaskTemplateMatch` | claude-sonnet-4-6 |
| 5 | Runtime resolve (no LLM) | `runtime_resolver.resolve_plan` | → `ResolvedPlan` (template/persona) | — |
| 6 | Task gen | `generators/task/creator.py:213` | prompt → task JSON + code_files | claude/gpt |
| 7 | Task eval | `infra/evals.py:564` | task → pass / blocking_issues | gpt-5-nano |
| 8 | Code eval | `infra/evals.py:622` | code → pass / blocking_issues | gpt-5-nano |
| 9 | Quality autofix | `task_quality/semantic.py:177` | task → autofixed fields | gpt-* |
| 10 | E2B gate (no LLM) | `infra/e2b/sandbox_eval.py` | code + run.sh → verdict + stdout_tail | — |
| 11 | Solution gen | `creator.generate_answer_code_and_steps` | task → solution files + steps | gpt-5.4 |
| 12 | Persistence (no LLM) | `creator.py` | → task_id, repo URLs, gist | — |

Deferred (own LLM calls, out of phase-1 scope): `flows/pr_review`,
`flows/non_tech`, `task_builder`, `task_input_parser`, `infra/utils.py`.

## Schema (WHAT) — training-ready

**LLM-call record** (one JSONL line per call):

```jsonc
{
  "trace_id", "run_id", "task_id", "parent_span_id",
  "stage", "module", "function",
  "provider",            // "anthropic" | "openai"
  "model", "call_type",  // "responses" | "chat.completions"
  "request":  { "system", "messages|input", "params": { reasoning_effort, max_tokens, json_schema } },
  "response": { "raw_text", "parsed_json", "finish_reason" },
  "usage":    { "input_tokens", "output_tokens" },
  "latency_ms", "attempt", "retries",
  "status",   // "ok" | "error" | "timeout"
  "error", "ts_start", "ts_end", "git_sha", "schema_version"
}
```

**Stage-span record:** `{ run_id, stage, status, duration_ms, input_summary, output_summary, error }`
(e.g. classifier → match; gate → verdict).

**Run manifest:** `{ run_id, competencies, proficiency, env, started_at, ended_at, outcome, stages[], model_versions, git_sha }`.

The LLM-call records are the gold corpus: clean `(prompt, completion)` pairs +
metadata to filter by stage / model / success.

## Instrumentation (HOW) — instrument once, not at 14 sites

Key fact: nearly every client is the same shape —
`openai.OpenAI(base_url=PORTKEY_GATEWAY_URL, default_headers=createHeaders(...))`,
calling `.responses.create` / `.chat.completions.create`.

New package `infra/tracing/`:

- **`context.py`** — contextvars (`run_id`, `task_id`, `stage`, `attempt`) +
  `trace_stage("classifier")` context manager for stage spans.
- **`client.py`** — `make_traced_openai(provider, **kw)` returns an
  `openai.OpenAI` whose `.responses.create` / `.chat.completions.create` are
  wrapped to read context, record request, call through, record
  response/usage/latency/retries/errors, and emit a trace event. **One wrapper
  captures every LLM call's I/O.**
- **`sink.py`** — append JSONL to `.task_agent_runs/run-<ts>/traces/`
  (`llm_calls.jsonl`, `stages.jsonl`, `manifest.json`); buffered, **failure-isolated**
  (a sink error must NEVER fail or slow the pipeline), **secret-redacting**.
- **`s3.py`** — end-of-run upload, **env-gated** on `TRACE_S3_BUCKET`
  (no bucket → local-only, no failure).

Wiring:

1. Replace the ~6 task-gen client builders with `make_traced_openai(...)`:
   `infra/classifier/llm_classifier.py`, `generators/scenarios/generator.py`,
   `generators/input_files/generator.py`, `infra/evals.py`,
   `generators/task/_clients.py`, `task_quality/semantic.py`. litellm callback
   for `generators/prompts/agent.py`.
2. Add `trace_id` + `metadata` (run_id/stage/task_id) to every `createHeaders(...)`
   → Portkey's own logs become a correlated second copy, queryable in its
   dashboard for free.
3. Wrap the 12 stages in `trace_stage(...)`, incl. non-LLM stages (resolve_plan,
   e2b gate, persistence). Thread the existing `.task_agent_runs/run-<ts>` id
   as `run_id`.

## Storage (the "better way") — tiered

- **Tier 1 — local JSONL (always):** `.task_agent_runs/run-<ts>/traces/` —
  co-located with existing stage logs, zero-dependency, inspectable.
- **Tier 2 — S3 (training corpus):** end-of-run upload, ML-partitioned:
  `s3://<bucket>/traces/dt=<YYYY-MM-DD>/run=<run_id>/{llm_calls,stages}.jsonl` +
  `manifest.json` → loadable straight into pandas / HF datasets / Athena.
- **Tier 3 — Portkey metadata tags (free):** via the `createHeaders` change;
  optional thin Supabase index (`run_id → s3_path, outcome`) for discovery +
  joins to `tasks`.

Future option: model traces as OpenTelemetry GenAI spans for standard tooling;
start custom-JSONL (simpler + directly training-ready) and keep an OTel export
door open.

## Rollout

0. **Setup (DONE):** branch `feat/pipeline-tracing` off latest `origin/main`;
   session fixes restored (timeout / gate-retry / passed-strictness / nodejs
   prompt + tests); GitNexus index refresh.
1. **DONE** — `infra/tracing/` (`context`, `client`, `sink`, `s3`, `__init__`) + `tests/test_tracing.py` (10 tests). Code-reviewed + fixed.
2. **DONE** — `boto3` already in requirements; S3 env-gated on `TRACE_S3_BUCKET`; `s3.py` region aligned to `S3_REGION` (Utkrushta convention); `.env` got `TRACE_S3_BUCKET=aptitudetestsdev` + `TRACE_S3_PREFIX=traces` (creds/region already shared). litellm + Portkey metadata-tag DEFERRED.
3. **DONE** — wrapped 6 task-gen clients with `trace_client(...)`: classifier, scenarios, input_files, evals, `_clients` (×2). `task_quality/semantic.py` covered transitively. litellm/`agent.py` DEFERRED (needs callback).
4. **DONE** — `trace_stage` spans in `creator.py` (classifier/task_gen/eval/gate/quality/solution) + `set_attempt`/`set_task_id`; `cli/generate.py` opens `trace_run(TRACE_RUN_ID)` + finally(`write_manifest`+`upload_run_traces`); `run_pipeline.py` injects `TRACE_RUN_ID` + forces `PIPELINE_TRACING_ENABLED` on (task stage) / off (others). Verified: 312 tests pass, end-to-end smoke (real run-dir path), env-handoff unit test, adversarial review (2 robustness fixes applied).
5. **PENDING (user's call)** — verify on a real `run_pipeline` run. Creates real GitHub/Supabase artifacts + uploads to the shared `aptitudetestsdev` S3 bucket + hits E2B; not run autonomously. Command: `.venv/bin/python run_pipeline.py --name "<combo>" --proficiency <LEVEL> --env dev --count 1`, then inspect `.task_agent_runs/run-<ts>/traces/{llm_calls,stages}.jsonl` + `s3://aptitudetestsdev/traces/dt=.../run=<ts>/`.
6. (Later) extend to pr_review / non_tech / task_builder flows + litellm/DSPy prompt-gen callback + Portkey metadata tags.

## Open items

- **S3 (RESOLVED):** reuses Utkrushta's already-shared creds/region in `.env`;
  `TRACE_S3_BUCKET=aptitudetestsdev` set (local-only — `.env` is gitignored), so dev
  runs upload to the shared dev bucket under `traces/dt=…/run=…/`. (Review note: the
  prefix is flat across devs — fine for an aggregate corpus; revisit if per-dev
  isolation is wanted. To disable uploads, unset `TRACE_S3_BUCKET`.)
- Unrelated WIP (CLAUDE.md, `python_redis_intermediate_prompt.py` rewrite,
  `creator.py` / `evaluator.py` / `evals.py`) remains parked in
  `stash@{0} "fix retry eval gate"` — not carried onto this branch; sort
  separately.
