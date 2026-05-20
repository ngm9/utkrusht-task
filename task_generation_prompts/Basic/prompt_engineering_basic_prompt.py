PROMPT_CONTEXT = """
Let me provide you with some context about the company and role:

Company Context:
{organization_background}

Roles and Responsibilities:
{role_context}

Based on this information, could you summarize what you understand about the company and role requirements?
"""

PROMPT_PROMPT_ENGINEERING_BASIC_INPUT_AND_ASK = """
Now that you understand the company context and role requirements, let me provide you with the specific inputs for generating a Prompt Engineering assessment task.

INPUT COMPETENCIES:
{competencies}

INPUT ROLE CONTEXT:
{role_context}

INPUT REAL-WORLD SCENARIOS FOR TASK INSPIRATION:
{real_world_task_scenarios}

SCENARIO FOCUS:
The candidate is a Prompt Engineer who has been handed a small package containing a real production prompt (or two prompt variants) plus the artefacts a real prompt engineer would actually have on hand to diagnose what is going wrong and decide what to ship next. The specific feature, AI capability (classification, routing, extraction, summarisation, generation, Q&A, etc.), product surface, and business domain MUST come from the chosen real-world scenario above. Do not default to any one domain or capability — let the scenario drive it.

The package they receive is always a LEAN 4-FILE package, never a sprawling folder. The exact 4 files depend on which of the TWO TASK SHAPES the chosen scenario calls for:

TASK SHAPE A — DIAGNOSE & REWRITE (the chosen scenario describes a single production prompt that is producing wrong outputs in real traces):
  - `docs/system_overview.md` — combined orientation: feature, inputs, outputs, eval setup (1-line), files in package, glossary. Flaw-neutral.
  - `docs/system_prompt.md` — the live production prompt with 1-2 plausibly-overlooked weaknesses
  - `data/traces.csv` — 20-30 rows, ~30-40% failures whose `judge_notes` map back to the specific prompt weaknesses
  - one of `docs/style_guide.md` OR `docs/output_schema.md` — the contract the rewrite must respect (so the candidate cannot just hand-wave "make it better")

TASK SHAPE B — A/B VARIANT DECISION (the chosen scenario describes two prompt variants that have been A/B tested):
  - `docs/system_overview.md` — combined orientation: feature, what is being decided, who pushed which variant, headline win rate, files in package, glossary. Flaw-neutral.
  - `docs/variant_a_prompt.md` — full production prompt for variant A (the incumbent, usually)
  - `docs/variant_b_prompt.md` — full production prompt for variant B (the challenger)
  - `data/ab_test_results.csv` — 20-30 rows, per-case both variants' outputs + judge scores + case_type. The headline says one variant wins (e.g., "B wins 58/42") but per-segment results show the winner regresses on a high-risk minority case_type.

The candidate must:

For TASK SHAPE A:
(a) Identify the specific weaknesses in the current prompt — citing exact lines or sections plus 1-2 failing traces as evidence
(b) Provide a rewritten v2 prompt that fixes them while respecting the style guide / output schema contract
(c) Name the trade-off the v2 rewrite makes (what gets slightly worse, or what to watch in production)

For TASK SHAPE B:
(a) Recommend which variant ships — full launch, limited launch, or hold — with a clear rationale
(b) Identify what is missing or misleading in the A/B test design itself (sample skew, judge prompt that scores only format, narrow segmentation, etc.)
(c) Propose ONE concrete prompt iteration to queue next, citing evidence from the per-case results

WHAT THIS TASK TESTS:
- Ability to read a production prompt critically — spotting under-specified instructions, missing edge-case handling, vague output formats, weak or missing examples
- Ability to read a small traces or A/B results file and link concrete failures back to specific prompt sections
- Ability to rewrite a prompt with targeted, defensible changes — not vague "make it better" notes
- Ability to compare two prompt variants and surface segment-level regressions hidden by the headline win rate
- Understanding that a v2 prompt must respect external contracts (style guide, output schema, downstream system)
- Practical communication: a concrete next step, not a list of observations

EVAL RUBRIC SIGNALS (what separates strong from weak candidates):
- Cites specific lines or phrasing from the prompt(s) as evidence — not just "the prompt is bad"
- Distinguishes prompt-level failures (the prompt does not address this case) from data-level failures (input is genuinely OOD)
- For SHAPE A: the v2 rewrite is concrete — adds named sections, named examples, named edge-case rules. Does NOT delete working parts. Respects the style guide / schema.
- For SHAPE B: looks past the headline win rate, computes per-case_type results, recommends ship/limited/hold with a defensible rationale tied to evidence
- Names ONE concrete next step — not a vague taxonomy of "things to try"
- Acknowledges the trade-off the change makes (more verbose on edge cases, slightly slower, increased refusal rate, etc.)

CRITICAL TASK GENERATION REQUIREMENTS:
- Draw inspiration from ONE of the real-world scenarios provided above to set the business domain, AI capability, and which task shape (A or B) applies. The scenario you pick is the source of truth for the feature, the inputs, the outputs, the case_type vocabulary, and whether the task is a critique-rewrite or an A/B decision.
- Across multiple generations, vary which scenario you pick so the resulting tasks span different domains, AI capabilities, and BOTH task shapes — never bias toward shape A or shape B exclusively, and never default to any one industry or AI capability
- The task must be completable within {minutes_range} minutes for a BASIC proficiency Prompt Engineer
- For SHAPE A: the system_prompt.md must contain 1-2 realistic, plausibly-overlooked weaknesses without being cartoonishly broken. The traces must contain 6-10 failing rows whose judge_notes visibly link the failure back to the prompt's gaps when read carefully.
- For SHAPE B: variant_a_prompt.md and variant_b_prompt.md must each be FULL production prompts (not snippets). Variant B should have a headline win — but per case_type, it should regress on a meaningful minority segment, with judge_notes on those rows exposing what variant B got wrong that variant A got right.
- Do NOT give away the v2 rewrite, the missing prompt sections, the recommended A/B winner, or the next iteration in the data — the candidate must reason to them
- Do NOT label any document as "flawed" or annotate the weakness — every file should look like a real internal artefact

Before we proceed to the detailed task generation instructions, please confirm your understanding by answering:

1. What will the task be about? (Describe the business domain, the AI tool, whether it is SHAPE A or SHAPE B, and the specific deliverable the candidate must produce)
2. What will the task look like? (Describe the FOUR files in the package — for SHAPE A: system_overview.md, system_prompt.md, traces.csv, plus style_guide.md or output_schema.md; for SHAPE B: system_overview.md, variant_a_prompt.md, variant_b_prompt.md, ab_test_results.csv — what each contains, where the patterns or weaknesses sit, and the expected deliverable format at BASIC proficiency level)

Please provide a brief summary of your understanding before proceeding with the full task generation.
"""

