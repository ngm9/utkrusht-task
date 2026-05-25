# Task Builder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local conversational web app ("Task Builder") that interviews a user in natural language for the task-generation pipeline's inputs, validates them against real data, and runs the pipeline with live per-stage progress streamed into the chat.

**Architecture:** A new `task_builder/` FastAPI package drives the four existing CLI stages (`generate_input_files` → `scenario_generator` → `prompt_generator` → `multiagent generate_tasks`). The conversational bot uses structured-output slot-filling: one LLM call per turn returns JSON `{reply, slots_update, ready_to_generate}`; the server owns and validates the `TaskBrief` state. Phase 0 ("Layer B") first adds real `focus_areas` and `domain` parameters to `scenario_generator` so two of the six interview answers have somewhere to land.

**Tech Stack:** Python 3, FastAPI, uvicorn, sse-starlette, Pydantic v2, Click, pytest. LLM access via the existing Portkey gateway (Claude Sonnet 4.6 for the bot). Vanilla HTML/CSS/JS frontend.

**Spec:** `docs/superpowers/specs/2026-05-18-task-builder-conversational-frontend-design.md`

---

## Conventions for every task

- Run Python with the project venv: `.venv/bin/python`.
- Run tests with: `.venv/bin/python -m pytest <path> -v`.
- Tests live in `tests/`. `conftest.py` already loads `.env` at collection time.
- After a task's tests pass, commit. The repo owner does their own commits in
  practice — if executing via subagents, still run the commit step; if a human is
  driving, they may batch commits. Commit messages use Conventional Commits.

---

# Phase 0 — Layer B: `focus_areas` and `domain` parameters

Self-contained. After Phase 0, `scenario_generator` accepts two new optional flags
and still behaves identically when they are omitted.

## Task 1: Focus-areas and domain prompt blocks in `scenario_generator/prompts.py`

**Files:**
- Modify: `scenario_generator/prompts.py`
- Test: `tests/test_scenario_focus_domain.py` (create)

- [ ] **Step 1: Write the failing test**

Create `tests/test_scenario_focus_domain.py`:

```python
"""Layer B — focus_areas and domain wiring in scenario_generator prompts."""
from scenario_generator.prompts import (
    build_focus_areas_block,
    build_domain_rule_block,
    build_generation_prompt,
)


def test_focus_areas_block_empty_when_none():
    assert build_focus_areas_block(None) == ""
    assert build_focus_areas_block([]) == ""


def test_focus_areas_block_lists_areas_when_set():
    block = build_focus_areas_block(["idempotency", "error handling"])
    assert "ASSESSMENT FOCUS" in block
    assert "idempotency" in block
    assert "error handling" in block


def test_domain_rule_block_default_keeps_variety():
    block = build_domain_rule_block(None)
    assert "DIFFERENT business domain" in block


def test_domain_rule_block_pins_one_domain_when_set():
    block = build_domain_rule_block("fintech payments")
    assert "fintech payments" in block
    assert "ALL scenarios" in block
    assert "DIFFERENT business domain" not in block


def test_generation_prompt_injects_focus_when_set():
    prompt = build_generation_prompt(
        competencies_with_scopes="X",
        proficiency="BASIC",
        competency_names="Java",
        count=3,
        existing_scenarios=[],
        focus_areas=["idempotency"],
        domain=None,
    )
    assert "idempotency" in prompt
    assert "ASSESSMENT FOCUS" in prompt


def test_generation_prompt_pins_domain_when_set():
    prompt = build_generation_prompt(
        competencies_with_scopes="X",
        proficiency="BASIC",
        competency_names="Java",
        count=3,
        existing_scenarios=[],
        focus_areas=None,
        domain="healthcare",
    )
    assert "ALL scenarios" in prompt
    assert "healthcare" in prompt
    assert "DIFFERENT business domain" not in prompt


def test_generation_prompt_unchanged_when_no_focus_or_domain():
    """Backward compatibility: omitting both flags = today's behaviour."""
    prompt = build_generation_prompt(
        competencies_with_scopes="X",
        proficiency="BASIC",
        competency_names="Java",
        count=3,
        existing_scenarios=[],
    )
    assert "DIFFERENT business domain" in prompt
    assert "ASSESSMENT FOCUS" not in prompt
```

- [ ] **Step 2: Run the test, verify it fails**

Run: `.venv/bin/python -m pytest tests/test_scenario_focus_domain.py -v`
Expected: FAIL — `ImportError: cannot import name 'build_focus_areas_block'`.

- [ ] **Step 3: Add the block templates and builders to `prompts.py`**

In `scenario_generator/prompts.py`, after the `INTEGRATION_RULE_BLOCK_EMPTY = ""`
line (around line 416), add:

```python
# ============================================================================
# FOCUS AREAS BLOCK — user-chosen areas to bias scenarios toward (Layer B)
# ============================================================================

FOCUS_AREAS_BLOCK = """ASSESSMENT FOCUS — bias scenarios toward these areas:
{focus_areas_text}

At least one scenario MUST primarily exercise each focus area listed above. Stay within the competency scope, but prioritise these areas when choosing what each scenario tests."""

FOCUS_AREAS_BLOCK_EMPTY = ""


# ============================================================================
# DOMAIN RULE BLOCK — vary domains (default) or pin one domain (Layer B)
# ============================================================================

DOMAIN_RULE_BLOCK_VARIED = "- Each scenario MUST use a DIFFERENT business domain (fintech, healthcare, logistics, e-commerce, SaaS, edtech, travel, food delivery, IoT, media/streaming, HR/recruiting, real estate)"

DOMAIN_RULE_BLOCK_PINNED = "- ALL scenarios MUST take place in the {domain} business domain. Do NOT vary the business domain across scenarios — every scenario lives in {domain}."


def build_focus_areas_block(focus_areas: list[str] | None) -> str:
    """Render the focus-areas emphasis block, or empty string when unset."""
    if not focus_areas:
        return FOCUS_AREAS_BLOCK_EMPTY
    focus_areas_text = "\n".join(f"- {area}" for area in focus_areas)
    return FOCUS_AREAS_BLOCK.format(focus_areas_text=focus_areas_text)


def build_domain_rule_block(domain: str | None) -> str:
    """Return the domain QUALITY RULE: variety (default) or pinned to one domain."""
    if not domain:
        return DOMAIN_RULE_BLOCK_VARIED
    return DOMAIN_RULE_BLOCK_PINNED.format(domain=domain)
```

- [ ] **Step 4: Wire the placeholders into both generation prompt templates**

In `SCENARIO_GENERATION_PROMPT` (the coding template): replace the QUALITY RULES
domain line — change

```
- Each scenario MUST use a DIFFERENT business domain (fintech, healthcare, logistics, e-commerce, SaaS, edtech, travel, food delivery, IoT, media/streaming, HR/recruiting, real estate)
```

to

```
{domain_rule_block}
```

and immediately after the `{assessment_scope_block}` line in that same template,
insert a blank line then `{focus_areas_block}`.

In `SCENARIO_GENERATION_PROMPT_NON_CODE`: replace its domain line

```
- Each scenario MUST use a DIFFERENT business domain (fintech, healthcare, logistics, e-commerce, SaaS, edtech, travel, food delivery, media/streaming, HR/recruiting, real estate)
```

with `{domain_rule_block}`, and insert `{focus_areas_block}` after its
`{assessment_scope_block}` line the same way.

- [ ] **Step 5: Extend `build_generation_prompt` to accept and pass the new args**

In `build_generation_prompt`, add two parameters to the signature (after
`is_non_code: bool = False`):

```python
    focus_areas: list[str] = None,
    domain: str = None,
```

Inside the function, after `scope_block = build_assessment_scope_block(background)`,
add:

```python
    focus_block = build_focus_areas_block(focus_areas)
    domain_block = build_domain_rule_block(domain)
```

Add `focus_areas_block=focus_block` and `domain_rule_block=domain_block` to BOTH
`.format(...)` calls — the `SCENARIO_GENERATION_PROMPT_NON_CODE.format(...)` call
and the `SCENARIO_GENERATION_PROMPT.format(...)` call.

- [ ] **Step 6: Run the test, verify it passes**

Run: `.venv/bin/python -m pytest tests/test_scenario_focus_domain.py -v`
Expected: PASS — all 7 tests green.

- [ ] **Step 7: Run the full suite to confirm no regression**

Run: `.venv/bin/python -m pytest -q`
Expected: all previously-passing tests still pass.

- [ ] **Step 8: Commit**

```bash
git add scenario_generator/prompts.py tests/test_scenario_focus_domain.py
git commit -m "feat: add focus_areas and domain prompt blocks to scenario_generator"
```

