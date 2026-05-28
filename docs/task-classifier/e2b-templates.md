# E2B Templates & Registry

> **Status:** `utkrusht-python` shipped (one `built` row). Registry table is shipped but is **not yet a capability sheet** — that's the merged-model work.
> **Updated:** 2026-05-27
> **Sister doc:** [Task Classifier](./classifier.md) — owns the merged-design decision. This doc covers the operational reality of templates: what's in each one, what the registry row should carry, and what we need to change to get from "build-command lookup" to "capability sheet the classifier reads."

## The concept — each row is the template's capability sheet

The `template_registry` table looks superficially like a build-command lookup ("here's the `pip install` line for Python tasks"). In the [merged design](./classifier.md#the-design--classifier-picks-template_id-directly), it's something stronger: **each row is the capability sheet the classifier reads to decide which template a task should boot.**

The row describes:

| Axis | Field | What it tells the classifier |
|---|---|---|
| Identity | `template_id`, `status` | Is this template real and currently picked-able? |
| Image content | `runtime`, `language_versions`, `frameworks`, `datastores`, `tools`, `needs_browser`, `needs_gpu`, `capabilities_note` | What's already baked in — so the task's `run.sh` doesn't need to install it |
| Who grades it | `personas[]` | Which reviewer persona this template can host (one row → many personas) |
| How to run | `build_cmd`, `test_cmd`, `compile_cmd` | The platform's pre-flight commands, idiomatic for this stack |
| Provenance | `manifest_hash`, `generated_at`, `registry_version` | Proof the row matches the actual image — see "Drift control" below |

The classifier picks a template by reading every row where `status='built'` and matching the task's competency combo against these sheets. Adding a new template = adding a row. Removing a runtime we never built = deleting a row. **The registry is the deployable set; there is no other catalog.**

## What is an E2B template

An E2B template is a pre-built Firecracker microVM snapshot, registered with E2B under a name like `utkrusht-python`. A sandbox boots from it in ~150 ms with **nothing installed at boot** — every dependency the task needs is already baked into the image.

Templates are defined as Python (E2B v2 SDK), built via `python build_prod.py` (or `build_dev.py`) from the template's directory, and uploaded to the E2B registry. A `template_registry` row points at one (`template_id` matches the E2B-side name).

The build-time lifecycle is:

```
template.py  (Python — declares apt/pip/curl steps via AsyncTemplate chain)
     │
     │  python build_prod.py
     ▼
E2B builds a Firecracker snapshot, registers it as `utkrusht-python`
     │
     ▼
template_registry row exists / is updated to point at it
     │
     ▼
sandbox_eval (gate) and deploy both call Sandbox.create("utkrusht-python")
```

The classifier reads the row; the gate boots the image; the candidate later gets a sandbox from the same template. **One image lineage** — see "One template lineage, used for both eval and deployment" below.

## What's in the registry today

Two template directories live in [`infra/e2b/templates/`](../../infra/e2b/templates/). They are not equally important.

### `utkrusht-python` — the active "fat Python" template

**Path:** [`infra/e2b/templates/python/template.py`](../../infra/e2b/templates/python/template.py).
**Status:** `built` — the only currently-active row in the registry.
**Base:** `from_python_image("3.12")` (lean Python image; no Jupyter).

What's baked in:

| Layer | What's installed |
|---|---|
| System | `ca-certificates curl gnupg lsb-release git jq postgresql-client default-mysql-client netcat-openbsd` |
| Docker | Full DinD — `docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin` |
| Python — web | `fastapi flask django uvicorn[standard] gunicorn httpx requests` |
| Python — ORM/DB clients | `sqlalchemy psycopg2-binary pymongo redis` |
| Python — LLM | `langchain llama-index openai anthropic pinecone chromadb` |
| Python — data | `pandas numpy` |
| Python — test | `pytest pytest-asyncio` |
| Compat shim | `/usr/local/bin/docker-compose` → `docker compose` (v1→v2 alias) |
| Browser surfaces | `ttyd` :7681 (terminal), `code-server` :8443 (IDE), `adminer` :8080 (DB GUI), `php-cli php-pgsql php-mysql` |

What's **not** baked in (intentionally):

- Service containers (Postgres, Redis, Mongo, MySQL servers). Each task brings its own `docker-compose.yml`; DinD runs it inside the sandbox.
- Versions on most pip packages (`pip install fastapi flask django ...` floats to latest at build time — see "Gaps" below).

### `utkrusht-python-sql` — the original PoC (legacy)

**Path:** [`infra/e2b/templates/python-sql/template.py`](../../infra/e2b/templates/python-sql/template.py).
**Status:** registered with E2B but the `python/` template was explicitly authored to supersede it (see comment in `python/template.py:14`).
**Base:** `e2bdev/code-interpreter:latest` (heavier — ships Jupyter we don't need).

Differences from `utkrusht-python`:

| | `python-sql` (legacy) | `python` (active) |
|---|---|---|
| Base image | `e2bdev/code-interpreter:latest` | `from_python_image("3.12")` |
| Python lib set | `psycopg2-binary sqlalchemy pandas` | Fat — fastapi/flask/django + LLM stack + data + test |
| MySQL client | ❌ | ✓ |
| Intended life | Replaced by `python` | Active |

These two templates have ~80% overlap. Keeping them both alive is exactly the [sprawl failure mode](./classifier.md#sprawl-avoidance) the merged design warns about — the classifier can't reliably distinguish them, and CVE patches double. Once `utkrusht-python` is verified end-to-end, `utkrusht-python-sql` should be marked `deprecated` in the registry and the directory removed.

### Other rows in `template_registry`

Per [migration 2026-05-26-template-registry-add-status-and-proposed-rows.sql](../../migrations/2026-05-26-template-registry-add-status-and-proposed-rows.sql), every runtime in the current `Runtime` Literal has a row, but only `python` is `built`:

| runtime | template_name | status |
|---|---|---|
| `python` | `utkrusht-python` | **`built`** |
| `node`, `java`, `php`, `go`, `rust`, `flutter`, `ruby`, `scala` | `utkrusht-<lang>` | `proposed` |

The `proposed` rows document intent (recipe captured, template name reserved) but no E2B-side template exists yet — the gate filters them via `.eq("status","built")` and skips with `no_template`.

## How the registry feeds the gate today

[`infra/e2b/sandbox_eval.py`](../../infra/e2b/sandbox_eval.py) boots a sandbox from the template that matches the classifier's `runtime`, copies code in, and runs build → test → optional compile. Today most of this is implicit:

```python
spec = _get_template(runtime)              # registry lookup
sb = await Sandbox.create(spec.template_name)
_run(sb, "pip install --break-system-packages -r requirements.txt", ...)   # ← hardcoded
_run(sb, "python -m pytest -q --tb=short", ...)                            # ← hardcoded
if exit_code == 5:
    _run(sb, "python -m compileall -q .", ...)                             # ← hardcoded
```

The registry **stores** `build_cmd` / `test_cmd` / `compile_cmd`, but `sandbox_eval` doesn't yet read them — the strings are hardcoded in Python. This is the cheapest first step toward "registry as source of truth" (see [What we should do next](#what-we-should-do-next)).

## `run.sh` vs `build_cmd` — who runs what, when

A natural question: each task already ships a `run.sh`. Why does the registry carry separate `build_cmd` / `test_cmd` columns instead of just executing it?

They serve different consumers at different points in the lifecycle.

| | `run.sh` (task-owned) | `build_cmd` / `test_cmd` (registry-owned) |
|---|---|---|
| **Runs when** | Candidate's session starts | Eval gate, before the task ships |
| **Process shape** | Long-running — `docker compose up`, seed DB, start dev server | Short-lived — install deps, run pytest, exit |
| **Exit semantics** | "Server is up" — no exit code to grade against | `0` = pass, `1` = test failure, `5` = no tests |
| **Scope** | Per task (different services, seeds, dev-server invocation) | Per template (every Python task installs the same way) |
| **Consumer** | Candidate, in their IDE / terminal | The platform's pre-flight quality gate |

Three concrete reasons the gate can't just execute `run.sh`:

1. **`run.sh` doesn't exit.** It runs `docker compose up && python app/main.py` — the dev server runs forever. The gate needs a process that ends so it can read an exit code.
2. **The test command is a property of the runtime, not the task.** Every Python task runs `pytest`; every Node task runs `npm test`. Embedding that in each task's `run.sh` means every prompt-generator output has to remember the right invocation — drift becomes per-task instead of fixed by the platform.
3. **The orchestration is opposite.** Gate wants: copy code in → install deps → run tests → kill. Candidate wants: bring up services → keep the dev server running → expose ports.

So registry columns aren't a duplicate of `run.sh` — they're the platform's pre-flight checklist that runs **before** any candidate ever sees `run.sh`.

## Gaps vs. the merged model

The merged design expects each row to be a *capability sheet that cannot lie about its image*. The current registry is closer to a build-command lookup. The gap:

| Gap | Where it shows up |
|---|---|
| Most pip packages are unpinned (`pip install fastapi flask django ...`) | Two builds of the "same" template can install different versions; reproducibility broken |
| No `personas` column | `kind` on the classification row carries persona — conflated with shape, single-valued |
| No `frameworks` / `datastores` / `tools` columns on `template_registry` | Capability info lives only in `template.py` shell strings — extractable only by reading source |
| No `manifest_hash` / `generated_at` / `registry_version` columns | Nothing detects "Dockerfile changed, row didn't"; sheet vs. image drift goes unnoticed |
| No manifest emitted by the build pipeline | `build_prod.py` calls `AsyncTemplate.build()` and exits — never writes a structured record of what's in the image |
| No CI check tying `template.py` to the row's hash | Drift, when it happens, surfaces in eval failure weeks later, not at build time |
| `runtime` is the PK — only one template per language | `utkrusht-python-llm` and `utkrusht-python-web` can't coexist (and `python-sql` + `python` conflict already) |
| `utkrusht-python-sql` overlaps `utkrusht-python` ~80% | The "sheet ambiguity" failure mode in flesh — LLM matcher can't reliably distinguish them |

## What it takes to get to the merged model

Five template-side changes; they sequence with the classifier doc's [migration path](./classifier.md#migration-path).

### 1. Pin pip versions

`pip install fastapi==0.115.4 flask==3.0.3 ...` — every package gets a version. Either inline in `template.py` or via a `requirements-template.txt` the build copies in.

Reproducibility is the surface reason. The deeper reason: an honest capability sheet says "this template provides fastapi 0.115.4," not "this template provides fastapi, whatever version was latest at build time." Pins also surface dep conflicts at build time (LangChain pin vs. fastapi pin) rather than weeks later in eval.

### 2. Capability sheet authoring — two viable shapes

**Option A — `manifest.yaml` next to `template.py`.** Hand-author the sheet; CI hashes both files together.

```yaml
template_id: utkrusht-python
runtime: python3.12
language_versions: { python: "3.12" }
frameworks: [fastapi, flask, django, sqlalchemy, langchain, llama-index]
datastores: []                # template-level; services come from task compose
tools: [pytest, docker, psql, mysql, adminer, ttyd, code-server]
needs_browser: false
needs_gpu: false
personas: [backend, data, mle, llm]
build_cmd: "pip install --break-system-packages -r requirements.txt"
test_cmd:  "python -m pytest -q --tb=short"
```

Pros: easy to start, reviewable in PR.
Cons: two sources of truth (the .yaml and the .py); they will drift between rebuilds.

**Option B — single-source-of-truth Python in `template.py`.** Declare apt/pip packages as Python collections; `template.py` *both* builds the image and emits the manifest. Sheet and image cannot diverge by construction.

```python
APT_PACKAGES = ["ca-certificates", "curl", ..., "default-mysql-client"]
PIP_PACKAGES = {"fastapi": "0.115.4", "flask": "3.0.3", "langchain": "0.3.7", ...}
TOOLS_BAKED  = ["ttyd@1.7.7", "code-server@4.96.4", "adminer@4.8.1", "docker", "psql", "mysql"]
PERSONAS     = ["backend", "data", "mle", "llm"]

template = (
    AsyncTemplate()
    .from_python_image("3.12")
    .run_cmd(f"apt-get install -y {' '.join(APT_PACKAGES)}")
    .run_cmd(f"pip install {' '.join(f'{k}=={v}' for k, v in PIP_PACKAGES.items())}")
    ...
)

MANIFEST = {
    "template_id":       "utkrusht-python",
    "runtime":           "python3.12",
    "language_versions": {"python": "3.12"},
    "frameworks":        [k for k in PIP_PACKAGES if k in WEB_OR_ORM_OR_LLM_KEYS],
    "tools":             TOOLS_BAKED + ["pytest", "docker"],
    "personas":          PERSONAS,
    "apt":               APT_PACKAGES,
    "pip":               PIP_PACKAGES,
}
```

Pros: image and sheet cannot disagree; refactoring once is cheaper now (one template) than later (five).
Cons: requires touching `template.py` for the existing template.

**Recommendation: Option B.** A is a stepping stone that becomes the drift problem the merged design exists to prevent. The refactor is roughly half a day for the existing `python/template.py`; doing it now (with one template) is much cheaper than retrofitting it onto a growing set.

### 3. Emit manifest + hash at build time

`build_prod.py` writes `MANIFEST` to `manifest.json`, hashes it, and updates the row:

```python
manifest_json = json.dumps(MANIFEST, sort_keys=True, indent=2)
manifest_hash = hashlib.sha256(manifest_json.encode()).hexdigest()

supabase.table("template_registry").update({
    **MANIFEST,                                       # capability sheet columns
    "manifest_hash":    manifest_hash,
    "generated_at":     datetime.utcnow().isoformat(),
    "registry_version": current_version + 1,
}).eq("template_id", "utkrusht-python").execute()
```

Bumping `registry_version` invalidates cached classifications — see [cache invalidation](./classifier.md#cache-invalidation-has-two-keys).

### 4. CI gate — the durability investment

A check that runs on every PR touching `infra/e2b/templates/<name>/`:

1. Import `MANIFEST` from the template's `template.py`.
2. Compute its hash.
3. Compare to `template_registry.manifest_hash` for that row.
4. If different → fail the build with: "rebuild and re-upload the template, then update the registry row."

**This is the single load-bearing investment** for the merged design's durability — see [the classifier doc's Step 3](./classifier.md#migration-path). Without it, capability sheets drift from reality within months; the LLM picks based on stale info; the merged design rots. With it, sheets cannot lie.

### 5. Deduplicate `python-sql` and `python`

Once `utkrusht-python` is verified end-to-end:

```sql
UPDATE template_registry SET status = 'deprecated' WHERE template_id = 'utkrusht-python-sql';
```

Then remove `infra/e2b/templates/python-sql/`. The row stays for cache validity but the LLM stops picking it. This is the smallest version of the [fragmentation policy](./classifier.md#sprawl-avoidance): two templates with 90% overlap aren't two templates, they're one template and one CVE-patch overhead.

## Fat vs. composition — what the merged design resolves

A previous draft of this doc went deep on "should we ship one fat template per runtime, or compose smaller leaves via E2B's `from_template()`?" The merged design dissolves this question into a different one: **how many distinct rows do we maintain in the registry?**

- **Today:** one fat row (`utkrusht-python`) handles every Python task. The classifier doesn't need to distinguish `python-llm` from `python-web` because there's nothing to distinguish.
- **Later:** if signal demands ([base bloat, over-serving, `no_match` clustering](./classifier.md#signals-that-justify-a-split)), `utkrusht-python` splits into siblings (`utkrusht-python-llm`, `utkrusht-python-web`, `utkrusht-python-nlp`). Each is a separate row with a distinctive capability sheet.

The sibling pattern is preferred over E2B `from_template()` inheritance — see the classifier doc's [sibling vs inheritance](./classifier.md#sibling-templates-not-e2b-inheritance) note. Inheritance feels DRY but makes rebuild graphs ugly and CVE patching cascades; siblings are independently buildable / patchable.

**Don't pre-split.** Three signals to wait for, before fragmenting:

1. Build time on the base past ~60 s, or image size past some MB ceiling.
2. Most tasks routed to the base also `pip install <heavy lib>` at sandbox boot.
3. ≥5 `no_match` rows / month sharing the same `missing_capabilities`.

Until then, one fat row is honest about what we deploy.

## One template lineage — eval + deploy use the same image

There is no separate "eval template" and "candidate template." The same image boots both contexts; the only difference is what gets run against it.

| Why one lineage | Detail |
|---|---|
| **Production parity** | Anything that passes eval must run on what the candidate actually gets. A split re-introduces "eval template was fine, deploy template missing a library" bugs at the template layer. |
| **Single source of truth** | Adding a Python package means updating one template, not two. |
| **"Dead weight" cost is negligible** | Browser tools running during automated eval are background processes on a microVM — cost nothing observable. |
| **Eval-gate boot time is fine** | Even 5–10 s per eval is acceptable; eval runs at task-generation time, not per candidate request. |

The eval gate boots a sandbox from the same template the candidate would receive, copies the task code in, runs `build_cmd` → `test_cmd`, captures pass/fail, then kills the sandbox. Candidates get the same template with a longer idle timeout and the browser URLs exposed.

## E2B SDK capabilities — verified

| Finding | Detail |
|---|---|
| **`from_template()` inheritance** | Supported; chains from a parent template. **Sibling rows are still the recommended split shape** for the reasons in the classifier doc. |
| **Multi-container natively** | No first-class sidecar primitive. Documented pattern: DinD + the task's own compose. |
| **Account limits** | Pro tier: 100 concurrent sandboxes, 24-hour sessions, 20 GiB storage. ~12 templates × ~1.5–3 GiB fits. |
| **Cold-start latency** | ~78–180 ms (Firecracker snapshot). The 3–8 s before "ready" is start-cmd (dockerd + ttyd + code-server) — independent of image size. |
| **Base image** | Prefer language-specific convenience methods (`from_python_image()`, `from_node_image()`) over the heavier `e2bdev/code-interpreter`. `python/` already does this; `python-sql/` doesn't. |

## Worked examples — TaskRuntime → template (under the merged model)

After Step 4 of the migration the classifier returns `template_id` + `persona` directly. Sample matches:

| Task | template_id | persona | Task's compose |
|---|---|---|---|
| `Python - FastAPI` | `utkrusht-python` | `backend` | (none) |
| `Python - FastAPI + Postgres` | `utkrusht-python` | `backend` | postgres-server |
| `Python + LlamaIndex` | `utkrusht-python` | `llm` | (none) |
| `MySQL` (alone) | `utkrusht-python` | `dba` | mysql-server |
| `Helm chart for a microservice` | **no_match** — `suggested_template: utkrusht-infra`, `missing_capabilities: ["helm","kubectl"]` | n/a | n/a |
| `Flutter mobile app` | **no_match** — `suggested_template: utkrusht-flutter`, `missing_capabilities: ["dart","flutter-sdk"]` | n/a | n/a |

The first four pick the same template, different personas — that's the [personas-as-list](./classifier.md#personas-are-a-list-not-a-scalar) decision in action. The last two surface as structured `no_match` rows — those are the [template roadmap signal](./classifier.md#wire-the-no_match-path).

## Implementation status (2026-05-27)

| Component | Status |
|---|---|
| `template_registry` table — `runtime` PK, build/test/compile columns | **Shipped** |
| `template_registry.status` column + `proposed` rows for all runtimes | **Shipped** |
| `utkrusht-python` template (fat Python, only `built` row) | **Shipped** |
| `utkrusht-python-sql` template (legacy, narrow lib set) | **Shipped — to be deprecated** once `utkrusht-python` is verified |
| `sandbox_eval` reads `template_name` from registry | **Shipped** |
| `sandbox_eval` reads `build_cmd` / `test_cmd` from registry | **Proposed** (~15 LOC; first step) |
| Capability sheet columns on `template_registry` (`personas`, `frameworks`, `datastores`, `tools`, etc.) | **Proposed — classifier doc Step 1** |
| `manifest_hash` / `generated_at` / `registry_version` columns | **Proposed — classifier doc Step 1** |
| Pip version pinning in `template.py` | **Proposed** |
| `MANIFEST` const in `template.py` (single source of truth — Option B) | **Proposed** |
| Manifest emission in `build_prod.py` (writes `manifest.json` + updates row) | **Proposed** |
| CI gate (manifest hash matches row) | **Proposed — the durability gate** |
| Switch PK from `runtime` to `template_id` | **Proposed — classifier doc Step 2** |
| Deprecate `utkrusht-python-sql` | **Proposed** — once `utkrusht-python` is verified |
| Additional templates (node, java, php, go, rust, flutter, infra, playwright) | **Proposed** — build only when `no_match` clusters justify |

## What we should do next

The sequence below is the template-side prerequisites for the classifier doc's [migration path](./classifier.md#migration-path). Order matters; Step 4 of this list is the gate without which the design rots.

1. **Wire `sandbox_eval` to read `build_cmd` / `test_cmd` from `template_registry`** (~15 LOC). Turns the registry from "stored but unused" into "actively consumed." Cheapest validation of the pattern.
2. **Pin pip versions in `infra/e2b/templates/python/template.py`.** Honest capability sheet starts here. Rebuilds `utkrusht-python` once.
3. **Refactor `template.py` to Option B** (single-source-of-truth Python with `APT_PACKAGES`, `PIP_PACKAGES`, `MANIFEST` constants). Half a day with one template; harder with five.
4. **Add manifest emission to `build_prod.py`** — writes `manifest.json`, hashes it, updates `template_registry.manifest_hash` and the capability sheet columns. Lands together with the schema ALTER in the classifier doc's Step 1.
5. **Build the CI gate** that fails on `template.py` ↔ row hash mismatch. **This is the durability investment.** Without it, no rewriteable second template should land.
6. **Deprecate `utkrusht-python-sql`** once `utkrusht-python` is verified end-to-end. Then remove the directory.
7. **Build the second template (`utkrusht-node-base`) with the new shape from day one** — pinned versions, MANIFEST const, generated `manifest_hash`. Retrofitting these onto a growing set is harder than starting with them.

Steps 4–7 of the classifier doc's migration (LLM emits `template_id`, `task_template_match` table, no_match wiring, dropping `Runtime` Literal) land after the registry can carry honest capability sheets — i.e., after this doc's steps 1–5.

## Out of scope (for now)

- E2B SDK capability verification beyond what's listed above — separate spike if anything new surfaces.
- Building the proposed-but-not-built rows (`utkrusht-node`, etc.) — let `no_match` clusters drive the order.
- The droplet → E2B deploy migration for tasks already running on droplets — outside this doc's concern (droplet path was retired 2026-05-25).
- v2 multi-tenancy on templates (per-org template forks) — not on the roadmap; would only make sense if a customer needed an org-specific lib set.
