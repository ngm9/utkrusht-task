from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional, Type, Union

from pydantic import BaseModel, field_validator, model_validator
from supabase import Client

from infra.logger_config import logger


# ---------------------------------------------------------------------------
# Failure & Exception types
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

_VALID_PROFICIENCIES = {"BEGINNER", "BASIC", "INTERMEDIATE", "ADVANCED", "EXPERT"}


class CriteriaEntry(BaseModel):
    competency_id: str
    proficiency: str
    name: str
    scope: Optional[str] = None

    @field_validator("competency_id")
    @classmethod
    def competency_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must not be empty")
        return v

    @field_validator("proficiency")
    @classmethod
    def proficiency_valid(cls, v: str) -> str:
        upper = v.upper() if v else ""
        if upper not in _VALID_PROFICIENCIES:
            raise ValueError(f"must be one of {', '.join(sorted(_VALID_PROFICIENCIES))}")
        return upper

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must not be empty")
        return v


class TaskBlob(BaseModel):
    model_config = {"strict": True}

    title: str
    definitions: Dict[str, str]
    hints: str
    resources: Dict[str, str]
    outcomes: List[str]
    question: str
    short_overview: List[str]

    @field_validator("title", "question", "hints")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must not be empty")
        return v

    @field_validator("definitions")
    @classmethod
    def definitions_non_empty(cls, v: Dict[str, str]) -> Dict[str, str]:
        if not v:
            raise ValueError("must not be empty")
        for key, value in v.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"value for key '{key}' must be a non-empty string")
        return v

    @field_validator("resources")
    @classmethod
    def resources_has_github_repo(cls, v: Dict[str, str]) -> Dict[str, str]:
        if not v.get("github_repo", "").strip():
            raise ValueError("must contain a non-empty 'github_repo' key")
        return v

    @field_validator("outcomes", "short_overview")
    @classmethod
    def list_not_empty(cls, v: List[str]) -> List[str]:
        if not isinstance(v, list):
            raise ValueError("must be a list of strings, not a string")
        if not v:
            raise ValueError("must not be an empty list")
        for item in v:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("every entry must be a non-empty string")
        return v


class TaskForDB(BaseModel):
    model_config = {"strict": True}

    created_at: str
    pre_requisites: List[str]
    answer: str
    criterias: List[CriteriaEntry]
    is_deployed: bool
    task_blob: TaskBlob
    is_shared_infra_required: bool
    readme_content: Dict
    eval_info: Dict
    solutions: Dict

    @field_validator("created_at", "answer")
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

    @field_validator("pre_requisites")
    @classmethod
    def pre_requisites_strict_list(cls, v: List[str]) -> List[str]:
        if not isinstance(v, list):
            raise ValueError("must be a list of strings, not a string")
        if not v:
            raise ValueError("must not be an empty list")
        for item in v:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("every entry must be a non-empty string")
        return v

    @field_validator("eval_info")
    @classmethod
    def eval_info_has_required_keys(cls, v: Dict) -> Dict:
        for key in ("task_eval", "code_eval"):
            if key not in v:
                raise ValueError(f"must contain '{key}' key")
        return v

    @field_validator("solutions")
    @classmethod
    def solutions_has_required_keys(cls, v: Dict) -> Dict:
        for key in ("steps", "answer_repo"):
            if key not in v:
                raise ValueError(f"must contain '{key}' key")
        if not isinstance(v.get("answer_repo"), str) or not v["answer_repo"].strip():
            raise ValueError("'answer_repo' must be a non-empty string")
        return v

    @field_validator("is_deployed")
    @classmethod
    def must_be_false_at_insert(cls, v: bool) -> bool:
        if v is not False:
            raise ValueError("must be False at insert time")
        return v

    @model_validator(mode="after")
    def no_duplicate_competency_ids(self) -> "TaskForDB":
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pydantic_errors_to_failures(exc: Exception, task_name: str) -> List[ValidationFailure]:
    from pydantic import ValidationError as PydanticValidationError

    failures: List[ValidationFailure] = []
    if isinstance(exc, PydanticValidationError):
        for err in exc.errors():
            loc = ".".join(str(p) for p in err["loc"])
            failures.append(ValidationFailure(
                field=loc,
                actual_value=err.get("input"),
                constraint=err["msg"].replace("Value error, ", ""),
            ))
    return failures


