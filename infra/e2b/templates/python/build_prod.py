import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from e2b import AsyncTemplate, default_build_logger

# ``infra/e2b/manifest.py`` is three directories up from this file (which
# lives in ``infra/e2b/templates/python/``). Add the repo root to sys.path so
# this script can be run directly with ``python build_prod.py``.
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from infra.e2b.manifest import write_manifest  # noqa: E402
from template import manifest, template  # noqa: E402

# Pick up E2B_API_KEY from a .env in this dir or any parent (repo root).
load_dotenv()


def emit_manifest() -> dict:
    """Write manifest.json + manifest_hash next to template.py.

    Called unconditionally before the E2B build because the manifest
    describes the SOURCE of the template, not the deployed state — a failed
    upload should not block manifest emission.
    """
    template_dir = Path(__file__).resolve().parent
    return write_manifest(template_dir, manifest)


async def main() -> None:
    info = emit_manifest()
    print(
        f"manifest written: {info['manifest_path']} "
        f"(sha256={info['manifest_hash']})"
    )
    # Derive template id from the manifest so renaming is a one-line change
    # in template.py (manifest["template_id"]) — never edit the literal here.
    await AsyncTemplate.build(
        template,
        manifest["template_id"],
        cpu_count=2,
        memory_mb=2048,
        on_build_logs=default_build_logger(),
    )


if __name__ == "__main__":
    asyncio.run(main())
