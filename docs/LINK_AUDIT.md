# Public Portfolio Link and Evidence Audit

**Run date:** November 22, 2026 (Toronto)

## What was checked

Used the connected GitHub API to read the full recursive `main` file trees for the account profile repository (`reddydev-ai/reddydev-ai`) and three independent project repositories (`reddydev-ai/guardeval`, `reddydev-ai/policymind`, `reddydev-ai/flowagent`). These trees were not truncated.

I inspected Markdown relative links and GitHub-owned file/tree/workflow links in the:
- public GitHub profile README;
- all three technical repository READMEs;
- GuardEval central portfolio narrative and HTML landing-page source;
- GuardEval product case study, security decision, publishing guide (pre-update) and interview walkthrough.

**Result:** 56 of 56 examined *file/tree/workflow path references* resolved to a real path in the current repository trees. In addition, the live deployed website passed its [automated rendered desktop/mobile audit](https://github.com/reddydev-ai/guardeval/actions/runs/45109675298), including HTTP 200, all three project cards, anchor IDs and no horizontal overflow.

## What that does not establish

- It does not prove all external browser requests will continue to return HTTP 200. GitHub can throttle automated clients; links can change after this audit.
- It does not validate historical snapshots or third-party caches. A stale repository summary listing only starter files is not evidence of today's `main` contents.
- It does not turn passing synthetic integration into measured generative-model quality.
- The audit predates the latest release decision document and page revisions. The final browser audit must run again after these are merged.
- The short GitHub account Bio field was not modified.

## Important identity distinction

This GuardEval repository evaluates RAG and LangGraph workflow mechanics. It is **not affiliated with** the academic [GuardEval content moderation benchmark and GemmaGuard model](https://arxiv.org/abs/2601.03273).

## Useful current sources

- [Full current repository tree](https://github.com/reddydev-ai/guardeval/tree/main)
- [Product decision record](RELEASE_DECISION_RECORD.md)
- [Live-service integration workflow](../.github/workflows/live-integration.yml)
- [Browser-rendered verification workflow](../.github/workflows/portfolio-browser.yml)

**Conclusion:** The "missing docs / evaluation directory" concern is not supported by the inspected GitHub main branch. The discrepancy is consistent with an old snapshot or cache but the precise cause of the other reviewer's snapshot is unknown.