---

## Task 2: Thread `focus_areas`/`domain` through `scenario_generator/generator.py`

**Files:**
- Modify: `scenario_generator/generator.py`
- Test: `tests/test_scenario_focus_domain.py` (extend)

- [ ] **Step 1: Write the failing test**

Append to `tests/test_scenario_focus_domain.py`:

```python
from unittest.mock import MagicMock
from scenario_generator.generator import call_llm_generate


def _fake_response(payload: str):
    resp = MagicMock()
    resp.output_text = payload
    resp.usage = MagicMock(input_tokens=10, output_tokens=10)
    return resp


def test_call_llm_generate_passes_focus_and_domain_into_prompt():
    client = MagicMock()
    client.responses.create.return_value = _fake_response('{"scenarios": ["s1"]}')

    competencies = [{"name": "Java", "proficiency": "BASIC",
                     "scope": "x", "long_scope": "x"}]
    call_llm_generate(
        client=client,
        competencies=competencies,
        count=1,
        existing_scenarios=[],
        focus_areas=["idempotency"],
        domain="fintech",
    )

    sent = client.responses.create.call_args.kwargs["input"]
    user_msg = next(m["content"] for m in sent if m["role"] == "user")
    assert "idempotency" in user_msg
    assert "fintech" in user_msg
    assert "ALL scenarios" in user_msg
```

- [ ] **Step 2: Run the test, verify it fails**

Run: `.venv/bin/python -m pytest tests/test_scenario_focus_domain.py::test_call_llm_generate_passes_focus_and_domain_into_prompt -v`
Expected: FAIL — `TypeError: call_llm_generate() got an unexpected keyword argument 'focus_areas'`.

- [ ] **Step 3: Add the parameters to `call_llm_generate`**

In `call_llm_generate`, add to the signature (after `is_non_code: bool = False`):

```python
    focus_areas: List[str] = None,
    domain: str = None,
```

In the `build_generation_prompt(...)` call inside `call_llm_generate`, add:

```python
        focus_areas=focus_areas,
        domain=domain,
```

- [ ] **Step 4: Add the parameters to `generate_scenarios_for_competencies`**

In `generate_scenarios_for_competencies`, add to the signature (after
`is_non_code: bool = False`):

```python
    focus_areas: List[str] = None,
    domain: str = None,
```

In the `call_llm_generate(...)` call inside the generation loop, add:

```python
                focus_areas=focus_areas,
                domain=domain,
```

- [ ] **Step 5: Run the test, verify it passes**

Run: `.venv/bin/python -m pytest tests/test_scenario_focus_domain.py -v`
Expected: PASS — all 8 tests green.

- [ ] **Step 6: Commit**

```bash
git add scenario_generator/generator.py tests/test_scenario_focus_domain.py
git commit -m "feat: thread focus_areas/domain through scenario generation"
```

---

## Task 3: CLI flags in `scenario_generator/__main__.py` and `run_pipeline.py`

**Files:**
- Modify: `scenario_generator/__main__.py`
- Modify: `run_pipeline.py`
- Test: `tests/test_scenario_focus_domain.py` (extend)

- [ ] **Step 1: Write the failing test**

Append to `tests/test_scenario_focus_domain.py`:

```python
from click.testing import CliRunner


def test_cli_accepts_focus_areas_and_domain_options():
    from scenario_generator.__main__ import generate_scenarios_cli
    runner = CliRunner()
    result = runner.invoke(generate_scenarios_cli, ["--help"])
    assert result.exit_code == 0
    assert "--focus-areas" in result.output
    assert "--domain" in result.output
```

- [ ] **Step 2: Run the test, verify it fails**

Run: `.venv/bin/python -m pytest tests/test_scenario_focus_domain.py::test_cli_accepts_focus_areas_and_domain_options -v`
Expected: FAIL — `--focus-areas` not in help output.

- [ ] **Step 3: Add the Click options to `scenario_generator/__main__.py`**

After the existing `--dry-run` `@click.option(...)` decorator and before the
`def generate_scenarios_cli(...)` line, add:

```python
@click.option(
    "--focus-areas",
    multiple=True,
    help="Areas to bias scenarios toward. Comma-separated or repeated.",
)
@click.option(
    "--domain",
    default=None,
    help="Pin all scenarios to a single business domain (e.g. 'fintech payments').",
)
```

Change the function signature from

```python
def generate_scenarios_cli(competency_file, count, output, append, background_file, dry_run):
```

to

```python
def generate_scenarios_cli(competency_file, count, output, append, background_file,
                           dry_run, focus_areas, domain):
```

Just before the `generate_scenarios_for_competencies(` call, normalise focus areas
(accept both `--focus-areas "a, b"` and repeated flags):

```python
    focus_list = []
    for item in focus_areas:
        focus_list.extend(p.strip() for p in item.split(",") if p.strip())
    if focus_list:
        click.echo(f"Focus areas: {', '.join(focus_list)}")
    if domain:
        click.echo(f"Domain (pinned): {domain}")
```

Add the two arguments to the `generate_scenarios_for_competencies(...)` call:

```python
        focus_areas=focus_list or None,
        domain=domain,
```

- [ ] **Step 4: Run the CLI test, verify it passes**

Run: `.venv/bin/python -m pytest tests/test_scenario_focus_domain.py::test_cli_accepts_focus_areas_and_domain_options -v`
Expected: PASS.

- [ ] **Step 5: Pass the flags from `run_pipeline.py` stage 2**

In `run_pipeline.py`, add two CLI options to `main()`'s `argparse` setup, after the
`--count` argument:

```python
    ap.add_argument("--focus-areas", action="append", default=[],
                    help="Focus area(s) for scenarios. Comma-separated or repeated.")
    ap.add_argument("--domain", default=None,
                    help="Pin all scenarios to one business domain.")
```

After `level = args.proficiency.upper()`, normalise focus areas:

```python
    focus_areas: list[str] = []
    for item in args.focus_areas:
        focus_areas.extend(p.strip() for p in item.split(",") if p.strip())
```

In the Stage 2 `_run_stage(combo_dir, "02_scenarios", [...])` command list, append
the new flags conditionally — change the stage 2 block to build the command first:

```python
    scenario_cmd = [
        py, "-m", "scenario_generator",
        "--competency-file", str(comp_json),
        "--background-file", str(bg_json),
        "--count", str(args.count), "--append",
    ]
    for area in focus_areas:
        scenario_cmd += ["--focus-areas", area]
    if args.domain:
        scenario_cmd += ["--domain", args.domain]
    rec = _run_stage(combo_dir, "02_scenarios", scenario_cmd)
```

- [ ] **Step 6: Verify `run_pipeline.py` still parses**

Run: `.venv/bin/python run_pipeline.py --help`
Expected: help text shows `--focus-areas` and `--domain`; exit code 0.

- [ ] **Step 7: Run the full suite**

Run: `.venv/bin/python -m pytest -q`
Expected: all tests pass.

- [ ] **Step 8: Commit**

```bash
git add scenario_generator/__main__.py run_pipeline.py tests/test_scenario_focus_domain.py
git commit -m "feat: expose --focus-areas/--domain in scenario CLI and run_pipeline"
```

**Phase 0 complete.** `scenario_generator` now honours focus areas and a pinned
domain; omitting both flags reproduces today's behaviour exactly.

---

# Phase 1 — `task_builder` backend core

## Task 4: Package skeleton, dependencies, and `slots.py`

**Files:**
- Modify: `requirements.txt`
- Create: `task_builder/__init__.py`
- Create: `task_builder/slots.py`
- Test: `tests/test_task_builder_slots.py` (create)

- [ ] **Step 1: Add dependencies and install**

Append to `requirements.txt`:

```
fastapi
uvicorn[standard]
sse-starlette
httpx
```

Run: `.venv/bin/python -m pip install fastapi "uvicorn[standard]" sse-starlette httpx`
Expected: installs succeed; `pydantic` (v2) arrives as a FastAPI dependency.

- [ ] **Step 2: Write the failing test**

Create `tests/test_task_builder_slots.py`:

