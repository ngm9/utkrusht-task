PROMPT_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_VOICE_AGENT_EVAL_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Voice Agent Evaluation Framework assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

SCENARIO FOCUS:
The candidate's team is shipping a voice AI agent that conducts candidate screening interviews. The task must require the candidate to design an evaluation framework covering:
(a) What 5-7 dimensions to measure (e.g., response capture accuracy, turn-taking, summary quality, recommendation calibration, safety/bias, latency, candidate experience)
(b) How to label 100 sample calls — labeling scheme, annotator selection, inter-rater reliability, disagreement resolution
(c) A "ship / don't ship" quality threshold — what metrics, what cutoffs, what evidence supports the decision
(d) What to automate (LLM-as-judge, regex checks, latency monitoring) vs. what requires human review (subjective quality, edge cases, bias detection)

WHAT THIS TASK TESTS:
- Hands-on evaluation design (not theoretical knowledge)
- Tradeoff reasoning (cost vs. coverage, speed vs. accuracy, automation vs. human judgment)
- AI systems thinking (understanding how offline evals relate to online monitoring, how ground truth is established, how evaluation cost scales)

EVAL RUBRIC SIGNALS (what separates strong from weak candidates):
- Distinguishes offline evals (pre-launch on labeled data) vs. online evals (post-launch monitoring with live traffic)
- Defines what "ground truth" means for each dimension (e.g., hiring manager override as ground truth for recommendation quality)
- Acknowledges evaluation cost and proposes practical tradeoffs (not everything needs human review)
- Shows awareness that the same model generating outputs cannot reliably judge its own quality without careful design

