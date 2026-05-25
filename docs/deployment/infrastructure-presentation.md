arar# Deployment Infra Talk — Speaking Notes

> This is a script, not a doc. Read it like you'd actually say it.
> Open `deployment-infrastructure.excalidraw` on the side. ~10–12 min total.
> Italics = stage directions to yourself. Bracketed `[…]` = optional, drop if short on time.

---

## 0. Hook — start without the diagram

*(stand up, look around once, breathe)*

> "Okay so… umm, before I pull up the diagram, quick context. Right now, when a candidate takes our test, their environment runs on a DigitalOcean droplet. Mostly works, fine. But there's one failure mode we hit basically every week —
>
> — candidate closes their laptop mid-test and walks away. That's it. And their droplet just… sits there. Occupied. Forever. And then someone — *(point at self or someone)* — somebody has to SSH in and clean it up by hand. It's pure toil. No engineering value.
>
> So we looked at six replacements — Fargate, Fly Machines, K8s, Kata, vCluster, agent sandboxes — and picked one. E2B. In the next ten minutes I want to walk you through *why* we picked it, *what changes for the candidate*, and *what we have to build on the backend*. Cool? Chalo."

*(pull up the diagram, full screen)*

---

## 1. TODAY — the red box on the left (~2 min)

*(point at the red rectangle)*

> "Okay so, left side, red. This is what we have today. When I run `multiagent.py deploy-task`, it does — uhh — it reads the task row from Supabase, picks an idle droplet from `AVAILABLE_IPS`, SFTPs the files into `/root/task` on that droplet, then SSHs in and runs `bash run.sh`. Compose stack comes up. Done. *(small pause)*
>
> But… *(point at the five small red boxes)* …the problem is, state lives in five places. Five.
>
> One — Supabase says `is_deployed = true`. Fine.
> Two — the GitHub repo, that's the source of files.
> Three — the `/root/task` directory sitting on the droplet, which holds the *current* copy.
> Four — Docker state on the droplet — running containers, volumes, networks.
> Five — `AVAILABLE_IPS`, an env var, which we maintain by hand.
>
> And none of these is the single source of truth. Like — if someone asks me right now, 'what's running where?' — I have to SSH into every droplet, run `docker ps`, and cross-reference with Supabase. Every single time. That's the actual day-to-day pain."

*(point at the pain block)*

> "The abandoned-task scenario is the worst one — *(slow down here, this is the hook)* — candidate closes the laptop, network drops, or they just give up. `kill.sh` never fires. Containers, volumes, the `/root/task` folder — all of it just lingers. Next deploy hits that droplet, sees non-zero containers, skips it. And one by one, droplets become 'occupied.' Pool fills up, manual cleanup. *(shrug)* Toil.
>
> Cold start, by the way, is around 60 to 90 seconds. SFTP plus `compose up` plus DB readiness wait."

*(beat)*

> "So that's the problem. Now let's look at the fix."

---

## 2. TOMORROW — the green box on the right (~2 min)

*(walk to the right side of the diagram, point)*

> "Right side, green. The replacement is — agent sandboxes. E2B specifically. *(small wave)* The vendor name is interchangeable, the *category* matters more.
>
> Agent sandboxes came out of the AI ecosystem — basically built for OpenAI / Anthropic-style agents. The problem they solve maps almost one-to-one to ours: 'spin up an isolated Linux box, run code, capture output, tear down — programmatically.' Same thing.
>
> And the key shift is — *(tap the green box hard)* — the sandbox handle itself becomes the source of truth. No `AVAILABLE_IPS`, no SSH-and-poll. You call `Sandbox.list()` on the SDK and that's the inventory. That's it."

*(point at the four green capability boxes one by one, slow down)*

