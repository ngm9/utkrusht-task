"""E2B sandbox-based task deployment flow.

Alternate deployment path for assessment tasks. Mirrors
``multiagent.py deploy-task`` / ``reset-task`` but targets E2B sandboxes
instead of DigitalOcean droplets. Existing droplet flow is untouched.

Entry point: ``python -m e2b_flow``.
"""

__version__ = "0.1.0"
