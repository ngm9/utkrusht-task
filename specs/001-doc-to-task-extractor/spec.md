# Feature Specification: Customer Doc → Per-Task Markdown Extractor

**Feature Branch**: `001-doc-to-task-extractor`
**Created**: 2026-05-12
**Status**: Draft
**Input**: User description: "Given a customer-supplied assessment brief (a `.docx`, `.pdf`, `.txt`, or `.md` file) that may describe one or more tasks, use an LLM as the orchestrator to read the entire brief, decide how many tasks it contains, decide which tools to call for each task (image extraction from embedded media, scraping starter code from external services like CodePen / CodeSandbox / Gist, uploading assets to the shared Google Drive, etc.), and produce one self-contained markdown file per task that captures the full task specification — the same artifact a human would otherwise hand-author into a `questions_prompt` field. Output lands in a local `tmp/` directory for human review; nothing is written to `task_input_files/`, Supabase, GitHub, or any other shared state at this stage."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Single-Task Brief Extraction (Priority: P1)

A teammate has a customer brief in `.docx` form that describes one assessment task with prose, requirements, and acceptance criteria. They want a markdown file that captures the task's full specification so they can drop it into the existing `questions_prompt` workflow without spending 30 minutes hand-extracting it.

**Why this priority**: This is the smallest possible cut of value. It validates the LLM-as-orchestrator pattern with the minimum surface area, before adding multi-task or resource-extraction complexity. If only this story ships, the team still saves ~30 minutes per customer brief.

**Independent Test**: Take a stripped-down single-task `.docx` (e.g., a hand-made fixture covering just the MySQL section of the Nerdium brief), run the extractor, and verify the resulting markdown file contains the business context, schema details, functional requirements, and evaluation criteria in a structured form. No external tool calls required.

**Acceptance Scenarios**:

1. **Given** a `.docx` brief containing exactly one task with embedded paragraphs and tables, **When** the extractor runs, **Then** a single markdown file is produced under `tmp/extract_<timestamp>/task-1.md` containing all the task's content with section headings preserved.
2. **Given** the same brief is re-run on the same input, **When** the extractor runs a second time, **Then** the output markdown is byte-identical to the first run (within-session idempotency).
3. **Given** a brief in `.txt` or `.md` format with the same content, **When** the extractor runs, **Then** the produced markdown is functionally equivalent to the `.docx` output (format-agnostic).

---

### User Story 2 — Multi-Task Brief Separation (Priority: P2)

A teammate has a customer brief that bundles multiple tasks together in one document — for example, a brief that combines a database-query task and a frontend design-replication task, or a brief that lists three numbered tasks under one heading. The LLM must decide where the boundaries lie and produce one markdown file per task.

**Why this priority**: Multi-task briefs are common in real customer engagements — most briefs we've received describe more than one assessment task. Without this support, the teammate has to manually split the input before running the extractor. With it, the extractor handles the realistic input format directly.

**Independent Test**: Run the extractor on the full Nerdium brief (`Nerdium Test.docx`) and verify exactly two markdown files are produced: one for the MySQL task and one for the frontend task. Each markdown file's content must align with the corresponding section of the source brief.

**Acceptance Scenarios**:

1. **Given** the Nerdium `.docx` brief containing both MySQL and frontend sections, **When** the extractor runs, **Then** two markdown files are produced — `task-1-mysql.md` and `task-2-frontend.md` (slug from LLM-inferred task name) — each containing only its own task's content.
2. **Given** a brief with three numbered tasks under one heading ("Task 1", "Task 2", "Task 3"), **When** the extractor runs, **Then** three markdown files are produced, each capturing one numbered task.
3. **Given** a brief that looks like one task but actually mixes two unrelated topics, **When** the extractor runs, **Then** the LLM either produces two files OR produces one file plus a clear log entry explaining why it chose to treat them as one task.

---

### User Story 3 — Image Resource Extraction (Priority: P2)

The customer brief contains an embedded design image (e.g., a popup mockup for a frontend task). The extractor must extract the image from the source document, upload it to the shared Google Drive `task-resources` folder (via the existing `non_tech_flow/google_utils.py` helpers), and embed the resulting Drive URL in the per-task markdown so a downstream consumer can render the image inline.

