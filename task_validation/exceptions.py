"""Failure and exception types raised by the task DAO.

Kept in their own module so models, helpers, and DAO classes can import
them without circular dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class ValidationFailure:
    field: str
    actual_value: Any
    constraint: str
    environment: Optional[str] = None

    def __str__(self) -> str:
        value_repr = repr(self.actual_value)
        if isinstance(self.actual_value, str) and len(self.actual_value) > 200:
            value_repr = repr(self.actual_value[:200] + "...")
        env_suffix = f" (env={self.environment})" if self.environment else ""
        return f"{self.field}: got {value_repr}, {self.constraint}{env_suffix}"


class TaskDAOError(Exception):
    """Base for everything raised by the task DAO."""


class TaskValidationError(TaskDAOError):
    def __init__(self, failures: List[ValidationFailure], task_name: str = "") -> None:
        self.failures = failures
        self.task_name = task_name
        super().__init__(str(self))

    def __str__(self) -> str:
        header = f"ValidationError for task '{self.task_name}': {len(self.failures)} check(s) failed"
        lines = [f"  [{i+1}] {f}" for i, f in enumerate(self.failures)]
        return "\n".join([header] + lines)


class TaskWriteError(TaskDAOError):
    def __init__(self, task_id: str, all_failures: List[str], environment: str) -> None:
        self.task_id = task_id
        self.all_failures = all_failures
        self.environment = environment
        super().__init__(str(self))

    def __str__(self) -> str:
        ids = ", ".join(f"'{c}'" for c in self.all_failures)
        return (
            f"TaskWriteError: task_competencies insert failed for task_id='{self.task_id}' in env={self.environment}\n"
            f"  Failed competency links: [{ids}]\n"
            f"  ACTION REQUIRED: Manually delete tasks row with task_id='{self.task_id}' "
            f"from Supabase {self.environment} before retrying."
        )