def _extract_task_name(task_data: dict) -> str:
    try:
        return task_data.get("task_blob", {}).get("title", "") or task_data.get("name", "unknown")
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# DAO
# ---------------------------------------------------------------------------

class BaseTaskDAO:
    """Single chokepoint for writes to ``tasks`` + ``task_competencies``.

    Mirrors the class-based DAO pattern used in
    ``flask_service/ats/daos.py``: one class per logical aggregate, taking
    a ``supabase.Client`` at construction time.

    Subclasses override ``MODEL`` to validate task variants (PR review,
    non-tech) that share the same target table but have different blob
    shapes. The FK pre-flight check and the two-step insert logic are
    inherited unchanged.

    Default ``MODEL`` is ``TaskForDB`` (the coding/tech-stack task variant),
    so callers that need that variant can instantiate this class directly.
    """

    MODEL: ClassVar[Type[BaseModel]] = TaskForDB

    def __init__(self, supabase_client: Client) -> None:
        self.supabase = supabase_client

    def validate(self, task_data: dict, env: str = "dev") -> BaseModel:
        from pydantic import ValidationError as PydanticValidationError

        task_name = _extract_task_name(task_data)
        failures: List[ValidationFailure] = []

        # 1. Schema validation
        try:
            validated = self.MODEL.model_validate(task_data)
        except PydanticValidationError as exc:
            failures.extend(_pydantic_errors_to_failures(exc, task_name))

        if failures:
            raise TaskValidationError(failures, task_name)

        # 2. FK pre-flight check
        competency_ids = list({c.competency_id for c in validated.criterias})
        try:
            result = (
                self.supabase.table("competencies")
                .select("competency_id")
                .in_("competency_id", competency_ids)
                .execute()
            )
            found_ids = {row["competency_id"] for row in (result.data or [])}
        except Exception as exc:
            raise TaskValidationError(
                [ValidationFailure(
                    field="criterias[*].competency_id",
                    actual_value=None,
                    constraint="could not reach Supabase to verify competency IDs",
                    environment=env,
                )],
                task_name,
            ) from exc

        missing = [cid for cid in competency_ids if cid not in found_ids]
        if missing:
            for cid in missing:
                failures.append(ValidationFailure(
                    field="criterias[?].competency_id",
                    actual_value=cid,
                    constraint="must exist in competencies table",
                    environment=env,
                ))
            raise TaskValidationError(failures, task_name)

        total_checks = len(self.MODEL.model_fields) + len(competency_ids)
        logger.info(f"Validation passed: {total_checks} checks on task '{task_name}'")
        return validated

    def insert(self, task_data: dict, env: str = "dev") -> dict:
        result = self.supabase.table("tasks").insert(task_data).execute()

        if not result.data or len(result.data) == 0:
            raise TaskDAOError("Failed to insert task into Supabase — no data returned")

        supabase_task = result.data[0]
        task_id = supabase_task.get("task_id") or supabase_task.get("id")

        criterias = task_data.get("criterias", [])
        failed_competency_ids: List[str] = []

        for criteria in criterias:
            competency_id = (
                criteria.get("competency_id")
                if isinstance(criteria, dict)
                else criteria.competency_id
            )
            if competency_id:
                try:
                    self.supabase.table("task_competencies").insert({
                        "task_id": task_id,
                        "competency_id": competency_id,
                    }).execute()
                except Exception as exc:
                    logger.error(
                        f"task_competencies insert failed for competency_id='{competency_id}': {exc}"
                    )
                    failed_competency_ids.append(competency_id)

        if failed_competency_ids:
            raise TaskWriteError(task_id, failed_competency_ids, env)

        return supabase_task

    def validate_and_insert(self, task_data: dict, env: str = "dev") -> dict:
        self.validate(task_data, env=env)
        return self.insert(task_data, env=env)


