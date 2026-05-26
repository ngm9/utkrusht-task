# E2B Templates & Registry

> **Status:** `utkrusht-python` shipped; other templates proposed. `template_registry` table is shipped, but the `build_cmd`/`test_cmd`/`compile_cmd` columns aren't actively read by `sandbox_eval` yet.
> **Updated:** 2026-05-26
> **Sister doc:** [Task Classifier](./classifier.md) — produces the `TaskRuntime` that picks which template to boot.
> **Open proposal:** [merge classifier output and template registry into one decision](./classifier.md#proposed-evolution-merge-taskruntime-and-template_registry-into-one-decision) — would turn each row in this registry into the capability sheet the classifier reads, with `no_match` becoming a first-class signal and templates becoming a fragmenting family (e.g. `utkrusht-python` → `utkrusht-python-llm`) driven by data signals. The schema sketch and migration path live in the classifier doc; the operational details for templates (fragmentation policy, sibling-vs-inheritance, manifest-hash-from-Dockerfile) are summarised there too.

## Problem statement — what is an E2B template, and why one per runtime?

An **E2B template** is a pre-built Firecracker microVM snapshot, registered with E2B by name (e.g. `utkrusht-python`). A sandbox boots from it in ~150 ms with **nothing installed at boot** — every dependency the task needs is already baked into the image.

[`e2b_flow/templates/python-sql/template.py`](../../e2b_flow/templates/python-sql/template.py):

```python
from e2b import AsyncTemplate

template = (
    AsyncTemplate()
    .from_image("e2bdev/code-interpreter:latest")
    .run_cmd("apt-get install -y postgresql-client netcat-openbsd ...")
    .run_cmd("install docker-ce docker-compose-plugin ...")  # DinD
    .run_cmd("pip install psycopg2-binary sqlalchemy pandas")
    .run_cmd("install ttyd ...")                              # browser terminal
    .run_cmd("dpkg -i code-server_4.96.4_amd64.deb")          # browser VS Code
    .run_cmd("install adminer ...")                           # DB GUI
    .copy("start.sh", "/usr/local/bin/start.sh")
    .set_start_cmd("sudo /usr/local/bin/start.sh", "sleep 20")
)
```

Built once via `python build_prod.py` → registered with E2B → boots as a snapshot. **Pip/npm/apt at runtime is exactly the wrong pattern.** The candidate gets a sandbox where `import fastapi` just works because FastAPI is already there.

### The intuitive plan that doesn't scale

A naive approach would be "one template per task type." The math kills it:

```
8 runtimes × 5 frameworks × 4 datastores × 3 messaging × … ≈ 480+ templates
```

That's a maintenance disaster. Every new framework or DB combination becomes a new template to build, ship, and update.

### The actual shape

A template carries **runtime + lane** (e.g. Python + web frameworks, Node + mobile, Python + LLM libs). Service containers (Postgres, Redis, Mongo, Kafka) are NOT in the template — they come from the **task's own `docker-compose.yml`**, started by `docker compose up` inside the sandbox via Docker-in-Docker.

```
┌──────────────────────────────┬──────────────────────────────┐
│ Owner: Platform              │ Owner: Each task             │
├──────────────────────────────┼──────────────────────────────┤
│ E2B template                 │ docker-compose.yml           │
│  • Runtime SDK (Python, JDK) │  • postgres-server           │
│  • Lane libraries (fastapi,  │  • redis-server              │
│    spring-boot, ...)         │  • mongo-server              │
│  • DinD (Docker daemon)      │  • kafka-broker              │
│  • Browser tools             │ run.sh / kill.sh             │
│  • ~11 templates total       │  • compose up / compose down │
└──────────────────────────────┴──────────────────────────────┘
```

Template count is bounded by **runtime × framework-lane**, NOT by databases × messaging × everything else. That's the design trick that makes the maintenance surface tractable.

This is confirmed by `DEFAULT_PROBE_PORTS` in [`e2b_flow/sandbox_manager.py`](../../e2b_flow/sandbox_manager.py):

| Ports baked into the template | Ports the task brings via compose |
|---|---|
| 7681 (ttyd), 8443 (code-server), 8080 (Adminer) | 5432 (Postgres), 6379 (Redis), 27017 (Mongo) |
| Plus 8000/3000/5000 — the candidate's app dev server | |

---

## Why do we need a `template_registry` table?

This is the **real architectural question**, and it deserves an honest answer.

### Your intuition is half right

"Why is `build_cmd` / `test_cmd` / `compile_cmd` in a runtime-level table? Each task is different — each task has its own `requirements.txt`, its own tests, its own code."

**True. But there are two different things going on:**

| What's task-specific | What's runtime-specific |
|---|---|
| The **content** to operate on: `requirements.txt`, the test files, the source code | The **command shape** for that runtime's tooling |
| `requirements.txt` (different per task) | `pip install -r requirements.txt` (same for every Python task) |
| Test files (different per task) | `python -m pytest -q --tb=short` (same for every Python task) |
| Source code | `python -m compileall -q .` (same for every Python task) |

Different Python tasks use different libraries, but they all install them the same way: `pip install -r requirements.txt`. Different Java tasks use different Maven dependencies, but they all build the same way: `mvn package`. The **command** is a property of the language's tooling — not of any individual task.

So `template_registry` stores the *runtime's idiomatic build/test recipe*, and the task's `requirements.txt` (or `pom.xml`, or `package.json`) is the input that recipe operates on. They're orthogonal.

### What `template_registry` actually does

Schema:

| column | type | role |
|---|---|---|
| `runtime` | `text` PK | `python`, `node`, `java`, `go`, … |
| `template_name` | `text` | E2B template id, e.g. `utkrusht-python` |
| `build_cmd` | `text` | e.g. `pip install --break-system-packages -r requirements.txt` |
| `test_cmd` | `text` | e.g. `python -m pytest -q --tb=short` |
| `compile_cmd` | `text` | e.g. `python -m compileall -q .` (optional) |
| `needs_browser` | `bool` | for Playwright lanes |
| `description` | `text` | what's baked into the image |
| `status` | `text` (added 2026-05-26) | `built` / `proposed` / `deprecated` — see "Why only one row is `built`" below |

### Current rows in the registry

After [`2026-05-26-template-registry-add-status-and-proposed-rows.sql`](../../migrations/2026-05-26-template-registry-add-status-and-proposed-rows.sql), every runtime in the `TaskRuntime.runtime` Literal has a row:

| runtime | template_name | build_cmd | test_cmd | status |
|---|---|---|---|---|
| `python` | `utkrusht-python` | `pip install --break-system-packages -r requirements.txt` | `python -m pytest -q --tb=short` | **`built`** |
| `node` | `utkrusht-node` | `npm ci` | `npm test` | `proposed` |
| `java` | `utkrusht-java` | `mvn -q -DskipTests package` | `mvn -q test` | `proposed` |
| `php` | `utkrusht-php` | `composer install --no-progress` | `vendor/bin/phpunit` | `proposed` |
| `go` | `utkrusht-go` | `go mod download` | `go test ./...` | `proposed` |
| `rust` | `utkrusht-rust` | `cargo build --quiet` | `cargo test --quiet` | `proposed` |
| `flutter` | `utkrusht-flutter` | `flutter pub get` | `flutter test` | `proposed` |
| `ruby` | `utkrusht-ruby` | `bundle install --quiet` | `bundle exec rspec` | `proposed` |
| `scala` | `utkrusht-scala` | `sbt -batch compile` | `sbt -batch test` | `proposed` |
| `none` | — | — | — | (no row — db_only / non_code tasks always skip the gate) |

### Why only one row is `built`

An E2B template isn't a database row — it's a **microVM snapshot built with `python build_prod.py`, uploaded to E2B's registry, and given a name** (e.g. `utkrusht-python`). Inserting a `template_registry` row for `utkrusht-java` doesn't conjure the template into existence; the gate would still fail with "template not registered" when it tries to boot.

So the `status` column carries the truth:

- **`built`** — there's a real E2B template registered with this name. `_get_template` returns the row, `sandbox_eval` boots successfully.
- **`proposed`** — the row documents intent (recipe captured, template_name reserved) but no E2B template exists yet. `_db_load_template` filters these out with `.eq("status", "built")` so the gate cleanly skips with `no_template` — same behaviour as before this migration, just now backed by visible SQL data.
- **`deprecated`** — for templates we've removed; same filter behaviour as `proposed`.

The proposed rows pay off when each template gets built:

1. Build the E2B template (`python build_prod.py`, ~1 hour per template).
2. Verify it boots and runs tests for a sample task.
3. **One SQL line**: `UPDATE template_registry SET status='built' WHERE runtime='node'`. Done — the gate now boots it for every Node task without a code change.

### Composition caveat — the 11-template hierarchy isn't in here yet

The "Template hierarchy" section below proposes ~11 templates including composition leaves like `utkrusht-python-sql` / `utkrusht-python-web` / `utkrusht-python-llm` — three templates sharing `runtime="python"`. **The current schema can't hold this.** `runtime` is the primary key, so only one row per language is allowed.

Storing the full leaf hierarchy requires schema evolution:
- Drop `runtime` as PK, use `template_name` as PK
- Keep `runtime` as a non-unique FK column
- Add a `lane` column (e.g. `sql` / `web` / `llm` / `base`) to disambiguate leaves
- Update `_get_template` from a single-key lookup to a (runtime, lane) lookup driven by the picker function

That's a follow-up migration. For now the registry holds **one row per language**, the picker function in `template_name_for_runtime` is what it is, and the composition-leaf design is captured in this doc as the target architecture.

## Fat templates vs composition — what should we actually do?

This is a real design question and the doc's original answer (~11 composition leaves) is probably the wrong one at our scale. Let me lay out the trade-off honestly.

### What "fat templates" means

One template per runtime, baking **everything common for that runtime**:

```
utkrusht-python      Python + all common DB drivers (psycopg2, pymongo, redis-py, mysqlclient)
                     + all common frameworks (fastapi, flask, django, uvicorn, sqlalchemy)
                     + all common LLM libs (langchain, llama-index, openai, anthropic)
                     + pandas, numpy, pytest, +DinD, +browser tools
                     → ONE image, ANY Python task.

utkrusht-node        Node + all common frameworks (express, next, react, jest, vitest)
                     + react-native CLI, expo
                     + +DinD, +browser tools
                     → ONE image, ANY Node task.
…
```

This is exactly what `utkrusht-python` already **is** today. Look at the row in `template_registry`: "Fat base: fastapi, flask, django, sqlalchemy, redis, pymongo, langchain, llama-index, pandas, numpy, pytest." The doc proposed splitting it into 3 leaves (`python-sql`, `python-web`, `python-llm`) — but the deployed version is one fat template.

### What "composition" means

A base template per runtime, plus leaves per framework lane, glued together with E2B's `from_template()`:

```
utkrusht-python-base    Python + DinD + browser tools + common runtime deps
   ├── utkrusht-python-sql       +postgres tooling
   ├── utkrusht-python-web       +fastapi/flask/django
   └── utkrusht-python-llm       +langchain/llama-index
```

Smaller leaves, layer-cache shared. The doc's aspirational design.

### Head-to-head

| Concern | Fat templates | Composition |
|---|---|---|
| **Number of templates** | ~8 (one per runtime + playwright + infra special-cases) | ~13 (7 roots + 6 leaves) |
| **Image size per template** | ~3–4 GiB | ~1.5 GiB base + ~200 MiB per leaf |
| **Total storage on E2B** | ~25 GiB (Pro tier: 20 GiB — slightly over, may need bump) | ~12 GiB (comfortable) |
| **Cold-start latency** | ~150 ms (snapshot size doesn't matter) | ~150 ms (same) |
| **Start-cmd latency** | ~3–8 s (dockerd + ttyd + code-server) | ~3–8 s (same — independent of image size) |
| **Picker function complexity** | Trivial: `runtime → template_name` | Multi-axis: `(runtime, kind, frameworks, datastores, needs_browser) → template_name`. Half the existing `pick_template()` is disambiguation. |
| **Schema fit** | One row per runtime — current schema fits | Needs PK change + `lane` column + picker rewrite |
| **Adding a new framework** | Either do nothing or rebuild the fat template once | Either rebuild a leaf, build a new leaf, or push into the base |
| **Dependency-conflict risk** | Higher — everything coexists in one venv | Lower — each leaf only carries its lane |
| **Security surface** | Higher — more installed packages = larger CVE surface | Lower |
| **"Missing template" failure** | Doesn't exist — any Python task can use `utkrusht-python` | Combo not anticipated as a leaf has no template; gate skips |

### The size argument is weaker than it looks

At our scale, the headline "composition saves disk" argument doesn't survive scrutiny:

- **E2B Pro tier ships 20 GiB storage.** 8 fat templates × ~3 GiB ≈ 24 GiB. Slightly over — needs a tier bump or some pruning. Not a blocker.
- **Cold-start latency is constant regardless of image size.** Firecracker boots from a snapshot in ~78–180 ms whether the image is 500 MiB or 5 GiB. Verified in the SDK section below.
- **Start-cmd latency is also independent.** The 3–8 s before a sandbox is "ready" is dockerd + ttyd + code-server warming up — not loading the image off disk. Same number either way.
- **User-perceived latency: zero difference between fat and composition.**

### What we should actually do — recommendation

**Fat templates, with two special-case branches.** Concretely:

| Template | Runtime | Bakes in | Notes |
|---|---|---|---|
| `utkrusht-python` ✅ | python | All common DB drivers, frameworks, LLM libs, pandas, pytest | What's deployed today. |
| `utkrusht-node` | node | express, react, next, ts, jest, vitest, react-native, expo | Fat — covers web AND mobile. |
| `utkrusht-java` | java | JDK 17, maven, gradle, spring-boot, hibernate, JUnit | Fat. |
| `utkrusht-php` | php | php-fpm, composer, laravel, phpunit | Fat. |
| `utkrusht-go` | go | Go toolchain + common libs (gin, chi, sqlx) | Static binaries — toolchain is tiny anyway. |
| `utkrusht-rust` | rust | cargo + tokio, serde, sqlx, axum | Fat by Rust standards but still small. |
| `utkrusht-flutter` | flutter | Dart SDK + flutter + emulator | Standalone. Mobile tasks have no compose. |
| `utkrusht-playwright` *(special-case)* | node | node base + chromium-headless + playwright | Chromium adds ~300 MiB; worth a separate image. |
| `utkrusht-infra` *(proposed)* | (none) | kubectl + helm + terraform + kind/k3d | For `kind="infra"` tasks (see classifier doc). |

**~9 templates total.** The schema fits today (one row per runtime, plus playwright and infra as additional rows — would need the `template_name` PK evolution noted above for those two special-cases, but only for them, not for the whole hierarchy).

### Why this is the right default

1. **It's what already works.** `utkrusht-python` is fat, ships everything Python, runs every Python task today without issue. Composition leaves were aspirational; fat is operational.
2. **Picker function shrinks dramatically.** Today `pick_template()` has 11 lines disambiguating leaves. With fat templates: 8 lines, one per runtime, no overlap logic.
3. **The dependency-conflict risk is real but manageable.** When LangChain + Django + Pinecone actually conflict, that's the day you split `python-llm` as a leaf. Don't pre-split before the conflict exists.
4. **Cold-start is constant.** The biggest perceived-cost argument against fat is wrong: image size doesn't affect boot time.
5. **"Missing template" is a worse failure mode than "slightly large template."** When a candidate's combo doesn't match any leaf, the gate skips with `no_template` and a real task ships unverified. With fat templates, this can't happen as long as the runtime has a template at all.

### When you'd actually split (the right reasons)

- **Genuine dependency conflict.** If LangChain pins `pydantic<2` and FastAPI requires `pydantic>=2`, you can't put both in one image. Split into `python-llm` + `python-web`.
- **Heavy outlier libs.** Chromium for Playwright (~300 MiB). CUDA for ML training (~1 GiB). These genuinely justify a special-case template.
- **Security boundary.** If a customer needs a no-LLM template for compliance reasons, split it.
- **Image-size headroom exhausted.** If E2B Pro hits its limit and a tier bump isn't acceptable.

None of these apply today. **Default to fat. Split when forced.**

### What this means for the doc below

The "Template hierarchy" section below shows the composition design. **Treat it as historical aspiration, not current direction.** The recommendation above is what the registry should actually look like. The doc will get rewritten to lead with fat templates once you've decided to commit (this section is the proposal that triggers that rewrite).

### The honest case for / against

**For** — three real reasons:

1. **Update safety.** When (not if) Python's idiomatic test command evolves — new pytest flag, new test runner — it's a one-row `UPDATE` in `template_registry`. The alternative (the build/test command stored on every classification-registry row) requires updating N rows and risks drift between them.
2. **Adding a runtime is data, not code.** Want Java support? Insert one row into `template_registry`. No edit to `sandbox_eval.py` to fork on `runtime == "java"`. Especially valuable as Node/Java/Go support lands.
3. **One source of truth for "what command runs this runtime?"** Today only `sandbox_eval` reads this. Tomorrow when E2B-based deploy ships, the deploy path reads the same row. The gate and deploy can't drift.

**Against** — be honest:

1. **Today, the columns aren't actually read.** [`sandbox_eval.py`](../../e2b_flow/sandbox_eval.py) hardcodes the same strings:
   ```python
   _run(sb, "pip install --break-system-packages -r requirements.txt", ...)
   _run(sb, "python -m pytest -q --tb=short", ...)
   _run(sb, "python -m compileall -q .", ...)
   ```
   These match the seeded `template_registry.python` row by construction, but nothing in code re-reads them at runtime. So today the registry is **forward scaffolding** — it pays off when the multi-runtime gate refactor lands, not before.
2. **Only one consumer today.** Just `sandbox_eval` (via `template_name_for_runtime`). Deploy doesn't read it yet. So the "single source of truth across consumers" benefit is theoretical until deploy lands.
3. **Drift risk while the columns are unused.** Someone could change the Python build command in `sandbox_eval.py` and forget to update the seeded row. Nothing would break, because the row isn't read — but you've now got two sources documenting different things.

### So what should we do?

Three options, in order of how I'd recommend them:

1. **Wire `sandbox_eval` to read from the registry.** ~15 LOC change. Eliminates the drift risk *and* validates the registry pattern now instead of when you're under pressure adding Java/Node. The change:

   ```python
   # in sandbox_eval.py, where _TEMPLATES is read today
   from generators.task.runtime_resolver import _get_template

   def run_sandbox_eval(code_files, task_runtime):
       spec = _get_template(task_runtime.runtime)
       if not spec:
           return _finish(skipped, "no_template")
       _run(sb, spec.build_cmd, ...)
       _run(sb, spec.test_cmd, ...)
       if exit_code == 5 and spec.compile_cmd:
           _run(sb, spec.compile_cmd, ...)
   ```

   **Recommended.** Small change, real consolidation, validates the design.

2. **Keep the columns as scaffolding (current state).** No code change. Risk: drift between the seed row and hardcoded literals. Pay off later when adding Java.

3. **Drop the columns until they're needed.** Pure YAGNI. Migration is trivial. Re-add when wiring Node/Java. Honest, but loses the "one INSERT to add a runtime" benefit you've already paid for.

### Why not put `build_cmd` on the combo row instead?

That was the *first* design instinct ("classify and store everything together"). It's wrong:

- 50+ combos × identical Python build command = 50+ copies of `"pip install --break-system-packages -r requirements.txt"`. Update once → fan-out across all rows.
- Adding a new combo doesn't change the build command — but you'd be writing the value anew on every classification-registry insert.
- The `build_cmd` is a function of `runtime`, not of `combo_key`. That's the textbook case for normalization (3NF).

Storing build_cmd on the combo row would be denormalisation that propagates the same value redundantly. The two-table split with FK is the right normalised shape.

### `run.sh` vs `build_cmd` — who runs what, when

Natural follow-up: each task already ships a `run.sh`. Why does the eval gate need separate `build_cmd` / `test_cmd` columns instead of just executing it?

Because they serve different consumers at different points in the lifecycle.

|                      | `run.sh` (task-owned)                                            | `build_cmd` / `test_cmd` (registry-owned)            |
| -------------------- | ---------------------------------------------------------------- | ---------------------------------------------------- |
| **Runs when**        | Candidate's session starts                                       | Eval gate, before the task ships                     |
| **Process shape**    | Long-running — `docker compose up`, seed DB, start dev server    | Short-lived — install deps, run pytest, exit         |
| **Exit semantics**   | "Server is up" — no exit code to grade against                   | `0` = pass, `1` = test failure, `5` = no tests       |
| **Scope**            | Per task (different services, seeds, dev-server invocation)      | Per runtime (every Python task installs the same way)|
| **Consumer**         | The candidate, in their IDE / terminal                           | The platform's pre-flight quality gate               |

Three concrete reasons the gate can't just execute `run.sh`:

1. **`run.sh` doesn't exit.** It runs `docker compose up && python app/main.py` — the dev server runs forever. The gate needs a process that ends so it can read an exit code. Wrapping the script in a timeout and parsing stdout for "did pytest pass?" is fragile in a way that `pytest; echo $?` isn't.
2. **The test command is a property of the runtime, not the task.** Every Python task runs `pytest`; every Node task runs `npm test`. Embedding that in each task's `run.sh` means every prompt-generator output has to remember the right invocation — drift (`pytest` vs `python -m pytest`, `--tb=short` vs not) becomes per-task instead of fixed by the platform.
3. **The orchestration is opposite.** The gate wants: copy code in → install deps → run tests → kill. The candidate wants: bring up services → keep the dev server running → expose ports to a browser. Same template, opposite lifecycle.

So the registry columns aren't a duplicate of `run.sh` — they're the platform's pre-flight checklist that runs **before** any candidate ever sees `run.sh`, and they're never invoked at candidate runtime.

---

## Template hierarchy — composition-aware

Final shape, based on E2B SDK capabilities verified against the v2 SDK:

```
utkrusht-python-base   from_python_image()
                       + DinD, ttyd, code-server, adminer, compose-shim, common deps
   ├── utkrusht-python-sql       from_template("utkrusht-python-base") + psycopg2, sqlalchemy, postgresql-client
   ├── utkrusht-python-web       from_template("utkrusht-python-base") + fastapi, flask, django, uvicorn
   └── utkrusht-python-llm       from_template("utkrusht-python-base") + langchain, llama-index, openai, anthropic

utkrusht-node-base     from_node_image()
                       + DinD, ttyd, code-server, adminer, compose-shim
   ├── utkrusht-node-web         from_template("utkrusht-node-base") + express, react, next, typescript, jest
   ├── utkrusht-node-mobile      from_template("utkrusht-node-base") + react-native, expo
   └── utkrusht-playwright       from_template("utkrusht-node-base") + chromium-headless, playwright

utkrusht-java-base     from_debian_image() + JDK 17 + maven + gradle + DinD + browser tools
   └── utkrusht-java-spring      from_template("utkrusht-java-base") + spring-boot starters

# stand-alone (no leaves yet):
utkrusht-php-laravel   from_debian_image() + php-fpm + composer + laravel + DinD + browser tools
utkrusht-go-base       from_debian_image() + go toolchain + DinD + browser tools
utkrusht-rust-base     from_debian_image() + cargo + common crates + DinD + browser tools
utkrusht-flutter       from_debian_image() + dart SDK + flutter + browser tools  (no DinD)
```

**Effective maintenance surface:** 7 roots + ~6 leaves = ~13 template files. Each leaf is ~20 LOC because of `from_template()` composition.

### Common boilerplate baked into every template

- Docker daemon (DinD) so tasks can `docker compose up` against their own compose file
- `ttyd` browser terminal on port 7681
- `code-server` browser VS Code on port 8443
- Adminer browser DB GUI on port 8080 (any SQL DB task uses this)
- Compose v1→v2 shim, `netcat-openbsd`, `git`, `jq`

### One template lineage, used for both eval and deployment

We do **not** maintain "eval templates" and "deploy templates" as separate sets:

| Why not | Detail |
|---|---|
| **Production parity** | Anything that passes eval must run on the template the candidate actually gets. A split would re-introduce F12-class bugs at the template layer ("eval template was fine, deploy template missing a library"). |
| **Single source of truth** | Adding a Python package means updating one template, not two. |
| **"Dead weight" cost is negligible** | Browser tools running during automated eval are background processes on a microVM. They cost nothing observable. |
| **Boot time is fine for eval** | Even 5–10 s per eval is acceptable — eval runs at task-generation time, not per candidate request. |

The eval gate boots a sandbox from the same template the candidate would receive, copies the task code in, runs the test suite, captures pass/fail + stderr/stdout, then kills the sandbox. Candidates get the same template, with a longer idle timeout and the browser URLs exposed.

---

## E2B SDK capabilities — verified

| Finding | Detail |
|---|---|
| **Template composition / inheritance** — YES | `AsyncTemplate().from_template("utkrusht-python-base")` chains from a parent. Plus layer-level cache sharing across templates within a team. |
| **Multi-container natively** — NO | No first-class sidecar primitive. Documented pattern: Docker-in-Docker + the task's own compose. This is exactly what `python-sql` already does. |
| **Account-level limits** — not a constraint | Pro tier: 100 concurrent sandboxes (expandable to 1100), 24-hour sessions, 20 GiB storage. 13 templates × ~1.5 GB fits comfortably. |
| **Cold-start latency** — ~78–180 ms | Firecracker microVM snapshot boot. The "5–10 s" earlier drafts worried about is **start-cmd execution** (dockerd + ttyd + code-server initialising), not the snapshot itself. |
| **Best-practice base image** | Use language-specific convenience methods (`from_python_image()`, `from_node_image()`, etc.), not the heavier `e2bdev/code-interpreter`. |

### Design consequences

1. **Use language-specific base methods**, not `e2bdev/code-interpreter`. Leaner.
2. **Embrace `from_template()` for composition.** Build base templates once, derive leaves with ~20 LOC each.
3. **DinD stays.** No design change; the task's own `docker-compose.yml` brings up its services.
4. **Don't pre-optimise image size.** 20 GiB of headroom on Pro covers any reasonable shape.
5. **Cold-start is dominated by start-cmd, not snapshot.** If eval-gate latency ever matters, profile `start.sh`; the VM boot itself is ~150 ms.

---

## Template picker — `TaskRuntime` → template name

Mechanical mapping (lives in [`generators/task/runtime_resolver.py`](../../generators/task/runtime_resolver.py) via `template_name_for_runtime`):

```python
def pick_template(rt: TaskRuntime) -> str:
    if rt.kind == "mobile" and rt.runtime == "flutter": return "utkrusht-flutter"
    if rt.kind == "mobile" and rt.runtime == "node":    return "utkrusht-node-mobile"
    if rt.kind == "testing" and rt.needs_browser:       return "utkrusht-playwright"
    if rt.kind == "llm":                                return "utkrusht-python-llm"
    if rt.runtime == "python" and "postgres" in rt.datastores:
                                                        return "utkrusht-python-sql"
    if rt.runtime == "python" and rt.frameworks:        return "utkrusht-python-web"
    if rt.runtime == "node":                            return "utkrusht-node-web"
    if rt.runtime == "java":                            return "utkrusht-java-spring"
    if rt.runtime == "php":                             return "utkrusht-php-laravel"
    if rt.runtime == "go":                              return "utkrusht-go-base"
    if rt.runtime == "rust":                            return "utkrusht-rust-base"
    raise ValueError(f"no template for {rt}")
```

Service containers are NOT a picker concern — they're brought by the task's compose file.

---

## What changes in generated task content

The prompt generator used to instruct the LLM to produce `run.sh` and `kill.sh` that install Docker, install the language runtime, install system packages, then bring up services. That made sense for the droplet target (bare VM). For the E2B target, **most of that boilerplate is already in the template** and should be stripped.

`run.sh` and `kill.sh` themselves **stay** — they remain the contract between task and platform. What goes inside them changes.

### Before (droplet-shaped)

```bash
# run.sh
apt-get update
apt-get install -y python3 python3-pip postgresql-client docker.io
pip install -r requirements.txt
docker compose up -d
psql -h localhost -U postgres < seed.sql
python app/main.py
```

### After (sandbox-aware — template provides infra)

```bash
# run.sh
docker compose up -d              # task's own compose for postgres-server
psql -h localhost -U postgres < seed.sql
python app/main.py
```

Same shape for `kill.sh` — drop the uninstall steps; keep `docker compose down`.

### Where this lands in the prompt-generator

The HARD CONSTRAINT block in [`generators/prompts/agent.py`](../../generators/prompts/agent.py) now reads:

```
The TaskRuntime fields determine the generated content:
  • runtime, frameworks, libraries — already pre-installed by the E2B template.
    Do NOT include apt-get install, pip install, or npm install for these in run.sh.
  • datastores — generate a docker-compose.yml that brings up these service
    containers (Postgres, Redis, Mongo, …). run.sh does `docker compose up`,
    kill.sh does `docker compose down`.
  • kind="mobile" — no Dockerfile, no compose; the template ships the SDK.
    run.sh runs the runtime's native test command (e.g. `flutter test`).
  • needs_browser — the template (utkrusht-playwright) already ships chromium;
    do NOT install it in run.sh.
```

The classifier output drives this. See [Task Classifier](./classifier.md) for the upstream side.

---

## Worked examples — TaskRuntime → Template

| Task | TaskRuntime | Template | Task's compose |
|---|---|---|---|
| `Python - FastAPI` | runtime=python, frameworks=(fastapi,), kind=app | `utkrusht-python-web` | (none) |
| `Python - FastAPI + Postgres` | runtime=python, frameworks=(fastapi,), datastores=(postgres,), kind=app | `utkrusht-python-sql` | postgres-server |
| `Flutter` | runtime=flutter, kind=mobile | `utkrusht-flutter` | (none) |
| `Golang, Redis` | runtime=go, datastores=(redis,), kind=app | `utkrusht-go-base` | redis-server |
| `Playwright` | runtime=node, kind=testing, needs_browser=True | `utkrusht-playwright` | (none) |
| `Python + LlamaIndex` | runtime=python, frameworks=(llama-index,), kind=llm | `utkrusht-python-llm` | (none) |
| `Java + Spring Boot + Postgres` | runtime=java, frameworks=(spring-boot,), datastores=(postgres,), kind=app | `utkrusht-java-spring` | postgres-server |
| `MySQL` (alone) | runtime=none, datastores=(mysql,), kind=db_only | `utkrusht-python-sql` (reused; has psql client + Adminer) | mysql-server |
| `MERN Stack` | runtime=node, frameworks=(express, react), datastores=(mongo,), kind=app | `utkrusht-node-web` | mongo-server |
| `Firebase + React Native` | runtime=node, frameworks=(react-native, firebase), kind=mobile | `utkrusht-node-mobile` | (none) |

Ten wildly different tasks, all assembled from **~11 templates + each task's own compose**.

---

## Implementation status (2026-05-26)

| Component | Status | Where |
|---|---|---|
| `template_registry` table (B6) | **Shipped** — migration + python seed row | [migration](../../migrations/2026-05-25-create-template-registry.sql) |
| `template_registry.status` column + rows for every runtime | **Shipped (2026-05-26)** — python=built, node/java/php/go/rust/flutter/ruby/scala=proposed | [migration](../../migrations/2026-05-26-template-registry-add-status-and-proposed-rows.sql) |
| `template_name_for_runtime` helper | **Shipped** | [`generators/task/runtime_resolver.py`](../../generators/task/runtime_resolver.py) |
| `e2b_flow/sandbox_eval.py` reads template name from registry | **Shipped** | — |
| `e2b_flow/sandbox_eval.py` reads `build_cmd`/`test_cmd`/`compile_cmd` from registry | **Proposed** (today hardcoded — see "What we should do") | — |
| E2B build/test gate (Python only — `utkrusht-python`) | **Shipped** | [`e2b_flow/sandbox_eval.py`](../../e2b_flow/sandbox_eval.py) |
| Additional templates (node-web / node-mobile / java-spring / php-laravel / go-base / rust-base / flutter / playwright / python-llm) | **Proposed** — design only | — |
| `from_template()` composition (base + leaves) | **Proposed** — depends on building the templates | — |
| `from_python_image()` etc. base-method migration | **Proposed** — replace `e2bdev/code-interpreter` in `python-sql` | — |

---

## What we should do next

1. **Wire `sandbox_eval` to read commands from `template_registry`** (~15 LOC). This is the small change that turns the registry from "stored but unused" into "actively consumed." It also validates the pattern before you're under pressure to add a second runtime. See "Why do we need a `template_registry` table?" above for the case.
2. **Build the second template** (`utkrusht-node-base` + a leaf like `utkrusht-node-web`). This forces the multi-runtime path to work end-to-end and exercises the registry for real.
3. **Decide on the merged-model direction.** Before building the second template, consider the open proposal in the classifier doc to [merge classifier output and template registry into one decision](./classifier.md#proposed-evolution-merge-taskruntime-and-template_registry-into-one-decision). If you go that way, the second template should land with `personas: text[]` and a generated `manifest_hash` from day one — both are prerequisites for the merge, and retrofitting them onto a growing template set is harder than starting with them.
4. **Defer the full ~11-template buildout** until you have demand. The current single-template setup handles the largest task chunk (Python).
5. **Profile `start.sh` if eval-gate latency becomes a problem.** The microVM boot is ~150 ms; everything above that is start-cmd (dockerd warm-up, etc.). Don't pre-optimise image size — 20 GiB headroom on Pro covers anything reasonable.
6. **Once `kind="infra"` becomes a real need** (K8s / Helm / Terraform tasks), build a `utkrusht-infra` template with `kubectl`, `helm`, `terraform`, and a fake/lightweight cluster (kind / k3d) for validation. The gate then runs `helm lint` / `kubectl --dry-run` / `terraform validate` instead of pytest. *(If the merged-model proposal has shipped by then, this template's row will be a no-match's `suggested_template` — the doc-driven roadmap becomes data-driven.)*

---

## Out of scope (for now)

- E2B SDK capability verification beyond what's listed above — separate spike if anything new in the SDK surfaces.
- Building the ~10 additional templates — separate epic, designs above.
- The droplet → E2B deploy migration for tasks already running on droplets — outside this doc's concern.
- v2 multi-tenancy on templates (per-org template forks) — not on the roadmap, would only make sense if a customer needed an org-specific lib set.
