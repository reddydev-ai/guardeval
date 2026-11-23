"""Pure guard tests: never allow fabricated or misattributed live evidence."""
from copy import deepcopy

import pytest

from app.live import verify_evidence, _service_url
from app.live_fixtures import RAG_CASES, SOURCE_FILENAME


def example():
    case = RAG_CASES[0]
    return {
        "evidence_origin": "same-invocation-retrieval",
        "generation_mode": "extractive-demo",
        "answer": {
            "answer": f"Mistral policy says the ceiling is 42 CAD. [{SOURCE_FILENAME} p.1]",
            "citations": [{"source": SOURCE_FILENAME, "page": 1}],
        },
        "retrieved_contexts": [
            {"source": SOURCE_FILENAME, "page": 1, "text": "Mistral reimburses 42 CAD per day", "score": 0.1}
        ],
    }, case


def test_valid_same_invocation_evidence():
    body, case = example()
    out = verify_evidence(body, case, require_llm=False)
    assert out["reference_in_retrieval"]
    assert out["citations_verified"]


@pytest.mark.parametrize("alter", [
    lambda b: b.update(evidence_origin="reference-dataset"),
    lambda b: b.update(retrieved_contexts=[]),
    lambda b: b["retrieved_contexts"][0].update(text="No meal reimbursement"),
    lambda b: b["retrieved_contexts"][0].update(page=2),
    lambda b: b["answer"].update(citations=[]),
    lambda b: b["answer"].update(answer="42 days instead"),
])
def test_forged_or_unproven_response_fails(alter):
    body, case = example()
    alter(body)
    with pytest.raises(AssertionError):
        verify_evidence(body, case, require_llm=False)


def test_demo_response_cannot_be_used_as_llm_validation():
    body, case = example()
    with pytest.raises(AssertionError, match="cannot use extractive"):
        verify_evidence(body, case, require_llm=True)


@pytest.mark.parametrize("unsafe", [
    "http://example.com:8000",
    "http://127.0.0.1.evil.com:8000",
    "https://example.com:8443?token=secret",
    "https://user:password@example.com",
])
def test_service_endpoints_are_local_by_default(monkeypatch, unsafe):
    monkeypatch.setenv("POLICYMIND_URL", unsafe)
    monkeypatch.delenv("ALLOW_REMOTE_EVAL", raising=False)
    with pytest.raises(RuntimeError):
        _service_url("POLICYMIND_URL")


def test_pdf_line_wrapping_does_not_hide_correct_evidence():
    body, case = example()
    body["retrieved_contexts"][0]["text"] = "Mistral reimburses 42\nCAD per day"
    body["answer"]["answer"] = f"Reimbursement: 42\nCAD. [{SOURCE_FILENAME} p.1]"
    out = verify_evidence(body, case, require_llm=False)
    assert out["reference_in_answer"]


def test_inline_citation_is_required_even_with_correct_metadata():
    body, case = example()
    body["answer"]["answer"] = "The reimbursement ceiling is 42 CAD."
    with pytest.raises(AssertionError, match="inline"):
        verify_evidence(body, case, require_llm=False)


def test_llm_output_cannot_pass_no_key_smoke_mode():
    body, case = example()
    body["generation_mode"] = "llm"
    with pytest.raises(AssertionError, match="Smoke mode"):
        verify_evidence(body, case, require_llm=False)


def test_remote_https_requires_explicit_hostname_allowlist(monkeypatch):
    monkeypatch.setenv("POLICYMIND_URL", "https://evaluation.example.com")
    monkeypatch.setenv("ALLOW_REMOTE_EVAL", "true")
    monkeypatch.delenv("EVAL_ALLOWED_HOSTS", raising=False)
    with pytest.raises(RuntimeError, match="allowlist"):
        _service_url("POLICYMIND_URL")
    monkeypatch.setenv("EVAL_ALLOWED_HOSTS", "other.example.com,evaluation.example.com")
    assert _service_url("POLICYMIND_URL") == "https://evaluation.example.com"


def test_remote_evaluation_rejects_http_even_when_allowlisted(monkeypatch):
    monkeypatch.setenv("POLICYMIND_URL", "http://evaluation.example.com")
    monkeypatch.setenv("ALLOW_REMOTE_EVAL", "true")
    monkeypatch.setenv("EVAL_ALLOWED_HOSTS", "evaluation.example.com")
    with pytest.raises(RuntimeError, match="HTTPS"):
        _service_url("POLICYMIND_URL")
