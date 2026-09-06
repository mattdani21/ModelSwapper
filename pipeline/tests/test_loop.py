"""Loop tests with the fake backend (CPU-only gates for Phase 1)."""
import hashlib
import json
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pipeline.loop import file_sha256, kv_checkpoint_name, run_task  # noqa: E402
from pipeline.prompts import parse_plan  # noqa: E402
from router.rules import DeterministicRouter  # noqa: E402
from runtime.fake_backend import FakeBackend  # noqa: E402

EXAMPLE = os.path.join("benchmarks", "tasks", "_EXAMPLE")
MODELS = {"reason": "fake-r.gguf", "code": "fake-c.gguf", "review": "fake-v.gguf"}


def _write_model(dirpath: str, name: str, content: bytes) -> str:
    """Tiny fake artifact bytes (never real weights) + its path."""
    path = os.path.join(dirpath, name)
    with open(path, "wb") as f:
        f.write(content)
    return path


def _read_task_texts() -> tuple:
    with open(os.path.join(EXAMPLE, "problem.md"), encoding="utf-8") as f:
        problem = f.read()
    with open(os.path.join(EXAMPLE, "starter", "solution.py"), encoding="utf-8") as f:
        starter = f.read()
    return problem, starter


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


def _retry_factory(backends, fail_restore=False):
    """Factory recording backends; code fails attempt 1, passes on retry."""
    def code(prompt):
        if "Reviewer feedback" in prompt:
            return _reference_text()
        return "def most_common_word(text):\n    return None\n"

    def critic(prompt):
        return "Implement the real algorithm; the candidate returns None."

    def factory(model_path: str, port: int) -> FakeBackend:
        name = os.path.basename(model_path)
        role = {"fake-r.gguf": "reason", "fake-c.gguf": "code", "fake-v.gguf": "review"}.get(name, "review")
        b = FakeBackend(model_path, callable_resp={
            "reason": lambda p: "1. plan\n2. implement", "code": code, "review": critic,
        }[role])
        b.fail_restore = fail_restore
        backends.append(b)
        return b
    return factory


def test_kv_cache_saves_after_first_code_attempt_restores_on_retries():
    """G1.3 (issue #16): with kv_cache_dir set, the CODE phase checkpoints
    after attempt 1 and restores the SAME checkpoint on every retry.
    SWAP-01: the name is content-addressed from the real artifact bytes."""
    backends = []
    with tempfile.TemporaryDirectory() as kvdir, tempfile.TemporaryDirectory() as modeldir:
        code_model = _write_model(modeldir, "fake-c.gguf", b"fake code weights (no real model)")
        models = dict(MODELS, code=code_model)
        r = run_task(EXAMPLE, models, _retry_factory(backends),
                     max_iterations=3, kv_cache_dir=kvdir)
        # the checkpoint name is deterministic per (model content, task, plan)
        # — rebuild it from the same inputs the loop used (task files + empty
        # plan); the fake REASON phase returns exactly this plan text
        problem, starter = _read_task_texts()
        expected = kv_checkpoint_name(file_sha256(code_model), "_EXAMPLE",
                                      problem, starter, "1. plan\n2. implement")
    assert r.passed is True
    assert r.iterations == 2
    code_backends = [b for b in backends if b.model_path.endswith("fake-c.gguf")]
    assert len(code_backends) == 2  # one fresh server per code phase
    ops = code_backends[0].kv_ops + code_backends[1].kv_ops
    saves = [op for op in ops if op[0] == "save"]
    restores = [op for op in ops if op[0] == "restore"]
    assert len(saves) == 1, f"attempt 1 must save exactly once, got {saves}"
    assert len(restores) == 1, f"retry must restore exactly once, got {restores}"
    assert saves[0][1] == restores[0][1], "retry must restore the attempt-1 checkpoint"
    assert saves[0][1] == expected
    # phase records carry the prefill + KV facts
    code_phases = [p for p in r.phases if p["role"] == "code"]
    assert code_phases[0]["kv_saved"] is True and code_phases[0]["kv_used"] is False
    assert code_phases[1]["kv_used"] is True and code_phases[1]["kv_saved"] is False
    assert code_phases[0]["prompt_n"] == 300 and code_phases[1]["prompt_n"] == 128


def test_kv_cache_disabled_passes_no_kv_args():
    backends = []
    r = run_task(EXAMPLE, MODELS, _retry_factory(backends), max_iterations=3)
    assert r.passed is True
    code_backends = [b for b in backends if b.model_path.endswith("fake-c.gguf")]
    assert all(b.kv_ops == [] for b in code_backends), "no kv ops without kv_cache_dir"
    code_phases = [p for p in r.phases if p["role"] == "code"]
    assert all(p["kv_used"] is False and p["kv_saved"] is False for p in code_phases)