```python
"""TaskBrief slot model and merge logic."""
from task_builder.slots import TaskBrief, merge_brief, REQUIRED_SLOTS


def test_empty_brief_reports_all_required_slots_missing():
    brief = TaskBrief()
    assert set(brief.missing_slots()) == set(REQUIRED_SLOTS)
    assert brief.is_complete() is False


def test_full_brief_is_complete():
    brief = TaskBrief(
        competencies=["Java"],
        proficiency="BASIC",
        role="Backend Engineer",
        focus_areas=["idempotency"],
        domain="fintech",
    )
    assert brief.missing_slots() == []
    assert brief.is_complete() is True


def test_scenario_count_defaults_to_six_and_is_not_required():
    brief = TaskBrief(
        competencies=["Java"], proficiency="BASIC", role="Eng",
        focus_areas=["x"], domain="fintech",
    )
    assert brief.scenario_count == 6


def test_merge_brief_returns_new_object_without_mutating():
    original = TaskBrief(competencies=["Java"])
    merged = merge_brief(original, {"proficiency": "BASIC"})
    assert merged.proficiency == "BASIC"
    assert original.proficiency is None  # immutability
    assert merged.competencies == ["Java"]


def test_merge_brief_ignores_unknown_keys():
    brief = TaskBrief()
    merged = merge_brief(brief, {"nonsense": "value", "domain": "saas"})
    assert merged.domain == "saas"
    assert not hasattr(merged, "nonsense")
```

- [ ] **Step 3: Run the test, verify it fails**

Run: `.venv/bin/python -m pytest tests/test_task_builder_slots.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'task_builder'`.

- [ ] **Step 4: Create the package and `slots.py`**

Create `task_builder/__init__.py`:

```python
"""Task Builder — conversational web front-end for the task-generation pipeline."""
```

Create `task_builder/slots.py`:

```python
"""TaskBrief — the six interview slots, owned authoritatively by the server."""
from __future__ import annotations

from dataclasses import dataclass, field

from pydantic import BaseModel, Field

VALID_PROFICIENCIES: tuple[str, ...] = ("BEGINNER", "BASIC", "INTERMEDIATE", "ADVANCED")
REQUIRED_SLOTS: tuple[str, ...] = ("competencies", "proficiency", "role",
                                   "focus_areas", "domain")


class TaskBrief(BaseModel):
    """The collected interview answers. `scenario_count` is optional (defaults to 6)."""

    competencies: list[str] = Field(default_factory=list)
    proficiency: str | None = None
    role: str | None = None
    focus_areas: list[str] = Field(default_factory=list)
    domain: str | None = None
    scenario_count: int = 6

    def missing_slots(self) -> list[str]:
        """Required slots that are still empty, in REQUIRED_SLOTS order."""
        missing: list[str] = []
        if not self.competencies:
            missing.append("competencies")
        if not self.proficiency:
            missing.append("proficiency")
        if not self.role:
            missing.append("role")
        if not self.focus_areas:
            missing.append("focus_areas")
        if not self.domain:
            missing.append("domain")
        return missing

    def is_complete(self) -> bool:
        return not self.missing_slots()


def merge_brief(brief: TaskBrief, update: dict) -> TaskBrief:
    """Return a NEW TaskBrief with `update`'s known fields applied. Never mutates."""
    allowed = {k: v for k, v in update.items() if k in TaskBrief.model_fields}
    return brief.model_copy(update=allowed)


@dataclass
class Message:
    role: str   # "user" | "assistant"
    content: str


@dataclass
class SessionState:
    """In-memory per-conversation state. Lost on server restart (acceptable: local tool)."""

    session_id: str
    brief: TaskBrief = field(default_factory=TaskBrief)
    history: list[Message] = field(default_factory=list)
```

- [ ] **Step 5: Run the test, verify it passes**

Run: `.venv/bin/python -m pytest tests/test_task_builder_slots.py -v`
Expected: PASS — all 5 tests green.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt task_builder/__init__.py task_builder/slots.py tests/test_task_builder_slots.py
git commit -m "feat: add task_builder package skeleton and TaskBrief slot model"
```

---

## Task 5: Slot validation in `task_builder/validation.py`

**Files:**
- Create: `task_builder/validation.py`
- Test: `tests/test_task_builder_validation.py` (create)

- [ ] **Step 1: Write the failing test**

Create `tests/test_task_builder_validation.py`:

```python
"""Slot validation against the proficiency enum and the Supabase competencies table."""
from unittest.mock import MagicMock

from task_builder.validation import validate_proficiency, validate_competency


def test_validate_proficiency_accepts_canonical_values():
    result = validate_proficiency("intermediate")
    assert result.ok is True
    assert result.cleaned == "INTERMEDIATE"


def test_validate_proficiency_rejects_unknown_value():
    result = validate_proficiency("expert")
    assert result.ok is False
    assert "BEGINNER" in result.error  # error lists valid options


def _supabase_returning(rows_for_match, all_names):
    """Build a fake Supabase client. First .execute() = the name+proficiency match,
    second .execute() = the all-names fallback query."""
    client = MagicMock()
    match_result = MagicMock(data=rows_for_match)
    all_result = MagicMock(data=[{"name": n} for n in all_names])
    table = client.table.return_value
    table.select.return_value.ilike.return_value.eq.return_value.execute.return_value = match_result
    table.select.return_value.execute.return_value = all_result
    return client


def test_validate_competency_ok_when_row_exists():
    client = _supabase_returning([{"name": "Java"}], ["Java", "Python"])
    result = validate_competency("Java", "BASIC", client)
    assert result.ok is True
    assert result.cleaned == "Java"


def test_validate_competency_suggests_close_matches_when_missing():
    client = _supabase_returning([], ["Spring Boot", "Spring", "Java"])
    result = validate_competency("Sprng Boot", "BASIC", client)
    assert result.ok is False
    assert "Spring Boot" in result.suggestions
```

- [ ] **Step 2: Run the test, verify it fails**

Run: `.venv/bin/python -m pytest tests/test_task_builder_validation.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'task_builder.validation'`.

- [ ] **Step 3: Create `task_builder/validation.py`**

```python
"""Validate interview slot values against real data before they enter the brief."""
from __future__ import annotations

import difflib
from dataclasses import dataclass, field
from typing import Any

from task_builder.slots import VALID_PROFICIENCIES


@dataclass(frozen=True)
class SlotValidation:
    """Outcome of validating one slot value."""

    ok: bool
    cleaned: Any = None
    error: str | None = None
    suggestions: tuple[str, ...] = field(default_factory=tuple)


def validate_proficiency(value: str) -> SlotValidation:
    """Normalise a proficiency string to the canonical upper-case enum value."""
    if not value:
        return SlotValidation(ok=False, error="Proficiency is empty.")
    upper = value.strip().upper()
    if upper in VALID_PROFICIENCIES:
        return SlotValidation(ok=True, cleaned=upper)
    return SlotValidation(
        ok=False,
        error=f"'{value}' is not a valid proficiency. "
              f"Choose one of: {', '.join(VALID_PROFICIENCIES)}.",
    )


def _all_competency_names(supabase) -> list[str]:
    """Fetch the distinct competency names in the table (for close-match suggestions)."""
    result = supabase.table("competencies").select("name").execute()
    return sorted({row["name"] for row in (result.data or []) if row.get("name")})


def validate_competency(name: str, proficiency: str, supabase) -> SlotValidation:
    """Check that a competency exists in Supabase at the given proficiency.

    On miss, returns up to 5 close-name suggestions so the bot can re-ask.
    """
    if not name:
        return SlotValidation(ok=False, error="Competency name is empty.")
    match = (
        supabase.table("competencies")
        .select("name")
        .ilike("name", name.strip())
        .eq("proficiency", proficiency)
        .execute()
    )
    if match.data:
        return SlotValidation(ok=True, cleaned=match.data[0]["name"])

    all_names = _all_competency_names(supabase)
    suggestions = difflib.get_close_matches(name, all_names, n=5, cutoff=0.5)
    return SlotValidation(
        ok=False,
        error=f"No competency '{name}' at {proficiency} level.",
        suggestions=tuple(suggestions),
    )
```

- [ ] **Step 4: Run the test, verify it passes**

Run: `.venv/bin/python -m pytest tests/test_task_builder_validation.py -v`
Expected: PASS — all 4 tests green.

- [ ] **Step 5: Commit**

```bash
git add task_builder/validation.py tests/test_task_builder_validation.py
git commit -m "feat: add slot validation against proficiency enum and Supabase"
```

---

## Task 6: Bot system prompt and conversation engine

**Files:**
- Create: `task_builder/prompts.py`
- Create: `task_builder/conversation.py`
- Test: `tests/test_task_builder_conversation.py` (create)

- [ ] **Step 1: Write the failing test**

Create `tests/test_task_builder_conversation.py`:

```python
"""Conversation engine — structured-output slot-filling (Approach B)."""
import json
from unittest.mock import MagicMock

import pytest

from task_builder.conversation import run_turn, _extract_json, ConversationTurn


