# Tasks: Task Content-Quality Evals

**Input**: Design documents from `/specs/003-task-content-quality-evals/`
**Prerequisites**: spec.md ✓, plan.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

**Organization**: Tasks grouped by user story. Each story is independently testable by calling `task_quality.evaluate_task_quality()` directly — no full pipeline run required until Phase 8.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no shared state dependencies)
- **[Story]**: Maps to user story from spec.md (US1–US5)

---

## Phase 1: Setup

**Purpose**: Test infrastructure only. No source changes yet.

- [ ] T001 Create `tests/unit/__init__.py` and `tests/integration/__init__.py` if missing (no-op if spec-002 already added them — verify with `ls tests/unit/__init__.py tests/integration/__init__.py`)
- [ ] T002 Create `task_quality/` directory with empty `__init__.py` and a top-of-file module docstring matching the style of `task_validation/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Models + rule protocol that ALL user-story phases depend on. Must be complete before Phase 3 starts.

**⚠️ CRITICAL**: Phases 3–7 import from `task_quality.models` and `task_quality.rules` — these symbols must exist before story work starts.

- [ ] T003 [P] Add `Violation` frozen dataclass to `task_quality/models.py` per data-model.md (fields: `field_path`, `rule_name`, `actual_value`, `reason`)
- [ ] T004 [P] Add `QualityOutcome` enum to `task_quality/models.py` (values: `PASS`, `RETRY` — mirror `GateOutcome`)
- [ ] T005 [P] Add `QualityReport` dataclass to `task_quality/models.py` per data-model.md (fields: `passed`, `violations`, `feedback_text`, `llm_call_count`)
- [ ] T006 [P] Add `Rule` Protocol to `task_quality/models.py` (attributes: `name`, `applies_to_fields`, `check(task) -> list[Violation]`)
- [ ] T007 Add module-level constants to `task_quality/rules.py`: `MIN_QUESTION_CHARS = 120`, `MAX_QUESTION_CHARS = 1500`, `BULLET_GLYPH_REGEX`, `BOLD_MARKER_REGEX`, `NUMBERED_PREFIX_REGEX`, `TITLE_CONNECTOR_WORDS = frozenset({"a","an","the","of","to","in","on","for","and","or","with","by","at","vs"})` (depends on T003–T006)
- [ ] T008 Add empty `RULES: list[Rule] = []` registry to `task_quality/rules.py` (populated in subsequent phases)
- [ ] T009 Add `_compose_feedback(violations: list[Violation]) -> str` helper to `task_quality/runner.py` per data-model.md composition rules (depends on T003)

**Checkpoint**: `from task_quality.models import Violation, QualityReport, QualityOutcome, Rule` succeeds. `task_quality/rules.py` has constants and an empty registry. No rule logic yet.

---

## Phase 3: User Story 1 — Marker-Laden Bullets Rejected (Priority: P1) 🎯 MVP

**Goal**: Any `pre_requisites`, `outcomes`, or `short_overview` item that starts with a bullet glyph, contains a `**X**:` marker, is blank, or duplicates another item is detected.

**Independent Test**: Build a task dict with `outcomes[0] = "• Build the API"`, `outcomes[1] = "**Goal**: Ship it"`, and `pre_requisites[0] = "  "`. Call `evaluate_task_quality(task)`. Confirm exactly 3 violations, each naming the correct field path and rule.

### Implementation for User Story 1

- [ ] T010 [P] [US1] Implement `R_NoBulletGlyphPrefix` rule in `task_quality/rules.py` covering `pre_requisites`, `outcomes`, `short_overview`; uses `BULLET_GLYPH_REGEX` and `NUMBERED_PREFIX_REGEX`; register in `RULES`
- [ ] T011 [P] [US1] Implement `R_NoResidualBoldMarker` rule in `task_quality/rules.py` using `BOLD_MARKER_REGEX` (`r"\*\*[^*]+\*\*\s*:"`); register in `RULES`
- [ ] T012 [P] [US1] Implement `R_NoBlankOrDuplicateItem` rule in `task_quality/rules.py` (whitespace-only or repeated entries in the same list); register in `RULES`
- [ ] T013 [P] [US1] Add per-rule tests in `tests/unit/test_task_quality_rules.py` — for each of T010/T011/T012: one happy-path case, one sad-path case naming the expected `field_path` and `rule_name`
- [ ] T014 [US1] Add aggregation test in `tests/unit/test_task_quality_rules.py`: a task with violations in multiple rules produces a single concatenated list when `run_deterministic_rules()` is called

**Checkpoint**: `pytest tests/unit/test_task_quality_rules.py -k "US1"` passes. Bullet-marker class of defects is caught deterministically.

---

## Phase 4: User Story 2 — `short_overview` Has Exactly 3 Bullets In The Required Shape (Priority: P1)

**Goal**: `short_overview` count is checked deterministically; the 3-part semantic shape (artifact / goal / outcome) is checked by the consolidated LLM judge.

**Independent Test**: Three task dicts — (a) `short_overview` has 5 entries, (b) 3 entries all describing the goal, (c) 3 entries matching the reference example. Call `evaluate_task_quality(task)`. (a) fails on `R_ShortOverviewExactlyThree`; (b) passes deterministic but fails semantic (`R_ShortOverviewShape`); (c) passes.

### Implementation for User Story 2

- [ ] T015 [US2] Implement `R_ShortOverviewExactlyThree` rule in `task_quality/rules.py`; register in `RULES`
- [ ] T016 [US2] Add `CONTENT_QUALITY_RESPONSE_SCHEMA` to `infra/schemas.py` per data-model.md entity `SemanticJudgeResponse` (sections: `short_overview_shape`, `pre_requisites_framing`, `outcomes_framing`)
- [ ] T017 [US2] Implement `judge_task_content_quality(task: dict) -> list[Violation]` in `task_quality/semantic.py`: build consolidated prompt that includes the 3-part shape definition with the reference example from spec.md, the relevance + framing rules for `pre_requisites` and `outcomes`, and the task context (`title`, `question`, competency names, item lists); call `eval_openai_client.responses.create(model=EVAL_MODEL, ..., text={"format": {"type": "json_schema", ...}})`; parse response into `list[Violation]`
- [ ] T018 [US2] Add unit test for short_overview count in `tests/unit/test_task_quality_rules.py` covering 0, 1, 2, 3, 4, 5 entries
- [ ] T019 [US2] Add integration test in `tests/integration/test_task_quality_integration.py` for the 3-part shape: a fixture task whose `short_overview` is three rephrasings of the goal must produce at least one `R_ShortOverviewShape` violation from the real LLM call
- [ ] T020 [US2] Add unit test for `judge_task_content_quality` with a mocked `eval_openai_client.responses.create` returning a fixed `CONTENT_QUALITY_RESPONSE_SCHEMA` payload; assert it parses into the expected `Violation` list

**Checkpoint**: `pytest tests/unit/ -k "US2"` passes. `short_overview` count is enforced; semantic shape check returns the expected violations against a mock.

---

## Phase 5: User Story 3 — `pre_requisites` and `outcomes` Are Task-Relevant And Readable (Priority: P1)

**Goal**: Every `pre_requisites` and `outcomes` item references a substantive concept from the task and is a candidate-readable sentence.

**Independent Test**: A task with `pre_requisites[3] = "Familiarity with Python's standard library"` (generic) and `outcomes[1] = "It works."` (too short, no anchor) produces semantic violations naming both indexes when the LLM call returns the corresponding response. No deterministic rule fires.

### Implementation for User Story 3

- [ ] T021 [US3] Extend the prompt in `task_quality/semantic.py` to define "task-anchored" (must reference a substantive token from `title` / `question` / competency names / starter-code file paths) and "candidate-readable sentence" (capitalised, terminal punctuation, ≥ 6 words); include one positive example per category
- [ ] T022 [US3] Add unit test in `tests/unit/test_task_quality_runner.py` mocking the LLM response to include `pre_requisites_framing.violations = [{"index": 3, "reason": "generic / not task-anchored"}]`; assert the resulting `QualityReport` contains a violation at `pre_requisites[3]` with `rule_name="R_PrerequisiteFraming"`
- [ ] T023 [US3] Add integration test in `tests/integration/test_task_quality_integration.py` using a fixture whose `pre_requisites` contains one obviously-generic bullet on a task whose stack is specific (e.g., a Kafka-streaming task with a `"Familiarity with Python"` bullet); assert the real LLM call returns at least one `R_PrerequisiteFraming` violation
- [ ] T024 [US3] Add unit test for duplicate-detection in `tests/unit/test_task_quality_rules.py`: `pre_requisites` with two identical entries produces an `R_NoBlankOrDuplicateItem` violation naming the second position (covers FR-006)

**Checkpoint**: `pytest tests/unit/ tests/integration/ -k "US3"` passes. Relevance and framing checks fire on plausible defective fixtures.

---

## Phase 6: User Story 4 — Title Is Human-Readable, Not A Slug (Priority: P1)

**Goal**: Slug-shaped or all-lowercase or all-uppercase titles are rejected; legitimate Title Case passes.

**Independent Test**: Three task dicts — title = `"voice-agent-eval-framework"`, `"design voice agent eval framework"`, `"Design Voice Agent Eval Framework"`. Call `evaluate_task_quality()`. The first two produce violations; the third passes.

### Implementation for User Story 4

- [ ] T025 [P] [US4] Implement `R_TitleNotKebabSlug` rule in `task_quality/rules.py`: rejects if `task_blob.title` equals `name` slug (case-insensitive, trimmed) or contains no space; register in `RULES`
- [ ] T026 [P] [US4] Implement `R_TitleIsTitleCase` rule in `task_quality/rules.py` per research.md Decision 4 (first word capitalised; no length-≥-4 word fully lowercase except connector set; not all uppercase); register in `RULES`
- [ ] T027 [US4] Add unit tests in `tests/unit/test_task_quality_rules.py` for the title rules: kebab slug fails on `R_TitleNotKebabSlug`; lowercase sentence fails on `R_TitleIsTitleCase`; all-caps fails on `R_TitleIsTitleCase`; reference title `"Design Voice Agent Eval Framework"` passes both; title with connector words like `"Build a Notification Service"` passes both

**Checkpoint**: `pytest tests/unit/test_task_quality_rules.py -k "US4"` passes. Title slug class of defects is caught deterministically.

---

## Phase 7: User Story 5 — `question` Is Short Enough To Read At The Start Of The Task (Priority: P2)

**Goal**: Tasks whose `question` is shorter than `MIN_QUESTION_CHARS` or longer than `MAX_QUESTION_CHARS` are rejected with the actual length and the cap named in the violation.

**Independent Test**: Two task dicts — `question` of length ~330 (reference) and ~3500. Call `evaluate_task_quality()`. The first passes; the second produces an `R_QuestionLengthInRange` violation whose `reason` includes both the actual length and the configured `MAX_QUESTION_CHARS` value.

### Implementation for User Story 5

- [ ] T028 [US5] Implement `R_QuestionLengthInRange` rule in `task_quality/rules.py` using `MIN_QUESTION_CHARS` and `MAX_QUESTION_CHARS`; reason includes both the actual length and the configured cap so the operator can tell which side of the bound was hit; register in `RULES`
- [ ] T029 [US5] Add unit tests in `tests/unit/test_task_quality_rules.py` for boundary conditions: length = MIN−1, MIN, MAX, MAX+1 — assert exactly the bounds reject, the boundary values pass

**Checkpoint**: `pytest tests/unit/test_task_quality_rules.py -k "US5"` passes.

---

## Phase 8: Runner, Feedback Composer, And Wire Into `creator.py`

**Purpose**: Connect the completed rule registry + semantic judge into the retry loop. All checks above are tested independently; this phase is wiring.

- [ ] T030 Implement `evaluate_task_quality(task: dict) -> QualityReport` in `task_quality/runner.py`: iterate `RULES`, call `judge_task_content_quality(task)`, aggregate violations, compute `passed`, build `feedback_text` via `_compose_feedback`, set `llm_call_count`; on semantic-judge infra error, raise a plain `Exception` per research.md Decision 7
- [ ] T031 Implement `run_quality_for_attempt(candidate: dict, attempt: int) -> tuple[QualityOutcome, str]` in `task_quality/runner.py` (mirror `run_gate_for_attempt` shape)
- [ ] T032 Populate `task_quality/__init__.py` with the public API per `contracts/content-quality-api.md` (exports: `Violation`, `QualityReport`, `QualityOutcome`, `Rule`, `evaluate_task_quality`, `run_quality_for_attempt`, `RULES`)
- [ ] T033 Extend `generators/task/evaluator.py:build_retry_feedback` to accept optional keyword arg `quality_feedback: str | None = None`; when provided, append to `parts` list before the footer (per research.md Decision 8); add unit test in `tests/unit/test_task_quality_feedback.py` confirming substring presence
- [ ] T034 Modify `generators/task/creator.py:create_task` retry loop: import `run_quality_for_attempt` + `QualityOutcome`; after the gate's PASS branch, call `run_quality_for_attempt(candidate, attempt)`; on `RETRY` set `last_failure`, set `feedback = build_retry_feedback([], candidate_eval, quality_feedback=quality_feedback)`, `continue`; on `PASS` fall through to persistence
- [ ] T035 Add unit test in `tests/unit/test_task_quality_runner.py` asserting: (1) `evaluate_task_quality` aggregates deterministic + semantic violations into one report; (2) `run_quality_for_attempt` returns `(PASS, "")` when violations is empty and `(RETRY, non-empty)` otherwise; (3) `report.llm_call_count == 1` after a successful semantic call (mocked)

**Checkpoint**: `pytest tests/unit/ tests/integration/ -k "task_quality"` passes. The retry loop runs the new layer.

---

## Phase 9: Polish — Pitfalls + Smoke Test

- [ ] T036 [P] Add two entries to `docs/known_pipeline_pitfalls.md`: (1) residual `**X**:` markers in `outcomes`/`pre_requisites`; (2) kebab-case `task_blob.title`. Each entry names the rule(s) that catch the defect.
- [ ] T037 Run the full pipeline against one known-good competency combo (`python multiagent.py generate-tasks -c ... -b ... -s ...`); verify the new "Quality eval passed" log line appears and persistence proceeds without regression
- [ ] T038 Verify SC-007 with an integration assertion: instrument the test in `tests/integration/test_task_quality_integration.py` to count `eval_openai_client.responses.create` calls per `evaluate_task_quality` invocation; assert `count == 1`
- [ ] T039 Run `pytest -q` to confirm SC-008 (no regression in existing test suites)

**Checkpoint**: Real pipeline run completes with the new gate active; no regressions in pre-existing tests.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all story phases
- **Phase 3 (US1)**: Depends on Phase 2 — deterministic rules need `Violation`, `Rule`, registry
- **Phase 4 (US2)**: Depends on Phase 2 + Phase 3 (registry pattern reused); introduces the semantic judge module
- **Phase 5 (US3)**: Depends on Phase 4 — semantic judge already exists; this phase extends its prompt and tests
- **Phase 6 (US4)**: Depends on Phase 2 — independent of Phase 3/4/5 (different fields); can parallelize
- **Phase 7 (US5)**: Depends on Phase 2 — independent; can parallelize
- **Phase 8 (Runner + Wire)**: Depends on Phases 3–7 complete
- **Phase 9 (Polish)**: Depends on Phase 8 complete

### User Story Dependencies

- **US1 (P1)**: After Phase 2. No story dependencies.
- **US2 (P1)**: After Phase 2 + US1 (registry already exists). Introduces the LLM judge.
- **US3 (P1)**: After US2 (extends the same prompt + parser).
- **US4 (P1)**: After Phase 2. Independent of US1/US2/US3 (title-only field). Can parallelize.
- **US5 (P2)**: After Phase 2. Independent. Can parallelize with US4.

### Within Each Phase

- Models before the rules that use them.
- Rules before tests that call them.
- Tasks marked `[P]` within a phase touch different files (or non-overlapping regions of the same file) and have no execution-order dependency on each other.

---

## Parallel Execution Examples

### Phase 2 (Foundational)
```
Parallel: T003 (Violation) + T004 (QualityOutcome) + T005 (QualityReport) + T006 (Rule Protocol)
Sequential after: T007 (constants) → T008 (empty RULES) → T009 (_compose_feedback)
```

### Phase 3 (US1)
```
Parallel: T010 (R_NoBulletGlyphPrefix) + T011 (R_NoResidualBoldMarker) + T012 (R_NoBlankOrDuplicateItem) + T013 (per-rule tests)
Sequential after: T014 (aggregation test)
```

### Phases 6 + 7 in parallel (after Phase 2)
```
Stream A: T025 + T026 → T027              (US4: title rules)
Stream B: T028 → T029                      (US5: question length)
Can run concurrently with US1/US2/US3 phases too
```

### Wire phase (Phase 8)
```
Sequential: T030 (evaluate_task_quality) → T031 (run_quality_for_attempt) → T032 (__init__) → T033 (build_retry_feedback) → T034 (creator.py wire) → T035 (runner tests)
```

---

## Implementation Strategy

### MVP (User Stories 1 + 2 + 4 — the highest-impact P1 stories)

1. Phase 1: Setup (T001–T002)
2. Phase 2: Foundational (T003–T009)
3. Phase 3: US1 deterministic marker rules (T010–T014)
4. Phase 4: US2 short_overview count + semantic judge skeleton (T015–T020)
5. Phase 6: US4 title rules (T025–T027) — can run parallel with Phase 4
6. Phase 8 partial: T030–T034 (wire into creator.py with only the rules implemented so far)
7. **STOP and VALIDATE**: Run the full pipeline once with a known-clean combo; confirm pass; introduce a known-bad title (kebab slug) in a one-off test and confirm rejection with retry

### Full Delivery

Continue with Phase 5 (US3 framing), Phase 7 (US5 question length), Phase 9 (T036–T039 polish + SC verification).

---

## Task Summary

| Phase | Tasks | User Story | Parallelizable |
|-------|-------|------------|----------------|
| 1: Setup | T001–T002 | — | T001, T002 |
| 2: Foundational | T003–T009 | — | T003+T004+T005+T006 |
| 3: US1 Markers | T010–T014 | US1 | T010+T011+T012+T013 |
| 4: US2 short_overview + semantic judge | T015–T020 | US2 | T018+T019+T020 |
| 5: US3 Framing/Relevance | T021–T024 | US3 | T022+T023 |
| 6: US4 Title | T025–T027 | US4 | T025+T026 |
| 7: US5 Question Length | T028–T029 | US5 | — |
| 8: Runner + Wire | T030–T035 | — | T035 |
| 9: Polish | T036–T039 | — | T036 |
| **Total** | **39** | | |

**Suggested MVP scope**: Phases 1–4 + Phase 6 + T030–T034 (24 tasks) — delivers US1, US2 (deterministic count), and US4 end-to-end with a live retry-loop integration.
