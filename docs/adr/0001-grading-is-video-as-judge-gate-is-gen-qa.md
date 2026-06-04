# 1. Grading is video-as-judge; the generation gate is QA, not a grading instrument

Date: 2026-06-02
Status: Accepted (verify against `Utkrushta` grading DAG before building)

## Context

The AI-engineering task category plan centers on a deterministic mock-LLM, hidden
tests, and a two-run gate. The implicit assumption was that these artifacts grade the
candidate. They do not.

Candidate grading lives in a **separate project** (`Utkrushta`) and uses
**video-as-judge**: the candidate's screen recording + GitHub diff are analyzed by
Google Gemini against the stored `solutions` (reference), `task_blob` (question), and
`criterias` (competency names). The analysis rubric is a set of prompt steps **selected
by `task_type`** and baked into Utkrushta — not data we send per task. Grading does
**not** run hidden tests, execute candidate code, or use any mock-LLM.
(Source: `Utkrushta/airflow/dags/task_session_completion_dag.py` +
`video_analysis/pipeline.py`, per subagent exploration on 2026-06-02.)

## Decision

1. **Reposition the mock-LLM + hidden tests + two-run gate as generation-time-only**,
   with two purposes: (a) **gen QA** — prove an agent task is solvable + non-trivial
   before shipping; (b) **candidate iteration** — let the candidate *run* their agent
   during the session so the video shows real work. They are explicitly **not** the
   grading instrument.

2. **The gate is more valuable here, not less.** Video-grading is no safety net against
   a broken task — Gemini will still score a beautiful-but-unsolvable task from the
   video. The gate is the *only* check that the generated task actually works.
   *(Implementation status 2026-06-02: the gate is currently **single-run** — one
   `pytest` pass, accepts exit 0/1; the two-run empty-fails/reference-passes check is
   deferred. The argument holds either way.)*

3. **Invest in what grading consumes.** The only levers this repo has on a candidate's
   score are the **reference solution, the question text, and the competency names**.
   The scenario's `**Senior signal:**` content must be routed into the *persisted*
   `solutions` / `task_blob` (not left as gen-prompt-only guidance).

4. **Keep `task_type = ["BUILD"]` for v1** (A→C): steer the generic Gemini rubric via
   instrumented artifacts, ship, measure discrimination on the first cohort, and add an
   agent-aware `task_type` variant + rubric in `Utkrushta` only if the generic rubric
   cannot separate strong agent engineers from feature-completers.

5. **Drop the fairness-via-fixtures sophistication.** Because grading never runs
   candidate code, an alternative-but-valid candidate prompt path cannot be failed by a
   fixture miss. Fixtures need only be rich enough for the two-run gate + local
   iteration.

## Consequences

- The plan's effort allocation inverts: less on fixture richness / semantic matching,
  more on the reference solution + question + a "what good looks like" rubric block in
  `solutions`.
- The mock-LLM can be simpler than the plan's 4-tier design (see follow-up grilling on
  whether the semantic tier is needed at all for a gen-QA + iteration mock).
- A new, currently-absent "Handoff to grading / what grading consumes" section must be
  added to the plan.
- A new validity question replaces the original keystone: *can video-as-judge + a
  strong reference + competency names reliably assess senior agent engineering?* —
  answered empirically on the first cohort, with the grader-variant escape hatch.

## Alternatives considered

- **(B) Agent-aware grader variant from day one** — best fidelity, rejected for v1 as
  cross-project coupling that breaks the `["BUILD"]` decision before we know it's needed.
- **(A-only) Accept generic grading, no instrumentation** — cheapest, rejected: lowest
  confidence the assessment discriminates the senior signal it exists to measure.
- **Drop the mock + gate entirely** — rejected: removes the only safety net against
  shipping broken agent tasks, and removes the candidate's ability to run their agent.
