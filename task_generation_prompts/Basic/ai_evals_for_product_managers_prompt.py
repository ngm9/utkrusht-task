PROMPT_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_AI_EVALS_PM_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating an AI Evals for Product Managers assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

SCENARIO FOCUS:
The candidate works as a PM or PM-adjacent engineer responsible for evaluating AI features before launch. The task must require the candidate to work with real operational data from an AI system and produce a practical evaluation plan. The task should cover one or more of:
(a) Defining evaluation dimensions and metrics for an AI feature (connecting model metrics to product/business outcomes)
(b) Designing or reviewing test datasets and identifying gaps (coverage, edge cases, sampling bias)
(c) Creating or critiquing human evaluation rubrics (rating scales, rater instructions, reliability)
(d) Setting launch/no-launch quality thresholds with data-backed reasoning
(e) Recommending what to automate vs. what needs human review, with cost/coverage tradeoffs
(f) Interpreting evaluation results and making a product recommendation

WHAT THIS TASK TESTS:
- Practical evaluation design grounded in data (not theoretical knowledge)
- Ability to connect model performance metrics to product outcomes
- Tradeoff reasoning (precision vs recall, quality vs cost, automated vs human eval)
- Understanding of offline vs online evaluation and when each applies
- Clear communication of findings and recommendations for stakeholders

EVAL RUBRIC SIGNALS (what separates strong from weak candidates):
- Frames evaluation around product/business goals, not just model accuracy
- Identifies gaps in test data or evaluation methodology
- Proposes realistic thresholds tied to evidence, not arbitrary numbers
- Understands that different dimensions need different evaluation methods
- Acknowledges limitations (sampling bias, test set drift, proxy metric misalignment)

