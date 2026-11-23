"""Guard against misrepresenting synthetic scores as production evidence."""
from types import SimpleNamespace
import pytest
from app import runner


@pytest.mark.parametrize(("policy_url", "agent_url"), [
    ("http://localhost:8000", ""),
    ("", "http://localhost:8001"),
])
def test_mixed_live_offline_configuration_is_rejected(monkeypatch, policy_url, agent_url):
    monkeypatch.setattr(
        runner, "settings",
        SimpleNamespace(policymind_url=policy_url, flowagent_url=agent_url),
    )
    with pytest.raises(RuntimeError, match="BOTH"):
        runner.run_all()


def test_live_release_gating_fails_closed_until_retrieval_is_auditable(monkeypatch):
    monkeypatch.setattr(
        runner, "settings",
        SimpleNamespace(
            policymind_url="http://localhost:8000",
            flowagent_url="http://localhost:8001",
        ),
    )
    with pytest.raises(RuntimeError, match="Live release gating is disabled"):
        runner.run_all()
