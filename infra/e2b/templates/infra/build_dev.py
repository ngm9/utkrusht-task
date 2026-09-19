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

load_dotenv()


async def main() -> None:
    template_dir = Path(__file__).resolve().parent
    info = write_manifest(template_dir, manifest)
    print(f"manifest written: {info['manifest_path']} (sha256={info['manifest_hash']})")
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
