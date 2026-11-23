"""Regression tests. These are the quality gates: run in CI to block a deploy when
PolicyMind or FlowAgent quality drops below threshold.

    pytest -v

In OFFLINE mode these pass by construction (gold-derived outputs); the real value
is when POLICYMIND_URL / FLOWAGENT_URL point at live services and the thresholds
catch genuine regressions.
"""
from __future__ import annotations
import pytest

from app.config import get_settings
from app.runner import run_all

settings = get_settings()


@pytest.fixture(scope="module")
def report():
    return run_all()


def test_faithfulness_above_threshold(report):
    if report["mode"] != "live":
        pytest.skip("Offline simulated data is not a release-quality faithfulness gate.")
    score = report["policymind"]["ragas"].get("faithfulness")
    assert score is not None, "faithfulness not computed"
    assert score >= settings.min_faithfulness, (
        f"faithfulness {score:.3f} < {settings.min_faithfulness}"
    )


def test_hallucination_below_threshold(report):
    if report["mode"] != "live":
        pytest.skip("Offline simulated data is not a release-quality hallucination gate.")
    score = report["policymind"]["hallucination"].get("hallucination")
    if score is None:
        pytest.skip("hallucination not computed (DeepEval unavailable)")
    assert score <= settings.max_hallucination, (
        f"hallucination {score:.3f} > {settings.max_hallucination}"
    )


def test_task_completion_above_threshold(report):
    if report["mode"] != "live":
        pytest.skip("Offline simulated data is not a release-quality completion gate.")
    score = report["flowagent"]["task_completion"]["task_completion"]
    assert score >= settings.min_task_completion, (
        f"task completion {score:.3f} < {settings.min_task_completion}"
    )


def test_flowagent_risk_matches_expected(report):
    if report["mode"] != "live":
        pytest.skip("Offline simulated data is not a release-quality risk gate.")
    """Every FlowAgent scenario should produce the expected risk level."""
    mismatches = [
        r for r in report["flowagent"]["results"] if r["actual_risk"] != r["expected_risk"]
    ]
    assert not mismatches, f"risk mismatches: {[(m['vendor_name'], m['actual_risk']) for m in mismatches]}"


def test_offline_smoke_is_clearly_identified(report):
    if report["mode"] == "offline":
        assert report["validation_level"] == "synthetic-smoke-only"
        assert report["policymind"]["n_cases"] == 20
        assert report["flowagent"]["n_cases"] == 10
