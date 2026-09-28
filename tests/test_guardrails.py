import pytest

from genai_agent_lab.guardrails import Guardrails, GuardrailViolation


def test_allowed_read_tools():
    g = Guardrails()
    for t in ("list_instances", "get_metrics", "search_logs", "get_budget"):
        assert g.check_action(t) == "allowed"


def test_denies_destructive_verbs():
    g = Guardrails()
    with pytest.raises(GuardrailViolation):
        g.check_action("terminate_instance")
    with pytest.raises(GuardrailViolation):
        g.check_action("delete_volume")


def test_denies_unknown_tool():
    g = Guardrails()
    with pytest.raises(GuardrailViolation):
        g.check_action("sudo_make_sandwich")


def test_scrub_redacts_email_and_ocid():
    g = Guardrails()
    out = g.scrub("mail oncall@example.com about ocid1.volume.oc1..aaaa1111")
    assert "oncall@example.com" not in out
    assert "ocid1.volume" not in out
    assert "[redacted-email]" in out and "[redacted-ocid]" in out