> "Four properties matter —
>
> *(tap box 1)* One — the SDK is the inventory. `create()`, `kill()`, `list()`. Done.
>
> *(tap box 2)* Two — *(this is the big one, emphasize)* — idle-timeout is built in. You set it once when you create the sandbox, and that's it. Candidate walks away? Sandbox kills itself. The signature failure mode of the droplet flow just… doesn't exist here. Gone.
>
> *(tap box 3)* Three — pause and resume. Candidate needs a break? Pause it. You get a full disk-and-memory snapshot for free, including in-flight DB transactions. They come back, instant resume.
>
> *(tap box 4)* Four — and this is the most important one for the team — `run.sh`, `kill.sh`, the Compose files, none of that gets rewritten. The sandbox is just a Linux box with Docker. Whatever runs on a droplet today runs on a sandbox tomorrow. *Zero* task migration."

*(point at the wins block)*

> "Numbers from the PoC — I actually built a `python-sql` template, ran a real fintech spend-summary task end-to-end —
>
> Cold start: 25 to 35 seconds. Faster than droplets, even though we're spinning a fresh microVM each time. *(shrug + small smile)* Per-second billing — idle costs us nothing. Atomic teardown — `sb.kill()` and the entire VM is gone. And if vendor lock-in ever becomes a worry — `e2b-dev/infra` is Apache 2.0, we can self-host. Escape valve exists."

*(short pause)*

> "Make sense so far? *(check the room)* Cool, moving on."

---

## 3. Candidate Browser — the blue strip in the middle (~2 min)

*(point at the blue browser strip)*

> "Now, the candidate's POV. This is actually my favourite part.
>
> On the candidate's laptop — they install nothing. Zero. No Docker, no Postgres, no SSH key, no Node, nothing. They just open the browser, and the test UI gives them four tabs. Iframes, basically. *(point at the four tabs)*"

*(walk through tabs, energetic)*

> "Tab one — **terminal**. `ttyd` running on port 7681 inside the sandbox. Browser xterm, full root bash. They can run `psql -h localhost`, `redis-cli`, `kubectl`, whatever. It all works because — it's localhost *inside* the VM. No network gymnastics.
>
> Tab two — **editor**. `code-server` on port 8443. Full VS Code in the browser. Live file edits, integrated terminal, extensions. The whole 'clone the repo to your laptop' step is just — gone.
>
> Tab three — **app preview**. Whatever they're building — FastAPI, React, Express — gets exposed on a port. They click, they see their app.
>
> Tab four — *(slow down)* — **DB / service console**. This one's important. Adminer for Postgres, RedisInsight for Redis, mongo-express for Mongo, kafka-ui for Kafka. We're not building anything custom — the ecosystem already ships a canonical web GUI for every popular service. We just adopt them."

*(point at the iframe URL caption)*

> "All four iframes follow the same URL pattern — `https://<port>-<sandbox-id>.e2b.app`. E2B fronts each sandbox with an L7 reverse proxy that terminates TLS and routes by hostname prefix. Clean."

*(pause, then point at the red caveat — be honest here)*

> "But… here's the thing. *(serious tone)* This proxy is HTTPS only. Strictly HTTPS. So if a candidate thinks 'I'll just `psql -h ... -p 5432` from my laptop' — *nope*. The proxy parses the binary StartupMessage as malformed HTTP and rejects the connection. It just times out.
>
> We actually validated this empirically in the PoC. *(small laugh)* Spent half a day thinking raw TCP would work, then realised — yeah, no. So the fix is to bake a web console into each template. Adminer, RedisInsight — covers about 95% of real usage. For power users we keep `wstunnel` as a Phase 3 opt-in, not now.
>
> Right? One caveat, called out transparently. Moving on."

---

## 4. Inside the Sandbox + Templates — the purple box (~1.5 min)

*(point at the purple box)*

> "Let's zoom in. What's actually inside one sandbox —
>
> Firecracker microVM. Same isolation primitive Lambda and Fargate use — proven, battle-tested. Inside that, Linux with a full Docker daemon. So yes — *Docker-in-Docker inside Firecracker*. This was *the* one technical risk we explicitly de-risked in the PoC. *(beat)* And it works. `docker compose up`, `docker pull postgres:15`, network create, volume create, init SQL — all clean. Verified."