**Why this priority**: Design-replication and any visual-fidelity tasks require the candidate to see the design. Without image extraction, the human has to manually pull the image out of the source document, upload it to shared storage, and paste the URL into the markdown — a 20-minute chore per image observed in real engagements.

**Independent Test**: Run the extractor on a brief with one task and one embedded image. Verify the image lands in the shared Drive folder with public-link permissions, and the produced markdown contains the Drive thumbnail URL formatted as a markdown image embed.

**Acceptance Scenarios**:

1. **Given** a brief with one task and one embedded PNG image, **When** the extractor runs and the LLM decides the task requires the image, **Then** the image is uploaded to Drive `task-resources/`, permissions are set to anyone-with-link reader, and the markdown contains `![Design Reference](https://drive.google.com/thumbnail?id=<ID>&sz=w1200)` plus a `Full-resolution:` fallback link.
2. **Given** a brief with one task and no embedded image, **When** the extractor runs, **Then** no Drive upload occurs and the markdown contains no image references.
3. **Given** a brief with two tasks where only one references an image, **When** the extractor runs, **Then** only the task that needs the image gets the embed.

---

### User Story 4 — External Code Resource Extraction (Priority: P2)

The customer brief contains a URL pointing to an external code-hosting service that holds the starter code the candidate must build upon. The extractor must fetch the source files from that URL — bypassing Cloudflare and other bot-protection layers when the platform requires it — and embed the raw source code byte-for-byte in the per-task markdown as "starter code blocks", while ensuring the original URL is **not** present anywhere in the markdown. The LLM agent sees a single tool (`fetch_external_code(url)`) regardless of which platform the URL points to; platform-specific fetching logic is internal to the tool.

**Why this priority**: Starter-code-from-external-URL is the second-most-common resource type after images — customer briefs frequently link out to CodePen pens, public Gists, CodeSandbox projects, or similar to convey the starter scaffold a candidate should build on. Without this support, the human has to manually fetch the source — sometimes bypassing Cloudflare or other bot-protection layers — and paste each file into the markdown.

**Independent Test**: Run the extractor on a brief that references a public CodePen URL. Verify the markdown contains three code blocks (HTML, CSS, JS) labelled with their intended target filenames, that the contents match the pen's actual source byte-for-byte, and that the original CodePen URL appears nowhere in the markdown.

**Acceptance Scenarios**:

1. **Given** a brief referencing a public CodePen pen, **When** the extractor runs, **Then** the markdown contains three fenced code blocks under "STARTER CODE" with the pen's verbatim HTML, CSS, and JS content; the CodePen URL appears in no output file.
2. **Given** a brief referencing a public GitHub Gist, **When** the extractor runs, **Then** the markdown contains each Gist file as a fenced code block with its filename; the Gist URL appears in no output file.
3. **Given** a brief referencing an external URL whose platform is not yet supported by the fetcher (e.g., CodeSandbox in v1), **When** the extractor runs, **Then** the per-task markdown includes an inline note in the relevant section explaining that the referenced URL's platform is not yet supported and the candidate / operator should follow the link manually; no partial or corrupted starter code is embedded.
4. **Given** a brief referencing an external URL that returns a non-2xx response or is paywalled / private, **When** the extractor runs, **Then** the per-task markdown includes an inline note explaining the URL was unreachable and `run.log` records the fetch failure with status code; no partial or corrupted starter code is embedded.
5. **Given** the same external URL is referenced again in a re-run, **When** the extractor runs, **Then** the second run reads the cached content from `tmp/parser_cache/<sha256(url)>.json` and does not re-fetch over the network (idempotency).

---

### User Story 5 — Role Description Extraction (Priority: P3)

Many customer briefs include a short description of the target candidate role — seniority level, required years of experience, must-have skills, team context. When such a description is present, the extractor must capture it and include it as a dedicated **Role Description** section in each task's emitted markdown. When the brief contains no role description, the section is **omitted entirely** (not stubbed with placeholder text).

**Why this priority**: Knowing who the assessment is for shapes how it's interpreted — a "build a popup" task reads differently for a junior than for a senior. Today the role description is either lost during manual extraction or hand-copied into the `role_context` field of the background JSON. Surfacing it in the per-task markdown puts it where downstream consumers will actually see it.

