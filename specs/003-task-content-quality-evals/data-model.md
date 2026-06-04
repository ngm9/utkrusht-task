# Data Model: Task Content-Quality Evals

**Feature**: 003-task-content-quality-evals
**Date**: 2026-06-04

---

## Entities

### 1. `Violation`

A single rule firing on a single field path. The atomic unit of a quality report.

| Field | Type | Description |
|-------|------|-------------|
| `field_path` | `str` | Dot-path or indexed path to the offending field (e.g., `task_blob.title`, `outcomes[2]`, `short_overview[0]`) |
| `rule_name` | `str` | Stable identifier of the rule that fired (e.g., `R_NoBulletGlyphPrefix`, `R_TitleNotKebabSlug`) — used in feedback strings and tests |
| `actual_value` | `Any` | The actual value that failed (truncated to 200 chars for strings, summarised for lists) |
| `reason` | `str` | Human-readable description of why the rule fired (e.g., `"must not start with a bullet glyph (•/-/*/numbered)"`) |

**Validation rules** (internal):
- `field_path` must not be empty
- `rule_name` must match an entry in `task_quality.rules.RULES`
- `reason` must not be empty

---

### 2. `QualityReport`

The full outcome of one evaluation pass against a candidate task. Returned by `evaluate_task_quality()`.

| Field | Type | Description |
|-------|------|-------------|
| `passed` | `bool` | True iff `violations` is empty |
| `violations` | `list[Violation]` | All violations across deterministic + semantic checks; ordered deterministic-first |
| `feedback_text` | `str` | Composed corrective message for the LLM retry loop; empty when `passed == True` |
| `llm_call_count` | `int` | 0 if no semantic call was made (i.e., infra error before call), 1 on a successful call. Used to assert SC-007 in tests |

**Composition rules**:
- `feedback_text` is built by `_compose_feedback(violations)`:
  - Header: `"PREVIOUS ATTEMPT FAILED content-quality checks."`
  - One bullet per violation: `f"- [{rule_name}] {field_path}: {reason}. Got: {actual_value_truncated}"`
  - Footer: `"Correct every issue above. Return ONLY the corrected JSON object using the same canonical key names."`
- Order: deterministic-rule violations first (easier to fix), semantic violations second.

---

### 3. `QualityOutcome` (Enum)

Mirrors `GateOutcome` in `generators/task/gate.py`. Two values, no others.

| Value | Meaning |
|-------|---------|
| `PASS` | The task cleared all content-quality checks; proceed to persistence |
| `RETRY` | At least one rule fired; feedback string handed to the retry loop |

---

### 4. `Rule`

Each deterministic rule is a callable function registered in `RULES`. Defined as a `Protocol` so adding a rule does not require subclassing.

```python
class Rule(Protocol):
    name: str
    applies_to_fields: tuple[str, ...]
    def check(self, task: dict) -> list[Violation]: ...
```

**Required attributes**:
| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Stable identifier, lives in error messages and tests |
| `applies_to_fields` | `tuple[str, ...]` | Field paths the rule inspects; used by the runner to compose human-readable docs and by tests to assert coverage |
| `check(task)` | `(dict) -> list[Violation]` | Pure function: same input → same output, no side effects |

**Registry**:
```python
RULES: list[Rule] = [
    R_NoBulletGlyphPrefix,
    R_NoResidualBoldMarker,
    R_NoBlankOrDuplicateItem,
    R_ShortOverviewExactlyThree,
    R_TitleNotKebabSlug,
    R_TitleIsTitleCase,
    R_QuestionLengthInRange,
]
```

Adding a new rule requires editing **only** `task_quality/rules.py` (FR-018 / SC-006).

---

### 5. `SemanticJudgeResponse`

Internal type for parsing the structured LLM response. Mirrors the JSON schema `CONTENT_QUALITY_RESPONSE_SCHEMA` added to `infra/schemas.py`.

