# Feature Specification: Task Content-Quality Evals

**Feature Branch**: `003-task-content-quality-evals`
**Created**: 2026-06-04
**Status**: Draft
**Input**: User description: "Once a task is generated we need evals that check the *content* of the task — prerequisites should be a real bullet array with no leaked markdown markers, outcomes should be candidate-readable bullets, short_overview should be exactly 3 recruiter-readable bullets that describe the task, the goal, and the expected outcome, title should be human-readable not a slug, and question should be short. Read the task blob properly and reject anything off so it regenerates."

---

## Background

Two task-validation layers already exist:

1. **LLM critics** (`infra/evals.py` → `generators/task/evaluator.py`) judge semantic quality (realism, difficulty fit) and run inside the retry loop in `generators/task/creator.py` alongside the E2B build/test gate.
2. **Pydantic DAO validator** (`task_validation/`) checks **shape + FK** at insert time: `pre_requisites` is `List[str]`, `outcomes` is `List[str]`, items are non-empty, competency IDs exist in Supabase.

Neither layer checks the **content quality of parsed list and string fields**. Generated tasks have shipped with:

- `outcomes` items like `"**Challenge**: Build a scalable API…"` — residual bold/heading markers leaking through `format_outcomes()`.
- `pre_requisites` items prefixed with `"• "` (Unicode bullet glyph) — the splitter only strips ASCII `-` and `*`.
- `short_overview` of arbitrary length, with no enforced structure.
- `title` set to the kebab-case slug (`"offline-first-field-app-design"`) instead of the human-readable form a candidate sees (`"Design Voice Agent Eval Framework"`).
- `question` running to many paragraphs of background prose where the candidate-facing ask should be 2–3 short paragraphs at most.

These slip past both existing layers because the shape is technically valid and the LLM critic does not score on bullet hygiene. They cause two visible operator costs: the task looks unprofessional to candidates and recruiters, and the operator has to manually fix the JSON before the task is usable.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Marker-Laden Bullets Rejected Before Persistence (Priority: P1)

A pipeline run produces a task whose `outcomes` or `pre_requisites` entries contain leftover markdown markers (`**Challenge**:`, `**Goal**:`, `**Task**:`) embedded in the item text, or whose items start with a Unicode/ASCII bullet glyph (`•`, `-`, `*`). Today these slip through because the existing splitter only trims leading ASCII bullets and the DAO only checks non-emptiness. After this feature, every such item is detected before the GitHub repo + Gist + Supabase insert run, the attempt is rejected, and the retry loop hands the LLM concrete feedback so the next attempt produces clean bullets.

**Why this priority**: This is the single most common content defect seen on shipped tasks, it is visible to candidates the moment they open the task, and it is cheap to detect. Catching it before persistence prevents the recurring manual-fix toil.

**Independent Test**: Construct a task dict where one `outcomes` item starts with `"• "`, another contains `"**Goal**: …"`, and one `pre_requisites` item starts with `"- "`. Run the content-quality eval against the task. Confirm it returns a failure naming each offending field path and the specific violation, and that the retry-loop feedback string mentions every violation.

**Acceptance Scenarios**:

1. **Given** a task where `outcomes[2]` is `"• Every submission processed exactly once"`, **When** the content-quality eval runs, **Then** it returns a failure naming `outcomes[2]` with the reason "must not start with a bullet glyph (•/-/*)" — no GitHub or Supabase write is attempted.
2. **Given** a task where `pre_requisites[0]` is `"**Setup**: Docker installed locally"`, **When** the content-quality eval runs, **Then** it returns a failure naming `pre_requisites[0]` with the reason "must not contain a residual bold/heading marker like `**X**:`".
3. **Given** a task where all bullets are clean ASCII sentences, **When** the content-quality eval runs, **Then** it passes and the pipeline proceeds to persistence.
4. **Given** multiple bullets across multiple fields fail simultaneously, **When** the content-quality eval runs, **Then** the failure lists **every** offending field path and reason in one report — not just the first.

---

### User Story 2 — short_overview Has Exactly 3 Bullets In The Recruiter-Readable Shape (Priority: P1)

`short_overview` is read by recruiters, not candidates, and is currently arbitrary-length and arbitrary-content. After this feature, `short_overview` must be exactly three bullets in a fixed semantic shape:

1. **What the task is** — a one-line statement of the artifact being built.
2. **What the candidate has to do** — the goal of the task in the candidate's terms.
3. **What the expected outcome is** — the observable end-state when the task is solved.

Tasks that miss the count or the shape are rejected and regenerated.