def test_kv_restore_failure_falls_back_to_full_prefill():
    """Correctness first: a failed restore must not fail the phase — the
    backend falls back to a full prefill and the loop still completes."""
    backends = []
    with tempfile.TemporaryDirectory() as kvdir, tempfile.TemporaryDirectory() as modeldir:
        code_model = _write_model(modeldir, "fake-c.gguf", b"fake code weights (no real model)")
        models = dict(MODELS, code=code_model)
        r = run_task(EXAMPLE, models, _retry_factory(backends, fail_restore=True),
                     max_iterations=3, kv_cache_dir=kvdir)
    assert r.passed is True, f"restore failure must not break the retry: {r.error}"
    retry = [p for p in r.phases if p["role"] == "code"][1]
    assert retry["kv_used"] is False, "failed restore must report kv_used=False"
    assert retry["prompt_n"] == 300, "fallback must full-prefill (no cache benefit)"


def test_kv_checkpoint_name_content_addressed_fixtures():
    """SWAP-01 AC1 fixtures: same byte count with different content gives
    different names; identical bytes at a different path give the same name;
    the digest is the full 64-hex SHA-256 of the artifact."""
    with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
        same_dir_a = _write_model(d1, "code-a.gguf", b"x" * 4096)
        same_size_b = _write_model(d1, "code-b.gguf", b"y" * 4096)  # same bytes count
        other_path_a = _write_model(d2, "code-a.gguf", b"x" * 4096)  # identical bytes
        d_a = file_sha256(same_dir_a)
        assert d_a == file_sha256(other_path_a), "digest follows content, not path"
        assert d_a != file_sha256(same_size_b), "same size, different bytes -> different digest"
        assert re.fullmatch(r"[0-9a-f]{64}", d_a), "full SHA-256 hex digest"
        n_a = kv_checkpoint_name(d_a, "t1", "problem", "starter", "plan")
        assert n_a == kv_checkpoint_name(file_sha256(other_path_a), "t1", "problem",
                                         "starter", "plan")
        assert n_a != kv_checkpoint_name(file_sha256(same_size_b), "t1", "problem",
                                         "starter", "plan")
        assert n_a.startswith("kv-") and n_a.endswith(".bin")
        assert re.fullmatch(r"kv-[0-9a-f]{64}\.bin", n_a), "entire digest in the name"


def test_kv_checkpoint_name_deterministic_and_sensitive():
    """Same inputs -> same name; every identity input (task/problem/starter/
    plan) participates; the model artifact digest is never substituted."""
    with tempfile.TemporaryDirectory() as d:
        digest = file_sha256(_write_model(d, "code.gguf", b"fake weights (no real model)"))
    base = kv_checkpoint_name(digest, "t1", "problem", "starter", "plan")
    assert base == kv_checkpoint_name(digest, "t1", "problem", "starter", "plan")
    assert base != kv_checkpoint_name(digest, "t1", "problem", "starter", "plan2")
    assert base != kv_checkpoint_name(digest, "t2", "problem", "starter", "plan")
    assert base != kv_checkpoint_name(digest, "t1", "problem2", "starter", "plan")
    assert base != kv_checkpoint_name(digest, "t1", "problem", "starter2", "plan")
    assert base != kv_checkpoint_name("0" * 64, "t1", "problem", "starter", "plan")
    assert kv_checkpoint_name(None, "t1", "problem", "starter", "plan") is None
    assert kv_checkpoint_name("", "t1", "problem", "starter", "plan") is None


def test_kv_checkpoint_name_canonical_identity_object():
    """SWAP-01 contract pin: name = kv-<sha256(sorted JSON identity, utf-8)>.bin
    with identity_format_version 1 — locks the canonical serialization so any
    future drift breaks loudly."""
    digest = "ab" * 32
    identity = {
        "identity_format_version": 1,
        "model_sha256": digest,
        "task_id": "t1",
        "problem": "problem",
        "starter": "starter",
        "plan": "plan",
    }
    canonical = json.dumps(identity, sort_keys=True, separators=(",", ":"))
    expected = "kv-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest() + ".bin"
    assert kv_checkpoint_name(digest, "t1", "problem", "starter", "plan") == expected


