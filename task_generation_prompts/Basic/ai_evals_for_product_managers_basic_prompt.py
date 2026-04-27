PROMPT_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_AI_EVALS_PM_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating an AI Evals for Product Managers assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

SCENARIO FOCUS:
The candidate is a PM reviewing the pre-launch evaluation results for an AI classification or routing tool at a logistics, e-commerce, or SaaS company. The eval shows strong headline accuracy on a test set that is narrow in coverage — skewed toward common, clean cases with almost no representation of edge-case or high-risk scenarios. Ops or engineering wants to launch soon. The candidate must:
(a) Make a launch decision — full launch, limited launch, or hold — with a clear rationale grounded in the eval data
(b) Identify two or more specific scenario types missing from the test set that must be covered before broader rollout
(c) Optionally propose one concrete next step: a targeted data collection plan, a limited rollout design, or a specific metric threshold to meet first

WHAT THIS TASK TESTS:
- Ability to read an eval summary and identify what the numbers are NOT telling you
- Understanding that headline accuracy can mask poor coverage of important edge cases
- Practical launch judgment: when is 92% good enough, and when is it not?
- Test set design thinking: what scenarios matter most for the product's real-world risk profile
- Communication of a PM recommendation with evidence — not just gut feel

EVAL RUBRIC SIGNALS (what separates strong from weak candidates):
- Identifies that high accuracy on an unrepresentative sample is not the same as production readiness
- Links the missing scenario types to real business or user risk (e.g. customs mis-routing causes compliance issues, multi-issue emails get dropped or mis-labeled)
- Makes a specific, defensible launch decision — not just "it depends"
- Proposes missing scenarios that are grounded in the actual product context, not generic
- Shows awareness that launching to 100% of agents with a narrow test set is a different risk than a limited rollout to a subset

