"""classify_task_runtime — thin wrapper, no cache."""
from unittest.mock import patch

import pytest

from infra.classifier.classifier import classify_task_runtime, to_competencies
from infra.classifier.llm_classifier import ClassifierResult
from infra.classifier.runtime import Competency, TaskRuntime


def test_classify_calls_llm_and_returns_runtime():
    runtime = TaskRuntime(runtime="python", datastores=["postgres"], kind="script")
    result = ClassifierResult(runtime=runtime, confidence=0.95)
    comps = [Competency(name="Python", proficiency="BASIC"),
             Competency(name="SQL", proficiency="BASIC")]

    with patch("prompt_generator.classifier.classify_with_llm",
               return_value=result) as llm_mock:
        out = classify_task_runtime(comps)

    assert out == runtime
    llm_mock.assert_called_once_with(comps, client=None)


def test_classify_passes_llm_client_through():
    runtime = TaskRuntime(runtime="flutter", kind="mobile")
    result = ClassifierResult(runtime=runtime, confidence=0.9)
    comps = [Competency(name="Flutter", proficiency="INTERMEDIATE")]
    sentinel = object()

    with patch("prompt_generator.classifier.classify_with_llm",
               return_value=result) as llm_mock:
        classify_task_runtime(comps, llm_client=sentinel)  # type: ignore[arg-type]

    llm_mock.assert_called_once_with(comps, client=sentinel)


def test_empty_competencies_raises():
    with pytest.raises(ValueError):
        classify_task_runtime([])


def test_to_competencies_converts_dicts():
    items = [
        {"name": "Python", "proficiency": "INTERMEDIATE"},
        {"name": "SQL"},  # proficiency omitted → defaults to BASIC
    ]
    comps = to_competencies(items)
    assert comps == [
        Competency(name="Python", proficiency="INTERMEDIATE"),
        Competency(name="SQL", proficiency="BASIC"),
    ]
