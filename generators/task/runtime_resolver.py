"""Resolve a competency combo into a complete plan for the rest of the pipeline.

The single entry point for the question *"what infrastructure does this task
need?"* Reads/writes the ``task_template_match`` cache, calls the LLM
classifier on misses, hydrates the matched ``templates`` row, and returns
one bundle every downstream stage reads.

A ``ResolvedPlan`` carries two things:
  • ``match``    — the classifier's ``TaskTemplateMatch`` (template_id + persona)
  • ``template`` — the hydrated ``TemplateSpec`` (build/test/install + capabilities)

Per-task ``TaskIntent`` does NOT live here — see
``infra/classifier/runtime.TaskIntent`` for that model (in-memory only;
the ``tasks.task_intent`` column was dropped pending a live consumer).
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from infra.logger_config import logger
from infra.classifier.runtime import Competency, TaskTemplateMatch


# Cache-invalidation knob: bump when the classifier prompt OR the model
# changes so old rows re-classify.
_CLASSIFIER_MODEL = "claude-sonnet-4-6"

# Supabase table names — kept here so resolve_plan() is the only module
# coupled to the schema.
_TEMPLATES_TABLE = "templates"
_MATCH_TABLE = "task_template_match"


@dataclass(frozen=True)
class TemplateSpec:
    """Hydrated row from ``templates``.

    Used by the eval gate (template_id + build/test/compile + secondary
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
    # Provenance — when the capability sheet was emitted from the
    # manifest. Bumps on re-seed / re-insert, otherwise stable. ISO-8601
    # string as returned by Supabase. None when the column hasn't been
    # added yet (pre-migration) or the row predates it.
    generated_at: str | None = None


@dataclass(frozen=True)
class ResolvedPlan:
    """The single bundle every downstream consumer reads.

    Carries the match decision (cached per combo) + the hydrated template
    spec. Does NOT carry ``task_intent`` — that's emitted later by the
    content-generation LLM (model exists in
    ``infra/classifier/runtime.TaskIntent`` but isn't persisted today).

    On classifier failure, ``match`` is None — callers skip persona
    routing and skip the gate. When the classifier returned a useful
    no-match (``match.template_id is None`` but ``match.suggested_template``
    is set), ``template`` is a SYNTHESIZED ``TemplateSpec``
    (``registry_version == 0``) so the prompt-generator and task-creator
    can still proceed for pure-local tasks. The build/test gate still
    SKIPS for synthesized templates — see ``gate_supported`` below.
    """

    combo_key: str
    match: TaskTemplateMatch | None
    template: TemplateSpec | None

    @property
    def gate_supported(self) -> bool:
        """True when a BUILT template backs the plan — the build/test gate
        can boot it. False for synthesized fallbacks (``registry_version``
        is 0) and for completely empty plans.
        """
        return self.template is not None and self.template.registry_version > 0

    @property
    def is_synthesized(self) -> bool:
        """True when ``template`` is a fallback synthesized from
        ``match.suggested_template`` rather than a real built row.
        """
        return self.template is not None and self.template.registry_version == 0


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
    we build one here.

    Prefers ``SUPABASE_SERVICE_ROLE_KEY_APTITUDETESTSDEV`` over the anon key
    so RLS-protected tables (``task_template_match``, ``tasks``, etc.) are
    readable here. Falls back to anon for environments without a service-role
    key.
    """
    from supabase import create_client  # local import keeps this file importable without supabase installed
    url = os.getenv("SUPABASE_URL_APTITUDETESTSDEV")
    key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY_APTITUDETESTSDEV")
        or os.getenv("SUPABASE_API_KEY_APTITUDETESTSDEV")
    )
    if not url or not key:
        raise RuntimeError("Missing SUPABASE_URL_APTITUDETESTSDEV / SUPABASE_API_KEY_APTITUDETESTSDEV")
    return create_client(url, key)


def _row_to_template(row: dict) -> TemplateSpec:
    """Convert one ``templates`` row dict into a ``TemplateSpec``."""
    return TemplateSpec(
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
        generated_at=row.get("generated_at"),
    )


def _load_active_templates(supabase) -> list[TemplateSpec]:
    """SELECT every ``built`` template row, hydrated as ``TemplateSpec``.

    The LLM classifier reads these capability sheets to match a competency
    combo to one of the deployable templates.
    """
    resp = (supabase.table(_TEMPLATES_TABLE)
            .select("*")
            .eq("status", "built")
            .execute())
    return [_row_to_template(r) for r in (resp.data or [])]


def _get_template(supabase, template_id: str) -> TemplateSpec | None:
    """Fetch one ``templates`` row by id. Returns None if absent or not built."""
    resp = (supabase.table(_TEMPLATES_TABLE)
            .select("*")
            .eq("template_id", template_id)
            .eq("status", "built")
            .limit(1)
            .execute())
    rows = resp.data or []
    if not rows:
        return None
    return _row_to_template(rows[0])


def _synthesize_template_from_match(
    match: TaskTemplateMatch | None,
) -> TemplateSpec | None:
    """Synthesize a minimal ``TemplateSpec`` from a no-match decision.

    Used when the LLM classifier ran successfully and returned a useful
    no-match verdict — i.e. ``match.template_id is None`` BUT
    ``match.suggested_template`` is populated — and we still want the
    rest of the pipeline (prompt generator + task creator) to proceed
    because the task is pure-local (no Docker / no datastore needed).

    The synthesized spec is identifiable by ``registry_version == 0`` so
    the build/test gate can skip cleanly without trying to boot a
    sandbox that does not exist yet.

    Returns None when no synthesis is possible (no suggested_template and
    no missing_capabilities to work with).
    """
    if match is None:
        return None
    suggested = match.suggested_template
    missing = list(match.missing_capabilities or [])
    if not suggested and not missing:
        return None

    template_id = suggested or "synthesized-fallback"
    # We deliberately do NOT hard-code language/runtime maps here — the
    # downstream LLM infers the runtime from competency names + scope +
    # references. We just pass the classifier's own hint, stripped of
    # the convention prefix so the field stays consistent with built
    # templates ("python", "node", etc. rather than "utkrusht-python").
    primary_runtime = suggested or ""
    if primary_runtime.startswith("utkrusht-"):
        primary_runtime = primary_runtime[len("utkrusht-"):]
    personas = [match.persona] if match.persona else []

    return TemplateSpec(
        template_id=template_id,
        primary_runtime=primary_runtime,
        personas=personas,
        eval_methods=["test_suite"],
        capabilities={
            "frameworks": missing,
            "datastores": [],
        },
        build_cmd="",
        test_cmd="",
        compile_cmd=None,
        install_cmd=None,
        install_verify=None,
        install_seconds=None,
        manifest_hash="",
        registry_version=0,  # marker: synthesized, not a built row
        description=(
            f"Synthesized fallback for combo with no built template "
            f"(suggested: {suggested or 'n/a'})."
        ),
        generated_at=None,
    )


def _match_lookup(supabase, combo_key: str) -> tuple[TaskTemplateMatch | None, int | None, str | None]:
    """Return (match, cached_registry_version, classifier_model) for combo_key.

    ``(None, None, None)`` on miss. The registry_version + classifier_model
    are returned so the caller can validate freshness before trusting the
    cached match.
    """
    resp = (supabase.table(_MATCH_TABLE)
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


def _match_write(
    supabase,
    combo_key: str,
    match: TaskTemplateMatch,
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
        "classifier_model": _CLASSIFIER_MODEL,
        "registry_version": registry_version,
        # Refresh classified_at on EVERY upsert so UPDATE flows (re-
        # classification after a model bump / registry_version bump)
        # bump the timestamp. Postgres DEFAULT only fires on INSERT, so
        # UPDATEs would otherwise leave the row stamped with its original
        # classification time. UTC ISO-8601 — Supabase accepts that for
        # timestamptz.
        "classified_at": datetime.now(timezone.utc).isoformat(),
    }
    supabase.table(_MATCH_TABLE).upsert(payload).execute()


def _is_match_fresh(
    cached_model: str | None,
    cached_version: int | None,
    template: TemplateSpec | None,
) -> bool:
    """Stale rows auto-re-classify when the model or template registry changes.

    Rules:
      * Model mismatch → stale (the prompt may have changed semantics).
      * If the cache pointed at a real built template and that template's
        registry_version has bumped → stale.
      * no_match rows survive registry bumps (a new template might
        un-block them, but that's only worth re-evaluating on a model
        change; otherwise we'd re-call the LLM on every template insert).
      * Synthesized fallback templates (``registry_version == 0``) skip
        the version check — same rationale as no_match: version doesn't
        apply to a row that was never persisted in ``templates``.
    """
    if cached_model != _CLASSIFIER_MODEL:
        return False
    if (template is not None
            and template.registry_version > 0
            and cached_version != template.registry_version):
        return False
    return True


def resolve_plan(
    competencies: Iterable[Competency],
    *,
    supabase=None,
) -> ResolvedPlan:
    """Resolve a competency combo into a plan.

    Lookup order:
      1. ``task_template_match`` cache hit for combo_key (+ freshness check).
      2. Cache miss → call ``classify_match`` with the active templates
         → upsert the new match row → return.
      3. Cache unreachable → direct LLM call without persistence.
      4. LLM failure → return an empty plan (callers skip persona + gate).

    Never raises. Scenario / background are NOT inputs — those go to the
    content-generation LLM, which emits ``TaskIntent`` per task.
    """
    # Local imports so the module is importable without supabase / pydantic
    # in environments that only use the helpers.
    from infra.classifier.llm_classifier import ActiveTemplate, classify_match  # noqa: WPS433

    competencies = list(competencies)
    combo_key = make_combo_key(competencies)

    # ── Step 1: try the cache ──────────────────────────────────────────
    client = supabase
    if client is None:
        try:
            client = _build_supabase_client()
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                f"resolve_plan: supabase init failed for {combo_key!r}: {exc} — "
                "falling through to direct LLM call (no caching)"
            )
            client = None

    if client is not None:
        try:
            cached, cached_version, cached_model = _match_lookup(client, combo_key)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                f"resolve_plan: cache lookup failed for {combo_key!r}: {exc} — "
                "falling through to direct LLM call"
            )
            cached, cached_version, cached_model = None, None, None

        if cached is not None:
            template = (_get_template(client, cached.template_id)
                        if cached.template_id else None)
            # Fallback synthesis: cached no-match decision with a useful
            # suggested_template → synthesize so downstream stages don't
            # hard-fail on a pure-local task.
            if template is None and cached.template_id is None:
                template = _synthesize_template_from_match(cached)
                if template is not None:
                    logger.info(
                        f"resolve_plan: combo={combo_key!r} cache HIT "
                        f"(no-match) — synthesized template "
                        f"{template.template_id!r} from suggested_template"
                    )
            if _is_match_fresh(cached_model, cached_version, template):
                logger.info(
                    f"resolve_plan: combo={combo_key!r} cache HIT "
                    f"template_id={cached.template_id} persona={cached.persona}"
                )
                return ResolvedPlan(
                    combo_key=combo_key,
                    match=cached,
                    template=template,
                )
            logger.info(
                f"resolve_plan: combo={combo_key!r} cache STALE "
                f"(model={cached_model!r} vs {_CLASSIFIER_MODEL!r}, "
                f"version={cached_version} vs "
                f"{template.registry_version if template else 'n/a'}) — re-classifying"
            )

    # ── Step 2: cache miss / stale → LLM classify against active templates
    if client is not None:
        try:
            active = _load_active_templates(client)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                f"resolve_plan: failed to load active templates: {exc} — "
                "classifier will see an empty set (every output will be no_match)"
            )
            active = []
    else:
        active = []  # offline / no DB — empty set forces no_match

    # The classifier needs ActiveTemplate wrappers, not TemplateSpec.
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
        match = classify_match(competencies, active_for_llm)
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            f"resolve_plan: classifier failed for {combo_key!r}: {exc} — "
            "returning empty plan (no persona, no gate)"
        )
        return ResolvedPlan(combo_key=combo_key, match=None, template=None)

    # Hydrate the template spec for the matched id (if any).
    template = None
    registry_version = 1
    if match.template_id is not None and client is not None:
        try:
            template = _get_template(client, match.template_id)
            if template is not None:
                registry_version = template.registry_version
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                f"resolve_plan: template fetch failed for "
                f"{match.template_id!r}: {exc}"
            )

    # ── Step 3: best-effort write-through to cache ─────────────────────
    if client is not None:
        try:
            _match_write(client, combo_key, match,
                         registry_version=registry_version)
            logger.info(
                f"resolve_plan: combo={combo_key!r} cache WRITE — "
                f"template_id={match.template_id} persona={match.persona} "
                f"confidence={match.confidence:.2f}"
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                f"resolve_plan: cache write failed for {combo_key!r}: {exc}"
            )

    if template is None and match.template_id is not None:
        logger.info(
            f"resolve_plan: combo={combo_key!r} matched "
            f"template_id={match.template_id!r} but no built template row "
            f"could be hydrated — gate will skip"
        )

    # Fallback synthesis: classifier returned a useful no-match decision
    # (no matching built template, but suggested_template is set). Synth
    # a minimal TemplateSpec so prompt generation + task creation can
    # still proceed for pure-local tasks. The build/test gate stays
    # skipped (registry_version == 0 → gate_supported is False).
    if template is None and match.template_id is None:
        template = _synthesize_template_from_match(match)
        if template is not None:
            logger.info(
                f"resolve_plan: combo={combo_key!r} no built template — "
                f"synthesized fallback {template.template_id!r} "
                f"(missing_capabilities={match.missing_capabilities})"
            )

    return ResolvedPlan(
        combo_key=combo_key,
        match=match,
        template=template,
    )
