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
