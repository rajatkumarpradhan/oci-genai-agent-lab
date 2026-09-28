"""Structured trace of one agent run."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict


@dataclass
class Step:
    index: int
    thought: str
    action: str | None          # "tool[arg]" or None on final answer
    observation: str | None     # scrubbed tool output, or guardrail note
    guardrail: str              # "allowed" / "denied: ..." / "final"


@dataclass
class Trace:
    task: str
    steps: list[Step] = field(default_factory=list)
    final_answer: str | None = None
    stopped_reason: str = "completed"   # completed | max_steps | guardrail_stop

    def add(self, step: Step) -> None:
        self.steps.append(step)

    def action_sequence(self) -> list[str]:
        return [s.action for s in self.steps if s.action]

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)
