# Design Review Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a new `design_review_flow/` sub-package that generates UI/UX design review assessment tasks — LLM creates flaw injection specs and candidate briefs for curated Figma Community files, with a Figma plugin to apply flaws automatically.

**Architecture:** Two CLI commands (`generate` and `store`) separated by a manual Figma step. LLM generates flaw specs referencing exact layer names from pre-exported Figma layer trees. Eval gate validates specs before output. Supabase storage follows the `pr_review_flow` pattern exactly.

**Tech Stack:** Python 3.10+, Click CLI, OpenAI via Portkey, Supabase, TypeScript (Figma Plugin API)

**Spec:** `docs/superpowers/specs/2026-03-30-design-review-flow-design.md`

---

## File Structure

```
design_review_flow/
├── __init__.py                      # Package exports (create_design_review_task, store_design_review_task)
├── __main__.py                      # Click CLI: generate + store commands
├── design_review_multiagent.py      # Main orchestrator (LLM calls, eval gate, local save)
├── prompts.py                       # System + generation + eval prompts
├── schemas.py                       # JSON schemas for structured LLM output
├── design_review_evals.py           # Eval gate: validate flaw spec, brief, rubric
├── design_review_utils.py           # Helpers: cost tracking, local save, validation
├── figma_library.json               # Curated community file registry (starts empty)
├── layer_trees/                     # Figma layer tree exports (starts empty)
│   └── .gitkeep
└── figma_plugin/
    ├── manifest.json                # Figma plugin manifest
    ├── code.ts                      # Plugin logic: parse spec, match layers, apply flaws
    ├── ui.html                      # Plugin UI: paste JSON, preview, confirm
    ├── package.json                 # Dependencies (TypeScript only)
    └── tsconfig.json                # TypeScript config
```

**Local output directory:** `infra_assets/design_tasks/{timestamp}_{library_id}/`

---

### Task 1: Package Scaffolding + CLI

**Files:**
- Create: `design_review_flow/__init__.py`
- Create: `design_review_flow/__main__.py`

- [ ] **Step 1: Create `__init__.py`**

```python
"""
Design Review Task Generation package.

Generates UI/UX assessment tasks where candidates review Figma designs with intentional flaws.

Usage as CLI:
    python -m design_review_flow generate --competency-file <path> --library-entry-id <id>
    python -m design_review_flow store --spec-file <path> --figma-link <url>
"""

from design_review_flow.design_review_multiagent import (
    create_design_review_task,
    store_design_review_task,
)

__all__ = ["create_design_review_task", "store_design_review_task"]
```

- [ ] **Step 2: Create `__main__.py`**

Follow the exact pattern from `pr_review_flow/__main__.py`:

```python
"""CLI entry point for Design Review task generation.

Usage:
    python -m design_review_flow generate \
        --competency-file path/to/competency.json \
        --proficiency INTERMEDIATE \
        --scenario "SaaS onboarding redesign" \
        --library-entry-id lib-001 \
        --env dev

    python -m design_review_flow store \
        --spec-file path/to/design_task_spec.json \
        --figma-link "https://figma.com/file/...?duplicate" \
        --env dev
"""

import sys
import io
from pathlib import Path

import click

# Fix Unicode output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from design_review_flow.design_review_multiagent import (
    create_design_review_task,
    store_design_review_task,
)


@click.group()
def cli():
    """Design Review Task Generator."""
    pass


@cli.command()
@click.option(
    "--competency-file", "-c",
    type=click.Path(exists=True), required=True,
    help="Path to competency JSON file",
)
@click.option(
    "--proficiency", "-p",
    type=click.Choice(["BEGINNER", "BASIC", "INTERMEDIATE", "ADVANCED"]),
    required=True,
    help="Proficiency level for flaw scaling",
)
@click.option(
    "--scenario", "-s",
    type=str, required=True,
    help="Design scenario description (e.g., 'SaaS onboarding redesign')",
)
@click.option(
    "--library-entry-id", "-l",
    type=str, required=True,
    help="ID of the Figma library entry to use (from figma_library.json)",
)
@click.option(
    "--env", default="dev",
    type=click.Choice(["dev", "prod"]),
    help="Supabase environment (default: dev)",
)
@click.option(
    "--dry-run", is_flag=True, default=False,
    help="Generate and eval but don't save to disk",
)
def generate(competency_file, proficiency, scenario, library_entry_id, env, dry_run):
    """Generate a design review flaw spec + brief + rubric."""
    click.echo(f"\n{'='*70}")
    click.echo("  DESIGN REVIEW TASK GENERATOR")
    click.echo(f"{'='*70}")
    click.echo(f"  Competency file:  {competency_file}")
    click.echo(f"  Proficiency:      {proficiency}")
    click.echo(f"  Scenario:         {scenario}")
    click.echo(f"  Library entry:    {library_entry_id}")
    click.echo(f"  Environment:      {env}")
    if dry_run:
        click.echo("  Mode:             DRY RUN")
    click.echo()

    result = create_design_review_task(
        competency_file=Path(competency_file),
        proficiency=proficiency,
        scenario=scenario,
        library_entry_id=library_entry_id,
        env=env,
        dry_run=dry_run,
    )

    if not result:
        click.echo("\nTask generation failed. Check logs for details.", err=True)
        raise SystemExit(1)

    click.echo(f"\nSpec saved to: {result.get('local_dir', 'N/A')}")


@cli.command()
@click.option(
    "--spec-file", "-f",
    type=click.Path(exists=True), required=True,
    help="Path to generated design task spec JSON",
)
@click.option(
    "--figma-link", "-u",
    type=str, required=True,
    help="Figma duplicate link (URL) for the flawed design",
)
@click.option(
    "--env", default="dev",
    type=click.Choice(["dev", "prod"]),
    help="Supabase environment (default: dev)",
)
def store(spec_file, figma_link, env):
    """Store a design review task in Supabase (after Figma plugin step)."""
    click.echo(f"\n{'='*70}")
    click.echo("  DESIGN REVIEW TASK STORE")
    click.echo(f"{'='*70}")
    click.echo(f"  Spec file:    {spec_file}")
    click.echo(f"  Figma link:   {figma_link}")
    click.echo(f"  Environment:  {env}")
    click.echo()

    result = store_design_review_task(
        spec_file=Path(spec_file),
        figma_link=figma_link,
        env=env,
    )

    if not result:
        click.echo("\nStore failed. Check logs for details.", err=True)
        raise SystemExit(1)

    click.echo(f"\nTask stored! task_id: {result.get('task_id', 'N/A')}")


if __name__ == "__main__":
    cli()
```

- [ ] **Step 3: Verify CLI loads without import errors**

Run: `python -c "from design_review_flow import __init__"` — this will fail because `design_review_multiagent.py` doesn't exist yet. That's expected. We just verify the file is syntactically valid.

Run: `python -c "import ast; ast.parse(open('design_review_flow/__main__.py').read()); print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add design_review_flow/__init__.py design_review_flow/__main__.py
git commit --no-gpg-sign -m "feat(design-review): scaffold package with CLI entry point"
```

---

### Task 2: JSON Schemas

**Files:**
- Create: `design_review_flow/schemas.py`

- [ ] **Step 1: Create schemas**

Three schemas needed: flaw spec generation, candidate brief generation, eval response (reuse from `schemas.py`).