**Independent Test**: Run the extractor on a brief that contains an explicit "Role" / "We're hiring" / "Looking for" paragraph. Verify each emitted task markdown contains a `## Role Description` section reproducing that role text. Run again on a brief that contains no role description; verify the section is absent.

**Acceptance Scenarios**:

1. **Given** a brief containing a paragraph like *"We're hiring a Senior Backend Engineer with 3-5 years of MySQL experience"*, **When** the extractor runs, **Then** every emitted task markdown contains a `## Role Description` section reproducing that role information faithfully (as a short paragraph or bullet list).
2. **Given** a brief with no role description anywhere, **When** the extractor runs, **Then** no emitted task markdown contains a `## Role Description` section (the heading is absent, not present-and-empty).
3. **Given** a multi-task brief where the role description applies to all tasks, **When** the extractor runs, **Then** each task's markdown includes the **same** role description verbatim (role description is per-brief context, not per-task).

---

### Edge Cases

- **Empty document**: brief contains no extractable task content. Extractor emits zero `task-*.md` files and `run.log` records a single line "(input document contained no recognisable task content)".
- **Brief in a non-English language**: extractor processes the content and produces markdown in the source language; English-translation is out of scope for v1.
- **Brief contains a screenshot of code instead of pasting it**: extractor includes an inline note in the relevant task's markdown ("the original brief included a screenshot of code at this point; OCR is not supported — please transcribe manually") rather than attempting OCR.
- **External code URL returns 200 but with an unrelated page**: extractor validates that the returned content is parseable as the expected file type before embedding; on validation failure, emits an inline note in the task's markdown and logs the failure in `run.log`.
- **Extremely large image** (>10 MB): extractor uploads to Drive anyway but `run.log` records the size and a recommendation to compress for downstream UX.
- **Same brief re-run after the customer iterates**: extractor produces a fresh `tmp/extract_<timestamp>/` directory each run; previous runs are not modified. Comparing two runs is a downstream concern.
- **Brief has neither structured headings nor numbered tasks**: extractor falls back to LLM-only boundary inference and produces best-effort output. The LLM may include inline "**Note:**" comments in the markdown where it had to guess.
- **One task references the same image twice**: image is uploaded to Drive once (content-addressed by `sha256(image_bytes)`), and the same URL is reused in both references.
- **Brief references a `file://` or local-disk path**: extractor includes an inline note in the task's markdown ("the original brief referenced a local-disk path that cannot be retrieved automatically; please attach the file separately") and does not attempt access.
- **Brief contains no role description**: the emitted markdown simply omits the `## Role Description` section (heading not present); no warning emitted.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept a customer brief in `.docx`, `.txt`, or `.md` format as v1 input. `.pdf` support is out of scope for v1 and explicitly deferred.
- **FR-002**: System MUST use an LLM as the orchestrator — the LLM reads the entire parsed brief, decides how many tasks it contains, and decides which tools to call for each task. Deterministic heuristics (heading patterns, "Task N:" prefix detection) MAY be used as hints provided to the LLM but MUST NOT be the primary decision mechanism.
- **FR-003**: System MUST produce exactly one markdown file per detected task under `tmp/extract_<YYYY-MM-DD_HH-MM-SS>/task-N-<slug>.md`. The slug is LLM-inferred from the task content (e.g., `mysql`, `frontend`, `pr-review`).
- **FR-004**: Each per-task markdown file MUST contain the full task specification in a form suitable for direct use as a `questions_prompt` value in the existing pipeline: business context, schema / requirements / constraints, functional requirements, embedded resources (images, starter code), and evaluation criteria.
- **FR-005**: System MUST expose a tool to the LLM for **image extraction** from the source document (`.docx` via `zipfile` on `word/media/*`, `.md` via referenced local paths or URLs).
- **FR-006**: System MUST expose a tool to the LLM for **image hosting** that uploads to the shared Google Drive `task-resources` folder via the existing `non_tech_flow/google_utils.py` helpers and returns the resulting Drive thumbnail and view URLs.
- **FR-007**: System MUST expose **a single tool** `fetch_external_code(url)` to the LLM for fetching starter code from an external URL. The tool's surface to the LLM is platform-agnostic — the LLM gives a URL, the tool returns a dict of `{filename: source_content}` plus a `platform_detected` field. Internal dispatch by URL pattern selects the right fetcher; the LLM never sees per-platform branches.
  - **v1 scope** (must be supported): CodePen (Cloudflare-gated, requires `undetected_chromedriver` running visible Chrome — pattern proven during a prior real customer engagement), GitHub Gist (plain HTTP against `gist.githubusercontent.com/<user>/<id>/raw/<file>`).
  - **v1 not-yet-supported** (CodeSandbox, JSFiddle, Pastebin, Replit, GitLab Snippets): the tool MUST detect these URLs and return a structured "platform not yet supported" error that the LLM agent surfaces as an inline `**Note:**` in the affected task's markdown. Adding a new platform later is a per-platform module addition; no spec change required.
  - The tool MUST validate fetched content before returning: each file's content must parse cleanly as its expected file type (HTML / CSS / JS / etc., detected by filename extension). Validation failures return a structured error, not partial content.
