"""CLI: run golden-trace evaluation and print a JSON summary."""

from __future__ import annotations

import argparse
import json
import os

from .evaluate import run_golden


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline ReAct agent lab evaluation")
    default_golden = os.path.join(os.path.dirname(__file__), "..", "..", "fixtures", "golden.json")
    parser.add_argument("--golden", default=os.path.abspath(default_golden))
    args = parser.parse_args()

    results = run_golden(args.golden)
    passed = sum(1 for r in results if r.passed)
    summary = {
        "suite": "oci-genai-agent-lab golden traces",
        "cases": len(results),
        "passed": passed,
        "gate": "pass" if passed == len(results) else "fail",
        "details": [
            {
                "task": r.task,
                "passed": r.passed,
                "actions": r.actual_actions,
                "stopped_reason": r.stopped_reason,
            }
            for r in results
        ],
    }
    print(json.dumps(summary, indent=2))
    return 0 if summary["gate"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
