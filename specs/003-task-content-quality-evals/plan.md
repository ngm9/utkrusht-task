# Implementation Plan: Task Content-Quality Evals

**Branch**: `003-task-content-quality-evals` | **Date**: 2026-06-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-task-content-quality-evals/spec.md`

---

## Summary

Add a third validation layer — **content-quality evals** — that runs after the LLM critic and E2B build/test gate have passed in `generators/task/creator.py`, but before any GitHub repository, Gist, or Supabase row is created. A new `task_quality/` package owns a single rule registry covering deterministic checks (bullet-glyph prefixes, `**X**:` markers, blank/duplicate items, `short_overview` count, `task_blob.title` slug shape, `question` length cap) and one consolidated LLM-judge call for the semantic checks (`short_overview` 3-part shape, `pre_requisites` and `outcomes` task-relevance and framing). Violations are aggregated into one structured report and fed back through the existing retry loop using the same `EvalGateError`-on-exhaustion semantics as the gate. No new entry points, no DB schema changes, no autofix.

---

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: Pydantic v2 (already in `requirements.txt`), `infra.evals` (existing — reuses `eval_openai_client`, `EVAL_MODEL`, `EvalGateError`), `infra.schemas` (existing — extended with one new structured-output schema), `infra.logger_config` (existing)
**Storage**: None — this layer is stateless and writes nothing
**Testing**: pytest (already in use); unit tests cover every deterministic rule and the runner with a mocked LLM; one integration test exercises the real LLM call on a fixture task
**Target Platform**: Developer workstation / CI pipeline (Linux + Windows)
**Project Type**: Internal library package — new top-level package `task_quality/`, mirroring the shape of `task_validation/`
**Performance Goals**: At most **1 additional LLM call per generation attempt** (SC-007); deterministic checks run in well under 100 ms per task
**Constraints**:
- No autofix — every failure must regenerate (per "go with A" decision in brainstorming)
- No new CLI commands; this layer is invoked from `creator.py` only
- Coding pipeline only — PR-review and non-tech flows out of scope (FR-019)
- Pre-existing Pydantic shape checks in `task_validation/` remain unchanged (FR-020)
**Scale/Scope**: 1 new package (~5 files, ~450 LOC), ~30 LOC change in `creator.py`, one new prompt + one new JSON schema, ~3 test files

---

## Constitution Check

*GATE: Pre-Phase-0. Re-checked post-design below.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Small Correct Thing First | ✅ PASS | One new package + one integration point; no existing layer is replaced |
| II. CLI-First / Plugin Registry | ✅ PASS | Internal library, not a CLI; doesn't touch the plugin registry |
| III. Portkey Gateway Only | ✅ PASS | Reuses `eval_openai_client` (already Portkey → OpenAI) — no direct provider calls |
| IV. Database Safety | ✅ PASS | Runs before Supabase insert; no DB writes of its own |
| V. Local-First Artifact Saving | ✅ PASS | Runs before any local save or external write |
| VI. Pipeline Determinism & Idempotency | ✅ PASS | Same input → same deterministic verdicts; LLM verdicts use `temperature=0` defaults via existing Portkey config |
| VII. Pre-Flight Validation & Schema Discipline | ✅ PASS | This feature *extends* the pre-flight gate principle (FR-001, FR-002) |
| VIII. No Customer-Source Leakage | ✅ N/A | Reads task fields, no candidate-facing artifacts created |
| IX. Manual Preview Gate | ✅ N/A | Internal to the pipeline, not a parser preview stage |
| X. Cost Discipline | ✅ PASS | Hard ceiling of 1 LLM call per attempt (SC-007); the same `gpt-5-nano` model already used by `infra/evals.py` |
| XI. DRY | ✅ PASS | Single rule registry (FR-018); reuses Portkey client + JSON-schema infra |
| XII. Security by Default | ✅ PASS | Read-only; rejects malformed content before persistence |
| XIII. Continuous Process Improvement | ⚠️ REQUIRED | After implementation, add a pitfall entry to `docs/known_pipeline_pitfalls.md` documenting the bullet-marker class of defects this layer catches |

**Gate result**: PASS. No violations. XIII is a required action in the implementation tasks, not a blocker.

**Post-design re-check**: All principles still pass. The chosen design (one package, one LLM call per attempt, gate-style outcome enum) is the minimum-complexity correct solution.

---

## Project Structure

### Documentation (this feature)

```text
specs/003-task-content-quality-evals/
├── spec.md             ← already written
├── plan.md             ← this file
├── research.md         ← Phase 0 output (to be created)
├── data-model.md       ← Phase 1 output (to be created)
├── quickstart.md       ← Phase 1 output (to be created)
├── contracts/
│   └── content-quality-api.md   ← Phase 1 output (to be created)
├── checklists/
│   └── requirements.md          ← Phase 1 output (to be created)
└── tasks.md            ← Phase 2 output (/speckit.tasks — not yet created)
```

### Source Code

```text
task_quality/                 ← NEW package
├── __init__.py               ← public API surface (matches task_validation/__init__.py style)
├── models.py                 ← Rule, Violation, QualityReport, QualityOutcome enum
├── rules.py                  ← deterministic rule registry (single source of truth, FR-018)
├── semantic.py               ← LLM-judge wrapper: short_overview shape + framing/relevance
├── runner.py                 ← evaluate_task_quality(task) → QualityReport; run_quality_for_attempt()
└── exceptions.py             ← (optional) TaskQualityError if needed beyond report-style returns