PROMPT_INSTRUCTIONS = """

## GOAL
As a senior prompt engineering practitioner, you are generating a realistic work-item assessment that tests whether a Prompt Engineer candidate can read a production prompt critically, link traces back to prompt gaps, and either rewrite the prompt (SHAPE A) or pick between two variants and propose a next iteration (SHAPE B). The specific feature, AI capability, product surface, and business domain all come from the chosen real-world scenario — do not default to any one pattern. The task must feel like a real prompt iteration ticket — the kind a Prompt Engineer picks up on a Monday morning when ops or eng surfaces a problem.

## CRITICAL SUCCESS CRITERIA
The generated task MUST assess the following competencies:
1. **Prompt Anatomy Recognition**: Knowing what sections a real production prompt has and spotting when one is missing or under-specified
2. **Critical Prompt Reading**: Reading a prompt line-by-line and identifying plausibly-overlooked weaknesses with line-level evidence
3. **Trace Inspection**: Reading per-case traces or A/B results and linking specific failures to specific prompt sections
4. **Targeted Rewrite (SHAPE A only)**: Producing a v2 prompt that fixes the gaps, respects external contracts, and does not break the working parts
5. **Variant Comparison (SHAPE B only)**: Surfacing segment-level regressions hidden behind a headline win rate; making a defensible ship/limited/hold call
6. **Iteration Communication**: Naming the trade-off and one concrete next step — not vague observations

## INSTRUCTIONS

### Nature of the Task
- The task presents either a single broken production prompt (SHAPE A) or two A/B variants (SHAPE B) — chosen by the scenario
- Provide a LEAN 4-FILE package as starter materials. The exact 4 files differ by shape (see Data File Requirements below).
- The candidate answers the lettered questions in the work item directly — short concise responses per question, with evidence from the prompts and traces. The asks themselves live in the question field as explicit a) / b) / c) prompts; the candidate replies to those, not to a generic "send back N bullets" instruction.
- Do NOT provide a rubric, hints, or any framing that signals what the right answer is
- Do NOT annotate the prompts or traces with "this is the problem" comments — they should read like real internal artefacts
- The system overview must orient the candidate to the feature WITHOUT flagging any of the weaknesses — neutral architecture/onboarding doc tone, with the headline numbers (and for SHAPE B the variant comparison framing) presented matter-of-factly
- The data must require the candidate to compute or notice the failure pattern themselves — do not label any case_type as "weakness" or "regression"
- The total row count in `data/traces.csv` (SHAPE A) or `data/ab_test_results.csv` (SHAPE B) MUST equal the "Total evaluated cases" figure in the system overview AND the sum of any per-case_type counts shown in the overview. These numbers must match exactly — internal inconsistency is a defect.

### Data Realism Principle
Each file must match the kind of artefact a Prompt Engineer would actually receive in real production. We intentionally keep the per-case file SMALL so the candidate can read every row in a few minutes — but every individual row must be deeply realistic, as if pulled verbatim from production traffic:
- **traces.csv / ab_test_results.csv**: keep this LEAN — aim for 20-30 rows total. Do NOT generate 100+ rows. The realism budget must go into the CONTENT of each row, not the row count. Every `input_text` must read like a real verbatim message from a real user in the chosen domain — concrete names, IDs, dates, product/service references, natural phrasing variation, occasional realistic typos. Templated or placeholder-y inputs are a defect even at 20 rows.
- **System prompt(s) and constraint document**: these are where you spend your realism budget — they must read like real production artefacts (full multi-section prompts, label definitions, output schemas, examples). Do NOT shorten them to compensate for the small per-case row count — the prompts must remain rich and realistic.
- The trade-off is explicit: smaller per-case file, maximally realistic prompt(s) and per-row content.

### Data File Requirements

The package contains EXACTLY FOUR files. Each must look like a real internal artefact — no annotations, no flags, no "this is the issue" comments.

#### SHAPE A — DIAGNOSE & REWRITE (single broken prompt + failing traces)

**docs/system_overview.md** — combined orientation document
- Realistic length: 500-800 words, written as a neutral architecture / onboarding note
- MUST contain these sections, in order, using clear markdown headings:
  - **Feature** — one paragraph: what the AI tool is named, what product surface it lives on, who calls it, what problem it solves
  - **Inputs** — what the model sees on each call, plus any pre-processing the calling system applies
  - **Outputs** — what the model returns (label set / output schema / generated text format), plus any post-processing
  - **How this prompt was eval'd** — 3-5 lines: where the test set came from, that the production model was run with `docs/system_prompt.md` to produce predictions, that an LLM judge or human rater scored those predictions, and that all per-case rows landed in `data/traces.csv`. ALSO state the "Total evaluated cases" figure here — this number MUST equal the row count in traces.csv.
  - **Headline results** — 3-5 lines reporting the overall quality metric (overall accuracy / pass rate / average score), median latency, and a one-line "the prompt is mostly working but ops surfaced these specific failures" framing. Must NOT label any failure pattern as the diagnosis — the candidate finds it.
  - **The constraint document** — one short paragraph naming the OTHER doc in the package (`docs/style_guide.md` OR `docs/output_schema.md`) and what it is the source of truth for. Use exactly this phrasing depending on which constraint doc you generate:
    - If style guide: "`docs/style_guide.md` is the brand/voice/format contract this prompt must respect — any rewrite must stay inside it."
    - If output schema: "`docs/output_schema.md` is the downstream contract this prompt's output must conform to — the calling system parses against it; any rewrite must keep the schema valid."
  - **Files in this package** — bullet list naming every other file with a one-line description. Use exactly this phrasing (substituting the tool name where indicated):
    - `docs/system_prompt.md` — the production prompt that {{TOOL_NAME}} runs with on every live call
    - `docs/style_guide.md` OR `docs/output_schema.md` — the contract any rewrite must respect (pick the one that fits the scenario)
    - `data/traces.csv` — one row per evaluated case with the input, the model's output, the ground-truth (true label or reference output), latency, the case_type, the judge's score, and the judge's notes
  - **Glossary** — 3-5 short definitions of any domain-specific terms that show up in the case_type column or the judge notes. Definitions must come from the chosen scenario's domain.
- The overview MUST be flaw-neutral: do not call out the prompt's gaps. Describe the system as the team understands it.

**docs/system_prompt.md** — the production prompt the model runs with
- Realistic length: 300-700 words. NOT a 1-2 line stub. It must read like an actual production prompt a real eng/PM team has iterated on.
- MUST contain ALL of the following sections, written as actual instructions to the model. Use natural prompt phrasing, not bulleted documentation:
  - **Role / persona framing** — who the model is acting as, what product/team it's part of, the user context it serves (1 short paragraph)
  - **Task definition** — what the model is being asked to do on each call, in concrete terms tied to the inputs the calling system passes in
  - **Full label set OR output schema** — every label/category with a one-line definition (for classification), OR the full output structure with field names and descriptions (for extraction/generation/summary). NOT just label names with no descriptions.
  - **Output format constraints** — exact format, structure, length limits, JSON schema if applicable
  - **Edge-case / ambiguity handling rules** — what to do with empty inputs, multi-intent inputs, OOD cases, very long inputs (note: at least one important edge case should be MISSING or under-specified — that is the prompt's plausible weakness)
  - **Tone / safety guardrails** — language style, things to avoid
  - **At least ONE in-context example** — a short worked example showing input → expected output. Realistic, not toy.
- Must specify the AI tool's name (matching what appears in the overview)
- Must contain 1-2 plausibly-overlooked weaknesses that a careful Prompt Engineer could spot — e.g.:
  - Assumes a single intent per input when real inputs can have multiple
  - Lists labels but does not describe how to handle ambiguous or OOD cases
  - Does not address a clearly relevant edge case (international/multi-language inputs, very long inputs, attachments, missing source data)
  - Specifies tone/format but says nothing about factual accuracy
  - Output schema is specified for the happy path but says nothing about how to fill fields when source data is missing
  - In-context example covers only the easy case; no example for the failing edge case
- Do NOT make the weakness obvious by calling it out — it should read as a normal first-version prompt that someone shipped quickly. The prompt should be DETAILED and PROFESSIONAL elsewhere — the weakness sits inside an otherwise competent prompt.

**docs/style_guide.md** OR **docs/output_schema.md** — the contract the rewrite must respect (pick whichever fits the scenario better)
- Realistic length: 200-400 words
- If `style_guide.md`: should specify brand voice, tone rules, sentence length / format constraints, words to avoid, examples of approved vs rejected output snippets — like a real internal style guide a content/brand team owns
- If `output_schema.md`: should specify JSON schema with field names, types, required vs optional, allowed enum values for label fields, validation rules — like a real internal API contract doc
- This document is NOT flawed — it's the contract the v2 rewrite must respect. The candidate's rewrite should NOT change this document; if their rewrite breaks any rule in here, they lose points.

**data/traces.csv** — raw eval records, one row per test case
- Columns (classification): case_id, input_text, true_label, predicted_label, correct (true/false), latency_ms, case_type, judge_score, judge_notes
- Columns (non-classification: extraction / summary / generation / Q&A): case_id, input_text, reference_output, model_output, latency_ms, case_type, judge_score, judge_notes — pick the column scheme that matches the AI capability in the chosen scenario
- input_text: the most important realism column — must read like a verbatim sample from real production traffic. Concrete details, natural phrasing variation, occasional realistic typos. Length: under ~200 chars but specific enough that a reader can tell what each case is actually about. Templated or generic phrasing (e.g., "Customer asked about their order") is a DEFECT.
- predicted_label / model_output: realistic model output for the input — for incorrect cases, the output should be a plausible mistake the model would actually make given the prompt's gap.
- judge_notes: short (under ~120 chars) — for failing cases, the notes must, when read alongside system_prompt.md, expose the prompt weakness to a careful reader (e.g., "model picked one intent — input had two", "no value for required field, model invented one", "answered in English — input was Spanish"). Vary vocabulary across rows.
- case_type values: 3-4 types — ONE dominant easy type (~60-70% of rows), plus 2-3 minority/edge types that map to the prompt's specific weaknesses. Names MUST come from the scenario's domain.
- Volume: 20-30 rows total. Do NOT exceed 30 rows.
- Distribution: dominant type ~95-100% accurate; minority types ~30-60% accurate (these are where the prompt gaps surface). Overall accuracy ~75-88%.
- Latency: mostly 600-900ms with spikes to 1200-1800ms in edge cases.
- The actual row count of this file MUST equal the "Total evaluated cases" figure in system_overview.md.

#### SHAPE B — A/B VARIANT DECISION (two prompt variants + per-case results)

**docs/system_overview.md** — combined orientation document
- Realistic length: 500-800 words
- MUST contain these sections, in order:
  - **Feature** — one paragraph: AI tool name, product surface, who calls it, what problem it solves
  - **What is being decided** — one short paragraph: variant A is the incumbent, variant B is the challenger pushed by [team — e.g. content team, ops team, eng]; the eng team needs a recommendation today
  - **How the A/B was run** — 3-5 lines: where the test set came from, both variants were run on the same test set with the same model, an LLM judge or human rater compared per-case outputs, all per-case rows landed in `data/ab_test_results.csv`. State the "Total evaluated cases" figure here — MUST equal row count in ab_test_results.csv.
  - **Headline results** — 3-5 lines: report the overall win rate (e.g., "Variant B wins 58/42 on overall judge score"), median latency for each variant, and a one-line "B looks like the winner, eng wants to ship today" framing. Must NOT mention per-case_type breakdowns — that's what the candidate has to find.
  - **Files in this package** — bullet list naming every other file with a one-line description. Use exactly this phrasing (substituting the tool name where indicated):
    - `docs/variant_a_prompt.md` — the current production prompt {{TOOL_NAME}} runs with (the incumbent)
    - `docs/variant_b_prompt.md` — the challenger prompt the {{TEAM_NAME}} team is pushing
    - `data/ab_test_results.csv` — one row per evaluated case with the input, both variants' outputs, the ground truth/reference, both variants' judge scores, and the case_type
  - **Glossary** — 3-5 short definitions of any domain-specific terms in the case_type column or judge notes
- Flaw-neutral throughout: do not call out the segment-level regression. Describe what was measured and the headline number.

**docs/variant_a_prompt.md** — the incumbent production prompt
- Realistic length: 300-700 words. Full multi-section production prompt. Must include role/persona, task definition, output schema or label set with descriptions, format constraints, edge-case rules, tone/safety guardrails, and at least one in-context example. NOT a stub.
- This is the WORKING incumbent. It handles the high-risk minority case_type correctly because it has a specific instruction or example for it. It is more verbose / slightly slower than variant B on the easy case.

**docs/variant_b_prompt.md** — the challenger prompt
- Realistic length: 300-700 words. Same full multi-section structure as variant A. NOT a stub.
- This is the CHALLENGER. It is a re-written, leaner prompt that wins on the dominant easy case_type (clearer task framing, tighter format spec, faster). But it has DROPPED or WEAKENED the specific instruction / example that handled the high-risk minority case_type. The drop should not be obvious — it should look like a reasonable cleanup that accidentally removed something load-bearing.
- Variant A and Variant B must share the same role/persona framing, same output schema or label set, same format constraints. The difference is in 1-2 specific instructions or examples relevant to the minority case_type.

**data/ab_test_results.csv** — per-case A/B results
- Columns: case_id, input_text, reference_output (or true_label for classification), variant_a_output, variant_a_score, variant_b_output, variant_b_score, latency_ms_a, latency_ms_b, case_type
- input_text: same realism rules as SHAPE A traces — verbatim production-quality messages, no templating
- variant_a_output and variant_b_output: realistic outputs for the same input from each variant. On the dominant easy case_type, variant_b's output should be slightly tighter/cleaner and score higher. On the minority case_type, variant_b's output should drop the load-bearing behaviour and score meaningfully lower.
- variant_a_score and variant_b_score: numeric judge scores (e.g., 0-2 or 1-5 scale) — internally consistent with the output quality. Do NOT include a winner column — the candidate computes the per-case winner from the scores.
- case_type values: 3-4 types — ONE dominant easy type (~60-70% of rows) where variant B wins, plus 1-2 minority types (~20-40% of rows) where variant A wins meaningfully. Names from the scenario's domain.
- Volume: 20-30 rows total.
- Headline win rate: variant B wins 55-65% of cases overall (the headline result the team is leading with) — but per case_type, variant A wins on the high-risk minority by a clear margin.
- The actual row count of this file MUST equal the "Total evaluated cases" figure in system_overview.md.

### Proficiency Level Alignment
- **BASIC level expectations**:
  - Can read a production prompt and identify 1-2 plausible weaknesses with line-level evidence
  - Can read a small CSV and compute a per-group breakdown
  - Can produce a v2 prompt that targets specific gaps without breaking the working parts (SHAPE A)
  - Can recommend ship/limited/hold for an A/B test based on per-segment evidence (SHAPE B)
  - Can articulate one trade-off and one concrete next step
  - Does NOT need to design an eval framework, write an LLM-judge prompt from scratch, or propose a statistical A/B test methodology
- The scenario should have enough ambiguity that the rewrite (A) or decision (B) requires judgment, not just rule-following
- For SHAPE A: the correct rewrite has 2-4 specific changes — adding a missing edge-case rule, tightening a vague instruction, adding 1-2 worked examples for the failing case_type
- For SHAPE B: the correct call should be "limited launch" or "hold variant B" with a specific instruction to bring back the missing behaviour — not an obvious "ship A" or "ship B"

### AI and External Resource Policy
- Candidates are ENCOURAGED to use AI tools, spreadsheets, and any external resources
- The task assesses prompt-reading judgment and evidence-based reasoning — not memorisation
- Complexity should require genuine prompt engineering reasoning beyond what a single LLM prompt would produce on its own

### Task Generation Requirements
Based on the provided `real_world_task_scenarios`, create a task that:
- Uses the business domain and AI capability from the chosen scenario as the source of truth
- Picks ONE task shape (A or B) based on which the chosen scenario calls for; do not mix shapes within a single task
- Names the AI tool concretely with a name that fits the chosen domain (not a generic "AI classifier" or "the model")
- Generates EXACTLY FOUR FILES, no more, no less:
  - SHAPE A: `docs/system_overview.md`, `docs/system_prompt.md`, `docs/style_guide.md` OR `docs/output_schema.md`, `data/traces.csv`
  - SHAPE B: `docs/system_overview.md`, `docs/variant_a_prompt.md`, `docs/variant_b_prompt.md`, `data/ab_test_results.csv`
- Ensures internal consistency: tool name, label set / output format, input description, and case_type vocabulary used in `system_overview.md` MUST match what appears in every other file; the row count of the per-case CSV MUST equal the "Total evaluated cases" figure in `system_overview.md`
- Frames the task as a realistic work item: a Slack message from an eng/ops/PM, a prompt iteration ticket, or a launch readiness ping — not a homework problem
- Matches BASIC proficiency: the prompt weaknesses or per-segment regressions are spottable on a careful first read, not obscure
- Is completable within {minutes_range} minutes assuming the candidate uses system_overview to orient quickly, reads the prompt(s) carefully, scans the per-case CSV, and produces either the v2 prompt (A) or the ship/limited/hold call + next iteration (B)

---

## REQUIRED OUTPUT JSON STRUCTURE

{{
   "name": "Task Name — format: <verb> <subject>, maximum 50 characters. Examples: 'Rewrite Support Router Prompt', 'Pick Onboarding Email Variant'",
   "question": "MUST follow this exact structure (do not deviate, do not bury questions inside prose):\\n\\n[1-3 line work-item context — who is asking (e.g., 'Hey, ops is seeing a spike in mis-routes for {{TOOL_NAME}} — can you take a look at the prompt before standup?' or 'The content team is pushing variant B for {{TOOL_NAME}} — eng wants a recommendation today'), what the package contains, what is at stake. Conversational tone, like a real Slack/email message. Maximum 3 lines.]\\n\\na) [First explicit question — for SHAPE A: 'What are the specific weaknesses in the current prompt — cite exact lines and 1-2 traces?' For SHAPE B: 'Which variant should ship — full launch, limited launch, or hold? Why?']\\nb) [Second explicit question — for SHAPE A: 'Provide a rewritten v2 prompt that fixes them while respecting the {{style_guide / output_schema}}.' For SHAPE B: 'What is missing or misleading in the A/B test design itself?']\\nc) [Third explicit question — for SHAPE A: 'What trade-off does your rewrite make — what would you watch in production?' For SHAPE B: 'One concrete prompt iteration you would queue next, citing evidence?']\\n\\nRULES: each lettered question is on its own line, starts with 'a) ' / 'b) ' / 'c) ', and is one sentence. Do NOT cram multiple asks into a single bullet. Do NOT write a paragraph that ends with 'send back 3 bullets covering X, Y, Z' — that buries the asks. The candidate must be able to glance at the question and immediately see exactly what they need to deliver.",
   "code_files": {{
      "[file_path_1]": "[ACTUAL content of file 1 per the SHAPE A or SHAPE B specification above]",
      "[file_path_2]": "[ACTUAL content of file 2 per the SHAPE A or SHAPE B specification above]",
      "[file_path_3]": "[ACTUAL content of file 3 per the SHAPE A or SHAPE B specification above]",
      "[file_path_4]": "[ACTUAL content of file 4 per the SHAPE A or SHAPE B specification above]"
   }},
   "outcomes": "A 2-3 sentence description of what a good submission looks like. For SHAPE A: a v2 prompt with 2-4 named changes tied to specific traces, respecting the style guide / output schema, plus one trade-off and one production-watch metric. For SHAPE B: a specific ship/limited/hold call backed by per-case_type evidence, one named gap in the A/B test design, and one concrete next iteration. Do NOT reveal the answer.",
   "short_overview": "Bullet-point list in plain language: (1) the business situation and AI tool, (2) which task shape this is (critique-and-rewrite OR A/B variant decision) and what is in the FOUR-file package, (3) what the headline shows vs what the package may hide, (4) what the candidate must deliver.",
   "pre_requisites": "Bullet-point list:\\n- Ability to read a multi-section production prompt critically and cite specific lines\\n- Ability to read and group a small CSV (spreadsheet or Python/pandas)\\n- Familiarity with output schemas (JSON, structured fields) and basic style/voice guidelines\\n- Understanding of in-context examples, edge-case rules, and output format constraints in prompts\\n- Ability to write a concise, evidence-backed prompt iteration note",
   "answer": "High-level solution. For SHAPE A: (1) Name the 1-2 specific weaknesses in the prompt — under-specified edge case, missing example for failing case_type, vague output rule for missing source data — citing exact lines. (2) Identify 1-2 failing traces whose judge_notes confirm the link. (3) v2 prompt: keep the working role/task/format sections; add a named edge-case rule for the failing case_type; add a worked example for it; tighten the under-specified instruction. (4) Trade-off: slightly longer prompt, slightly slower on happy path. (5) Production watch: per-case_type accuracy on the previously-failing segment. For SHAPE B: (1) Compute per-case_type wins from ab_test_results.csv — variant A wins on the minority case_type by a clear margin. (2) Recommend HOLD variant B (or LIMITED launch) — the headline win rate is misleading. (3) Gap in A/B test design: too few minority-case rows / judge prompt only scoring format / etc. (4) Next iteration: bring back the load-bearing instruction or example from variant A into variant B's leaner structure, then re-run.",
   "hints": "For SHAPE A: read the system prompt with one question in mind — what is this NOT instructing the model to do? Then group traces.csv by case_type and look at the failing rows' judge_notes. For SHAPE B: do not stop at the headline win rate — group ab_test_results.csv by case_type and compute per-segment wins. Then diff the two prompts and ask which difference best explains the per-segment pattern.",
   "definitions": {{
      "system_prompt": "The instructions a model runs with in production — defines its role, task, output format, edge-case rules, and guardrails",
      "in_context_example": "A worked input → expected output pair embedded in the prompt itself, used to anchor the model on format and style",
      "output_schema": "The structured contract a model's output must conform to — usually JSON with required fields, types, and allowed enum values",
      "style_guide": "A brand/voice/format contract that any model output must respect — usually owned by content/brand teams",
      "case_type": "A label assigned to each test case grouping it by scenario (e.g. multi_intent, missing_field, non_english) — used to compute per-segment quality",
      "judge_score": "A numeric score assigned by an LLM-judge or human rater to a model output, scoring it against a rubric",
      "judge_notes": "Short free-text rationale from the judge explaining the score — often the fastest way to find the failure pattern",
      "headline_win_rate": "The overall percentage of A/B cases won by one variant — can mask segment-level regressions if the test set is skewed",
      "load_bearing_instruction": "A specific instruction or example in a prompt that handles a critical case — easy to remove during 'cleanup' but breaks behaviour"
   }}
}}

## CRITICAL REMINDERS
1. Output must be valid JSON only — no markdown, no explanations, no surrounding code fences. Do NOT wrap your response in ```json ... ``` — emit the raw JSON object starting with `{{` and ending with `}}`. Code fences inside string values (e.g., showing example outputs inside the prompt content) are fine; the OUTER response must not be fenced.
2. name must be short, verb-first, maximum 50 characters
3. code_files must contain EXACTLY 4 files. The exact 4 files depend on the task shape:
   - SHAPE A: `docs/system_overview.md`, `docs/system_prompt.md`, `docs/style_guide.md` OR `docs/output_schema.md`, `data/traces.csv`
   - SHAPE B: `docs/system_overview.md`, `docs/variant_a_prompt.md`, `docs/variant_b_prompt.md`, `data/ab_test_results.csv`
4. Pick ONE shape based on the chosen scenario. Do NOT mix shapes within a single task. Do NOT generate 5 files. Do NOT generate a separate test_set_composition.csv or eval_summary.md.
5. Do NOT include a README, hints file, rubric document, or any explanatory materials in code_files beyond the four — they must read like real internal artefacts
6. system_overview.md must be FLAW-NEUTRAL throughout: orient the reader to the feature, the eval setup, and the headline numbers — but never flag the prompt weakness (SHAPE A) or the per-segment regression (SHAPE B)
7. system_overview.md, the prompt(s), the constraint doc (SHAPE A), and the per-case CSV must be internally consistent — same tool name, same label set / output format, same case_type vocabulary, same input/output framing
8. ROW-COUNT CONSISTENCY: the actual row count of the per-case CSV MUST equal the "Total evaluated cases" figure in system_overview.md. Pick the number first (e.g., 24), then build everything to match it.
9. Per-case CSV must be a LEAN 20-30 row file — NOT large. Do not exceed 30 rows. Every input_text must read like a real verbatim message — specific names/IDs/dates/details, natural phrasing variation, occasional realistic typos. Templated phrasing across rows is a hard defect.
10. system_prompt.md (SHAPE A) and variant_a_prompt.md / variant_b_prompt.md (SHAPE B) must each be 300-700 words, multi-section, with role/persona + full label set or output schema (with descriptions) + format constraints + edge-case rules + tone/safety guardrails + at least one in-context example. 1-2 line stubs are a hard defect.
11. SHAPE A: the system_prompt.md must contain 1-2 plausible weaknesses sitting INSIDE an otherwise competent prompt — not cartoonishly broken, not annotated. The traces' judge_notes on failing rows must visibly link the failures back to those weaknesses.
12. SHAPE B: variant_a_prompt.md and variant_b_prompt.md must share the same role/persona, schema, format constraints. The difference is 1-2 specific instructions or examples relevant to the minority case_type — variant A has them, variant B has dropped/weakened them. The headline win rate favours variant B; per-segment results favour variant A on the minority. The ab_test_results.csv judge_notes (if present) or the variant outputs themselves must visibly expose the regression.
13. SHAPE A: the constraint doc (style_guide.md OR output_schema.md) is NOT flawed — it is the contract the v2 rewrite must respect. If the candidate's rewrite breaks it, they fail.
14. The "Files in this package" bullet list inside system_overview.md MUST use the exact phrasing from the spec for the file map, substituting the tool name (and team name for SHAPE B) where indicated
15. The question MUST follow the structure spec exactly: a 1-3 line conversational context, then a blank line, then explicit lettered questions ('a) ', 'b) ', 'c) ') each on its own line as a single direct question. Do NOT bury asks inside prose.
16. The deliverable must require judgment — for SHAPE A the rewrite must respect the constraint doc; for SHAPE B the call should be limited/hold, not an obvious ship-A or ship-B
17. outcomes and short_overview must be concise and must NOT reveal the answer
18. All CSV content must be actual data rows, not placeholders or descriptions
19. Domain, AI capability, tool name, label set / output schema, case_type vocabulary, AND task shape (A or B) all come from the chosen real-world scenario — DO NOT default to one industry, one capability, or one shape. Different scenarios must produce different-looking tasks.
"""

PROMPT_REGISTRY = {
    "Prompt Engineering (BASIC)": [
        PROMPT_CONTEXT,
        PROMPT_PROMPT_ENGINEERING_BASIC_INPUT_AND_ASK,
        PROMPT_INSTRUCTIONS,
    ]
}