*(point at the inner service boxes)*

> "Inside the sandbox, on a private Docker network, we run the same services we run on droplets today. Postgres, Redis, Mongo, the candidate's FastAPI or Express app, k3d if it's a K8s task. *Same* compose files. *Same* `init_database.sql`. The sandbox just hosts the daemon. *(shrug)* That's it."

*(point at templates note)*

> "Templates — we'll maintain about 6 to 8 total —
>
> `python-sql`, `python-fastapi`, `node-mongo`, `node-postgres`, `mern`, `react`, `java-spring`, `k8s-base`. A template is a Dockerfile plus a setup script, version-controlled in `e2b_flow/templates/`. CI rebuilds and registers them on PR merge.
>
> And per-task generation — that still produces the same `run.sh` and Compose files we ship today. Those just drop into the template at session start. Templates rarely rebuild. Tasks get generated all day. Decoupled."

---

## 5. End-to-end Flow — the yellow boxes at the bottom (~2 min)

*(walk to the bottom strip, sweep hand left to right)*

> "Okay, putting it all together. Candidate clicks Start — what happens?"

*(tap each yellow box)*

> "One — frontend. Candidate hits Start in `utkrushta-assessment`.
>
> Two — backend. `POST /sessions/start` comes in. Backend looks up `tasks.template_id` and `expected_ports`.
>
> Three — *(this is the meat)* — backend calls `Sandbox.create(template, timeout=2h)` on the E2B SDK. Then it git-clones the per-attempt repo into the sandbox. Then `bash run.sh`. Then probes the expected ports and collects the URLs.
>
> Four — Supabase has a new `sandbox_sessions` table. We insert a row — `sandbox_id`, status `active`, surfaces JSON, heartbeat timestamp. *That* is the source of truth for that session.
>
> Five — frontend renders `<SandboxLayout>` with the four iframe URLs. And it pings `/heartbeat` every 30 seconds while the tab is visible."

