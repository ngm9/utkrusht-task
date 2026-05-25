"""E2B sandbox-based task deployment flow.

The live deploy path for assessment tasks. Provisions E2B sandboxes and
writes E2B-tagged ``deployment_info`` back to Supabase. (The DigitalOcean
droplet path was retired on 2026-05-25.)

Entry point: ``python -m infra.e2b``.
"""

__version__ = "0.1.0"
