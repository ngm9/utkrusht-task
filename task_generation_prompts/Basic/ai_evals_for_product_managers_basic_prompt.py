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
The candidate is a PM reviewing the pre-launch evaluation **package** for an AI feature — the specific feature, AI capability (classification, routing, extraction, summarisation, generation, Q&A, etc.), product surface, and business domain MUST come from the chosen real-world scenario above. Do not default to any one domain or capability — let the scenario drive it. The package they receive must include the artefacts a real PM would have on hand to actually diagnose what the eval is and isn't telling them — presented as a LEAN 4-FILE package, not a sprawling folder: a single orientation document that combines the system overview + headline results + test-set composition table, the production system prompt, the evals/judge prompt that produced the scores, and a traces file with real input → model output → judge verdict rows. The eval shows strong headline accuracy / quality score on a test set that is narrow in coverage — skewed toward common, clean cases with almost no representation of edge-case or high-risk scenarios. Ops or engineering wants to launch soon. The candidate must:
(a) Make a launch decision — full launch, limited launch, or hold — with a clear rationale grounded in the eval data **and the prompts/traces**
(b) Identify two or more specific scenario types missing from the test set that must be covered before broader rollout, citing evidence from the traces or composition table
(c) Optionally propose one concrete next step: a targeted data collection plan, a limited rollout design, a tightened judge rubric, a system-prompt fix, or a specific metric threshold to meet first

WHAT THIS TASK TESTS:
- Ability to read an eval summary and identify what the numbers are NOT telling you
- Ability to read a system prompt and a judge prompt critically — spotting under-specified instructions, missing checks, or loaded scoring criteria
- Ability to read a traces sample and link concrete failures back to either prompt design or test-set coverage
- Understanding that headline accuracy can mask poor coverage of important edge cases
- Practical launch judgment: when is 92% good enough, and when is it not?
- Test set design thinking: what scenarios matter most for the product's real-world risk profile
- Communication of a PM recommendation with evidence — not just gut feel

EVAL RUBRIC SIGNALS (what separates strong from weak candidates):
- Identifies that high accuracy/quality on an unrepresentative sample is not the same as production readiness
- Cites specific lines or phrasing from the system prompt or judge prompt as evidence (e.g., "the judge prompt only checks output format — it never asks whether the content was sound", "the system prompt assumes one intent per input")
- Points to specific traces that illustrate the failure mode — not just aggregate stats
- Links the missing scenario types to real business or user risk in the chosen domain (concrete consequences, not generic phrasing)
- Makes a specific, defensible launch decision — not just "it depends"
- Proposes missing scenarios that are grounded in the actual product context of the chosen scenario, not generic
- Shows awareness that launching to 100% of users/traffic with a narrow test set is a different risk than a limited rollout to a subset