*(point at the bottom note about Submit + reconciler — slow this down, it's load-bearing)*

> "On Submit — backend runs pre-kill hooks. `pg_dump` to S3. Captures the final commit SHA from the attempt repo. Then `sandbox.kill()`. Marks the row `killed`. Triggers grading. Teardown is — *one second*. Atomic.
>
> Now — *(emphasize)* — this is the load-bearing piece — the **reconciler**. Background job, runs every 60 seconds —
>
> First check: any sandbox running on E2B *without* a Supabase row? That's an orphan. Kill it.
> Second check: any session active but heartbeat hasn't arrived past the idle window? Pause it. If it's been too long, expire it.
>
> So even if every other layer reports state wrong — frontend crash, backend crash, whatever — the reconciler converges to truth within 60 seconds. *That's* the safety net the droplet flow doesn't have. And this single piece is what permanently kills the 'someone SSHes in at 2am to clean up' scenario."

---

## 6. Closing — what stays, what's new, phasing (~1.5 min)

*(step back, hands together)*

> "Three things to take away —
>
> *(hold up one finger)* **One** — existing task content survives. `run.sh`, `kill.sh`, `docker-compose.yml`, `init_database.sql` — none of it gets rewritten. The sandbox is a Linux box. Same stuff runs. The diff is in *how* we provision and tear down, not in the tasks themselves. We don't touch tasks.
>
> *(two fingers)* **Two** — there's a parallel change on the GitHub side that isn't on the diagram, but I want to call out. Today we clone the canonical template repo using an org token. In Phase 2, every attempt gets a *fresh per-attempt private repo*. Two credentials — an SSH deploy key inside the sandbox, a fine-grained PAT for the candidate's laptop. Both get revoked at submit. Candidate can work in the sandbox, on their laptop, or both — all three are valid. And post-submit, we can optionally transfer ownership of the repo to the candidate's GitHub account — they keep it as a portfolio piece. *(small smile)* And they don't even need to log into GitHub unless they want to.
>
> *(three fingers)* **Three** — phasing. Phase 1 done — PoC validated end-to-end on hosted E2B with the `python-sql` template, real fintech task, all green. Phase 2 is backend work — `sandbox_sessions` table, `/sessions/*` endpoints, reconciler. Phase 3 is the frontend `<SandboxLayout>`. Phase 4 expands templates to 6–8 stacks. Phase 5 retires droplets. Phase 6 is optional — if volume crosses ~1500–2500 sandbox-hours per month, we self-host on Hetzner. Pays for itself in 1–2 months."

*(look around, slight smile)*

> "Bas, that's it. Questions? Happy to deep-dive any panel — the L7 caveat, the per-attempt repo model, the reconciler, the cost numbers, anything."

---

## Anticipated Q&A — quick draws

> *(answer in the same conversational register, don't switch to formal corporate)*

| Question | Quick reply |
|---|---|
| **What if E2B has an outage?** | Existing paused sessions become inaccessible, true. New sessions queue, or during the migration window we fall back to the legacy droplet path. Phase 6 has us self-hosting `e2b-dev/infra` on Hetzner — same SDK, our control plane. |
| **Sandbox escape risk?** | Firecracker microVM boundary — same one Lambda and Fargate use. The per-session E2B URL is the security boundary; consoles are unauthenticated in the PoC, Phase 3 adds a per-session token. |
| **What about K8s tasks?** | k3d preinstalled in `utkrusht-k8s-base`. Real `kubectl`, real K8s API on `localhost:6443`. Browser access via Headlamp or k9s-in-ttyd. |
| **Cost?** | At 2000 sessions/month × 2 hours each = 4000 sandbox-hours: roughly $800–2000 on E2B, $400–1200 on Daytona/Northflank. Self-host break-even is around 1500–2500 sandbox-hrs/mo. Below that, hosted wins. |
| **Why not Fargate / Cloud Run?** | 30–60s cold start, no Docker daemon → DinD scenarios break, no nesting → k3d won't run. That's it. |
| **Fly.io Machines?** | Honest answer — viable runner-up. Same Firecracker primitive. But you write the session lifecycle yourself. E2B gives you that abstraction for free. |
| **Vendor lock-in?** | `e2b-dev/infra` is Apache 2.0. Daytona OSS is a second escape hatch. Sleep well, options exist. |
| **What does the candidate lose?** | By default, local environment control. SSH opt-in is available from Phase 2+. Net positive for candidates without a strong local setup — and that's most of them. |

---

## Cheat sheet — bullet points to glance at

- **Today**: 5 sources of truth, abandoned droplets stay occupied, 60–90s cold start, manual cleanup.
- **Tomorrow**: sandbox handle = source of truth, idle-timeout self-cleans, 25–35s cold start, atomic teardown.
- **Candidate UX**: 4 iframes — terminal (ttyd), editor (code-server), app preview, DB console (Adminer/etc.).
- **Caveat**: HTTPS L7 only; raw TCP doesn't work → ship per-stack web consoles.
- **Inside**: Firecracker microVM + Docker daemon + Compose stack. DinD validated in PoC.
- **Templates**: ~6–8 per-stack. Tasks drop in at session start.
- **Backend**: new `sandbox_sessions` table; `/sessions/{start,heartbeat,pause,submit,end}`; reconciler every 60s.
- **GitHub**: per-attempt private repo, SSH deploy key + fine-grained PAT, both revoked at submit, optional ownership transfer.
- **Phasing**: PoC done → backend → frontend → templates → kill droplets → (maybe) self-host.

---

## Tone reminders to self

- Pause after the pain points. Let it land.
- Slow down on the L7 caveat — don't gloss it. Honesty here builds trust.
- "This is load-bearing" — actually emphasize the reconciler. People skim past it.
- Conversational English mostly. The occasional "chalo", "bas", "matlab" is fine where it flows naturally — don't force it.
- Don't read the diagram — *point* at it. Eyes on the room.
- If someone interrupts mid-section, finish the sentence, then take the question. Don't lose the thread.
