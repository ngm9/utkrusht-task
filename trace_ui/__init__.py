"""trace_ui — a tiny LIVE trace/log viewer for pipeline runs.

Streams a `run_pipeline.py` run's stage logs + captured LLM traces to a
browser in real time over Server-Sent Events. No build step, no extra deps:
FastAPI + uvicorn (already vendored for task_builder) and one static HTML
file with vanilla JS.

Run it with::

    python -m trace_ui

then open http://127.0.0.1:8765/ and pick a run.
"""

__all__ = ["__version__"]

__version__ = "0.1.0"
