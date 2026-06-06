# Contract: `task_quality` Public API

**Module**: `task_quality` (top-level package, imported by `generators/task/creator.py`)
**Date**: 2026-06-04

This document defines the public interface of the `task_quality` package. Symbols below are the stable contract; everything else is internal.

---

## Exports (from `task_quality/__init__.py`)

```python
from task_quality.models import (
    Violation,
    QualityReport,
    QualityOutcome,
    Rule,                       # Protocol
)
from task_quality.runner import (
    evaluate_task_quality,
    run_quality_for_attempt,
)
from task_quality.rules import RULES   # the registry (exposed for introspection + tests)
```

---

## Data Types

### `Violation` (dataclass, frozen)

```python
@dataclass(frozen=True)
class Violation:
    field_path: str        # e.g., "task_blob.title", "outcomes[2]"
    rule_name: str         # stable identifier
    actual_value: Any      # truncated for strings, summarised for lists
    reason: str            # human-readable
```

### `QualityReport` (dataclass)

```python
@dataclass
class QualityReport:
    passed: bool
    violations: list[Violation]
    feedback_text: str      # empty when passed == True
    llm_call_count: int     # 0 (infra error before call) or 1 (success)
```

### `QualityOutcome` (Enum)

```python
class QualityOutcome(Enum):
    PASS = "pass"
    RETRY = "retry"
```

### `Rule` (Protocol)

```python
class Rule(Protocol):
    name: str
    applies_to_fields: tuple[str, ...]
    def check(self, task: dict) -> list[Violation]: ...
```

---

## Functions

### `evaluate_task_quality(task: dict) -> QualityReport`

Run all deterministic rules in `RULES`, then run the consolidated semantic LLM judge, aggregate violations into one `QualityReport`, and return it.

**Raises**: `Exception` with a clear message if the semantic LLM call fails for non-content reasons (transport / parse). Does NOT raise for content violations — those go into `report.violations`.

**Returns**: `QualityReport`. `report.passed` is True iff `report.violations` is empty.

**Side effects**:
- One `responses.create` call against the Portkey gateway (Decision 2 in research.md).
- No DB access, no filesystem writes, no logging beyond a single info line on completion.

```
evaluate_task_quality(candidate)
  ├── for rule in RULES: violations += rule.check(candidate)        # deterministic, fast
  ├── violations += judge_task_content_quality(candidate)            # one LLM call
  └── return QualityReport(passed=..., violations=..., feedback_text=..., llm_call_count=...)
```

---

### `run_quality_for_attempt(candidate: dict, attempt: int) -> tuple[QualityOutcome, str]`

Wraps `evaluate_task_quality()` in the gate-style return shape so `generators/task/creator.py` consumes it uniformly with `run_gate_for_attempt`.

**Returns**:
- `(QualityOutcome.PASS, "")` when `report.passed` is True
- `(QualityOutcome.RETRY, report.feedback_text)` when `report.passed` is False

**Raises**: propagates infra errors from `evaluate_task_quality()`.

---

### `judge_task_content_quality(task: dict) -> list[Violation]` *(internal but contract-stable)*

The single consolidated LLM judge call. Returns a flat list of `Violation`s covering `short_overview` shape, `pre_requisites` framing/relevance, and `outcomes` framing/relevance. Implementation lives in `task_quality/semantic.py`.

**Schema**: returns `CONTENT_QUALITY_RESPONSE_SCHEMA` (added to `infra/schemas.py`).
**Model**: `EVAL_MODEL` from `infra/evals.py` (currently `gpt-5-nano-2025-08-07`).
**Client**: `eval_openai_client` from `infra/evals.py`.

Exposed via `task_quality/__init__.py` only for tests that need to mock it directly.

---

## Usage Pattern (in `generators/task/creator.py`)

