"""
Design Review Task Generation package.

Generates UI/UX assessment tasks where candidates review Figma designs with intentional flaws.

Usage as CLI:
    python -m design_review_flow generate --competency-file <path> --library-entry-id <id>
    python -m design_review_flow store --spec-file <path> --figma-link <url>
"""

from design_review_flow.design_review_multiagent import (
    create_design_review_task,
    store_design_review_task,
)

__all__ = ["create_design_review_task", "store_design_review_task"]
