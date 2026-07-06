"""Runtime E2B template builder.

Called by ``resolve_plan`` (generators/task/runtime_resolver.py) when the
LLM classifier returns a ``suggested_template`` or ``template_id`` that has
no ``status='built'`` row in the Supabase ``templates`` table.

``build_if_missing`` is the single public entry point:
  - Finds the local template definition in ``infra/e2b/templates/<id>/template.py``
  - Guards against concurrent builds via a ``status='building'`` DB lock
  - Calls ``AsyncTemplate.build()`` (blocking, ~10 min)
  - Upserts ``status='built'`` + manifest into Supabase
  - Deletes stale ``task_template_match`` no_match rows so the next
    ``resolve_plan`` call re-classifies against the new template
  - Returns a ``TemplateSpec`` on success, ``None`` on any failure

Never raises — callers degrade to the existing gate-skip behaviour on None.
"""
from __future__ import annotations

import asyncio
import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from infra.logger_config import logger

if TYPE_CHECKING:
    from generators.task.runtime_resolver import TemplateSpec

_TEMPLATES_DIR = Path(__file__).parent / "templates"
_E2B_CPU = 2
_E2B_MEMORY_MB = 2048


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _load_template_definition(template_id: str):
    """Load (manifest, template) from infra/e2b/templates/<dir>/template.py.

    Directory names use short names WITHOUT the ``utkrusht-`` prefix
    (e.g. ``node-base``, ``dotnet``, ``python-base``), while template_ids
    carry the full prefix (e.g. ``utkrusht-node-base``, ``utkrusht-dotnet``).
    We try both the full template_id and the stripped form so callers can
    pass either.

    Returns (None, None) if no matching directory is found.
    """
    candidates = [template_id]
    if template_id.startswith("utkrusht-"):
        candidates.append(template_id[len("utkrusht-"):])

    template_py = None
    for dir_name in candidates:
        p = _TEMPLATES_DIR / dir_name / "template.py"
        if p.exists():
            template_py = p
            break

    if template_py is None:
        return None, None

    module_name = f"_e2b_tmpl_{template_id.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, template_py)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:
        logger.warning(
            f"template_builder: failed to load {template_py}: {exc}"
        )
        return None, None

    return getattr(mod, "manifest", None), getattr(mod, "template", None)


def _get_current_status(supabase, template_id: str) -> str | None:
    """Return the current ``templates.status`` for template_id, or None if absent."""
    try:
        resp = (
            supabase.table("templates")
            .select("status")
            .eq("template_id", template_id)
            .limit(1)
            .execute()
        )
        rows = resp.data or []
        return rows[0]["status"] if rows else None
    except Exception as exc:
        logger.warning(f"template_builder: status check failed for {template_id!r}: {exc}")
        return None


def _upsert_status(supabase, template_id: str, manifest: dict, status: str, manifest_hash: str = "") -> None:
    """Upsert the templates row with the given status.

    Always supplies the three NOT NULL / no-default columns the schema requires:
      - ``manifest_hash``        — empty string for 'building', actual hash for 'built'
      - ``manifest_generated_at``— current UTC timestamp (ISO-8601)
      - ``registry_version``     — from manifest or 1
    """
    from datetime import datetime, timezone
    now_iso = datetime.now(timezone.utc).isoformat()
    payload = {
        **manifest,
        # Always enforce the caller's template_id — overrides whatever manifest says.
        "template_id": template_id,
        "status": status,
        "manifest_hash": manifest_hash or "",
        "manifest_generated_at": now_iso,
        "registry_version": int(manifest.get("registry_version") or 1),
    }
    try:
        supabase.table("templates").upsert(payload).execute()
        logger.info(
            f"template_builder: upserted {template_id!r} status={status!r}"
        )
    except Exception as exc:
        logger.error(
            f"template_builder: upsert FAILED for {template_id!r} "
            f"status={status!r}: {type(exc).__name__}: {exc}"
        )


def _invalidate_match_cache(supabase, template_id: str) -> None:
    """Delete stale no_match cache rows that pointed at this template as suggested.

    After a successful build, the LLM classifier must re-run for any combo
    that previously had no_match — otherwise the cached no_match row would
    prevent the newly built template from being picked up.
    """
    try:
        supabase.table("task_template_match").delete().eq(
            "suggested_template", template_id
        ).execute()
        logger.info(
            f"template_builder: invalidated task_template_match rows "
            f"with suggested_template={template_id!r}"
        )
    except Exception as exc:
        logger.warning(
            f"template_builder: cache invalidation failed for {template_id!r}: {exc}"
        )


