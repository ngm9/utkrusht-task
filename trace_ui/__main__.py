"""Launch the trace UI server: ``python -m trace_ui``.

Binds to 127.0.0.1:8765 by default (local-only; this exposes run logs and LLM
prompts, so it must not be served on a public interface). Override the port
with ``TRACE_UI_PORT`` and the host with ``TRACE_UI_HOST`` if you really need to.
"""

import os

import uvicorn

if __name__ == "__main__":
    host = os.environ.get("TRACE_UI_HOST", "127.0.0.1")
    port = int(os.environ.get("TRACE_UI_PORT") or "8765")
    uvicorn.run("trace_ui.server:app", host=host, port=port, reload=False)
