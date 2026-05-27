"""Resolve a competency combo into a complete plan for the rest of the pipeline.

The single entry point for the question *"what infrastructure does this task
need?"* Today this wraps the existing LLM classifier and a deterministic
template lookup. The combo-cache table (phase B1 of the production-readiness
plan) plugs in here later without any caller-side changes.

A ``ResolvedPlan`` bundles three things:
  • The classified facts (the existing ``TaskRuntime``).
  • The resolved template (e.g. ``utkrusht-python``) for the gate + deploy.
  • The per-runtime build/test recipe (``pip install`` + ``pytest`` today).

Centralising this in one module lets the rest of the codebase stop reasoning
about runtimes, templates, and recipes separately — every consumer reads the
same ``ResolvedPlan``.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, Optional

from infra.logger_config import logger
from infra.classifier.llm_classifier import classify_with_llm
from infra.classifier.runtime import Competency, TaskRuntime


# Bump when llm_classifier._SYSTEM_PROMPT or _MODEL changes; rows with an
# older classifier_version can be re-classified by a backfill job.
_CLASSIFIER_VERSION = "v1"

# Supabase table names — kept here so resolve_plan() is the only module
# coupled to the schema.
_COMBO_TABLE = "competency_combo_classification"
_TEMPLATE_TABLE = "template_registry"

# Per-process template cache. ``_get_template`` populates this on first hit
# for a runtime; later calls in the same process read from memory and don't
# re-query Supabase. Templates change rarely (new runtime onboarded,
# build_cmd tweak) — short-lived stale data is acceptable, restart picks up
# changes.
_TEMPLATE_CACHE: dict[str, Optional["TemplateSpec"]] = {}


@dataclass(frozen=True)
class TemplateSpec:
    """Per-runtime template + build/test recipe.

    Loaded by ``_get_template`` from the ``template_registry`` Supabase table
    (B6), with the ``_TEMPLATES`` dict below as the offline / pre-seeded
    fallback. The gate and (eventually) deploy read through ``_get_template``
    so they share one source of truth.
    """

    name: str
    build_cmd: str
    test_cmd: str
    compile_cmd: str | None = None
    needs_browser: bool = False


# Seed / fallback for ``_get_template``: matches the migration's INSERT row
# at ``migrations/2026-05-25-create-template-registry.sql``. Used when
# Supabase is unreachable / unconfigured (tests, offline dev) so the gate
# still works without a live DB.
_TEMPLATES: dict[str, TemplateSpec] = {
    "python": TemplateSpec(
        name="utkrusht-python",
        build_cmd="pip install --break-system-packages -r requirements.txt",
        test_cmd="python -m pytest -q --tb=short",
        compile_cmd="python -m compileall -q .",
    ),
}


@dataclass(frozen=True)
class ResolvedPlan:
    """The single object every downstream stage reads.

    Carries: the classified facts (``task_runtime``), the resolved template
    (or ``None`` for runtimes without a template), and the combo key for
    caching / FK references.

    Both ``task_runtime`` and ``template`` are optional so an empty plan can
    be returned safely on classifier failure — callers treat that as "skip
    persona routing and skip the gate," never as an error.
    """

    combo_key: str
    task_runtime: TaskRuntime | None
    template: TemplateSpec | None

    @property
    def runtime(self) -> str | None:
        """The runtime string (e.g. ``"python"``), or ``None`` if unclassified."""
        return self.task_runtime.runtime if self.task_runtime else None

    @property
    def kind(self) -> str | None:
        """The task kind (e.g. ``"app"``), or ``None`` if unclassified."""
        return self.task_runtime.kind if self.task_runtime else None

    @property
    def gate_supported(self) -> bool:
        """True when a template exists — the build/test gate can boot it."""
        return self.template is not None


def template_name_for_runtime(runtime: str | None, *, supabase=None) -> Optional[str]:
    """Return the E2B template name for ``runtime`` (e.g. ``"utkrusht-python"``).

    Convenience wrapper around :func:`_get_template`. Kept for callers that
    only need the template name; new code should prefer ``_get_template`` or
    read ``plan.template`` from a ``ResolvedPlan``.
    """
    spec = _get_template(runtime, supabase=supabase)
    return spec.name if spec else None


def _db_load_template(supabase, runtime: str) -> Optional[TemplateSpec]:
    """Read one row from ``template_registry`` by runtime. ``None`` when absent.

    Filters on ``status='built'`` so rows that document a designed-but-not-yet-
    shipped template (e.g. ``utkrusht-java`` with status='proposed') don't
    cause the gate to try booting a missing E2B template. Proposed rows are
    visible in the SQL registry for design/analytics purposes only.
    """
    resp = (supabase.table(_TEMPLATE_TABLE)
            .select("template_name,build_cmd,test_cmd,compile_cmd,needs_browser")
            .eq("runtime", runtime)
            .eq("status", "built")
            .limit(1)
            .execute())
    rows = resp.data or []
    if not rows:
        return None
    r = rows[0]
    return TemplateSpec(
        name=r["template_name"],
        build_cmd=r["build_cmd"],
        test_cmd=r["test_cmd"],
        compile_cmd=r.get("compile_cmd"),
        needs_browser=r.get("needs_browser") or False,
    )


def _get_template(runtime: str | None, *, supabase=None) -> Optional[TemplateSpec]:
    """Resolve a ``TemplateSpec`` for ``runtime`` — DB first, in-memory fallback.

    Lookup order:
      1. Per-process cache (``_TEMPLATE_CACHE``).
      2. ``template_registry`` table on Supabase.
      3. ``_TEMPLATES`` seed dict (matches the migration's INSERT row).

    Failures at every step degrade gracefully — the gate skipping with
    ``no_template`` is the right outcome when neither DB nor seed has a row.
    """
    if not runtime:
        return None
    if runtime in _TEMPLATE_CACHE:
        return _TEMPLATE_CACHE[runtime]

    spec: Optional[TemplateSpec] = None
    client = supabase
    if client is None:
        try:
            client = _build_supabase_client()
        except Exception as exc:  # noqa: BLE001
            logger.info(
                f"_get_template: supabase unavailable for runtime={runtime!r}: {exc} — "
                "using in-memory seed"
            )
            client = None
    if client is not None:
        try:
            spec = _db_load_template(client, runtime)
            if spec is not None:
                logger.info(
                    f"_get_template: runtime={runtime!r} resolved from "
                    f"template_registry → name={spec.name!r}"
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                f"_get_template: DB lookup failed for runtime={runtime!r}: {exc} — "
                "falling back to in-memory seed"
            )
    if spec is None:
        spec = _TEMPLATES.get(runtime)
        if spec is not None:
            logger.info(
                f"_get_template: runtime={runtime!r} resolved from in-memory seed "
                f"→ name={spec.name!r}"
            )
    _TEMPLATE_CACHE[runtime] = spec
    return spec


def make_combo_key(competencies: Iterable[Competency]) -> str:
    """Canonical key for a competency combo — sorted by name, proficiency-suffixed.

    The same shape ``get_task_prompt_by_technology_stack`` uses for prompt
    registry lookup, so a single competency-set has exactly one stable
    identity across the pipeline + the future combo cache.
    """
    parts = sorted(f"{c.name} ({c.proficiency})" for c in competencies)
    return ", ".join(parts)


def _build_supabase_client():
    """Lazy import + init the Supabase dev client. Tests inject via the
    ``supabase`` kwarg on ``resolve_plan``; production paths get None and
    we build one here."""
    from supabase import create_client  # local import keeps this file importable without supabase installed
    url = os.getenv("SUPABASE_URL_APTITUDETESTSDEV")
    key = os.getenv("SUPABASE_API_KEY_APTITUDETESTSDEV")
    if not url or not key:
        raise RuntimeError("Missing SUPABASE_URL_APTITUDETESTSDEV / SUPABASE_API_KEY_APTITUDETESTSDEV")
    return create_client(url, key)


def _cache_lookup(supabase, combo_key: str) -> Optional[TaskRuntime]:
    """Return the cached TaskRuntime for this combo, or None on miss.

    Classifications are platform-global — the classifier output for a given
    competency set is identical regardless of which org generated the task,
    so no organization_id is in the key.
    """
    resp = (supabase.table(_COMBO_TABLE)
            .select("runtime,kind,frameworks,datastores,messaging,needs_browser")
            .eq("combo_key", combo_key)
            .limit(1)
            .execute())
    rows = resp.data or []
    if not rows:
        return None
    r = rows[0]
    return TaskRuntime(
        runtime=r["runtime"],
        kind=r["kind"],
        frameworks=r.get("frameworks") or [],
        datastores=r.get("datastores") or [],
        messaging=r.get("messaging") or [],
        needs_browser=r.get("needs_browser") or False,
    )


def _cache_write(supabase, combo_key: str,
                 runtime: TaskRuntime, confidence: float) -> None:
    """Upsert a freshly classified TaskRuntime into the cache table."""
    # Only set template_runtime FK when a template row actually exists for
    # this runtime; otherwise the FK constraint will reject the insert.
    template_runtime = (
        runtime.runtime
        if _get_template(runtime.runtime, supabase=supabase) is not None
        else None
    )
    supabase.table(_COMBO_TABLE).upsert({
        "combo_key": combo_key,
        "runtime": runtime.runtime,
        "kind": runtime.kind,
        "frameworks": list(runtime.frameworks),
        "datastores": list(runtime.datastores),
        "messaging": list(runtime.messaging),
        "needs_browser": runtime.needs_browser,
        "template_runtime": template_runtime,
        "classifier_version": _CLASSIFIER_VERSION,
        "confidence": round(float(confidence), 2),
    }).execute()


def resolve_plan(
    competencies: Iterable[Competency],
    *,
    supabase=None,
) -> ResolvedPlan:
    """Resolve a competency combo into a full plan.

    Lookup order:
      1. Cache hit on ``competency_combo_classification`` keyed by combo_key.
      2. Cache miss → one LLM call → upsert the row → return.
      3. Cache unreachable (Supabase down, missing env) → fall through to a
         direct LLM call without persistence.
      4. LLM failure → return an empty plan (callers skip persona + gate).

    Never raises.
    """
    competencies = list(competencies)
    combo_key = make_combo_key(competencies)

    # ── Step 1: try the cache ──────────────────────────────────────────
    # Cache availability is purely a function of whether we can reach
    # Supabase; classifications are not tenant-scoped.
    client = supabase
    if client is None:
        try:
            client = _build_supabase_client()
        except Exception as exc:   # noqa: BLE001
            logger.warning(
                f"resolve_plan: supabase init failed for {combo_key!r}: {exc} — "
                "falling through to direct LLM call (no caching)"
            )
            client = None

    if client is not None:
        try:
            cached = _cache_lookup(client, combo_key)
        except Exception as exc:   # noqa: BLE001
            logger.warning(
                f"resolve_plan: cache lookup failed for {combo_key!r}: {exc} — "
                "falling through to direct LLM call"
            )
            cached = None
        if cached is not None:
            logger.info(
                f"resolve_plan: combo={combo_key!r} cache HIT "
                f"runtime={cached.runtime} kind={cached.kind}"
            )
            return ResolvedPlan(
                combo_key=combo_key,
                task_runtime=cached,
                template=_get_template(cached.runtime, supabase=client),
            )

    # ── Step 2: cache miss (or unreachable) → LLM ──────────────────────
    try:
        result = classify_with_llm(competencies)
        task_runtime = result.runtime
        confidence = result.confidence
    except Exception as exc:   # noqa: BLE001 — classifier failures must not crash a run
        logger.warning(
            f"resolve_plan: classifier failed for {combo_key!r}: {exc} — "
            "returning empty plan (no persona, no gate)"
        )
        return ResolvedPlan(combo_key=combo_key, task_runtime=None, template=None)

    # ── Step 3: best-effort write-through to cache ─────────────────────
    if client is not None:
        try:
            _cache_write(client, combo_key, task_runtime, confidence)
            logger.info(
                f"resolve_plan: combo={combo_key!r} cache MISS — wrote new row "
                f"runtime={task_runtime.runtime} kind={task_runtime.kind} "
                f"confidence={confidence:.2f}"
            )
        except Exception as exc:   # noqa: BLE001
            logger.warning(
                f"resolve_plan: cache write failed for {combo_key!r}: {exc}"
            )

    template = _get_template(task_runtime.runtime, supabase=client)
    if template is None:
        logger.info(
            f"resolve_plan: combo={combo_key!r} runtime={task_runtime.runtime!r} "
            f"-> no template (gate will skip)"
        )
    return ResolvedPlan(
        combo_key=combo_key,
        task_runtime=task_runtime,
        template=template,
    )


# ─────────────────────────────────────────────────────────────────────
# v2 path — Phase 2 of unified-classifier-template-schema.
#
# resolve_plan_v2(competencies) → ResolvedPlanV2(match, template).
# Cache: task_template_match keyed on combo_key (no scenario_hash).
# Per-task intent lives on tasks.task_intent — emitted later by the
# content-generation LLM, NOT here.
# ─────────────────────────────────────────────────────────────────────

# Cache-invalidation knob: bump when the classifier prompt OR the model
# changes so old rows re-classify.
_CLASSIFIER_MODEL_V2 = "claude-sonnet-4-6"

# v2 table names (mirrors `templates` + `task_template_match` migrations).
_TEMPLATES_TABLE_V2 = "templates"
_MATCH_TABLE_V2 = "task_template_match"


@dataclass(frozen=True)
class TemplateSpecV2:
    """Hydrated row from ``templates`` (v2 schema).

    Used by the eval gate (template_name + build/test/compile + secondary
    install) and the prompt generator (capabilities + personas + eval_methods).
    """

    template_id: str
    primary_runtime: str
    personas: list[str]
    eval_methods: list[str]
    capabilities: dict
    build_cmd: str
    test_cmd: str
    compile_cmd: str | None = None
    install_cmd: str | None = None
    install_verify: str | None = None
    install_seconds: int | None = None
    manifest_hash: str = ""
    registry_version: int = 1
    description: str | None = None


@dataclass(frozen=True)
class ResolvedPlanV2:
    """The single bundle every downstream consumer reads in v2.

    Carries the match decision (cached per combo) + the hydrated template
    spec. Does NOT carry ``task_intent`` — that's emitted later by the
    content-generation LLM and lives on ``tasks.task_intent``.

    On classifier failure, ``match`` is None — callers skip persona
    routing and skip the gate (same fail-safe contract as v1).
    On no_match, ``template`` is None but ``match.no_match_reason`` is
    set — callers can inspect ``match.missing_capabilities``.
    """

    combo_key: str
    match: "TaskTemplateMatch | None"
    template: TemplateSpecV2 | None


def _row_to_template_v2(row: dict) -> TemplateSpecV2:
    """Convert one ``templates`` row dict into a ``TemplateSpecV2``."""
    return TemplateSpecV2(
        template_id=row["template_id"],
        primary_runtime=row["primary_runtime"],
        personas=row.get("personas") or [],
        eval_methods=row.get("eval_methods") or ["test_suite"],
        capabilities=row.get("capabilities") or {},
        build_cmd=row["build_cmd"],
        test_cmd=row["test_cmd"],
        compile_cmd=row.get("compile_cmd"),
        install_cmd=row.get("install_cmd"),
        install_verify=row.get("install_verify"),
        install_seconds=row.get("install_seconds"),
        manifest_hash=row.get("manifest_hash") or "",
        registry_version=int(row.get("registry_version") or 1),
        description=row.get("description"),
    )


def _load_active_templates_v2(supabase) -> list[TemplateSpecV2]:
    """SELECT every ``built`` template row, hydrated as ``TemplateSpecV2``.

    The LLM classifier reads these capability sheets to match a competency
    combo to one of the deployable templates.
    """
    resp = (supabase.table(_TEMPLATES_TABLE_V2)
            .select("*")
            .eq("status", "built")
            .execute())
    return [_row_to_template_v2(r) for r in (resp.data or [])]


def _get_template_v2(supabase, template_id: str) -> TemplateSpecV2 | None:
    """Fetch one ``templates`` row by id. Returns None if absent or not built."""
    resp = (supabase.table(_TEMPLATES_TABLE_V2)
            .select("*")
            .eq("template_id", template_id)
            .eq("status", "built")
            .limit(1)
            .execute())
    rows = resp.data or []
    if not rows:
        return None
    return _row_to_template_v2(rows[0])


def _match_lookup_v2(supabase, combo_key: str) -> tuple["TaskTemplateMatch | None", int | None, str | None]:
    """Return (match, cached_registry_version, classifier_model) for combo_key.

    ``(None, None, None)`` on miss. The registry_version + classifier_model
    are returned so the caller can validate freshness before trusting the
    cached match.
    """
    # Local import to keep this module importable without pydantic when
    # someone is poking only the template-helpers.
    from infra.classifier.runtime import TaskTemplateMatch  # noqa: WPS433

    resp = (supabase.table(_MATCH_TABLE_V2)
            .select("template_id,persona,confidence,no_match_reason,"
                    "missing_capabilities,suggested_template,"
                    "classifier_model,registry_version")
            .eq("combo_key", combo_key)
            .limit(1)
            .execute())
    rows = resp.data or []
    if not rows:
        return None, None, None
    r = rows[0]
    match = TaskTemplateMatch(
        template_id=r.get("template_id"),
        persona=r.get("persona"),
        confidence=float(r.get("confidence") or 0.0),
        no_match_reason=r.get("no_match_reason"),
        missing_capabilities=r.get("missing_capabilities") or [],
        suggested_template=r.get("suggested_template"),
    )
    return match, int(r.get("registry_version") or 1), r.get("classifier_model")


def _match_write_v2(
    supabase,
    combo_key: str,
    match: "TaskTemplateMatch",
    *,
    registry_version: int,
) -> None:
    """Upsert one task_template_match row.

    ``registry_version`` is the snapshot of the matched template's
    registry_version at classify time. For no_match rows we still write
    a registry_version (1) so the CHECK on the table is satisfied; the
    next model upgrade triggers re-evaluation.
    """
    payload = {
        "combo_key": combo_key,
        "template_id": match.template_id,
        "persona": match.persona,
        "confidence": round(float(match.confidence), 2),
        "no_match_reason": match.no_match_reason,
        "missing_capabilities": list(match.missing_capabilities),
        "suggested_template": match.suggested_template,
        "classifier_model": _CLASSIFIER_MODEL_V2,
        "registry_version": registry_version,
    }
    supabase.table(_MATCH_TABLE_V2).upsert(payload).execute()


def _is_match_fresh_v2(
    cached_model: str | None,
    cached_version: int | None,
    template: TemplateSpecV2 | None,
) -> bool:
    """Stale rows auto-re-classify when the model or template registry changes.

    Rules:
      * Model mismatch → stale (the prompt may have changed semantics).
      * If the cache pointed at a real template and that template's
        registry_version has bumped → stale.
      * no_match rows survive registry bumps (a new template might
        un-block them, but that's only worth re-evaluating on a model
        change; otherwise we'd re-call the LLM on every template insert).
    """
    if cached_model != _CLASSIFIER_MODEL_V2:
        return False
    if template is not None and cached_version != template.registry_version:
        return False
    return True


def resolve_plan_v2(
    competencies: Iterable[Competency],
    *,
    supabase=None,
) -> ResolvedPlanV2:
    """Resolve a competency combo into a v2 plan.

    Lookup order:
      1. ``task_template_match`` cache hit for combo_key (+ freshness check).
      2. Cache miss → call ``classify_match_v2`` with the active templates
         → upsert the new match row → return.
      3. Cache unreachable → direct LLM call without persistence.
      4. LLM failure → return an empty plan (callers skip persona + gate).

    Never raises. Scenario / background are NOT inputs — those go to the
    content-generation LLM, which emits ``TaskIntent`` per task.
    """
    # Local imports so the module is importable without supabase / pydantic
    # in environments that only use the helpers.
    from infra.classifier.llm_classifier import classify_match_v2  # noqa: WPS433

    competencies = list(competencies)
    combo_key = make_combo_key(competencies)

    # ── Step 1: try the cache ──────────────────────────────────────────
    client = supabase
    if client is None:
        try:
            client = _build_supabase_client()
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                f"resolve_plan_v2: supabase init failed for {combo_key!r}: {exc} — "
                "falling through to direct LLM call (no caching)"
            )
            client = None

    if client is not None:
        try:
            cached, cached_version, cached_model = _match_lookup_v2(client, combo_key)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                f"resolve_plan_v2: cache lookup failed for {combo_key!r}: {exc} — "
                "falling through to direct LLM call"
            )
            cached, cached_version, cached_model = None, None, None

        if cached is not None:
            template = (_get_template_v2(client, cached.template_id)
                        if cached.template_id else None)
            if _is_match_fresh_v2(cached_model, cached_version, template):
                logger.info(
                    f"resolve_plan_v2: combo={combo_key!r} cache HIT "
                    f"template_id={cached.template_id} persona={cached.persona}"
                )
                return ResolvedPlanV2(
                    combo_key=combo_key,
                    match=cached,
                    template=template,
                )
            logger.info(
                f"resolve_plan_v2: combo={combo_key!r} cache STALE "
                f"(model={cached_model!r} vs {_CLASSIFIER_MODEL_V2!r}, "
                f"version={cached_version} vs "
                f"{template.registry_version if template else 'n/a'}) — re-classifying"
            )

    # ── Step 2: cache miss / stale → LLM classify against active templates
    if client is not None:
        try:
            active = _load_active_templates_v2(client)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                f"resolve_plan_v2: failed to load active templates: {exc} — "
                "classifier will see an empty set (every output will be no_match)"
            )
            active = []
    else:
        active = []  # offline / no DB — empty set forces no_match

    # The classifier needs ActiveTemplate wrappers, not TemplateSpecV2.
    from infra.classifier.llm_classifier import ActiveTemplate  # noqa: WPS433
    active_for_llm = [
        ActiveTemplate(
            template_id=t.template_id,
            primary_runtime=t.primary_runtime,
            personas=t.personas,
            eval_methods=t.eval_methods,
            capabilities=t.capabilities,
            description=t.description,
        )
        for t in active
    ]

    try:
        match = classify_match_v2(competencies, active_for_llm)
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            f"resolve_plan_v2: classifier failed for {combo_key!r}: {exc} — "
            "returning empty plan (no persona, no gate)"
        )
        return ResolvedPlanV2(combo_key=combo_key, match=None, template=None)

    # Hydrate the template spec for the matched id (if any).
    template = None
    registry_version = 1
    if match.template_id is not None and client is not None:
        try:
            template = _get_template_v2(client, match.template_id)
            if template is not None:
                registry_version = template.registry_version
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                f"resolve_plan_v2: template fetch failed for "
                f"{match.template_id!r}: {exc}"
            )

    # ── Step 3: best-effort write-through to cache ─────────────────────
    if client is not None:
        try:
            _match_write_v2(client, combo_key, match,
                            registry_version=registry_version)
            logger.info(
                f"resolve_plan_v2: combo={combo_key!r} cache WRITE — "
                f"template_id={match.template_id} persona={match.persona} "
                f"confidence={match.confidence:.2f}"
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                f"resolve_plan_v2: cache write failed for {combo_key!r}: {exc}"
            )

    if template is None and match.template_id is not None:
        logger.info(
            f"resolve_plan_v2: combo={combo_key!r} matched "
            f"template_id={match.template_id!r} but no built template row "
            f"could be hydrated — gate will skip"
        )
    return ResolvedPlanV2(
        combo_key=combo_key,
        match=match,
        template=template,
    )
