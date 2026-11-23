"""Guardrails for model-quality metrics; all tests are offline and deterministic."""
from copy import deepcopy
from types import SimpleNamespace

import pytest

from app.quality_gate import validate_quality_scores

CONFIG = SimpleNamespace(
    min_faithfulness=0.70,
    min_answer_relevancy=0.70,
    min_context_precision=0.60,
    max_hallucination=0.30,
)
RAGAS = {
    "engine": "ragas",
    "faithfulness": 0.85,
    "answer_relevancy": 0.82,
    "context_precision": 0.75,
    "n": 6,
}
DEEPEVAL = {"engine": "deepeval", "hallucination": 0.10, "n": 6}


def check(ragas=None, deepeval=None, cases=6):
    return validate_quality_scores(
        deepcopy(RAGAS) if ragas is None else ragas,
        deepcopy(DEEPEVAL) if deepeval is None else deepeval,
        cases,
        CONFIG,
    )


def test_actual_engines_with_complete_finite_metrics_can_pass():
    result = check()
    assert result["n_cases"] == 6
    assert set(result["validated_metric_keys"]) == {
        "faithfulness", "answer_relevancy", "context_precision", "hallucination"
    }


@pytest.mark.parametrize("engine", ["offline-heuristic", "llm-judge", "synthetic"])
def test_unverified_ragas_engine_is_rejected(engine):
    data = {**RAGAS, "engine": engine}
    with pytest.raises(AssertionError, match="engines"):
        check(ragas=data)


def test_unverified_deepeval_engine_is_rejected():
    with pytest.raises(AssertionError, match="engines"):
        check(deepeval={**DEEPEVAL, "engine": "offline-heuristic"})


@pytest.mark.parametrize("n", [None, 0, 5, 7, 6.0, True, "6"])
def test_incomplete_or_ambiguous_case_coverage_is_rejected(n):
    with pytest.raises(AssertionError, match="coverage"):
        check(ragas={**RAGAS, "n": n})


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -0.01, 1.01, None, True, "0.9"])
def test_invalid_faithfulness_cannot_pass(bad):
    with pytest.raises(AssertionError, match="faithfulness"):
        check(ragas={**RAGAS, "faithfulness": bad})


@pytest.mark.parametrize("metric,value", [
    ("faithfulness", 0.69),
    ("answer_relevancy", 0.69),
    ("context_precision", 0.59),
])
def test_below_threshold_rag_metrics_are_rejected(metric, value):
    with pytest.raises(AssertionError, match="failed"):
        check(ragas={**RAGAS, metric: value})


@pytest.mark.parametrize("bad", [float("nan"), float("-inf"), -0.1, 1.1, 0.31])
def test_invalid_or_excessive_hallucination_is_rejected(bad):
    with pytest.raises(AssertionError):
        check(deepeval={**DEEPEVAL, "hallucination": bad})


def test_empty_sample_is_not_allowed():
    with pytest.raises(AssertionError, match="No evaluated cases"):
        check(cases=0)


def test_configured_stricter_threshold_is_respected():
    strict = SimpleNamespace(**{**CONFIG.__dict__, "min_faithfulness": 0.95})
    with pytest.raises(AssertionError, match="failed"):
        validate_quality_scores(RAGAS, DEEPEVAL, 6, strict)
