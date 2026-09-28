from genai_agent_lab.agent import parse_turn


def test_parse_action_turn():
    thought, name, arg, final = parse_turn(
        "Thought: list first.\nAction: list_instances[]"
    )
    assert thought == "list first."
    assert name == "list_instances"
    assert arg == ""
    assert final is None


def test_parse_action_with_arg():
    _, name, arg, _ = parse_turn("Thought: x\nAction: get_metrics[i-0a1b2c]")
    assert (name, arg) == ("get_metrics", "i-0a1b2c")


def test_parse_final_answer():
    thought, name, arg, final = parse_turn("Final Answer: 42% used.")
    assert final == "42% used."
    assert name is None


def test_parse_rejects_garbage():
    import pytest

    with pytest.raises(ValueError):
        parse_turn("I am confused and emit no protocol tokens")