**Why this priority**: Recruiters use `short_overview` to decide which task to assign without reading the full question. A wrong count or a vague shape (e.g., three rephrasings of the goal) makes the recruiter-side UX unusable and is the most operator-visible symptom of a sloppy generation.

**Independent Test**: Construct three task dicts — (a) `short_overview` has 5 bullets, (b) `short_overview` has 3 bullets all describing the goal, (c) `short_overview` has 3 bullets matching the required shape. Run the eval. Confirm (a) and (b) fail with distinct, specific reasons; (c) passes.

**Acceptance Scenarios**:

1. **Given** a task where `short_overview` contains 5 entries, **When** the eval runs, **Then** it fails with `short_overview` reason "must contain exactly 3 bullets".
2. **Given** a task where `short_overview` has 3 entries but none of them describes the task artifact (point 1) — e.g., all three describe the goal — **When** the eval runs, **Then** it fails with `short_overview` reason "first bullet must describe the task artifact; second the goal; third the expected outcome".
3. **Given** a task whose `short_overview` matches the reference example (`["Build a production-grade event-driven pipeline …", "The platform processes thousands of daily submissions but the current pipeline can silently drop …", "Every submission is processed exactly once, scored results are published downstream, failed messages route …"]`), **When** the eval runs, **Then** it passes.
4. **Given** any `short_overview` bullet contains a residual marker (`•`, `**Goal**:`) or a leading bullet glyph, **When** the eval runs, **Then** the same field-level rules from User Story 1 apply.

---

### User Story 3 — pre_requisites and outcomes Are Candidate-Readable, Task-Relevant Bullets (Priority: P1)

`pre_requisites` and `outcomes` are read by the candidate at the start of the task. Today they sometimes ship as generic boilerplate ("Familiarity with Python", "Understanding of REST APIs") that says nothing about the specific task. After this feature, every bullet in both fields must reference at least one substantive concept from the task itself (the task title, the question, a competency name, or a notable file/library named in the starter code), and every bullet must be a complete candidate-readable sentence (capitalised, terminal punctuation, ≥ a minimum word count). Items that fail are rejected; the LLM regenerates with corrective feedback naming which bullets were generic.

There is **no upper bound** on the number of `pre_requisites` or `outcomes` bullets — long lists are acceptable if every bullet is task-specific.

**Why this priority**: A task whose prerequisites are "Knows Python" gives the candidate no signal about the actual task. Boilerplate bullets are a recurring failure mode and are the symptom most often cited when a generated task is rejected for manual fixing.

**Independent Test**: Construct a task whose `outcomes` contains one task-specific bullet and one generic bullet ("Understanding of testing"). Run the eval. Confirm it identifies the generic bullet by index and reason, and that a fully task-specific version passes.

**Acceptance Scenarios**:

1. **Given** a task on event-driven Kafka processing whose `pre_requisites[3]` is `"Familiarity with Python's standard library"`, **When** the eval runs, **Then** it fails with `pre_requisites[3]` reason "must reference a task-specific concept (no anchor in title/question/competencies/code)".
2. **Given** a task whose `outcomes[1]` is `"It works."` (3 words, no task anchor), **When** the eval runs, **Then** it fails with `outcomes[1]` reason "must be a candidate-readable sentence (too short / no task anchor)".
3. **Given** a task whose `pre_requisites` list has 8 bullets and every bullet references the task's specific stack and concepts, **When** the eval runs, **Then** it passes — count is not capped.
4. **Given** a `pre_requisites` or `outcomes` item that is a duplicate of another item in the same list, **When** the eval runs, **Then** it fails naming the duplicate position.

---

### User Story 4 — title Is Human-Readable, Not A Slug (Priority: P1)

`task_blob.title` is the title displayed to candidates and recruiters. Today the generator sometimes copies the kebab-case `name` slug into the `title` field, producing values like `"offline-first-field-app-design"` instead of `"Design Offline-First Field App"`. After this feature, a slug-shaped title is detected and rejected.

**Why this priority**: A slug title is the most visible defect on the candidate-facing surface. It is also trivially detectable, so there is no reason to ship it.

**Independent Test**: Construct two tasks — one with `title = "offline-first-field-app-design"` and one with `title = "Design Offline-First Field App"`. Run the eval. Confirm the first fails with a clear reason and the second passes.

**Acceptance Scenarios**:

