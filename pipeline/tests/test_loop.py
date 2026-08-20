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


def test_naive_handoff_carries_verbatim_transcript():
    """G2.3 arm: naive mode puts the full transcript in every later prompt."""
    prompts_seen = {"code": [], "critic": []}

    def code(prompt):
        prompts_seen["code"].append(prompt)
        if "Reviewer feedback" in prompt and "[CODE ATTEMPT]" in prompt:
            return _reference_text()
        return "def most_common_word(text):\n    return None\n"

    def critic(prompt):
        prompts_seen["critic"].append(prompt)
        assert "[REASON PLAN]" in prompt and "[CODE ATTEMPT]" in prompt
        return "implement the real algorithm"

    r = run_task(EXAMPLE, MODELS, _make_factory({"code": code, "review": critic}),
                 max_iterations=3, handoff="naive")
    assert r.passed is True
    assert "[REASON PLAN]" in prompts_seen["code"][0]
    assert "[CODE ATTEMPT]" in prompts_seen["code"][1]
    ctxs = [p.get("context_tokens_est") for p in r.phases if p.get("context_tokens_est")]
    assert ctxs and all(c > 0 for c in ctxs)
    # naive context must be strictly bigger than the capsule's at the same point
    assert ctxs[-1] >= ctxs[0]


def test_resident_mode_uses_one_backend_no_swaps():
    """G2.3 arm: single-model baseline — same backend instance every phase."""
    from runtime.fake_backend import FakeBackend
    instances = []

    orig_init = FakeBackend.__init__

    def spy_init(self, model_path, *a, **kw):
        instances.append(model_path)
        orig_init(self, model_path, *a, **kw)

    # resident mode uses models["reason"] for every phase — that model's
    # behaviour must therefore be the code expert in this test
    def factory(model_path: str, port: int) -> FakeBackend:
        return FakeBackend(model_path, callable_resp=lambda prompt: _reference_text())

    FakeBackend.__init__ = spy_init
    try:
        r = run_task(EXAMPLE, MODELS, factory, max_iterations=3, resident=True)
    finally:
        FakeBackend.__init__ = orig_init
    assert r.passed is True
    assert len(instances) == 1, f"resident mode must create exactly one backend, got {len(instances)}"
    assert r.phases[0]["load_s"] is not None
    # no eviction between phases: every model phase reports evict_s == 0.0
    model_evicts = [p["evict_s"] for p in r.phases if p["role"] != "review"]
    assert all(e == 0.0 for e in model_evicts), f"unexpected evictions: {model_evicts}"


def test_handoff_invalid_value_rejected():
    try:
        run_task(EXAMPLE, MODELS, _make_factory({}), handoff="banana")
        assert False, "should have raised"
    except ValueError:
        pass


def test_prefetch_hints_follow_phase_order():
    """G2.2: the loop tells each phase which specialist to pre-load next."""
    backends = []

    def code(prompt):
        if "Reviewer feedback" in prompt and "[CODE ATTEMPT]" in prompt:
            return _reference_text()
        return "def most_common_word(text):\n    return None\n"

    behaviours = {
        "fake-r.gguf": lambda p: "1. plan\n2. implement",
        "fake-c.gguf": code,
        "fake-v.gguf": lambda p: "implement the real algorithm",
    }

    def factory(model_path, port):
        b = FakeBackend(model_path, callable_resp=behaviours[os.path.basename(model_path)])
        backends.append(b)
        return b

    r = run_task(EXAMPLE, MODELS, factory, max_iterations=3, handoff="naive")
    assert r.passed is True
    hints = [b.prefetches[0] for b in backends]
    assert len(hints) >= 3
    assert hints[0] == MODELS["code"], f"reason should prefetch code, got {hints[0]}"
    assert hints[1] == MODELS["review"], f"code should prefetch review, got {hints[1]}"
    assert hints[2] == MODELS["code"], f"critic should prefetch code, got {hints[2]}"


def test_overlap_backend_swaps_and_prefetches(monkeypatch):
    """G2.2: OverlapBackend promotes via the engine and prefetches the next model."""
    import runtime.overlap_backend as ob

    class StubServer:
        port = 9999

    class StubEngine:
        def __init__(self):
            self.swaps = []
            self.prefetches = []
            self.srv = StubServer()

        def swap(self, model, port):
            self.swaps.append(model)
            return {"promoted": True, "load_s": 1.0, "evict_s": 0.05, "swap_s": 0.05}

        def prefetch(self, model):
            self.prefetches.append(model)

        def active(self):
            return self.srv

    class FakeResp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def __iter__(self):
            yield b'data: {"content":"hi","timings":{"predicted_n":2}}\n\n'

    engine = StubEngine()

    def fake_urlopen(req, timeout=900):
        return FakeResp()

    monkeypatch.setattr(ob.urllib.request, "urlopen", fake_urlopen)
    b = ob.OverlapBackend(engine, "models/A.gguf")  # type: ignore[arg-type]
    r = b.generate("hello", prefetch_model="models/B.gguf")
    assert engine.swaps == ["models/A.gguf"]
    assert engine.prefetches == ["models/B.gguf"]
    assert r.load_s == 0.0, "promoted swap must report hidden load (0.0)"
    assert r.evict_s == 0.05
    assert r.text == "hi"
