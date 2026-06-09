# Context — AI-Engineering Task Category

Canonical language for the AI-engineering assessment category. Terms here are
meaningful to assessment designers (testmakers / eng leads), not implementation
details. See `docs/plans/2026-05-27-ai-engineering-task-category.html` for the plan
and `docs/adr/` for hard-to-reverse decisions.

## Glossary

**Build-it task** — the single task shape for this category. The candidate is given
a real agent codebase and must *build / extend / harden / fix* the relevant piece.
There is no "memo" or "design-doc" shape. Distinct from a *planted-failure* task,
which is a build-it task whose starting codebase contains one precise injected bug.

**Mock-LLM** — a deterministic fake LLM server (FastAPI + httpx) that impersonates
the OpenAI and Anthropic HTTP APIs on `localhost:11434`. It returns recorded
responses matched to incoming prompts via tiered matching (exact → normalized →
semantic → loud-miss). It exists so agent code runs reproducibly and for free,
with no API keys.
What it measures: the **engineering scaffolding** around a model — model fallback,
cost ceilings, tool schemas, context budgeting, observability, memory. It explicitly
does **not** test live model-wrangling intuition (a deterministic mock cannot). See
ADR on this framing. The mock's authored fixtures deliberately encode *failure modes*
(token outlier, tool-error response, truncated context, malformed JSON) — the failure
modes are the test.

**Fixture** — a recorded `(prompt → response)` entry the mock-LLM matches against.
May carry a `tool_calls` array (function-calling) and may be keyed on context variants
(e.g. answer differently if a constraint was truncated out of the prompt). Authored by
the generation LLM alongside the reference solution ("trace your own code"). Binary
fixtures (image/audio) are hand-curated, not LLM-generated.

**Two-run gate** — the generation-time quality check (NOT candidate grading). Run 1:
scaffold + EMPTY candidate slots → tests must FAIL (proves the task has real work).
Run 2: scaffold + REFERENCE solution → tests must PASS (proves solvability). Both must
hold or the task is regenerated.
*Implementation status (2026-06-02):* the gate today is **single-run** — it writes
starter code, runs `pytest` once, and passes on exit 0 *or* 1 (red starter tests are
fine), failing only on collection/compile errors or a pytest crash. The full two-run
empty-fails/reference-passes check is **deferred**. References to "two-run" describe the
target, not current behavior.

**Competency scope** — free text on a competency row naming the skill and a *menu* of
acceptable frameworks ("fluent in one of LangGraph / CrewAI / Pydantic AI"). Commits to
no single framework. Read by the classifier to route to a template. The concrete
framework for a given task is fixed by the scenario's `**Stack:**` directive, not the
scope.

**Stack directive** — a `**Stack:**` header in a scenario string that fixes the
concrete framework for *that* task (e.g. `**Stack:** LangGraph + LiteLLM`). The
reference solution and mock fixtures are written against it.

## Boundaries

**This repo = task GENERATION + generation-time gating only.** Candidate grading
lives in a **separate project** (`Utkrushta`), which grades by **video-as-judge**, not
by running our tests.

**Video-as-judge** — Utkrushta's grading model. The candidate's screen-recording +
GitHub diff are analyzed by Google Gemini against the stored `solutions` (reference),
`task_blob` (question), and `criterias` (competency names). Gemini scores against a
**generic analysis rubric selected by `task_type`** (baked into Utkrushta, not sent
per-task). It does **not** run hidden tests, execute candidate code, or use any
mock-LLM. Consequence: the only levers this repo has on the candidate's score are the
**reference solution, the question text, and the competency names** — invest there.

**The mock-LLM + hidden tests + two-run gate are generation-time-only**, with two real
purposes: (1) **gen QA** — prove an agent task is solvable + non-trivial before ship
(the *only* safety net, since video-grading won't catch a broken task); (2) **candidate
iteration** — let the candidate run their agent during the session so the video shows
real work. They are NOT the grading instrument. Therefore: tests/fixtures need only be
rich enough for the two-run gate + local iteration; the fairness-via-fixtures concern
(alternative valid prompt paths) does **not** apply, because grading never runs
candidate code.

**Mock delivery = VENDORED per repo (implemented, proven 2026-06-02).** A creator helper
copies `infra/agent_runtime/*` into each task repo's `mockllm/` and adds a fixed
`tests/conftest.py` that boots the mock as a real uvicorn server on an ephemeral port
**inside the pytest session**, exposing an `llm` client fixture. So the mock is
self-contained in the repo and has **one boot path today: the gate's pytest conftest**
(also what a candidate gets when they run the tests). Authored once
(`infra/agent_runtime`), vendored copies are generated — single source, no logic drift.

**Candidate-iteration wiring (the open Q8/Q9 decision — an *additional* boot path).** For
the candidate to run their agent *interactively* (outside pytest) and produce a rich
video, the vendored mock must be running. Decision: **Utkrushta starts the same vendored
mock** for the candidate session, keyed on a **repo-artifact marker** (e.g. presence of
`mockllm/` / `mock_llm_server.py`), and sets `OPENAI_BASE_URL` / `ANTHROPIC_BASE_URL` /
`LITELLM_API_BASE` — so the candidate doesn't launch it by hand. This is a *second* boot
path for the already-vendored mock, not central ownership. Consequence: that candidate-UX
piece carries an Utkrushta change; the gate + manual `pytest` need no Utkrushta change.
`task_type` stays `["BUILD"]`, no new column — the marker is the signal.