```python
class _ShortOverviewIssue(TypedDict):
    position: Literal[0, 1, 2]
    expected: Literal["describes task artifact", "describes candidate goal", "describes expected outcome"]
    actual_summary: str

class _FramingViolation(TypedDict):
    index: int
    reason: Literal["generic / not task-anchored", "not a candidate-readable sentence", "duplicates earlier item"]

class SemanticJudgeResponse(TypedDict):
    short_overview_shape: dict     # {"matches_three_part_shape": bool, "issues": list[_ShortOverviewIssue]}
    pre_requisites_framing: dict   # {"violations": list[_FramingViolation]}
    outcomes_framing: dict         # {"violations": list[_FramingViolation]}
```

The parser converts each issue into a `Violation` with the matching `field_path` and `rule_name`:
- `short_overview_shape.issues[i]` → `Violation(field_path=f"short_overview[{position}]", rule_name="R_ShortOverviewShape", ...)`
- `pre_requisites_framing.violations[i]` → `Violation(field_path=f"pre_requisites[{index}]", rule_name="R_PrerequisiteFraming", ...)`
- `outcomes_framing.violations[i]` → `Violation(field_path=f"outcomes[{index}]", rule_name="R_OutcomeFraming", ...)`

---

### 6. `TaskQualityInfraError` (Exception, optional)

Raised when the semantic LLM call fails for non-content reasons (transport error, JSON parse failure on a 200 response). Distinct from `EvalGateError`.

| Field | Type | Description |
|-------|------|-------------|
| `underlying` | `Exception` | The wrapped exception (network, parse, etc.) |
| `attempt` | `int` | The retry-loop attempt that failed |

This may simply be a plain `Exception` with a clear message — the dedicated class is an optional refinement and not strictly required for the v1 contract.

---

## State Transitions

```
candidate task (dict, post-gate)
        │
        ▼
  [Phase 1: deterministic rules]
  for each Rule in RULES:
      violations.extend(rule.check(task))
        │
        ▼
  [Phase 2: semantic LLM judge]
  one call to eval_openai_client
        │
        ├──── infra error ──▶ raise Exception (run aborts, no writes)
        │
        ▼
  [Phase 3: aggregate]
  QualityReport(
      passed = (len(violations) == 0),
      violations = [...],
      feedback_text = compose_feedback(violations) if not passed else "",
      llm_call_count = 1,
  )
        │
        ▼
  outcome = PASS if passed else RETRY
  return (outcome, feedback_text)
```

---

## Relationships to Existing Code

| Existing symbol | Change |
|-----------------|--------|
| `generators/task/creator.py:create_task` retry loop | **Extended** — adds one `run_quality_for_attempt()` call between the gate's `PASS` and persistence |
| `generators/task/evaluator.py:build_retry_feedback` | **Extended** — adds optional `quality_report: QualityReport | None` parameter (Decision 8 in research.md) |
| `infra/schemas.py` | **Extended** — adds `CONTENT_QUALITY_RESPONSE_SCHEMA` |
| `infra/evals.py:eval_openai_client`, `EVAL_MODEL` | **Reused unchanged** — no new client, no new env var |
| `task_validation/` package | **Unchanged** — existing shape + FK checks remain in place (FR-020) |
| `infra/utils.py:format_outcomes`, `format_pre_requisites` | **Unchanged** — they still split LLM output into lists; the new layer judges the result of that split |

---

## Field Coverage Matrix

| Field | Deterministic rules | Semantic rules |
|-------|--------------------|--------------------|
| `task_blob.title` | `R_TitleNotKebabSlug`, `R_TitleIsTitleCase` | — |
| `question` | `R_QuestionLengthInRange` | — |
| `pre_requisites[*]` | `R_NoBulletGlyphPrefix`, `R_NoResidualBoldMarker`, `R_NoBlankOrDuplicateItem` | `R_PrerequisiteFraming` (relevance + sentence shape) |
| `outcomes[*]` | `R_NoBulletGlyphPrefix`, `R_NoResidualBoldMarker`, `R_NoBlankOrDuplicateItem` | `R_OutcomeFraming` (relevance + sentence shape) |
| `short_overview` | `R_ShortOverviewExactlyThree` | `R_ShortOverviewShape` (3-part: artifact / goal / outcome) |
| `short_overview[*]` | `R_NoBulletGlyphPrefix`, `R_NoResidualBoldMarker`, `R_NoBlankOrDuplicateItem` | — |
| `hints` | — (v1 out of scope) | — |
| `definitions` | — (v1 out of scope) | — |
