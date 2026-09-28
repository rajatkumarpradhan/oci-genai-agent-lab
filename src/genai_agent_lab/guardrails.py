"""Guardrails around the agent loop: tool allow-list, step cap, PII redaction."""

from __future__ import annotations

import re

# Read-only tools the agent may call. Anything else is denied before execution.
ALLOWED_TOOLS = {"list_instances", "get_metrics", "search_logs", "get_budget"}

# Names that must never run even if a tool module grows them later.
DENIED_VERBS = ("terminate", "delete", "stop", "create", "update", "attach", "detach")

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
OCID_RE = re.compile(r"ocid1\.[A-Za-z0-9._-]+")


class GuardrailViolation(Exception):
    pass


class Guardrails:
    def __init__(self, max_steps: int = 8, redact: bool = True):
        self.max_steps = max_steps
        self.redact = redact

    def check_action(self, action_name: str) -> str:
        """Return a guardrail note, or raise GuardrailViolation."""
        low = action_name.lower()
        if any(verb in low for verb in DENIED_VERBS):
            raise GuardrailViolation(f"denied: destructive action '{action_name}'")
        if action_name not in ALLOWED_TOOLS:
            raise GuardrailViolation(f"denied: '{action_name}' is not on the tool allow-list")
        return "allowed"

    def scrub(self, text: str) -> str:
        if not self.redact:
            return text
        text = EMAIL_RE.sub("[redacted-email]", text)
        text = OCID_RE.sub("[redacted-ocid]", text)
        return text