# ---------------------------------------------------------------------------
# PR Review variant
# ---------------------------------------------------------------------------
#
# PR review tasks share the ``tasks`` table but have a different blob shape:
#   - ``task_blob.task_type`` is fixed to ``"pr_review"``
#   - ``task_blob.short_overview`` and ``task_blob.outcomes`` are STRINGS
#     (the tech flow uses ``List[str]`` for both)
#   - ``task_blob.resources`` must contain both ``github_repo`` and
#     ``github_pr`` (the tech flow only requires ``github_repo``)
#   - ``task_blob.hints`` and ``task_blob.definitions`` may be empty
#   - top-level ``pre_requisites`` is a STRING (hardcoded in the flow)
#   - top-level ``answer`` may be empty (the answer key lives in
#     ``solutions``)
#   - ``solutions`` carries flaw-key fields instead of ``answer_repo``
#   - ``eval_info`` uses ``phase1`` / ``phase2`` rather than
#     ``task_eval`` / ``code_eval``

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


# ---------------------------------------------------------------------------
# Non-Tech variant
# ---------------------------------------------------------------------------
#
# Non-tech (AI/ML test-style) tasks also share the ``tasks`` table but:
#   - ``task_blob.task_overview`` replaces ``short_overview``
#   - ``task_blob.hints`` / ``task_blob.outcomes`` may be ``None``
#   - ``task_blob.definitions`` may be an empty dict
#   - top-level ``answer`` may be ``None`` (no canonical answer)
#   - top-level ``solutions`` and ``readme_content`` are ``None``
#     (no answer repo / no README)
#   - ``eval_info`` only carries ``task_eval`` (no ``code_eval``)
#   - ``task_id`` is pre-generated by the flow and included in the payload

class NonTechTaskBlob(BaseModel):
    model_config = {"strict": True}

    title: str
    definitions: Dict
    hints: Optional[str] = None
    resources: Dict
    outcomes: Optional[Union[str, List[str]]] = None
    question: str
    task_overview: List[str]

    @field_validator("title", "question")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must not be empty")
        return v

    @field_validator("task_overview")
    @classmethod
    def task_overview_strict_list(cls, v: List[str]) -> List[str]:
        if not isinstance(v, list):
            raise ValueError("must be a list of strings, not a string")
        if not v:
            raise ValueError("must not be an empty list")
        for item in v:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("every entry must be a non-empty string")
        return v


class NonTechTaskForDB(BaseModel):
    model_config = {"strict": True}

    task_id: Optional[str] = None
    created_at: str
    pre_requisites: List[str]
    answer: Optional[str] = None
    criterias: List[CriteriaEntry]
    is_deployed: bool
    task_blob: NonTechTaskBlob
    is_shared_infra_required: bool
    readme_content: Optional[Dict] = None
    eval_info: Dict
    solutions: Optional[Dict] = None

    @field_validator("created_at")
    @classmethod
    def created_at_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must not be empty")
        return v

    @field_validator("criterias")
    @classmethod
    def criterias_not_empty(cls, v: List[CriteriaEntry]) -> List[CriteriaEntry]:
        if not v:
            raise ValueError("must contain at least one entry")
        return v

    @field_validator("pre_requisites")
    @classmethod
    def pre_requisites_strict_list(cls, v: List[str]) -> List[str]:
        if not isinstance(v, list):
            raise ValueError("must be a list of strings, not a string")
        if not v:
            raise ValueError("must not be an empty list")
        for item in v:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("every entry must be a non-empty string")
        return v

    @field_validator("eval_info")
    @classmethod
    def eval_info_has_task_eval(cls, v: Dict) -> Dict:
        if "task_eval" not in v:
            raise ValueError("must contain 'task_eval' key")
        return v

    @field_validator("is_deployed")
    @classmethod
    def must_be_false_at_insert(cls, v: bool) -> bool:
        if v is not False:
            raise ValueError("must be False at insert time")
        return v

    @model_validator(mode="after")
    def no_duplicate_competency_ids(self) -> "NonTechTaskForDB":
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


class NonTechTaskDAO(BaseTaskDAO):
    """DAO for non-tech (AI/ML test-style) tasks. Inherits FK check + insert from BaseTaskDAO."""

    MODEL: ClassVar[Type[BaseModel]] = NonTechTaskForDB
