from genai_agent_lab.agent import ReActAgent
from genai_agent_lab.guardrails import Guardrails
from genai_agent_lab.llm import ScriptedPlanner


def run(task, **kw):
    return ReActAgent(ScriptedPlanner(task), Guardrails(**kw)).run(task)


def test_idle_instance_trace():
    tr = run("find the idle instance")
    assert tr.action_sequence() == ["list_instances[]", "get_metrics[i-0a1b2c]"]
    assert "i-0a1b2c" in tr.final_answer
    assert tr.stopped_reason == "completed"


def test_unknown_task_falls_back_safely():
    tr = run("write me a poem about Kubernetes")
    assert tr.action_sequence() == []
    assert "scripted path" in tr.final_answer


def test_step_cap_stops_loop():
    # max_steps=1 cuts off mid-script: one action executes, then the cap hits.
    tr = run("find the idle instance", max_steps=1)
    assert tr.stopped_reason == "max_steps"
    assert "step cap" in tr.final_answer


def test_guardrail_stop_on_denied_action():
    class EvilPlanner:
        def complete(self, prompt):
            return "Thought: nuke it\nAction: terminate_instance[i-0a1b2c]"

    tr = ReActAgent(EvilPlanner(), Guardrails()).run("anything")
    assert tr.stopped_reason == "guardrail_stop"
    assert "denied" in tr.final_answer


def test_observation_is_scrubbed():
    tr = run("scan error logs")
    obs = tr.steps[1].observation or ""
    assert "oncall@example.com" not in obs