```python
"""JSON schemas for Design Review structured LLM output."""

FLAW_SPEC_SCHEMA = {
    "name": "flaw_spec_response",
    "schema": {
        "type": "object",
        "properties": {
            "source_file": {
                "type": "string",
                "description": "Library entry ID"
            },
            "target_screens": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Screens where flaws are injected"
            },
            "flaws": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "screen": {"type": "string"},
                        "type": {
                            "type": "string",
                            "enum": [
                                "visual_hierarchy",
                                "accessibility",
                                "information_architecture",
                                "copy_microcopy",
                                "consistency",
                                "user_flow"
                            ]
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["critical", "major", "minor"]
                        },
                        "instruction": {
                            "type": "string",
                            "description": "Exact change to apply in Figma"
                        },
                        "target_layer": {
                            "type": "string",
                            "description": "Exact Figma layer name from layer tree"
                        },
                        "rationale": {
                            "type": "string",
                            "description": "UX principle this flaw violates"
                        }
                    },
                    "required": ["id", "screen", "type", "severity", "instruction", "target_layer", "rationale"],
                    "additionalProperties": False
                }
            },
            "answer_key": {
                "type": "object",
                "properties": {
                    "flaws_summary": {"type": "string"},
                    "expected_findings": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "overall_quality": {"type": "string"}
                },
                "required": ["flaws_summary", "expected_findings", "overall_quality"],
                "additionalProperties": False
            }
        },
        "required": ["source_file", "target_screens", "flaws", "answer_key"],
        "additionalProperties": False
    },
    "strict": False
}


CANDIDATE_BRIEF_SCHEMA = {
    "name": "candidate_brief_response",
    "schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "domain_context": {"type": "string"},
            "constraints": {
                "type": "array",
                "items": {"type": "string"}
            },
            "change_requests": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["critique", "redesign"]
                        },
                        "prompt": {"type": "string"}
                    },
                    "required": ["type", "prompt"],
                    "additionalProperties": False
                }
            },
            "submission_requirements": {
                "type": "object",
                "properties": {
                    "figma_link": {"type": "string"},
                    "written_rationale": {"type": "string"}
                },
                "required": ["figma_link", "written_rationale"],
                "additionalProperties": False
            },
            "time_limit_minutes": {"type": "integer"}
        },
        "required": ["title", "domain_context", "constraints", "change_requests", "submission_requirements", "time_limit_minutes"],
        "additionalProperties": False
    },
    "strict": False
}


EVALUATION_RUBRIC_SCHEMA = {
    "name": "evaluation_rubric_response",
    "schema": {
        "type": "object",
        "properties": {
            "criteria": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "weight": {"type": "integer"},
                        "scoring": {
                            "type": "object",
                            "properties": {
                                "excellent": {"type": "string"},
                                "good": {"type": "string"},
                                "acceptable": {"type": "string"},
                                "poor": {"type": "string"}
                            },
                            "required": ["excellent", "good", "acceptable", "poor"],
                            "additionalProperties": False
                        }
                    },
                    "required": ["name", "weight", "scoring"],
                    "additionalProperties": False
                }
            },
            "bonus_points": {"type": "string"}
        },
        "required": ["criteria", "bonus_points"],
        "additionalProperties": False
    },
    "strict": False
}
```

- [ ] **Step 2: Verify syntax**

Run: `python -c "from design_review_flow.schemas import FLAW_SPEC_SCHEMA, CANDIDATE_BRIEF_SCHEMA, EVALUATION_RUBRIC_SCHEMA; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add design_review_flow/schemas.py
git commit --no-gpg-sign -m "feat(design-review): add JSON schemas for LLM structured output"
```

---

### Task 3: Prompts

**Files:**
- Create: `design_review_flow/prompts.py`

- [ ] **Step 1: Create prompts file**

Follow the prompt patterns from `pr_review_flow/prompts/`. All prompts in a single file since this flow is simpler.

```python
"""Prompts for Design Review task generation."""

# ─── Flaw Spec Generation ───

FLAW_SPEC_SYSTEM_PROMPT = """\
You are a senior UX designer and design systems expert with 15+ years of experience \
evaluating and critiquing user interfaces. You specialize in identifying UX issues \
across accessibility, visual hierarchy, information architecture, and user flows.

Your task is to generate a flaw injection specification for a UI/UX design assessment. \
You will be given a Figma design's layer tree and metadata, and you must specify \
realistic UX flaws to inject into the design. These flaws should be things a real \
designer might accidentally introduce — not obviously planted errors.

CRITICAL RULES:
- Every target_layer you reference MUST exist in the provided layer tree
- Flaws must be specific and actionable (not vague like "make it worse")
- Instructions must be executable by a Figma plugin (text changes, color changes, \
  size changes, spacing changes, reordering)
- Rationale must cite a specific UX principle or guideline (WCAG, Nielsen heuristics, \
  Gestalt principles, etc.)
"""

FLAW_SPEC_GENERATION_PROMPT = """\
DESIGN FILE METADATA:
- Library ID: {library_id}
- Name: {library_name}
- Domain: {domain}
- Screens: {screens}

KEY ELEMENTS (layer names):
{frames_text}

FULL LAYER TREE:
{layer_tree_text}

COMPETENCIES BEING ASSESSED:
{competencies_text}

PROFICIENCY LEVEL: {proficiency}

SCENARIO: {scenario}

FLAW COUNT GUIDELINES:
- BEGINNER: 2-3 obvious flaws on a single screen
- BASIC: 3-4 flaws, mix of obvious and subtle
- INTERMEDIATE: 4-6 flaws across multiple screens, mostly subtle
- ADVANCED: 6-8 subtle flaws, some requiring flow-level thinking

Generate a flaw injection specification. Each flaw must:
1. Reference an EXACT layer name from the layer tree above
2. Have a clear, specific instruction that a Figma plugin can execute
3. Include a rationale explaining which UX principle is violated

{eval_feedback_block}\
"""

EVAL_FEEDBACK_BLOCK = """\

PREVIOUS ATTEMPT FEEDBACK — address these issues:
{feedback}
"""

EVAL_FEEDBACK_BLOCK_EMPTY = ""


# ─── Candidate Brief Generation ───

BRIEF_SYSTEM_PROMPT = """\
You are a hiring manager creating a UI/UX design assessment task. \
Generate a clear, professional brief for a design review candidate.

CRITICAL RULES:
- Do NOT mention or hint at specific flaws in the design
- The brief should frame the task as a general design review + improvement exercise
- Change requests should be broad enough that discovering specific issues is part of the test
- Include a mix of "critique" (find issues) and "redesign" (improve) requests
- Time limit should be realistic for the proficiency level
"""

BRIEF_GENERATION_PROMPT = """\
DESIGN FILE INFO:
- Name: {library_name}
- Domain: {domain}
- Screens: {screens}

FLAW TYPES INJECTED (DO NOT reveal these to the candidate):
{flaw_types_summary}

PROFICIENCY LEVEL: {proficiency}

SCENARIO: {scenario}

PROFICIENCY GUIDELINES for change request mix:
- BEGINNER: mostly "critique" (find the issues), time limit 30 min
- BASIC: critique + small fixes, time limit 35 min
- INTERMEDIATE: critique + redesign of specific components, time limit 45 min
- ADVANCED: full flow reimagination + rationale, time limit 60 min

Generate a candidate brief. The change_requests should naturally lead candidates \
toward discovering the injected flaws WITHOUT revealing them.

{eval_feedback_block}\
"""


# ─── Evaluation Rubric Generation ───

RUBRIC_SYSTEM_PROMPT = """\
You are an assessment design expert. Generate a scoring rubric for evaluating \
a UI/UX design review submission. The rubric should have clear, measurable criteria.
"""

RUBRIC_GENERATION_PROMPT = """\
FLAW SPEC SUMMARY:
{flaw_spec_summary}

CANDIDATE BRIEF:
{brief_summary}

PROFICIENCY LEVEL: {proficiency}

Generate an evaluation rubric with 4 criteria:
1. Flaw Identification (weight: 30) — how many injected flaws the candidate found
2. Design Changes Quality (weight: 30) — quality of modifications made
3. Written Rationale (weight: 25) — reasoning grounded in UX principles
4. Design Consistency (weight: 15) — maintaining visual consistency

Tailor the scoring descriptions to the specific flaws and brief above.
Include a bonus_points field for candidates who find issues beyond the injected flaws.
"""


# ─── Eval Gate Prompts ───

FLAW_SPEC_EVAL_PROMPT = """\
LAYER TREE (available layers in the Figma file):
{layer_tree_text}

GENERATED FLAW SPEC:
{flaw_spec_text}

PROFICIENCY LEVEL: {proficiency}

Evaluate this flaw injection spec STRICTLY against these criteria:

1. LAYER VALIDITY: Every target_layer in the spec MUST exist in the layer tree above. \
   Check each one. If ANY target_layer is not found in the tree, FAIL.

2. FLAW COUNT: Must match proficiency guidelines:
   - BEGINNER: 2-3 flaws
   - BASIC: 3-4 flaws
   - INTERMEDIATE: 4-6 flaws
   - ADVANCED: 6-8 flaws

3. ACTIONABILITY: Each instruction must be specific enough for a Figma plugin to execute \
   (text changes, color changes, size changes, spacing changes). Vague instructions like \
   "make it worse" or "reduce quality" → FAIL.

4. DISTINCTNESS: No two flaws should target the same layer. Each flaw must be unique.

5. RATIONALE: Each rationale must cite a real UX principle (WCAG, Nielsen heuristics, \
   Gestalt principles, etc.), not generic statements.

PASS: {{"pass": true, "issues": [], "validated_criteria": [...], "feedback": ""}}
FAIL: {{"pass": false, "issues": ["specific issue"], "validated_criteria": [...], "feedback": "detailed fix instructions"}}
"""

BRIEF_EVAL_PROMPT = """\
FLAW TYPES INJECTED:
{flaw_types_text}

GENERATED CANDIDATE BRIEF:
{brief_text}

Evaluate this candidate brief STRICTLY against these criteria:

1. NO ANSWER LEAKING: The brief must NOT mention specific flaws, specific layer names, \
   or specific changes that were injected. It should frame the task generally.

2. COHERENCE: domain_context must make sense for the design file's domain.

3. CONSTRAINTS: Must be specific and testable (not vague like "good design").

4. CHANGE REQUEST MIX: Must include both "critique" and "redesign" types \
   (unless BEGINNER level, which can be critique-only).

5. TIME LIMIT: Must be reasonable for the proficiency level (30-60 min range).

PASS: {{"pass": true, "issues": [], "validated_criteria": [...], "feedback": ""}}
FAIL: {{"pass": false, "issues": ["specific issue"], "validated_criteria": [...], "feedback": "detailed fix instructions"}}
"""
```