1. **Given** a task where `task_blob.title` is `"voice-agent-eval-framework"`, **When** the eval runs, **Then** it fails with `task_blob.title` reason "must be human-readable Title Case, not a kebab-case slug".
2. **Given** a task where `task_blob.title` is `"Design Voice Agent Eval Framework"`, **When** the eval runs, **Then** it passes.
3. **Given** a task where `task_blob.title` is `"design voice agent eval framework"` (lower case, spaces), **When** the eval runs, **Then** it fails with reason "must use Title Case capitalisation".
4. **Given** a task whose `name` (the slug) and `task_blob.title` are equal as strings, **When** the eval runs, **Then** it fails with reason "title must not be identical to the kebab-case `name` slug".

---

### User Story 5 — question Is Short Enough To Read At The Start Of The Task (Priority: P2)

`question` is read by the candidate as the first thing they see. Today the LLM sometimes produces multi-page question bodies that mix background, constraints, and deliverables in one block. After this feature, an unreasonably long `question` is rejected, with the LLM instructed to move setup/context into the README and keep `question` short and direct.

**Why this priority**: A long `question` is a real problem (candidates time out reading) but is less common than the bullet-hygiene defects and harder to define precisely. P2 reflects "worth catching, but the threshold needs tuning in production".

**Independent Test**: Construct a task whose `question` is one short paragraph (under the cap), and one whose `question` is six paragraphs. Run the eval. Confirm the short one passes and the long one fails with the actual length and the cap named in the error.

**Acceptance Scenarios**:

1. **Given** a task whose `question` is roughly the length of the cycle-detection reference example (1–2 short paragraphs, ≤ a defined character budget), **When** the eval runs, **Then** it passes.
2. **Given** a task whose `question` is several paragraphs of background prose that exceed the defined character cap, **When** the eval runs, **Then** it fails with `question` reason "exceeds maximum candidate-readable length (X chars / Y chars allowed); move setup detail into the README".
3. **Given** a task whose `question` is the empty string or fewer than a defined minimum length, **When** the eval runs, **Then** it fails with reason "too short to specify a candidate-facing task".

---

### Edge Cases

- **Bullet glyph appears mid-sentence rather than as a prefix** (e.g., a sentence about a "• character" itself): the rule targets the prefix only — mid-sentence glyphs are allowed.
- **A perfectly clean bullet that happens to be very long**: bullets have no upper length cap; only blanks, dupes, and lack of task anchor fail.
- **The competency name contains a substring of the task title** (so anchor-match is trivial): anchor matching considers a substantive token from any of `name`, `title`, `question`, competency names, or starter code file paths; matching on stop-words alone does not satisfy the anchor.
- **`short_overview` items legitimately need to span the same idea** (e.g., the task IS its own goal): rejected — operator must rephrase to fit the 3-part shape.
- **The retry budget is exhausted before content-quality evals pass**: the same `EvalGateError` semantics apply as for the existing eval gate — no GitHub repo, no Gist, no Supabase row.
- **PR-review and non-tech flows**: out of scope for v1. They use string-shaped `outcomes` / `short_overview` and have different DAO models; addressing them requires separate rule sets and is deferred.
- **`hints` field**: out of scope for v1 — it is a single paragraph and does not exhibit the bullet-hygiene defects.
- **`definitions` field**: out of scope for v1 — it is a key→value mapping not subject to bullet-hygiene rules.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST evaluate every generated task for content-quality violations after the LLM critic and E2B gate pass, but **before** any GitHub repository, Gist, or Supabase row is created.
- **FR-002**: The system MUST integrate with the existing retry loop in `generators/task/creator.py` such that content-quality failures cause the same retry behaviour as LLM critic failures: the loop regenerates with structured corrective feedback until the retry budget is exhausted.
- **FR-003**: The system MUST raise `EvalGateError` when the retry budget is exhausted with unresolved content-quality violations, mirroring the existing gate semantics (no external artifacts created).
- **FR-004**: For `pre_requisites`, `outcomes`, and `short_overview`, every item MUST be rejected if it begins with a bullet glyph (`•`, `-`, `*`, or whitespace thereof).
- **FR-005**: For `pre_requisites`, `outcomes`, and `short_overview`, every item MUST be rejected if it contains a residual bold/heading marker matching the shape `**...**:` anywhere in the item.
- **FR-006**: For `pre_requisites`, `outcomes`, and `short_overview`, every item MUST be rejected if it is blank, whitespace-only, or duplicates another item in the same list.
- **FR-007**: `short_overview` MUST contain exactly 3 items.
- **FR-008**: The three `short_overview` items MUST satisfy the semantic shape: item 1 describes the task artifact, item 2 describes the candidate's goal, item 3 describes the expected outcome. Tasks whose `short_overview` items do not collectively cover this shape MUST be rejected.
- **FR-009**: `pre_requisites` and `outcomes` MUST NOT enforce any upper bound on item count. Empty lists remain rejected by the existing DAO layer; this feature does not relax that.
- **FR-010**: Every `pre_requisites` and `outcomes` item MUST be rejected if it does not reference a substantive token from at least one of: `task_blob.title`, `question`, `criterias[*].name`, or a notable file path in the starter code. Stop-word matches do not count.
- **FR-011**: Every `pre_requisites` and `outcomes` item MUST be rejected if it is not a candidate-readable sentence (defined as: starts with a capital letter, ends with a terminal punctuation mark, and contains at least a minimum number of words).
- **FR-012**: `task_blob.title` MUST be rejected if it is in kebab-case slug form (all lowercase, joined by hyphens, no spaces), or if it equals the kebab-case `name` slug.
- **FR-013**: `task_blob.title` MUST be rejected if it does not use Title Case capitalisation (at minimum: the first word is capitalised, and no full word is unintentionally in screaming-snake or all-lowercase form).
- **FR-014**: `question` MUST be rejected if it exceeds a defined character cap suitable for candidate-readable framing, or if it falls below a defined minimum length sufficient to specify a task.
- **FR-015**: A single content-quality evaluation pass MUST report **every** violation found across all fields in one structured report — never just the first failure.
- **FR-016**: The corrective feedback handed back to the LLM on retry MUST name each failing field path, the violated rule, and the actual offending value (truncated when long). It MUST NOT be a generic "fix your output" message.
- **FR-017**: The content-quality eval MUST be callable as a standalone pure function against a parsed task dict — testable without invoking the full pipeline, LLM, GitHub, or Supabase.
- **FR-018**: Rule definitions MUST live in a single module (a rule registry) so that adding or modifying a rule requires editing exactly one file, never the orchestration code.
- **FR-019**: This feature MUST apply to the coding-pipeline flow (`generators/task/creator.py` → `BaseTaskDAO` / `TaskBlob`). PR-review (`flows/pr_review/`) and non-tech (`flows/non_tech/`) flows are explicitly out of scope for v1.
- **FR-020**: Existing Pydantic shape checks in `task_validation/` MUST remain in place unchanged — content-quality evals are an additional layer, not a replacement.

