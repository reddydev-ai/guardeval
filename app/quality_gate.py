"""Strict validation of optional live-LLM quality metrics.

A passing score is permitted only when every case has been evaluated by the
expected engine, every score is finite and in range, and each configured
threshold is satisfied. This module does not make production-release claims.
"""
from __future__ import annotations

import math
from collections.abc import Mapping

from .config import get_settings

RAG_THRESHOLDS = (
    ("faithfulness", "min_faithfulness", True),
    ("answer_relevancy", "min_answer_relevancy", True),
    ("context_precision", "min_context_precision", True),
)
HALLUCINATION_THRESHOLD = ("hallucination", "max_hallucination", False)


def _validated_unit(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise AssertionError(f"{name} must be a numeric metric")
    number = float(value)
    if not math.isfinite(number) or not (0.0 <= number <= 1.0):
        raise AssertionError(f"{name} must be finite and within [0, 1]")
    return number


def validate_quality_scores(
    ragas: Mapping[str, object], deepeval: Mapping[str, object], expected_cases: int,
    thresholds: object | None = None,
) -> dict:
    """Require complete RAGAS + DeepEval coverage and fail on any noncompliance."""
    if expected_cases < 1:
        raise AssertionError("No evaluated cases")
    if ragas.get("engine") != "ragas" or deepeval.get("engine") != "deepeval":
        raise AssertionError("Actual RAGAS and DeepEval engines are required; no fallback")
    for source in (ragas, deepeval):
        n = source.get("n")
        if isinstance(n, bool) or not isinstance(n, int) or n != expected_cases:
            raise AssertionError("Evaluation engine has incomplete or invalid case coverage")

    config = thresholds if thresholds is not None else get_settings()
    checked = {}
    for metric, config_name, higher_is_better in (*RAG_THRESHOLDS, HALLUCINATION_THRESHOLD):
        value = _validated_unit(
            ragas.get(metric) if metric != "hallucination" else deepeval.get(metric),
            metric,
        )
        threshold = _validated_unit(getattr(config, config_name), config_name)
        failed = value < threshold if higher_is_better else value > threshold
        if failed:
            raise AssertionError(f"{metric} failed its configured threshold")
        checked[metric] = value

    return {
        "ragas": dict(ragas),
        "deepeval": dict(deepeval),
        "n_cases": expected_cases,
        "validated_metric_keys": sorted(checked),
    }
