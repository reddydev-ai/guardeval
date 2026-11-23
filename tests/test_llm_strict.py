"""No model-quality score may be fabricated or silently downgraded.

The actual paid model run is deliberately NOT made by these unit tests.
"""
from types import SimpleNamespace
import builtins

import pytest

from app import evaluators


SAMPLE = [{
    "question": "What is the policy?",
    "response": "The permitted amount is 42 CAD.",
    "retrieved_contexts": ["Policy: 42 CAD per day."],
    "ground_truth": "42 CAD",
}]


def test_empty_model_evaluation_fails_closed():
    with pytest.raises(ValueError, match="empty"):
        evaluators.run_ragas_strict([])


def test_missing_judge_key_does_not_create_model_quality_score(monkeypatch):
    monkeypatch.setattr(evaluators, "settings", SimpleNamespace(openai_api_key=""))
    with pytest.raises(RuntimeError, match="authorized judge API key"):
        evaluators.run_ragas_strict(SAMPLE)


def test_missing_ragas_dependency_is_a_hard_error_not_heuristic(monkeypatch):
    monkeypatch.setattr(evaluators, "settings", SimpleNamespace(openai_api_key="synthetic-test-key"))
    original = builtins.__import__

    def deny_ragas(name, *args, **kwargs):
        if name == "ragas" or name.startswith("ragas."):
            raise ImportError("simulated RAGAS unavailability")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", deny_ragas)
    with pytest.raises(RuntimeError, match="Real RAGAS evaluation failed"):
        evaluators.run_ragas_strict(SAMPLE)


def test_strict_path_rejects_non_ragas_engine(monkeypatch):
    monkeypatch.setattr(
        evaluators, "_ragas_metrics",
        lambda samples, strict: {"engine": "offline-heuristic", "faithfulness": 1.0},
    )
    with pytest.raises(RuntimeError, match="did not return verified RAGAS"):
        evaluators.run_ragas_strict(SAMPLE)


def test_strict_path_accepts_real_engine_label_but_does_not_certify_it(monkeypatch):
    fake = {"engine": "ragas", "n": 1, "faithfulness": 0.9}
    monkeypatch.setattr(evaluators, "_ragas_metrics", lambda samples, strict: fake)
    assert evaluators.run_ragas_strict(SAMPLE) == fake
    # The full live gate independently validates coverage, all score fields
    # and thresholds. These tests do not prove any model made an API call.


def test_strict_path_refuses_missing_result(monkeypatch):
    monkeypatch.setattr(evaluators, "_ragas_metrics", lambda samples, strict: None)
    with pytest.raises(RuntimeError, match="did not return"):
        evaluators.run_ragas_strict(SAMPLE)