- **FR-007a**: External-code fetches MUST be cached locally by `sha256(url)` at `tmp/parser_cache/<hash>.json`. Re-runs on the same URL within a parser run MUST hit cache and skip the network round-trip. Failed fetches MUST also be cached (with a failure marker + reason + retry-allowed flag) so dead URLs don't trigger repeat work on every re-run.
- **FR-008**: System MUST expose a tool to the LLM for **image processing** (`process_image`) that (a) extracts the referenced image bytes from the source document, (b) uploads them to the shared Google Drive `task-resources` folder via `non_tech_flow/google_utils.py`, (c) returns Drive thumbnail URL + view URL + basic metadata (width, height, content-hash). The tool MUST NOT run any vision-LLM analysis — image understanding by downstream consumers is out of scope for this feature.
- **FR-009**: System MUST log every LLM call and every tool invocation to a structured run log under `tmp/extract_<timestamp>/run.log` with timestamps, tool name, inputs, outputs (or output reference), and cost data (input tokens, output tokens, dollar cost for LLM calls). Inline-note failures (unreachable URLs, unsupported platforms, screenshots-of-code, etc.) MUST also be entered into `run.log` so the operator has a single place to scan for issues.
- **FR-010**: System MUST cost no more than **$2.00** in LLM tokens per brief by default (constitution Principle X). Cost overruns MUST abort the run loudly with a clear error message naming the limit.
- **FR-011**: System MUST NOT write to `task_input_files/`, `task_generation_prompts/`, `task_scenarios.json`, Supabase (any environment), or GitHub during this stage. Output is confined to `tmp/extract_<timestamp>/`.
- **FR-012**: System MUST be invocable as `python -m parser <brief-path>` (sub-package CLI convention per constitution Principle II).
- **FR-013**: Within a single run, all stages are write-once: the output directory is created fresh at run start; the extractor MUST refuse to overwrite an existing `tmp/extract_<timestamp>/` directory (collision-free by timestamp).
- **FR-014**: Re-running the extractor on an unchanged brief within the same calendar second is allowed to produce a new output directory (collision is resolved by appending a uniquifier to the timestamp).
- **FR-015**: External resource URLs (CodePen, CodeSandbox, Gist, etc.) that appear in the source brief MUST be redacted from the per-task markdown — the candidate-facing artifact MUST contain the scraped *content* but never the *source URL* (constitution Principle VIII).
- **FR-016**: When the LLM emits any inline "**Note:**" entry into a task's markdown (unsupported platform, unreachable URL, screenshot-of-code, local-disk path, ambiguity it couldn't resolve), the run summary printed at exit MUST count and reference these so the operator knows to review them.
- **FR-017**: System MUST use only the Portkey gateway for all LLM calls (constitution Principle III). Provider headers MUST match the model.
- **FR-018**: System MUST extract any role description present in the brief (paragraphs introducing the target candidate role, seniority, years of experience, must-have skills, team context) and include it as a `## Role Description` section in **every** emitted task markdown. The section MUST be omitted entirely (no heading, no placeholder) when the brief contains no role description.

### Key Entities *(include if feature involves data)*

