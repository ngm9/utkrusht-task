"""Structured runtime spec for a generated task.

Replaces the legacy TaskCategory enum with a multi-dimensional record that
captures everything downstream code needs to scaffold a task:

  • runtime   — the language SDK the E2B template must preinstall
  • frameworks — named framework libraries (fastapi, spring-boot, …)
  • datastores — DB servers the task brings up via docker-compose
  • messaging  — Kafka/queue brokers the task brings up
  • needs_browser — True for Playwright/Selenium (template needs Chromium)
  • kind       — high-level shape that picks the prompt-template strategy
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Runtime = Literal[
    "python", "node", "java", "php", "go", "rust",
    "flutter", "ruby", "scala", "none",
]

Kind = Literal[
    "app", "script", "mobile", "frontend", "testing",
    "db_only", "llm", "vector_db", "non_code",
]


class TaskRuntime(BaseModel):
    """Multi-dimensional infrastructure spec for one task."""

    model_config = ConfigDict(frozen=True)

    runtime: Runtime
    frameworks: list[str] = Field(default_factory=list)
    datastores: list[str] = Field(default_factory=list)
    messaging: list[str] = Field(default_factory=list)
    needs_browser: bool = False
    kind: Kind


@dataclass(frozen=True)
class Competency:
    """Normalised competency tuple — the classifier's input."""

    name: str
    proficiency: str

    @property
    def name_lower(self) -> str:
        return self.name.lower()
