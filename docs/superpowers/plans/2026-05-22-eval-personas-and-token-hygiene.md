# Eval Personas + Token Hygiene — Implementation Plan

> **Status:** Implemented; staged for review on branch `feat/eval-personas`
> (branched off `feat/task-runtime-classifier`).
> Tests green except one pre-existing `origin/main` staleness (see Notes).

**Goal:** Two changes bundled into one PR, both unblocked by the `TaskRuntime`
classifier:

1. **F11 — token-truncation hygiene.** Raise the generation `max_tokens` cap
   and surface mid-output truncation as a typed, retryable error instead of a
   silent JSON-parse failure.
2. **Phase 1 — persona-routed eval critics.** Prepend a domain-specific
   reviewer persona to the eval-critic prompt, routed by `TaskRuntime.kind`.

**Spec:** `docs/research/task-eval-optimizer/task-eval-optimizer.md` (§1 persona
critics) and `.task_agent_runs/FOLLOWUPS.md` (F11).

---

## F11 — token-truncation hygiene

**Problem.** `utils.generate_task_with_code` called the LLM with
`max_tokens=16000`. A complex INTERMEDIATE task (multi-file repo + full README)
could exceed that, producing a JSON object cut off mid-output. All three
JSON-extraction strategies then fail and `generate_task_with_code` raises a
generic `RuntimeError: Failed to parse JSON` — the cause (token budget) is
invisible.

**Changes.**
- `utils.py` — both `chat.completions.create` calls (the per-prompt loop and
  the feedback-correction turn) raised from `max_tokens=16000` to `32000`.
- `utils.py` — after each call, inspect `response.choices[0].finish_reason`.
  When it is `"length"`, raise the new `LLMOutputTruncated(partial_text,
  attempt)` exception instead of continuing into a doomed parse.
- `evals.py` — defines `LLMOutputTruncated`. Carries the partial text and the
  attempt index for diagnostics.
- `multiagent.py` — `create_task`'s retry loop catches `LLMOutputTruncated`,
  records it as a failed attempt, and feeds back a corrective message
  ("previous attempt was cut off — keep the response shorter, close all
  braces") so the next attempt self-corrects rather than aborting the run.

## Phase 1 — persona-routed eval critics

**Problem.** `evals.py` runs one generic LLM critic over every task regardless
of domain. A generic reviewer doesn't reliably catch a missing `NOT NULL` on a
junction-table FK (a DBA would), or a chunking strategy that conflicts with the
retrieval question (an MLE would).

**Changes.**
- `evals.py` — new `PERSONA_PROMPTS: dict[str, str]`, one persona per
  `TaskRuntime.kind` value (`app`, `script`, `mobile`, `frontend`, `testing`,
  `db_only`, `llm`, `vector_db`, `non_code`). New `_persona_prefix(kind)`
  helper — returns the persona block to prepend, or `""` for `None` /
  unrecognised kinds (falls back to prior behaviour).
- `evals.py` — `llm_task_eval` and `llm_code_eval` gain an optional
  `kind: str | None = None` parameter. When supplied, the persona block is
  prepended to the existing `TASK_EVAL_PROMPT` / `CODE_EVAL_PROMPT`. Same
  model (`gpt-5-nano`), same JSON schema, same call shape — only the prompt
  prefix changes.
- `multiagent.py` — `create_task` classifies the competency set once via
  `classify_task_runtime` (one LLM call, before the retry loop), passes
  `task_runtime.kind` to `run_evaluations`, and **persists the full
  `TaskRuntime` onto the new `tasks` row** (`task_runtime` column). Net-new
  tasks now carry their runtime spec without a separate backfill.
- `multiagent.run_evaluations` — gains a `kind` parameter, threaded into both
  eval calls.

## Files changed

```
M  evals.py                       LLMOutputTruncated, PERSONA_PROMPTS,
                                   _persona_prefix, kind param on both evals
M  utils.py                       max_tokens 16k→32k, finish_reason check
M  multiagent.py                  classify once, pass kind, persist runtime,
                                   catch LLMOutputTruncated in the retry loop
M  tests/test_preflight.py        drop the 3 tests for the preflight checks
                                   removed in PR #1 (regression fix — see Notes)
A  tests/test_eval_personas.py    7 tests — persona coverage + prompt prepend
A  tests/test_token_truncation.py 2 tests — exception shape + length detection
```

## Tests

`tests/test_eval_personas.py` (7) — every `Kind` has a persona; `_persona_prefix`
empty for `None`/unknown, populated for known; `llm_task_eval` /
`llm_code_eval` prepend the persona only when `kind` is supplied.

`tests/test_token_truncation.py` (2) — `LLMOutputTruncated` carries
`partial_text` + `attempt`; `generate_task_with_code` raises it when the LLM
returns `finish_reason="length"`.

Full suite: **105 passed**, 1 pre-existing failure (see Notes).

## Notes for the reviewer

- **`tests/test_preflight.py` fix belongs to PR #1.** PR #1
  (`feat/task-runtime-classifier`) trimmed three checks out of
  `task_agent_preflight.py` but did not update this test file — so PR #1 as it
  stands has 4 failing preflight tests. This branch fixes them. If PR #1 hasn't
  merged yet, consider cherry-picking this one file's change back onto it;
  otherwise it rides in here harmlessly.
- **`tests/test_general_reference.py::test_zero_reference_combo_hits_level_6`
  is failing on `origin/main` already.** It asserts PHP + PHP-Laravel is a
  zero-reference combo, but the `php-task-prompts-input-files` merge added PHP
  prompt files — so the combo now finds Level-4 references. Stale test data,
  unrelated to this PR. Worth a one-line fix on `main` (swap in a genuinely
  reference-less combo), out of scope here.

## Out of scope (future PRs)

- I1 escalation retry — diagnose prompt-caused vs generation-caused failures;
  split small-edit patching from full prompt regeneration (the
  `eval-prefers-surgical-patch` principle). Deserves its own PR once persona
  critics have produced failure-pattern data.
- Multi-judge ensemble (task-eval-optimizer §3).
- E2B build/test gate (FOLLOWUPS.md F12).
