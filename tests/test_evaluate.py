import json

from genai_agent_lab.evaluate import run_golden


def test_golden_suite_passes():
    results = run_golden("fixtures/golden.json")
    assert results and all(r.passed for r in results)


def test_eval_detects_tampered_expectation(tmp_path):
    golden = json.load(open("fixtures/golden.json"))
    golden["cases"][0]["expected_actions"] = ["get_budget[]"]  # wrong on purpose
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(golden))
    results = run_golden(str(p))
    assert not results[0].passed