def _client_returning(content: str):
    """Fake Portkey/OpenAI client whose chat completion returns `content`."""
    client = MagicMock()
    choice = MagicMock()
    choice.message.content = content
    client.chat.completions.create.return_value = MagicMock(choices=[choice])
    return client


def test_extract_json_pulls_object_from_surrounding_text():
    text = 'Sure! {"reply": "hi", "slots_update": {}, "ready_to_generate": false} done'
    assert _extract_json(text) == {"reply": "hi", "slots_update": {},
                                   "ready_to_generate": False}


def test_run_turn_parses_a_clean_json_response():
    payload = json.dumps({
        "reply": "What stack?",
        "slots_update": {"proficiency": "BASIC"},
        "ready_to_generate": False,
    })
    client = _client_returning(payload)
    turn = run_turn(client, history=[], user_message="hello")
    assert isinstance(turn, ConversationTurn)
    assert turn.reply == "What stack?"
    assert turn.slots_update == {"proficiency": "BASIC"}
    assert turn.ready_to_generate is False


def test_run_turn_retries_once_on_invalid_json_then_succeeds():
    good = json.dumps({"reply": "ok", "slots_update": {}, "ready_to_generate": False})
    client = MagicMock()
    bad_choice = MagicMock()
    bad_choice.message.content = "not json at all"
    good_choice = MagicMock()
    good_choice.message.content = good
    client.chat.completions.create.side_effect = [
        MagicMock(choices=[bad_choice]),
        MagicMock(choices=[good_choice]),
    ]
    turn = run_turn(client, history=[], user_message="hello")
    assert turn.reply == "ok"
    assert client.chat.completions.create.call_count == 2


def test_run_turn_gives_graceful_fallback_when_retry_also_fails():
    client = _client_returning("still not json")
    turn = run_turn(client, history=[], user_message="hello")
    assert turn.slots_update == {}
    assert turn.ready_to_generate is False
    assert turn.reply  # non-empty graceful message
```

- [ ] **Step 2: Run the test, verify it fails**

Run: `.venv/bin/python -m pytest tests/test_task_builder_conversation.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'task_builder.conversation'`.

- [ ] **Step 3: Create `task_builder/prompts.py`**

```python
"""System prompt for the Task Builder conversational bot."""

SYSTEM_PROMPT = """You are the Task Builder assistant. Your job is to interview a \
hiring engineer, in a friendly natural conversation, to assemble a complete brief for \
a coding-assessment task. You collect SIX pieces of information (slots):

1. competencies   — the tech stack(s), e.g. ["Java", "Spring Boot"]. A list of names.
2. proficiency    — exactly one of: BEGINNER, BASIC, INTERMEDIATE, ADVANCED.
3. role           — a short description of the role the candidate is hired for.
4. focus_areas    — 1-3 things the task should assess, e.g. ["idempotency", "API design"].
5. domain         — one business domain to set the task in, e.g. "fintech payments".
6. scenario_count — optional; defaults to 6 if the user does not say.

RULES:
- Ask about MISSING slots one topic at a time. Be concise and warm.
- Extract answers from whatever the user types into the structured slots_update.
- NEVER claim that task generation has started or finished. You only collect the brief.
- Set "ready_to_generate" to true ONLY when all five required slots \
(competencies, proficiency, role, focus_areas, domain) are filled.
- When ready, summarise the brief back and ask the user to confirm before generating.
- If the server tells you a competency was not found, apologise and ask again, \
offering the suggested close matches.

OUTPUT CONTRACT — every response MUST be a single JSON object, and nothing else:
{
  "reply": "<the message shown to the user>",
  "slots_update": { "<only the slots you learned this turn>": <value> },
  "ready_to_generate": <true|false>
}
Return ONLY that JSON object. No markdown, no code fences, no text around it."""
```

- [ ] **Step 4: Create `task_builder/conversation.py`**

```python
"""Structured-output conversation engine (Approach B): one LLM call per turn."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

import openai
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders

from task_builder.prompts import SYSTEM_PROMPT
from task_builder.slots import Message

BOT_MODEL = "claude-sonnet-4-6"

_FALLBACK_REPLY = ("Sorry — I got a bit confused there. Could you say that again?")


@dataclass
class ConversationTurn:
    """One parsed bot turn."""

    reply: str
    slots_update: dict = field(default_factory=dict)
    ready_to_generate: bool = False


def build_bot_client() -> openai.OpenAI:
    """Portkey gateway → Anthropic, mirroring multiagent.py's client setup."""
    return openai.OpenAI(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        base_url=PORTKEY_GATEWAY_URL,
        default_headers=createHeaders(
            provider="anthropic",
            api_key=os.getenv("PORTKEY_API_KEY"),
        ),
    )


def _extract_json(text: str) -> dict:
    """Parse the first top-level JSON object from an LLM response.

    Tolerates leading/trailing prose. Raises ValueError if none is found.
    """
    start = text.find("{")
    if start == -1:
        raise ValueError("no JSON object in response")
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start:i + 1])
    raise ValueError("unbalanced JSON object in response")


def _to_turn(parsed: dict) -> ConversationTurn:
    return ConversationTurn(
        reply=str(parsed.get("reply", "")).strip() or _FALLBACK_REPLY,
        slots_update=parsed.get("slots_update") or {},
        ready_to_generate=bool(parsed.get("ready_to_generate", False)),
    )


def _call(client: openai.OpenAI, messages: list[dict]) -> str:
    resp = client.chat.completions.create(model=BOT_MODEL, messages=messages)
    return resp.choices[0].message.content or ""


