"""
Prompt templates for the Prompt Generator.

Contains the meta-prompt (tells the LLM how to write a task generation prompt),
evaluation prompt, JSON schema for structured output, and few-shot example loader.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional

from scenario_generator.prompts import PROFICIENCY_GUARDRAILS


# ============================================================================
# FEW-SHOT EXAMPLE PATHS (relative to project root)
# ============================================================================

_PROJECT_ROOT = Path(__file__).parent.parent

FEW_SHOT_EXAMPLES = {
    "docker-multi-service": {
        "path": _PROJECT_ROOT / "task_generation_prompts" / "Basic" / "microservices_basic_prompt.py",
        "annotation": "Docker multi-service deployment model. Thorough run.sh/kill.sh instructions, per-service health checks, inter-service networking, strong README structure with 3-5 bullets max per section.",
    },
    "docker-backend": {
        "path": _PROJECT_ROOT / "task_generation_prompts" / "Basic" / "nodejs_mongodb_basic_prompt.py",
        "annotation": "Docker backend deployment model with DB seeding. Covers docker-compose with health checks, init_database.sql for schema/seed data, dual-layer focus (database optimization + API design).",
    },
    "no-docker": {
        "path": _PROJECT_ROOT / "task_generation_prompts" / "Basic" / "expressjs_basic_prompt.py",
        "annotation": "No-docker deployment model. Pure backend with source code + README only. Clean 3-part structure (CONTEXT, INPUT_AND_ASK, INSTRUCTIONS). Good example of minimal infrastructure.",
    },
    "design-only": {
        "path": _PROJECT_ROOT / "task_generation_prompts" / "Basic" / "system_design_prompt.py",
        "annotation": "Design-only deployment model. No source code, only README.md + DESIGN_TEMPLATE.md. Evaluates architectural thinking, trade-off reasoning, communication clarity.",
    },
}


def load_few_shot_examples(deployment_model: str) -> List[Dict[str, str]]:
    """Load 2-3 few-shot examples based on deployment model.

    Selection logic:
    - 1 example matching the target deployment model (primary)
    - 2 contrast examples from other deployment models
    Note: We have 1 curated example per deployment model. If more examples
    are added per model in the future, this function should be updated to
    select 2 matching + 1 contrast.
    """
    examples = []
    all_models = list(FEW_SHOT_EXAMPLES.keys())

    # Primary: matching deployment model
    if deployment_model in FEW_SHOT_EXAMPLES:
        entry = FEW_SHOT_EXAMPLES[deployment_model]
        content = _read_example_file(entry["path"])
        if content:
            examples.append({
                "deployment_model": deployment_model,
                "annotation": entry["annotation"],
                "content": content,
            })

    # Fill remaining slots (up to 3 total) from other models
    for model_name in all_models:
        if len(examples) >= 3:
            break
        if model_name == deployment_model:
            continue
        entry = FEW_SHOT_EXAMPLES[model_name]
        content = _read_example_file(entry["path"])
        if content:
            examples.append({
                "deployment_model": model_name,
                "annotation": entry["annotation"],
                "content": content,
            })

    return examples


def _read_example_file(path: Path) -> Optional[str]:
    """Read a few-shot example file, returning None on error."""
    try:
        return path.read_text(encoding="utf-8")
    except (IOError, OSError):
        return None


# ============================================================================
# STRUCTURED OUTPUT SCHEMA — LLM returns JSON with 3 prompt sections
# ============================================================================

GENERATION_SCHEMA = {
    "type": "json_schema",
    "name": "prompt_generation",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "context_prompt": {
                "type": "string",
                "description": (
                    "The CONTEXT prompt section. Sets company and role context. "
                    "MUST contain template variables {organization_background} and {role_context}. "
                    "Should ask the LLM to summarize its understanding of the company and role."
                ),
            },
            "input_and_ask_prompt": {
                "type": "string",
                "description": (
                    "The INPUT_AND_ASK prompt section. Lists competencies and scenarios. "
                    "MUST contain template variables {competencies} and {real_world_task_scenarios}. "
                    "Should include critical task generation requirements and ask for confirmation "
                    "of understanding before proceeding."
                ),
            },
            "instructions_prompt": {
                "type": "string",
                "description": (
                    "The INSTRUCTIONS prompt section. Detailed task generation rules including: "
                    "JSON output format with all required fields (name, title, question, code_files, "
                    "outcomes, short_overview, pre_requisites, answer, hints, definitions), "
                    "README structure (Task Overview, Objectives, How to Verify, Helpful Tips), "
                    "code quality rules, deployment infrastructure requirements, and proficiency "
                    "calibration guidelines. This is the longest and most detailed section."
                ),
            },
        },
        "required": ["context_prompt", "input_and_ask_prompt", "instructions_prompt"],
        "additionalProperties": False,
    },
}


# ============================================================================
# META SYSTEM PROMPT — tells LLM it's writing a prompt template, not a task
# ============================================================================

META_SYSTEM_PROMPT = """You are a senior assessment architect with 15+ years of experience designing technical coding assessments for engineering hiring.

