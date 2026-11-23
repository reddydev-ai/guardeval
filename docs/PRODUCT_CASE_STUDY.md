# GuardEval — Evaluation as an AI Product Capability

**Project type:** Independent portfolio prototype · **Audience:** AI Automation Product Manager and technical product interviews

## Problem
Teams may ship convincing chatbot demos without knowing whether answers are supported, citations are correct, or automated actions remain under human control. A quality gate must make a falsifiable claim about *what was actually tested*.

## Product principle
Do not confuse a green synthetic smoke test with real model quality. GuardEval separates: (a) offline/synthetic harness checks, (b) genuine running-service integration against synthetic content, and (c) optional credentialed model-quality measurement, which **has not been executed**.

## Product users

| User | Need | Guardrail |
| --- | --- | --- |
| AI Product Manager | Decide whether a release is sufficiently evidenced | Clearly labeled test level and exclusions |
| Evaluation engineer | Reproduce service behavior | Disposable synthetic corpus and CI |
| Risk reviewer | Audit evidence | Correct retrieved page, answer citation and reviewer gate |
| Platform operator | Prevent silent regression | Fail-closed checks, separate credentials and strict dependencies |

## What is empirically verified
GitHub Actions has run actual PolicyMind and FlowAgent services with synthetic data. Five RAG scenarios and six vendor workflow scenarios passed, including inline citation, top-page evidence, reviewer authorization and replay rejection. The entire optional RAGAS/DeepEval dependency stack installs and imports. **No paid LLM generation or LLM-judge experiment has been performed.**

## Metrics: how to interpret them
- **Top-1 retrieval hit rate**: one reference appearing in the first retrieved policy chunk. It is not general RAG recall.
- **Citation match rate**: source/page plus inline citation checks on synthetic cases. It does not prove comprehensive claim support.
- **Risk/approval correctness**: six deterministic synthetic scenarios; no field error rate is inferred.
- **Model quality:** would require separate held-out human-labeled samples, actual generated answers, independent LLM judges, calibration and adverse-case coverage.

## Product decisions
1. Make a false green release result impossible by default.
2. Reject missing or partial metric rows rather than silently averaging available scores.
3. Separate evaluation credentials from ordinary service credentials.
4. Preserve per-case evidence and record error types without publicly leaking documents.
5. Choose a modest trustworthy coverage claim over an impressive unverifiable quality percentage.

## Phased roadmap
**Current:** real-service synthetic integration and strict optional judging infrastructure.

**Next:** an independently reviewed held-out dataset, refusal and contradiction cases, judge disagreement study, latency and model-cost measurement (only with budget approval).

**Production gate (not complete):** identity-aware access, non-public benchmark storage, gold-label governance, measurement uncertainty, drift monitoring, reproducible model versions and escalation/runbooks.

## PM interview narrative
*Situation:* AI answer quality is probabilistic and standard unit tests alone can mislead product owners.

*Task:* Define a release decision framework that distinguishes integration correctness from model quality.

*Approach:* Build reproducible synthetic services, source-linked evidence, explicit failure behavior and unambiguous coverage reporting.

*Result you can legitimately claim:* Passing CI-verified integration of five RAG and six workflow scenarios and a strict, installable evaluation framework. **Do not claim a measured hallucination reduction or production reliability improvement from this prototype.**

## Evidence
- [Current technical README](../README.md)
- [Real-service CI workflow](../.github/workflows/live-integration.yml)
- [Model dependency checks](../.github/workflows/model-dependencies.yml)
- [Strict validation tests](../tests/)

**Status:** A reproducible quality-engineering foundation, not a production quality certification.
