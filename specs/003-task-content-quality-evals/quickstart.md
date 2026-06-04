# Quickstart: Task Content-Quality Evals

**For**: developers implementing or testing this feature

---

## What changes

One new package and one wire-in:

| Change | Details |
|--------|---------|
| **Add** `task_quality/` package | `models.py`, `rules.py`, `semantic.py`, `runner.py`, `__init__.py` |
| **Modify** `infra/schemas.py` | Add `CONTENT_QUALITY_RESPONSE_SCHEMA` |
| **Modify** `generators/task/creator.py` | Call `run_quality_for_attempt()` between the gate's PASS and persistence |
| **Modify** `generators/task/evaluator.py` | Extend `build_retry_feedback()` to accept a `quality_report` |
| **Add** `tests/unit/test_task_quality_rules.py` | One test per deterministic rule |
| **Add** `tests/unit/test_task_quality_runner.py` | Runner + report aggregation with mocked semantic call |
| **Add** `tests/unit/test_task_quality_feedback.py` | Feedback-string composition checks |
| **Add** `tests/integration/test_task_quality_integration.py` | One real LLM call on a fixture task |
| **Modify** `docs/known_pipeline_pitfalls.md` | Document bullet-marker + kebab-title pitfalls |

---

## Running the tests

```bash
# Unit tests (no LLM call, no Supabase)
pytest tests/unit/test_task_quality_rules.py
pytest tests/unit/test_task_quality_runner.py
pytest tests/unit/test_task_quality_feedback.py

# Integration test (requires PORTKEY_API_KEY + OPENAI_API_KEY in .env)
pytest tests/integration/test_task_quality_integration.py

# Whole new layer
pytest tests/unit/test_task_quality_* tests/integration/test_task_quality_*

# Full suite (regression check)
pytest -q
```

---

## Triggering quality eval manually (debugging)

```python
from task_quality import evaluate_task_quality, QualityOutcome

# Build a task dict shaped like the candidate object inside the retry loop:
candidate = {
    "name": "voice-agent-eval-framework",
    "task_blob": {
        "title": "Design Voice Agent Eval Framework",
        "definitions": {"...": "..."},
        "hints": "...",
        "resources": {"github_repo": "https://github.com/..."},
        "outcomes": [
            "Score every voice-agent response on a structured rubric covering accuracy, fluency, and safety.",
            "Persist scored interactions to the postgres results table with the rubric breakdown intact.",
        ],
        "question": "Build an evaluation harness that scores recorded voice-agent interactions ...",
        "short_overview": [
            "Build an evaluation harness for a production voice agent.",
            "The harness must score every recorded interaction against a structured safety + accuracy rubric.",
            "Every scored interaction is persisted with rubric breakdown and can be queried by the QA team.",
        ],
    },
    "pre_requisites": [
        "Familiarity with structured output APIs and JSON schemas in OpenAI / Anthropic SDKs.",
        "Experience with postgres bulk inserts and transactional batch semantics.",
    ],
    "outcomes": [
        # mirrors task_blob.outcomes pre-validation
    ],
    "question": "...",
    "criterias": [{"name": "Voice Agent Evaluation", "proficiency": "INTERMEDIATE", "competency_id": "..."}],
}

report = evaluate_task_quality(candidate)

if report.passed:
    print(f"PASS — {report.llm_call_count} LLM call(s)")
else:
    print(f"FAIL — {len(report.violations)} violation(s)")
    for v in report.violations:
        print(f"  [{v.rule_name}] {v.field_path}: {v.reason}")
    print("\nFEEDBACK FOR LLM RETRY:\n")
    print(report.feedback_text)
```

---

## Adding a new content-quality rule

The rule registry lives in **one file**: `task_quality/rules.py`. Adding a new deterministic rule is a 3-step change in that file:

1. Define a new function or dataclass implementing the `Rule` protocol from `task_quality/models.py`:
   ```python
   @dataclass(frozen=True)
   class _NoMarkdownLink:
       name: str = "R_NoMarkdownLinkSyntax"
       applies_to_fields: tuple[str, ...] = ("outcomes", "pre_requisites")

       def check(self, task: dict) -> list[Violation]:
           # ...
   ```
2. Add an instance to the `RULES` registry list at the bottom of the file.
3. Add a corresponding test in `tests/unit/test_task_quality_rules.py`.

No other file needs to change (FR-018 / SC-006).

---

## Adding a new semantic rule

Semantic rules are folded into the consolidated LLM call to preserve SC-007 (≤ 1 LLM call/attempt). To add one:

1. Extend `CONTENT_QUALITY_RESPONSE_SCHEMA` in `infra/schemas.py` with a new key for the new verdict.
2. Update the prompt in `task_quality/semantic.py` to describe the new check, with an example pair.
3. Extend the response parser in `semantic.py` to translate the new key into `Violation` instances.
4. Add a test case to `tests/integration/test_task_quality_integration.py` using a fixture that exhibits the new defect.

No new LLM call is added; the existing one returns the new verdict alongside the others.

---

## Tuning thresholds

The two numeric thresholds live as module-level constants in `task_quality/rules.py`:

```python
MIN_QUESTION_CHARS = 120
MAX_QUESTION_CHARS = 1500
```

Adjusting either is a one-line edit. The choice is justified in `research.md` (Decision 5). Tightening them retroactively may cause existing tasks to be regenerated on next pipeline run — re-validate the threshold against shipped tasks before changing.

---

## Environment behaviour

The semantic judge uses `eval_openai_client` and `EVAL_MODEL` from `infra/evals.py` — same Portkey → OpenAI route, same model (`gpt-5-nano-2025-08-07`), same credentials (`PORTKEY_API_KEY` + `OPENAI_API_KEY`). No new env var.

The quality layer does NOT use any Supabase environment; it is a pure pre-persistence pass with no DB access.

---

## Running a full pipeline integration check

After Phase D wires the layer into `creator.py`, verify end-to-end with a known-good combo:

```bash
python multiagent.py generate-tasks \
  -c data/generated/input_files/.../competency_*.json \
  -b data/generated/input_files/.../background_*.json \
  -s data/generated/scenarios/task_scenarios_*.json
```

Expect on success:
- Log line: `"Quality eval passed: 0 violations across N rules"`
- One additional LLM call per attempt visible in Portkey dashboard
- No regression in the existing retry-budget exhaustion behaviour (`EvalGateError` still raises after `MAX_EVAL_RETRIES + 1` attempts when violations cannot be cleared)
