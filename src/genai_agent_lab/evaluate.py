"""Golden-trace evaluation: run tasks, compare behaviour to expectations."""

from __future__ import annotations

import json
from dataclasses import dataclass

from .agent import ReActAgent
from .guardrails import Guardrails
from .llm import ScriptedPlanner


@dataclass
class EvalResult:
    task: str
    passed: bool
    expected_actions: list[str]
    actual_actions: list[str]
    answer_contains: str
    stopped_reason: str


def run_golden(path: str) -> list[EvalResult]:
    with open(path, encoding="utf-8") as fh:
        golden = json.load(fh)
    results: list[EvalResult] = []
    for case in golden["cases"]:
        agent = ReActAgent(ScriptedPlanner(case["task"]), Guardrails(max_steps=case.get("max_steps", 8)))
        trace = agent.run(case["task"])
        actions_ok = trace.action_sequence() == case["expected_actions"]
        answer_ok = case["answer_contains"] in (trace.final_answer or "")
        reason_ok = trace.stopped_reason == case.get("expected_stop", "completed")
        results.append(EvalResult(
            task=case["task"],
            passed=actions_ok and answer_ok and reason_ok,
            expected_actions=case["expected_actions"],
            actual_actions=trace.action_sequence(),
            answer_contains=case["answer_contains"],
            stopped_reason=trace.stopped_reason,
        ))
    return results
