# Decision Record DR-001 — Scope, Release Evidence and No-Go Calls

**Project:** Independent AI Automation Product Management portfolio
**State:** Public engineering evidence only; production user deployment is not approved
**Last reviewed:** November 22, 2026 (Toronto)
**Stakeholders in this hypothetical product review:** AI product owner, engineering lead, policy/domain SME, security, risk/compliance and end-user research lead. These are *proposed roles*, not a claim those parties approved this prototype.

## The concrete product decision

**Do not ship a public AI question-answering or vendor-approval backend.** Publish static documentation and reproducible synthetic integration evidence instead. Even if the containers run, the services lack verified user identity, policy/document ACLs and real-model quality results. Public inference would create unnecessary risk without demonstrating demand.

**Do not label GuardEval a production quality gate.** The current no-key CI runs real PolicyMind and FlowAgent services on a small synthetic corpus. It tests mechanics, *not* general generative quality.

These decisions trade off a public interactive demo and possible convenience for security and evidence integrity. A constrained interactive demo can be reconsidered only after release blockers are resolved; there is no evidence that a live demo by itself improves recruiter outcomes.

## Gate register — current observations, not invented production KPIs

| Gate / check | Acceptance criterion | Observable evidence | Current decision | What this means |
| --- | --- | --- | --- | --- |
| Running-service retrieval & citation | Each of 5 scripted synthetic queries returns expected source/page evidence and an inline citation; no skipped case | [Integration workflow](https://github.com/reddydev-ai/guardeval/actions/workflows/live-integration.yml) and [validator](../app/live.py) | **PASS: 5 scripted cases** | Selected retrieval/citation mechanics passed only for the seeded synthetic corpus |
| Human review and workflow integrity | Each of 6 scripted synthetic vendor scenarios satisfies its documented risk/approval rule; unauthorized reviewer and replay rejected | [Integration workflow](https://github.com/reddydev-ai/guardeval/actions/workflows/live-integration.yml) and [validator](../app/live.py) | **PASS: 6 scripted cases** | Selected workflow/security branches worked in isolation |
| Synthetic/regression integrity | Complete pytest suite returns no failing tests | [Smoke workflow](https://github.com/reddydev-ai/guardeval/actions/workflows/eval.yml) | **PASS: last verified run** | Engineering regression, not live model quality |
| Evaluation infrastructure | Pinned optional RAGAS/DeepEval dependencies install and required APIs import | [Dependency preflight](https://github.com/reddydev-ai/guardeval/actions/workflows/model-dependencies.yml) | **PASS: imports only** | Does not prove model or judge calls can run end-to-end |
| Real LLM answer quality | Actual generative answers on a separate document-held-out, human-reviewed dataset, judge calibration and per-case error review | [Evaluation protocol](../evaluation/PROTOCOL.md) | **NOT MEASURED — BLOCKED** | No RAGAS/DeepEval quality outcome can be advertised |
| Adversarial and abstention behavior | Held-out conflicts, missing-source questions and malicious-context cases execute with reviewed expected outcomes | [30 draft scenarios](../evaluation/catalogue_v1.jsonl) | **NOT TESTED — BLOCKED** | Cases are draft/unreviewed and some lack fixtures |
| Production identity / policy-data protection | OIDC/SSO, resource authorization, secure ingestion, retention, auditability and incident response are reviewed and exercised | [Security decision](SECURITY_AND_DEPLOYMENT_DECISION.md) | **NOT IMPLEMENTED — BLOCKED** | Private demo only |

**Interpreting "PASS":** A CI success is a binary result for a defined, limited test, not a 100% population reliability score. This matrix is updated as an evidence register; it is not a benchmark leaderboard.

## Quality threshold configuration versus validated acceptance criteria

The repository config contains **illustrative defaults**, not independently calibrated release thresholds:

| Configured metric | Current code default | Can it justify shipping now? |
| --- | ---: | --- |
| Minimum faithfulness | 0.70 | **No**: real LLM evaluation has not run |
| Minimum answer relevancy | 0.70 | **No** |
| Minimum context precision | 0.60 | **No** |
| Maximum hallucination | 0.30 | **No** |
| Minimum task completion | 0.70 | **No** |

These values come from [app/config.py](../app/config.py). They are neither scientifically justified PM targets nor measured outputs; they must be revisited against severity, baseline performance, and independent human judgments. No universal 0.70 quality bar is acceptable for every regulated use case.

## A measurable product discovery plan (not completed)

1. **Baseline:** observe how operations staff search synthetic/approved policies today, record time-to-correct-citation, task failure rate and confidence in the answer. Do not infer savings from technical latency.
2. **Instrument the workflow:** consented task events for retrieval, evidence checking, abstention, review, override and user-reported usefulness; avoid raw sensitive document logging.
3. **Compare options:** manual search versus cited retrieval, rule-only vendor checks versus agent-assisted preparation, with the same user tasks and independently labeled outcomes.
4. **Decide with stakeholders:** choose a user-valued metric and an agreed minimum acceptable quality and severity threshold. Pre-register cohort, duration and denominator rather than reporting after-the-fact wins.
5. **Ship narrowly or say no:** if any severe unsupported decision, unauthorized approval or sensitive-data disclosure is observed, block rollout until root cause and controls are verified.

**PM proof today:** the explicit scope and trade-off decision, reproducible acceptance gates, and no-go rationale. **Not yet PM proof:** user discovery, prioritization with a real product team, adoption data, adoption improvements, and a validated ROI case.

## Name disambiguation

This repository's **GuardEval** is an **independent RAG and workflow integration / QA project**. It has **no affiliation** with the published [GuardEval moderation benchmark and GemmaGuard model](https://arxiv.org/abs/2601.03273). It neither contains that benchmark nor makes the moderation paper's claims.
