"""Runner: turns datasets into model outputs, then scores them.

Two modes:
  - LIVE: if POLICYMIND_URL / FLOWAGENT_URL are set, it calls the real APIs.
  - OFFLINE: otherwise it synthesises plausible outputs from the gold data so the
    full harness + dashboard run end-to-end without the other services up.
    OFFLINE results are clearly flagged so nobody mistakes them for a live eval.

Results are written to results.json for the dashboard and the regression tests.
"""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone

import httpx

from .config import get_settings
from .datasets import POLICYMIND_CASES, FLOWAGENT_CASES
from .evaluators import (
    run_ragas,
    run_deepeval_hallucination,
    run_deepeval_task_completion,
)

settings = get_settings()
RESULTS_PATH = os.getenv("RESULTS_PATH", "results.json")


# ----------------------------- output collection ---------------------------- #
def _policymind_outputs() -> list[dict]:
    samples = []
    for case in POLICYMIND_CASES:
        if settings.policymind_url:
            resp = httpx.post(
                f"{settings.policymind_url.rstrip('/')}/ask",
                json={"question": case["question"]},
                timeout=60,
            ).json()
            answer = resp.get("answer", "")
            contexts = case["contexts"]  # reference contexts only; NOT actual retrieval
        else:
            # OFFLINE: simulate a faithful answer from the gold context.
            answer = case["ground_truth"]
            contexts = case["contexts"]
        samples.append(
            {
                "question": case["question"],
                "response": answer,
                "retrieved_contexts": contexts or ["(no context)"],
                "ground_truth": case["ground_truth"],
                "contexts": contexts,
            }
        )
    return samples


def _flowagent_outputs() -> list[dict]:
    results = []
    for case in FLOWAGENT_CASES:
        if settings.flowagent_url:
            base = settings.flowagent_url.rstrip("/")
            started = httpx.post(
                f"{base}/verify",
                json={"vendor_name": case["vendor_name"], "submitted_docs": case["submitted_docs"]},
                timeout=120,
            ).json()
            thread_id = started.get("thread_id")
            actual_risk = started.get("approval_request", {}).get("risk_level")
            done = httpx.post(
                f"{base}/verify/resume",
                json={"thread_id": thread_id, "decision": "approve", "comment": "eval run"},
                timeout=120,
            ).json()
            memo = done.get("memo", "")
            actual_risk = done.get("risk_level", actual_risk)
        else:
            # OFFLINE: simulate the deterministic document rule.
            required = {"Certificate of Insurance", "WSIB Clearance", "GST/HST Registration", "Signed MSA"}
            missing = required - set(case["submitted_docs"])
            actual_risk = "green" if not missing else ("yellow" if len(missing) == 1 else "red")
            memo = f"Vendor {case['vendor_name']} assessed as {actual_risk}. Missing: {sorted(missing) or 'none'}."
        results.append(
            {
                "vendor_name": case["vendor_name"],
                "task": case["task"],
                "expected_risk": case["expected_risk"],
                "actual_risk": actual_risk,
                "memo": memo,
            }
        )
    return results


# --------------------------------- run -------------------------------------- #
from .tracing import setup_tracing, tracing_active

def run_all() -> dict:
    run_id = setup_tracing()
    mode = "live" if (settings.policymind_url and settings.flowagent_url) else "offline"
    if bool(settings.policymind_url) != bool(settings.flowagent_url):
        raise RuntimeError("Live evaluation requires BOTH POLICYMIND_URL and FLOWAGENT_URL; mixed simulated/live scores are prohibited.")
    if mode == "live":
        raise RuntimeError("Live release gating is disabled: PolicyMind does not expose actual retrieved contexts to this evaluator. Do not score gold contexts as live retrieval.")

    pm_samples = _policymind_outputs()
    fa_results = _flowagent_outputs()

    ragas_scores = run_ragas(pm_samples)
    hallucination = run_deepeval_hallucination(
        [{"question": s["question"], "response": s["response"], "contexts": s["contexts"]} for s in pm_samples]
    )
    task_completion = run_deepeval_task_completion(fa_results)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "validation_level": "synthetic-smoke-only" if mode == "offline" else "live-unverified",
        "langsmith_run_id": run_id,
        "langsmith_active": tracing_active(),
        "policymind": {
            "ragas": ragas_scores,
            "hallucination": hallucination,
            "n_cases": len(pm_samples),
        },
        "flowagent": {
            "task_completion": task_completion,
            "results": fa_results,
            "n_cases": len(fa_results),
        },
        "thresholds": {
            "min_faithfulness": settings.min_faithfulness,
            "min_answer_relevancy": settings.min_answer_relevancy,
            "min_context_precision": settings.min_context_precision,
            "max_hallucination": settings.max_hallucination,
            "min_task_completion": settings.min_task_completion,
        },
    }

    with open(RESULTS_PATH, "w") as f:
        json.dump(report, f, indent=2)
    return report


if __name__ == "__main__":
    out = run_all()
    print(json.dumps(out, indent=2))