Your job is to write a PROMPT TEMPLATE that will be used by ANOTHER LLM to generate individual assessment tasks. You are NOT generating a task — you are generating the INSTRUCTIONS that will produce tasks.

The prompt template you create will be used in a multi-turn conversation:
1. CONTEXT section: Sets company/role context, asks the LLM to confirm understanding
2. INPUT_AND_ASK section: Provides competencies and scenarios, asks for task plan confirmation
3. INSTRUCTIONS section: Detailed rules for generating the task JSON output

CRITICAL RULES:
- The template must contain these exact template variables (with single curly braces): {organization_background}, {role_context}, {competencies}, {real_world_task_scenarios}
- JSON examples within the template must use DOUBLE curly braces {{ }} since the template will be formatted with Python .format()
- The INSTRUCTIONS section must specify the complete JSON output structure the task LLM should produce
- All starter code the task LLM generates must be FULLY FUNCTIONAL — zero syntax/runtime errors
- The template must enforce NO TODO comments and NO solution hints in generated starter code
- The template must enforce production-level code quality expectations"""


# ============================================================================
# BUILD META-PROMPT — composes all layers into the generation prompt
# ============================================================================

def build_meta_prompt(
    techs: List[str],
    proficiency: str,
    deployment_model: str,
    deployment_eval_criteria: str,
    registry_key: str,
    tech_slug_upper: str,
    level: str,
    few_shot_examples: List[Dict[str, str]],
    eval_failure_feedback: Optional[List[Dict[str, str]]] = None,
) -> str:
    """Build the complete meta-prompt for prompt generation.

    Args:
        techs: List of technology names (e.g., ["Java", "Kafka"])
        proficiency: Proficiency level (e.g., "BASIC")
        deployment_model: One of: no-docker, docker-backend, docker-multi-service, design-only
        deployment_eval_criteria: Text criteria from DEPLOYMENT_MODELS
        registry_key: The PROMPT_REGISTRY key (e.g., "Java (BASIC), Kafka (BASIC)")
        tech_slug_upper: Uppercase slug for constant naming (e.g., "JAVA_KAFKA")
        level: Proficiency level (e.g., "BASIC")
        few_shot_examples: List of loaded few-shot examples
        eval_failure_feedback: Optional list of previous failure feedback for retry
    """
    proficiency_upper = proficiency.upper()

    # Layer 2: Structure requirements
    structure_block = f"""
## OUTPUT STRUCTURE REQUIREMENTS

You must return a JSON object with exactly 3 fields: context_prompt, input_and_ask_prompt, instructions_prompt.

The constant names in the final Python file will be:
- PROMPT_{tech_slug_upper}_{level}_CONTEXT
- PROMPT_{tech_slug_upper}_{level}_INPUT_AND_ASK
- PROMPT_{tech_slug_upper}_{level}_INSTRUCTIONS

The PROMPT_REGISTRY key will be: "{registry_key}"