- [ ] **Step 2: Verify syntax**

Run: `python -c "from design_review_flow.prompts import FLAW_SPEC_SYSTEM_PROMPT, BRIEF_SYSTEM_PROMPT; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add design_review_flow/prompts.py
git commit --no-gpg-sign -m "feat(design-review): add LLM prompts for flaw spec, brief, and rubric generation"
```

---

### Task 4: Utilities

**Files:**
- Create: `design_review_flow/design_review_utils.py`

- [ ] **Step 1: Create utils file**

Mirror `pr_review_flow/pr_review_utils.py` patterns:

```python
"""Design Review utilities: library management, cost tracking, local save, validation."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from logger_config import logger


# ─── Library Management ───

def load_figma_library() -> List[Dict]:
    """Load the Figma community file library."""
    library_path = Path(__file__).parent / "figma_library.json"
    if not library_path.exists():
        logger.warning(f"Figma library not found at {library_path}")
        return []
    return json.loads(library_path.read_text(encoding="utf-8"))


def get_library_entry(library_entry_id: str) -> Optional[Dict]:
    """Get a specific library entry by ID."""
    library = load_figma_library()
    for entry in library:
        if entry.get("id") == library_entry_id:
            return entry
    return None


def load_layer_tree(library_entry_id: str) -> Optional[Dict]:
    """Load the Figma layer tree for a library entry."""
    layer_tree_path = Path(__file__).parent / "layer_trees" / f"{library_entry_id}.json"
    if not layer_tree_path.exists():
        logger.warning(f"Layer tree not found at {layer_tree_path}")
        return None
    return json.loads(layer_tree_path.read_text(encoding="utf-8"))


def extract_layer_names(layer_tree: Dict, prefix: str = "") -> List[str]:
    """Recursively extract all layer names from a Figma layer tree.

    Figma REST API returns a tree with 'name' and 'children' fields.
    Returns flat list of full layer paths like 'Frame / Subframe / Button'.
    """
    names = []
    name = layer_tree.get("name", "")
    full_name = f"{prefix} / {name}".strip(" / ") if prefix else name

    if name:
        names.append(full_name)

    for child in layer_tree.get("children", []):
        names.extend(extract_layer_names(child, full_name))

    return names


def format_frames_for_prompt(frames: Dict) -> str:
    """Format the frames/key_elements from a library entry for prompt injection."""
    parts = []
    for screen_name, screen_data in frames.items():
        frame_name = screen_data.get("frame_name", screen_name)
        parts.append(f"Screen: {screen_name} (frame: {frame_name})")
        for element_name, layer_name in screen_data.get("key_elements", {}).items():
            parts.append(f"  - {element_name}: {layer_name}")
    return "\n".join(parts)


# ─── Validation ───

def validate_flaw_layers(flaws: List[Dict], layer_names: List[str]) -> List[str]:
    """Check that all flaw target_layers exist in the layer tree. Returns list of invalid layers."""
    invalid = []
    for flaw in flaws:
        target = flaw.get("target_layer", "")
        if target and target not in layer_names:
            invalid.append(f"Flaw {flaw.get('id', '?')}: layer '{target}' not found")
    return invalid


def validate_figma_link(link: str) -> bool:
    """Basic validation that the link is a Figma URL."""
    return link.startswith("https://figma.com/") or link.startswith("https://www.figma.com/")


def validate_spec_file(spec_data: Dict) -> List[str]:
    """Validate a generated spec file has all required fields."""
    errors = []
    required = ["flaw_spec", "candidate_brief", "evaluation_rubric", "library_entry"]
    for field in required:
        if field not in spec_data:
            errors.append(f"Missing required field: {field}")
    return errors


# ─── Token Usage & Cost ───

def extract_usage(response) -> Dict:
    """Extract token usage from an OpenAI Responses API response."""
    usage = getattr(response, "usage", None)
    if usage:
        return {
            "input_tokens": getattr(usage, "input_tokens", 0),
            "output_tokens": getattr(usage, "output_tokens", 0),
        }
    return {"input_tokens": 0, "output_tokens": 0}


PRICING = {
    "gpt-5-nano-2025-08-07": {"input": 0.50, "output": 2.00},
    "gpt-5.1-2025-11-13": {"input": 2.00, "output": 8.00},
}


def calculate_cost(total_usage: Dict, model: str) -> float:
    """Calculate cost in USD from token usage."""
    prices = PRICING.get(model, {"input": 1.25, "output": 10.00})
    input_cost = (total_usage["input_tokens"] / 1_000_000) * prices["input"]
    output_cost = (total_usage["output_tokens"] / 1_000_000) * prices["output"]
    return input_cost + output_cost


def format_cost_summary(usage_by_model: Dict) -> str:
    """Format a cost summary string."""
    lines = ["Cost Breakdown:"]
    grand_total_cost = 0.0
    for model, usage in usage_by_model.items():
        cost = calculate_cost(usage, model)
        grand_total_cost += cost
        lines.append(f"  {model}: {usage['input_tokens']:,} in + {usage['output_tokens']:,} out = ${cost:.6f}")
    lines.append(f"  Total: ${grand_total_cost:.6f}")
    return "\n".join(lines)


# ─── Local Save ───

def save_design_task_locally(
    library_id: str,
    flaw_spec: Dict,
    candidate_brief: Dict,
    evaluation_rubric: Dict,
    library_entry: Dict,
    eval_info: Dict,
    competencies: List[Dict],
) -> Path:
    """Save generated design task spec locally for inspection.

    Returns path to the saved directory.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = Path(__file__).parent.parent / "infra_assets" / "design_tasks" / f"{timestamp}_{library_id}"
    base_dir.mkdir(parents=True, exist_ok=True)

    spec_data = {
        "flaw_spec": flaw_spec,
        "candidate_brief": candidate_brief,
        "evaluation_rubric": evaluation_rubric,
        "library_entry": library_entry,
        "eval_info": eval_info,
        "competencies": competencies,
        "generated_at": datetime.now().isoformat(),
    }

    spec_path = base_dir / "design_task_spec.json"
    spec_path.write_text(
        json.dumps(spec_data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # Also save candidate brief separately for easy sharing
    brief_path = base_dir / "candidate_brief.json"
    brief_path.write_text(
        json.dumps(candidate_brief, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # Save flaw spec separately for the Figma plugin
    plugin_spec_path = base_dir / "flaw_spec_for_plugin.json"
    plugin_spec_path.write_text(
        json.dumps(flaw_spec, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    logger.info(f"Saved design review task locally: {base_dir}")
    return base_dir
```

