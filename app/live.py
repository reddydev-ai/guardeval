"""Fail-closed, real-service GuardEval runner.

Never substitutes gold contexts for retrieved evidence. The built-in CI mode
exercises real APIs on a *synthetic* corpus without an LLM, so it is a service
integration gate, NOT a model-quality or production-safety certification.

An opt-in LLM quality mode requires real generation plus RAGAS and DeepEval;
missing credentials, unavailable engines and failed thresholds are hard failures.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import httpx

from .live_fixtures import FLOW_CASES, RAG_CASES, SOURCE_FILENAME


def _service_url(name: str) -> str:
    value = os.environ.get(name, "").strip().rstrip("/")
    u = urlsplit(value)
    if not u.scheme or not u.hostname or u.username or u.password or u.query or u.fragment:
        raise RuntimeError(f"{name} must be a valid service base URL without credentials or query")
    local = u.hostname in {"127.0.0.1", "localhost"}
    if not ((local and u.scheme == "http") or (u.scheme == "https" and os.getenv("ALLOW_REMOTE_EVAL") == "true")):
        raise RuntimeError(f"{name} must be local HTTP, or an explicitly permitted HTTPS endpoint")
    return value


def _secret(name: str) -> str:
    value = os.getenv(name, "")
    if not value:
        raise RuntimeError(f"Missing {name}; refusing anonymous evaluation")
    return value


def verify_evidence(body: dict, case: dict, *, require_llm: bool) -> dict:
    """Pure validator; negative/forged outcomes are tested separately."""
    if body.get("evidence_origin") != "same-invocation-retrieval":
        raise AssertionError("Evidence is not tied to the answer invocation")
    mode = body.get("generation_mode")
    if mode not in {"llm", "extractive-demo"}:
        raise AssertionError("Unverifiable generation mode")
    if require_llm and mode != "llm":
        raise AssertionError("LLM quality run cannot use extractive demo responses")
    if not require_llm and mode != "extractive-demo":
        raise AssertionError("Smoke mode requires extractive-demo responses; an LLM run must be explicitly selected")

    answer = body.get("answer")
    if not isinstance(answer, dict) or not isinstance(answer.get("answer"), str):
        raise AssertionError("Missing live answer")
    contexts = body.get("retrieved_contexts")
    if not isinstance(contexts, list) or not contexts:
        raise AssertionError("No live retrieved contexts")
    for item in contexts:
        if not isinstance(item, dict) or not isinstance(item.get("text"), str):
            raise AssertionError("Malformed retrieved context")
        if not isinstance(item.get("source"), str) or not isinstance(item.get("page"), int):
            raise AssertionError("Context provenance missing")

    top = contexts[0]
    if top["source"] != SOURCE_FILENAME or top["page"] != case["page"]:
        raise AssertionError(f"Unexpected top retrieved context for case {case['id']}")
    normalize = lambda text: re.sub(r"\s+", " ", text).strip().casefold()
    if normalize(case["reference"]) not in normalize(top["text"]):
        raise AssertionError(f"Reference is absent from retrieved evidence for {case['id']}")

    citations = answer.get("citations")
    if not isinstance(citations, list) or not any(
        isinstance(c, dict) and c.get("source") == SOURCE_FILENAME
        and c.get("page") == case["page"] for c in citations
    ):
        raise AssertionError(f"Answer has no matching source/page citation: {case['id']}")

    # Lightweight exact-answer assertion for synthetic corpus. Judge-based
    # quality scoring is independently required in LLM quality mode.
    response_text = answer["answer"]
    if f"[{SOURCE_FILENAME} p.{case['page']}]" not in response_text:
        raise AssertionError(f"Answer is missing the expected inline source citation: {case['id']}")
    exact_answer = normalize(case["reference"]) in normalize(response_text)
    if not exact_answer and not require_llm:
        raise AssertionError(f"Extractive demo did not return expected reference: {case['id']}")

    return {
        "case_id": case["id"],
        "retrieved_top_page": top["page"],
        "citations_verified": True,
        "reference_in_retrieval": True,
        "reference_in_answer": exact_answer,
        "generation_mode": mode,
        "response": response_text,
        "contexts": [c["text"] for c in contexts],
        "reference": case["reference"],
        "question": case["question"],
    }


def _request(client: httpx.Client, method: str, url: str, **kwargs) -> dict:
    response = client.request(method, url, **kwargs)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise AssertionError("Service did not return a JSON object")
    return payload


def run_live() -> dict:
    policy_url = _service_url("POLICYMIND_URL")
    flow_url = _service_url("FLOWAGENT_URL")
    policy_key = _secret("POLICYMIND_API_KEY")
    eval_key = _secret("POLICYMIND_EVAL_KEY")
    flow_key = _secret("FLOWAGENT_API_KEY")
    reviewer_key = _secret("FLOWAGENT_REVIEWER_KEY")
    if policy_key == eval_key or flow_key == reviewer_key:
        raise RuntimeError("Business and evaluation/reviewer credentials must be independent")

    mode_setting = os.getenv("EVAL_REQUIRE_LLM", "false").strip().lower()
    if mode_setting not in {"true", "false"}:
        raise RuntimeError("EVAL_REQUIRE_LLM must be exactly true or false")
    require_llm = mode_setting == "true"
    if require_llm and not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("LLM quality gate requires a judge model API key")

    policy_headers = {"X-API-Key": policy_key, "X-Eval-Key": eval_key}
    flow_headers = {"X-API-Key": flow_key}
    approval_headers = {**flow_headers, "X-Reviewer-Key": reviewer_key}

    with httpx.Client(timeout=180, follow_redirects=False, trust_env=False) as client:
        for base in [policy_url, flow_url]:
            health = _request(client, "GET", base + "/health")
            if health.get("status") != "ok":
                raise AssertionError("Service health check failed")

        # Verify authorization, not merely that credentials happen to work.
        bad = client.post(policy_url + "/evaluation/ask", json={"question": RAG_CASES[0]["question"]},
                          headers={"X-API-Key": policy_key, "X-Eval-Key": "bad-evaluation-secret"})
        if bad.status_code != 403:
            raise AssertionError("Evidence endpoint accepted wrong evaluation key")

        rag_results = []
        for case in RAG_CASES:
            body = _request(
                client, "POST", policy_url + "/evaluation/ask",
                headers=policy_headers, json={"question": case["question"]},
            )
            rag_results.append(verify_evidence(body, case, require_llm=require_llm))

        flow_results = []
        for case in FLOW_CASES:
            started = _request(client, "POST", flow_url + "/verify", headers=flow_headers,
                               json={"vendor_name": case["vendor_name"], "submitted_docs": case["submitted_docs"]})
            if started.get("status") != "awaiting_approval" or not started.get("thread_id"):
                raise AssertionError("FlowAgent did not pause for approval")
            if started.get("approval_request", {}).get("risk_level") != case["expected_risk"]:
                raise AssertionError(f"Incorrect pre-approval risk: {case['id']}")
            finished = _request(
                client, "POST", flow_url + "/verify/resume", headers=approval_headers,
                json={"thread_id": started["thread_id"], "decision": case["decision"], "comment": "synthetic evaluation"},
            )
            if finished.get("status") != "done" or finished.get("decision") != case["decision"]:
                raise AssertionError(f"Reviewer decision was not preserved: {case['id']}")
            if finished.get("risk_level") != case["expected_risk"] or not finished.get("memo"):
                raise AssertionError(f"Incorrect final risk or missing memo: {case['id']}")
            flow_results.append({"case_id": case["id"], "risk_matches": True, "approval_preserved": True})

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "live-model-quality" if require_llm else "live-service-smoke",
        "validation_level": "synthetic-corpus-independent-live-retrieval",
        "rag": {
            "n_cases": len(rag_results),
            "top1_retrieval_hit_rate": sum(x["reference_in_retrieval"] for x in rag_results) / len(rag_results),
            "citation_match_rate": sum(x["citations_verified"] for x in rag_results) / len(rag_results),
            "literal_answer_hit_rate": sum(x["reference_in_answer"] for x in rag_results) / len(rag_results),
            "generation_modes": sorted({x["generation_mode"] for x in rag_results}),
            "case_ids": [x["case_id"] for x in rag_results],
        },
        "agent": {
            "n_cases": len(flow_results),
            "risk_accuracy": sum(x["risk_matches"] for x in flow_results) / len(flow_results),
            "approval_integrity": sum(x["approval_preserved"] for x in flow_results) / len(flow_results),
            "case_ids": [x["case_id"] for x in flow_results],
        },
        "release_quality_certified": False,
    }
    if require_llm:
        # Never accept a heuristic or silent library fallback in model-quality
        # mode. Require engines that actually evaluated live model outputs.
        from .evaluators import run_ragas, run_deepeval_hallucination
        from .quality_gate import validate_quality_scores
        rag_samples = [{
            "question": r["question"],
            "response": r["response"],
            "retrieved_contexts": r["contexts"],
            "ground_truth": r["reference"],
        } for r in rag_results]
        scores = run_ragas(rag_samples)
        hallucination = run_deepeval_hallucination([{
            "question": r["question"], "response": r["response"], "contexts": r["contexts"]
        } for r in rag_results])
        # Reject misleading fallback engines, missing cases, invalid scores,
        # and anything below the configured model-quality thresholds.
        validate_quality_scores(scores, hallucination, len(rag_results))
        report["rag"]["ragas"] = scores
        report["rag"]["deepeval"] = hallucination
        report["validation_level"] = "synthetic-corpus-live-llm-and-judge"
        # A tiny synthetic corpus is NOT proof of production readiness.
        report["release_quality_certified"] = False

    output = Path(os.getenv("LIVE_EVAL_REPORT", "live-evaluation-report.json"))
    output.parent.mkdir(parents=True, exist_ok=True)
    # Intentional: do not write raw snippets, answers, API keys or full prompts.
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(run_live(), indent=2))
