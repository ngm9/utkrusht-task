# Research & Decisions

This document captures the **architectural decisions made** while designing
this feature, along with the **alternatives considered and rejected**. It's
where a reviewer can sanity-check the proposed approach against options that
weren't picked.

For the architecture itself, see [`flow.md`](./flow.md).
For the user-facing requirements, see [`spec.md`](./spec.md).

## Decision 1 — LLM-agentic loop vs. multi-pass deterministic pipeline

**Choice:** LLM-agentic loop. One Portkey call to Claude Sonnet with
function-calling enabled; the LLM decides the order and combination of tool
calls dynamically.

**Rationale:** customer briefs are highly variable. One brief has a clean
heading-per-task structure; another mixes prose and tables; another splits a
single task across two visually-distinct sections. A multi-pass pipeline
("parse → detect boundaries → classify tech → extract resources → build
spec") forces us to anticipate every shape of input in code. An agent loop
handles arbitrary shapes with the same code because the LLM decides what to
do at each step.

**Alternative rejected — Multi-pass deterministic pipeline:**
- *How it would work:* Python orchestrator with discrete LLM calls per stage,
  each stage producing a strict output that's fed to the next.
- *Why rejected:* every new brief format requires adding a new stage or
  branching an existing one. The orchestrator code grows linearly with brief
  variation. The agent loop's flexibility is more valuable than the
  multi-pass's predictability for this problem.

**Alternative rejected — Hybrid (deterministic skeleton + LLM-agentic
sub-stages):**
- *How it would work:* Python orchestrates the high-level "for each task,
  call an agentic sub-loop"; each sub-loop is itself agentic.
- *Why rejected:* nests complexity. The single-loop design is simpler to
  reason about and to debug (one set of message history, one cost
  accumulator, one set of tool calls).

## Decision 2 — Three tools vs. six (or more) separate scrapers

**Choice:** Three tools exposed to the agent: `process_image`,
`fetch_external_code`, `emit_task`. The `fetch_external_code` tool
dispatches internally to per-platform fetchers; the LLM doesn't see
platform-specific tools.

**Rationale:** the LLM doesn't need to know which platform a URL points to.
Giving it `scrape_codepen`, `scrape_codesandbox`, `scrape_jsfiddle`, etc. as
separate tools forces the LLM to do URL-pattern-matching it doesn't need to
do, and forces us to add tool definitions every time a new platform is
supported. One tool with internal dispatch keeps the agent's surface stable
and makes future platform additions an internal-only change.

**Alternative rejected — One tool per platform:**
- *How it would work:* `scrape_codepen(url)`, `scrape_codesandbox(url)`,
  `scrape_gist(url)`, …
- *Why rejected:* (1) the LLM does redundant URL-pattern matching; (2) the
  function-calling spec balloons with each platform; (3) adding a platform
  requires LLM-side change, not just internal.

**Alternative rejected — Generic `fetch_url(url)` returning raw bytes:**
- *How it would work:* one tool that fetches anything, the LLM parses the
  bytes itself.
- *Why rejected:* (1) the LLM has to do platform-specific HTML parsing
  inline, expensive and error-prone; (2) Cloudflare bypass logic still has
  to live somewhere — pushing it into the agent's context exposes the
  implementation detail.

## Decision 3 — Image handling: extract + upload only (no vision-LLM analysis)

**Choice:** `process_image` does two things atomically: extract the image
from the source document and upload it to Drive. It returns Drive URLs
(thumbnail + view) plus basic metadata (width, height, content hash) and
nothing more. **No vision-LLM analysis. No structured visual description.
No colour-palette extraction.**

**Rationale:** image *understanding* — describing the design for a
downstream consumer that can't see the image — is a downstream-consumer
concern, not an extraction concern. The extractor's job is to make the
image addressable (Drive URL embedded in the markdown) so anyone reading
the markdown can click through and view it. If a downstream task needs
visual transcription, that's the downstream task's responsibility (and a
separate spec).

Skipping vision keeps the tool surface simple, removes a category of LLM
cost from the per-brief budget, and avoids producing transcription content
that could disagree with the actual image (a quality concern when the
vision LLM mis-describes a colour or layout).

**Alternative rejected — Bundle vision-LLM analysis into `process_image`:**
- *How it would work:* `process_image` returns Drive URLs PLUS a structured
  `vision_description` + `visual_elements` list + `color_palette` produced
  by a vision-LLM call.
- *Why rejected:* moves image-understanding responsibility into the
  extractor when it belongs downstream; adds a per-image LLM cost; risks
  introducing inaccurate transcription that disagrees with the image. The
  user explicitly chose to remove this from scope.

**Alternative rejected — Three separate tools (`extract_image`,
`upload_image`, optional `analyse_image`):**
- *Why rejected:* extract + upload always happen together for any embedded
  image we surface to the operator — splitting them adds a decision the
  LLM doesn't need.

## Decision 4 — Single LLM model (Sonnet) for the whole loop vs. tiered

**Choice:** Claude Sonnet for the orchestration loop. No Haiku-tier
orchestration; no Opus-tier for premium tasks. (Vision-LLM is out per
Decision 3, so there is no second model in play.)

**Rationale:** Haiku is fast and cheap but unreliable on the kind of fuzzy
boundary-detection a real customer brief demands (mixed prose, ambiguous
numbering, tables that span sections). The cost saving from Haiku doesn't
recoup the cost of incorrect outputs that have to be redone. Sonnet handles
the full loop comfortably within the $2/brief budget (typical 2-task brief
observed at ~$0.40 in the Nerdium engagement).

**Alternative rejected — Haiku for orchestration, Sonnet for spec
construction:**
- *Why rejected:* boundary detection and tool selection are exactly where
  Haiku falls down on messy briefs. The tier-shift adds complexity for
  marginal savings.

**Alternative rejected — Opus for the whole loop:**
- *Why rejected:* unnecessary. Sonnet output quality has been good enough on
  the Nerdium engagement to not justify the price step.

## Decision 5 — Cloudflare bypass via `undetected_chromedriver` (visible browser)

**Choice:** for CodePen specifically, run `undetected_chromedriver` in
non-headless mode (a visible Chrome window briefly appears, then closes).

**Rationale:** during the Nerdium engagement we verified this is the only
reliable approach today. Plain HTTP (`requests`/`curl` with any User-Agent)
gets a 403 Cloudflare challenge page. Headless Chrome also gets blocked —
Cloudflare detects the fingerprint. Visible Chrome via
`undetected_chromedriver` passes in ~5 seconds and gives us a clearance
cookie that the same browser session then uses to fetch the `.html`/`.css`/
`.js` raw exports.

**Implication:** this feature cannot run on a headless server today. CI
support requires `xvfb` (Linux) or a managed browser service (Browserless
etc.). Out of scope for v1; documented as a constraint.

**Alternative rejected — Plain HTTP with rotating User-Agents and proxies:**
- *Why rejected:* doesn't actually pass Cloudflare's JS challenge. Higher
  ops complexity (proxy pool management), lower reliability.

**Alternative rejected — `cloudscraper` library or similar JS-execution shims:**
- *Why rejected:* Cloudflare's fingerprint detection has gotten stricter;
  these libraries' bypass rate has degraded. `undetected_chromedriver` with
  a real Chrome is the only thing that worked reliably during the engagement.

**Alternative rejected — Ask the user to manually paste the CodePen source:**
- *Why rejected:* defeats the point of automation. The manual workflow
  already does this; automating it is the whole feature.

## Decision 6 — v1 scope of supported scraping platforms

**Choice:** v1 ships with CodePen + GitHub Gist. Everything else (CodeSandbox,
JSFiddle, Pastebin, Replit, GitLab snippets) returns a structured "not yet
supported" error that the agent surfaces as an inline `**Note:**` in the affected task's markdown.

**Rationale:** CodePen is the only platform observed in real customer briefs
so far (Nerdium engagement). Gist is the second-most-common in the broader
ecosystem and is trivially easy to support (plain HTTP, no auth, no
bypass). Adding the others is a per-platform module of ~30 lines each; we
add them when a real brief needs them.

**Alternative rejected — Support all major platforms in v1:**
- *Why rejected:* speculative work for platforms we haven't seen yet in real
  briefs. Constitution Principle I (Small Correct Thing First) — ship what
  the real workload needs, add others on demand.

## Decision 7 — Output stays in `tmp/`; no auto-write to pipeline paths

**Choice:** this feature only writes to `tmp/extract_<timestamp>/`. It does
**not** write to `task_input_files/`, `task_generation_prompts/`,
`task_scenarios.json`, Supabase, GitHub, or any other shared state.

**Rationale:** human review of LLM-generated content is non-negotiable
(constitution Principle IX). Briefs are ambiguous; the LLM can confidently
produce wrong output. A 5-minute review at the `tmp/` stage prevents
60-minute "why is this task broken?" debugging downstream. Auto-write would
collapse this safety gate.

The "auto-write to pipeline" step belongs to a future feature
(`specs/002-extractor-to-pipeline-integration` when we get there).

**Alternative rejected — Auto-write with a `--dry-run` flag:**
- *Why rejected:* opt-in dry-run becomes opt-out auto-write in practice.
  Reversing the default makes the safe path the default.

## Decision 8 — Within-run idempotency only; cross-run deferred

**Choice:** within a single run, every external fetch (image / code URL) is
cached by content hash; re-running the same operation hits cache. Across
runs (re-running the parser on the same brief later), each run gets a fresh
`tmp/extract_<timestamp>/` directory; no cross-run deduplication.

**Rationale:** within-run idempotency is essential for tool reliability and
cost cap (we shouldn't re-scrape CodePen if the agent forgets it called us
already). Cross-run idempotency is nice-to-have but adds complexity (hashing
the input doc, managing a cross-run cache directory, deciding cache
invalidation policy) that we don't need yet.

When customers iterate on a brief, the operator is in the loop and decides
whether to re-use a prior run or start fresh. That's a feature, not a bug.

**Alternative rejected — Cross-run cache keyed by `sha256(brief_bytes)`:**
- *Why rejected:* premature; defer to a future spec if measured re-run rates
  justify it. Constitution Principle I.

## Decision 9 — Pydantic for tool I/O schemas

**Choice:** every tool input and output is a Pydantic model. Pydantic
generates the JSON-schema that's passed to Portkey's function-calling spec.

**Rationale:** Pydantic is already in the repo's `requirements.txt` and is
the standard schema layer across `multiagent.py`, the OpenAI structured-
output schemas in `schemas.py`, and the per-flow sub-packages. Using it for
the parser's tools keeps validation consistent with the rest of the codebase
and gives us free schema export for the agent.

**Alternative rejected — Raw `dict` arguments:**
- *Why rejected:* no validation, no schema export, no IDE support, no type
  safety.

**Alternative rejected — `dataclasses` + manual JSON-schema:**
- *Why rejected:* hand-writing JSON-schema for function-calling is tedious
  and drift-prone.

## Decision 10 — Ambiguity surfaced inline; no separate gaps file

**Choice:** when the LLM encounters genuine ambiguity (a schema column not
defined in any table, a conflicting redirect URL, a reference it can't
resolve), it includes an inline `**Note:**` paragraph in the relevant
section of the emitted markdown and proceeds. There is **no** separate
`gaps.md` artifact, no `log_gap` tool, and no structured gap-tracking
mechanism.

**Rationale:** the operator reviewing the markdown in `tmp/` sees inline
notes in context — same place, same eye-sweep. A separate `gaps.md`
splits attention across two files for no real gain. Inline notes also
ride with the markdown if it's later copied into the pipeline.

**Alternative rejected — Structured `gaps.md` file with one entry per
ambiguity:**
- *Why rejected:* extra artifact for the operator to check; ambiguity is
  always best understood in context next to the relevant content.

**Alternative rejected — LLM aborts loudly on any ambiguity:**
- *Why rejected:* over-strict; many briefs have minor ambiguity the LLM
  can navigate with a best-effort choice + inline note. Loud abort would
  block on cases that don't actually need human resolution.

## Decision 11 — Role description as a per-brief content element (no tool)

**Choice:** when the brief contains role-introducing prose (target
seniority, years of experience, must-have skills, team context), the
LLM reproduces that prose under a `## Role Description` heading in **every
emitted task markdown** for that brief. No new tool is added — role
extraction happens inside the LLM's natural content-composition step
during `emit_task`. When the brief has no role description, the heading is
omitted entirely.

**Rationale:** role description is content the LLM already reads as part of
the brief — it's not a separate fetch operation. Adding a tool would add
complexity for no benefit; a clear system-prompt instruction is sufficient.
The system prompt's "Markdown output requirements" section lists Role
Description as an **optional** section (omit when absent), placed
immediately after Task Overview.

**Alternative rejected — Add a `extract_role_description` tool:**
- *Why rejected:* unnecessary; role text is inline in the brief, the LLM
  already has it in context. A tool adds round-trips for nothing.

**Alternative rejected — Add Role Description only to the first task's
markdown, not every task:**
- *Why rejected:* downstream consumers may read tasks individually; every
  task should be self-contained. Reproducing the role description in each
  task's markdown is a small redundancy with high context-portability
  value.

## Decision 12 — No test strategy in this design phase

**Choice:** test files and test strategy are deferred to the implementation
phase. The design documents focus on architecture and decisions; specific
test coverage and fixture lists land alongside the code in `tasks.md` and
the implementation PRs.

**Rationale:** test scaffolding is implementation detail; design-time
discussion of "which tests cover US3" doesn't change the architecture and
crowds out the readable design. When `/speckit.tasks` generates the atomic
task list, each task includes its testing expectations.

## Open questions (deferred to implementation phase)

These don't need to be resolved before implementation begins, but should
be answered as part of `/speckit.tasks` output or during early implementation:

1. **Role-description detection heuristics** — does the LLM reliably
   recognise role-introducing prose ("we're hiring...", "looking for...",
   "the candidate should have..."), or do we need to seed the system prompt
   with explicit cues? Probably reliable for clearly-labelled paragraphs;
   ambiguous when role context is sprinkled throughout the brief.
2. **System prompt iteration loop** — how often will we tweak the prompt as
   real briefs surface new failure modes? Probably weekly during the first
   month; settling after.
3. **Failure-mode catalogue** — as real briefs hit production, accumulate a
   per-engagement "what went wrong" list and use it to improve the prompt +
   tool implementations.
