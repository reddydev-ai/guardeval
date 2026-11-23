"""GuardEval dashboard. Runs the evaluation and visualises scores against
thresholds. Run with:  streamlit run dashboard.py
"""
import streamlit as st

from app.config import get_settings
from app.runner import run_all

settings = get_settings()

st.set_page_config(page_title="GuardEval", page_icon="🧪", layout="wide")
st.title("🧪 GuardEval — LLM Evaluation & Guardrails")
st.caption("Evaluates PolicyMind (RAG) and FlowAgent (agent) before release.")

if st.button("Run evaluation", type="primary"):
    with st.spinner("Running RAGAS + DeepEval + regression checks..."):
        st.session_state.report = run_all()

report = st.session_state.get("report")
if not report:
    st.info("Click **Run evaluation** to score the latest outputs.")
    st.stop()

st.markdown(f"**Mode:** `{report['mode']}`  ·  **Generated:** {report['generated_at']}")
if report["mode"] == "offline":
    st.error("SYNTHETIC SMOKE DATA ONLY — these scores are not real model quality measurements, and do not certify a release. Live release gating is disabled until real retrieval contexts can be evaluated securely.")

th = report["thresholds"]


def metric_row(label, value, threshold, higher_is_better=True):
    if value is None:
        st.metric(label, "n/a")
        return
    if report["mode"] != "live":
        st.metric(label, f"{value:.2f}", delta="synthetic — not validated")
        return
    ok = value >= threshold if higher_is_better else value <= threshold
    st.metric(label, f"{value:.2f}", delta=f"{'✅ pass' if ok else '❌ fail'} (thr {threshold})")


st.header("PolicyMind — RAG quality")
c1, c2, c3, c4 = st.columns(4)
ragas = report["policymind"]["ragas"]
with c1:
    metric_row("Faithfulness", ragas.get("faithfulness"), th["min_faithfulness"])
with c2:
    metric_row("Answer relevancy", ragas.get("answer_relevancy"), th["min_answer_relevancy"])
with c3:
    metric_row("Context precision", ragas.get("context_precision"), th["min_context_precision"])
with c4:
    metric_row("Hallucination", report["policymind"]["hallucination"].get("hallucination"),
               th["max_hallucination"], higher_is_better=False)
st.caption(f"Engine: {ragas.get('engine')}  ·  cases: {report['policymind']['n_cases']}")

st.header("FlowAgent — task completion")
tc = report["flowagent"]["task_completion"]["task_completion"]
metric_row("Task completion", tc, th["min_task_completion"])
st.dataframe(
    [
        {
            "Vendor": r["vendor_name"],
            "Expected": r["expected_risk"],
            "Actual": r["actual_risk"],
            "Match": "✅" if r["actual_risk"] == r["expected_risk"] else "❌",
        }
        for r in report["flowagent"]["results"]
    ],
    use_container_width=True,
)