- **Customer Brief**: the input document. May be one or many tasks. Contains paragraphs, tables, embedded images, and external resource URLs.
- **Parsed AST**: deterministic structured representation of the brief produced by the input-format-specific parser (`python-docx` for `.docx`, plain read for `.md`/`.txt`). The LLM operates on this AST, not the raw file bytes.
- **Task Chunk**: the LLM's decision about which sections of the AST belong to one task. Identified by an LLM-assigned name slug and a list of section indices.
- **Resource**: any non-text artifact attached to a task. Three types: `image` (embedded binary), `code-snippet-url` (external URL to scraping), `reference-url` (URL the candidate will use unchanged, e.g., a redirect target).
- **Per-Task Markdown**: the output artifact, one per task. Contains all of the task's text plus inline-embedded resources (Drive URLs for images, fenced code blocks for scraped starter code) and an optional **Role Description** section.
- **Role Description**: an optional per-brief content element captured from any role-introducing prose in the brief. Reproduced verbatim in every task's markdown under `## Role Description`. Absent when the brief contains no role information.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For the Nerdium brief (`Nerdium Test.docx`, 2 tasks: MySQL + frontend, 1 embedded image, 1 CodePen URL), the extractor produces exactly two `task-*.md` files plus a `run.log` summary with **zero manual intervention** between invocation and output review.
- **SC-002**: The per-task markdown files for the Nerdium brief contain ≥90% of the content a human would manually extract for the `questions_prompt` field, measured by comparing the auto-output against the hand-authored `questions_prompt` text currently in `task_input_files/input_mysql_task/basic/background_forQuestions_utkrusht_mysql_basic.json` and the HTML/CSS/JS equivalent.
- **SC-003**: For a brief referencing a public CodePen URL, the starter code embedded in the per-task markdown is **byte-for-byte identical** to the CodePen pen's `.html`, `.css`, and `.js` source files.
- **SC-004**: For a brief with an embedded image, the image lands in the shared Drive `task-resources` folder with public-link permissions within the same run, and the markdown contains a Drive thumbnail URL that renders inline when the markdown is previewed in GitHub or VS Code.
- **SC-005**: The `emit_task` tool MUST run a source-URL leak check before writing any markdown file. The check is a regex over a maintained list of code-hosting domains (initially `codepen\.io`, `codesandbox\.io`, `jsfiddle\.net`, `gist\.github\.com`, `pastebin\.com`, `replit\.com`, `gitlab\.com/snippets`; the list lives in the `fetch_external_code` tool module so it's updated in lockstep with new platform support). On any match, `emit_task` MUST reject the call and return a structured error the LLM agent receives — forcing it to remove the URL and retry. No markdown file lands on disk with a source URL leaked.
- **SC-006**: LLM cost per brief, measured by the run log's cost summary, is **≤ $2.00 USD** for briefs up to 10 pages / 5 tasks.
- **SC-007**: A teammate reviewing the contents of `tmp/extract_<timestamp>/` can confirm correctness (or identify needed edits) in **under 5 minutes** for a typical 1–2 task brief.
- **SC-008**: For a brief containing a role description paragraph, every emitted task markdown contains a `## Role Description` section reproducing that role information; for a brief with no role description, no emitted task markdown contains the heading.
- **SC-009**: The end-to-end run time for the Nerdium brief (2 tasks, 1 image upload, 1 CodePen scrape with Cloudflare bypass) is **under 3 minutes** on a typical developer workstation.
- **SC-010**: Re-running the extractor on the same input produces a fresh `tmp/extract_<timestamp>/` directory without modifying or deleting any prior run's output (within-session idempotency at the file-system level).

---

## Out of Scope (deferred to later specs)

To keep this feature shippable, the following are **explicitly deferred** to future specs and MUST NOT creep into the implementation:

- Writing the extracted markdown into `task_input_files/.../background_*.json` (`questions_prompt` field) — that's a separate "spec 002 — extractor → pipeline integration" feature.
- Triggering `multiagent.py generate_tasks` after extraction — same as above.
- Inserting new competency rows into Supabase if the extracted task targets a new tech stack — separate spec.
- Writing or auto-editing a prompt module in `task_generation_prompts/` — separate spec.
- Dev → prod copy of the resulting task — separate spec.
- PDF input support — explicitly deferred to a later spec ("003 — PDF brief parsing"), even though the parser layer can technically add `pdfplumber` later.
- Cross-run idempotency by content-hash (same brief → same output dir name) — separate spec; v1 uses timestamp-keyed dirs.
- Web UI for previewing the output — separate spec.
- OCR for screenshots-of-code — separate spec.
- Translation for non-English briefs — separate spec.
