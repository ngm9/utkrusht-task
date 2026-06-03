"""Task validation package.

Public API kept stable for existing call sites — ``from task_validation
import BaseTaskDAO, TaskValidationError`` continues to work after the
package split.

Internally the symbols live in four focused modules:

- ``task_validation.exceptions`` — ValidationFailure + exception hierarchy
- ``task_validation.base``        — CriteriaEntry + TaskBlob + TaskForDB +
                                    BaseTaskDAO (coding pipeline)
- ``task_validation.pr_review``   — PR review variant
- ``task_validation.non_tech``    — non-tech variant
"""
from task_validation.exceptions import (
    TaskDAOError,
    TaskValidationError,
    TaskWriteError,
    ValidationFailure,
)
from task_validation.base import (
    BaseTaskDAO,
    CriteriaEntry,
    TaskBlob,
    TaskForDB,
)
from task_validation.pr_review import (
    PRReviewTaskBlob,
    PRReviewTaskDAO,
    PRReviewTaskForDB,
)
from task_validation.non_tech import (
    NonTechTaskBlob,
    NonTechTaskDAO,
    NonTechTaskForDB,
)

__all__ = [
    # exceptions
    "TaskDAOError",
    "TaskValidationError",
    "TaskWriteError",
    "ValidationFailure",
    # coding pipeline
    "BaseTaskDAO",
    "CriteriaEntry",
    "TaskBlob",
    "TaskForDB",
    # PR review variant
    "PRReviewTaskBlob",
    "PRReviewTaskDAO",
    "PRReviewTaskForDB",
    # non-tech variant
    "NonTechTaskBlob",
    "NonTechTaskDAO",
    "NonTechTaskForDB",
]
