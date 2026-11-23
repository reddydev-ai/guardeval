# 7-minute interview walkthrough — AI Automation Product Manager

**Purpose:** Demonstrate clear product decisions rather than a dashboard of unvalidated accuracy scores. No paid API call or public infrastructure is required.

## Minute 0–1: Frame the problem
AI systems need better release criteria than “the answer looked good.” Product owners need reliable answers, evidence, a predictable response to uncertainty and accountable human decisions.

## Minute 1–2: The portfolio system
Explain three distinct independent prototypes:

- [PolicyMind](https://github.com/reddydev-ai/policymind): verifiable cited policy search and source lifecycle.
- [FlowAgent](https://github.com/reddydev-ai/flowagent): deterministic risk checks, approval interrupt and reviewer controls.
- [GuardEval](https://github.com/reddydev-ai/guardeval): running-service synthetic integration and explicit judge-quality gates.

**Do not claim these projects were deployed for an employer.**

## Minute 2–3: The product trade-off
When a policy answer lacks evidence, a confident hallucination is worse than a visible limitation. The PM decision is to invest in source provenance, evaluation and human review before making a broad automation promise.

## Minute 3–4: Show actual verified mechanics
Open the [GuardEval live-service workflow](../.github/workflows/live-integration.yml). This starts real private PolicyMind and FlowAgent services, seeds a synthetic PDF, then tests five document questions and six vendor approval scenarios. Inspect [integration runner](../app/live.py) for same-request context checks, inline citations, authorization and replay protection.

## Minute 4–5: Explain what a green CI run does **not** prove
No paid generative model was used in the standard CI run. The synthetic corpus is small and public. Do not advertise five successful RAG examples as a measured general accuracy rate. The [30-case design catalogue](../evaluation/catalogue_v1.jsonl) is explicitly unreviewed and not approved for scoring.

## Minute 5–6: Proposed product KPIs
Discuss decision-level product measures, all **proposed, not achieved**:
- Verified citation correctness on independently reviewed content
- Unsupported material claim rate and severe failure count
- Successful task completion and human override/exception rate
- Feedback closure time and trust/repeat-use signals
- Latency and cost per successful task; net user time saved against baseline

## Minute 6–7: Roadmap and go/no-go
For production, prioritize access control, secure ingestion, version lifecycle, authoritative data and properly reviewed evaluations. Keep prototype services private. Explain how you would decide to release, iterate, narrow scope or stop.

## Answers to likely hiring-panel challenges
**“Why not simply use a better LLM?”** Because source authority, lifecycle, access rights and a human decision boundary remain product/system problems; model choice alone will not fix them.

**“Did you reduce hallucinations by X%?”** No such rate was independently measured for these public projects. CI verifies integration and some guardrails. A larger reviewed benchmark and real model/judge calls are needed.

**“How would you justify ROI?”** Establish an existing-task baseline, measure task success, incident severity, human handling time, token costs and sustained adoption. Don't count synthetic integration passes as business savings.

**“Is the demo production-secure?”** No. Shared-key demos are isolated. The [release decision record](SECURITY_AND_DEPLOYMENT_DECISION.md) lists the identity, ingestion, audit and operational requirements still absent.

**“What is your strongest technical leadership signal?”** The disciplined separation of a correct workflow, a trustworthy evidence trail and actual validated model-quality measurements.

## Verification links
- [Live-service CI](https://github.com/reddydev-ai/guardeval/actions/workflows/live-integration.yml)
- [Regression and integrity CI](https://github.com/reddydev-ai/guardeval/actions/workflows/eval.yml)
- [Dependency preflight](https://github.com/reddydev-ai/guardeval/actions/workflows/model-dependencies.yml)

*This is a proposed interview narrative, not a record of actual interviews or interviewer feedback.*