- [ ] **Step 2: Verify syntax**

Run: `python -c "from design_review_flow.design_review_utils import load_figma_library, extract_usage; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add design_review_flow/design_review_utils.py
git commit --no-gpg-sign -m "feat(design-review): add utility functions for library, validation, cost tracking"
```

---

### Task 5: Eval Gate

**Files:**
- Create: `design_review_flow/design_review_evals.py`

- [ ] **Step 1: Create evals file**

Follow `pr_review_flow/pr_review_evals.py` pattern exactly:

```python
"""Evaluation gates for Design Review task generation."""

import json
from logger_config import logger
from schemas import EVAL_RESPONSE_SCHEMA
from design_review_flow.prompts import FLAW_SPEC_EVAL_PROMPT, BRIEF_EVAL_PROMPT
from design_review_flow.design_review_utils import extract_usage

EVAL_MODEL = "gpt-5-nano-2025-08-07"


def eval_flaw_spec(flaw_spec: dict, layer_tree_text: str, proficiency: str, openai_client) -> tuple:
    """Evaluate flaw injection spec quality. Returns (eval_result_dict, usage_dict)."""
    flaw_spec_text = json.dumps(flaw_spec, indent=2)

    prompt = FLAW_SPEC_EVAL_PROMPT.format(
        layer_tree_text=layer_tree_text,
        flaw_spec_text=flaw_spec_text,
        proficiency=proficiency,
    )
    messages = [{"role": "user", "content": prompt}]

    try:
        response = openai_client.responses.create(
            model=EVAL_MODEL,
            input=messages,
            reasoning={"effort": "medium"},
            text={
                "format": {
                    "type": "json_schema",
                    "name": EVAL_RESPONSE_SCHEMA["name"],
                    "schema": EVAL_RESPONSE_SCHEMA["schema"],
                    "strict": EVAL_RESPONSE_SCHEMA["strict"],
                }
            },
        )
        usage = extract_usage(response)
        raw = getattr(response, "output_text", None)
        if not raw:
            return {"pass": False, "issues": ["No response from eval API"], "validated_criteria": [], "feedback": ""}, usage
        return json.loads(raw), usage
    except Exception as e:
        logger.error(f"Flaw spec eval error: {e}")
        return {"pass": False, "issues": [str(e)], "validated_criteria": [], "feedback": ""}, {"input_tokens": 0, "output_tokens": 0}


def eval_candidate_brief(brief: dict, flaw_types: list, openai_client) -> tuple:
    """Evaluate candidate brief for answer leaking and coherence. Returns (eval_result_dict, usage_dict)."""
    brief_text = json.dumps(brief, indent=2)
    flaw_types_text = "\n".join(f"- {ft}" for ft in flaw_types)

    prompt = BRIEF_EVAL_PROMPT.format(
        flaw_types_text=flaw_types_text,
        brief_text=brief_text,
    )
    messages = [{"role": "user", "content": prompt}]

    try:
        response = openai_client.responses.create(
            model=EVAL_MODEL,
            input=messages,
            reasoning={"effort": "medium"},
            text={
                "format": {
                    "type": "json_schema",
                    "name": EVAL_RESPONSE_SCHEMA["name"],
                    "schema": EVAL_RESPONSE_SCHEMA["schema"],
                    "strict": EVAL_RESPONSE_SCHEMA["strict"],
                }
            },
        )
        usage = extract_usage(response)
        raw = getattr(response, "output_text", None)
        if not raw:
            return {"pass": False, "issues": ["No response from eval API"], "validated_criteria": [], "feedback": ""}, usage
        return json.loads(raw), usage
    except Exception as e:
        logger.error(f"Brief eval error: {e}")
        return {"pass": False, "issues": [str(e)], "validated_criteria": [], "feedback": ""}, {"input_tokens": 0, "output_tokens": 0}
```

- [ ] **Step 2: Verify syntax**

Run: `python -c "from design_review_flow.design_review_evals import eval_flaw_spec, eval_candidate_brief; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add design_review_flow/design_review_evals.py
git commit --no-gpg-sign -m "feat(design-review): add LLM eval gates for flaw spec and brief"
```

---

### Task 6: Main Orchestrator

**Files:**
- Create: `design_review_flow/design_review_multiagent.py`

- [ ] **Step 1: Create orchestrator**

This is the core file. Follow `pr_review_flow/pr_review_multiagent.py` structure exactly.

