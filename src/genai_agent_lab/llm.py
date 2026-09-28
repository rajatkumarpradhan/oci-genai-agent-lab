"""Deterministic scripted planner standing in for an LLM.

A real ReAct agent calls an LLM (for example an OCI Generative AI chat
model) to produce Thought/Action text. This lab replaces that call with a
rule-based planner so the whole loop runs offline and reproducibly. The
planner emits the exact text format an LLM would, so the agent's parser,
guardrails and trace logic are exercised honestly.
"""

from __future__ import annotations

# A small task book: keyword -> scripted ReAct turns. Each turn is the raw
# text an LLM would emit. The planner walks its script in order.
TASK_SCRIPTS: dict[str, list[str]] = {
    "idle instance": [
        "Thought: I should list the compute instances first.\nAction: list_instances[]",
        "Thought: Now I check metrics for the instance that looks idle.\nAction: get_metrics[i-0a1b2c]",
        "Final Answer: Instance i-0a1b2c (dev-box) averages 2.1% CPU over 7 days and is a candidate to stop; estimated idle cost $18.40/month.",
    ],
    "budget": [
        "Thought: I need the current budget status.\nAction: get_budget[]",
        "Final Answer: Spend is $412.30 of a $500.00 budget (82%). At the current rate the budget is exceeded around day 26; review the top two services.",
    ],
    "error logs": [
        "Thought: Search the logs for recent errors.\nAction: search_logs[ERROR]",
        "Thought: One error mentions an OCID; I will quote it.\nAction: search_logs[ocid1]",
        "Final Answer: Found 3 ERROR entries; the recurring one is a volume attachment timeout.",
    ],
}

FALLBACK = "Final Answer: I do not have a scripted path for this task in the offline lab."


class ScriptedPlanner:
    """Plays back scripted ReAct turns for known tasks.

    This is deliberately *not* a model: it makes the lab deterministic so
    trace evaluation can gate on exact behaviour. Swap this class for a
    real LLM client to go live (not done in this portfolio project).
    """

    def __init__(self, task: str):
        self._task = task.lower()
        self._script = self._pick()
        self._pos = 0

    def _pick(self) -> list[str]:
        for keyword, script in TASK_SCRIPTS.items():
            if keyword in self._task:
                return list(script)
        return [FALLBACK]

    def complete(self, prompt: str) -> str:
        """Return the next scripted turn, ignoring the prompt like a stub."""
        if self._pos >= len(self._script):
            # Anything past the script: terminate safely.
            return self._script[-1] if self._script else FALLBACK
        turn = self._script[self._pos]
        self._pos += 1
        return turn