infra/
└── schemas.py                ← MODIFIED: add CONTENT_QUALITY_RESPONSE_SCHEMA (one new structured-output schema)

generators/task/
├── creator.py                ← MODIFIED: invoke run_quality_for_attempt() between gate pass and persistence
└── evaluator.py              ← MODIFIED: extend build_retry_feedback() to incorporate QualityReport.feedback_text

tests/
├── unit/
│   ├── test_task_quality_rules.py        ← each deterministic rule, happy + sad paths
│   ├── test_task_quality_runner.py       ← runner with mocked semantic LLM call
│   └── test_task_quality_feedback.py     ← retry-loop feedback string composition
└── integration/
    └── test_task_quality_integration.py  ← one real LLM call on a fixture task

docs/
└── known_pipeline_pitfalls.md            ← MODIFIED: add bullet-marker / kebab-title entries
```

**Structure Decision**: A new `task_quality/` **package** (not a single module) — mirroring `task_validation/`. The rule registry, the semantic judge, the runner, and the models are each focused enough to warrant their own file; collapsing them would produce a ~450-LOC module that violates the "small, well-bounded units" guidance. No subclass-per-flow variant is needed for v1 (coding only).

---

## Architecture & Data Flow

```
                  generators/task/creator.py (retry loop)
                  ┌────────────────────────────────────────┐
                  │ generate_task_with_code()              │
                  │   │                                    │
                  │   ▼                                    │
                  │ is_task_hollow()  ──fail──┐            │
                  │   │                       │            │
                  │   ▼                       │            │
                  │ run_evaluations()         │            │
                  │ (LLM critics)  ──fail──┐  │            │
                  │   │                    │  │            │
                  │   ▼                    │  │            │
                  │ run_gate_for_attempt() │  │            │
                  │ (E2B build/test) ─fail─┤  │            │
                  │   │                    │  │            │
                  │   ▼                    │  │            │
                  │ ╔═══════════════════╗  │  │   ◄── NEW  │
                  │ ║ run_quality_for_  ║  │  │            │
                  │ ║   attempt()       ║──┼──┼─ fail      │
                  │ ║                   ║  │  │  (build    │
                  │ ║ ┌───────────────┐ ║  │  │   feedback,│
                  │ ║ │ deterministic │ ║  │  │   continue)│
                  │ ║ │ rules (rules. │ ║  │  │            │
                  │ ║ │ py)           │ ║  │  │            │
                  │ ║ └───────┬───────┘ ║  │  │            │
                  │ ║         ▼         ║  │  │            │
                  │ ║ ┌───────────────┐ ║  │  │            │
                  │ ║ │ semantic LLM  │ ║  │  │            │
                  │ ║ │ judge (1 call)│ ║  │  │            │
                  │ ║ │ semantic.py   │ ║  │  │            │
                  │ ║ └───────┬───────┘ ║  │  │            │
                  │ ║         ▼         ║  │  │            │
                  │ ║ QualityReport     ║  │  │            │
                  │ ║ aggregated        ║  │  │            │
                  │ ╚═══════════════════╝  │  │            │
                  │   │                    ▼  ▼            │
                  │   │       build_retry_feedback(reasons,│
                  │   │             eval_info, report)     │
                  │   │                    │               │
                  │   │           ◄────────┘ (retry)       │
                  │   ▼                                    │
                  │ persistence (GitHub, Gist, Supabase)   │
                  └────────────────────────────────────────┘
