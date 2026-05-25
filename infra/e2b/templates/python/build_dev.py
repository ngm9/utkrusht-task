import asyncio

from dotenv import load_dotenv
from e2b import AsyncTemplate, default_build_logger

from template import template

# Pick up E2B_API_KEY from a .env in this dir or any parent (repo root).
load_dotenv()


async def main():
    await AsyncTemplate.build(
        template,
        "utkrusht-python-dev",
        cpu_count=2,
        memory_mb=2048,
        on_build_logs=default_build_logger(),
    )


if __name__ == "__main__":
    asyncio.run(main())