CRITICAL TASK GENERATION REQUIREMENTS:
- Draw inspiration from ONE of the real-world scenarios provided above to set the business domain and AI tool context — the scenario you pick is the source of truth for the feature, the AI capability, the inputs, the outputs, and the case_type vocabulary. Do not substitute or default to a different domain.
- Across multiple generations, vary which scenario you pick so the resulting tasks span different domains and AI capabilities — never bias toward any one industry, AI capability, or example tool name.
- The task must be completable within {minutes_range} minutes for a BASIC proficiency PM
- The data files must contain obvious patterns a BASIC candidate can spot: a clear skew in case-type distribution, a visible drop in quality for underrepresented categories, and at least 2-3 traces in the underrepresented categories that visibly illustrate the failure mode
- The system prompt and judge prompt must contain at least one realistic, plausibly-overlooked weakness each (e.g., system prompt assumes a single intent, judge prompt scores only label/format match and not reasoning quality) — without being cartoonishly broken
- Do NOT give away the decision or the missing scenarios in the data — the candidate must reason to them
- Do NOT label any document as "flawed" or annotate the weakness — it should look like a real internal artefact

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, the AI tool, the eval situation, and the specific launch decision the candidate must make)
2. What will the task look like? (Describe the FOUR files in the eval package — system_overview.md (which absorbs the headline results and the test-set composition table), system_prompt.md, judge_prompt.md, and traces.csv — what each contains, where the patterns or weaknesses sit, and the expected deliverable format at BASIC proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_INSTRUCTIONS = """

## GOAL
As a senior AI product management expert, you are generating a realistic work-item assessment that tests whether a PM candidate can read an evaluation summary, identify coverage gaps, and make a defensible launch decision for an AI feature. The specific feature, AI capability (classification, routing, extraction, summarisation, generation, Q&A, etc.), product surface, and business domain all come from the chosen real-world scenario — do not default to any one pattern. The task must feel like a real pre-launch review — the kind a PM would face in a sprint review or launch readiness meeting.

## CRITICAL SUCCESS CRITERIA
The generated task MUST assess the following competencies:
1. **Eval Result Interpretation**: Reading an accuracy/latency summary and identifying what the numbers obscure
2. **Prompt Critique**: Reading the model's system prompt and the LLM-judge prompt and spotting under-specified instructions, missing checks, or loaded scoring criteria
3. **Trace Inspection**: Reading actual input → output → judge-verdict rows and linking specific failures to either prompt design or test-set coverage
4. **Coverage Gap Analysis**: Recognising that a test set skewed to easy cases does not validate production readiness
5. **Launch Decision Reasoning**: Making a specific, evidence-backed launch recommendation (full / limited / hold)
6. **Test Set Design**: Naming concrete missing scenario types tied to real product risk, not generic categories
7. **PM Communication**: Expressing a recommendation concisely with a rationale — not just listing observations

## INSTRUCTIONS

### Nature of the Task
- The task presents a realistic pre-launch eval situation where an AI tool has been tested internally and results look good on paper, but the test set is narrow and the prompts/judge have plausible-but-overlooked weaknesses
- Provide a LEAN 4-FILE eval package as starter materials: a **system overview** document (which orients the reader and ALSO contains the headline results section and the test-set composition table inline), the model's **system prompt**, the **evals/judge prompt**, and a **traces file** with real input → model output → judge verdict rows
- The candidate answers the lettered questions in the work item directly — a short concise response per question, with evidence from the prompts and traces. The asks themselves live in the question field as explicit a) / b) / c) prompts; the candidate replies to those, not to a generic "send back N bullets" instruction.
- Do NOT provide a rubric, hints, or any framing that signals what the right answer is
- Do NOT annotate the prompts or traces with "this is the problem" comments — they should read like real internal artefacts
- The system overview must orient the candidate to the feature and the eval setup WITHOUT flagging any of the weaknesses — it should read like a neutral architecture/onboarding doc someone wrote when v1 shipped, with the headline numbers and the composition table presented matter-of-factly
- The data must require the candidate to compute or notice the skew themselves — do not label the distribution as "biased" or "unrepresentative" anywhere in the overview
- The total row count in `traces.csv` MUST equal the sum of `count` values in the composition table inside the overview AND the "Total evaluated cases" figure in the headline results section. These three numbers must match exactly — internal inconsistency between them is a defect.

### Data Realism Principle
Each file must match the kind of artefact a PM would actually receive in real production. For this task, we intentionally keep the traces file SMALL so the candidate can read every row in a few minutes — but every individual row must be deeply realistic, as if pulled verbatim from production traffic:
- **traces.csv (row-per-event file)**: keep this LEAN — aim for 20–30 rows total. Do NOT generate 100+ rows; a smaller, hand-quality sample is the explicit design choice for this assessment so the candidate can read each trace carefully without drowning. The realism budget must go into the CONTENT of each row, not the row count. Every `input_text` must read like a real verbatim message from a real user in the chosen domain — concrete names, IDs, dates, product/service references, natural phrasing variation, occasional realistic typos. Templated or placeholder-y inputs are a defect even at 20 rows.
- **System prompt and judge prompt**: these are where you spend your realism budget — they must read like real production artefacts (full multi-section prompts, label definitions, scoring anchors, examples). Do NOT shorten the prompts to compensate for the small trace count — the prompts must remain rich and realistic.
- **Aggregation/summary tables** (composition breakdowns, per-category counts): use only as many rows as the categories or buckets require. A 4-category breakdown has 4 rows. Do not pad summaries with synthetic categories.
- The trade-off is explicit: smaller traces file, maximally realistic input prompt / judge prompt / per-row content.

### Data File Requirements

The package contains EXACTLY FOUR files: three prose documents under `docs/` and one data file under `data/`. Each must look like a real internal artefact — no annotations, no flags, no "this is the issue" comments.

**docs/system_overview.md** — a single combined orientation document that absorbs the headline summary and the composition table. This is the candidate's FIRST stop: open it, understand the system, see the headline numbers, see the composition skew, then go read the prompts and traces.
- Realistic length: 600–900 words, written as a neutral architecture / onboarding note
- MUST contain these sections, in order, using clear markdown headings:
  - **Feature** — one paragraph: what the AI tool is named, what product surface it lives on, who calls it, what business problem it solves
  - **Inputs** — what the model sees on each call (e.g., raw email body + sender metadata; or customer question + product context; or clinician visit notes), plus any pre-processing the calling system applies before the model sees it
  - **Outputs** — what the model returns (label set for classification; output format for generation/summary), plus any post-processing the calling system applies before the user sees it
  - **Eval setup** — a 4–6 line description of how this eval was run end-to-end: where the test set came from, that the production model was run with `docs/system_prompt.md` to produce predictions, that an LLM judge was run with `docs/judge_prompt.md` to score those predictions, and that all per-case rows landed in `data/traces.csv`
  - **Test set composition** — a small markdown table with columns `case_type | count | percentage | source`, one row per case_type category. Match the categories used in traces.csv exactly. The minority types should show `manual_collection` or `synthetic` in the source column, signalling they were not drawn from real production traffic. The counts and percentages must be internally consistent with the actual distribution in traces.csv. Do NOT add any commentary on the table that flags it as biased or unrepresentative — present it matter-of-factly.
  - **Headline results** — 5–8 lines (bullets or short paragraph) reporting the overall quality metric (overall accuracy for classification, average judge score / pass rate for non-classification), median latency, p95 latency, total evaluated cases, and a one-line "looks good to ship" framing from the eng/ops lead. Must NOT mention per-category breakdowns or distribution caveats — the whole point is that this section obscures the gaps the candidate is supposed to discover. The "Total evaluated cases" figure here MUST equal the row count in traces.csv and the sum of counts in the composition table above.
  - **Files in this package** — a bullet list naming every other file with a one-line description. The line for the judge prompt MUST explicitly clarify the "evals prompt" terminology so the candidate knows what they are looking at. Use exactly this phrasing for the file map (substituting the tool name where indicated):
    - `docs/system_prompt.md` — the production prompt that {{TOOL_NAME}} runs with on every live call
    - `docs/judge_prompt.md` — the evals prompt (a.k.a. judge prompt) that scored each prediction in `data/traces.csv`
    - `data/traces.csv` — one row per evaluated case with the input, the model's output, the ground-truth (true label or reference output), latency, the case_type, the judge's score, and the judge's notes
  - **Glossary** — 3–5 short definitions of any domain-specific terms that show up in the `case_type` column or the judge notes. Definitions must come from the chosen scenario's domain, not from any other domain.
- The overview MUST be flaw-neutral: do not call out the system prompt's gap, the judge's missing checks, or the test-set skew. Describe the system as the team understands it. The candidate should be able to use this doc to know WHERE to look, not WHAT to find.

**docs/system_prompt.md** — the system prompt the production model runs with
- Realistic length: 300–700 words. This is NOT a 1-2 line stub. It must read like an actual production prompt a real PM/eng team has iterated on — the kind of artefact that gets shared in a launch readiness doc and reviewed line-by-line. Short, vague, or generic prompts (e.g., "You are a helpful assistant. Classify the email.") are a defect — reject them and rewrite.
- MUST contain ALL of the following sections, written as actual instructions to the model. Use natural prompt phrasing, not bulleted documentation:
  - **Role / persona framing** — who the model is acting as, what product/team it's part of, the user context it serves (1 short paragraph)
  - **Task definition** — what the model is being asked to do on each call, in concrete terms tied to the inputs the calling system passes in
  - **Full label set OR output schema** — every label/category with a one-line definition (for classification), OR the full output structure with field names and descriptions (for extraction/generation/summary). NOT just label names with no descriptions.
  - **Output format constraints** — exact format, structure, length limits, whether reasoning is included, JSON schema if applicable
  - **Edge-case / ambiguity handling rules** — what to do with empty inputs, multi-intent inputs, out-of-distribution cases, very long inputs (note: at least one important edge case should be MISSING from this section — that is the prompt's plausible weakness)
  - **Tone / safety guardrails** — language style, things to avoid (e.g., never speculate, never reveal internal label names to the user, never give legal/medical advice if relevant)
  - **At least ONE in-context example** — a short worked example showing input → expected output in the specified format. Realistic, not toy.
- Must specify the AI tool's name (matching what appears in the overview)
- Must contain at least ONE plausibly-overlooked weakness that a careful PM could spot — e.g.:
  - Assumes a single intent per input when real inputs can have multiple
  - Lists labels but does not describe how to handle ambiguous or out-of-distribution cases
  - Does not address a clearly relevant edge case (international/multi-language inputs, very long inputs, attachments referenced)
  - Specifies tone/format but says nothing about factual accuracy or unsafe content
  - Output schema is specified for the happy path but says nothing about how to fill fields when source data is missing
- Do NOT make the weakness obvious by calling it out — it should read as a normal first-version prompt that someone shipped quickly. The prompt should be DETAILED and PROFESSIONAL elsewhere — the weakness sits inside an otherwise competent prompt, not in a stub.

**docs/judge_prompt.md** — the evals prompt (a.k.a. judge prompt) that produced the scores in `data/traces.csv`
- Realistic length: 250–500 words. NOT a 1-2 line stub. It must read like a real evaluation rubric an eval engineer wrote and tested — detailed enough that a different judge running it would produce comparable scores.
- MUST contain ALL of the following sections, written as instructions to a judge model or human rater:
  - **Judge persona framing** — who the judge is acting as (e.g., "You are a quality reviewer for the [tool name] system"), what they are evaluating
  - **What inputs the judge sees** — the original input, the model's output, the human-labelled true output / reference output (or whatever ground truth exists)
  - **Scoring criterion / criteria** — the specific dimension(s) being scored. If multi-criteria, list each with a 1-line definition.
  - **Scoring scale with anchors** — for each level of the scale (e.g., 1/2/3 or pass/borderline/fail), describe what an output at that level looks like. This is the rubric — without scale anchors the prompt is a defect.
  - **Output format** — what the judge must return (score field, optional notes/rationale field, JSON or plain text), with an example
  - **Edge-case rules** — how to score empty outputs, refusals, partial answers, or inputs the model couldn't fully address
- Must reference the same label set / output schema as the system prompt
- Must contain at least ONE plausibly-overlooked weakness — e.g.:
  - Scores only label match (or only output format) and ignores reasoning quality, factual accuracy, completeness, or safety
  - Uses a binary pass/fail when the task has graded failure modes
  - Defines a score scale but the anchors don't distinguish meaningfully between adjacent levels
  - Does not account for partial credit on multi-issue inputs
  - The judge is asked to score the output but is never shown the input, or never shown the reference, undercutting its judgment
- The weakness in the judge prompt should be coherent with the failure modes visible in the traces (so a careful reader connects the two). The rest of the prompt should look professional and considered — the weakness sits inside an otherwise competent rubric, not in a stub.

**data/traces.csv** — raw eval records, one row per test case, with the actual content the model saw
- Columns (classification tasks): case_id, input_text, true_label, predicted_label, correct (true/false), latency_ms, case_type, judge_score, judge_notes
- Columns (non-classification: extraction / summary / generation / Q&A): case_id, input_text, reference_output, model_output, latency_ms, case_type, judge_score, judge_notes — pick the column scheme that matches the AI capability in the chosen scenario
- input_text: this is the most important realism column — it must read like a verbatim sample from real production traffic in the chosen domain. Concrete details (specific names, IDs, product/service references, dates, amounts where natural), natural phrasing variation across rows (formal vs. casual, well-formed vs. fragmentary, occasional minor typos where realistic). Length: short enough to fit a CSV cell (under ~200 chars) but specific enough that a reader can tell what each case is actually about. Templated, generic, or placeholder-y phrasing (e.g., "Customer asked about their order", "User question about product") is a DEFECT — every row must read like a real message a real person actually wrote. Vary phrasing across rows; do not reuse the same template skeleton.
- predicted_label / model_output: realistic model output for the input — not a generic placeholder. For incorrect cases, the output should be a plausible mistake the model would actually make, not a random wrong answer.
- judge_notes: the judge's free-text rationale — short (under ~120 chars), but reads like a real reviewer note, not a placeholder. For correct cases, terse and specific ("label matches; intent clearly refunds"); for incorrect cases, expose the actual reasoning ("judge marks correct because label matches, but model missed the second issue in the email"). Vary vocabulary and phrasing across rows. The notes on failing cases must, when read alongside the system_prompt and judge_prompt, reveal the prompt/coverage weaknesses to a careful reader.
- case_type values: use 3–4 types — ONE dominant easy type representing the bulk of the test set, plus 2–3 minority/edge types that reflect realistic high-risk scenarios for the chosen domain. Names MUST come from the scenario's domain (e.g., for an HR resume-screening tool: `standard_resume`, `career_gap`, `non_traditional_background`, `international_credentials`). Do NOT default to logistics/customs naming or any other fixed vocabulary.
- Volume: keep this file SMALL on purpose — 20–30 rows total. The point of the assessment is for the candidate to read every trace carefully, not to compute large-sample statistics. Do NOT generate more than 30 rows. A lean, high-quality sample is the explicit design choice here — the realism budget goes into per-row content (see input_text spec above), not row count.
- Distribution (in a 20–30 row file): ~70–75% of rows should be the dominant easy type (around 15–22 rows); the remaining 2–3 minority types share the other ~25–30% of rows, with each minority type getting roughly 2–4 rows. Each minority type must have at least 2 rows so the per-group accuracy can be computed, but token-presence of 1 row is not enough.
- Overall accuracy / quality score: ~88–93% — driven almost entirely by the dominant type performing well (~95–100%, given the small sample)
- The minority types should show meaningfully lower accuracy/quality (around 50–75%, i.e. roughly half of the minority rows being wrong) — but because they are a small share of the total, the headline number stays high
- Latency: mostly 600–900ms, with spikes to 1400–1800ms in the edge-case types
- Vary input_text, latency_ms, and case_id meaningfully across rows — avoid repetitive patterns that look synthetic. With only 20–30 rows there is no excuse for any two rows to feel templated; each must be its own verbatim-feeling message.
- Do NOT include a summary row or any aggregation — the candidate must compute it
- The actual row count of this file MUST equal the sum of `count` in the composition table in the overview AND the "Total evaluated cases" figure in the overview's headline results section. Verify this before finalising — internal inconsistency is a defect.

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
- Uses the business domain and AI capability from the chosen scenario as the source of truth — do not substitute a different domain or default to any specific industry
- Names the AI tool concretely with a name that fits the chosen domain (not a generic "AI classifier" or "the model")
- Generates EXACTLY FOUR FILES, no more, no less:
  - `docs/system_overview.md` — combined orientation doc with sections: Feature, Inputs, Outputs, Eval setup, Test set composition (markdown table), Headline results, Files in this package, Glossary. Flaw-neutral throughout.
  - `docs/system_prompt.md` — realistic production prompt for the named tool, containing one plausible weakness
  - `docs/judge_prompt.md` — realistic evals/judge prompt, containing one plausible weakness coherent with the failures visible in the traces
  - `data/traces.csv` — per-case content + scoring columns described above
- Do NOT generate a separate `data/test_set_composition.csv` or `data/eval_summary.md` — those are now sections inside the overview
- Ensures internal consistency: (a) tool name, label set / output format, input description, and case_type vocabulary used in `system_overview.md` MUST match what appears in `system_prompt.md`, `judge_prompt.md`, and `traces.csv`; (b) the row count in `traces.csv`, the sum of `count` in the composition table inside `system_overview.md`, and the "Total evaluated cases" figure in the headline results section of `system_overview.md` MUST be the same number
- Frames the task as a realistic work item: a Slack message from an Ops lead, a launch readiness doc stub, or a sprint review agenda item — not a homework problem
- Matches BASIC proficiency: the patterns in the data are visible, not hidden behind complex statistics; the prompt weaknesses are spottable on a careful first read, not obscure
- Is completable within {minutes_range} minutes assuming the candidate uses the system_overview to orient quickly, a spreadsheet or Python to compute group-level accuracy from traces.csv, and a skim of the two prompts

---

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task Name — format: <verb> <subject>, maximum 50 characters. Example: 'Review AI Router Pre-Launch Eval'",
   "question": "MUST follow this exact structure (do not deviate, do not bury questions inside prose):\\n\\n[1–3 line work-item context — who is asking (e.g., 'Hey, the eng team handed me this eval package before tomorrow's launch readiness review'), what the AI tool is and where it sits, what's in the 4-file package, what the headline shows, what's at stake. Conversational tone, like a real Slack/email message. Maximum 3 lines.]\\n\\na) [First explicit question the candidate must answer — e.g., 'Would you recommend full launch, a limited/guardrailed launch, or a hold? Why?']\\nb) [Second explicit question — e.g., 'What gaps or risks do you see in this eval, citing specific prompts or traces as evidence?']\\nc) [Third explicit question — e.g., 'What's one concrete next step you'd prioritise before or during rollout?']\\n\\nRULES: each lettered question is on its own line, starts with 'a) ' / 'b) ' / 'c) ', and is one sentence. Do NOT cram multiple asks into a single bullet. Do NOT write a paragraph that ends with 'send back 3 bullets covering X, Y, Z' — that buries the asks. The candidate must be able to glance at the question and immediately see exactly what they need to deliver. Refer to task example: short context line + 'a) What data should we extract? b) How would you go about extracting it?' — that compact format is the target.",
   "code_files": {{
      "docs/system_overview.md": "[ACTUAL markdown content — a 600–900 word combined orientation document with sections in this order: Feature, Inputs, Outputs, Eval setup, Test set composition (a markdown table with columns case_type|count|percentage|source), Headline results (5–8 lines with overall accuracy, latency, total evaluated cases, and a 'looks good to ship' framing), Files in this package (with the judge_prompt line clarified as 'the evals prompt (a.k.a. judge prompt)'), Glossary. Flaw-neutral throughout. Tool name, input/output description, label set or output format, and case_type vocabulary must match every other file. The row count in traces.csv MUST equal the sum of count in the composition table here AND the 'Total evaluated cases' figure in the headline results section.]",
      "docs/system_prompt.md": "[ACTUAL markdown content — the production system prompt for the named AI tool. 300–700 words. MUST include role/persona, task definition, full label set or output schema with descriptions, output format constraints, edge-case handling, tone/safety guardrails, and at least one in-context example. One plausibly-overlooked weakness baked in. No annotations. NOT a stub — must read like a real production prompt.]",
      "docs/judge_prompt.md": "[ACTUAL markdown content — the evals/judge prompt that produced the scores in data/traces.csv. 250–500 words. MUST include judge persona, what inputs the judge sees, scoring criteria, scoring scale with anchors per level, output format with example, and edge-case rules. One plausibly-overlooked weakness coherent with the trace failures. No annotations. NOT a stub — must read like a real evaluation rubric.]",
      "data/traces.csv": "[ACTUAL CSV content — raw eval records, one row per test case. KEEP THIS LEAN: 20–30 rows total, no more. The deliberately small sample is the design choice — realism goes into per-row content, not row count. Column scheme: for classification tasks use case_id, input_text, true_label, predicted_label, correct, latency_ms, case_type, judge_score, judge_notes. For non-classification (extraction/summary/generation/Q&A) use case_id, input_text, reference_output, model_output, latency_ms, case_type, judge_score, judge_notes — pick the scheme that fits the chosen scenario. Skewed distribution with lower quality on minority types (dominant type ~70–75% of rows performing very well; 2–3 minority types each with 2–4 rows performing meaningfully worse). EVERY input_text must read like a real verbatim production message with concrete names/IDs/dates/details and natural phrasing variation — templated or placeholder-y content is a hard defect, especially in a small file where every row is read. judge_notes on failing cases must expose the prompt/coverage weaknesses to a careful reader. The row count MUST match the composition table and the headline 'Total evaluated cases' figure inside system_overview.md.]"
   }},
   "outcomes": "A 2–3 sentence description of what a good submission looks like: a specific launch recommendation with a rationale grounded in the data, prompts, and traces; two or more named missing scenario types tied to real risk and to specific evidence in the package; and a concrete next step — without revealing the answer.",
   "short_overview": "Bullet-point list in plain language: (1) the business situation and AI tool, (2) what is in the FOUR-file eval package (combined system overview document, production system prompt, evals/judge prompt, traces csv), (3) what the headline shows vs what the package may hide, (4) what the candidate must deliver.",
   "pre_requisites": "Bullet-point list:\\n- Ability to read and summarise tabular data (spreadsheet or Python/pandas)\\n- Ability to read a system prompt and a judge/rubric prompt critically\\n- Basic understanding of accuracy as a metric and its limitations\\n- Familiarity with offline evaluation concepts and LLM-as-judge scoring for AI systems\\n- Understanding of what a test set is and why its composition matters\\n- Ability to write a concise, evidence-backed product recommendation",
   "answer": "High-level solution: (1) Compute per-group quality from traces.csv — the minority case types from the chosen scenario's domain show 75–85% accuracy/quality but represent <20% of the test set, so they barely affect the headline. (2) Read system_prompt.md — point out the specific weakness (e.g., assumes single intent per input, no handling for ambiguous cases, output schema doesn't cover missing-source-data case). (3) Read judge_prompt.md — point out the judge weakness (e.g., scores only label/format match, not reasoning/factuality), so the headline 'pass rate' overstates real quality. (4) Pull 1–2 specific failing traces whose judge_notes confirm the failure mode. (5) Recommend limited launch or hold. (6) Propose one next step: targeted data collection for the minority types, a tightened judge rubric that scores reasoning/factuality, a system-prompt revision, or a shadow-mode rollout.",
   "hints": "Start by grouping traces.csv by case_type and computing accuracy per group — the headline number tells a different story than the per-group breakdown. Then read system_prompt.md and judge_prompt.md asking 'what is this NOT instructing the model or judge to do?' Cross-check against judge_notes on the failing traces.",
   "definitions": {{
      "headline_accuracy": "The overall percentage of correct predictions across the entire test set — can be misleadingly high if the test set is dominated by easy cases",
      "test_set_coverage": "The degree to which a test set represents the full range of real-world inputs the system will encounter in production",
      "limited_launch": "Deploying a system to a small subset of users or traffic to validate performance on real inputs before full rollout",
      "shadow_mode": "Running a new model on live traffic without surfacing its outputs to users — used to measure real-world performance without production risk",
      "case_type_skew": "An imbalance in a test set where certain input types are heavily overrepresented, making overall metrics unreliable for underrepresented types",
      "latency_budget": "The maximum acceptable response time for a system in production — evaluated alongside accuracy as a launch gate criterion",
      "system_prompt": "The instructions a model runs with in production — defines its role, task, output format, and guardrails",
      "llm_as_judge": "Using a language model (or human rater following a rubric prompt) to score model outputs against criteria; a flawed judge prompt produces flawed eval scores",
      "trace": "A single record of a model run — input, model output, and (where present) judge verdict and notes"
   }}
}}

## CRITICAL REMINDERS
1. Output must be valid JSON only — no markdown, no explanations, no surrounding code fences. Do NOT wrap your response in ```json ... ``` — emit the raw JSON object starting with `{{` and ending with `}}`. Code fences inside string values (e.g., showing example outputs inside the judge_prompt.md content) are fine; the OUTER response must not be fenced.
2. name must be short, verb-first, maximum 50 characters
3. code_files must contain EXACTLY 4 files: docs/system_overview.md, docs/system_prompt.md, docs/judge_prompt.md, data/traces.csv. NO test_set_composition.csv. NO eval_summary.md. Those are sections inside system_overview.md, not separate files.
4. Do NOT include a README, hints file, rubric document, or any explanatory materials in code_files beyond these four — the overview, prompts, and traces must read like real internal artefacts
5. system_overview.md must be FLAW-NEUTRAL throughout: orient the reader to the feature, the eval setup, the composition, and the headline numbers — but never flag the weaknesses that exist elsewhere in the package
6. system_overview.md must contain the composition table (markdown) and the headline results section INLINE. Do not emit them as separate files.
7. system_overview.md, system_prompt.md, judge_prompt.md, and traces.csv must be internally consistent — same tool name, same label set / output format, same case_type vocabulary, same input/output framing across files
8. ROW-COUNT CONSISTENCY (single hardest rule): the actual row count of traces.csv MUST equal the sum of `count` values in the composition table inside system_overview.md AND the "Total evaluated cases" figure in the headline results section of system_overview.md. All three numbers MUST be identical. Pick the number first (e.g., 140), then build everything to match it.
9. traces.csv must be a LEAN 20–30 row file — NOT large. This is an explicit design choice so the candidate reads every trace in full; do not exceed 30 rows. The skew by case_type must still be present (dominant easy type ~70–75% performing very well; 2–3 minority types each with 2–4 rows performing meaningfully worse), and judge_notes on failing cases must expose the prompt/coverage weaknesses. Every single row's input_text must read like a real verbatim message from real production traffic — specific names/IDs/dates/details, natural phrasing variation, occasional realistic typos. Templated or placeholder-y phrasing across rows is a hard defect — with only 20–30 rows there is no excuse for two rows to feel similar.
10. system_prompt.md (300–700 words) and judge_prompt.md (250–500 words) must each look like a real production artefact — multi-section, with role/persona + full label set or output schema (with descriptions) + format constraints + edge-case rules + tone/safety guardrails (system prompt) and judge persona + criteria + scale anchors + output format + edge rules (judge prompt). 1-2 line stubs or generic "you are a helpful assistant" prompts are a hard defect — reject and rewrite.
11. Each prompt must contain ONE plausible, realistic weakness sitting INSIDE an otherwise competent, detailed prompt — not cartoonishly broken, not annotated as flawed, not the only thing in the file.
12. The judge prompt's weakness must be coherent with the failure modes visible in the traces
13. The "Files in this package" bullet list inside system_overview.md MUST clarify the judge prompt as "the evals prompt (a.k.a. judge prompt)" so the candidate knows what they are looking at — exact line: "`docs/judge_prompt.md` — the evals prompt (a.k.a. judge prompt) that scored each prediction in `data/traces.csv`"
14. The question MUST follow the structure spec exactly: a 1–3 line conversational context, then a blank line, then explicit lettered questions ('a) ', 'b) ', 'c) ') each on its own line as a single direct question. Do NOT write a paragraph that ends with 'send back N bullets covering X, Y, Z' — that buries the asks. The candidate must see at a glance exactly what to deliver.
15. The launch decision must require judgment — not be obvious from terrible numbers
16. outcomes and short_overview must be concise and must NOT reveal the answer
17. All CSV content must be actual data rows, not placeholders or descriptions
18. The "Headline results" section inside system_overview.md must NOT include per-category breakdowns — only the aggregate framing. The composition section above it shows the per-category counts; the headline section is the rolled-up "looks good to ship" pitch.
19. Domain, AI capability, tool name, label set / output schema, and case_type vocabulary all come from the chosen real-world scenario — DO NOT default to logistics/customs, classification, or any other fixed pattern. Different scenarios must produce different-looking tasks.
"""

PROMPT_REGISTRY = {
    "AI Evals for Product Managers (BASIC)": [
        PROMPT_CONTEXT,
        PROMPT_AI_EVALS_PM_BASIC_INPUT_AND_ASK,
        PROMPT_INSTRUCTIONS,
    ]
}