### Key Entities

- **Content-Quality Rule**: a single named check (e.g., "no leading bullet glyph", "exactly 3 short_overview bullets", "title is not a slug"). Each rule names the fields it applies to, the deterministic or semantic check it performs, and the error message template handed back when it fires.
- **Content-Quality Violation**: a single rule firing on a single field path. Contains the field path (e.g., `outcomes[2]`), the rule name, the offending value (truncated), and the human-readable reason.
- **Content-Quality Report**: the full outcome of one evaluation pass — pass/fail, the list of violations (possibly empty), and the corrective-feedback string composed for the LLM retry loop.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero generated tasks reach Supabase with a `pre_requisites`, `outcomes`, or `short_overview` item starting with a `•`/`-`/`*` bullet glyph — verified by a recurring scan of the `tasks` table on dev that finds no offending rows.
- **SC-002**: Zero generated tasks reach Supabase with a residual `**…**:` bold-marker pattern in any `pre_requisites`, `outcomes`, or `short_overview` item — verified by the same recurring scan.
- **SC-003**: 100% of generated tasks reaching Supabase have exactly 3 `short_overview` bullets — verified by a simple count query against `tasks.task_blob->'short_overview'`.
- **SC-004**: 100% of generated tasks reaching Supabase have a `task_blob.title` that contains at least one space and is not equal to the `name` slug — verified by a simple query.
- **SC-005**: A pipeline operator can read the eval failure output and identify every offending field without opening the task JSON — verified by a usability check on the printed report (every violation names field path, rule, offending value, reason).
- **SC-006**: Adding a new content-quality rule (e.g., "no Markdown link syntax in outcomes") requires editing exactly one file — verified by performing the change after implementation and confirming no other file is touched.
- **SC-007**: Content-quality evaluation adds no more than 1 LLM call per generation attempt (used for the `short_overview` shape and the `pre_requisites`/`outcomes` framing checks — the rest are deterministic) — verified by an integration test that asserts the LLM call count per attempt.
- **SC-008**: Existing test suites (`tests/unit/`, `tests/integration/`, `tests/test_*`) continue to pass — verified by `pytest -q` exit zero.
- **SC-009**: Re-running a previously failing generation after fixing the underlying prompt produces a passing task on the next attempt, with no orphaned GitHub repos or Supabase rows from the failed attempts — verified by an integration test.