def test_kv_checkpoint_disabled_when_artifact_missing():
    """SWAP-01 AC2: an unreadable/missing model artifact disables checkpoint
    restore/save (no kv ops at all) while normal generation with retries
    still completes — no empty/all-zero digest is ever substituted."""
    backends = []
    with tempfile.TemporaryDirectory() as kvdir, tempfile.TemporaryDirectory() as modeldir:
        missing = os.path.join(modeldir, "does-not-exist", "fake-c.gguf")
        models = dict(MODELS, code=missing)
        assert file_sha256(missing) is None
        r = run_task(EXAMPLE, models, _retry_factory(backends),
                     max_iterations=3, kv_cache_dir=kvdir)
    assert r.passed is True, f"normal generation must still work: {r.error}"
    assert r.iterations == 2
    code_backends = [b for b in backends if b.model_path.endswith("fake-c.gguf")]
    assert len(code_backends) == 2
    assert all(b.kv_ops == [] for b in code_backends), \
        "missing artifact must disable both save and restore"
    code_phases = [p for p in r.phases if p["role"] == "code"]
    assert all(p["kv_used"] is False and p["kv_saved"] is False for p in code_phases)


def test_code_model_digest_computed_once_per_run(monkeypatch):
    """SWAP-01 AC3: the model artifact is hashed at most once per run_task
    call — a retry (second code attempt) must never rehash the file."""
    import pipeline.loop as loop
    calls = {"n": 0}
    real = loop.file_sha256

    def counting(path):
        calls["n"] += 1
        return real(path)

    monkeypatch.setattr(loop, "file_sha256", counting)
    backends = []
    with tempfile.TemporaryDirectory() as kvdir, tempfile.TemporaryDirectory() as modeldir:
        code_model = _write_model(modeldir, "fake-c.gguf", b"fake code weights (no real model)")
        r = run_task(EXAMPLE, dict(MODELS, code=code_model), _retry_factory(backends),
                     max_iterations=3, kv_cache_dir=kvdir)
    assert r.passed is True
    assert r.iterations == 2, "test needs a retry to prove no rehash per attempt"
    assert calls["n"] == 1, f"digest must be computed exactly once per run, got {calls['n']}"


def test_precomputed_digest_never_rehashes(monkeypatch):
    """SWAP-01 AC3: when run_pipeline hands in a digest computed once per CLI
    run, the loop must not touch the artifact file at all."""
    import pipeline.loop as loop

    def boom(path):
        raise AssertionError("loop must not hash when the caller supplied the identity")

    monkeypatch.setattr(loop, "file_sha256", boom)
    supplied = hashlib.sha256(b"fake code weights (no real model)").hexdigest()
    backends = []
    with tempfile.TemporaryDirectory() as kvdir, tempfile.TemporaryDirectory() as modeldir:
        code_model = _write_model(modeldir, "fake-c.gguf", b"fake code weights (no real model)")
        r = run_task(EXAMPLE, dict(MODELS, code=code_model), _retry_factory(backends),
                     max_iterations=3, kv_cache_dir=kvdir,
                     model_sha256s={"code": supplied})
        problem, starter = _read_task_texts()
        expected = kv_checkpoint_name(supplied, "_EXAMPLE", problem, starter,
                                      "1. plan\n2. implement")
    assert r.passed is True
    assert r.iterations == 2
    code_backends = [b for b in backends if b.model_path.endswith("fake-c.gguf")]
    ops = code_backends[0].kv_ops + code_backends[1].kv_ops
    assert ops[0][1] == expected, "precomputed identity must produce the same name"


def test_kv_cache_run_private_namespace_no_cross_run_reuse():
    """SWAP-01: two separate run_task calls against the SAME kv_cache_dir
    must land in different private namespaces (a second run can never
    restore the first run's checkpoint files)."""
    with tempfile.TemporaryDirectory() as kvdir, tempfile.TemporaryDirectory() as modeldir:
        code_model = _write_model(modeldir, "fake-c.gguf", b"fake code weights (no real model)")
        models = dict(MODELS, code=code_model)

        def stub_factory(backends):
            def factory(model_path: str, port: int) -> FakeBackend:
                name = os.path.basename(model_path)
                role = {"fake-r.gguf": "reason", "fake-c.gguf": "code",
                        "fake-v.gguf": "review"}.get(name, "review")
                b = FakeBackend(model_path, callable_resp={
                    "reason": lambda p: "1. plan\n2. implement",
                    "code": lambda p: "def most_common_word(text):\n    return None\n",
                    "review": lambda p: "no",
                }[role])
                backends.append(b)
                return b
            return factory

        # two independent runs, same task, same base cache dir
        run_task(EXAMPLE, models, stub_factory([]), max_iterations=1, kv_cache_dir=kvdir)
        run_task(EXAMPLE, models, stub_factory([]), max_iterations=1, kv_cache_dir=kvdir)
        namespaces = sorted(d for d in os.listdir(kvdir) if d.startswith("run-"))
        assert len(namespaces) == 2, f"each run needs its own private namespace: {namespaces}"
        assert namespaces[0] != namespaces[1]






