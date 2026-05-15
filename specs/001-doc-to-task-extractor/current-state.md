# Current State — How We Extract Customer Briefs Today

This document captures **what happens today**, before this feature is built.
It's the baseline we're measuring the proposed solution against.

## The workflow today, end-to-end

A customer sends an assessment brief — usually as a `.docx`, sometimes as a
PDF or a Notion export pasted into text. The brief may describe one task or
several tasks bundled together.

A teammate (call them "the operator") then performs this manual sequence:

1. **Open the brief** in Word or Pages.
2. **Read it cover-to-cover** to understand: how many distinct tasks are
   present, which technology stacks they target, what proficiency level fits,
   what external resources (design images, code-hosting URLs, datasets) are
   referenced.
3. **Decide task boundaries.** Sometimes obvious (the brief uses clear section
   headings); sometimes a judgement call (mixed prose, ambiguous numbering).
4. **For each detected task:**
   a. Pull out the business context, schema/requirements, functional
      requirements, evaluation criteria, into a per-task mental model.
   b. **If the task references an embedded image** (design reference,
      screenshot, diagram): manually unzip the `.docx` (`word/media/*`),
      identify the right image, save it locally.
   c. **If the task references an external URL** (CodePen, CodeSandbox,
      Gist, etc.): open the URL in a browser, manually copy the source code
      from each editor panel. CodePen specifically requires the browser
      session because of Cloudflare; HTTP clients get a 403.
   d. **If an image was extracted in step b:** upload it to the shared Google
      Drive `task-resources/` folder via the Drive web UI, set link-sharing
      to "anyone with the link", copy the resulting URL.
5. **Write the per-task markdown by hand** — this is the heart of the work.
   The teammate composes a long markdown string containing the business
   context, schema tables, numbered functional requirements, embedded image
   URL (if any), starter code blocks (if any), and evaluation criteria. The
   output structure has to match what the existing pipeline expects in the
   `questions_prompt` field of the background JSON.
6. **Spot the gaps** — schema columns referenced but not defined, conflicting
   requirements, missing redirect URLs. Resolve them by either inferring
   sensible defaults (risky), pinging the customer (slow), or flagging them
   for review (clean but adds a step).
7. **Edit the input JSON files** in `task_input_files/input_<tech>/...` to
   embed the generated markdown into the `questions_prompt` field.
8. **Edit the prompt module** in `task_generation_prompts/<level>/` if a new
   tech stack is being introduced.
9. **Edit the scenarios file** `task_input_files/task_scenarios/task_scenarios.json`
   to add a short pointer for this brief.

Only after step 9 can the operator run `python multiagent.py generate_tasks`
on the prepared inputs.

## What we measured during a real engagement (May 2026)

We ran this workflow against the Nerdium brief (`Nerdium Test.docx`, two
tasks: a MySQL query-writing task and a frontend popup-replication task,
with one embedded image and one CodePen URL).

| Step | Time spent |
|---|---|
| Read + decide boundaries | ~15 minutes |
| Extract image from `.docx`, upload to Drive | ~10 minutes |
| Open CodePen + bypass Cloudflare + copy each editor panel | ~25 minutes |
| Write the per-task markdown by hand (both tasks) | ~50 minutes |
| Spot + flag schema gaps (`m_email` missing, `d_is_anonymous` missing) | ~5 minutes |
| Edit input JSONs and the prompt module | ~30 minutes |
| Run `multiagent.py generate_tasks` per task (downstream — out of scope) | ~10 minutes |
| **Total operator time** | **~145 minutes for two tasks** |

That's about 70-75 minutes per task. For a customer expecting a 10-task brief
to be processed in a day, today's workflow caps us at roughly one customer's
worth of work per operator per day.

## What goes wrong today

Even when the operator does everything right, several failure modes
regularly show up:

- **Inconsistency between operators.** Two teammates handling similar briefs
  on the same day will produce different `questions_prompt` markdown — same
  intent, divergent wording. Downstream tasks generated from those briefs
  vary correspondingly.
- **Missed image content.** A teammate uploads the image to Drive but
  doesn't describe what's in it. The downstream LLM (in
  `multiagent.py generate_tasks`) cannot see the image, so the generated
  task says "replicate this design" without telling the candidate what the
  design contains. The candidate clicks the link, but the LLM that built
  the task didn't know the design's structure.
- **Customer-source URL leakage.** Without a disciplined check, the original
  CodePen URL sometimes ends up in the generated repo as a "boilerplate
  link" — which trivially defeats the assessment because the candidate can
  read the answer directly from the source pen.
- **Schema-gap discovery is gated on operator vigilance.** If the operator
  doesn't notice that a query references an undefined column, the generated
  task is broken and the gap surfaces during candidate testing — wasting
  candidate time and producing a negative customer-facing experience.
- **Re-runs are not idempotent.** If the customer iterates on the brief and
  the operator re-runs the workflow, they often re-do all manual work
  because there's no caching. The CodePen scrape is run again. The image is
  re-uploaded to Drive as a new file.
- **Bus factor of 1.** Only operators who have done this before know which
  manual steps matter. Onboarding a new operator is itself a ~half-day
  shadow-and-walkthrough exercise.

## What scales poorly

The friction grows linearly with two axes:

1. **Tasks per brief** (more tasks = more hand-written markdown).
2. **Resources per task** (more images / more CodePen URLs / more datasets =
   more scrape + upload + transcribe cycles).

It does not grow with **briefs per week** beyond what a single operator can
hold in their head. So the bottleneck is operator throughput.

## The bug list the operator discovers along the way

Many pipeline bugs were discovered during the manual workflow because the
operator is in the loop end-to-end. These are real, today, and orthogonal to
the parser — but worth fixing alongside it. See
[`docs/known_pipeline_pitfalls.md`](../../docs/known_pipeline_pitfalls.md)
for the running list (currently 7 items, including duplicate Supabase
triggers, eval-pipeline routing breakage, an `{{minutes_range}}` template
bug, and several others).

The proposed feature won't fix any of those pitfalls directly. But by making
the operator's loop tighter, it makes pitfalls more visible — the operator
notices a broken eval pipeline within seconds of running, not buried at the
end of a 75-minute extraction effort.
