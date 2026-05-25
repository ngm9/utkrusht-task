# E2B Build/Test Gate

> Companion to [classifier-and-templates.md](../task-classifier/classifier-and-templates.md).
> The classifier decides *what* a task is; this gate decides *whether the
> generated code actually runs*.

## TL;DR

After the LLM eval critics pass a generated task, the **E2B build/test gate**
boots a real sandbox, writes the generated `code_files` into it, and verifies
the code **compiles and the test suite runs**. It is a deterministic execution
check that sits behind the judgment-based LLM evals. Implemented in
`e2b_flow/sandbox_eval.py`, wired into `multiagent.py`'s `create_task` retry
loop, and gated behind the `SANDBOX_EVAL_ENABLED` env flag (off by default).

## Why this matters — the F12 failure class

The two LLM critics (`task_eval`, `code_eval`) are *judgment*: a model reads
the task and the starter code and decides if they look right. A model can read
a test file as plausible while it does not actually parse or import.

The motivating case (`F12` in `.task_agent_runs/FOLLOWUPS.md`): a Flutter task
shipped a test file full of `implements dynamic` / missing-import errors. Both
LLM critics passed it. Nothing in the pipeline ever *ran* the code, so the
broken starter shipped to a candidate.

The gate closes that hole: it does not ask "does this look right" — it runs
`pytest` and reads the exit code.

## Where it runs

Inside `create_task`'s generation retry loop (`multiagent.py`), per attempt:

```
generate  ->  LLM evals (task_eval + code_eval)  ->  [E2B gate]  ->  persist
```

- The gate runs **only when both LLM evals pass** — there is no point executing
  code the critics already rejected.
- It runs **only when `SANDBOX_EVAL_ENABLED` is truthy** (`1` / `true` / `yes`).
  Off by default, so normal runs are unaffected.
- A gate **failure** feeds the compiler/test output back as retry feedback and
  forces another generation attempt.
- A gate **skip** (see below) is logged and the task proceeds normally.
- The verdict is stored on the task row at `eval_info.sandbox_eval`.

## How it works — `run_sandbox_eval(code_files, task_runtime)`

1. **Pick a template.** `_TEMPLATE_FOR_RUNTIME` maps `task_runtime.runtime` to
   an E2B template — currently `python` → `utkrusht-python`. Any other runtime
   has no template yet → **skip** (`no_template`).
2. **Guard empty input.** No `code_files` → **skip** (`no_code`).
3. **Boot the sandbox.** `Sandbox.create(template=..., timeout=300)`. If the
   boot fails → **skip** (`infra_error`) — infra flakes never fail a task.
4. **Write the code in.** Every entry of `code_files` is written under
   `/home/user/task/`.
5. **Bring up services.** If the task ships a `docker-compose.yml`, run
   `docker compose up -d --wait` (Docker-in-Docker). A non-zero exit →
   **FAIL** (`compose_failed`).
6. **Install task deps.** If the task ships a `requirements.txt`, run
   `pip install --break-system-packages -r requirements.txt`. Non-zero →
   **FAIL** (`pip_failed`).
7. **Run the suite.** `python -m pytest -q --tb=short`.
   - If pytest collected **0 tests** (exit 5), fall back to
     `python -m compileall -q .` so a task that legitimately ships no tests
     still gets a parse gate: clean → **PASS** (`no_tests_compile_ok`);
     syntax error → **FAIL** (`compile_error`).
   - Otherwise, classify via `_classify_pytest` (below).
8. **Tear down.** `sb.kill()` runs in a `finally` block — the sandbox is always
   killed, on pass, fail, or error.

## pytest exit-code classification — `_classify_pytest`

The gate does **not** require tests to *pass*. A generated starter ships
by-design failing tests — making them green is the candidate's job. The gate
fails only when the suite cannot **compile or run**.

| pytest exit | Meaning | Verdict |
|---|---|---|
| output contains a collection error | a test/source file does not parse or import | **FAIL** `collection_error` |
| 0 | all tests passed | **PASS** `ok` |
| 1 | some tests failed (but compiled + ran) | **PASS** `ok` |
| 5 | no tests collected | handled earlier by the `compileall` fallback |
| 2 / 3 / 4 | interrupted / internal / usage error | **FAIL** `test_run_error` |

