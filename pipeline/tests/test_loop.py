"""Loop tests with the fake backend (CPU-only gates for Phase 1)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pipeline.loop import run_task  # noqa: E402
from pipeline.prompts import parse_plan  # noqa: E402
from router.rules import DeterministicRouter  # noqa: E402
from runtime.fake_backend import FakeBackend  # noqa: E402

EXAMPLE = os.path.join("benchmarks", "tasks", "_EXAMPLE")
MODELS = {"reason": "fake-r.gguf", "code": "fake-c.gguf", "review": "fake-v.gguf"}


def _reference_text() -> str:
    with open(os.path.join(EXAMPLE, "reference", "solution.py")) as f:
        return f.read()


def _make_factory(role_behaviour: dict):
    """role_behaviour: {'code': callable(prompt)->str, ...}"""
    def factory(model_path: str, port: int) -> FakeBackend:
        name = os.path.basename(model_path)
        role = {"fake-r.gguf": "reason", "fake-c.gguf": "code", "fake-v.gguf": "review"}.get(name, "review")
        return FakeBackend(model_path, callable_resp=role_behaviour.get(role))
    return factory


def test_passes_on_first_attempt():
    def code(prompt):
        return _reference_text()

    r = run_task(EXAMPLE, MODELS, _make_factory({"code": code}), max_iterations=3)
    assert r.passed is True
    assert r.iterations == 1
    roles = [p["role"] for p in r.phases]
    assert roles == ["reason", "code", "review"]
    assert r.tests_passed == r.tests_total >= 5
    assert r.capsule_bytes > 0


def test_retry_loop_with_critic_feedback():
    calls = {"n": 0}

    def code(prompt):
        calls["n"] += 1
        if "Reviewer feedback" in prompt:
            return _reference_text()
        return "def most_common_word(text):\n    return None\n"

    def critic(prompt):
        return "The candidate returns None instead of the most frequent word. Implement the real algorithm."

    r = run_task(EXAMPLE, MODELS, _make_factory({"code": code, "review": critic}), max_iterations=3)
    assert r.passed is True
    assert calls["n"] == 2
    roles = [p["role"] for p in r.phases]
    assert "critic" in roles
    assert r.iterations == 2


def test_budget_exhaustion_fails():
    def code(prompt):
        return "def most_common_word(text):\n    return None\n"

    r = run_task(EXAMPLE, MODELS, _make_factory({"code": code}), max_iterations=2)
    assert r.passed is False
    assert r.error and "budget" in r.error
    assert r.tests_total > 0


def test_router_transitions():
    rt = DeterministicRouter(max_iterations=2)
    assert rt.initial_phase() == "reason"
    assert rt.next_phase("reason", False, 0) == "code"
    assert rt.next_phase("code", False, 1) == "review"
    assert rt.next_phase("review", False, 1) == "code"  # retry within budget
    assert rt.next_phase("review", False, 2) == "done"  # budget exhausted
    assert rt.next_phase("review", True, 1) == "done"   # passed
    assert rt.model_for("critic", MODELS) == MODELS["review"]


def test_parse_plan_extracts_steps():
    steps = parse_plan("1. read input\n2. validate\n- handle empty\n")
    assert len(steps) == 3
    assert steps[0]["step"] == "read input"
    assert steps[0]["status"] == "planned"


def test_parse_plan_falls_back_to_raw():
    steps = parse_plan("just implement it carefully")
    assert len(steps) == 1
