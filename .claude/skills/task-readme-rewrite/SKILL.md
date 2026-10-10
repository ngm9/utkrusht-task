---
name: task-readme-rewrite
description: Use when a task README (repo README.md + Supabase readme_content + gist) reveals the planted defects, the fix, the rules the candidate is meant to derive, or enumerates the instances they are meant to discover (the third leak — name the class, never the members), or when two sibling tasks share the same objectives — to reframe it open-ended in the style that matches the task's shape and level (plain goal statements at INTERMEDIATE/ADVANCED for every shape; team observations only for BASIC repair tasks; probe-style verification for design/build tasks), produce a before/after review doc in the Utkrusht house style, and, once approved, push the rewrite to all five targets (repo README, Supabase readme_content, gist, task_blob.question, and task_blob.short_overview). Also use when a task's in-product description (question) or Problem Statement card (short_overview) states the requirements or mechanisms rather than the outcome, or when a candidate-facing surface is already open-ended and non-leaking but is not in the shape/framing this skill prescribes (e.g. per-line Objectives instead of one shared class-level vocabulary, an Overview that isn't the four-sentence scenario structure, a short_overview whose third bullet doesn't state evaluation criteria) and should be reframed to match the house style anyway, or in scan mode to find which tasks across dev/prod have README leaks and need the same treatment.
---

# Task README Rewrite Skill

Reframes a task README so the candidate is handed **the problem, not the answer**. The
generator tends to write READMEs that list the failure classes in the overview, name the
fix in the objectives, spell out the mechanism in the tips, and state the pass condition
in the verify section. This skill strips each of those back and leaves the thinking to
the candidate.

**What "open-ended" means depends on the task's shape** — see *Task shape decides the
style* below. Get that call right first; the section rules branch on it, and applying the
wrong branch makes a README longer and *more* revealing, not less.

**Conformance, not just leaks (reviewer directive 2026-09-18).** Leaks are the floor, not
the whole job. Whenever you read a task's candidate-facing surfaces — README (Overview,
Objectives, Tips, Verify), `question`, `short_overview`, `title`, `hints`, `outcomes` —
check them against the exact shape and framing this skill prescribes for the task's shape,
**not only** for whether they leak. A section can be perfectly open-ended and non-leaking
and still be in the wrong shape: Objectives phrased per-line instead of on one shared
class-level vocabulary, an Overview that isn't the four-sentence scenario structure, a
`short_overview` whose third bullet restates bullet 2 instead of stating evaluation
criteria, surfaces that don't reuse the same class words. When that happens, **reframe it
to fully match the house style anyway**, and if a required framing element is missing,
draft it. This holds even when `readme_scan.py` reports `clean` — the scanner catches
leaks, not shape drift. Reference the approved READMEs (`35bd49ee` for ADVANCED) as the
target shape. As always: draft → show the before/after → push only on approval.

Two modes:

- **Scan** — `scripts/readme_scan.py` walks every `ready` task in an env and scores each
  README section for leak patterns. Use it to find which tasks need rewriting.
- **Rewrite** — one task at a time: fetch, rewrite by the rules below, build the
  before/after review doc, get approval, then push.

**Never push without explicit approval.** The rewrite changes what every future candidate
sees. Propose first, show the before/after doc, wait.

## Style reference

Use these as the reference for tone and length. Pick the one whose **shape** matches the
task you are rewriting (see *Task shape decides the style*).

**Repair tasks** (approved 2026-09-07):

- AWS Lambda ADVANCED `5b6549db` (`lambda-refund-reliability`) — a repair task with planted defects.
- Apache Spark INTERMEDIATE `379f0c07` (`parcel-eta-spark-tuning`) — a performance/correctness task.

Both live in `docs/lambda-refund-readme-rewrite.html` (repo) and on html-docs
(`https://www.html-docs.com/s/57add549ec`, document id `0713f96a-dedd-465b-a449-fbdf701b9bb2`).

**Design / build tasks** (approved 2026-09-14):

- Jenkins ADVANCED `cca98c38` (`utility-metering-delivery-pipeline`) — a brownfield
  pipeline the candidate reworks to a standard. Read its live README for the full worked
  example: goal-statement Objectives, probe-style How to Verify, tips with no grading
  reference and no port/URL detail.
  `https://github.com/UtkrushtApps/utility-metering-delivery-pipeline`

  Its generating module was updated to match, so future tasks on that track start out
  right: `task_generation_prompts/Advanced/jenkins_pipelines_infra_advanced_prompt/`
  (edit `_gen_prompt_module.py` and regenerate — never hand-edit the generated module).

## Task shape decides the style

Before drafting anything, read the current README end to end **and** enough of the starter
to answer one question: **is the candidate fixing something that is broken, or building
something that does not exist yet?**

| | **Repair task** | **Design / build task** |
|---|---|---|
| Starter ships | working system + planted defects | a naive or absent implementation |
| Candidate does | find the cause, fix it | design the thing to a standard |
| Objectives style | **team observations** — what someone noticed (BASIC only; INTERMEDIATE/ADVANCED use goal statements, see below) | **plain goal statements** — what must be true |
| How to Verify style | **what should be true afterwards** | **probes** — what to try and where to look |
| Reference | `5b6549db`, `379f0c07` | `cca98c38` |

Signals it is a **repair** task: the title says repair/fix/debug/tune; `solvability_runs/`
notes list planted defects; the objectives map one-to-one onto specific broken behaviours;
tests ship and are RED on the starter.

Signals it is a **design/build** task: the title says design/build/rework; grading is
judge-only with no test suite; the starter is correct but naive or missing entirely; the
objectives describe a standard to reach rather than symptoms to chase.

