"""LangSmith tracing setup.

LangSmith traces LangChain/RAGAS calls automatically when these env vars are set:
  LANGCHAIN_TRACING_V2=true
  LANGCHAIN_API_KEY=ls-your-key
  LANGCHAIN_PROJECT=guardeval      (optional, defaults to "default")

This module enables tracing explicitly so it works regardless of env var order,
and provides a helper to tag each eval run with metadata (run_id, mode).

If LANGCHAIN_API_KEY is not set, tracing is silently skipped — GuardEval works
fully without it. LangSmith is observability, not a dependency.
"""
from __future__ import annotations
import os
import uuid


def setup_tracing(run_name: str = "guardeval-run") -> str | None:
    """Enable LangSmith tracing for this evaluation run.
    Returns the run_id if tracing is active, None otherwise.
    """
    api_key = os.getenv("LANGCHAIN_API_KEY", "")
    if not api_key:
        return None

    # These env vars activate the LangChain callback that sends traces to LangSmith
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "guardeval")

    run_id = str(uuid.uuid4())
    os.environ["LANGCHAIN_RUN_ID"] = run_id

    try:
        from langsmith import Client
        client = Client(api_key=api_key)
        # Tag the run so it shows up labelled in LangSmith
        client.create_run(
            name=run_name,
            run_type="chain",
            id=run_id,
            inputs={"mode": os.getenv("EVAL_MODE", "offline")},
        )
        return run_id
    except Exception:
        # LangSmith unavailable or network issue - continue without tracing
        return None


def tracing_active() -> bool:
    return bool(os.getenv("LANGCHAIN_API_KEY")) and os.getenv("LANGCHAIN_TRACING_V2") == "true"