def run_turn(client: openai.OpenAI, history: list[Message],
             user_message: str) -> ConversationTurn:
    """Run one conversation turn. Retries once on unparseable JSON, then degrades
    gracefully to a fallback reply rather than raising."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += [{"role": m.role, "content": m.content} for m in history]
    messages.append({"role": "user", "content": user_message})

    try:
        return _to_turn(_extract_json(_call(client, messages)))
    except (ValueError, json.JSONDecodeError):
        pass

    nudge = messages + [{"role": "user",
                         "content": "Your last reply was not valid JSON. "
                                    "Reply again with ONLY the JSON object."}]
    try:
        return _to_turn(_extract_json(_call(client, nudge)))
    except (ValueError, json.JSONDecodeError):
        return ConversationTurn(reply=_FALLBACK_REPLY)
```

- [ ] **Step 5: Run the test, verify it passes**

Run: `.venv/bin/python -m pytest tests/test_task_builder_conversation.py -v`
Expected: PASS — all 4 tests green.

- [ ] **Step 6: Commit**

```bash
git add task_builder/prompts.py task_builder/conversation.py tests/test_task_builder_conversation.py
git commit -m "feat: add conversation engine and bot system prompt"
```

---

## Task 7: Turn orchestration — validate, merge, corrective call

**Files:**
- Modify: `task_builder/conversation.py`
- Test: `tests/test_task_builder_conversation.py` (extend)

- [ ] **Step 1: Write the failing test**

Append to `tests/test_task_builder_conversation.py`:

```python
import json as _json
from task_builder.conversation import apply_turn, ChatResult
from task_builder.slots import SessionState


def _client_seq(*payloads):
    """Fake client returning each payload in order across calls."""
    client = MagicMock()
    choices = []
    for p in payloads:
        c = MagicMock()
        c.message.content = p
        choices.append(MagicMock(choices=[c]))
    client.chat.completions.create.side_effect = choices
    return client


def _supabase_ok():
    client = MagicMock()
    table = client.table.return_value
    table.select.return_value.ilike.return_value.eq.return_value.execute.return_value = \
        MagicMock(data=[{"name": "Java"}])
    return client


def test_apply_turn_merges_valid_slots_into_session_brief():
    session = SessionState(session_id="s1")
    payload = _json.dumps({
        "reply": "Got it.",
        "slots_update": {"proficiency": "basic", "role": "Backend Engineer"},
        "ready_to_generate": False,
    })
    result = apply_turn(session, "I need a basic backend task",
                        client=_client_seq(payload), supabase=_supabase_ok())
    assert isinstance(result, ChatResult)
    assert session.brief.proficiency == "BASIC"   # normalised
    assert session.brief.role == "Backend Engineer"
    assert "proficiency" not in result.missing_slots


def test_apply_turn_rejects_invalid_proficiency_and_does_not_store_it():
    session = SessionState(session_id="s1")
    bad = _json.dumps({"reply": "ok", "slots_update": {"proficiency": "wizard"},
                       "ready_to_generate": False})
    corrected = _json.dumps({"reply": "Which level?", "slots_update": {},
                             "ready_to_generate": False})
    result = apply_turn(session, "make it wizard level",
                        client=_client_seq(bad, corrected), supabase=_supabase_ok())
    assert session.brief.proficiency is None
    assert "proficiency" in result.missing_slots


def test_apply_turn_ready_only_when_server_agrees_brief_is_complete():
    session = SessionState(session_id="s1")
    session.brief = session.brief.model_copy(update={
        "competencies": ["Java"], "proficiency": "BASIC", "role": "Eng",
        "focus_areas": ["idempotency"], "domain": "fintech",
    })
    payload = _json.dumps({"reply": "Ready!", "slots_update": {},
                           "ready_to_generate": True})
    result = apply_turn(session, "looks good",
                        client=_client_seq(payload), supabase=_supabase_ok())
    assert result.ready is True
```

- [ ] **Step 2: Run the test, verify it fails**

Run: `.venv/bin/python -m pytest tests/test_task_builder_conversation.py -k apply_turn -v`
Expected: FAIL — `ImportError: cannot import name 'apply_turn'`.

- [ ] **Step 3: Add `ChatResult` and `apply_turn` to `conversation.py`**

Add these imports at the top of `task_builder/conversation.py`:

```python
from task_builder.slots import SessionState, TaskBrief, merge_brief
from task_builder.validation import validate_competency, validate_proficiency
```

(Keep the existing `from task_builder.slots import Message` — combine the two
`task_builder.slots` imports into one line.)

Append to `task_builder/conversation.py`:

```python
@dataclass
class ChatResult:
    """What the /api/chat handler returns to the browser."""

    reply: str
    brief: TaskBrief
    missing_slots: list[str]
    ready: bool


def _clean_slots_update(update: dict, supabase) -> tuple[dict, list[str]]:
    """Validate a raw slots_update. Returns (accepted_fields, rejection_messages).

    Rejected fields are dropped — the server never stores an unvalidated value.
    """
    accepted: dict = {}
    rejections: list[str] = []

    if "proficiency" in update:
        check = validate_proficiency(str(update["proficiency"]))
        if check.ok:
            accepted["proficiency"] = check.cleaned
        else:
            rejections.append(check.error or "Invalid proficiency.")

    # competency validation needs a proficiency — prefer the just-accepted one.
    proficiency = accepted.get("proficiency")
    if "competencies" in update and proficiency:
        names = update["competencies"] or []
        good: list[str] = []
        for name in names:
            check = validate_competency(str(name), proficiency, supabase)
            if check.ok:
                good.append(check.cleaned)
            else:
                hint = (f" Did you mean: {', '.join(check.suggestions)}?"
                        if check.suggestions else "")
                rejections.append((check.error or "Unknown competency.") + hint)
        if good:
            accepted["competencies"] = good

    for plain in ("role", "domain"):
        if update.get(plain):
            accepted[plain] = str(update[plain]).strip()
    if update.get("focus_areas"):
        accepted["focus_areas"] = [str(x).strip() for x in update["focus_areas"] if str(x).strip()]
    if isinstance(update.get("scenario_count"), int):
        accepted["scenario_count"] = update["scenario_count"]

    return accepted, rejections


def apply_turn(session: SessionState, user_message: str, *,
               client: openai.OpenAI, supabase) -> ChatResult:
    """Run one full chat turn: LLM call → validate → merge → (corrective call)."""
    turn = run_turn(client, session.history, user_message)
    accepted, rejections = _clean_slots_update(turn.slots_update, supabase)
    session.brief = merge_brief(session.brief, accepted)

    reply = turn.reply
    # If the server rejected something, give the bot one corrective turn so the
    # re-ask reaches the user inside this same response.
    if rejections:
        note = ("SERVER VALIDATION: the following values were rejected and NOT "
                "saved — " + " ".join(rejections) + " Ask the user to correct them.")
        corrective = run_turn(client, session.history,
                              user_message + "\n\n" + note)
        reply = corrective.reply

    session.history.append(Message(role="user", content=user_message))
    session.history.append(Message(role="assistant", content=reply))

    missing = session.brief.missing_slots()
    ready = turn.ready_to_generate and not missing
    return ChatResult(reply=reply, brief=session.brief,
                      missing_slots=missing, ready=ready)
```

- [ ] **Step 4: Run the test, verify it passes**

Run: `.venv/bin/python -m pytest tests/test_task_builder_conversation.py -v`
Expected: PASS — all 7 tests green.

- [ ] **Step 5: Commit**

```bash
git add task_builder/conversation.py tests/test_task_builder_conversation.py
git commit -m "feat: add turn orchestration with validation and corrective call"
```

---

## Task 8: FastAPI server — chat routes

**Files:**
- Create: `task_builder/server.py`
- Create: `task_builder/__main__.py`
- Test: `tests/test_task_builder_server.py` (create)

- [ ] **Step 1: Write the failing test**

Create `tests/test_task_builder_server.py`:

```python
"""FastAPI chat routes — /api/health, /api/session, /api/chat."""
import json
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from task_builder.server import app


def _payload(reply, slots, ready):
    return json.dumps({"reply": reply, "slots_update": slots,
                       "ready_to_generate": ready})


def test_health_endpoint():
    client = TestClient(app)
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_session_then_chat_flow():
    client = TestClient(app)
    fake_client = MagicMock()
    choice = MagicMock()
    choice.message.content = _payload("Hi! What stack?", {}, False)
    fake_client.chat.completions.create.return_value = MagicMock(choices=[choice])

    with patch("task_builder.server.build_bot_client", return_value=fake_client), \
         patch("task_builder.server.get_supabase", return_value=MagicMock()):
        session = client.post("/api/session").json()
        assert "session_id" in session

        chat = client.post("/api/chat", json={
            "session_id": session["session_id"],
            "message": "I want a task",
        }).json()
        assert "reply" in chat
        assert "brief" in chat
        assert "missing_slots" in chat
        assert chat["ready"] is False


def test_chat_with_unknown_session_returns_404():
    client = TestClient(app)
    resp = client.post("/api/chat", json={"session_id": "nope", "message": "hi"})
    assert resp.status_code == 404
```

- [ ] **Step 2: Run the test, verify it fails**

Run: `.venv/bin/python -m pytest tests/test_task_builder_server.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'task_builder.server'`.

- [ ] **Step 3: Create `task_builder/server.py`**

```python
"""FastAPI app for Task Builder — chat routes (generation routes added in Phase 2)."""
from __future__ import annotations

import uuid

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from generate_input_files.generator import init_supabase
from task_builder.conversation import apply_turn, build_bot_client
from task_builder.slots import SessionState

app = FastAPI(title="Task Builder")

# In-memory session store — lost on restart (acceptable for a local single-user tool).
SESSIONS: dict[str, SessionState] = {}

_GREETING = ("Hi! I'll help you put together a coding assessment. "
             "First — what tech stack should the candidate work in?")


def get_supabase():
    """Supabase client for competency validation (dev environment)."""
    return init_supabase("dev")


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/session")
def create_session() -> dict:
    """Start a conversation; returns a session id and the bot's opening line."""
    session_id = uuid.uuid4().hex
    SESSIONS[session_id] = SessionState(session_id=session_id)
    return {"session_id": session_id, "reply": _GREETING}