### context_prompt requirements:
- Must contain {{organization_background}} and {{role_context}} template variables (single curly braces in your output)
- Should set company context and role requirements
- Should ask the receiving LLM to summarize its understanding

### input_and_ask_prompt requirements:
- Must contain {{competencies}} and {{real_world_task_scenarios}} template variables
- Should list critical task generation requirements (scenario alignment, complexity calibration, time constraints)
- Should ask the receiving LLM to confirm understanding before proceeding

### instructions_prompt requirements:
- This is the LONGEST and MOST DETAILED section
- Must specify the complete JSON output format the task LLM should produce:
  {{{{
    "name": "kebab-case-task-name (under 50 chars)",
    "title": "Human-readable action verb + subject",
    "question": "Business scenario and specific ask",
    "code_files": {{{{"README.md": "...", "source files": "..."}}}},
    "outcomes": "Expected results as bullet points",
    "short_overview": "Business context, goal, expected outcome",
    "pre_requisites": "Tools and knowledge required",
    "answer": "High-level solution approach",
    "hints": "Single-line nudge (not full answer)",
    "definitions": {{{{"term": "definition"}}}}
  }}}}
- Must specify README.md structure: Task Overview, Objectives, How to Verify, Helpful Tips
- Must enforce: no TODO comments, no solution hints, fully functional starter code
- Must enforce: production-level code quality, best practices
- Must enforce: task drawn from real-world scenarios provided in input
"""

    # Layer 3: Deployment model injection
    deployment_block = f"""
## DEPLOYMENT MODEL: {deployment_model}

The prompt you generate is for tasks that use the "{deployment_model}" deployment model.

{deployment_eval_criteria}

Make sure your INSTRUCTIONS section includes DETAILED infrastructure requirements covering all the above points. The task LLM reading your prompt must know exactly what deployment files to generate and what they must contain.
"""

    # Proficiency guardrails
    proficiency_block = ""
    if proficiency_upper in PROFICIENCY_GUARDRAILS:
        proficiency_block = f"""
## PROFICIENCY GUARDRAILS

The prompt you generate is for {proficiency_upper} level tasks. Include these guardrails in your INSTRUCTIONS section so the task LLM calibrates complexity correctly:

{PROFICIENCY_GUARDRAILS[proficiency_upper]}
"""

    # Layer 4: Few-shot examples
    examples_block = "\n## FEW-SHOT EXAMPLES\n\nBelow are existing prompt templates that demonstrate good quality. Study their structure, depth, and coverage — then write a prompt of similar quality for the specified technology.\n\nIMPORTANT: These examples use legacy constant naming conventions. Ignore their variable names — your output is a JSON object, and the post-processor handles Python constant naming.\n"
    for i, ex in enumerate(few_shot_examples, 1):
        examples_block += f"""
### Example {i} (deployment model: {ex['deployment_model']})
**Why this is a good example:** {ex['annotation']}

```python
{ex['content']}
```
"""

    # Tech-specific context
    tech_names = ", ".join(techs)
    tech_context = f"""
## YOUR TASK

Generate a prompt template for: **{tech_names}** at **{proficiency_upper}** proficiency level.

The prompt must be comprehensive enough that an LLM reading it can generate complete, working assessment tasks for {tech_names} developers with appropriate complexity for the {proficiency_upper} level.
"""

    # Eval failure feedback (for retries)
    feedback_block = ""
    if eval_failure_feedback:
        feedback_block = "\n## PREVIOUS ATTEMPT FEEDBACK\n\nYour previous generation attempt failed evaluation. Fix these issues:\n"
        for fb in eval_failure_feedback:
            feedback_block += f"\n- **Issue:** {fb.get('reason', 'Unknown')}\n"

    return (
        structure_block
        + deployment_block
        + proficiency_block
        + tech_context
        + examples_block
        + feedback_block
    )


# ============================================================================
# EVALUATION PROMPT — checks generated prompt quality
# ============================================================================

EVAL_SYSTEM_PROMPT = """You are a strict quality evaluator for task generation prompts. You evaluate whether a prompt template will produce high-quality, working coding assessment tasks.