CRITICAL TASK GENERATION REQUIREMENTS:
- Draw inspiration from ONE of the real-world scenarios provided above to set the business domain and AI tool context
- The task must be completable within {minutes_range} minutes for a BASIC proficiency PM
- The data files must contain obvious patterns a BASIC candidate can spot: a clear skew in email type distribution, a visible drop in accuracy for underrepresented categories
- Do NOT give away the decision or the missing scenarios in the data — the candidate must reason to them
- Select a different real-world scenario each time to ensure variety in domain (logistics, fintech, healthcare, e-commerce, HR, edtech, media)

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, the AI tool, the eval situation, and the specific launch decision the candidate must make)
2. What will the task look like? (Describe the data files provided, what patterns they contain, and the expected deliverable format at BASIC proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_INSTRUCTIONS = """

## GOAL
As a senior AI product management expert, you are generating a realistic work-item assessment that tests whether a PM candidate can read an evaluation summary, identify coverage gaps, and make a defensible launch decision for an AI classification or routing system. The task must feel like a real pre-launch review — the kind a PM would face in a sprint review or launch readiness meeting.

## CRITICAL SUCCESS CRITERIA
The generated task MUST assess the following competencies:
1. **Eval Result Interpretation**: Reading an accuracy/latency summary and identifying what the numbers obscure
2. **Coverage Gap Analysis**: Recognising that a test set skewed to easy cases does not validate production readiness
3. **Launch Decision Reasoning**: Making a specific, evidence-backed launch recommendation (full / limited / hold)
4. **Test Set Design**: Naming concrete missing scenario types tied to real product risk, not generic categories
5. **PM Communication**: Expressing a recommendation concisely with a rationale — not just listing observations

## INSTRUCTIONS

### Nature of the Task
- The task presents a realistic pre-launch eval situation where an AI tool has been tested internally and results look good on paper, but the test set is narrow
- Provide two data files as starter materials: an eval summary showing per-category accuracy and a test set composition breakdown showing the distribution skew
- The candidate produces a short written recommendation (3–5 bullet points or a brief paragraph): launch decision + gap analysis + one next step
- Do NOT provide a rubric, hints, or any framing that signals what the right answer is
- The data must require the candidate to compute or notice the skew themselves — do not label the distribution as "biased" or "unrepresentative"

### Data File Requirements

**data/eval_summary.csv** (~30 rows):
- Columns: email_id (or case_id), true_label, predicted_label, correct (true/false), latency_ms, case_type, word_count
- case_type values: use 4 types — e.g. `standard_domestic`, `long_thread`, `multi_issue`, `international_customs` (adapt names to the chosen domain)
- Distribution: ~80% of rows should be the dominant easy type; the other three types should have 5–10 rows each
- Overall accuracy: ~91–93% — driven almost entirely by the dominant type performing well (~96–97%)
- The minority types should show meaningfully lower accuracy (75–85%) — but because there are so few rows, the headline number stays high
- Latency: mostly 600–900ms, a few spikes to 1400–1800ms in the edge-case types
- Do NOT include a summary row or any aggregation — the candidate must compute it

**data/test_set_composition.csv** (~8 rows):
- Columns: case_type, count, percentage, source
- Makes the distribution skew explicit in numbers — the candidate should be able to see at a glance that 3 of the 4 types are underrepresented
- Source column: e.g. `production_sample`, `manual_collection`, `synthetic` — the minority types should show `manual_collection` or `synthetic`, signalling they were not drawn from real production traffic

### Proficiency Level Alignment
- **BASIC level expectations**:
  - Can read a CSV and compute a simple per-group accuracy breakdown
  - Can identify obvious distribution skew from a composition table
  - Can make a launch decision with a short rationale — does not need to cite statistical significance
  - Can name 2 missing scenario types grounded in the domain — does not need an exhaustive taxonomy
  - Does NOT need to design a sampling strategy, compute confidence intervals, or propose an A/B test
- The scenario should have enough ambiguity that the launch decision requires judgment, not just rule-following
- The correct answer should be "limited launch" or "hold" — not an obvious "don't ship" based on terrible numbers

### AI and External Resource Policy
- Candidates are ENCOURAGED to use AI tools, spreadsheets, and any external resources
- The task assesses judgment and evidence-based reasoning — not memorisation or recall
- Complexity should require genuine evaluation reasoning beyond what a single LLM prompt would produce

### Task Generation Requirements
Based on the provided `real_world_task_scenarios`, create a task that:
- Sets a specific business domain (logistics, fintech, e-commerce, HR, healthcare, edtech, media) drawn from the scenario
- Names the AI tool concretely (e.g. "ShipRoute AI", "ClaimSorter", "TicketTagger") — not a generic "AI classifier"
- Generates `eval_summary.csv` with the accuracy/latency/case_type breakdown described above
- Generates `test_set_composition.csv` with the distribution and source breakdown
- Frames the task as a realistic work item: a Slack message from an Ops lead, a launch readiness doc stub, or a sprint review agenda item — not a homework problem
- Matches BASIC proficiency: the patterns in the data are visible, not hidden behind complex statistics
- Is completable within {minutes_range} minutes assuming the candidate uses a spreadsheet or Python to compute group-level accuracy

---

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task Name — format: <verb> <subject>, maximum 50 characters. Example: 'Review AI Router Pre-Launch Eval'",
   "question": "A short paragraph framing the work item — who is asking, what the AI tool does, what the eval showed at headline level, and what decision needs to be made. Should feel like a real message or brief, not a test prompt.",
   "code_files": {{
      "data/eval_summary.csv": "[ACTUAL CSV content — ~30 rows — with columns: case_id, true_label, predicted_label, correct, latency_ms, case_type, word_count. Skewed distribution with lower accuracy on minority types.]",
      "data/test_set_composition.csv": "[ACTUAL CSV content — ~8 rows — with columns: case_type, count, percentage, source. Makes the distribution skew and data provenance explicit.]"
   }},
   "outcomes": "A 2–3 sentence description of what a good submission looks like: a specific launch recommendation with a rationale grounded in the data, two or more named missing scenario types tied to real risk, and a concrete next step — without revealing the answer.",
   "short_overview": "Bullet-point list in plain language: (1) the business situation and AI tool, (2) what the eval data shows and what it hides, (3) what the candidate must deliver.",
   "pre_requisites": "Bullet-point list:\\n- Ability to read and summarise tabular data (spreadsheet or Python/pandas)\\n- Basic understanding of accuracy as a metric and its limitations\\n- Familiarity with offline evaluation concepts for AI classification systems\\n- Understanding of what a test set is and why its composition matters\\n- Ability to write a concise, evidence-backed product recommendation",
   "answer": "High-level solution: compute per-group accuracy from eval_summary.csv — the minority case types (multi-issue, international, long-thread) show 75–85% accuracy but represent <15% of the test set, so they barely affect the headline. Recommend limited launch or hold. Name the underrepresented types as the gap. Propose one next step: targeted data collection for the minority types, or a shadow-mode rollout to surface real production distribution before full launch.",
   "hints": "Start by grouping eval_summary.csv by case_type and computing accuracy per group — the headline number tells a different story than the per-group breakdown.",
   "definitions": {{
      "headline_accuracy": "The overall percentage of correct predictions across the entire test set — can be misleadingly high if the test set is dominated by easy cases",
      "test_set_coverage": "The degree to which a test set represents the full range of real-world inputs the system will encounter in production",
      "limited_launch": "Deploying a system to a small subset of users or traffic to validate performance on real inputs before full rollout",
      "shadow_mode": "Running a new model on live traffic without surfacing its outputs to users — used to measure real-world performance without production risk",
      "case_type_skew": "An imbalance in a test set where certain input types are heavily overrepresented, making overall metrics unreliable for underrepresented types",
      "latency_budget": "The maximum acceptable response time for a system in production — evaluated alongside accuracy as a launch gate criterion"
   }}
}}

## CRITICAL REMINDERS
1. Output must be valid JSON only — no markdown, no explanations, no code fences
2. name must be short, verb-first, maximum 50 characters
3. code_files must contain EXACTLY 2 files: eval_summary.csv and test_set_composition.csv
4. Do NOT include a README, hints file, rubric, or any explanatory materials in code_files
5. eval_summary.csv must have ~30 rows with a clear but non-obvious accuracy skew by case_type
6. The question must read like a real work item, not a test prompt
7. The launch decision must require judgment — not be obvious from terrible numbers
8. outcomes and short_overview must be concise and must NOT reveal the answer
9. All CSV content must be actual data rows, not placeholders or descriptions
"""

PROMPT_REGISTRY = {
    "AI Evals for Product Managers (BASIC)": [
        PROMPT_CONTEXT,
        PROMPT_AI_EVALS_PM_BASIC_INPUT_AND_ASK,
        PROMPT_INSTRUCTIONS,
    ]
}
