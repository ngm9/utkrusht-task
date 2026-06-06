# Research: Task Content-Quality Evals

**Feature**: 003-task-content-quality-evals
**Date**: 2026-06-04
**Status**: Complete — no NEEDS CLARIFICATION remaining

---

## Decision 1: Package vs Module — New `task_quality/` Package

**Decision**: Add a new top-level **package** `task_quality/` (multi-file), not a single root-level module.

**Rationale**: The feature splits cleanly into four focused concerns — models, deterministic rule registry, semantic LLM judge, and runner — each of which has its own test surface. Collapsing them into one module would produce a ~450 LOC file that violates the "small, well-bounded units" guidance and complicates the per-concern test files. The precedent is already set in this repo: `task_validation/` was refactored from a single file into a package on commit `433d0cf` ("validation layer separated") for exactly the same reason.

**Alternatives considered**:
- Single root-level file `task_quality.py` — matches spec-002's choice but doesn't fit; spec-002 had ~150 LOC, this feature is 3× that and naturally splits.
- Add into `task_validation/` package — wrong layering; `task_validation/` is a Pydantic schema validator that has no LLM dependency, no retry semantics, and runs at insert time. Quality evals need the Portkey client, an LLM round-trip budget, and live inside the retry loop. Merging would entangle insert-time checks with retry-time checks.
- Add into `generators/task/evaluator.py` — wrong layering; that file owns the LLM-critic personas and the retry-feedback composer for the *existing* eval layer. Putting content-quality rules there couples a generic post-LLM gate to one specific pipeline.

---

## Decision 2: Single Consolidated LLM Call vs One Call Per Semantic Concern

**Decision**: One consolidated LLM call per attempt that returns all semantic verdicts at once — `short_overview` 3-part shape, `pre_requisites` framing/relevance, and `outcomes` framing/relevance — in a single structured-output response.

**Rationale**: SC-007 caps the feature at 1 additional LLM call per generation attempt. Three separate calls would triple LLM cost and triple latency for no quality gain — the three concerns share the same task context and the same prompt would describe all three with the same examples. Returning structured output via the existing `EVAL_RESPONSE_SCHEMA` pattern keeps parsing simple.

**Alternatives considered**:
- Three separate calls — easier to prompt-engineer per concern, but violates SC-007 and adds ~6s of latency per attempt.
- Inline the semantic check into the existing `llm_task_eval` critic — entangles a content-hygiene rubric with the realism/difficulty rubric the critic already evaluates, and makes failure-feedback harder to attribute. Keeping them separate lets the operator see which layer rejected the task.

---

## Decision 3: Bullet-Glyph Alphabet for Prefix-Detection

**Decision**: Reject any item in `pre_requisites`, `outcomes`, or `short_overview` whose first non-whitespace token matches the regex:
```
^[\s]*[•‣▪▶◦⁃\-\*–—]\s+
```
which covers:

| Glyph | Unicode | Name |
|-------|---------|------|
| `•` | U+2022 | Bullet |
| `‣` | U+2023 | Triangular bullet |
| `▪` | U+25AA | Black small square |
| `▶` | U+25B6 | Black right-pointing triangle |
| `◦` | U+25E6 | White bullet |
| `⁃` | U+2043 | Hyphen bullet |
| `-` | U+002D | ASCII hyphen-minus |
| `*` | U+002A | Asterisk |
| `–` | U+2013 | En dash |
| `—` | U+2014 | Em dash |

Additionally, reject any item whose first non-whitespace token matches a numbered-list prefix: `^[\s]*(\(?\d{1,2}[\.\)]\s+|\d{1,2}\s*[\-–—]\s+)` (e.g., `"1. "`, `"1) "`, `"(1) "`, `"1 - "`).

**Rationale**: The existing splitter (`infra/utils.py:format_outcomes`) only strips ASCII `- ` and `* `. Unicode bullets (`•`) and dashes are the most common leak in shipped output. Numbered prefixes are a separate failure mode where the LLM emits `"1. Build the API"` instead of `"Build the API"`. Catching both at the same checkpoint avoids a second fix-and-redeploy cycle later.

**Alternatives considered**:
- ASCII-only (`-`, `*`) — leaves the most common defect (`•`) unfixed.
- Strip-and-accept (autofix) — rejected by the v1 architectural choice (block + retry, no autofix). Autofix would silently mask the LLM regression that produced the marker in the first place.

---

## Decision 4: Title Case Strictness Heuristic

**Decision**: `task_blob.title` must satisfy ALL of:
1. Contains at least one space character.
2. Is not equal (case-insensitively, after trimming) to the kebab-case `name` slug.
3. First word is capitalised (first character uppercase).
4. No word of length ≥ 4 is fully lowercase, **unless** it is in the connector set: `{a, an, the, of, to, in, on, for, and, or, with, by, at, vs}` (case-insensitive).
5. Is not fully uppercase (i.e., not screaming-snake or all-caps).

A passing example: `"Design Voice Agent Eval Framework"`.
A failing example: `"voice-agent-eval-framework"` (rules 1, 3, 4 fail), `"VOICE AGENT EVAL FRAMEWORK"` (rule 5 fails).

**Rationale**: The combination of "contains a space" + "first word capitalised" + "long words not all lowercase" catches the kebab-slug failure (no spaces), the lowercase-sentence failure (`"design voice agent eval framework"`), and the all-caps failure. The connector exception prevents over-rejection of legitimate titles like `"Build a Notification Service"` where `"a"` is correctly lowercase.

**Alternatives considered**:
- "Every word capitalised" — over-strict; rejects legitimate connectors and reads as Press-Release Title Case which is not what we want.
- LLM judge for title formatting — wasteful; the heuristic above catches the defects the operator has actually seen, deterministically, in microseconds.

