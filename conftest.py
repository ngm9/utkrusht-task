"""Pytest root conftest — loads ``.env`` so modules that initialize API clients
at import time (``evals.py``, ``multiagent.py``) succeed in test collection.

Imports that happen at the top of those modules currently include side-effects:

    eval_openai_client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"], ...)

Without this conftest, the OpenAI client init would raise ``OpenAIError`` and
pytest collection would abort before any test even runs.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env", override=False)
except ImportError:  # pragma: no cover
    # Fall back to whatever's already in the environment.
    pass

# Guard against accidentally running tests against prod Supabase by overriding
# only when a placeholder is missing.
os.environ.setdefault("OPENAI_API_KEY", "test-placeholder")
