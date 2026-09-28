"""ReAct loop: Thought/Action/Observation cycles until Final Answer."""

from __future__ import annotations

import json
import re

from .guardrails import Guardrails, GuardrailViolation
from .tools import TOOLS, ToolError
from .trace import Step, Trace

ACTION_RE = re.compile(r"Action:\s*([A-Za-z_][A-Za-z0-9_]*)\[(.*?)\]\s*$", re.S)
FINAL_RE = re.compile(r"Final Answer:\s*(.*)$", re.S)
THOUGHT_RE = re.compile(r"Thought:\s*(.*?)(?:\n|$)")


def parse_turn(text: str) -> tuple[str, str | None, str | None, str | None]:
    """Parse one planner turn.

    Returns (thought, action_name, action_arg, final_answer). Exactly one of
    (action_name, final_answer) is set on a well-formed turn.
    """
    thought_m = THOUGHT_RE.search(text)
    thought = thought_m.group(1).strip() if thought_m else ""
    final_m = FINAL_RE.search(text)
    if final_m:
        return thought, None, None, final_m.group(1).strip()
    action_m = ACTION_RE.search(text)
    if action_m:
        return thought, action_m.group(1), action_m.group(2).strip(), None
    raise ValueError(f"unparseable planner turn: {text!r}")


class ReActAgent:
    def __init__(self, planner, guardrails: Guardrails | None = None):
        self.planner = planner
        self.guardrails = guardrails or Guardrails()

    def run(self, task: str) -> Trace:
        trace = Trace(task=task)
        scratchpad = ""
        for i in range(self.guardrails.max_steps):
            turn = self.planner.complete(scratchpad)
            thought, name, arg, final = parse_turn(turn)
            if final is not None:
                trace.add(Step(i, thought, None, None, "final"))
                trace.final_answer = self.guardrails.scrub(final)
                return trace
            assert name is not None and arg is not None
            action_str = f"{name}[{arg}]"
            try:
                note = self.guardrails.check_action(name)
            except GuardrailViolation as exc:
                trace.add(Step(i, thought, action_str, None, str(exc)))
                trace.stopped_reason = "guardrail_stop"
                trace.final_answer = f"Stopped by guardrails: {exc}"
                return trace
            try:
                result = TOOLS[name](arg) if arg else TOOLS[name]()
                observation = self.guardrails.scrub(json.dumps(result, sort_keys=True))
            except ToolError as exc:
                observation = f"tool error: {exc}"
            trace.add(Step(i, thought, action_str, observation, note))
            scratchpad += f"\n{turn}\nObservation: {observation}"
        trace.stopped_reason = "max_steps"
        trace.final_answer = "Stopped: step cap reached without a final answer."
        return trace
