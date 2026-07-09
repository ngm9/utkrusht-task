"""``python -m flows.tech`` — run the tech task-generation pipeline.

Thin entry point; the orchestrator lives in ``flows.tech.pipeline``.
"""
import sys

from flows.tech.pipeline import main

if __name__ == "__main__":
    sys.exit(main())
