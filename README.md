# GuardEval — Verifiable RAG and Agent Workflow Evaluation

> **For AI Product Management interviews:** [7-minute product walkthrough](docs/INTERVIEW_WALKTHROUGH.md) · [Security and zero-cost deployment decision](docs/SECURITY_AND_DEPLOYMENT_DECISION.md). These documents clearly distinguish tested prototypes from unmet production requirements.


> **Product-management portfolio brief:** [Problem, users, success metrics, roadmap and limitations](docs/PRODUCT_CASE_STUDY.md). This is an independent prototype; no employer or customer outcome is claimed.


GuardEval is an open-source portfolio project for evaluating [PolicyMind](https://github.com/reddydev-ai/policymind) (policy-document RAG) and [FlowAgent](https://github.com/reddydev-ai/flowagent) (human-reviewed vendor verification).

**Current verified capability:** An automated, reproducible *real-service integration gate* using a dedicated synthetic corpus. The workflow starts both real APIs, ingests a PDF into Qdrant, tests the retrieved evidence and citations, and exercises LangGraph approvals. No production data or paid LLM credentials are used in default CI.

**Not yet verified:** Real generative-model quality, calibrated hallucination rates, adversarial robustness and readiness for production deployment. An optional strict LLM-judge path exists, but has not passed a credentialed, end-to-end model evaluation. Never interpret a successful integration job as those assurances.

## Verification architecture

```text
Five-page synthetic PDF ──> PolicyMind /ingest ──> Qdrant
                                                   |
Question ──> PolicyMind /evaluation/ask (dual-key) ┘
                          |
                          +─> exact same-request retrieved text, source, page
                          +─> actual answer and generation mode
                          |
                          +─> GuardEval: source, top-1 evidence, inline citations,
                                         literal reference, mode and security checks

Six synthetic vendor cases ──> FlowAgent /verify (API key)
                                   |
                                   +─> risk + missing docs + approval interrupt
                                   +─> wrong reviewer rejected
                                   +─> /verify/resume (separate reviewer key)
                                   +─> decision, risk, documents and replay checked

Default CI output ──> redacted JSON summary (no documents, queries or keys)
```

## What the tests genuinely demonstrate

| Layer | Evidence | Limit |
| --- | --- | --- |
| Retrieval | Real Qdrant index; top-ranked chunk must contain the correct independent reference | Five synthetic RAG scenarios |
| Provenance | Correct source/page in returned evidence **and** inline answer citation | Does not prove all answer claims are true |
| Answer mode | No-key smoke mode refuses LLM output; LLM mode refuses extractive fallback | Actual generative-model testing is not automatically run |
| Workflow | Real LangGraph start, interruption, reviewer decision and resume | Six synthetic vendor cases |
| Authorization | Bad evaluation key, bad API key and bad reviewer key must fail | Shared demo credentials are not identity-based authorization |
| Replay | Second resume of an already completed review must be rejected | No concurrency or distributed-lock test |
| Optional LLM metrics | Requires genuine RAGAS/DeepEval engines, complete case coverage, finite 0–1 scores and configured thresholds | Credentialed model-quality runs remain unverified |

There are two distinct CI workflows. `.github/workflows/eval.yml` runs legacy **synthetic smoke checks** on saved/reference data; they are not live evaluation results. `.github/workflows/live-integration.yml` runs **actual services** without LLM credentials and verifies retrieval and workflow mechanics.

## Run on a disposable local environment

The simplest reproducible path is the [live-service Actions workflow](https://github.com/reddydev-ai/guardeval/actions/workflows/live-integration.yml), whose job checks out the other two repositories and creates **separate virtual environments** (they use incompatible major versions of LangChain dependencies). A separate [model-dependency preflight](https://github.com/reddydev-ai/guardeval/actions/workflows/model-dependencies.yml) installs the full GuardEval dependency set, checks the environment, and imports the RAGAS/DeepEval APIs without calling paid models. The workflow binds both services to localhost, uses a throwaway Qdrant store, and uses distinct *synthetic-only* authentication keys.

For a local run, start PolicyMind and FlowAgent on separate private ports, then set these values in the GuardEval environment:

```bash
export POLICYMIND_URL=http://127.0.0.1:8000
export FLOWAGENT_URL=http://127.0.0.1:8001
export POLICYMIND_API_KEY=your-local-demo-key
export POLICYMIND_EVAL_KEY=your-different-local-eval-key
export FLOWAGENT_API_KEY=your-local-agent-key
export FLOWAGENT_REVIEWER_KEY=your-separate-local-reviewer-key
export EVAL_REQUIRE_LLM=false
python -m scripts.seed_live
python -m app.live
```

PolicyMind must be configured with `POLICYMIND_ENABLE_EVAL_API=true` and matching server-side credentials. Its evaluation endpoint returns document text. **Never expose it on a public server or run this fixture seeder against an existing business index.** The seeder rejects non-local targets. It is intended for a disposable dataset only.

The GuardEval report in `live-evaluation-report.json` is ignored by Git; its GitHub artifact excludes raw questions, retrieved chunks, model outputs and authentication values.

## Optional LLM-model quality mode

`EVAL_REQUIRE_LLM=true` is a separate, strict path that expects real LLM answers from PolicyMind, authentic RAGAS and DeepEval judging, a complete sample set, finite scores and quality thresholds taken from `app/config.py`. It fails closed if the configured model or evaluator is unavailable. It **has not been validated using paid credentials**, and must not be described as a production release gate.

Before attempting it, use the separate model-evaluation environment tested in the dependency preflight, configure authorized API keys **separately for PolicyMind's answer generation and GuardEval's judges**, and use only synthetic or explicitly approved content. Passing the import test does **not** mean the paid judge or model evaluation was executed. Start with an independently selected, much larger held-out dataset covering out-of-scope questions, missing and contradictory documents, prompt-injection attempts, errors, latency and operational constraints. Evaluate label quality and judge agreement before trusting thresholds.

## Integrity and security boundaries

- Same-invocation evidence is returned by a restricted PolicyMind endpoint; this does not provide cryptographic attestation.
- **Synthetic pass rates are not estimates of general-world accuracy.** No probabilistic confidence bounds or production safety guarantees are inferred from the small corpus.
- PolicyMind's confidence score is a retrieval-derived heuristic and is not calibrated.
- The default mode never treats reference contexts as if the service retrieved them.
- Remote evaluation targets require both `ALLOW_REMOTE_EVAL=true` and an explicit `EVAL_ALLOWED_HOSTS` hostname allowlist, with HTTPS enforced; do not evaluate untrusted URLs.
- Keep all services private; identity, per-document permissions, audit logs, rate limiting, secret rotation, prompt-injection defense and security review are still required for production.

## Repository organization

```text
app/live.py                Real API integration runner, evidence checks, redacted report
app/live_fixtures.py       Independent synthetic RAG and vendor cases
app/quality_gate.py        Strict optional RAGAS/DeepEval score validation
app/runner.py              Legacy offline synthetic scorer (not live quality evidence)
scripts/seed_live.py       Local-only synthetic PDF seed through real ingest API
tests/                     Integrity, authorization, metrics and regression checks
.github/workflows/         Separate synthetic-smoke and live-service CI workflows
```

**Project status:** Real-service CI integration is implemented and verifiable. Credentialed LLM evaluation and production security remain separate, unmet validation milestones.
