"""Tools used by the task extractor pipeline.

These are plain Python functions — not LLM tool-call handlers.
They are called directly by extractor.py before and after the LLM call.

  fetch_external_code  — fetch starter code from external URLs (Gist, etc.)
  process_image        — upload embedded doc images to Drive, return URLs
  emit_task            — strip protected domains and write task-N-slug.md
"""
