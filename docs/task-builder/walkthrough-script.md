# Task Builder — Walkthrough Script

> A spoken talk-track for presenting Task Builder to teammates or stakeholders.
> Companion to [`task-builder-architecture.md`](task-builder-architecture.md) —
> that doc is the *reference*; this is what you *say*.

---

## How to use this script

- **Length:** ~12 minutes of talking + Q&A. Time cues like `[3:30]` are
  guidance, not a stopwatch.
- **Audience:** technical-ish — engineers, or a mixed room. It assumes no prior
  knowledge of the task-generation pipeline.
- **Format of this script:**
  - **SAY** — the narration. It's written to be spoken; read it aloud, or
    paraphrase it in your own words.
  - **SHOW / DO** — stage directions: what to have on screen, what to click.
  - **IF ASKED** — pocket answers for questions that tend to come up *in that
    moment*. Longer Q&A is in [Appendix A](#appendix-a--qa-pocket-answers).
- **Before you start, have ready:**
  1. The server running — `python -m task_builder` — and reachable at
     `http://127.0.0.1:8000`.
  2. A browser tab open on that page, but **don't start chatting yet**.
  3. The architecture doc open in a second tab, for the under-the-hood section.
  4. A competency you *know* exists in the dev database, and one deliberately
     misspelled, for the validation demo.

---

## [0:00] — Opening: the problem

> **SHOW:** Slide or just your terminal. Nothing in the browser yet.

**SAY:**

"Before I show you Task Builder, let me describe the problem it solves.

Until now, creating a *single* coding-assessment task went like this. You'd
hand-write a couple of JSON files — one describing the competency, one for the
candidate background. Then you'd run four separate command-line tools, one after
another, in a specific order, where the output of each one is the input to the
next. Get the order wrong, or point one tool at the wrong file, and you wouldn't
find out until two steps later.

In practice that meant only the person who *built* the pipeline could run it
reliably. Everyone else filed a request and waited.

Task Builder fixes that."

---

## [1:00] — What it is, in one breath

> **SHOW:** Switch to the browser tab — the Task Builder page, bot greeting
> visible.

**SAY:**

"This is Task Builder. It's a small web app you run locally. You open this page,
a bot interviews you, you click one button, and it runs that entire four-tool
pipeline for you — showing you the live logs as it goes.

That's the whole product. The goal was simple: make it so *anyone* on the team
can produce a task, not just the pipeline's author. Turn a command-line chore
into a conversation."

> **IF ASKED — "Is this in production / hosted?"**
> "No — it's deliberately a local, single-user tool. It binds to localhost only.
> We'll come back to why that's a deliberate choice."

---

## [2:00] — The mental model: two phases

> **SHOW:** The architecture doc, section 1 — or just hold up two fingers.

**SAY:**

"If you remember nothing else from this talk, remember that Task Builder has
exactly **two phases**.

**Phase one is the interview.** The bot asks you questions and collects your
answers into a form. We call that form the **TaskBrief**. It has five fields:
the tech stack, the proficiency level, the role you're hiring for, the focus
areas the task should test, and a business domain to set the task in.

**Phase two is the generation.** Once that form is complete, you click Generate,
and a five-stage pipeline runs in the background to actually build the task.

Now — here's the one subtle thing about phase one that's worth saying out loud.
The bot is deliberately **not in charge**. It does not decide anything. It just
*collects* answers and *proposes* them. The **server** validates every answer
against real data, and the server alone decides when the form is complete enough
to generate. The bot proposes; the server disposes. That separation is what
keeps the thing trustworthy — a chatty language model can't talk its way into
generating a task with bad inputs."

---

## [3:30] — Live demo, part one: the interview

> **DO:** Click into the chat. Work through the interview for real.

**SAY (as you go):**

"Let me just use it. The bot opens by asking for a tech stack — I'll say
*Java, Spring Boot*.

Notice it asks for **one thing at a time**. It's not throwing a giant form at
me; it's a conversation. Next it asks for the proficiency level — I'll say
*intermediate*. Then the role, the focus areas, the domain."

> **DO:** When you reach a competency field, type a **deliberately wrong**
> competency name.

**SAY:**

"Now watch this. I'm going to misspell the tech stack on purpose.

See what happened — the bot came back and said it couldn't find that, and it
*suggested* the closest real matches. That's the validation I mentioned. Every
competency I give it is checked against our actual competency database. If it's
not real, it never enters the form — the bot apologises and re-asks, with
suggestions. So you can't accidentally generate a task for a tech stack that
doesn't exist."

> **DO:** Finish the five answers. The summary card appears.

**SAY:**

"And now that all five fields are filled, the bot summarises everything back to
me in this card — tech stack, level, role, focus areas, domain — and asks me to
confirm. *This card only appears when the form is genuinely complete.* That's the
server deciding, not the bot."

> **IF ASKED — "What if I tell it the level after the tech stack?"**
> "It handles that — order doesn't matter. It just needs a level *eventually* to
> validate the competency against."

---

## [6:00] — Live demo, part two: generation and live logs

> **DO:** Point at the environment picker on the summary card, then click
> **Generate task →**.

**SAY:**

"On the card there's an environment picker — dev or prod — that decides where
the finished task gets stored. I'll leave it on dev and click **Generate**.

Now phase two kicks in. The five stages run: a preflight check, then input
files, then scenarios, then the prompt, then the actual task creation.

Watch the chat. Each stage gets its own **collapsible panel**. The stage that's
*currently running* is expanded, and you can watch its log scroll in **real
time** — this isn't a spinner, it's the actual output of the tool as it
produces it. When a stage finishes successfully, its panel **collapses** to a
single green line with a duration. If a stage *fails*, its panel stays open so
you can see exactly what went wrong.

So at any moment you know precisely where the pipeline is and what it's doing.
That visibility is the second half of what makes this better than the command
line."

> **DO:** Let it run to completion (or cut to a pre-baked finished run if time
> is tight).

**SAY:**

"And when it's all done, you get a final bubble with the outcome — and on
success, a clickable link straight to the generated GitHub repository. That's
the task, built."

> **IF ASKED — "How does the browser get live logs?"**
> "Server-Sent Events — a one-way stream from server to browser. I'll show the
> mechanism in the next section."

---

## [8:00] — Under the hood: the architecture

> **SHOW:** The architecture doc, section 2 — the big-picture diagram.

**SAY:**

"Let me show you what's actually happening behind that chat window. It's
deliberately small — a FastAPI server and **nine short Python files**.

Follow a single chat message. The browser sends it to the server. The server
hands it to the **conversation module**, which makes **one call to the language
model** — through our Portkey gateway to Claude. The model replies with a small
JSON object: a message to show you, and any fields it learned. The server
validates those fields, merges the good ones into the TaskBrief, and sends the
reply back. One message in, one message out. That's the whole interview loop.

Now generation. When you click Generate, the server doesn't run the pipeline on
the request — it spawns a **background worker thread**. That thread runs the
**runner module**, which executes the five stages, each one as a subprocess.

And the live logs — here's the neat part. While each stage runs, a *second*
little thread, the **log tailer**, watches that stage's log files on disk and
pushes any new lines onto a queue. The server drains that queue and streams it
to your browser over Server-Sent Events. That's why you see output appear as
it's produced.

One more thing, and it's important: the runner **does not reimplement the
pipeline**. The pipeline already existed as a script called `run_pipeline.py`.
The runner *reuses* its stage helpers and just wraps them — adding the
event-streaming and the live log tailing. We didn't rebuild anything; we put a
conversational front-end and a live view on top of what was already there."

> **IF ASKED — "Why a thread and not async?"**
> "The pipeline stages are blocking subprocesses. A worker thread keeps them off
> the web request, and a queue carries events back to the async SSE response.
> Simple and good enough for a single-user local tool."

---

## [10:00] — Design decisions worth calling out

**SAY:**

"A few choices were deliberate, and they're worth knowing.

**One — the bot can't force generation.** Even if the model says 'ready', the
server independently re-checks that the form is actually complete before it
will run anything. Two safety nets, not one.

**Two — all the state lives in memory.** Sessions and runs are just dictionaries
in the server process. Restart the server and they're gone. For a local,
single-user tool that's a feature, not a flaw — there's no database to set up,
nothing to clean up.

**Three — the live-log feature was added without touching the server at all.**
The log tailer just emits the *same kind of event* the pipeline stages already
emit. It rode the rails that were already there. That's a sign of a clean
seam."

---

## [11:00] — Honest limitations

**SAY:**

"I want to be upfront about the rough edges, because they're easy questions and
you should own the answers.

- **Competency validation always uses the dev database** — even if you pick
  prod as your storage environment. If dev and prod ever drift apart, that's a
  gap.
- **State is lost on restart**, as I said — fine here, but it means this isn't
  something you'd leave running for days or share between people.
- **The chat is synchronous** — each message is a blocking call to the language
  model, so there's a short pause per turn.

None of these are bugs. They're scoped trade-offs for a local tool. But if
someone asks 'could we host this for the whole team', the honest answer is:
not without addressing those three first."

---

## [12:00] — Close

**SAY:**

"So, to wrap up.

Task Builder takes a job that used to need the pipeline's author and four
command-line tools run in exact order — and turns it into a conversation and a
button.

The architecture is small on purpose: a FastAPI server, a bot that interviews
you and fills a five-field form, a server that validates every answer, and a
thin wrapper that runs the *existing* pipeline in the background with the logs
streamed live to your screen.

The interview, and the generation. That's it. Happy to take questions."

---

## Appendix A — Q&A pocket answers

Crisp answers for questions that come after the talk.

**"Which language model does the bot use?"**
Claude — specifically Sonnet — reached through our Portkey gateway, the same way
the rest of the pipeline talks to its models.

**"What are the five stages exactly?"**
Preflight (a sanity check), input files, scenarios, the prompt, and finally task
creation. The first four prepare inputs; the last one actually builds and
eval-gates the task.

**"What happens if a stage fails?"**
The pipeline stops at the first failure. That stage's log panel stays expanded
so you can see why, and you get a final 'failed' bubble. Nothing partial is
silently shipped.

**"Is a task that fails the eval gate a success or a failure?"**
A failure. If the final stage generates a task but our eval gate rejects it,
Task Builder reports the run as failed — not a partial win.

**"Can two people use it at once?"**
Technically the server would accept it, but it's designed and intended as a
single-user local tool. Don't.

**"Why doesn't the bot ask how many scenarios to generate?"**
That's intentionally not the user's decision — it defaults automatically. The
bot is explicitly told never to bring it up.

**"How is this different from just running `run_pipeline.py`?"**
Same pipeline underneath. Task Builder adds two things: the conversational
interview that gathers and *validates* the inputs, and the live, per-stage log
view. It's a front-end and a window, not a new engine.

**"Where do the generated tasks end up?"**
In a GitHub repository, with the task stored in Supabase — dev or prod depending
on the environment picker. The final chat bubble links straight to the repo.

---

## Appendix B — the 3-minute version

If you only have a few minutes, say just this:

"Task Builder is a local web app that replaces a painful command-line workflow.

Making one coding-assessment task used to mean hand-editing JSON files and
running four CLI tools in the right order — a job only the pipeline's author
could do reliably.

Task Builder turns that into two steps. **One: a chat.** A bot interviews you
for five things — tech stack, level, role, focus areas, domain — and validates
every answer against real data as you go. **Two: a button.** When the form is
complete you click Generate, and it runs the five-stage pipeline in the
background, streaming each stage's live logs into the chat, and finishes with a
link to the generated repo.

Under the hood it's a small FastAPI server that wraps the *existing* pipeline —
it didn't reinvent anything. The bot only proposes inputs; the server validates
them and decides when to run. Conversation in, validated task out."