You must be STRICT. If the prompt is missing critical sections or would produce broken tasks, mark it as FAIL."""


def build_eval_prompt(
    generated_prompt_text: str,
    deployment_model: str,
    proficiency: str,
    deployment_eval_criteria: str,
) -> str:
    """Build the evaluation prompt for a generated prompt template."""
    return f"""Evaluate the following task generation prompt template.

## PROMPT TO EVALUATE

{generated_prompt_text}

## EVALUATION CRITERIA

### 1. Completeness
Does the INSTRUCTIONS section cover ALL of these?
- JSON output format with fields: name, title, question, code_files, outcomes, short_overview, pre_requisites, answer, hints, definitions
- README structure: Task Overview, Objectives, How to Verify, Helpful Tips
- Code quality rules (no TODO, no solution hints, functional starter code)
- Production-level expectations

### 2. Proficiency Calibration ({proficiency})
- Are complexity expectations appropriate for {proficiency} level?
- Does it reference appropriate time constraints?
- Does it set correct concept boundaries (allowed vs forbidden)?

### 3. Deployment Correctness ({deployment_model})
{deployment_eval_criteria}
Are the infrastructure instructions detailed enough to produce WORKING deployments?

### 4. No Solution Leakage
- Does the prompt enforce no TODO comments in generated starter code?
- Does the prompt enforce no solution hints?
- Does the prompt enforce no setup/run commands in README?

### 5. Scenario Alignment
- Does the prompt instruct use of {{real_world_task_scenarios}} for inspiration?
- Does the prompt enforce selecting from provided scenarios?

## OUTPUT FORMAT

Return a JSON object:
{{
  "pass": true/false,
  "reasons": ["reason1", "reason2"]  // empty if pass=true
}}

Be STRICT. Mark as FAIL if any of the 5 criteria are not adequately addressed."""


EVAL_SCHEMA = {
    "type": "json_schema",
    "name": "prompt_evaluation",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "pass": {
                "type": "boolean",
                "description": "Whether the prompt passes all evaluation criteria",
            },
            "reasons": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of failure reasons (empty if pass=true)",
            },
        },
        "required": ["pass", "reasons"],
        "additionalProperties": False,
    },
}


# ============================================================================
# POST-PROCESSOR — assembles JSON output into Python file
# ============================================================================

def assemble_python_file(
    context_prompt: str,
    input_and_ask_prompt: str,
    instructions_prompt: str,
    tech_slug_upper: str,
    level: str,
    registry_key: str,
) -> str:
    """Assemble the 3 prompt sections into a complete Python file.

    Args:
        context_prompt: The CONTEXT prompt text from LLM
        input_and_ask_prompt: The INPUT_AND_ASK prompt text from LLM
        instructions_prompt: The INSTRUCTIONS prompt text from LLM
        tech_slug_upper: Uppercase tech slug (e.g., "JAVA_KAFKA")
        level: Proficiency level (e.g., "BASIC")
        registry_key: The PROMPT_REGISTRY key (e.g., "Java (BASIC), Kafka (BASIC)")

    Returns:
        Complete Python file content as a string.
    """
    # Escape triple quotes within prompt content to avoid breaking Python strings
    def escape_triple_quotes(text: str) -> str:
        return text.replace('"""', '\\"\\"\\"')

    ctx = escape_triple_quotes(context_prompt)
    inp = escape_triple_quotes(input_and_ask_prompt)
    ins = escape_triple_quotes(instructions_prompt)

    ctx_name = f"PROMPT_{tech_slug_upper}_{level}_CONTEXT"
    inp_name = f"PROMPT_{tech_slug_upper}_{level}_INPUT_AND_ASK"
    ins_name = f"PROMPT_{tech_slug_upper}_{level}_INSTRUCTIONS"

    return f'''{ctx_name} = """
{ctx}
"""

{inp_name} = """
{inp}
"""

{ins_name} = """
{ins}
"""

PROMPT_REGISTRY = {{
    "{registry_key}": [
        {ctx_name},
        {inp_name},
        {ins_name},
    ],
}}
'''
