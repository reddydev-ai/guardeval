"""Ensure draft evaluation cases cannot be mistaken for a certified benchmark."""
import json
import re
from collections import Counter
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "evaluation" / "catalogue_v1.jsonl"

def test_catalogue_has_30_unique_unreviewed_cases():
    rows = [json.loads(line) for line in PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) == 30
    ids = [row["id"] for row in rows]
    assert len(ids) == len(set(ids))
    assert all(re.fullmatch(r"[a-z0-9-]+", value) for value in ids)
    assert all(row.get("review_status") == "draft_unreviewed" for row in rows)
    assert all(row.get("approved_for_scoring") is False for row in rows)
    assert all(isinstance(row["question"], str) and row["question"].strip() for row in rows)

def test_expected_type_distribution_and_review_splits():
    rows = [json.loads(line) for line in PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert Counter(row["kind"] for row in rows) == {
        "answerable": 15, "unanswerable": 5, "conflict": 3,
        "prompt_injection": 3, "stale_version": 2, "human_approval": 2,
    }
    assert Counter(row["split"] for row in rows) == {"development": 6, "candidate_holdout": 24}

def test_answerable_items_are_cited_and_unreviewed_challenges_are_not_claimed_achieved():
    rows = [json.loads(line) for line in PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    for row in rows:
        if row["kind"] == "answerable":
            assert row["expected_source"] == "guardeval_test_policy.pdf"
            assert row["expected_page"] in range(1, 6)
            assert row["expected_literal"] in row["source_evidence"]
            assert row["expected_response_type"] == "answer_with_citation"
        else:
            assert row["split"] == "candidate_holdout"
            assert row.get("fixture_requirement")
            assert row["approved_for_scoring"] is False
