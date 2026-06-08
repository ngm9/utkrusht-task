"""Launch the Task Builder web server: python -m task_builder.

Bind is env-driven so the same entrypoint works for local dev and container
deploy. Defaults are container-friendly (0.0.0.0 + :8000); override with
TASK_BUILDER_HOST / PORT if needed.
"""
import os

import uvicorn

if __name__ == "__main__":
    host = os.environ.get("TASK_BUILDER_HOST", "0.0.0.0")
    port = int(os.environ.get("PORT") or os.environ.get("TASK_BUILDER_PORT") or "8000")
    uvicorn.run("task_builder.server:app", host=host, port=port, reload=False)