```python
"""Main orchestrator for Design Review task generation."""

import os
import json
import traceback
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional

import openai
from dotenv import load_dotenv
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders
from supabase import Client, create_client

from logger_config import logger
from design_review_flow.schemas import (
    FLAW_SPEC_SCHEMA,
    CANDIDATE_BRIEF_SCHEMA,
    EVALUATION_RUBRIC_SCHEMA,
)
from design_review_flow.prompts import (
    FLAW_SPEC_SYSTEM_PROMPT,
    FLAW_SPEC_GENERATION_PROMPT,
    BRIEF_SYSTEM_PROMPT,
    BRIEF_GENERATION_PROMPT,
    RUBRIC_SYSTEM_PROMPT,
    RUBRIC_GENERATION_PROMPT,
    EVAL_FEEDBACK_BLOCK,
    EVAL_FEEDBACK_BLOCK_EMPTY,
)
from design_review_flow.design_review_evals import eval_flaw_spec, eval_candidate_brief
from design_review_flow.design_review_utils import (
    get_library_entry,
    load_layer_tree,
    extract_layer_names,
    format_frames_for_prompt,
    validate_flaw_layers,
    validate_spec_file,
    validate_figma_link,
    extract_usage,
    format_cost_summary,
    save_design_task_locally,
)
from utils import read_json_file_robust

load_dotenv()

GENERATION_MODEL = "gpt-5.1-2025-11-13"
EVAL_MODEL = "gpt-5-nano-2025-08-07"
MAX_RETRIES = 2


def init_supabase(env: str = "dev") -> Client:
    """Initialize Supabase client for the given environment."""
    if env == "prod":
        url = os.getenv("SUPABASE_URL_APTITUDETESTS")
        key = os.getenv("SUPABASE_API_KEY_APTITUDETESTS")
    else:
        url = os.getenv("SUPABASE_URL_APTITUDETESTSDEV")
        key = os.getenv("SUPABASE_API_KEY_APTITUDETESTSDEV")

    if not url or not key:
        raise ValueError(f"Missing Supabase credentials for env '{env}'")
    return create_client(url, key)


def init_openai_client() -> openai.OpenAI:
    """Initialize OpenAI client via Portkey gateway."""
    api_key = os.getenv("OPENAI_API_KEY")
    portkey_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    if not portkey_key:
        raise RuntimeError("PORTKEY_API_KEY not set")
    return openai.OpenAI(
        api_key=api_key,
        base_url=PORTKEY_GATEWAY_URL,
        default_headers=createHeaders(
            provider="openai",
            api_key=portkey_key,
        ),
    )


def _track_usage(usage_by_model: dict, model: str, usage: dict):
    """Accumulate token usage by model."""
    if model not in usage_by_model:
        usage_by_model[model] = {"input_tokens": 0, "output_tokens": 0}
    usage_by_model[model]["input_tokens"] += usage.get("input_tokens", 0)
    usage_by_model[model]["output_tokens"] += usage.get("output_tokens", 0)


# ─── Phase 1: Generate Flaw Spec ───

def generate_flaw_spec(
    openai_client,
    library_entry: Dict,
    layer_tree: Dict,
    competencies: List[Dict],
    proficiency: str,
    scenario: str,
    usage_by_model: Dict,
    eval_feedback: str = "",
) -> Optional[Dict]:
    """Generate flaw injection spec via LLM."""
    # Format inputs
    layer_names = extract_layer_names(layer_tree)
    layer_tree_text = "\n".join(layer_names)
    frames_text = format_frames_for_prompt(library_entry.get("frames", {}))
    competencies_text = "\n".join(
        f"- {c.get('name', '')} ({c.get('proficiency', '')}): {c.get('scope', '')}"
        for c in competencies
    )
    feedback_block = EVAL_FEEDBACK_BLOCK.format(feedback=eval_feedback) if eval_feedback else EVAL_FEEDBACK_BLOCK_EMPTY

    prompt = FLAW_SPEC_GENERATION_PROMPT.format(
        library_id=library_entry["id"],
        library_name=library_entry["name"],
        domain=library_entry["domain"],
        screens=", ".join(library_entry.get("screens", [])),
        frames_text=frames_text,
        layer_tree_text=layer_tree_text,
        competencies_text=competencies_text,
        proficiency=proficiency,
        scenario=scenario,
        eval_feedback_block=feedback_block,
    )

    messages = [
        {"role": "system", "content": FLAW_SPEC_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    try:
        response = openai_client.responses.create(
            model=GENERATION_MODEL,
            input=messages,
            reasoning={"effort": "medium"},
            text={
                "format": {
                    "type": "json_schema",
                    "name": FLAW_SPEC_SCHEMA["name"],
                    "schema": FLAW_SPEC_SCHEMA["schema"],
                    "strict": FLAW_SPEC_SCHEMA["strict"],
                }
            },
        )
        usage = extract_usage(response)
        _track_usage(usage_by_model, GENERATION_MODEL, usage)

        raw = getattr(response, "output_text", None)
        if not raw:
            logger.error("No output from flaw spec generation")
            return None
        return json.loads(raw)
    except Exception as e:
        logger.error(f"Flaw spec generation error: {e}\n{traceback.format_exc()}")
        return None


def run_flaw_spec_generation(
    openai_client,
    library_entry: Dict,
    layer_tree: Dict,
    competencies: List[Dict],
    proficiency: str,
    scenario: str,
    usage_by_model: Dict,
) -> Optional[Dict]:
    """Generate flaw spec with eval gate and retry loop."""
    layer_names = extract_layer_names(layer_tree)
    layer_tree_text = "\n".join(layer_names)
    eval_feedback = ""

    for attempt in range(MAX_RETRIES + 1):
        logger.info(f"Flaw spec generation attempt {attempt + 1}/{MAX_RETRIES + 1}")

        flaw_spec = generate_flaw_spec(
            openai_client, library_entry, layer_tree,
            competencies, proficiency, scenario,
            usage_by_model, eval_feedback,
        )
        if not flaw_spec:
            eval_feedback = "Generation returned no output. Try again."
            continue

        # Pre-validation: check layer names exist
        invalid_layers = validate_flaw_layers(flaw_spec.get("flaws", []), layer_names)
        if invalid_layers:
            eval_feedback = f"Invalid layer references: {'; '.join(invalid_layers)}"
            logger.warning(f"Pre-validation failed: {eval_feedback}")
            continue

        # LLM eval gate
        eval_result, eval_usage = eval_flaw_spec(
            flaw_spec, layer_tree_text, proficiency, openai_client
        )
        _track_usage(usage_by_model, EVAL_MODEL, eval_usage)

        if eval_result.get("pass"):
            logger.info("Flaw spec passed evaluation")
            return flaw_spec

        eval_feedback = eval_result.get("feedback", "Evaluation failed")
        logger.warning(f"Flaw spec eval failed (attempt {attempt + 1}): {eval_feedback}")

    logger.error("Flaw spec generation failed after all retries")
    return None


# ─── Phase 2: Generate Candidate Brief ───

def generate_candidate_brief(
    openai_client,
    library_entry: Dict,
    flaw_spec: Dict,
    proficiency: str,
    scenario: str,
    usage_by_model: Dict,
    eval_feedback: str = "",
) -> Optional[Dict]:
    """Generate candidate brief via LLM."""
    flaw_types = list(set(f.get("type", "") for f in flaw_spec.get("flaws", [])))
    flaw_types_summary = ", ".join(flaw_types)
    feedback_block = EVAL_FEEDBACK_BLOCK.format(feedback=eval_feedback) if eval_feedback else EVAL_FEEDBACK_BLOCK_EMPTY

    prompt = BRIEF_GENERATION_PROMPT.format(
        library_name=library_entry["name"],
        domain=library_entry["domain"],
        screens=", ".join(library_entry.get("screens", [])),
        flaw_types_summary=flaw_types_summary,
        proficiency=proficiency,
        scenario=scenario,
        eval_feedback_block=feedback_block,
    )

    messages = [
        {"role": "system", "content": BRIEF_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    try:
        response = openai_client.responses.create(
            model=GENERATION_MODEL,
            input=messages,
            reasoning={"effort": "medium"},
            text={
                "format": {
                    "type": "json_schema",
                    "name": CANDIDATE_BRIEF_SCHEMA["name"],
                    "schema": CANDIDATE_BRIEF_SCHEMA["schema"],
                    "strict": CANDIDATE_BRIEF_SCHEMA["strict"],
                }
            },
        )
        usage = extract_usage(response)
        _track_usage(usage_by_model, GENERATION_MODEL, usage)

        raw = getattr(response, "output_text", None)
        if not raw:
            logger.error("No output from brief generation")
            return None
        return json.loads(raw)
    except Exception as e:
        logger.error(f"Brief generation error: {e}\n{traceback.format_exc()}")
        return None


def run_brief_generation(
    openai_client,
    library_entry: Dict,
    flaw_spec: Dict,
    proficiency: str,
    scenario: str,
    usage_by_model: Dict,
) -> Optional[Dict]:
    """Generate candidate brief with eval gate and retry loop."""
    flaw_types = [f.get("type", "") for f in flaw_spec.get("flaws", [])]
    eval_feedback = ""

    for attempt in range(MAX_RETRIES + 1):
        logger.info(f"Brief generation attempt {attempt + 1}/{MAX_RETRIES + 1}")

        brief = generate_candidate_brief(
            openai_client, library_entry, flaw_spec,
            proficiency, scenario, usage_by_model, eval_feedback,
        )
        if not brief:
            eval_feedback = "Generation returned no output. Try again."
            continue

        # LLM eval gate
        eval_result, eval_usage = eval_candidate_brief(brief, flaw_types, openai_client)
        _track_usage(usage_by_model, EVAL_MODEL, eval_usage)

        if eval_result.get("pass"):
            logger.info("Candidate brief passed evaluation")
            return brief

        eval_feedback = eval_result.get("feedback", "Evaluation failed")
        logger.warning(f"Brief eval failed (attempt {attempt + 1}): {eval_feedback}")

    logger.error("Brief generation failed after all retries")
    return None


# ─── Phase 3: Generate Evaluation Rubric ───

def generate_evaluation_rubric(
    openai_client,
    flaw_spec: Dict,
    brief: Dict,
    proficiency: str,
    usage_by_model: Dict,
) -> Optional[Dict]:
    """Generate evaluation rubric via LLM. No eval gate — rubric structure is schema-enforced."""
    flaw_spec_summary = json.dumps(
        {"flaws": [{"type": f["type"], "severity": f["severity"], "rationale": f["rationale"]} for f in flaw_spec.get("flaws", [])]},
        indent=2
    )
    brief_summary = json.dumps(
        {"title": brief.get("title"), "change_requests": brief.get("change_requests")},
        indent=2
    )

    prompt = RUBRIC_GENERATION_PROMPT.format(
        flaw_spec_summary=flaw_spec_summary,
        brief_summary=brief_summary,
        proficiency=proficiency,
    )

    messages = [
        {"role": "system", "content": RUBRIC_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    try:
        response = openai_client.responses.create(
            model=GENERATION_MODEL,
            input=messages,
            reasoning={"effort": "medium"},
            text={
                "format": {
                    "type": "json_schema",
                    "name": EVALUATION_RUBRIC_SCHEMA["name"],
                    "schema": EVALUATION_RUBRIC_SCHEMA["schema"],
                    "strict": EVALUATION_RUBRIC_SCHEMA["strict"],
                }
            },
        )
        usage = extract_usage(response)
        _track_usage(usage_by_model, GENERATION_MODEL, usage)

        raw = getattr(response, "output_text", None)
        if not raw:
            logger.error("No output from rubric generation")
            return None
        return json.loads(raw)
    except Exception as e:
        logger.error(f"Rubric generation error: {e}\n{traceback.format_exc()}")
        return None


# ─── Entry Points ───

def create_design_review_task(
    competency_file: Path,
    proficiency: str,
    scenario: str,
    library_entry_id: str,
    env: str = "dev",
    dry_run: bool = False,
) -> Optional[Dict]:
    """Generate a design review task: flaw spec + brief + rubric.

    Returns dict with local_dir path, or None on failure.
    """
    openai_client = init_openai_client()
    usage_by_model = {}

    # Load inputs
    competencies = read_json_file_robust(competency_file)
    if isinstance(competencies, dict):
        competencies = competencies.get("competencies", [competencies])
    if not isinstance(competencies, list):
        competencies = [competencies]

    library_entry = get_library_entry(library_entry_id)
    if not library_entry:
        logger.error(f"Library entry '{library_entry_id}' not found in figma_library.json")
        return None

    layer_tree = load_layer_tree(library_entry_id)
    if not layer_tree:
        logger.error(f"Layer tree not found for '{library_entry_id}'")
        return None

    # Phase 1: Generate flaw spec
    logger.info("Phase 1: Generating flaw injection spec...")
    flaw_spec = run_flaw_spec_generation(
        openai_client, library_entry, layer_tree,
        competencies, proficiency, scenario, usage_by_model,
    )
    if not flaw_spec:
        print(format_cost_summary(usage_by_model))
        return None

    # Phase 2: Generate candidate brief
    logger.info("Phase 2: Generating candidate brief...")
    brief = run_brief_generation(
        openai_client, library_entry, flaw_spec,
        proficiency, scenario, usage_by_model,
    )
    if not brief:
        print(format_cost_summary(usage_by_model))
        return None

    # Phase 3: Generate evaluation rubric
    logger.info("Phase 3: Generating evaluation rubric...")
    rubric = generate_evaluation_rubric(
        openai_client, flaw_spec, brief, proficiency, usage_by_model,
    )
    if not rubric:
        print(format_cost_summary(usage_by_model))
        return None

    # Validate rubric weights sum to 100
    total_weight = sum(c.get("weight", 0) for c in rubric.get("criteria", []))
    if total_weight != 100:
        logger.error(f"Rubric weights sum to {total_weight}, expected 100")
        print(format_cost_summary(usage_by_model))
        return None

    # Build eval info
    eval_info = {
        "flaw_spec_eval": {"passed": True},
        "brief_eval": {"passed": True},
    }

    # Save locally
    if not dry_run:
        local_dir = save_design_task_locally(
            library_entry_id, flaw_spec, brief, rubric, library_entry, eval_info,
            competencies,
        )
    else:
        local_dir = "DRY_RUN"

    # Print cost summary
    print(format_cost_summary(usage_by_model))

    logger.info(f"Design review task generated successfully")
    return {
        "local_dir": str(local_dir),
        "dry_run": dry_run,
        "flaw_count": len(flaw_spec.get("flaws", [])),
    }


def store_design_review_task(
    spec_file: Path,
    figma_link: str,
    env: str = "dev",
) -> Optional[Dict]:
    """Store a generated design review task in Supabase.

    Called after the Figma plugin step, when the flawed design is ready.
    """
    # Load and validate spec file
    spec_data = json.loads(spec_file.read_text(encoding="utf-8"))
    errors = validate_spec_file(spec_data)
    if errors:
        logger.error(f"Spec file validation failed: {'; '.join(errors)}")
        return None

    # Validate Figma link
    if not validate_figma_link(figma_link):
        logger.error(f"Invalid Figma link: {figma_link}")
        return None

    flaw_spec = spec_data["flaw_spec"]
    brief = spec_data["candidate_brief"]
    rubric = spec_data["evaluation_rubric"]
    library_entry = spec_data["library_entry"]
    eval_info = spec_data.get("eval_info", {})

    # Build Supabase record
    created_at = datetime.now(timezone.utc)

    # Build criterias from library entry domain
    criterias_for_db = [
        {
            "name": "UI/UX Design",
            "proficiency": flaw_spec.get("flaws", [{}])[0].get("severity", "INTERMEDIATE").upper()
                if flaw_spec.get("flaws") else "INTERMEDIATE",
        }
    ]

    # Use competency info if available in the spec
    if "competencies" in spec_data:
        criterias_for_db = [
            {
                "competency_id": c.get("competency_id") or c.get("id"),
                "name": c.get("name"),
                "proficiency": c.get("proficiency", "BASIC"),
            }
            for c in spec_data["competencies"]
        ]

    task_data = {
        "created_at": created_at.isoformat(),
        "pre_requisites": "Figma account (free tier), understanding of UX principles",
        "answer": "",
        "criterias": criterias_for_db,
        "is_deployed": False,
        "task_blob": {
            "title": brief.get("title", "Design Review Task"),
            "task_type": "design_review",
            "question": f"Review the provided Figma design and complete the change requests. "
                        f"Submit your modified Figma link and written rationale.",
            "short_overview": brief.get("domain_context", ""),
            "outcomes": "Candidate identifies UX flaws, makes design improvements, and provides written rationale",
            "resources": {
                "figma_source_link": library_entry.get("figma_community_url", ""),
                "figma_flawed_link": figma_link,
            },
            "hints": "",
            "definitions": {},
            "domain_context": brief.get("domain_context", ""),
            "constraints": brief.get("constraints", []),
            "change_requests": brief.get("change_requests", []),
            "submission_requirements": brief.get("submission_requirements", {}),
            "time_limit_minutes": brief.get("time_limit_minutes", 45),
            "attribution": f"{library_entry.get('attribution', 'Unknown')}, {library_entry.get('license', 'CC BY 4.0')}",
        },
        "is_shared_infra_required": False,
        "readme_content": None,
        "eval_info": eval_info,
        "solutions": {
            "flaw_spec": flaw_spec,
            "answer_key": flaw_spec.get("answer_key", {}),
            "evaluation_rubric": rubric,
        },
    }

    # Insert into Supabase
    try:
        supabase = init_supabase(env)
        result = supabase.table("tasks").insert(task_data).execute()
        task_id = result.data[0].get("id") or result.data[0].get("task_id")
        logger.info(f"Task stored in Supabase ({env}): {task_id}")

        # Insert task-competency relationships
        for criteria in criterias_for_db:
            comp_id = criteria.get("competency_id")
            if comp_id:
                supabase.table("task_competencies").insert({
                    "task_id": task_id,
                    "competency_id": comp_id,
                }).execute()

        return {"task_id": task_id, "env": env}

    except Exception as e:
        logger.error(f"Supabase insert error: {e}\n{traceback.format_exc()}")
        return None
```