---

## Decision 5: Question Length Bounds — MIN_QUESTION_CHARS=120, MAX_QUESTION_CHARS=1500

**Decision**: Reject `question` (the parsed string field) if `len(question.strip()) < 120` or `> 1500`.

**Rationale**: The cycle-detection reference example provided by the user is roughly 330 characters (excluding line breaks). The IoT-platform sample task in `data/generated/tasks/python_fastapi_system_design_intermediate_example.json` is ~1100 characters, and qualifies as a legitimate longer question (system-design tasks need more setup). 1500 leaves headroom for the longer-format tasks while still rejecting multi-page question bodies. 120 rejects effectively-empty questions (`"Build it."` is 11 chars) while accepting concise ones.

These constants live in `task_quality/rules.py` as module-level names so they can be tuned without changing the rule's logic. A future change to the cap is a 1-line PR.

**Alternatives considered**:
- Word-count instead of char-count — char-count is more reliable across languages and avoids tokenisation edge cases; the user thinks in terms of "candidate reading load" which scales with characters more than words.
- Soft cap with LLM verdict — wasteful; question-length is a pure measurement problem with no semantic nuance.

---

## Decision 6: Relevance Check — LLM Judge, Not Deterministic Word-Overlap

**Decision**: The relevance check for `pre_requisites` and `outcomes` items (FR-010) is performed by the consolidated semantic LLM call, not by a deterministic word-overlap heuristic.

**Rationale**: A word-overlap heuristic over `name`/`question`/competency names produces high false positives (a generic bullet like `"Familiarity with Python"` would pass for any Python task) and high false negatives (a task-specific bullet that paraphrases the question without sharing tokens would fail). The LLM, with the task context in hand, can judge whether each bullet meaningfully anchors to the specific task. The cost is bounded — this check is folded into the single consolidated LLM call from Decision 2.

**Alternatives considered**:
- Pure word-overlap with stop-word filter — fast but unreliable; produces noisy retry-loop feedback.
- Embedding similarity between bullet and task — adds an embedding-model dependency this repo doesn't currently have at this layer.
- Skip relevance entirely in v1 — defers a primary defect class (generic boilerplate prerequisites) and breaks SC-002-class confidence in the layer.

---

## Decision 7: Semantic-Judge Transport-Error Behaviour

**Decision**: If the consolidated LLM call to the semantic judge fails for a non-content reason (transport error, 5xx from Portkey, JSON parse failure on a successful HTTP response), the runner raises a plain `Exception` ("content-quality semantic judge unreachable: …") that aborts the run. The deterministic rule results are logged for the operator but no Supabase or GitHub write occurs.

**Rationale**: An infra error during the semantic call is not something the LLM regeneration retry can fix — regenerating the task produces a new candidate but the next attempt would still hit the same unreachable judge. Falling through to "skip the semantic check and accept" silently degrades quality. Counting it as RETRY just burns the retry budget on an unrelated failure. Aborting is the cheapest, clearest path: operator sees the infra error, retries when infra recovers.

**Alternatives considered**:
- Treat as RETRY (like a content failure) — wastes the retry budget on an unfixable failure mode and conflates infra problems with content problems in the operator's mental model.
- Skip the semantic check and accept the task — silently lowers quality during outages and is hard to detect after the fact.
- Promote to `EvalGateError` — wrong taxonomy; `EvalGateError` means "quality failed after exhausting retries", not "infra was unreachable". Using it would muddy the operator's understanding of what failed.

---

## Decision 8: Retry-Feedback Composition

**Decision**: Extend the existing `generators/task/evaluator.py:build_retry_feedback(hollow_reasons, eval_info)` signature to accept an optional `quality_report: QualityReport | None` parameter and, when provided, append its `feedback_text` to the existing parts.

**Rationale**: Single composer means the LLM sees one unified feedback message per retry, in a consistent format, no matter which layer (`hollow`, `LLM critic`, `E2B gate`, or `content quality`) flagged the problem. Operator and prompt-engineering both benefit from one feedback shape rather than two. The existing parts-list pattern (`parts = [...] ; ... ; return "\n\n".join(parts)`) extends naturally.

**Alternatives considered**:
- New separate `build_quality_feedback()` function and concatenate at the creator.py level — duplicates the join logic and risks divergence between the two feedback formats over time.
- Embed quality violations into `eval_info["task_eval"]["issues"]` and let the existing path render them — overloads the meaning of `task_eval` (which is the LLM critic verdict) and corrupts logged eval data with content-hygiene noise.

---

## Decision 9: GateOutcome-Style Return Instead of Exception-on-Failure

**Decision**: The public `run_quality_for_attempt(candidate, attempt) -> tuple[QualityOutcome, str]` returns `(QualityOutcome.PASS, "")` or `(QualityOutcome.RETRY, feedback_text)` — it does **not** raise on content failure. Only infra errors raise.

**Rationale**: The existing E2B gate uses exactly this shape (`generators/task/gate.py:run_gate_for_attempt → (GateOutcome, str)`). Mirroring it lets `creator.py` consume both layers with the same `if outcome == RETRY: feedback = ...; continue` block. Failure to mirror would mean two different control-flow shapes for two adjacent gate layers — high cognitive load with zero benefit.

**Alternatives considered**:
- Raise `TaskQualityError` on every failure — would require try/except at the call site for every retry, inconsistent with the gate's pattern, and gives "failed to clear quality" the same exceptional weight as "infra is broken".
- Return a plain `QualityReport` and let `creator.py` decide — pushes the gate/pass policy into the orchestrator, which is exactly what the existing gate abstraction was created to avoid.

---

## No Open Questions

All NEEDS CLARIFICATION items from plan.md are resolved. Proceed to Phase 1.
