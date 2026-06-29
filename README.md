# GuardEval — LLM Evaluation & Guardrails Layer

GuardEval tests **PolicyMind** and **FlowAgent** before every release. It measures
**faithfulness, answer relevancy, context precision, hallucination risk**, and
**task completion**, and ships a **pytest regression suite** that acts as a CI
quality gate plus a **Streamlit dashboard** for visual review.

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

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add OPENAI_API_KEY
```

### Run the dashboard
```bash
streamlit run dashboard.py
```

### Run the regression gate (CI)
```bash
pytest -v
```

### Evaluate the live services
```bash
export POLICYMIND_URL=http://localhost:8000
export FLOWAGENT_URL=http://localhost:8001
pytest -v          # now scores real outputs and enforces thresholds
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
