# Evaluation Catalogue v1 — zero-budget quality evidence protocol

**State:** 30 synthetic *draft* cases authored for test planning. No human review, no independent locked test set, no model-quality scores. All entries contain `review_status: draft_unreviewed` and `approved_for_scoring: false`.

## Coverage inventory

| Type | Draft cases | Intended evaluation |
| --- | ---: | --- |
| Answerable with citation | 15 | Correct fact, evidence, and source page |
| Unanswerable | 5 | Correct abstention; avoid unrelated answers |
| Conflicting policies | 3 | Surface conflicting evidence and request authoritative version |
| Prompt injection | 3 | Ignore instructions embedded in retrieved documents |
| Stale/replaced source | 2 | Freshness and deletion lifecycle |
| Human approval | 2 | Reject unauthorized or repeated decisions |
| **Total** | **30** | **NOT YET SCORED** |

The first 6 answerable items are tagged `development`; 24 are tagged `candidate_holdout` for *planning*. This is **not** an independently held-out benchmark: multiple questions paraphrase the same five known synthetic facts, and negative/conflict cases require new fixtures. Do not claim an external accuracy estimate from this collection.

## Review and acceptance process
1. A human SME must approve the scope, expected outcomes, literal policy text, page citations and abstention definitions. Record reviewer identity, decision and approval time in an access-controlled record, not public Git history.
2. Separate benchmark development and holdout sets **by document and distinct underlying fact**, not merely question wording. Freeze the holdout before any prompt/model tuning.
3. Create self-contained synthetic fixtures for negative tests. The current retrieval fallback may retrieve unrelated text and is **not proven to abstain**.
4. For every actual evaluation capture prompt/policy version, response, all returned sources, latency, model version, judge model, token/cost totals, result and failure taxonomy. Keep sensitive outputs out of public artifacts.
5. Use blind human claim-level review of judge results before choosing thresholds. Report numerators, denominators and uncertainty, and severe-case failure counts separately.
6. Maintain a **zero-cost** CI route that validates schema and the existing 5 RAG / 6 agent integration scenarios. Never set `approved_for_scoring=true` automatically.

## Product acceptance criteria (proposed, not yet validated)
- Unauthorized actions and secret disclosure: zero tolerated defects.
- Missing/contradictory policy: disclose uncertainty rather than make a confident unsupported assertion.
- Correct citation: quote actual source/page for every factual answer.
- Document update/deletion: old facts must not survive in retrieval without explicit historical-version support.
- Model improvement claims: only after real generated responses, human-approved labels and calibrated evaluation.

## Current evidence
- [Current CI-tested service integration](../.github/workflows/live-integration.yml)
- [Dataset](catalogue_v1.jsonl)
- [Product decision case study](../docs/PRODUCT_CASE_STUDY.md)

**This catalogue is a research/design deliverable, not a passing model benchmark.**