- [ ] **Step 2: Verify syntax**

Run: `python -c "import ast; ast.parse(open('design_review_flow/design_review_multiagent.py').read()); print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add design_review_flow/design_review_multiagent.py
git commit --no-gpg-sign -m "feat(design-review): add main orchestrator with 3-phase LLM pipeline and Supabase storage"
```

---

### Task 7: Library + Layer Tree Scaffolding

**Files:**
- Create: `design_review_flow/figma_library.json`
- Create: `design_review_flow/layer_trees/.gitkeep`

- [ ] **Step 1: Create empty library**

```json
[]
```

- [ ] **Step 2: Create layer_trees directory**

```bash
mkdir -p design_review_flow/layer_trees && touch design_review_flow/layer_trees/.gitkeep
```

- [ ] **Step 3: Create infra_assets/design_tasks directory**

```bash
mkdir -p infra_assets/design_tasks
```

- [ ] **Step 4: Commit**

```bash
git add design_review_flow/figma_library.json design_review_flow/layer_trees/.gitkeep
git commit --no-gpg-sign -m "feat(design-review): scaffold figma library and layer tree directories"
```

---

### Task 8: Figma Plugin

**Files:**
- Create: `design_review_flow/figma_plugin/manifest.json`
- Create: `design_review_flow/figma_plugin/code.ts`
- Create: `design_review_flow/figma_plugin/ui.html`
- Create: `design_review_flow/figma_plugin/package.json`
- Create: `design_review_flow/figma_plugin/tsconfig.json`

- [ ] **Step 1: Create `manifest.json`**

```json
{
  "name": "Utkrushta Design Review - Flaw Injector",
  "id": "utkrushta-design-review-flaw-injector",
  "api": "1.0.0",
  "main": "code.js",
  "ui": "ui.html",
  "editorType": ["figma"]
}
```

