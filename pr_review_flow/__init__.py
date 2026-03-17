"""
PR Review Task Generation package.

Generates assessment tasks where candidates review GitHub PRs with intentional flaws.

Usage as CLI:
    python -m pr_review_flow --competency-file <path> --background-file <path> --scenarios-file <path>
"""

from pr_review_flow.pr_review_multiagent import create_pr_review_task

__all__ = ["create_pr_review_task"]
