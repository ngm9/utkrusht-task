"""PR review variant — model + DAO.

PR review tasks share the ``tasks`` table but have a different blob shape:
  - ``task_blob.task_type`` is fixed to ``"pr_review"``
  - ``task_blob.short_overview`` and ``task_blob.outcomes`` are STRINGS
    (the coding flow uses ``List[str]`` for both)
  - ``task_blob.resources`` must contain both ``github_repo`` and
    ``github_pr`` (the coding flow only requires ``github_repo``)
  - ``task_blob.hints`` and ``task_blob.definitions`` may be empty
  - top-level ``pre_requisites`` is a STRING (hardcoded in the flow)
  - top-level ``answer`` may be empty (the answer key lives in
    ``solutions``)
  - ``solutions`` carries flaw-key fields instead of ``answer_repo``
  - ``eval_info`` uses ``phase1`` / ``phase2`` rather than
    ``task_eval`` / ``code_eval``
"""
from __future__ import annotations

from typing import ClassVar, Dict, List, Optional, Type

from pydantic import BaseModel, field_validator, model_validator

from task_validation.base import BaseTaskDAO, CriteriaEntry


class PRReviewTaskBlob(BaseModel):
    model_config = {"strict": True}

    title: str
    task_type: str
    question: str
    short_overview: str
    outcomes: str
    resources: Dict[str, str]
    hints: str
    definitions: Dict[str, str]

    @field_validator("title", "question", "short_overview", "outcomes")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must not be empty")
        return v

    @field_validator("task_type")
    @classmethod
    def task_type_is_pr_review(cls, v: str) -> str:
        if v != "pr_review":
            raise ValueError("must be exactly 'pr_review'")
        return v

    @field_validator("resources")
    @classmethod
    def resources_has_repo_and_pr(cls, v: Dict[str, str]) -> Dict[str, str]:
        for key in ("github_repo", "github_pr"):
            if not v.get(key, "").strip():
                raise ValueError(f"must contain a non-empty '{key}' key")
        return v


class PRReviewTaskForDB(BaseModel):
    model_config = {"strict": True}

    created_at: str
    pre_requisites: str
    answer: str
    criterias: List[CriteriaEntry]
    is_deployed: bool
    task_blob: PRReviewTaskBlob
    is_shared_infra_required: bool
    readme_content: Optional[Dict] = None
    eval_info: Dict
    solutions: Dict

    @field_validator("created_at", "pre_requisites")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must not be empty")
        return v

    @field_validator("criterias")
    @classmethod
    def criterias_not_empty(cls, v: List[CriteriaEntry]) -> List[CriteriaEntry]:
        if not v:
            raise ValueError("must contain at least one entry")
        return v

    @field_validator("eval_info")
    @classmethod
    def eval_info_has_phases(cls, v: Dict) -> Dict:
        for key in ("phase1", "phase2"):
            if key not in v:
                raise ValueError(f"must contain '{key}' key")
        return v

    @field_validator("solutions")
    @classmethod
    def solutions_has_pr_keys(cls, v: Dict) -> Dict:
        for key in ("steps", "overall_verdict", "pr_description_issues"):
            if key not in v:
                raise ValueError(f"must contain '{key}' key")
        if not isinstance(v.get("overall_verdict"), str) or not v["overall_verdict"].strip():
            raise ValueError("'overall_verdict' must be a non-empty string")
        return v

    @field_validator("is_deployed")
    @classmethod
    def must_be_false_at_insert(cls, v: bool) -> bool:
        if v is not False:
            raise ValueError("must be False at insert time")
        return v

    @model_validator(mode="after")
    def no_duplicate_competency_ids(self) -> "PRReviewTaskForDB":
        ids = [c.competency_id for c in self.criterias]
        seen, dupes = set(), set()
        for cid in ids:
            if cid in seen:
                dupes.add(cid)
            seen.add(cid)
        if dupes:
            raise ValueError(
                f"criterias contains duplicate competency_id values: {sorted(dupes)}"
            )
        return self


class PRReviewTaskDAO(BaseTaskDAO):
    """DAO for PR review tasks. Inherits FK check + insert from BaseTaskDAO."""

    MODEL: ClassVar[Type[BaseModel]] = PRReviewTaskForDB