Note: `id` must be replaced with the actual plugin ID after registering on Figma's developer platform.

- [ ] **Step 2: Create `package.json`**

```json
{
  "name": "utkrushta-flaw-injector",
  "version": "1.0.0",
  "description": "Figma plugin to inject UX flaws for design review assessments",
  "scripts": {
    "build": "tsc",
    "watch": "tsc --watch"
  },
  "devDependencies": {
    "@figma/plugin-typings": "^1.100.0",
    "typescript": "^5.0.0"
  }
}
```

- [ ] **Step 3: Create `tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "none",
    "lib": ["ES2020"],
    "strict": true,
    "outDir": ".",
    "rootDir": ".",
    "typeRoots": ["./node_modules/@figma"]
  },
  "include": ["code.ts"]
}
```

- [ ] **Step 4: Create `code.ts`**

```typescript
// Flaw Injector Plugin — applies flaw specs to Figma designs

interface Flaw {
  id: string;
  screen: string;
  type: string;
  severity: string;
  instruction: string;
  target_layer: string;
  rationale: string;
}

interface FlawSpec {
  source_file: string;
  target_screens: string[];
  flaws: Flaw[];
  answer_key: {
    flaws_summary: string;
    expected_findings: string[];
    overall_quality: string;
  };
}

interface ApplyResult {
  flaw_id: string;
  status: "applied" | "needs_manual" | "error";
  message: string;
}

// Show the UI
figma.showUI(__html__, { width: 500, height: 600 });

// Listen for messages from the UI
figma.ui.onmessage = async (msg: { type: string; spec?: string }) => {
  if (msg.type === "preview") {
    await handlePreview(msg.spec || "");
  } else if (msg.type === "apply") {
    await handleApply(msg.spec || "");
  } else if (msg.type === "cancel") {
    figma.closePlugin();
  }
};

async function handlePreview(specJson: string) {
  try {
    const spec: FlawSpec = JSON.parse(specJson);
    const results: Array<{ flaw_id: string; found: boolean; layer_name: string }> = [];

    for (const flaw of spec.flaws) {
      const node = findNodeByName(flaw.target_layer);
      results.push({
        flaw_id: flaw.id,
        found: node !== null,
        layer_name: flaw.target_layer,
      });
    }

    figma.ui.postMessage({ type: "preview-result", results });
  } catch (e) {
    figma.ui.postMessage({
      type: "error",
      message: `Failed to parse spec: ${(e as Error).message}`,
    });
  }
}

async function handleApply(specJson: string) {
  try {
    const spec: FlawSpec = JSON.parse(specJson);
    const results: ApplyResult[] = [];

    for (const flaw of spec.flaws) {
      const result = await applyFlaw(flaw);
      results.push(result);
    }

    figma.ui.postMessage({ type: "apply-result", results });
    figma.notify(
      `Done: ${results.filter((r) => r.status === "applied").length} applied, ` +
      `${results.filter((r) => r.status === "needs_manual").length} need manual action`
    );
  } catch (e) {
    figma.ui.postMessage({
      type: "error",
      message: `Failed to apply: ${(e as Error).message}`,
    });
  }
}

function findNodeByName(name: string): SceneNode | null {
  // Search the entire document for a node with the exact name
  // v1: exact match only — no fuzzy matching per spec
  const allNodes = figma.currentPage.findAll();

  for (const node of allNodes) {
    if (node.name === name) {
      return node;
    }
  }

  return null;
}

async function applyFlaw(flaw: Flaw): Promise<ApplyResult> {
  const node = findNodeByName(flaw.target_layer);

  if (!node) {
    return {
      flaw_id: flaw.id,
      status: "needs_manual",
      message: `Layer not found: "${flaw.target_layer}"`,
    };
  }

  try {
    const instruction = flaw.instruction.toLowerCase();

    // Text content changes
    if (node.type === "TEXT" && hasTextChange(instruction)) {
      await applyTextChange(node, flaw.instruction);
      return { flaw_id: flaw.id, status: "applied", message: `Text changed on "${node.name}"` };
    }

    // Color/fill changes
    if (hasColorChange(instruction)) {
      applyColorChange(node, flaw.instruction);
      return { flaw_id: flaw.id, status: "applied", message: `Color changed on "${node.name}"` };
    }

    // Size changes
    if (hasSizeChange(instruction)) {
      applySizeChange(node, flaw.instruction);
      return { flaw_id: flaw.id, status: "applied", message: `Size changed on "${node.name}"` };
    }

    // Font changes
    if (node.type === "TEXT" && hasFontChange(instruction)) {
      await applyFontChange(node, flaw.instruction);
      return { flaw_id: flaw.id, status: "applied", message: `Font changed on "${node.name}"` };
    }

    // If we can't determine the change type, mark as manual
    return {
      flaw_id: flaw.id,
      status: "needs_manual",
      message: `Found layer "${node.name}" but couldn't auto-apply: "${flaw.instruction}"`,
    };
  } catch (e) {
    return {
      flaw_id: flaw.id,
      status: "error",
      message: `Error applying to "${node.name}": ${(e as Error).message}`,
    };
  }
}

// ─── Change Detection Helpers ───

function hasTextChange(instruction: string): boolean {
  return /change text|change .* to|rename|update text|text from .* to/i.test(instruction);
}

function hasColorChange(instruction: string): boolean {
  return /#[0-9a-fA-F]{6}|color|fill|background/i.test(instruction);
}

function hasSizeChange(instruction: string): boolean {
  return /size|resize|reduce .* size|increase .* size|width|height|smaller|larger/i.test(instruction);
}

function hasFontChange(instruction: string): boolean {
  return /font.?size|font.?weight|bold|regular|light/i.test(instruction);
}

// ─── Change Application Helpers ───

async function applyTextChange(node: TextNode, instruction: string): Promise<void> {
  // Extract "to 'X'" or "to \"X\"" pattern
  const toMatch = instruction.match(/(?:to|with)\s+['"]([^'"]+)['"]/i);
  if (toMatch) {
    await figma.loadFontAsync(node.fontName as FontName);
    node.characters = toMatch[1];
    return;
  }

  // Extract "from 'X' to 'Y'" pattern
  const fromToMatch = instruction.match(/from\s+['"]([^'"]+)['"]\s+to\s+['"]([^'"]+)['"]/i);
  if (fromToMatch) {
    await figma.loadFontAsync(node.fontName as FontName);
    node.characters = fromToMatch[2];
    return;
  }
}