def _row_to_template_spec(manifest: dict, manifest_hash: str):
    """Convert manifest dict + hash into a TemplateSpec (avoids circular import)."""
    from generators.task.runtime_resolver import TemplateSpec
    return TemplateSpec(
        template_id=manifest["template_id"],
        primary_runtime=manifest["primary_runtime"],
        personas=manifest.get("personas") or [],
        eval_methods=manifest.get("eval_methods") or ["test_suite"],
        capabilities=manifest.get("capabilities") or {},
        build_cmd=manifest["build_cmd"],
        test_cmd=manifest["test_cmd"],
        compile_cmd=manifest.get("compile_cmd"),
        install_cmd=manifest.get("install_cmd"),
        install_verify=manifest.get("install_verify"),
        install_seconds=manifest.get("install_seconds"),
        manifest_hash=manifest_hash,
        registry_version=int(manifest.get("registry_version") or 1),
        description=manifest.get("description"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def build_if_missing(template_id: str, supabase) -> "TemplateSpec | None":
    """Build and register an E2B template if a local definition exists but no
    built row is in the Supabase ``templates`` table.

    Steps:
      1. Load ``infra/e2b/templates/<template_id>/template.py`` via importlib.
         Return None immediately if the directory does not exist.
      2. Check current DB status.  Return None if already ``'built'`` or ``'building'``.
      3. Upsert ``status='building'`` (distributed lock).
      4. Call ``AsyncTemplate.build()`` via ``asyncio.run()`` (blocking ~10 min).
      5. Write ``manifest.json`` + ``manifest_hash`` to the template directory.
      6. Upsert ``status='built'`` with the manifest hash.
      7. Delete stale ``task_template_match`` rows so next run re-classifies.
      8. Return a ``TemplateSpec`` built from the manifest.

    Returns None on any failure — callers fall back to the existing skip path.
    Never raises.
    """
    from e2b import AsyncTemplate
    from infra.e2b.manifest import write_manifest

    # Step 1 — local definition
    manifest, template_def = _load_template_definition(template_id)
    if manifest is None or template_def is None:
        logger.info(
            f"template_builder: no local definition found for {template_id!r} "
            f"— skipping build (hand-author infra/e2b/templates/<id>/template.py to enable)"
        )
        return None

    # Step 2 — distributed lock check
    current_status = _get_current_status(supabase, template_id)
    if current_status == "built":
        logger.info(
            f"template_builder: {template_id!r} already built — returning spec from manifest"
        )
        try:
            return _row_to_template_spec(manifest, manifest_hash="")
        except Exception as exc:
            logger.warning(
                f"template_builder: could not build TemplateSpec for already-built "
                f"{template_id!r}: {exc}"
            )
            return None
    if current_status == "building":
        logger.info(
            f"template_builder: {template_id!r} is already building "
            f"(another process) — skipping to avoid duplicate build"
        )
        return None

    # Step 3 — claim the build slot
    logger.info(
        f"template_builder: claiming build slot for {template_id!r} "
        f"(current_status={current_status!r})"
    )
    _upsert_status(supabase, template_id, manifest, "building")

    # Step 4 — build (blocking, ~10 min)
    logger.info(
        f"template_builder: starting AsyncTemplate.build for {template_id!r} "
        f"— this takes ~10 minutes, pipeline will resume after"
    )
    try:
        asyncio.run(
            AsyncTemplate.build(
                template_def,
                template_id,
                cpu_count=_E2B_CPU,
                memory_mb=_E2B_MEMORY_MB,
            )
        )
    except Exception as exc:
        logger.error(
            f"template_builder: AsyncTemplate.build FAILED for {template_id!r}: {exc}"
        )
        _upsert_status(supabase, template_id, manifest, "failed")
        return None

    logger.info(f"template_builder: build complete for {template_id!r}")

    # Step 5 — write manifest artifacts to disk
    template_dir = _TEMPLATES_DIR / template_id
    try:
        info = write_manifest(template_dir, manifest)
        manifest_hash = info["manifest_hash"]
    except Exception as exc:
        logger.warning(
            f"template_builder: write_manifest failed for {template_id!r}: {exc} "
            f"— using empty hash"
        )
        manifest_hash = ""

    # Step 6 — mark built in Supabase
    _upsert_status(supabase, template_id, manifest, "built", manifest_hash)
    logger.info(
        f"template_builder: {template_id!r} registered in Supabase "
        f"status='built' hash={manifest_hash[:12]}…"
    )

    # Step 7 — invalidate stale no_match cache
    _invalidate_match_cache(supabase, template_id)

    # Step 8 — return TemplateSpec so resolve_plan can hydrate immediately
    try:
        return _row_to_template_spec(manifest, manifest_hash)
    except Exception as exc:
        logger.warning(
            f"template_builder: could not build TemplateSpec for {template_id!r}: {exc}"
        )
        return None
