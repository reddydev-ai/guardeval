# Published GitHub Portfolio — Maintenance and Verification

**Current state (verified November 22, 2026 Toronto):**
- The [GitHub account profile README](https://github.com/reddydev-ai/reddydev-ai/blob/main/README.md) is **published**.
- The [portfolio website](https://reddydev-ai.github.io/guardeval/) is **deployed** via GitHub Pages, sourced from `main:/docs`.
- A [GitHub Pages deploy run](https://github.com/reddydev-ai/guardeval/actions/runs/45108665677) and [automated browser-rendered audit](https://github.com/reddydev-ai/guardeval/actions/runs/45109675298) succeeded. The latter checked 1440px desktop and 390px mobile, rendered text, cards, internal anchors and horizontal overflow.
- Three independent project repositories are public and linked from the profile.
- The account-level **short GitHub Bio field** cannot be edited using the available repository connector. It is separate from the published README and may still need alignment.

## How to maintain the published materials

1. Edit the profile introduction in [reddydev-ai/reddydev-ai/README.md](https://github.com/reddydev-ai/reddydev-ai/blob/main/README.md).
2. Edit the one-page website source at [docs/index.html](index.html) and merge changes into `main`; GitHub Pages will rebuild. Observe the [Pages workflow](https://github.com/reddydev-ai/guardeval/actions) before saying the update is live.
3. Edit the expanded [portfolio narrative](../PORTFOLIO.md) and linked [product decision record](RELEASE_DECISION_RECORD.md) whenever metrics, evidence or release scope changes.
4. Run [browser visual QA](../.github/workflows/portfolio-browser.yml) to check responsive layout and save full-page desktop/mobile screenshots. Inspect screenshot artifacts for typography and spacing as a separate *human review*.
5. Recheck all external GitHub paths and workflow statuses before sending to recruiters. No tool can guarantee an external URL will never change.

## What must not be done

- Do not publish real employer policy documents, proprietary operational data, identity tokens, or model API keys.
- Do not claim the default CI's extractive synthetic questions measure general LLM answer quality.
- Do not create real-model scores, customer adoption or savings figures without the actual reviewed experiment.
- Do not expose the PolicyMind/FlowAgent backend APIs publicly under the current prototype security controls.

**Portfolio release ≠ AI service production release.** Publishing static evidence is intentional and is substantially lower risk.