**Before** (current code, retry-loop tail):
```python
if t_pass and c_pass:
    gate_outcome, gate_feedback = run_gate_for_attempt(
        plan, candidate, candidate_eval, attempt,
    )
    if gate_outcome == GateOutcome.RETRY:
        last_failure = candidate_eval
        feedback = gate_feedback
        continue
    task_data = candidate
    eval_info = candidate_eval
    logger.info(f"Attempt {attempt}: evals passed - proceeding to storage")
    break
```

**After**:
```python
from task_quality import run_quality_for_attempt, QualityOutcome

if t_pass and c_pass:
    gate_outcome, gate_feedback = run_gate_for_attempt(
        plan, candidate, candidate_eval, attempt,
    )
    if gate_outcome == GateOutcome.RETRY:
        last_failure = candidate_eval
        feedback = gate_feedback
        continue

    quality_outcome, quality_feedback = run_quality_for_attempt(candidate, attempt)
    if quality_outcome == QualityOutcome.RETRY:
        last_failure = {**candidate_eval, "quality_feedback": quality_feedback}
        feedback = build_retry_feedback([], candidate_eval, quality_feedback=quality_feedback)
        continue

    task_data = candidate
    eval_info = candidate_eval
    logger.info(f"Attempt {attempt}: evals + gate + quality passed - proceeding to storage")
    break
```

---

## Companion Change: `generators/task/evaluator.py:build_retry_feedback`

**Before**:
```python
def build_retry_feedback(
    hollow_reasons: list[str], eval_info: Optional[Dict]
) -> str:
```

**After**:
```python
def build_retry_feedback(
    hollow_reasons: list[str],
    eval_info: Optional[Dict],
    *,
    quality_feedback: Optional[str] = None,
) -> str:
```

When `quality_feedback` is provided, it is appended as one more `parts` entry before the final "Address every issue above" footer (Decision 8 in research.md).

---

## Quality Check Coverage (run by `evaluate_task_quality`)

| Check | Type | Field |
|-------|------|-------|
| Item does not start with bullet glyph (`•`, `‣`, `▪`, `▶`, `-`, `*`, `–`, `—`, numbered prefixes) | deterministic | `pre_requisites[*]`, `outcomes[*]`, `short_overview[*]` |
| Item does not contain residual `**X**:` marker | deterministic | `pre_requisites[*]`, `outcomes[*]`, `short_overview[*]` |
| Item is non-blank and non-duplicate | deterministic | `pre_requisites[*]`, `outcomes[*]`, `short_overview[*]` |
| Exactly 3 entries | deterministic | `short_overview` |
| Not equal to `name` slug; contains a space | deterministic | `task_blob.title` |
| Title-case heuristic (Decision 4 in research.md) | deterministic | `task_blob.title` |
| Within `[MIN_QUESTION_CHARS, MAX_QUESTION_CHARS]` | deterministic | `question` |
| 3-part shape: artifact / goal / outcome | semantic | `short_overview[0]`, `short_overview[1]`, `short_overview[2]` |
| Task-anchored + candidate-readable sentence | semantic | `pre_requisites[*]` |
| Task-anchored + candidate-readable sentence | semantic | `outcomes[*]` |

---

## Failure Modes

| Failure | Behaviour |
|---------|-----------|
| Deterministic rule fires | `Violation` added to report; runner returns `RETRY` with feedback |
| Semantic LLM call returns issues | `Violation`s added to report; runner returns `RETRY` |
| Semantic LLM call fails (transport, parse) | `Exception` raised; run aborts; no Supabase or GitHub write |
| All checks pass | runner returns `(PASS, "")`; persistence proceeds |
| Retry budget exhausted | the existing `EvalGateError` raises from `creator.py` — quality layer does not raise its own exhaustion error |

---

## Stability Notes

- Adding a new deterministic rule is non-breaking — callers see new `Violation` entries through the same `QualityReport` shape.
- Adding a new semantic check is non-breaking — same return type, new entries in `report.violations`.
- The `Violation` and `QualityReport` shapes are the documented stable contract; downstream consumers can rely on the field names and types listed above.
