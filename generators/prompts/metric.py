"""
Quality metric for DSPy compilation (MIPROv2).

Given a (gold_prompt, generated_prompt) pair, produces a [0.0, 1.0] score
that MIPROv2 maximizes. The metric blends multiple signals:

  - Structural validity (parse, registry key, format vars) — pass/fail gate
  - Section coverage — does the generated prompt have the same major sections?
  - Code-files coverage — are the same starter files specified?
  - Length similarity — within a reasonable ballpark of the gold

Hard structural failures yield a score of 0.
"""

from __future__ import annotations

import re
from typing import Optional

from infra.classifier.classifier import Competency
from generators.prompts.validator import validate_prompt_file


def _extract_headers(source: str) -> set[str]:
    """Extract markdown-style headers from the source."""
    headers = set()
    for match in re.finditer(r"^#+\s+([A-Za-z].+)$", source, re.MULTILINE):
        headers.add(match.group(1).strip().lower())
    return headers


def _extract_code_files(source: str) -> set[str]:
    """Extract code_file names mentioned in the source's REQUIRED OUTPUT block."""
    files = set()
    for match in re.finditer(
        r'"([a-zA-Z0-9_./-]+\.(?:py|sh|sql|yml|md|txt|js|json|jsx|tsx|ts|gitignore))"\s*:',
        source,
    ):
        files.add(match.group(1).lower())
    return files


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _length_similarity(a_len: int, b_len: int) -> float:
    if a_len == 0 and b_len == 0:
        return 1.0
    if a_len == 0 or b_len == 0:
        return 0.0
    ratio = min(a_len, b_len) / max(a_len, b_len)
    return ratio


def quality_metric(
    example,
    prediction,
    trace=None,
) -> float:
    """DSPy-compatible metric.

    Args:
        example: dspy.Example with `competencies`, `proficiency`, `new_prompt_file` (gold)
        prediction: dspy.Prediction with `new_prompt_file` (predicted)
        trace: unused

    Returns:
        Score in [0.0, 1.0].
    """
    gold = getattr(example, "new_prompt_file", "") or ""
    pred = getattr(prediction, "new_prompt_file", "") or ""
    competencies = getattr(example, "competencies", "")
    proficiency = getattr(example, "proficiency", "BASIC")

    if not pred or not gold:
        return 0.0

    # Strip code fences if present
    pred = pred.strip()
    if pred.startswith("```"):
        lines = pred.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        pred = "\n".join(lines)

    # Parse competencies string back into list of dicts for the validator
    comp_dicts = []
    for part in competencies.split(","):
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^(.*?)\s*\((\w+)\)$", part)
        if m:
            comp_dicts.append({"name": m.group(1).strip(), "proficiency": m.group(2)})
        else:
            comp_dicts.append({"name": part, "proficiency": proficiency})

    # 1. Hard structural validity — fail with 0 if invalid
    val = validate_prompt_file(pred, comp_dicts, proficiency)
    if not val.passed:
        return 0.0

    # 2. Section coverage (Jaccard similarity over headers)
    gold_headers = _extract_headers(gold)
    pred_headers = _extract_headers(pred)
    section_score = _jaccard(gold_headers, pred_headers)

    # 3. Code files coverage
    gold_files = _extract_code_files(gold)
    pred_files = _extract_code_files(pred)
    files_score = _jaccard(gold_files, pred_files)

    # 4. Length similarity (within order of magnitude)
    length_score = _length_similarity(len(gold), len(pred))

    # Weighted combination — files coverage matters most, then sections, then length.
    weights = {
        "structural": 0.30,    # Already gated above; keep as a base score
        "files": 0.30,
        "sections": 0.25,
        "length": 0.15,
    }
    total = (
        weights["structural"] * 1.0
        + weights["files"] * files_score
        + weights["sections"] * section_score
        + weights["length"] * length_score
    )
    return round(total, 4)


def metric_summary(example, prediction, trace=None) -> dict:
    """Verbose version of the metric — useful for debugging compilation."""
    gold = getattr(example, "new_prompt_file", "") or ""
    pred = getattr(prediction, "new_prompt_file", "") or ""

    return {
        "score": quality_metric(example, prediction, trace),
        "gold_chars": len(gold),
        "pred_chars": len(pred),
        "gold_headers": len(_extract_headers(gold)),
        "pred_headers": len(_extract_headers(pred)),
        "gold_files": len(_extract_code_files(gold)),
        "pred_files": len(_extract_code_files(pred)),
    }
