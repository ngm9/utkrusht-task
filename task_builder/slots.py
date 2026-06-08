"""TaskBrief — the six interview slots, owned authoritatively by the server."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, Field

VALID_PROFICIENCIES: tuple[str, ...] = ("BEGINNER", "BASIC", "INTERMEDIATE", "ADVANCED")
REQUIRED_SLOTS: tuple[str, ...] = ("competencies", "proficiency", "role",
                                   "focus_areas", "domain")


class TaskBrief(BaseModel):
    """The collected interview answers. `scenario_count` is optional (defaults to 6)."""

    competencies: list[str] = Field(default_factory=list)
    proficiency: str | None = None
    role: str | None = None
    focus_areas: list[str] = Field(default_factory=list)
    domain: str | None = None
    scenario_count: int = 6

    def missing_slots(self) -> list[str]:
        """Required slots that are still empty, in REQUIRED_SLOTS order."""
        return [slot for slot in REQUIRED_SLOTS if not getattr(self, slot)]

    def is_complete(self) -> bool:
        return not self.missing_slots()


def merge_brief(brief: TaskBrief, update: dict) -> TaskBrief:
    """Return a NEW TaskBrief with `update`'s known fields applied. Never mutates."""
    allowed = {k: v for k, v in update.items() if k in TaskBrief.model_fields}
    return brief.model_copy(update=allowed)


@dataclass
class Message:
    role: Literal["user", "assistant"]
    content: str


@dataclass
class SessionState:
    """In-memory per-conversation state.

    Lost on server restart — acceptable for a local single-user tool.
    """

    session_id: str
    brief: TaskBrief = field(default_factory=TaskBrief)
    history: list[Message] = field(default_factory=list)
