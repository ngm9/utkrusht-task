# 3. Utkrushta bootstraps the mock-LLM, keyed on a repo-artifact marker

Date: 2026-06-02
Status: Accepted

## Context

Under video-as-judge grading (ADR 0001), the mock-LLM's only candidate-facing value is
letting the candidate *run* their agent during the session, so the screen recording
shows real work. That requires the candidate's sandbox to actually start the mock + set
`OPENAI_BASE_URL` / `ANTHROPIC_BASE_URL` / `LITELLM_API_BASE`.

The generation pipeline auto-sets `is_shared_infra_required = bool(has_docker)`
(`creator.py:520`), and Utkrushta provisions a sandbox when that flag is set (or when
`template_id` is set), cloning the repo and running its setup.

Two ways to make the mock start in-session were considered: ship a per-repo
`docker-compose.yml` that runs the mock (auto-tripping `is_shared_infra_required`, zero
Utkrushta change), or have Utkrushta's session bootstrap start it.

## Decision

**The mock is VENDORED into each task repo** (implemented + proven 2026-06-02): a creator
helper copies `infra/agent_runtime/*` into the repo's `mockllm/` and adds a fixed
`tests/conftest.py` that boots the mock as a uvicorn server on an ephemeral port inside
the pytest session. Single source (`infra/agent_runtime`), generated copies — no logic
drift. **Boot path #1 (live): the gate's pytest conftest** — also what a candidate gets
when running the tests.

**Boot path #2 (this decision): Utkrushta starts the same vendored mock for the
candidate's *interactive* session.** It detects an agent task by a **repo-artifact
marker** (e.g. presence of `mockllm/` / `mock_llm_server.py`), starts the vendored mock,
and exports `OPENAI_BASE_URL` / `ANTHROPIC_BASE_URL` / `LITELLM_API_BASE`, so the
candidate can run their agent without launching the mock by hand (→ a richer video for
the grader). This is an *additional* boot path for an already-vendored mock, **not**
central ownership.

The marker is the signal — `task_type` stays `["BUILD"]` (ADR 0001) and no new column is
added. This follows `platform-prereqs.md`'s principle: route from self-describing
artifacts, not a stored intent field.

## Consequences

- **The gate and manual `pytest` need NO Utkrushta change** — the vendored conftest boots
  the mock. Only **boot path #2** (interactive candidate run) carries an Utkrushta
  session-bootstrap change; the first task requires coordinating two repos *only* for that
  UX piece, not for generation or gating.
- Mock code lives with the task (vendored); both boot paths start the *same* vendored
  server, so "runs in the gate" implies "runs for the candidate."
- A plan section "Handoff to grading / candidate session" should define the marker, the
  start command, and the env contract for boot path #2.
- Open: whether boot path #2 is worth the cross-project work for v1, or whether candidates
  can be told to run the vendored mock themselves (a one-line command) until usage
  justifies the Utkrushta bootstrap.

## Alternatives considered

- **(A) Per-repo `docker-compose` mock service** (recommended in grilling) — zero
  cross-project change, rides the existing `has_docker → is_shared_infra_required` path.
  Superseded by the **implemented** approach: vendor the mock + boot via pytest conftest,
  which is even more self-contained and already proven.
- **(C) New task column / un-defer `python-ai-agent` as the signal** — rejected: breaks
  the no-new-column anti-goal / pulls deferred platform work (ADR 0002) back in.