**Why the fork exists.** Observation framing sounds open-ended, but it *forces*
specificity: to write "the team noticed X" you must state X concretely, and on a design
task the concrete X **is** the answer. It only works where the symptom differs from the
cause — a repair task, where "one customer was refunded twice" is a genuine symptom the
candidate still has to trace. On a design task the symptom *is* the requirement, so
observation framing collapses into restating the spec with a story wrapped round it.
That is exactly what happened on `cca98c38` before its rewrite:

```
Before (observation style — states the rule, 31 words):
- The on-call engineer needs deployed images to be traceable to the exact commit that
  produced them, because incident review and rollback depend on knowing what shipped.

After (goal statement — states the goal, 10 words):
- Make deployments easy to identify, understand, and recover when needed.
```

Mood is not the lever; **specificity is**. A vague instruction hides more than a precise
observation.

**INTERMEDIATE and ADVANCED tasks take the goal-statement style whatever their shape
(reviewer decisions, 2026-09-15 and 2026-09-18).** On `35bd49ee`
(`clinical-safety-agent-repair`, Multi-Agent / Tool Use / Production Agent Engineering,
ADVANCED) a team-observation draft was rejected as "not proper — the change is not
working"; the reviewer asked for the same style as the RAG tasks, and on 2026-09-18
extended the rule to INTERMEDIATE as well. The observation style stays for BASIC repair
tasks only. At INTERMEDIATE and ADVANCED, every section is framed as below — **this is
the reference README; frame every section like this.**

#### Reference README — `35bd49ee`, approved and pushed 2026-09-15

```
## Task Overview
A clinical trial is a study testing a medicine, and reports of health problems during it are
called adverse-event reports. They arrive by phone, through an online patient portal, or from
partner organisations; a supervisor decides which AI specialist agents look at each one, the
specialists consult the study's records, and every run ends with a decision, any review it
needs, and an audit history that the safety physicians work through each morning. The service
has been live for one reporting cycle, and the safety physicians, the regulatory operations
lead and the QA auditor have each reported decisions they cannot rely on, while readiness and
the invariant checks have stayed green throughout. A missed or mistimed safety decision in a
clinical trial is a patient-safety and regulatory problem, not a workflow inconvenience.

## Objectives
- Keep decisions with the people who should make them.
- Make triage timely and reliable for every team that depends on it.
- Keep case records consistent.
- Make every decision auditable.
- Surface whatever else a safety physician would refuse to sign off on.

## Helpful Tips
- Run the supplied reports before changing anything, and watch what each participant saw and what the final decision kept.
- Think about what "the same event" means when it arrives twice from different places.
- Consider how an auditor would re-read a decision a month later, and what they would need to trust it.
- Explore what happens when a lookup does not go as planned.

## How to Verify
> [!NOTE]
> Copy .env.example to .env and set your provider key. The invariant tests run offline and need no key; only the end-to-end run does.

- Run a report a physician would want to see, and look at where it ends up the next morning.
- Compare the due date on each supplied report with what that study's own rules would give it.
- Send one patient's event through two channels, then replay it, and compare what the service kept.
- Reconstruct one decision from its audit history alone, and ask whether you could tell what was known and what was not.
```

What each section is doing, and what it replaced:

- **Overview** — four sentences: (1) plain-language opener a non-specialist can follow
  (kept from a teammate's edit — explain the domain, never the defects); (2) how the
  system works and who reads its output; (3) who complained + "readiness and the invariant
  checks have stayed green"; (4) why it matters in the domain's terms. It replaced
  "regulatory operations (reporting deadlines), and QA (reviewing decisions later)" —
  parentheticals that attached each team to its defect — and a setup sentence ("Use your
  own provider key…") that the Verify note already carries.
- **Objectives** — the ledgerops move applied line by line. Keep the verb, replace the
  specifics with the class word (*efficient*, *reliable*, *consistent*, *clear*,
  *auditable*, *timely*):

  | Instance-level (rejected) | Class-level (approved) |
  |---|---|
  | Keep every decision the process needs a person for in a person's hands. | Keep decisions with the people who should make them. |
  | Make every report reach the people who must act on it, in time. | Make triage timely and reliable for every team that depends on it. |
  | Keep one event one case, however many times it arrives. | Keep case records consistent. |
  | Make every decision reconstructible from what was actually known when it was made. | Make every decision auditable. |
  | Surface whatever else a safety physician would refuse to sign off on. | (kept) |

  Why each passes: "in a person's hands" named the human-review gate → "the people who
  should make them" is the class; "in time" named the deadline defect → "timely and
  reliable" is the class; "one event one case… however many times it arrives" named
  dedup → "consistent" is the class; "what was actually known when it was made" named
  the lost-evidence / failed-lookup defect → "auditable" is the class. None of them
  pasted into an agent would tell it what to build. The rejected column was itself a
  reframe of the original rules ("Serious or unclear reports reach a safety physician
  before a case is closed", "…with the right reporting deadline", "Repeat reports of one
  event stay together") — expect **two** passes: first strip the rule, then strip the
  instance.
- **Tips** — where to think, not what to find. Each points at a defect by the *experience*
  the candidate can have (watch what the final decision kept; what "the same event"
  means; how an auditor would re-read it; what happens when a lookup goes wrong), never by
  the mechanism. It replaced three generic tips ("Run the supplied reports", "Compare what
  the teams expect", "Recheck every scenario") that gave the candidate nowhere to think.
- **Verify** — probes, one per objective, in order: do something, look somewhere, no
  expected result. It replaced pass conditions that restated the withheld rules ("reports
  reach the right team with a deadline that follows the study rules", "wait for a safety
  physician", "remain one case"). A line was dropped ("without revealing private patient
  details") because no planted defect backs it — do not keep a check the code cannot fail.

Rename the task title to a "Make …" / "Harden …" form in the same push so the scanner
applies the design/build standard, and move `title`, `question`, `short_overview`,
`hints`, `outcomes` to the same altitude in the same `task_blob` PATCH.

**Concurrent edits.** Before pushing the repo README, `git fetch` and look at what
changed on `main` since you cloned — on `35bd49ee` two teammates had pushed three README
commits the same day. Do not overwrite silently: show the reviewer their version, propose
push / keep / merge, and merge what is good (the plain-language opener above came from
them). Commit with a message that names the superseded commit.

## The rules, section by section

The README keeps its four `## ` sections in this order: **Task Overview, Objectives,
Helpful Tips, How to Verify**. Some tasks carry an extra **Application Access** section
(endpoint list); keep it, place it between Tips and Verify, and strip any paragraph in it
that tells the candidate what to watch for.

### Task Overview

Keep the original opening. Product framing, what the system does, who reads its output.
That part is usually fine.

Replace **the one sentence that enumerates the defects** ("but it reads too much input,
enriches hubs slowly, and duplicates rows when a day is rerun", "the current configuration
is intentionally incomplete: deployments are slow, the image is larger than necessary...")
with a neutral note that the system has been running, that the teams depending on it have
reported behaviour that does not fit, and that their reports are listed under Objectives.
End with the job in one sentence: look into each report and make the outcome right,
without changing what the business logic means.

Do not add resource names, batch sizes, delivery semantics, or file paths that the
original did not have. Keep it to one paragraph, two at most.

**Design/build tasks at ADVANCED — write the overview from the scenario, not from the
code.** The generator's overview names the components it planted the defects in ("a
reproduced bug allows a scoped question to reuse plausible evidence… especially when
cached answers are involved. The evaluation layer also compresses distinct risks") — each
clause is a pointer to a file. Rewrite it as four sentences the domain owner would say:

1. what the system is and who relies on it;
2. the structural fact that makes the problem hard (amendments per site; products renamed,
   merged and split; facts spread across several documents);
3. who has complained and — if true — that the release checks stayed green throughout;
4. why it matters in the domain's own terms (patient safety, a regulatory finding).

Approved, `6a49454c` (2026-09-15):

```
A medical information team runs a question-answering service over the protocol documents of a
Phase III oncology programme. Protocols are amended several times during a study, and each site
operates under the amendment in force when it was activated. The service has been live for two
quarters, and the medical-information lead, the study statistician and the QA auditor have each
reported answers that do not match the protocol version that applies to them, while the release
checks have stayed green throughout. Wrong dosing or eligibility guidance at a site is a
patient-safety and regulatory problem, not a cosmetic one.
```

No component names (cache, evaluation layer, retrieval, index), no "reproduced bug", no
"your work is to harden…" closer — the Objectives carry the ask.

### Objectives (BASIC repair tasks only) — one observation per planted defect

**This branch applies only to BASIC repair tasks** — at INTERMEDIATE and ADVANCED, repair
tasks use the goal-statement style (see the rule above, extended to INTERMEDIATE
2026-09-18). Each bullet is **one or two short sentences**: which team was doing what, and
what they noticed. Nothing else.

```
- The finance team was reconciling last week's payouts and noticed that one customer had been refunded twice for a single order. This should not happen.
- The operations team reran one business date to pick up late scan events and found that the shipment count for that date had roughly doubled afterwards.
```

Rules:

- Real roles only: finance, QA, operations, platform, security review, on-call engineer,
  a developer, an analyst. Pick the team that would actually have seen it.
- **No internals.** No queue/table/bucket/service names, no ids, no fixture names, no
  "visibility timeout", "partition", "broadcast", "healthcheck", "restart policy".
- **No reproduction recipe.** Not "by resending the same request", not "using the slow
  fixture". Say what was seen, not how to trigger it.
- **No fix.** Not "should align X with Y", not "needs a DLQ". If a bullet could be
  pasted into the code review as the change description, it is too specific.
- Keep the mapping: every planted defect gets exactly one observation, so grading and
  tours still line up. Two defects can share a bullet only if a real team would have
  reported them as one incident.
- Length matters. The first draft of this style was three sentences per bullet with
  order ids and quoted tickets; it was rejected as "very descriptive". Short wins.

### Objectives (design / build tasks) — one plain goal per required behaviour

Each bullet is **one sentence, roughly 10–15 words**, stating the outcome the system must
achieve. Plain business English, the way a tech lead states a goal in a brief. The
approved set, from `cca98c38` (2026-09-14):

```
- Build a pipeline that makes the overall build process as efficient as possible.
- Make deployments easy to identify, understand, and recover when needed.
- Enable services to progress through the build process independently wherever possible.
- Keep services aligned with the shared code they depend on throughout the development process.
- Ensure that only stable, production-ready code can be released.
- Ensure deployment configuration is handled securely and reliably.
```

Rules:

- **No team framing.** Not "The platform team expects…", not "The release engineer
  noticed…". See *Task shape decides the style* for why this backfires here.
- **No `because <consequence>` clause.** The justification is a second hint; the goal
  alone is enough.
- **State the goal, never the rule that achieves it.** "Makes the build process as
  efficient as possible", not "only rebuilds the service that changed". If a bullet could
  be handed to an implementer as the acceptance test, it is too specific.
- **One concern per bullet.** If a bullet bundles two separable concerns (a release gate
  *and* credential handling), split it. Six short bullets beat four compound ones.
- Imperative mood is fine and expected here ("Build…", "Ensure…", "Keep…"). That is a
  deliberate departure from the repair style — the leak risk lives in specificity, not
  mood.
- Keep the mapping: every required behaviour gets exactly one bullet, so grading and
  tours still line up.

Bad, with the reason:

```
- "Use a parallel block driven by a list of changed services."        → names the mechanism
- "A change to one service should create a new image only for it."    → states the rule, not the goal
- "The on-call engineer needs images traceable to the commit…"        → team-framed, so forced to state the rule
- "Make the pipeline fast and safe."                                   → too vague to aim at
```

#### The third leak — enumerated instances (added 2026-09-15)

Beyond *mechanism* and *pass condition* there is a third way a goal statement gives the
task away: it **lists the instances** the candidate is meant to discover. The reviewer's
own examples, from `ledgerops-activity-workspace`:

```
Communicate invalid date or lifecycle choices clearly to users.   →  Communicate errors in user inputs clearly.
Preserve accurate money, status, and deletion semantics in displayed rows.  →  Preserve data semantics in the rows displayed.
```

The move is always the same: **keep the verb, swap the instances for the class**. "Invalid
date or lifecycle choices" is the answer key for two checks; "errors in user inputs" is the
category the candidate has to explore. Name the class, never the members.

**The agent-paste test.** Paste the bullet, alone, into an AI coding agent that cannot see
the repository. If it is enough instruction to implement anything, the bullet is too
specific. "Make every answer auditable back to what it was built from" fails to instruct
an agent; "Preserve evidence provenance across the answer lifecycle" tells it to thread
provenance through every stage, including the cache. Apply this to every bullet, and to
the `question` field, before calling a draft done.

**ADVANCED is strict.** Zero enumerated instances anywhere in the Objectives. The ADVANCED
candidate should not be able to hand the README to an agent and get the task done; they
have to read the system, work out what is wrong, and decide what "right" means. At
INTERMEDIATE one instance-level bullet is tolerable where the task is otherwise
under-specified; say so when you keep it.

A worked reframe, approved on `6a49454c` (RAG / Vector DB / AI Evaluation, ADVANCED), after
three rounds of tightening:

```
Keep generated answers grounded in eligible evidence.         →  Keep answers consistent with the rules that apply.
Preserve evidence provenance across the answer lifecycle.     →  Make every answer auditable back to what it was built from.
Make evaluation failures separable and reproducible.          →  (kept — already class-level; the reviewer called it "the ideal one")
What other risks should the quality gate surface before rollout?  →  Surface whatever else the quality gate should catch before rollout.
```

Rejected on the way, with the reason: "Keep answers faithful to the protocol version that
actually applied" (still an instance — *version* is the answer); "Make every answer
auditable" (too short next to the others — the reviewer wants the bullets to be similar in
length and weight); "Anyone reviewing an answer must be able to check where it came from"
(different construction from its siblings, read as a different list).

**The judgment bullet.** One bullet that invites the candidate beyond the stated scope is
the ADVANCED tell. Either form is approved: a question ("What other risks should the
quality gate surface before rollout?") or a sentence ("Surface whatever else the quality
gate should catch before rollout."). The reviewer preferred the sentence when the other
three are sentences; keep the list uniform.

**Objectives must be distinct per task — examples are style, never content.** Two tasks in
the same competency family that share the same four objectives *are the same task* to a
candidate, whatever the domain dressing. When the second task exists to cover a different
competency (e.g. Graph-based Knowledge Systems next to AI Evaluation), the objectives must
ask for **different things**, not the same bar in the same cadence. The generator pastes
the prompt module's example objectives verbatim — check for that first (`6a49454c`
shipped with the module's four examples word for word). Approved contrast, `3976d75a`
(RAG / Graph-based Knowledge Systems / Vector DB, ADVANCED, 2026-09-15):

```
- Keep answers whole when the facts live in different places.
- Make every answer distinguishable from a close match.
- Make disagreements in the bank's own records visible, never silently resolved.
- Surface whatever else should change when the product history changes.
```

Composition, abstention, contradiction, knowledge maintenance — none overlaps the
oncology set, and a candidate who has done one has not done the other. When you propose a
sibling task's objectives, put both lists side by side and say what is different; the
reviewer rejected two drafts that "sounded the same" before this one.

### Helpful Tips — general working advice only

Four bullets, none of which mention a file, a script, a fixture, a technique, or a
scenario. The approved set for a repair task:

```
- Get the stack running and watch a normal <unit of work> go through end to end before you touch anything.
- Reproduce what each team saw before deciding what to change.
- Think about what correct means for <domain: a system that moves money / a daily job people rely on>, not just whether the code runs without errors.
- Whatever you change should still be checkable by hand afterwards.
```

Adapt the domain phrase and the unit of work. A tip that points at a tool the task ships
(e.g. "the job records its own execution observations on every run, read them before the
code") is allowed; a tip that points at a folder or file ("the scripts under `scripts/`
let you resend the same request") is not — that draft was rejected for "revealing files
and what perfectly to do".

Drop every original tip that names a mechanism: "compare delivery timing with the
function's maximum runtime", "think about which identifiers stay stable across retries",
"consider staged builds", "review copy order for cache behaviour".

On a design/build task at ADVANCED the tips are **where to think, not what to find**. Drop
any tip whose noun is the fix: "Analyze whether cached artifacts can outlive the evidence
they depend on" (the cache bug), "Explore whether repeated evaluation runs explain the
same failure dimensions" (the eval fix). Replace with tips that name an experience the
candidate can have:

```
- Think about what "the same question" means for two different sites.
- Explore what happens when you run the evaluation twice without changing anything.
- Consider how citations would be re-read by an independent auditor.
```

One tip may point at the *existence* of a capability without naming it as the gap
("Consider what the system knows about the relationships between products, documents and
states, and whether it uses that knowledge or just its text") — that is the most a tip
may say about where the fix lives.

Two rules that apply to **both** task shapes:

- **Never mention grading**, the grader, or how the submission is assessed. "Whatever you
  build should be something you can check by hand afterwards" — not "…the same way the
  grading will check it". Tips are working advice, not a description of the assessment.
- **No access or setup detail the platform already surfaces** — ports, URLs, console
  links. The candidate reaches those through `expected_ports` (labelled buttons in the
  task UI) and the tour's link steps. "Your pipeline runs on a Jenkins controller inside
  your task environment" is orientation and belongs; "— open it on port 8080 to trigger
  builds and read run logs" is setup detail and does not.

A design/build task may keep **one** tip naming a script the task ships whose invocation
is part of the design ("a deploy script, `deploy_script.py`, ships a built image into your
task environment and starts it there — how and when it is invoked is part of the pipeline
design"). It must not name the script's flags, the credential it needs, or where in the
flow it belongs. That is the one permitted path in the whole README.

### How to Verify (repair tasks) — required behaviour, not instructions

One bullet per observation, phrased as **what should be true afterwards**. Vary the
openers; do not prefix every bullet with "After your fix" (rejected as repetitive).

```
- Sending the same refund request more than once should result in that customer being refunded exactly once, with a single record of it.
- Running the same business date twice should leave the curated row count unchanged.
```

Rules:

- No commands, no script paths, no ids, no "check the configuration at localhost:4566".
- No mechanism in the check: "the health endpoint should only report healthy when the API
  can actually serve requests", not "add a healthcheck with start_period".
- Naming the scenario is unavoidable here (this is the acceptance criteria) and is fine.
  Naming the fix is not.
- Keep the closing bullet that points at the shipped test/invariant suite, if the task
  has one: "The scripts under `tests/` exercise these behaviours once `run.sh` reports the
  stack is ready." That is the one place a path is allowed.

### How to Verify (design / build tasks) — probes, not pass conditions

Each bullet names **an experiment to run and where to look**. It must *not* say what the
correct result is — the candidate judges that against the Objectives. The approved set,
from `cca98c38`:

```
- Change a single service, run the pipeline, and look at what it actually produced.
- Look at what ends up running in your task environment, and ask whether you could tell exactly what produced it.
- Change two unrelated services in the same commit, and watch how their work moves through the pipeline.
- Change only the shared code, and check which services end up affected.
- Make a change that touches no service at all, and see what the pipeline decides to do.
- Try a release from work that is not on the main line, and confirm the outcome is what you would want.
- Check how the deployment gets the configuration it needs, and whether any of it is visible in the pipeline definition itself.
```

**This is the rule most easily got wrong, and the one that quietly undoes the whole
rewrite.** On a repair task the pass condition is safe to state, because knowing the
symptom is not knowing the cause. On a design task the pass condition *is* the spec — so a
Verify section written in the repair style hands back everything the Objectives just
withheld. The candidate reads both sections.

```
Bad  (pass condition): "A change confined to one service should result in exactly one new image for that service."
Good (probe):          "Change a single service, run the pipeline, and look at what it actually produced."
```

Rules:

- Pattern: `"<make this change>, and <where to look>."` One probe per Objective, in the
  same order as the Objectives.
- No commands, no flags, no paths, no mechanism — and **no expected result**.
- Vary the opening verb. Do not start every bullet with "Change".
- **One** bullet may mention the task environment directly. No other bullet may.
- Read Objectives and How to Verify together, as a candidate would, before calling it
  done: between them they must still not give away any rule the candidate is meant to
  derive.

**A probe must not describe what the report should contain.** "Introduce a small
evidence-scope perturbation, and inspect the evaluation report *dimensions*" tells the
candidate the report needs dimensions — the Objective just withheld that. Approved form,
`6a49454c`:

```
- Deliberately break one thing the service promises, re-run the evaluation, and see whether the report would have stopped a release.
- Repeat an unchanged evaluation run, and compare the reported verdicts and audit trail.
```

"Whether the report would have stopped a release" is an outcome the candidate judges;
"dimensions" is the design. Same for knowledge tasks: "Correct one relationship in the
product history, ask again, and see whether the answer follows."

**Before you apply this branch**, know the trade-off and raise it: probes remove the
candidate's ability to self-confirm they are finished. Someone who reads "efficient" as
*layer caching* rather than *change-scoped rebuilds* can run every probe, see plausible
output, and believe they passed — and with judge-only grading they find out late. If the
reviewer wants a safety net, keep the one or two bullets that most define the task's shape
assertive and let the rest go probe-style. Offer that variant; do not decide it silently.

### Structure

- Headings are `## ` (two hashes). Some generated READMEs use `# `; fix them.
- Section order: Overview, Objectives, Tips, [Application Access], Verify. Some
  generated READMEs put Objectives after Access; reorder.
- Supabase `readme_content` is a **JSON object** (`{"task_overview": "...", "objectives":
  [...], "helpful_tips": [...], "how_to_verify": [...]}`) — that is what the generator
  writes via `infra.utils.parse_markdown_to_json` (the generator calls it from `creator.py`), and what the
  product reads. On push, produce it from the final markdown with that same function
  (never hand-build the dict, never store markdown or a Python dict *repr* — the
  Docker/Java tasks `e2925703` and `2f3830e7` shipped a repr string once). The scanner
  reads both forms.

## `question` — the task description shown in the product

`task_blob.question`, Supabase only — not in the repo or the gist. It is the primary
candidate-facing description, so a `question` that lists the mechanisms undoes an
open-ended README on its own. The generator's default is to enumerate every required
behaviour here, which is exactly the failure.

Shape: **set the scene, then state the expectations at the same altitude as the
Objectives.** Plain prose, no bullets, no backticks, no file paths.

1. Who the candidate is and what the system is — team, domain, the services and what
   they share.
2. The situation: something already exists and runs, but is not trusted. Say only that
   — never why, never in what way.
3. What the work must achieve, written as outcomes, in the same words the Objectives
   use.

Approved, from `cca98c38` (2026-09-15):

```
You have joined the platform team at a utility-metering company whose billing platform is
split into four small services - meter ingestion, usage rating, billing export, and
customer alerts - that share a common support package. A first-pass delivery pipeline
already exists and runs, but the release team does not trust it and it does not cover the
platform. Your job is to rework and extend it so that the overall build process becomes as
efficient as possible, deployments are easy to identify, understand, and recover when
needed, and services can progress through the build process independently wherever
possible. It must also keep every service aligned with the shared code it depends on,
allow only stable, production-ready code to be released, and handle deployment
configuration securely and reliably.
```

What it replaced, and the test to apply:

```
Wrong (enumerates the mechanisms):
  "Build only the services truly affected by a source change, tag container images with
   the exact commit, run unrelated affected builds concurrently, rebuild all dependents
   when shared support changes, and perform main-line-only controlled releases where the
   deployment target comes from the controller-managed secret store."
```

Every clause there names a mechanism the Objectives deliberately stopped naming — commit
tagging, concurrency, main-line gating, the secret store. If a clause of the `question`
could be pasted into the pipeline as a requirement, it is too low.

**Keep `question` and Objectives in lockstep.** Stating the expectations inline (rather
than pointing at the README) duplicates them in two fields, which is safe only while both
sit at the same altitude. Whenever you change one, re-read the other in the same pass —
this is the field most likely to drift back down and quietly re-leak.

An acceptable alternative, used by the prod Actions sibling `544c07f1`, is to set the
scene and then point at the README instead of restating: *"…have specific expectations
for what a trustworthy pipeline needs to do here, listed in this task's README under
Objectives."* That removes the drift risk entirely, at the cost of a `question` that does
not stand alone. Either is fine; do not mix them.

## `short_overview` — the "Problem Statement" card (three bullets, different rules)

This is `task_blob.short_overview`, shown to candidates before they open the task as
its "Problem Statement" card — a separate field from the README, with its own shape.
`task-audit` checks its structure (exactly 3 bullets, no glyphs, no file paths); this
skill checks its **framing**, which structure checks miss entirely.

Approved reference (2026-09-08), a Rillguard sensor-alerting task:

```
- Rillguard collects safety readings from field sensors for water utilities and
  alerts operators when conditions turn unsafe, but the current system risks losing
  readings or missing alerts when something downstream goes wrong.
- This redesign needs to make sure no incoming reading is ever lost, no alert is
  ever duplicated or missed, and the system keeps working reliably even during
  traffic bursts or an outage of the alerting provider.
- What separates a strong submission is whether alerts genuinely still reach
  operators on time during failures and traffic bursts, whether no reading or alert
  is ever lost or duplicated, and whether the reasoning behind the design decisions
  is sound.
```

Three bullets, three different jobs:

1. **What the system is** — one or two sentences: what it does, for whom, and the
   one-line risk/problem with it today. Context, not a task list.
2. **What needs to happen** — the required outcome, framed as a property of the
   *system*, never as an instruction to the *candidate*. "This redesign needs to make
   sure X, Y, Z" — not "You must implement X" / "Candidates should build Y." If a
   bullet reads naturally with "You" or "The candidate" inserted at the front, it is
   in the wrong voice; rewrite it as a fact about what the system must guarantee.
3. **What separates a strong submission** — the evaluation criteria, in plain
   language, stated as the actual dimensions someone would grade on ("whether X
   still holds during Y", "whether the reasoning is sound"), not a restatement of
   bullet 2. This is the one place naming *how good* work is told apart from
   adequate work belongs — it should never appear in the README itself (see
   How to Verify above, which states pass/fail behaviour, not grading nuance).

**Altitude — bullet 2 states outcomes, never the rules that achieve them.** The voice
rule above catches *"You must implement idempotency keys"*; it does **not** catch a
correctly-voiced bullet that simply lists every requirement. That second failure is the
same trap as the Objectives section, and it matters more here because the Problem
Statement card is read **before** the candidate opens the task — so an over-specified
bullet 2 hands over the specification on the preview screen and quietly undoes an
open-ended README.

The DESIGN_REVIEW family is the reference for this altitude — they stay at outcome level
throughout (`588ce95d` Rillguard, `a3f31a3f` Streamcart, `6f02f4e8` HarborMint,
`0d15ccb6` Trailpix, `bfff804f` Parcelo; the field is `task_blob.task_overview` on those
rows). Streamcart's bullet 2 is the model:

```
"This calls for a cloud setup that keeps browsing and checkout fast and reliable during a
 flash sale, protects every order that's already been placed, and keeps costs reasonable
 outside of sale periods."
```

Note what is absent: no autoscaling, no queue, no CDN, no replica count. Compare on
`cca98c38`, where the voice was right and the altitude was wrong:

```
Wrong (right voice, lists the rules):
  "The delivery workflow needs to rebuild only the services a commit actually affects,
   produce images traceable to the exact commit that built them, refresh every service
   when shared code changes, and release only from the main line…"

Right (outcome altitude):
  "This rework needs to make the build process efficient, keep what gets deployed easy to
   identify and recover, let unrelated services progress independently while staying
   consistent with the shared code they depend on, and make sure only sound code is
   released with its deployment configuration handled securely."
```

Openers for bullet 2 that read naturally: "This redesign needs to…", "This rework needs
to…", "This calls for…", "This work is about…". For bullet 3, vary it: "A strong
submission is judged on…", "The quality of a submission is measured by…", "What
separates a strong submission is…".

Bad bullet 2 (candidate-directed, common LLM default): "You should implement
idempotency keys and a dead-letter queue to prevent duplicate or lost alerts." — this
also leaks the mechanism, doubling the defect.
Good bullet 2 (system-outcome, same requirement): "This redesign needs to make sure
no incoming reading is ever lost, no alert is ever duplicated or missed, and the
system keeps working reliably even during traffic bursts or an outage of the
alerting provider."

Scan for this with `--check-overview` (below) — it flags bullet 2 written as a direct
instruction and a missing/weak evaluation-criteria bullet 3.

## Rewrite workflow

### 1. Fetch the current README from all three places

```bash
# Supabase (dev or prod) — task_blob has repo + gist under resources
URL=$(grep -E '^SUPABASE_URL_APTITUDETESTSDEV=' .env | cut -d= -f2- | tr -d '"'"'"' ')
KEY=$(grep -E '^SUPABASE_API_KEY_APTITUDETESTSDEV=' .env | cut -d= -f2- | tr -d '"'"'"' ')
curl -s "$URL/rest/v1/tasks?select=task_id,is_enabled,readme_content,task_blob&task_id=eq.<UUID>" \
  -H "apikey: $KEY" -H "Authorization: Bearer $KEY"

# Repo README (clone into the scratchpad, never into the project)
TOKEN=$(grep -E '^GITHUB_UTKRUSHTAPPS_TOKEN=' .env | head -1 | cut -d= -f2- | tr -d '"'"'"' ')
git clone -q https://x-access-token:$TOKEN@github.com/UtkrushtApps/<repo>.git <scratch>/<repo>
```

Use `$URL`/`$KEY` from `SUPABASE_URL_APTITUDETESTS` / `SUPABASE_API_KEY_APTITUDETESTS`
for prod. Filter on `task_blob->>title` (`task_blob-%3E%3Etitle=ilike.*spark*`), not on a
`title` column — the table has none. `task_id` is a uuid column, so `like` does not
work on it; use `eq`.

`task_blob` also carries two more candidate-facing fields that are rewrite targets in
their own right (step 2): **`question`** (the task description shown in the product) and
**`short_overview`** (the Problem Statement card). Fetch both in the same call, and scan
the card with `--check-overview`.

Also read the starter code enough to know **what the candidate is actually being asked to
do** (Dockerfile, compose, handler, Terraform, transforms, pipeline definition). While
in the repo, look for **answer-key leaks that are not in the README**: a `hidden_tests`
file or a `grading/` directory committed to the *candidate* repo (the generator's
`hidden_tests` envelope has been found written to the repo root as a JSON blob — full
source of the hidden grading tests, including expected ids). Report it in step 4 and, once
the reviewer says so, delete it from the candidate repo; hidden tests in the `-answers`
repo are removed on the same instruction (`6a49454c`, `3976d75a`). Check
`solvability_runs/<repo>/` first — if the task was verified, the notes list the defects or
the required behaviours. On a repair task every observation must map to a real defect; do
not invent incidents the code cannot produce.

### 1b. Call the task shape, out loud

Decide **repair** or **design/build** using *Task shape decides the style*, and say which
you picked and why before drafting. Every section rule below branches on this, so a wrong
call produces a confident rewrite in the wrong style. If the task genuinely straddles both
(a brownfield rework with planted defects *and* a standard to reach), say so and ask —
do not average the two styles together.

Then do the **conformance pass** (see *Conformance, not just leaks* up top): for each
surface, ask not only "does it leak?" but "is it in the shape this skill prescribes for the
called shape?" A surface that is open-ended and `clean` on the scanner can still be in the
wrong shape — reframe it to match the reference (`35bd49ee` for ADVANCED) anyway, and draft
any required framing element that is missing. List which surfaces you are changing for
conformance vs. for a leak, so the reviewer sees both.

### 2. Draft the rewrite — README, `question` **and** `short_overview`

Apply the rules for the shape you called. Save the After README as markdown in the
scratchpad. Do not touch the repo yet.

**A rewrite is not finished until `question` and `short_overview` are rewritten too.**
All three are candidate-facing, and the two Supabase fields are read *before* the repo is
opened — so leaving either at the old altitude hands back whatever the README just stopped
saying. Draft `question` against its rules below, and re-read it against the Objectives in
the same pass: when the expectations are stated inline they must match, word-altitude for
word-altitude.

**On `short_overview` specifically.** It is the Problem
Statement card the candidate reads *before* opening the task, so leaving it untouched
hands back on the preview screen whatever the README just stopped saying — the same
read-them-together failure as Objectives vs How to Verify. Draft its three bullets against
the `short_overview` rules below (voice **and** altitude) and save them as a
`bullets.json` array in the scratchpad for step 5. If it is already correct, say so
explicitly in step 4 rather than silently skipping it.

Before moving on, re-read the drafted **Objectives and How to Verify together**, as a
candidate would. Between them they must not give away a rule the candidate is meant to
derive — this is where design/build rewrites most often leak straight back.

Also draft **`title`, `hints` and `outcomes`** in the same pass. They are candidate- or
grader-facing and the generator writes them at mechanism altitude ("Trace how evidence
scope, provenance, cache identity, and evaluation dimensions move…"; outcomes that list
"trial, site, date, amendment, and manifest context"). `hints` becomes one nudge that
names a starting experience, not a component ("Start with one reviewer question whose
answer needs two documents, and follow it from the question to the final wording");
`outcomes` becomes one line per Objective at the Objective's altitude plus the standing
code-quality line. `definitions` and `pre_requisites` may keep domain terms but should not
name the fix either — flag them if they do.

**Heading assertion.** Many infra-shape starters ship `invariants/test_scaffold.py` (or
similar) asserting the README's `## ` headings in exact order. Read it before drafting;
the rewrite must keep the four headings and their order, or `run.sh` goes red on the
unsolved starter.

### 3. Build the before/after review doc

Add the task as a new **Part N** to `docs/lambda-refund-readme-rewrite.html`, following
the exact structure already there (partmeta line, "What changed" table, then one
Before/After panel pair per section). Give `short_overview` its own Before/After pair
alongside the README sections — the reviewer approves it too. The file is in the Utkrusht house style (green brand
bar, shimmer hero, 880px paper, Inter) — do not restyle it. Do not add an internal status
callout ("nothing has been pushed yet"); it goes stale and was removed on review.

Push the same file to html-docs so the reviewer sees it at the known link:

```
mcp__html-docs__update  id=0713f96a-dedd-465b-a449-fbdf701b9bb2  api_key=<HTMLDOCS_API_KEY from ~/.claude.json>  html=<full file>
```

The `/s/57add549ec` share slug is **not** the document id — pass the UUID. Then `open`
the local file so the reviewer has it in the browser.

### 4. Show it and stop

Report which task, the shape you called, what changed per section, whether `question`
and `short_overview` changed (and if not, why it was already correct), and anything found in
the repo along the way (broken helper scripts, wrong heading levels, dict-repr Supabase
rows). Then wait.
The reviewer has so far asked for two or three rounds of tightening per task; expect that.

### 5. Push, once approved, to all five targets

The README text lives in three places and must not drift; `question` and
`short_overview` are two further targets, both Supabase-only — and `title`, `hints`, `outcomes` ride along in the same `task_blob` PATCH (step 2 drafted them):

1. **Repo README.md** — commit to `UtkrushtApps/<repo>` on its default branch. Push
   with `GITHUB_UTKRUSHTAPPS_TOKEN` via an `x-access-token` URL from a small Python
   helper that loads `.env` with `python-dotenv` — never `source .env` in the shell (an
   unquoted value executes and echoes a key into the transcript; this happened) and never
   print the push URL unmasked.
2. **Supabase `readme_content`** — PATCH the row in every env the task exists in (dev,
   and prod if promoted). Store the `parse_markdown_to_json(readme)` object (see *Structure*).
3. **Gist** — update the README file in `task_blob.resources.github_gist` with
   `GITHUB_GIST_TOKEN`.
4. **Supabase `task_blob.question`** — Supabase only. PATCH it in every env the task
   exists in, wrapped as `{"task_blob": {...}}` (never send the raw blob as the body).
5. **Supabase `task_blob.short_overview`** — Supabase only; it is *not* in the repo or
   the gist. **Always use `scripts/apply_overview.py`** — never hand-roll the PATCH:

   ```bash
   python .claude/skills/task-readme-rewrite/scripts/apply_overview.py \
       --task-id <UUID> --env dev --bullets-file bullets.json --dry-run   # check first
   python .claude/skills/task-readme-rewrite/scripts/apply_overview.py \
       --task-id <UUID> --env dev --bullets-file bullets.json --also-env prod
   ```

   The script self-checks the draft against `scan_overview()` before writing, wraps the
   body as `{"task_blob": {...}}` (sending the raw blob sets columns named after its own
   keys — a bug that already shipped once), verifies the write landed, and re-scans after.
   Run `--dry-run` first every time.

If the task has a tour, re-read the tour's intro/markdown steps afterwards: they were
generated from the old wording and may quote it.

## Scan mode

```bash
python .claude/skills/task-readme-rewrite/scripts/readme_scan.py --env dev            # all ready tasks
python .claude/skills/task-readme-rewrite/scripts/readme_scan.py --env prod --enabled-only
python .claude/skills/task-readme-rewrite/scripts/readme_scan.py --env prod --task-id <UUID> --show
python .claude/skills/task-readme-rewrite/scripts/readme_scan.py --env dev --json > scan.json
```

Per task it reports a verdict (`clean` / `review` / `rewrite`) and the reasons, e.g.:

```
5b6549db  rewrite  overview: enumerates defects ("but repeated delivery and mixed-quality batches can create...") · objectives: names fix ("Align delivery timing with") · tips: mechanism ("Compare the queue's delivery timing") · verify: config/command ("Check the deployed local configuration at http://localhost:4566")
```

It is heuristic, read-only, and errs toward flagging. `rewrite` means at least one
section names a defect or fix; `review` means only soft signals (long objectives, file
paths in tips, `#` headings, dict-repr storage). Read the README before acting on either.

**The scanner is shape-aware.** It infers repair vs design/build from the task title
(`design|build|rework|create|implement`) and switches which standard it applies, so it no
longer reports the design/build house style as a defect. On a design/build task it:

- **skips** the repair-only checks (imperative objectives, "no team/role opener"), and
  tolerates exactly one file path in Tips — the permitted shipped-script mention;
- **adds** four signals of its own — objectives that are team-framed or carry a
  `because` clause, and Verify bullets that state pass conditions;
- **stops** treating "X exists but the team does not trust it" in the overview as
  enumerating defects, which is the approved design-task opening.

Two rules apply to both shapes and are flagged everywhere: Tips that mention grading, and
Tips that carry ports/URLs the platform already surfaces.

Title-based shape inference is a proxy, not ground truth — a design task titled
"Harden…" reads as repair. If the verdict's reasons look like they are applying the wrong
standard, call the shape yourself and ignore the mismatched lines.

## What this skill does not do

- It does not change planted defects, tests, scripts, or fixtures. README text only.
- It does not fix the prompt modules. Once a track has an approved rewrite, fold the
  rules into that track's `agent_prompts/.../*_prompt.py` README rules separately so
  future generations start out right (`pipeline-readme-tour-fixes` covers the master-level
  edits already made for headings and objective style).
