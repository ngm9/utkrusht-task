# Tasks: Customer Doc → Per-Task Markdown Extractor

**Input**: Design documents from `/specs/001-doc-to-task-extractor/`
**Prerequisites**: `plan.md`, `spec.md`, `flow.md`, `research.md`, `current-state.md`

**Tests**: Test scaffolding is **deferred** per `research.md` Decision 12. Tasks below intentionally do not include test files.

**Organisation**: Tasks are grouped by user story (US1–US5 from `spec.md`).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1–US5)
- Every task description includes the exact file path

## Path Conventions

Single-project layout. Paths relative to `D:\Utkrushta_task\`. New sub-package `task_input_parser/` is a sibling of `non_tech_flow/`, `pr_review_flow/`, `scenario_generator/`, `generate_input_files/`.

---

## Phase 1: Setup

- [ ] T001 Create the new sub-package directory `task_input_parser/` with empty `task_input_parser/__init__.py`
- [ ] T002 Create `task_input_parser/__main__.py` that imports and invokes `task_input_parser.cli.main()` so `python -m task_input_parser` works
- [ ] T003 [P] Verify all required dependencies are in `requirements.txt` (`python-docx`, `portkey-ai`, `google-api-python-client`, `click`, `pydantic`, `markdown-it-py`, `requests`); add any missing. **Do NOT add `undetected-chromedriver`** — per Decision 5 the parser does not bypass bot protection.
- [ ] T004 [P] Add `tmp/parser_cache/` and `tmp/extract_*/` to `.gitignore` if not already covered

---

## Phase 2: Foundational (Blocking Prerequisites)

Build the core scaffolding every user story depends on: CLI, AST parser, cost accumulator, leak-check, agent loop skeleton, tool registry, and the single always-required tool `emit_task`.

- [ ] T005 Create `task_input_parser/cli.py` with a Click `@click.command()` accepting `brief_path` (positional), `--output-root` (default `tmp/`), and `--cost-cap-usd` (default 2.00)
- [ ] T006 Create `task_input_parser/cost.py` with `CostAccumulator` dataclass (fields: `cap_usd`, `total_input_tokens`, `total_output_tokens`, `total_usd`, `by_model`), methods `add(usage, model)`, `check_or_abort()`, `total()`, and a `CostCapExceeded` exception
- [ ] T007 [P] Create `task_input_parser/leak_check.py` exporting `LEAK_DOMAINS: list[str]` (initial: `codepen\.io`, `codesandbox\.io`, `jsfiddle\.net`, `gist\.github\.com`, `pastebin\.com`, `replit\.com`, `gitlab\.com/snippets`) and `check_leak(text: str) -> list[str]`
- [ ] T008 Create `task_input_parser/ast.py` with Pydantic models `Section`, `Table`, `EmbeddedImage`, `ExternalLink`, `CodeFence`, `BriefAST`, plus public `parse(path: Path) -> BriefAST` dispatcher branching on file extension
- [ ] T009 Implement `parse_docx(path)` in `task_input_parser/ast.py` using `python-docx` for paragraphs + tables and `zipfile` for `word/media/*` images; populate `BriefAST` with sections, tables, embedded images, hyperlinks
- [ ] T010 [P] Implement `parse_markdown(path)` in `task_input_parser/ast.py` using `markdown-it-py`; detect sections via headings, tables via GFM, code fences, external URLs
- [ ] T011 [P] Implement `parse_text(path)` in `task_input_parser/ast.py` as plain read with heuristic section splits (all-caps, numbered prefixes, trailing colons)
- [ ] T012 Create `task_input_parser/tools/__init__.py` exposing `all_tools()` (JSON-schema list for Portkey function-calling) and `dispatch(name, args_json, output_dir)`
- [ ] T013 Implement `task_input_parser/tools/emit.py` with Pydantic models `EmitTaskInput` (fields `slug`, `markdown_content`) and `EmitTaskOutput` (fields `written_to`, `file_size_bytes`, `inline_note_count`); `emit_task()` calls `task_input_parser.leak_check.check_leak()` BEFORE writing — on any match, raises `LeakDetectedError` listing the matched domains; counts occurrences of the literal substring `**Note:**` in the markdown for the run summary
- [ ] T014 Create `task_input_parser/agent.py` with the agent-loop skeleton: a `run(ast, output_dir, cost)` function that initialises a Portkey client (reuse the pattern from `multiagent.py`), seeds message history with system + user messages, loops on `tool_calls`, dispatches to tools, updates `cost`, and aborts on `cost.check_or_abort()` breach; returns a `RunSummary` dataclass with `emitted_tasks`, `inline_notes`, `total_cost`
- [ ] T015 Create `task_input_parser/prompts/system.md` v1 — agent role, task definition, procedure, tool contracts, markdown output format (section order: Task Overview → Role Description (optional) → Business Context → Schema/Requirements → Functional Requirements → Resources → Evaluation Criteria), prohibitions (no invention, no source-URL leak, inline `**Note:**` for ambiguity), termination. Single-task scope; multi-task / images / scrape added in later phases.
- [ ] T016 Wire `task_input_parser/cli.py` end-to-end: parse args → `ast.parse(path)` → create `tmp/extract_<timestamp>/` → instantiate `CostAccumulator` → call `agent.run()` → write `run.log` and `cost.json` → print summary → exit with appropriate code

---

## Phase 3: User Story 1 — Single-Task Brief Extraction (P1)

**Story goal**: A single-task `.docx` / `.md` / `.txt` brief produces exactly one markdown file in `tmp/extract_*/`.

**Independent test**: Hand-make a minimal single-task `.docx` fixture; run `python -m task_input_parser <fixture>`; confirm one `task-1-<slug>.md` is produced.

- [ ] T017 [US1] Refine `task_input_parser/prompts/system.md` for the single-task path: emit exactly one `emit_task` call after reading the entire AST; if the AST appears to contain more than one task, include an inline `**Note:**` flagging the boundary uncertainty and proceed with the best-guess single task
- [ ] T018 [US1] Add a minimal hand-made single-task fixture at `tests/task_input_parser/fixtures/single_task.docx` (content only — no test code)
- [ ] T019 [US1] Manually run `python -m task_input_parser tests/task_input_parser/fixtures/single_task.docx` and verify one markdown file lands in `tmp/extract_<timestamp>/`; check `cost.json` is under budget
- [ ] T020 [US1] Polish error messages and CLI output in `task_input_parser/cli.py` so the operator gets a clear summary (tasks emitted, inline notes counted, total cost, runtime, output dir path)

---

## Phase 4: User Story 2 — Multi-Task Brief Separation (P2)

**Story goal**: A multi-task brief produces N markdown files, one per task, with content correctly attributed.

**Independent test**: Run on a multi-task fixture; verify N files with correct partitioning.

- [ ] T021 [US2] Extend `task_input_parser/prompts/system.md` with multi-task boundary-detection guidance (heading depth, "Task N:" prefix, all-caps section markers, distinct schema/code blocks); when boundary is ambiguous, the LLM picks its best guess and adds an inline `**Note:**` in the affected markdown
- [ ] T022 [US2] Add a hand-made multi-task fixture at `tests/task_input_parser/fixtures/multi_task_no_resources.docx` (three numbered tasks under one heading; no images or external URLs)
- [ ] T023 [US2] Add the real Nerdium fixture at `tests/task_input_parser/fixtures/nerdium_test.docx` (copy of `C:\Users\Meet\Downloads\Nerdium Test.docx`)
- [ ] T024 [US2] Manually run `python -m task_input_parser tests/task_input_parser/fixtures/multi_task_no_resources.docx` and verify three markdown files are produced with correct content partitioning
- [ ] T025 [US2] Manually run `python -m task_input_parser tests/task_input_parser/fixtures/nerdium_test.docx` and verify exactly two markdown files (MySQL + frontend) with correct content separation. **Image and code-fetch will fail at this phase** (handled in US3/US4); expect inline `**Note:**` entries in the affected markdown sections

---

## Phase 5: User Story 3 — Image Resource Extraction (P2)

**Story goal**: An embedded design image is extracted, uploaded to the shared Drive `task-resources/` folder, and the per-task markdown embeds the Drive URLs (thumbnail for inline render + view URL for full-resolution fallback). **No vision-LLM analysis** — per `research.md` Decision 3, image understanding is downstream's concern.

**Independent test**: Run on a brief with one embedded image; verify the image lands in Drive with public-link reader permission and the markdown contains a Drive thumbnail URL embed.

- [ ] T026 [US3] Create `task_input_parser/tools/image.py` with Pydantic models `ProcessImageInput` (field `image_ref`) and `ProcessImageOutput` (fields `drive_thumbnail_url`, `drive_view_url`, `drive_file_id`, `width_px`, `height_px`, `content_hash`)
- [ ] T027 [US3] [P] Implement image-extraction-from-`.docx` in `task_input_parser/tools/image.py` using `zipfile` against `word/media/*`; resolves `image_ref` to local bytes + basic metadata (width, height via Pillow)
- [ ] T028 [US3] [P] Implement Drive-upload helper in `task_input_parser/tools/image.py` wrapping `non_tech_flow.google_utils.get_or_create_task_resources_folder` and `non_tech_flow.google_utils._share_publicly`; returns `{drive_thumbnail_url, drive_view_url, drive_file_id}`
- [ ] T029 [US3] Implement content-addressed cache in `task_input_parser/tools/image.py`: hash `(sha256(image_bytes))` → `tmp/parser_cache/<hash>.drive.json`. Cache hit: skip Drive upload, return cached URLs.
- [ ] T030 [US3] Register `process_image` in `task_input_parser/tools/__init__.py:all_tools()` and `dispatch()`
- [ ] T031 [US3] Extend `task_input_parser/prompts/system.md` with image-handling instructions: when to call `process_image`; how to format the inline embed (thumbnail URL via `![Design Reference](...)` for inline render, view URL on a `Full-resolution:` line for fallback)
- [ ] T032 [US3] Manually run `python -m task_input_parser tests/task_input_parser/fixtures/nerdium_test.docx` and verify (a) the frontend task's markdown contains a Drive thumbnail embed that renders inline in a markdown previewer; (b) the MySQL task's markdown has no image (no spurious call); (c) re-running uses the cached Drive URL (no second upload)

---

## Phase 6: User Story 4 — External Code Resource Extraction (P2)

**Story goal**: External code-hosting URLs (CodePen + GitHub Gist in v1) are fetched, embedded byte-for-byte as starter-code blocks in the per-task markdown, and the original URL is never leaked.

**Independent test**: Run on a brief referencing a public GitHub Gist; verify one fenced code block per file with byte-for-byte content and zero `gist.github.com` mentions in the output. Run separately on a CodePen brief; verify a `**Note:**` paragraph explains bot-protection and asks the operator to paste manually — no scrape attempted.

- [ ] T033 [US4] Create `task_input_parser/tools/fetch.py` with Pydantic models `FetchExternalCodeInput` (field `url`), `FetchedFile` (fields `filename`, `content`, `detected_language`), and `FetchExternalCodeOutput` (fields `platform_detected`, `status`, `files` list, `error` optional)
- [ ] T034 [US4] [P] Create `task_input_parser/tools/scrape/__init__.py` exporting `detect_platform(url: str) -> str` returning `"codepen"`, `"gist"`, `"codesandbox_unsupported"`, `"jsfiddle_unsupported"`, `"pastebin_unsupported"`, `"replit_unsupported"`, `"unknown"` based on URL regex
- [ ] T035 [US4] [P] Create `task_input_parser/tools/scrape/base.py` with shared helpers: content-addressed cache (`tmp/parser_cache/<sha256(url)>.json`), `validate_files(files: list[FetchedFile]) -> bool` checking each content parses cleanly per filename extension
- [ ] T036 [US4] [P] Implement `task_input_parser/tools/scrape/gist.py` exposing `fetch_gist(url) -> list[FetchedFile]`: extract `<user>/<id>` from URL; fetch each file via `requests.get` from `gist.githubusercontent.com/<user>/<id>/raw/<file>`
- [ ] T037 [US4] In `task_input_parser/tools/fetch.py`, handle CodePen URLs by returning `status="bot_protected"` immediately (no network call, no browser launch) with the canonical operator-facing message: *"Your document contains a link to a bot-protected external resource. We do not circumvent these protections (jurisdictional restrictions). Open the link, copy the source file-by-file into this document, and re-run the parser."* **No `undetected_chromedriver`** — per Decision 5 the parser does not bypass bot protection.
- [ ] T038 [US4] Wire dispatch in `task_input_parser/tools/fetch.py:fetch_external_code()`: detect platform → call appropriate fetcher → validate files → cache → return Pydantic output; on unsupported platform return status `"platform_not_supported"`; on validation/fetch failure return appropriate status with details
- [ ] T039 [US4] Register `fetch_external_code` in `task_input_parser/tools/__init__.py:all_tools()` and `dispatch()`
- [ ] T040 [US4] Verify `task_input_parser/leak_check.py:LEAK_DOMAINS` covers all platforms touched by the fetcher (CodePen, Gist, CodeSandbox, JSFiddle, Pastebin, Replit, GitLab snippets)
- [ ] T041 [US4] Extend `task_input_parser/prompts/system.md` with external-code instructions: when to call `fetch_external_code`; format starter-code blocks as fenced blocks with filename in the language hint; explicit prohibition on mentioning the source URL anywhere; on `platform_not_supported` or `fetch_failed`, the agent adds an inline `**Note:**` in the relevant section instead of embedding partial content
- [ ] T042 [US4] Manually run `python -m task_input_parser tests/task_input_parser/fixtures/nerdium_test.docx` and verify (a) the frontend task's markdown contains a `**Note:**` paragraph asking the operator to paste the CodePen source manually (no scrape attempted); (b) no `codepen.io` string anywhere in the output; (c) re-running hits cache; (d) total runtime under 60 seconds (no Chrome window opens at any point)

---

## Phase 7: User Story 5 — Role Description Extraction (P3)

**Story goal**: When the brief contains role-introducing prose, the LLM reproduces it as a `## Role Description` section in every emitted task's markdown. When absent, the section is omitted entirely.

**Independent test**: Run on a brief with an explicit role description paragraph; verify every emitted task markdown contains a populated `## Role Description` section. Run on a brief without; verify no task contains the heading.

- [ ] T043 [US5] Extend `task_input_parser/prompts/system.md` with role-description guidance: scan the brief for role-introducing prose ("we're hiring", "looking for", "the candidate should have", explicit seniority/years/skills); when found, reproduce verbatim under a `## Role Description` heading in every emitted task's markdown; when absent, omit the section entirely (heading not present)
- [ ] T044 [US5] Add a hand-made fixture at `tests/task_input_parser/fixtures/single_task_with_role.docx` containing one task plus a clear role-description paragraph; run the extractor and verify the emitted markdown has the `## Role Description` section
- [ ] T045 [US5] Manually re-run `python -m task_input_parser tests/task_input_parser/fixtures/single_task.docx` (no role description) and verify the emitted markdown has **no** `## Role Description` heading
- [ ] T046 [US5] Manually re-run `python -m task_input_parser tests/task_input_parser/fixtures/nerdium_test.docx` and verify **each** of the two emitted task markdowns contains the same `## Role Description` section if the Nerdium brief includes one (or none if it doesn't)

---

## Phase 8: Polish & Cross-Cutting Concerns

- [ ] T047 [P] Add a run-summary footer to `task_input_parser/cli.py` printing (tasks emitted, inline notes counted, total cost, total runtime, output directory path) at end of every run
- [ ] T048 [P] Ensure `run.log` captures structured entries (timestamp, stage, tool name, inputs hash, outputs hash, model, tokens, cost, duration) per FR-009
- [ ] T049 [P] Update `CLAUDE.md` to document `python -m task_input_parser <brief-path>` under "Common Commands"
- [ ] T050 [P] Update `TASK_MANAGEMENT_GUIDE.md` to reference the extractor as the first step of customer-brief handling (replacing the manual workflow in `current-state.md`)
- [ ] T051 Run end-to-end acceptance on Nerdium fixture: invoke `python -m task_input_parser tests/task_input_parser/fixtures/nerdium_test.docx`; confirm (a) two markdown files emitted, (b) ≥90% content overlap with the hand-authored `questions_prompt` in `task_input_files/input_mysql_task/basic/background_forQuestions_utkrusht_mysql_basic.json`, (c) no source-URL leakage, (d) runtime under 3 minutes, (e) cost under $2 (SC-001, SC-002, SC-005, SC-006, SC-009)
- [ ] T052 Capture any pipeline bugs discovered during T051 in `docs/known_pipeline_pitfalls.md` per constitution Principle XIII

---

## Dependencies & Execution Order

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1) ← MVP shippable
   → Phase 4 (US2) → Phase 5 (US3) → Phase 6 (US4) → Phase 7 (US5) → Phase 8 (Polish)
```

US2 / US3 / US4 phases are independent in terms of code but share the system prompt — run sequentially to avoid prompt-merge conflicts.

**Per-phase parallel opportunities** (`[P]` tasks):

- **Phase 1**: T003, T004
- **Phase 2**: T007, T010, T011
- **Phase 5 (US3)**: T027, T028
- **Phase 6 (US4)**: T034, T035, T036
- **Phase 8**: T047, T048, T049, T050

---

## Implementation Strategy — MVP First

| Ship | Tasks | What works after | Operator value |
|---|---|---|---|
| **MVP** | T001–T020 (Setup + Foundational + US1) | Single-task `.docx` / `.md` / `.txt` briefs → one markdown file per brief | Saves ~30 min/brief for the simplest case |
| **+ multi-task** | T021–T025 (US2) | Multi-task briefs → N markdown files | Saves ~60 min/brief |
| **+ images** | T026–T032 (US3) | Embedded design images extracted + uploaded to Drive + inline embed in markdown | Removes manual image-handling chore |
| **+ external code** | T033–T042 (US4) | Gist URLs → byte-for-byte starter-code blocks. CodePen / other bot-protected URLs → clean `**Note:**` directing manual paste. No source-URL leakage anywhere. | Removes manual Gist fetch chore; gives clean fallback for bot-protected platforms. |
| **+ role description** | T043–T046 (US5) | `## Role Description` section auto-populated when present in the brief | Role context surfaces in each task's markdown |
| **+ polish** | T047–T052 (Phase 8) | CLI summary, structured run log, docs updated, end-to-end acceptance on Nerdium | Operator UX feels finished; team can adopt confidently |

The team can stop after **any** ship and have a working, deployable tool.

---

## Summary

- **Total tasks**: 52
- **Tasks per user story**: US1 = 4, US2 = 5, US3 = 7, US4 = 10, US5 = 4
- **Setup / Foundational tasks**: 4 + 12 = 16
- **Polish tasks**: 6
- **Parallelisable tasks** (`[P]`): 12
- **Suggested MVP scope**: complete through T020 (end of US1)
- **Independent test criteria**:
  - US1: minimal single-task fixture → 1 markdown file (T019)
  - US2: 3-task fixture → 3 files; Nerdium fixture → 2 files (T024, T025)
  - US3: Nerdium frontend task → Drive thumbnail embed renders inline (T032)
  - US4: Nerdium frontend task → CodePen URL produces a clean bot-protected `**Note:**` (no bypass, no scrape, no Chrome launch); separately, a Gist fixture → byte-for-byte content embedded (T042)
  - US5: role-description fixture → `## Role Description` section in every task's markdown; no-role fixture → heading absent (T044, T045)

After this file is approved, the next step is `/speckit.implement T001` to begin Ship 1 (the MVP).