A `collection_error` is the F12 bug class itself — a file that an LLM critic
read as fine but that does not compile.

## Verdict reference — `SandboxEvalResult`

`run_sandbox_eval` returns a `SandboxEvalResult` (`passed`, `skipped`,
`verdict`, `detail`, `stdout_tail`); `.as_dict()` is persisted to
`eval_info.sandbox_eval`.

| verdict | class | meaning |
|---|---|---|
| `ok` | PASS | test suite compiled and executed |
| `no_tests_compile_ok` | PASS | no tests, but every `.py` file compiles |
| `collection_error` | FAIL | a test/source file does not parse or import |
| `compile_error` | FAIL | no tests, and `compileall` found a syntax error |
| `compose_failed` | FAIL | the task's service containers do not start |
| `pip_failed` | FAIL | `pip install -r requirements.txt` failed |
| `test_run_error` | FAIL | pytest exited 2/3/4 — the suite did not run cleanly |
| `no_template` | SKIP | no sandbox template for this runtime |
| `no_code` | SKIP | no `code_files` to evaluate |
| `infra_error` | SKIP | sandbox boot or an unexpected error — never blocks a task |

## Skip semantics — a skip never blocks a task

`skipped=True` means the gate produced **no verdict** — no template for the
runtime, no code, or an E2B infra failure. Callers must treat a skip as
**neither pass nor fail**: a task is never rejected because *our* infrastructure
flaked. Only `passed=False` (a real FAIL verdict) triggers a regeneration.

## The `utkrusht-python` template

The gate boots from a **pre-built** E2B template (`e2b_flow/templates/python/`)
rather than installing dependencies at eval time. The template bakes in:

- Python 3.12 base
- Docker-in-Docker — so a task can bring its own `docker-compose.yml` for
  service containers (Postgres / Redis / Mongo); the template stays DB-agnostic
- The fat dependency set every Python lane can ask for — web frameworks
  (fastapi, flask, django, uvicorn, gunicorn), HTTP clients, ORMs + DB clients
  (sqlalchemy, psycopg2, pymongo, redis), the LLM ecosystem (langchain,
  llama-index, openai, anthropic, pinecone, chromadb), data libs, and pytest
- Browser surfaces (ttyd, code-server, adminer) — one template lineage serves
  both the eval gate and candidate-facing deployment
- A `docker-compose` v1 → v2 shim, for task scripts that call the old binary

Because the heavy install is baked, an eval sandbox boots in seconds ready to
run; the task only tops up anything task-specific via its own
`requirements.txt`.

Build: `python build_dev.py` (→ `utkrusht-python-dev`), then
`python build_prod.py` (→ `utkrusht-python`) once verified.

## Configuration

| Knob | Where | Effect |
|---|---|---|
| `SANDBOX_EVAL_ENABLED` | env var | gate runs only when truthy (`1`/`true`/`yes`) |
| `_TEMPLATE_FOR_RUNTIME` | `sandbox_eval.py` | runtime → template map; extend as templates ship |
| `_SANDBOX_TIMEOUT_S` (300) | `sandbox_eval.py` | sandbox lifetime cap |
| `_CMD_TIMEOUT_S` (240) | `sandbox_eval.py` | per-command timeout |

## Validation

- **Unit tests** (`tests/test_sandbox_eval.py`) — `_classify_pytest` across the
  exit-code matrix, `run_sandbox_eval` skip paths, the env-flag parser.
- **Live, synthetic** — a known-good Python task → `ok` (PASS); a test file with
  a deliberate syntax error → `collection_error` (FAIL, gate caught F12).
- **Live, real pipeline** — the generated `iot-sensor-ingestion-redis-fix`
  Python+Redis task ran through the gate end to end: booted `utkrusht-python`,
  brought up its Redis service, installed deps, ran pytest → `verdict=ok`,
  recorded at `eval_info.sandbox_eval`.

## Current limits

- **Python only.** `runtime != python` skips until more templates ship
  (Go, Node, Java, etc.).
- The gate verifies *compile + run*, not test correctness — by design.
- A task that ships no tests degrades to a compile check
  (`no_tests_compile_ok`); the F12 bug class is only fully exercised when a task
  actually ships tests.