CRITICAL TASK GENERATION REQUIREMENTS:
- Draw inspiration from the real-world scenarios provided above to create the task
- The task complexity must be appropriate for BASIC proficiency — candidates should be able to complete it within {minutes_range} minutes
- Provide realistic but analyzable data files (eval results, test datasets, rating outputs, system configs)
- The data should contain obvious patterns a BASIC candidate can spot
- Do NOT give away the solution in the starter materials
- Select a different real-world scenario each time to ensure variety in task generation

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the AI product context, the evaluation challenge, and the specific problem the candidate will solve)
2. What will the task look like? (Describe the data files provided, the expected deliverables, and how the task aligns with the BASIC proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_INSTRUCTIONS = """

## GOAL
As a senior AI product manager with 15+ years of experience in AI evaluation frameworks, you are tasked with generating a comprehensive assessment scenario that evaluates candidates' ability to design, critique, and execute evaluation plans for production AI features. The generated task must assess practical evaluation design skills, metric selection, tradeoff reasoning, and stakeholder communication — suitable for presentation to CTOs and technical leadership.

## CRITICAL SUCCESS CRITERIA
The generated task MUST validate the following competencies:
1. **Evaluation Design**: Ability to define meaningful, measurable dimensions for AI product quality tied to business outcomes
2. **Metric Selection**: Choosing appropriate metrics for the AI use case and understanding tradeoffs (precision vs recall, quality vs latency/cost)
3. **Test Data Design**: Understanding what makes a good evaluation dataset — coverage, edge cases, representativeness, avoiding data leakage
4. **Human Evaluation**: Designing rubrics, rating scales, and rater instructions with basic reliability awareness
5. **Threshold Setting**: Data-driven reasoning about launch/no-launch decisions with clear metrics and cutoffs
6. **Offline vs Online Awareness**: Understanding that pre-launch testing and post-launch monitoring serve different purposes
7. **Stakeholder Communication**: Summarizing findings and recommendations clearly for product/engineering leadership

## INSTRUCTIONS

### Nature of the Task
- **Task must present a business problem** where an AI feature is being evaluated before launch, after launch, or during iteration — and the candidate must design or critique the evaluation approach
- **The scenario must provide actual operational data files** that candidates will analyze:
  - Evaluation results (CSV) showing AI system outputs with quality ratings, metrics, or labels
  - System configuration or prompt (TXT/JSON) that the AI feature uses
  - Optionally: test dataset samples, human rating outputs, or A/B test results
- **Candidates should create deliverable documents** (Word/PDF/Markdown) containing:
  - Evaluation dimensions tied to product goals
  - Metric definitions with rationale
  - Test data assessment or design recommendations
  - Quality thresholds with data-backed reasoning
  - Evaluation method recommendations (automated vs human, offline vs online)
  - Brief stakeholder summary with launch recommendation
- **CRITICAL**: Include ONLY the raw data files that candidates need to analyze — NO templates, NO example frameworks, NO explanatory materials
- **DO NOT GIVE AWAY THE SOLUTION** in the starter materials
- **Time Constraint**: The task must be designed so candidates can complete it within {minutes_range} minutes

**Your job**: Generate ONLY the exact data files needed for the scenario. Typically 2-4 files (CSV data, config/prompt, optionally rubric or test set). **DO NOT generate any additional files not specified.**

### Data File Requirements

**Primary data file (CSV, 40-80 rows)**:
- Should contain AI system outputs with quality indicators, labels, or ratings
- Must contain clear patterns: e.g., certain categories performing worse, specific failure modes clustering, metric correlations
- Should show a system that is mediocre (not terrible) — making the launch decision genuinely require reasoning
- Include enough variety to surface evaluation gaps

**System config or prompt file (TXT or JSON)**:
- A realistic configuration for the AI feature
- Should contain identifiable issues or suboptimal settings
- Should be small enough to review in 2-3 minutes

**Optional additional files**:
- Human rating results, test dataset samples, or A/B test summaries
- Only if the scenario requires them — keep the total file count to 2-4

### Proficiency Level Alignment
- **BASIC level expectations**:
  - Candidate can identify obvious patterns in evaluation data
  - Candidate can define reasonable evaluation dimensions and metrics
  - Candidate can propose a sensible evaluation plan with basic quality controls
  - Candidate can set thresholds with some data backing, even if statistical reasoning is simple
  - Candidate can distinguish between automated and human evaluation needs
  - Candidate does NOT need to design statistically rigorous experiments or implement evaluation pipelines
- **The question must NOT include hints** — hints will be provided separately in the "hints" field
- Ensure the scenario reflects realistic AI product challenges

### AI and External Resource Policy
- **Candidates are ENCOURAGED to use AI tools** including ChatGPT, Claude, LLM playgrounds, and any external resources
- **Tasks are designed to assess** genuine evaluation reasoning, pattern recognition in data, and practical framework design
- **Complexity should require** understanding of evaluation tradeoffs beyond what a simple prompt to an LLM would produce
- Evaluation focuses on the quality of reasoning, evidence usage, and practical applicability — not memorization

### Task Generation Requirements
Based on the provided `real_world_task_scenarios`, create a task that:
- **GENERATES DATA FILES** matching the AI evaluation context from the scenarios
- **INCLUDES ONLY RAW DATA FILES** in the `code_files` output — NO templates, NO examples, NO explanatory guides
- Creates realistic operational data demonstrating:
  - Clear but not trivial quality patterns
  - Identifiable gaps in evaluation methodology or test coverage
  - Enough ambiguity to make launch decisions require reasoning
- Requires candidates to:
  - Analyze evaluation data for patterns and quality issues
  - Define evaluation dimensions connected to product goals
  - Design or critique test data and evaluation methodology
  - Set data-informed quality thresholds
  - Recommend evaluation methods (automated vs human, offline vs online)
  - Prepare a brief stakeholder summary with a launch recommendation
- Matches BASIC proficiency level while assuming AI tool usage
- **Time constraints**: Completable within {minutes_range} minutes
- Emphasizes practical reasoning over theoretical perfection

---


## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task Name — MUST be in format <verb><subject> and maximum 50 characters. Example: 'Evaluate Chatbot Launch Readiness'",
   "question": "A short description of the task scenario including the specific ask from the candidate — what evaluation needs to be designed or critiqued and why?",
   "code_files": {{
      "data/[primary_data_file].csv": "[ACTUAL CSV content with 40-80 rows of evaluation data showing realistic patterns]",
      "config/[config_or_prompt_file]": "[ACTUAL configuration or prompt content with identifiable issues]",
      "[optional_additional_file]": "[Additional data file ONLY if the scenario requires it]"
   }},
   "outcomes": "A very short description (1-2 sentences) of what tangible deliverables should exist if the task is completed well, without revealing the solution.",
   "short_overview": "Bullet-point list in simple language describing: (1) the business problem, (2) the evaluation design goal, and (3) the expected outcome.",
   "pre_requisites": "List bullet-points required for knowledge and tools for the task:\\n- Access to spreadsheet software or Python/pandas for CSV analysis\\n- Understanding of AI evaluation frameworks and metrics\\n- Basic knowledge of AI product patterns (chatbots, summarization, classification, etc.)\\n- Documentation tools (Word/Markdown editor)\\n- Ability to identify patterns in tabular data\\n- Critical thinking for tradeoff analysis",
   "answer": "Only a high-level solution approach — identify key patterns in data, define dimensions tied to product goals, propose evaluation methodology, set thresholds based on evidence, map automated vs human evaluation methods.",
   "hints": "A single guiding hint that nudges toward good evaluation practices without revealing the solution.",
   "definitions": {{
      "offline_evaluation": "Testing an AI system against a fixed labeled dataset before deployment — catches known failure modes but cannot capture all production scenarios",
      "online_evaluation": "Monitoring an AI system's performance on live traffic after deployment — captures real-world edge cases but requires careful metric design",
      "precision": "The proportion of positive predictions that are actually correct — high precision means few false positives",
      "recall": "The proportion of actual positive cases that are correctly identified — high recall means few false negatives",
      "ground_truth": "The accepted correct answer used to evaluate model outputs — may come from human labels, domain experts, or business rules",
      "inter_rater_reliability": "A measure of agreement between multiple human annotators labeling the same data — high agreement suggests clear and consistent labeling guidelines"
   }}
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, in format `<verb> <subject>`, maximum 50 characters
3. **code_files** must include ONLY the raw data files explicitly required by the scenario (2-4 files)
4. **NO README.md**, NO templates, NO examples, NO explanatory guides in code_files
5. **Primary CSV** should have 40-80 rows with realistic patterns
6. **outcomes** and **short_overview** must be concise descriptions in simple language
7. **hints** must be a single line; **definitions** must include evaluation-specific terms
8. **Task must be completable within the allocated time** for BASIC proficiency level
9. **NO solutions revealed** in starter materials or data files
10. **Tradeoff reasoning and evidence-based thinking** must be required to solve the task
"""

PROMPT_REGISTRY = {
    "AI Evals for Product Managers (BASIC)": [
        PROMPT_CONTEXT,
        PROMPT_AI_EVALS_PM_INPUT_AND_ASK,
        PROMPT_INSTRUCTIONS,
    ]
}
