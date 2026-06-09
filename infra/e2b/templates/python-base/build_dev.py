import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from e2b import AsyncTemplate, default_build_logger

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from infra.e2b.manifest import write_manifest  # noqa: E402
from template import manifest, template  # noqa: E402

# Pick up E2B_API_KEY from a .env in this dir or any parent (repo root).
load_dotenv()


def emit_manifest() -> dict:
    """Write manifest.json + manifest_hash next to template.py.

    Mirrors ``build_prod.py``: a dev build that changes ``template.py``'s
    ``manifest`` dict must refresh the on-disk artifacts so downstream
    consumers (LLM classifier, drift checks) see the current values.
    """
    template_dir = Path(__file__).resolve().parent
    return write_manifest(template_dir, manifest)


async def main() -> None:
    info = emit_manifest()
    print(
        f"manifest written: {info['manifest_path']} "
        f"(sha256={info['manifest_hash']})"
    )
    # Derive the dev template id from the prod id so the rename only has to
    # happen in one place (manifest["template_id"] in template.py).
    dev_template_id = f"{manifest['template_id']}-dev"
    await AsyncTemplate.build(
        template,
        dev_template_id,
        cpu_count=2,
        memory_mb=2048,
        on_build_logs=default_build_logger(),
    )


if __name__ == "__main__":
    asyncio.run(main())
