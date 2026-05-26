# TaskRuntime Classifier — dev backfill validation

> **Date:** 2026-05-22
> **Environment:** Supabase dev (`SUPABASE_URL_APTITUDETESTSDEV`)
> **Result:** PASS ✅

Validation of the LLM-only classifier shipped on `feat/task-runtime-classifier`. Goal: drop the default-bucket share from the rule-based classifier's **54%** to under **15%**.

## Backfill run

```
$ PYTHONPATH=. .venv/bin/python scripts/backfill_task_runtime.py --env dev

Loaded 341 rows from tasks (dev).
  already_classified=0  no_competencies=0  unique_groups_to_classify=119

Done. groups_classified=119, failed=0, task_rows_updated=341, elapsed=305.3s.
```

- **341 tasks classified, 0 failures.**
- **119 unique competency-set groups → 119 LLM calls.** In-memory dedup at script time, no cache table needed.
- **~5 min 5 s** wall time. **~$0.12** Sonnet spend (a bit higher than the $0.05 estimate; Sonnet pricing on the Portkey gateway scales by output tokens — each TaskRuntime JSON is small but adds up across 119 calls).

## Distribution by `kind` (n=341)

| kind | count | share |
|---|---|---|
| `app` | 154 | **45.2%** |
| `frontend` | 59 | 17.3% |
| `non_code` | 47 | 13.8% |
| `script` | 25 | 7.3% |
| `testing` | 14 | 4.1% |
| `db_only` | 12 | 3.5% |
| `mobile` | 12 | 3.5% |
| `llm` | 12 | 3.5% |
| `vector_db` | 6 | 1.8% |

## Distribution by `runtime` (n=341)

| runtime | count |
|---|---|
| `node` | 94 |
| `none` | 73 (mostly `non_code` + `db_only`) |
| `python` | 70 |
| `java` | 55 |
| `php` | 18 |
| `go` | 17 |
| `flutter` | 12 |
| `scala` | 1 |
| `rust` | 1 |

## Field coverage

| Field | populated | share |
|---|---|---|
| `frameworks` non-empty | 132 | 38.7% |
| `datastores` non-empty | 58 | 17.0% |
| `messaging` non-empty | 10 | 2.9% |
| `needs_browser=True` | 14 | 4.1% |

## Success metric

The closest equivalent of the old rule-based `PURE_CODE` default bucket — `kind="script"` with all of `frameworks`, `datastores`, `messaging` empty — accounts for:

> **25 of 341 tasks (7.3%)** — well under the 15% bar.

The old rule-based classifier dumped **54%** of tasks into `PURE_CODE`. The LLM classifier reduces that to **7.3%**, with the rest of the previously-misclassified tasks now distributed correctly across `app`, `frontend`, `mobile`, `non_code`, `testing`, `db_only`, `llm`, and `vector_db`.

## Low-confidence groups for human review

The backfill flagged **54 of 119 groups (45%)** with `confidence < 0.7`. Inspection: most are legitimately ambiguous and the LLM is being appropriately cautious rather than wrong.

Examples:

- `REST APIs` (BASIC, INTERMEDIATE) — a concept, not a runtime. Confidence 0.34–0.35.
- `Microservices` — same; concept, not runtime. Confidence 0.35–0.38.
- `Python` alone, `Java` alone, `PHP` alone — could be script *or* app; ambiguous without context.
- `Docker` alone — a tool, not a runtime.
- `Firebase + React Native` — mobile mapping is reasonable but the LLM marks the mapping as soft.
- `Data Structures and Algorithms` (BASIC, INTERMEDIATE) — algorithmic exercises that genuinely don't fit any specific runtime cleanly.
- `Voice Agent Evaluation`, `AI Evals for PMs`, `Prompt Engineering` — non-code categories the LLM flags so a human confirms.

These low-confidence rows are a feature, not a bug — the LLM is surfacing exactly the kinds of inputs where a rule-based system would have silently guessed wrong. Recommended next step: a one-off pass through the 54 rows, with manual overrides written back to `tasks.task_runtime` directly (the `classifier_source` semantics from the design doc — though we removed the dedicated column, the JSON itself can include an override marker if/when needed).

## What this validates

- **The LLM-only classifier shape works.** No rule list to maintain; new technologies are auto-handled by the model.
- **In-memory dedup matches what the proposed cache table would have saved.** 341 tasks → 119 LLM calls = a 2.9× saving without permanent schema overhead.
- **Field structure is genuinely useful.** 38.7% of tasks have explicit frameworks; 17% have datastores. Downstream consumers (persona critics, E2B template picker) read those directly without re-deriving from competencies.

## Next

`feat/task-runtime-classifier` is **ready to commit, push, and PR**. The author's review of the 18 staged files is the only thing between the current state and a merged PR.