```

**Key flow rules:**

1. Quality eval runs **after** the gate, **before** persistence. The LLM-critic and gate already cleared semantic-quality and build-correctness; this layer only catches content-hygiene defects that those layers don't score on.
2. The runner returns a `QualityOutcome` enum (`PASS` / `RETRY`) plus a feedback string — exactly the same shape as `run_gate_for_attempt`. The retry loop in `creator.py` consumes both the same way: if `RETRY`, continue the loop with feedback; if budget exhausted, raise `EvalGateError`.
3. Deterministic rules run first and short-circuit nothing — every rule runs on every task so the report aggregates **all** violations (FR-015). The semantic LLM judge always runs (one call), even when deterministic checks already found violations — the LLM's framing-and-shape verdict is composed into the same report so the LLM regeneration prompt sees every problem in one pass.
4. The semantic LLM uses the existing `eval_openai_client` from `infra/evals.py` and the `EVAL_MODEL` constant (`gpt-5-nano-2025-08-07`). No new client, no new env var.

---

## Implementation Phases

### Phase A — Core Models + Deterministic Rule Registry (`task_quality/models.py`, `rules.py`)

1. Define `Violation` dataclass: `field_path: str`, `rule_name: str`, `actual_value: Any`, `reason: str`.
2. Define `QualityReport` dataclass: `passed: bool`, `violations: list[Violation]`, `feedback_text: str` (lazy-computed).
3. Define `QualityOutcome` enum: `PASS`, `RETRY` — mirrors `GateOutcome`.
4. Define `Rule` protocol or dataclass: `name: str`, `applies_to: list[str]`, `check(task) -> list[Violation]`.
5. Implement deterministic rules as a single registry in `rules.py`:
   - `R_NoBulletGlyphPrefix` — `pre_requisites`, `outcomes`, `short_overview` items
   - `R_NoResidualBoldMarker` — same three fields; regex `\*\*[^*]+\*\*\s*:`
   - `R_NoBlankOrDuplicateItem` — same three fields
   - `R_ShortOverviewExactlyThree` — `short_overview` count == 3
   - `R_TitleNotKebabSlug` — `task_blob.title` not equal to `name` and contains at least one space
   - `R_TitleIsTitleCase` — first word capitalised, no fully-lowercase tokens (excluding small connectors)
   - `R_QuestionLengthInRange` — `question` between `MIN_QUESTION_CHARS` and `MAX_QUESTION_CHARS`
   - `RULES: list[Rule] = [R_NoBulletGlyphPrefix, R_NoResidualBoldMarker, ...]` — the single source of truth (FR-018).
6. Implement `run_deterministic_rules(task: dict) -> list[Violation]` that iterates `RULES` and concatenates.

### Phase B — Semantic LLM Judge (`task_quality/semantic.py`, `infra/schemas.py`)

1. Add `CONTENT_QUALITY_RESPONSE_SCHEMA` to `infra/schemas.py`. Shape:
   ```json
   {
     "short_overview_shape": {
       "matches_three_part_shape": true|false,
       "issues": [{"position": 0|1|2, "expected": "describes task artifact", "actual_summary": "..."}]
     },
     "pre_requisites_framing": {
       "violations": [{"index": int, "reason": "generic / not task-anchored / not a complete sentence"}]
     },
     "outcomes_framing": {
       "violations": [{"index": int, "reason": "..."}]
     }
   }
   ```
2. Implement `judge_task_content_quality(task: dict) -> list[Violation]` in `semantic.py`:
   - Build one consolidated prompt covering all three semantic concerns.
   - Inject task title, question, competency names, and the three list fields.
   - Call `eval_openai_client.responses.create(model=EVAL_MODEL, ...)` with the structured-output schema.
   - Parse the response and convert each issue into a `Violation` keyed by the appropriate field path.
3. The prompt explicitly defines the 3-part `short_overview` shape (artifact / goal / outcome) with the reference example from the spec, and explicitly defines what "task-anchored" means for `pre_requisites` and `outcomes`.

### Phase C — Runner + Retry-Loop Integration

1. `runner.py`:
   - `evaluate_task_quality(task: dict) -> QualityReport` — runs deterministic rules + semantic judge, aggregates violations, composes `feedback_text`.
   - `run_quality_for_attempt(candidate: dict, attempt: int) -> tuple[QualityOutcome, str]` — wraps `evaluate_task_quality` in the gate-style return shape so `creator.py` consumes it uniformly.
2. Compose `feedback_text` to name each field path, rule, and offending value (FR-016). Order: deterministic rules first (cheapest to fix), semantic last.
3. `task_quality/__init__.py` exports the public API: `evaluate_task_quality`, `run_quality_for_attempt`, `QualityReport`, `QualityOutcome`, `Violation`.

### Phase D — Wire Into `creator.py`

1. After `run_gate_for_attempt` returns `GateOutcome.PASS`, call `run_quality_for_attempt(candidate, attempt)`.
2. If outcome is `RETRY`:
   - Set `last_failure` to include quality violations (e.g., extend `eval_info` with a `"quality_report"` key).
   - Set `feedback = quality_feedback` (or concatenate with any gate feedback if both layers had something to say — but gate would have failed and short-circuited first, so this should not occur).
   - `continue` the retry loop.
3. If outcome is `PASS`, fall through to persistence as today.
4. Extend `generators/task/evaluator.py:build_retry_feedback(...)` to optionally accept a `quality_report` and append its feedback to the existing parts.

### Phase E — Tests

1. `tests/unit/test_task_quality_rules.py`:
   - One test per deterministic rule covering the happy path and at least one failure mode.
   - One test exercising the aggregation: multiple rules firing simultaneously produce one report with all violations.
2. `tests/unit/test_task_quality_runner.py`:
   - Mocks `judge_task_content_quality` to return a fixed list of violations; asserts `QualityReport` aggregates correctly.
   - Asserts `feedback_text` mentions every field path and reason.
   - Asserts `run_quality_for_attempt` returns the right `QualityOutcome` for pass and fail cases.
3. `tests/unit/test_task_quality_feedback.py`:
   - Verifies `build_retry_feedback(hollow=[], eval_info=None, quality_report=<failing>)` produces a feedback string that the LLM can act on (smoke check via substring assertions).
4. `tests/integration/test_task_quality_integration.py`:
   - Calls `judge_task_content_quality` on a known-bad fixture task and asserts the LLM identifies the expected `short_overview` shape miss (single integration test to keep cost minimal).

### Phase F — Documentation + Pitfalls

1. Add an entry to `docs/known_pipeline_pitfalls.md`:
   - "Residual `**X**:` markers in `outcomes` / `pre_requisites` items — symptom: candidates see bold markup in plain-text rendering; cause: LLM emits Markdown headings in items; prevention: handled by `task_quality.rules.R_NoResidualBoldMarker`."
   - "Kebab-case `task_blob.title` (e.g., `offline-first-field-app-design`) — symptom: title looks like a slug to candidates/recruiters; cause: fallback from missing `title` to `name`; prevention: handled by `task_quality.rules.R_TitleNotKebabSlug` and `R_TitleIsTitleCase`."

---

## Open Decisions (deferred to `research.md`)

These need to be settled in Phase 0 before Phase A starts:

1. **`MAX_QUESTION_CHARS` and `MIN_QUESTION_CHARS`**: the spec asserts the rule (FR-014); the concrete cap needs to be calibrated against the reference example (the cycle-detection question is ~330 chars excluding line breaks). Tentative: `MIN=120`, `MAX=1500`. Decision in `research.md`.
2. **Title-case strictness**: how lenient is "Title Case"? Lock the regex / heuristic in `research.md` (proposed: first character upper, ≥ 1 space, no token is fully lowercase unless it is in a short connector set `{a, an, the, of, to, in, on, for, and, or, with}`).
3. **Bullet-glyph alphabet**: the spec mentions `•`, `-`, `*`. Confirm whether `–` (en-dash), `—` (em-dash), `▪`, `‣`, numbered prefixes (`1.`, `1)`) should also be rejected — likely yes; decide and lock in `research.md`.
4. **Semantic-judge fallback when the LLM call fails**: should a transport error count as RETRY (regenerate the task) or be surfaced as an infra error that aborts the run? Default: treat as infra error; mirror `infra/evals.py` behaviour. Confirm in `research.md`.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Semantic judge accuracy is brittle — it could wrongly flag a perfectly valid `short_overview` | Single-call prompt with explicit reference example from the spec; integration test on a fixture; failure mode is "extra retry", not "lost work", because every retry produces fresh artifacts |
| Retry loop runs out of budget because deterministic rules force regeneration that the LLM doesn't fix | The existing `EvalGateError` already surfaces this; no GitHub or Supabase write occurs in that path. Operator alerts on the recurring failure mode and the rule can be relaxed if it proves unrealistic |
| Adding one more LLM call per attempt slows generation | Bounded by SC-007 to **one** additional call per attempt; the model is `gpt-5-nano`, which is the same one already used by `infra/evals.py`. Estimated added cost: < 2 s per attempt |
| New rules added later create flakiness in existing tests | Rules live in a single registry (`task_quality/rules.py`); test file `test_task_quality_rules.py` is structured one-test-per-rule so adding a rule doesn't require touching unrelated tests |
| Integration with `creator.py` breaks the retry loop semantics | Mirror the existing `run_gate_for_attempt` contract exactly; `creator.py` change is ~5 lines (one `if outcome == RETRY` block) |

---

## Complexity Tracking

*No Constitution violations requiring justification.*

The one piece of added complexity — a new top-level package — is justified by FR-018 (single-file rule registry) and the same package-shape precedent already set by `task_validation/`.
