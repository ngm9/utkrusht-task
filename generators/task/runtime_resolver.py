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
    """Read one row from ``template_registry`` by runtime. ``None`` when absent."""
    resp = (supabase.table(_TEMPLATE_TABLE)
            .select("template_name,build_cmd,test_cmd,compile_cmd,needs_browser")
            .eq("runtime", runtime)
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


def _utkrusht_org_id() -> Optional[str]:
    """Read the Utkrusht UUID from env. None if unset (caller treats as no cache)."""
    return os.getenv("UTKRUSHT_ORG_ID")


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


def _cache_lookup(supabase, combo_key: str, org_id: str) -> Optional[TaskRuntime]:
    """Return the cached TaskRuntime for this combo, or None on miss."""
    resp = (supabase.table(_COMBO_TABLE)
            .select("runtime,kind,frameworks,datastores,messaging,needs_browser")
            .eq("combo_key", combo_key)
            .eq("organization_id", org_id)
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


def _cache_write(supabase, combo_key: str, org_id: str,
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
        "organization_id": org_id,
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
    org_id = _utkrusht_org_id()

    # ── Step 1: try the cache ──────────────────────────────────────────
    client = supabase
    if client is None and org_id is not None:
        try:
            client = _build_supabase_client()
        except Exception as exc:   # noqa: BLE001
            logger.warning(
                f"resolve_plan: supabase init failed for {combo_key!r}: {exc} — "
                "falling through to direct LLM call (no caching)"
            )
            client = None

    if client is not None and org_id is not None:
        try:
            cached = _cache_lookup(client, combo_key, org_id)
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
    if client is not None and org_id is not None:
        try:
            _cache_write(client, combo_key, org_id, task_runtime, confidence)
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
