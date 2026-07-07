"""``to_competencies`` — dict→Competency conversion helper."""
from infra.classifier.classifier import to_competencies
from infra.classifier.runtime import Competency


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