@app.post("/api/chat")
def chat(req: ChatRequest) -> dict:
    """Run one conversation turn against the session's brief."""
    session = SESSIONS.get(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Unknown session")

    result = apply_turn(session, req.message,
                        client=build_bot_client(), supabase=get_supabase())
    return {
        "reply": result.reply,
        "brief": result.brief.model_dump(),
        "missing_slots": result.missing_slots,
        "ready": result.ready,
    }
```

> Note: the `StaticFiles` / `FileResponse` imports are used by the frontend route
> added in Task 12. They are imported now so the file is not re-edited for imports.

- [ ] **Step 4: Create `task_builder/__main__.py`**

```python
"""Launch the Task Builder web server: python -m task_builder."""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("task_builder.server:app", host="127.0.0.1", port=8000, reload=False)
```

- [ ] **Step 5: Run the test, verify it passes**

Run: `.venv/bin/python -m pytest tests/test_task_builder_server.py -v`
Expected: PASS — all 3 tests green.

- [ ] **Step 6: Commit**

```bash
git add task_builder/server.py task_builder/__main__.py tests/test_task_builder_server.py
git commit -m "feat: add FastAPI server with chat routes and launcher"
```

**Phase 1 complete.** The bot can hold a full slot-filling conversation over HTTP.

---

# Phase 2 — Pipeline runner and live streaming

## Task 9: Background pipeline runner in `task_builder/runner.py`

**Files:**
- Create: `task_builder/runner.py`
- Test: `tests/test_task_builder_runner.py` (create)

`run_pipeline.py` already exposes the module-level helpers `_run_stage`,
`_locate_input_files`, and `_summarise_task_stage`. The runner reuses them directly
— no refactor of `run_pipeline.py` is required (a refinement of spec §9).

- [ ] **Step 1: Write the failing test**

Create `tests/test_task_builder_runner.py`:

```python
"""Background pipeline runner — stage events and failure handling."""
from unittest.mock import patch

from task_builder.runner import run_pipeline_for_brief, StageEvent
from task_builder.slots import TaskBrief


def _brief():
    return TaskBrief(competencies=["Java"], proficiency="BASIC", role="Eng",
                     focus_areas=["idempotency"], domain="fintech")


def _stage_ok(label):
    return {"label": label, "exit_code": 0, "duration_s": 1.0,
            "stdout": "/tmp/x.stdout", "stderr": "/tmp/x.stderr", "cmd": []}


def test_runner_emits_one_event_per_stage_on_success(tmp_path):
    events: list[StageEvent] = []

    with patch("task_builder.runner._run_stage", side_effect=lambda d, label, c: _stage_ok(label)), \
         patch("task_builder.runner._locate_input_files",
               return_value=(tmp_path / "c.json", tmp_path / "b.json")), \
         patch("task_builder.runner._summarise_task_stage", return_value="TASK CREATED"):
        run_pipeline_for_brief(_brief(), run_id="r1", emit=events.append,
                               runs_root=tmp_path)

    labels = [e.stage for e in events if e.status in ("ok", "failed")]
    assert labels == ["00_preflight", "01_input_files", "02_scenarios",
                      "03_prompt", "04_tasks"]
    assert events[-1].stage == "done"
    assert events[-1].status == "completed"


def test_runner_stops_and_reports_on_stage_failure(tmp_path):
    events: list[StageEvent] = []

    def fake_stage(d, label, c):
        rec = _stage_ok(label)
        if label == "02_scenarios":
            rec["exit_code"] = 1
        return rec

    with patch("task_builder.runner._run_stage", side_effect=fake_stage), \
         patch("task_builder.runner._locate_input_files",
               return_value=(tmp_path / "c.json", tmp_path / "b.json")):
        run_pipeline_for_brief(_brief(), run_id="r2", emit=events.append,
                               runs_root=tmp_path)

    assert any(e.stage == "02_scenarios" and e.status == "failed" for e in events)
    assert events[-1].stage == "done"
    assert events[-1].status == "failed"
    assert not any(e.stage == "03_prompt" for e in events)  # stopped early
```

- [ ] **Step 2: Run the test, verify it fails**

Run: `.venv/bin/python -m pytest tests/test_task_builder_runner.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'task_builder.runner'`.

- [ ] **Step 3: Create `task_builder/runner.py`**

```python
"""Run the four-stage pipeline for a TaskBrief, emitting a StageEvent per stage."""
from __future__ import annotations

import datetime
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from run_pipeline import (
    REPO_ROOT,
    RUNS_DIR,
    SCENARIOS_FILE,
    _locate_input_files,
    _pick_python,
    _run_stage,
    _summarise_task_stage,
)
from task_builder.slots import TaskBrief

# Ordered stage labels the runner walks through.
STAGES = ("00_preflight", "01_input_files", "02_scenarios", "03_prompt", "04_tasks")


@dataclass
class StageEvent:
    """One progress event streamed to the browser."""

    stage: str               # a STAGES label, or "done"
    status: str              # "running" | "ok" | "failed" | "completed"
    detail: str = ""
    duration_s: float | None = None
    outcome: str | None = None


EmitFn = Callable[[StageEvent], None]


def run_pipeline_for_brief(brief: TaskBrief, *, run_id: str, emit: EmitFn,
                           runs_root: Path = RUNS_DIR) -> None:
    """Execute the pipeline for `brief`, calling `emit` before and after each stage.

    Stops at the first failing stage. Always emits a terminal "done" event.
    """
    py = _pick_python()
    names = list(brief.competencies)
    level = (brief.proficiency or "BASIC").upper()
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    combo_dir = runs_root / f"web-{ts}-{run_id}"
    combo_dir.mkdir(parents=True, exist_ok=True)

    def _stage(label: str, cmd: list[str]) -> dict:
        emit(StageEvent(stage=label, status="running"))
        start = time.time()
        rec = _run_stage(combo_dir, label, cmd)
        ok = rec["exit_code"] == 0
        emit(StageEvent(stage=label, status="ok" if ok else "failed",
                        duration_s=round(time.time() - start, 1),
                        detail="" if ok else f"exit code {rec['exit_code']}"))
        return rec

    try:
        rec = _stage("00_preflight", [
            py, "task_agent_preflight.py",
            "--combo", f"{','.join(names)}:{level}", "--env", "dev",
        ])
        if rec["exit_code"] != 0:
            return emit(StageEvent("done", "failed", detail="preflight failed"))

        t0 = time.time()
        rec = _stage("01_input_files", [
            py, "-m", "generate_input_files",
            "--competency-name", ", ".join(names),
            "--proficiency", level, "--role", brief.role or "", "--env", "dev",
        ])
        if rec["exit_code"] != 0:
            return emit(StageEvent("done", "failed", detail="input files failed"))

        comp_json, bg_json = _locate_input_files(names, level, t0)

        scenario_cmd = [
            py, "-m", "scenario_generator",
            "--competency-file", str(comp_json), "--background-file", str(bg_json),
            "--count", str(brief.scenario_count), "--append",
        ]
        for area in brief.focus_areas:
            scenario_cmd += ["--focus-areas", area]
        if brief.domain:
            scenario_cmd += ["--domain", brief.domain]
        rec = _stage("02_scenarios", scenario_cmd)
        if rec["exit_code"] != 0:
            return emit(StageEvent("done", "failed", detail="scenario stage failed"))

        rec = _stage("03_prompt", [
            py, "-m", "prompt_generator", "--name", ", ".join(names),
            "--proficiency", level, "--env", "dev", "--force", "--verbose",
        ])
        if rec["exit_code"] != 0:
            return emit(StageEvent("done", "failed", detail="prompt stage failed"))

        rec = _stage("04_tasks", [
            py, "multiagent.py", "generate_tasks",
            "-c", str(comp_json), "-b", str(bg_json), "-s", str(SCENARIOS_FILE),
        ])
        outcome = _summarise_task_stage(Path(rec["stdout"]))
        if rec["exit_code"] != 0 or "REJECTED" in outcome or "ERROR" in outcome:
            return emit(StageEvent("done", "failed", detail=outcome, outcome=outcome))

        emit(StageEvent("done", "completed", detail=outcome, outcome=outcome))
    except Exception as exc:  # noqa: BLE001 — surface any stage crash to the UI
        emit(StageEvent("done", "failed", detail=f"runner error: {exc}"))
```

- [ ] **Step 4: Run the test, verify it passes**

Run: `.venv/bin/python -m pytest tests/test_task_builder_runner.py -v`
Expected: PASS — both tests green.

- [ ] **Step 5: Commit**

```bash
git add task_builder/runner.py tests/test_task_builder_runner.py
git commit -m "feat: add background pipeline runner with stage events"
```

---

## Task 10: Generation routes and SSE streaming in `server.py`

**Files:**
- Modify: `task_builder/server.py`
- Test: `tests/test_task_builder_server.py` (extend)

- [ ] **Step 1: Write the failing test**

Append to `tests/test_task_builder_server.py`:

```python
from task_builder.slots import TaskBrief


def test_generate_rejects_incomplete_brief():
    client = TestClient(app)
    session = client.post("/api/session").json()
    resp = client.post("/api/generate", json={"session_id": session["session_id"]})
    assert resp.status_code == 400  # brief not ready


def test_generate_starts_a_run_for_a_complete_brief():
    client = TestClient(app)
    session = client.post("/api/session").json()
    sid = session["session_id"]

    # Inject a complete brief directly into the session store.
    from task_builder.server import SESSIONS
    SESSIONS[sid].brief = TaskBrief(
        competencies=["Java"], proficiency="BASIC", role="Eng",
        focus_areas=["idempotency"], domain="fintech",
    )

    with patch("task_builder.server._launch_run") as launch:
        resp = client.post("/api/generate", json={"session_id": sid})
        assert resp.status_code == 200
        assert "run_id" in resp.json()
        launch.assert_called_once()
```

- [ ] **Step 2: Run the test, verify it fails**

Run: `.venv/bin/python -m pytest tests/test_task_builder_server.py -k generate -v`
Expected: FAIL — `/api/generate` returns 404 (route not defined).

- [ ] **Step 3: Add the generation routes to `server.py`**

Add these imports to the top of `task_builder/server.py`:

```python
import asyncio
import queue
import threading

from sse_starlette.sse import EventSourceResponse

from task_builder.runner import StageEvent, run_pipeline_for_brief
```

Add this run registry and helpers below the `SESSIONS` declaration:

```python
# In-memory run registry: run_id -> a thread-safe event queue.
RUNS: dict[str, "queue.Queue[StageEvent]"] = {}


def _launch_run(run_id: str, brief) -> None:
    """Start the pipeline in a worker thread; events land on RUNS[run_id]."""
    q: "queue.Queue[StageEvent]" = queue.Queue()
    RUNS[run_id] = q
    threading.Thread(
        target=run_pipeline_for_brief,
        args=(brief,),
        kwargs={"run_id": run_id, "emit": q.put},
        daemon=True,
    ).start()
```

Add the two routes at the end of `server.py`:

```python
class GenerateRequest(BaseModel):
    session_id: str


@app.post("/api/generate")
def generate(req: GenerateRequest) -> dict:
    """Kick off a pipeline run for a session whose brief is complete."""
    session = SESSIONS.get(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Unknown session")
    if not session.brief.is_complete():
        raise HTTPException(status_code=400, detail="Brief is not complete")

    run_id = uuid.uuid4().hex
    _launch_run(run_id, session.brief)
    return {"run_id": run_id}


@app.get("/api/runs/{run_id}/events")
async def run_events(run_id: str):
    """Server-Sent Events stream of StageEvents for a run."""
    q = RUNS.get(run_id)
    if q is None:
        raise HTTPException(status_code=404, detail="Unknown run")

    async def event_source():
        loop = asyncio.get_event_loop()
        while True:
            event: StageEvent = await loop.run_in_executor(None, q.get)
            yield {"data": __import__("json").dumps(event.__dict__)}
            if event.stage == "done":
                break

    return EventSourceResponse(event_source())
```

- [ ] **Step 4: Run the test, verify it passes**

Run: `.venv/bin/python -m pytest tests/test_task_builder_server.py -v`
Expected: PASS — all 5 tests green.

- [ ] **Step 5: Commit**

```bash
git add task_builder/server.py tests/test_task_builder_server.py
git commit -m "feat: add generate route and SSE event streaming"
```

**Phase 2 complete.** A complete brief now launches the pipeline and streams
per-stage progress.

---

# Phase 3 — Frontend

The frontend is vanilla HTML/CSS/JS; the repo has no JavaScript test runner, and
adding one is out of scope. Frontend tasks are verified by (a) server-side route
tests and (b) the documented manual browser checklist in Task 13.

## Task 11: Static page and styles

**Files:**
- Create: `task_builder/static/index.html`
- Create: `task_builder/static/styles.css`
- Modify: `task_builder/server.py` (serve the page)
- Test: `tests/test_task_builder_server.py` (extend)

- [ ] **Step 1: Write the failing test**

Append to `tests/test_task_builder_server.py`:

```python
def test_root_serves_the_task_builder_page():
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Task Builder" in resp.text
```

- [ ] **Step 2: Run the test, verify it fails**

Run: `.venv/bin/python -m pytest tests/test_task_builder_server.py -k root_serves -v`
Expected: FAIL — `GET /` returns 404.

- [ ] **Step 3: Create `task_builder/static/styles.css`**

```css
:root {
  --bg:#0f1115; --panel:#161a22; --border:#262c38; --text:#e6e8ee;
  --muted:#8a93a6; --user:linear-gradient(135deg,#7c5cff,#4ea3ff);
  --bot:#232938; --good:#34d399; --bad:#f87171;
}
* { box-sizing:border-box; }
html,body { height:100%; margin:0; }
body {
  font:14px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;
  background:radial-gradient(1200px 600px at 20% -10%,#1c1f2e,var(--bg) 60%);
  color:var(--text); display:flex; flex-direction:column;
}
header {
  padding:14px 22px; border-bottom:1px solid var(--border);
  display:flex; align-items:center; gap:10px;
}
.logo { width:26px; height:26px; border-radius:8px; background:var(--user); }
header h1 { font-size:15px; margin:0; font-weight:600; }
main { flex:1; overflow-y:auto; padding:26px 0 130px; display:flex;
  justify-content:center; }
.chat { width:min(720px,92vw); display:flex; flex-direction:column; gap:12px; }
.row { display:flex; gap:10px; align-items:flex-end; }
.row.user { justify-content:flex-end; }
.avatar { width:28px; height:28px; border-radius:50%; display:grid;
  place-items:center; font-size:12px; font-weight:700; flex-shrink:0; }
.avatar.bot { background:#2b3142; color:#cdd3e0; }
.avatar.user { background:var(--user); color:#fff; }
.bubble { max-width:78%; padding:11px 14px; border-radius:14px;
  white-space:pre-wrap; word-wrap:break-word; }
.bot .bubble { background:var(--bot); border:1px solid var(--border);
  border-bottom-left-radius:4px; }
.user .bubble { background:var(--user); color:#fff; border-bottom-right-radius:4px; }
.stage { color:var(--muted); font-size:13px; }
.stage.ok { color:var(--good); }
.stage.failed { color:var(--bad); }
.summary { background:var(--panel); border:1px solid var(--border);
  border-radius:14px; padding:14px 16px; }
.summary h4 { margin:0 0 10px; font-size:13px; }
.kv { display:grid; grid-template-columns:130px 1fr; gap:6px 12px; font-size:13px; }
.kv .k { color:var(--muted); }
.cta { margin-top:12px; background:var(--user); color:#fff; border:0;
  padding:9px 14px; border-radius:10px; font-weight:600; cursor:pointer; }
.cta[disabled] { opacity:.5; cursor:default; }
.dock { position:fixed; left:0; right:0; bottom:0; padding:14px 22px 18px;
  background:linear-gradient(180deg,transparent,var(--bg) 40%); }
.dock-inner { width:min(720px,92vw); margin:0 auto; display:flex; gap:8px;
  background:var(--panel); border:1px solid var(--border); border-radius:14px;
  padding:8px 8px 8px 14px; }
.dock input { flex:1; background:transparent; border:0; outline:0;
  color:var(--text); font-size:14px; }
.dock button { background:var(--user); color:#fff; border:0; padding:9px 16px;
  border-radius:10px; font-weight:600; cursor:pointer; }
```

- [ ] **Step 4: Create `task_builder/static/index.html`**

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Task Builder</title>
  <link rel="stylesheet" href="/static/styles.css" />
</head>
<body>
  <header>
    <div class="logo"></div>
    <h1>Task Builder</h1>
  </header>
  <main><div class="chat" id="chat"></div></main>
  <div class="dock">
    <div class="dock-inner">
      <input id="msg" placeholder="Type a message…" autocomplete="off" />
      <button id="send">Send</button>
    </div>
  </div>
  <script src="/static/app.js"></script>
</body>
</html>
```

- [ ] **Step 5: Serve the static files from `server.py`**

Add to `task_builder/server.py`, just after `app = FastAPI(title="Task Builder")`:

```python
_STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(_STATIC_DIR / "index.html")
```

Add `from pathlib import Path` to the imports at the top of `server.py`.

- [ ] **Step 6: Run the test, verify it passes**

Run: `.venv/bin/python -m pytest tests/test_task_builder_server.py -v`
Expected: PASS — all 6 tests green.

- [ ] **Step 7: Commit**

```bash
git add task_builder/static/index.html task_builder/static/styles.css task_builder/server.py tests/test_task_builder_server.py
git commit -m "feat: serve Task Builder static page"
```

---

## Task 12: Frontend chat logic — `app.js`

**Files:**
- Create: `task_builder/static/app.js`

- [ ] **Step 1: Create `task_builder/static/app.js`**

```javascript
// Task Builder chat client — talks to the FastAPI backend.
const chat = document.getElementById("chat");
const input = document.getElementById("msg");
const sendBtn = document.getElementById("send");
let sessionId = null;
let busy = false;

function bubble(role, text, cls) {
  const row = document.createElement("div");
  row.className = "row " + (role === "user" ? "user" : "bot");
  const avatar = `<div class="avatar ${role}">${role === "user" ? "Y" : "U"}</div>`;
  const body = `<div class="bubble ${cls || ""}">${text}</div>`;
  row.innerHTML = role === "user" ? body + avatar : avatar + body;
  chat.appendChild(row);
  row.scrollIntoView({ behavior: "smooth", block: "end" });
  return row.querySelector(".bubble");
}

function summaryCard(brief) {
  const card = bubble("bot", "", "summary");
  card.innerHTML = `<h4>Task brief</h4><div class="kv">
    <div class="k">Tech stack</div><div>${brief.competencies.join(", ")}</div>
    <div class="k">Proficiency</div><div>${brief.proficiency}</div>
    <div class="k">Role</div><div>${brief.role}</div>
    <div class="k">Focus areas</div><div>${brief.focus_areas.join(", ")}</div>
    <div class="k">Domain</div><div>${brief.domain}</div>
    <div class="k">Scenarios</div><div>${brief.scenario_count}</div>
  </div><button class="cta" id="gen">Generate task →</button>`;
  card.querySelector("#gen").onclick = startGeneration;
}

async function startSession() {
  const res = await fetch("/api/session", { method: "POST" });
  const data = await res.json();
  sessionId = data.session_id;
  bubble("bot", data.reply);
}

async function send() {
  const text = input.value.trim();
  if (!text || busy || !sessionId) return;
  busy = true;
  input.value = "";
  bubble("user", text);
  const thinking = bubble("bot", "…");
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message: text }),
    });
    const data = await res.json();
    thinking.textContent = data.reply;
    if (data.ready) summaryCard(data.brief);
  } catch (e) {
    thinking.textContent = "Network error — please try again.";
  } finally {
    busy = false;
  }
}

function startGeneration() {
  const gen = document.getElementById("gen");
  if (gen) gen.disabled = true;
  fetch("/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
  })
    .then((r) => r.json())
    .then((data) => streamRun(data.run_id))
    .catch(() => bubble("bot", "Could not start generation.", "stage failed"));
}

function streamRun(runId) {
  const es = new EventSource(`/api/runs/${runId}/events`);
  es.onmessage = (ev) => {
    const e = JSON.parse(ev.data);
    if (e.stage === "done") {
      const cls = e.status === "completed" ? "stage ok" : "stage failed";
      bubble("bot", e.outcome || e.detail || e.status, cls);
      es.close();
    } else if (e.status === "ok" || e.status === "failed") {
      const cls = e.status === "ok" ? "stage ok" : "stage failed";
      const mark = e.status === "ok" ? "✓" : "✗";
      bubble("bot", `${mark} ${e.stage} ${e.detail || ""}`.trim(), cls);
    } else {
      bubble("bot", `running ${e.stage}…`, "stage");
    }
  };
  es.onerror = () => es.close();
}

sendBtn.onclick = send;
input.addEventListener("keydown", (e) => { if (e.key === "Enter") send(); });
startSession();
```

- [ ] **Step 2: Manual smoke test**

Run the server: `.venv/bin/python -m task_builder`
Open `http://127.0.0.1:8000` in a browser. Verify:
- The bot greeting appears on load.
- Typing a reply produces a bot response (requires real `ANTHROPIC_API_KEY` /
  `PORTKEY_API_KEY` and Supabase env vars in `.env`).
- After all slots are filled, the summary card with a "Generate task →" button
  appears.
- Pressing it streams stage lines (`✓ 01_input_files`, …) into the chat.

Stop the server with Ctrl-C.

- [ ] **Step 3: Commit**

```bash
git add task_builder/static/app.js
git commit -m "feat: add Task Builder frontend chat client"
```

---

## Task 13: End-to-end integration test and documentation

**Files:**
- Create: `tests/test_task_builder_integration.py`
- Create: `task_builder/README.md`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Write the integration test**

Create `tests/test_task_builder_integration.py`:

```python
"""End-to-end: session → multi-turn chat → complete brief → generate (mocked LLM)."""
import json
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from task_builder.server import app, SESSIONS


def _bot(reply, slots, ready):
    choice = MagicMock()
    choice.message.content = json.dumps({
        "reply": reply, "slots_update": slots, "ready_to_generate": ready,
    })
    client = MagicMock()
    client.chat.completions.create.return_value = MagicMock(choices=[choice])
    return client


def _supabase_ok():
    sb = MagicMock()
    table = sb.table.return_value
    table.select.return_value.ilike.return_value.eq.return_value.execute.return_value = \
        MagicMock(data=[{"name": "Java"}])
    return sb


def test_full_conversation_to_ready_then_generate():
    client = TestClient(app)
    with patch("task_builder.server.get_supabase", return_value=_supabase_ok()), \
         patch("task_builder.server._launch_run") as launch:
        sid = client.post("/api/session").json()["session_id"]

        # Turn 1: collect proficiency + competencies.
        with patch("task_builder.server.build_bot_client",
                   return_value=_bot("ok", {"proficiency": "BASIC",
                                            "competencies": ["Java"]}, False)):
            client.post("/api/chat", json={"session_id": sid, "message": "java basic"})

        # Turn 2: fill the rest and mark ready.
        with patch("task_builder.server.build_bot_client",
                   return_value=_bot("Ready!", {"role": "Backend Engineer",
                                                "focus_areas": ["idempotency"],
                                                "domain": "fintech"}, True)):
            final = client.post("/api/chat", json={
                "session_id": sid, "message": "backend, idempotency, fintech",
            }).json()

        assert final["ready"] is True
        assert SESSIONS[sid].brief.is_complete()

        run = client.post("/api/generate", json={"session_id": sid})
        assert run.status_code == 200
        launch.assert_called_once()
```

- [ ] **Step 2: Run the integration test, verify it passes**

Run: `.venv/bin/python -m pytest tests/test_task_builder_integration.py -v`
Expected: PASS.

- [ ] **Step 3: Run the FULL suite**

Run: `.venv/bin/python -m pytest -q`
Expected: every test passes, including the pre-existing suite.

- [ ] **Step 4: Create `task_builder/README.md`**

```markdown
# Task Builder

A local conversational web app that interviews you for the task-generation
pipeline's inputs and runs the pipeline with live progress.

## Run it

    .venv/bin/python -m task_builder

Open http://127.0.0.1:8000

## Requires (in .env)

`ANTHROPIC_API_KEY`, `PORTKEY_API_KEY` (the conversational bot),
`SUPABASE_URL_APTITUDETESTSDEV` + `SUPABASE_API_KEY_APTITUDETESTSDEV`
(competency validation), plus everything the pipeline stages need.

## How it works

The bot fills six slots — competencies, proficiency, role, focus areas, domain,
scenario count — validates them (competencies against Supabase), then runs
`generate_input_files → scenario_generator → prompt_generator → multiagent
generate_tasks`, streaming per-stage progress over Server-Sent Events.

See `docs/superpowers/specs/2026-05-18-task-builder-conversational-frontend-design.md`.
```

- [ ] **Step 5: Add a Task Builder entry to `CLAUDE.md`**

In `CLAUDE.md`, under "### Sub-packages", add a table row:

```
| `task_builder/` | Conversational web front-end (FastAPI) that interviews for pipeline inputs and runs the pipeline with live progress |
```

- [ ] **Step 6: Commit**

```bash
git add tests/test_task_builder_integration.py task_builder/README.md CLAUDE.md
git commit -m "test: add task_builder integration test; docs: document task_builder"
```

**Phase 3 complete.** The Task Builder web app is functional end to end.

---

# Self-review checklist (completed by plan author)

**Spec coverage:**
- §5 architecture / package layout → Tasks 4, 6, 8, 9, 11.
- §6 `TaskBrief` / `SessionState` → Task 4.
- §7 data flow + server-owns-state → Tasks 7, 8, 10.
- §8 conversation engine (Approach B) → Tasks 6, 7.
- §9 runner + streaming → Tasks 9, 10 (run_pipeline helpers imported, not refactored
  — a documented refinement).
- §10 Layer B → Tasks 1, 2, 3.
- §11 HTTP API (all 6 routes) → Tasks 8, 10, 11.
- §12 frontend → Tasks 11, 12.
- §13 error handling → Task 6 (bad JSON), Task 7 (validation/corrective), Task 9
  (stage failure), Task 9 preflight stage.
- §14 testing → every task is TDD; integration test in Task 13.
- §15 dependencies → Task 4.
- §16 file-by-file list → all files covered.

**Placeholder scan:** no TBD/TODO; every code step contains complete code.

**Type consistency:** `TaskBrief`, `SessionState`, `Message`, `merge_brief`,
`SlotValidation`, `validate_proficiency`/`validate_competency`, `ConversationTurn`,
`run_turn`, `ChatResult`, `apply_turn`, `StageEvent`, `run_pipeline_for_brief`,
`build_bot_client`, `get_supabase`, `_launch_run` — names are used identically
across every task that references them.
