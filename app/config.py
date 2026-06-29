"""Configuration for GuardEval."""
import os
from functools import lru_cache
from pydantic import BaseModel


class Settings(BaseModel):
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    judge_model: str = os.getenv("JUDGE_MODEL", "gpt-4o")

    # Optional: live service URLs. If unset, GuardEval evaluates saved fixtures.
    policymind_url: str = os.getenv("POLICYMIND_URL", "")
    flowagent_url: str = os.getenv("FLOWAGENT_URL", "")

    # Pass/fail thresholds used by the regression suite and dashboard.
    min_faithfulness: float = float(os.getenv("MIN_FAITHFULNESS", "0.70"))
    min_answer_relevancy: float = float(os.getenv("MIN_ANSWER_RELEVANCY", "0.70"))
    min_context_precision: float = float(os.getenv("MIN_CONTEXT_PRECISION", "0.60"))
    max_hallucination: float = float(os.getenv("MAX_HALLUCINATION", "0.30"))
    min_task_completion: float = float(os.getenv("MIN_TASK_COMPLETION", "0.70"))

    # LangSmith tracing is enabled automatically if these env vars are set:
    #   LANGCHAIN_TRACING_V2=true, LANGCHAIN_API_KEY=...


@lru_cache
def get_settings() -> Settings:
    return Settings()
