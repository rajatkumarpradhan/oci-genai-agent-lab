import json
import subprocess
import sys


def test_cli_gate_passes():
    proc = subprocess.run(
        [sys.executable, "-m", "genai_agent_lab", "--golden", "fixtures/golden.json"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["gate"] == "pass"
    assert summary["passed"] == summary["cases"] == 4
