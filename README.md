# GuardEval — LLM Evaluation & Guardrails Layer

GuardEval is a portfolio evaluation harness for **PolicyMind** and **FlowAgent**. Its current GitHub Actions workflow executes **synthetic/offline smoke checks only**; it does NOT test or certify the live services before release. It measures
**faithfulness, answer relevancy, context precision, hallucination risk**, and
**task completion**, and ships a **pytest regression suite** that acts as a CI
quality gate plus a **Streamlit dashboard** for exploratory visual review.

This is the project that signals production maturity: most candidates build a RAG
demo; few build the evaluation layer that proves the demo is reliable.

## What it evaluates

| Target | Metrics | Tool |
|---|---|---|
| **PolicyMind** (RAG) | Faithfulness, answer relevancy, context precision | RAGAS |
| **PolicyMind** (RAG) | Hallucination rate | DeepEval |
| **FlowAgent** (agent) | Task completion (risk correct + memo produced) | DeepEval / rule |
| Both | Regression pass/fail vs thresholds | pytest |

## How it runs

```
datasets.py  (20 PolicyMind Q&A + 10 FlowAgent scenarios, gold answers)
     │
     ▼ runner.py
   LIVE  → calls POLICYMIND_URL /ask  and  FLOWAGENT_URL /verify(+resume)
   OFFLINE → simulates outputs from gold data (no services needed; clearly flagged)
     │
     ▼ evaluators.py
   RAGAS  → faithfulness / relevancy / context precision
   DeepEval → hallucination / task completion
     │
     ▼ results.json
     ├─► dashboard.py   (Streamlit: scores vs thresholds, pass/fail)
     └─► tests/         (pytest: CI quality gate)
```

> RAGAS and DeepEval move fast. If a version mismatch occurs, the evaluators fall
> back to a transparent LLM-judge scorer **clearly labelled by the `engine` field**
> such as `engine: llm-judge`, so the harness always runs and results are never
> silently wrong.

## Evaluation integrity (important)

The offline runner synthesizes answers from reference data. Its scores **do not measure actual model quality** and must not be used as release evidence or presented as validated production metrics. Although API clients are implemented, **live release gating is intentionally disabled** until real retrieval contexts are captured safely from PolicyMind and an authorized evaluation environment is provisioned. Configuring only one service URL now fails explicitly. Judge errors no longer return an invented passing score. Current CI verifies smoke-test mechanics only; full end-to-end evaluation, secrets provisioning, and safety review remain pending.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add OPENAI_API_KEY
set -a; source .env; set +a  # export credentials for this shell (trusted local file only)
```

### Run the dashboard
```bash
streamlit run dashboard.py
```

### Run the regression gate (CI)
```bash
pytest -v
```

### Live evaluation (intentionally disabled until retrieval evidence is available)
```bash
export POLICYMIND_URL=http://localhost:8000
export FLOWAGENT_URL=http://localhost:8001
pytest -v          # currently FAILS CLOSED until real retrieved contexts are available
```

### Optional: LangSmith tracing
Set `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` to capture full traces of
every judged run in LangSmith.

## Known limitations
- OFFLINE mode scores gold-derived outputs (sanity check, not a real eval).
- Task-completion for FlowAgent is rule-based (risk match + memo present); deepen
  with DeepEval's conversational/task metrics for richer scoring.
- Dataset is a starter 20/10 set — expand with adversarial, edge-case, and production-style examples.

## What I would improve next
- Expand datasets and add adversarial / prompt-injection probes.
- Add latency and cost tracking per query alongside quality.
- GitHub Actions workflow included in .github/workflows/eval.yml.
- Track scores over time (store results.json history) to detect drift.