function applyColorChange(node: SceneNode, instruction: string): void {
  const hexMatch = instruction.match(/#([0-9a-fA-F]{6})/);
  if (!hexMatch) return;

  const hex = hexMatch[1];
  const r = parseInt(hex.substring(0, 2), 16) / 255;
  const g = parseInt(hex.substring(2, 4), 16) / 255;
  const b = parseInt(hex.substring(4, 6), 16) / 255;

  if ("fills" in node) {
    node.fills = [{ type: "SOLID", color: { r, g, b } }];
  }
}

function applySizeChange(node: SceneNode, instruction: string): void {
  if (!("resize" in node)) return;

  // Try to extract specific dimensions
  const widthMatch = instruction.match(/width\s*(?:to\s*)?(\d+)/i);
  const heightMatch = instruction.match(/height\s*(?:to\s*)?(\d+)/i);

  if (widthMatch || heightMatch) {
    const newWidth = widthMatch ? parseInt(widthMatch[1]) : node.width;
    const newHeight = heightMatch ? parseInt(heightMatch[1]) : node.height;
    node.resize(newWidth, newHeight);
    return;
  }

  // Handle "reduce size to match" or percentage-based
  if (/reduce|smaller|decrease/i.test(instruction)) {
    node.resize(node.width * 0.7, node.height * 0.7);
  } else if (/increase|larger|bigger/i.test(instruction)) {
    node.resize(node.width * 1.3, node.height * 1.3);
  }
}

async function applyFontChange(node: TextNode, instruction: string): Promise<void> {
  const currentFont = node.fontName as FontName;
  await figma.loadFontAsync(currentFont);

  // Font size changes
  const sizeMatch = instruction.match(/font.?size\s*(?:to\s*)?(\d+)/i);
  if (sizeMatch) {
    node.fontSize = parseInt(sizeMatch[1]);
    return;
  }

  // Font weight changes
  if (/bold/i.test(instruction)) {
    try {
      const boldFont: FontName = { family: currentFont.family, style: "Bold" };
      await figma.loadFontAsync(boldFont);
      node.fontName = boldFont;
    } catch {
      // Bold variant not available
    }
  } else if (/regular|normal/i.test(instruction)) {
    try {
      const regularFont: FontName = { family: currentFont.family, style: "Regular" };
      await figma.loadFontAsync(regularFont);
      node.fontName = regularFont;
    } catch {
      // Regular variant not available
    }
  }
}
```

- [ ] **Step 5: Create `ui.html`**

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Inter, system-ui, sans-serif; padding: 16px; font-size: 13px; color: #333; }
    h2 { font-size: 16px; margin-bottom: 12px; }
    textarea {
      width: 100%; height: 180px; padding: 8px; border: 1px solid #ddd;
      border-radius: 6px; font-family: monospace; font-size: 12px; resize: vertical;
    }
    .btn-group { display: flex; gap: 8px; margin-top: 12px; }
    button {
      flex: 1; padding: 8px 16px; border: none; border-radius: 6px;
      font-size: 13px; cursor: pointer; font-weight: 500;
    }
    .btn-primary { background: #0D99FF; color: white; }
    .btn-primary:hover { background: #0B85E0; }
    .btn-secondary { background: #E8E8E8; color: #333; }
    .btn-secondary:hover { background: #D8D8D8; }
    .btn-danger { background: #F24822; color: white; }
    .btn-danger:hover { background: #D93E1C; }
    .btn-primary:disabled, .btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }
    #results { margin-top: 16px; max-height: 250px; overflow-y: auto; }
    .result-item {
      display: flex; align-items: center; gap: 8px; padding: 6px 8px;
      border-bottom: 1px solid #f0f0f0; font-size: 12px;
    }
    .result-item:last-child { border-bottom: none; }
    .status-found { color: #14AE5C; }
    .status-not-found { color: #F24822; }
    .status-applied { color: #14AE5C; }
    .status-manual { color: #FFCD29; }
    .status-error { color: #F24822; }
    .error-msg { color: #F24822; margin-top: 8px; font-size: 12px; }
    .summary { margin-top: 12px; padding: 8px; background: #f5f5f5; border-radius: 6px; font-size: 12px; }
  </style>
</head>
<body>
  <h2>Flaw Injector</h2>
  <p style="margin-bottom: 8px; color: #666;">Paste the flaw injection spec JSON below:</p>
  <textarea id="spec-input" placeholder='Paste flaw_spec_for_plugin.json contents here...'></textarea>

  <div class="btn-group">
    <button id="btn-preview" class="btn-secondary" onclick="preview()">Preview Matches</button>
    <button id="btn-apply" class="btn-primary" onclick="apply()" disabled>Apply Flaws</button>
    <button class="btn-secondary" onclick="cancel()">Cancel</button>
  </div>

  <div id="results"></div>

  <script>
    function preview() {
      const spec = document.getElementById('spec-input').value;
      if (!spec.trim()) return;
      document.getElementById('btn-preview').disabled = true;
      document.getElementById('btn-preview').textContent = 'Scanning...';
      parent.postMessage({ pluginMessage: { type: 'preview', spec } }, '*');
    }

    function apply() {
      const spec = document.getElementById('spec-input').value;
      if (!spec.trim()) return;
      document.getElementById('btn-apply').disabled = true;
      document.getElementById('btn-apply').textContent = 'Applying...';
      parent.postMessage({ pluginMessage: { type: 'apply', spec } }, '*');
    }

    function cancel() {
      parent.postMessage({ pluginMessage: { type: 'cancel' } }, '*');
    }

    onmessage = (event) => {
      const msg = event.data.pluginMessage;
      const resultsDiv = document.getElementById('results');

      if (msg.type === 'preview-result') {
        document.getElementById('btn-preview').disabled = false;
        document.getElementById('btn-preview').textContent = 'Preview Matches';

        const found = msg.results.filter(r => r.found).length;
        const total = msg.results.length;

        let html = `<div class="summary">${found}/${total} layers found</div>`;
        html += msg.results.map(r =>
          `<div class="result-item">
            <span class="${r.found ? 'status-found' : 'status-not-found'}">${r.found ? '✓' : '✗'}</span>
            <span>${r.flaw_id}: ${r.layer_name}</span>
          </div>`
        ).join('');

        resultsDiv.innerHTML = html;

        // Enable apply only if at least one layer found
        document.getElementById('btn-apply').disabled = found === 0;
      }

      if (msg.type === 'apply-result') {
        document.getElementById('btn-apply').disabled = false;
        document.getElementById('btn-apply').textContent = 'Apply Flaws';

        const applied = msg.results.filter(r => r.status === 'applied').length;
        const manual = msg.results.filter(r => r.status === 'needs_manual').length;
        const errors = msg.results.filter(r => r.status === 'error').length;

        let html = `<div class="summary">Applied: ${applied} | Manual: ${manual} | Errors: ${errors}</div>`;
        html += msg.results.map(r => {
          const cls = r.status === 'applied' ? 'status-applied' : r.status === 'needs_manual' ? 'status-manual' : 'status-error';
          const icon = r.status === 'applied' ? '✓' : r.status === 'needs_manual' ? '⚠' : '✗';
          return `<div class="result-item">
            <span class="${cls}">${icon}</span>
            <span>${r.flaw_id}: ${r.message}</span>
          </div>`;
        }).join('');

        resultsDiv.innerHTML = html;
      }

      if (msg.type === 'error') {
        resultsDiv.innerHTML = `<div class="error-msg">${msg.message}</div>`;
        document.getElementById('btn-preview').disabled = false;
        document.getElementById('btn-preview').textContent = 'Preview Matches';
        document.getElementById('btn-apply').textContent = 'Apply Flaws';
      }
    };
  </script>
</body>
</html>
```

- [ ] **Step 6: Verify TypeScript compiles (optional — requires npm install)**

```bash
cd design_review_flow/figma_plugin && npm install && npm run build
```

Expected: `code.js` generated without errors. (Skip if Node.js not available — can be done later.)

- [ ] **Step 7: Commit**

```bash
git add design_review_flow/figma_plugin/
git commit --no-gpg-sign -m "feat(design-review): add Figma plugin for automated flaw injection"
```

---

### Task 9: End-to-End Verification

- [ ] **Step 1: Verify full CLI loads**

Run: `python -m design_review_flow --help`
Expected: Shows `generate` and `store` commands with their options.

- [ ] **Step 2: Verify `generate --help`**

Run: `python -m design_review_flow generate --help`
Expected: Shows all flags: `--competency-file`, `--proficiency`, `--scenario`, `--library-entry-id`, `--env`, `--dry-run`

- [ ] **Step 3: Verify `store --help`**

Run: `python -m design_review_flow store --help`
Expected: Shows all flags: `--spec-file`, `--figma-link`, `--env`

- [ ] **Step 4: Verify all imports resolve**

Run: `python -c "from design_review_flow import create_design_review_task, store_design_review_task; print('All imports OK')"`
Expected: `All imports OK`

- [ ] **Step 5: Commit if any fixes were needed**

```bash
git add design_review_flow/
git commit --no-gpg-sign -m "fix(design-review): resolve import and CLI issues from end-to-end verification"
```

---

### Task 10: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Add design review CLI commands to CLAUDE.md**

Add to the "Common Commands" section:

```markdown
### Design review task generation
```bash
# Generate flaw spec + brief + rubric
python -m design_review_flow generate \
  --competency-file path/to/competency.json \
  --proficiency INTERMEDIATE \
  --scenario "SaaS onboarding redesign" \
  --library-entry-id lib-001

# Store task in Supabase (after Figma plugin step)
python -m design_review_flow store \
  --spec-file path/to/design_task_spec.json \
  --figma-link "https://figma.com/file/...?duplicate" \
  --env dev
```
```

- [ ] **Step 2: Add to Architecture sub-packages table**

Add row:
```markdown
| `design_review_flow/` | UI/UX design review assessments with Figma flaw injection |
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit --no-gpg-sign -m "docs: add design review flow to CLAUDE.md"
```