CRITICAL TASK GENERATION REQUIREMENTS:
- Draw inspiration from the real-world scenarios provided above to create the task
- The task complexity must be appropriate for BASIC proficiency — candidates should be able to complete it within {minutes_range} minutes
- Provide realistic but analyzable data files (call logs with clear failure patterns, a flawed system prompt, a config with suboptimal parameters)
- The data should contain obvious patterns a BASIC candidate can spot (e.g., high disagreement rate on certain failure types, correlation between config settings and failures)
- Do NOT give away the solution in the starter materials
- Select a different real-world scenario each time to ensure variety in task generation

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the voice agent context, the evaluation challenge, and the specific problem the candidate will solve)
2. What will the task look like? (Describe the data files provided, the expected deliverables, and how the evaluation framework design aligns with the BASIC proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_INSTRUCTIONS = """

## GOAL
As a senior AI product manager expert in AI evaluation frameworks and voice agent systems, you are tasked with generating a comprehensive assessment scenario that evaluates candidates' ability to design, reason about, and implement evaluation frameworks for production AI systems. The generated task must assess practical evaluation design skills, tradeoff reasoning, and AI systems thinking — suitable for presentation to CTOs and technical leadership.

## CRITICAL SUCCESS CRITERIA
The generated task MUST validate the following competencies:
1. **Evaluation Design**: Ability to define meaningful, measurable dimensions for AI system quality
2. **Labeling & Annotation**: Understanding of how to create ground truth data — annotator selection, labeling schemes, inter-rater reliability
3. **Threshold Setting**: Data-driven reasoning about ship/no-ship decisions with clear metrics and cutoffs
4. **Automation vs. Human Review**: Practical judgment about what can be automated reliably vs. what needs human oversight
5. **Offline vs. Online Evaluation**: Awareness that pre-launch testing and post-launch monitoring serve different purposes
6. **Cost-Aware Thinking**: Recognition that evaluation has real costs and proposing practical tradeoffs
7. **AI Literacy**: Understanding of LLM behavior, failure modes, and limitations relevant to voice agents

## INSTRUCTIONS

### Nature of the Task
- **Task must present a business problem** where a voice AI interview agent is about to ship or has recently launched, and the candidate must design the evaluation framework
- **The scenario must provide actual operational data files** that candidates will analyze to inform their framework design:
  - Call logs (CSV) showing real patterns — success/failure rates, hiring manager agreement/disagreement, failure categories
  - The current system prompt (TXT) with embedded issues the candidate should identify
  - Agent configuration (JSON) with parameters that correlate with quality issues
- **Candidates should create deliverable documents** (Word/PDF/Markdown) containing:
  - 5-7 evaluation dimensions with clear definitions and measurement methods
  - A labeling scheme for 100 sample calls (labels, annotators, process, disagreement handling)
  - Ship/don't-ship threshold with specific metrics, cutoffs, and supporting rationale
  - Automation vs. human-review matrix mapping each dimension to its evaluation method
  - Brief executive summary with the go/no-go recommendation
- **CRITICAL**: Include ONLY the raw data files that candidates need to analyze — NO templates, NO example frameworks, NO explanatory materials
- **DO NOT GIVE AWAY THE SOLUTION** in the starter materials
- The task must require candidates to analyze the data, identify patterns, and use evidence to support their framework design
- **Time Constraint**: The task must be designed so candidates can complete it within {minutes_range} minutes

**Your job**: Generate ONLY the exact data files described above (call logs CSV, system prompt TXT, agent config JSON). **DO NOT generate any additional files not specified.**

### Data File Requirements

**call_logs.csv** (100 rows):
- Columns: call_id, candidate_id, duration_sec, agent_version, transcript_snippet, agent_summary, agent_recommendation (HIRE/NO_HIRE/UNSURE), hiring_manager_override (AGREE/DISAGREE/PENDING), failure_reason (nullable: INTERRUPTION, MISSED_RESPONSE, OFF_TOPIC, HALLUCINATED_SKILL, null)
- Must contain clear patterns: e.g., INTERRUPTION failures correlate with short duration, HALLUCINATED_SKILL cases have high DISAGREE rate, certain agent_version performs worse
- ~60-65% AGREE rate overall (system is mediocre, not terrible) to make the ship/don't-ship decision genuinely ambiguous
- Include a mix of null failure_reason (successful calls) and specific failure types at realistic frequencies

**interview_system_prompt.txt**:
- A realistic but flawed system prompt for a voice interview agent
- Should contain identifiable issues: vague summarization instructions, no explicit handling of candidate silence/hesitation, missing guardrails for off-topic responses, overly aggressive recommendation criteria
- Should be 200-400 words — realistic length for a BASIC candidate to read and critique

**agent_config.json**:
- Include: temperature, max_tokens, turn_taking_timeout_ms, silence_threshold_ms, max_interview_duration_sec, evaluation_rubric_weights, model_version
- Some values should be suboptimal (e.g., high temperature causing inconsistent summaries, short silence threshold causing interruptions)
- Should be small enough to review in 2-3 minutes

### Proficiency Level Alignment
- **BASIC level expectations**:
  - Candidate can identify obvious patterns in the call logs (high-frequency failure types, agreement rates)
  - Candidate can define reasonable evaluation dimensions even if not perfectly comprehensive
  - Candidate can propose a sensible labeling scheme with basic quality controls
  - Candidate can set a threshold with some data backing, even if the statistical reasoning is simple
  - Candidate can distinguish at least some automated vs. human-review dimensions
  - Candidate does NOT need to design statistically rigorous experiments or build automated pipelines
- **The question must NOT include hints** — hints will be provided separately in the "hints" field
- Ensure the scenario reflects realistic voice AI challenges

### AI and External Resource Policy
- **Candidates are ENCOURAGED to use AI tools** including ChatGPT, Claude, LLM playgrounds, and any external resources
- **Tasks are designed to assess** genuine evaluation reasoning, pattern recognition in data, and practical framework design
- **Complexity should require** understanding of evaluation tradeoffs beyond what a simple prompt to an LLM would produce
- Evaluation focuses on the quality of reasoning, evidence usage, and practical applicability — not memorization

### Task Generation Requirements
Based on the provided `real_world_task_scenarios`, create a task that:
- **GENERATES DATA FILES** matching the voice agent evaluation context
- **INCLUDES ONLY RAW DATA FILES** in the `code_files` output — NO templates, NO examples, NO explanatory guides
- **CRITICAL**: Generate ONLY the 3 files specified (call_logs.csv, interview_system_prompt.txt, agent_config.json). Do NOT create additional files.
- Creates realistic operational data demonstrating:
  - Clear but not trivial failure patterns in the call logs
  - Identifiable prompt issues in the system prompt
  - Correlations between config parameters and failure types
  - Enough ambiguity to make the ship/don't-ship decision require reasoning
- Requires candidates to:
  - Analyze call log data for patterns and failure frequencies
  - Define evaluation dimensions grounded in the data they observe
  - Design a practical labeling scheme with annotator guidance
  - Set a data-informed quality threshold
  - Map dimensions to automated vs. human evaluation methods
  - Prepare a brief executive summary with a go/no-go recommendation
- Matches BASIC proficiency level while assuming AI tool usage
- **Time constraints**: Completable within {minutes_range} minutes
- Emphasizes practical reasoning over theoretical perfection

---


## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task Name — MUST be in format <verb><subject> and maximum 50 characters. Example: 'Design Voice Agent Eval Framework'",
   "question": "A short description of the task scenario including the specific ask from the candidate — what evaluation framework needs to be designed and why?",
   "code_files": {{
      "data/call_logs.csv": "[ACTUAL CSV content with 100 rows of call log data showing realistic patterns — call_id, candidate_id, duration_sec, agent_version, transcript_snippet, agent_summary, agent_recommendation, hiring_manager_override, failure_reason]",
      "prompts/interview_system_prompt.txt": "[ACTUAL system prompt content — 200-400 words — with embedded flaws for the candidate to identify: vague instructions, missing guardrails, aggressive thresholds]",
      "config/agent_config.json": "[ACTUAL JSON config with temperature, max_tokens, turn_taking_timeout_ms, silence_threshold_ms, max_interview_duration_sec, evaluation_rubric_weights, model_version — some values suboptimal]"
   }},
   "outcomes": "A very short description (1-2 sentences) of what tangible deliverables should exist if the task is completed well, without revealing the solution. For example: a structured evaluation framework with defined dimensions, a labeling methodology, data-backed quality thresholds, and an automation vs. human-review breakdown tied to a go/no-go recommendation.",
   "short_overview": "Bullet-point list in simple language describing: (1) the business problem (voice agent quality issues before launch), (2) the evaluation design goal (framework covering dimensions, labeling, thresholds, automation), and (3) the expected outcome (evidence-backed ship/don't-ship recommendation).",
   "pre_requisites": "List bullet-points required for knowledge and tools for the task:\\n- Access to spreadsheet software or Python/pandas for CSV analysis\\n- Understanding of evaluation frameworks and metrics for AI systems\\n- Basic knowledge of voice AI / conversational AI concepts\\n- Documentation tools (Word/Markdown editor)\\n- Ability to identify patterns in tabular data\\n- Critical thinking for tradeoff analysis (cost vs. coverage, automation vs. human review)",
   "answer": "Only a high-level solution approach — identify key failure patterns in data, define dimensions anchored to observed issues, propose labeling with inter-rater reliability checks, set thresholds based on agreement rates and failure frequencies, map automatable dimensions (latency, format compliance) vs. human-required (summary quality, bias detection).",
   "hints": "Start by computing the hiring manager agreement rate per failure_reason category — the dimensions where humans disagree most with the agent are where your evaluation framework needs the most attention.",
   "definitions": {{
      "ground_truth": "The accepted correct answer used to evaluate model outputs — in this context, the hiring manager's assessment serves as ground truth for recommendation quality",
      "inter_rater_reliability": "A measure of agreement between multiple human annotators labeling the same data — high agreement suggests the labeling scheme is clear and consistent",
      "offline_evaluation": "Testing an AI system against a fixed labeled dataset before deployment — catches known failure modes but cannot capture all production scenarios",
      "online_evaluation": "Monitoring an AI system's performance on live traffic after deployment — captures real-world edge cases but requires careful metric design",
      "LLM_as_judge": "Using a language model to automatically evaluate another model's outputs — cost-effective but may share blind spots with the model being evaluated",
      "ship_threshold": "The minimum quality bar an AI system must meet before being approved for production deployment — typically defined as a set of metrics each exceeding specific cutoff values"
   }}
}}

## CRITICAL REMINDERS
1. **Output must be valid JSON only** — no markdown, no explanations, no code fences
2. **name** must be short, descriptive, in format `<verb> <subject>`, maximum 50 characters
3. **code_files** must include EXACTLY 3 files: call_logs.csv, interview_system_prompt.txt, agent_config.json
4. **NO README.md**, NO templates, NO examples, NO explanatory guides in code_files
5. **call_logs.csv** must have exactly 100 data rows with realistic patterns and ~60-65% overall agreement rate
6. **outcomes** and **short_overview** must be concise descriptions in simple language
7. **hints** must be a single line; **definitions** must include evaluation-specific terms
8. **Task must be completable within the allocated time** for BASIC proficiency level
9. **NO solutions revealed** in starter materials or data files
10. **Tradeoff reasoning and evidence-based thinking** must be required to solve the task
"""

PROMPT_REGISTRY = {
    "Voice Agent Evaluation (BASIC)": [
        PROMPT_CONTEXT,
        PROMPT_VOICE_AGENT_EVAL_INPUT_AND_ASK,
        PROMPT_INSTRUCTIONS,
    ]
}
