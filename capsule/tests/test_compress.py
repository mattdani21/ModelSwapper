"""G2.4 — Capsule v1 compression stage tests."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from capsule.capsule import Capsule  # noqa: E402
from capsule.compress import compress, estimate_tokens, growth_ratio  # noqa: E402


def _busy_capsule(iterations: int = 6, artifact_chars: int = 4000) -> Capsule:
    """A capsule with a long task history (grown append-only, like the real loop)."""
    c = Capsule.new(
        task_id="ablation-01",
        goal="Implement a bounded LRU cache with expiry. " * 8,
        constraints=["Must be stdlib-only", "Thread-safe", "O(1) ops"],
    )
    c.set_plan([{"step": f"step {i}", "status": "planned", "notes": ""} for i in range(20)])
    for i in range(iterations):
        c.add_artifact(f"solution.py", "def solve():\n" + ("    pass  # attempt %d\n" % i) * (artifact_chars // 30), kind="code")
        c.add_decision("review", f"retry {i}", f"tests failed, root cause guess #{i}: " + "x" * 300)
        c.complete_phase("code", "Qwen3-4B-Q4_K_M.gguf", outcome="ok", tokens=800 + i * 50)
        c.complete_phase("review", "grader", outcome="retry", tokens=0)
    return c


def test_budget_respected():
    c = _busy_capsule()
    raw = c.to_json()
    compressed = compress(c.data, budget_tokens=2000)
    compressed_tokens = estimate_tokens(json.dumps(compressed, sort_keys=True, ensure_ascii=False))
    assert compressed_tokens <= 2000, f"budget breached: {compressed_tokens} > 2000"
    # and it actually shrunk a lot
    assert compressed_tokens < estimate_tokens(raw) // 3


def test_verbatim_core_preserved():
    c = _busy_capsule()
    out = compress(c.data, budget_tokens=2000)
    assert out["task_id"] == c.data["task_id"]
    assert out["goal"] == c.data["goal"]
    assert out["constraints"] == c.data["constraints"]
    # newest artifact survives (content start intact)
    assert out["artifacts"][-1]["path"] == "solution.py"
    assert out["schema_version"] == c.data["schema_version"]


def test_round_trip_valid():
    c = _busy_capsule()
    out = compress(c.data, budget_tokens=4000)
    # the compressed dict must still load as a Capsule and validate
    round_trip = Capsule.from_json(json.dumps(out))
    problems = round_trip.validate(strict=False)
    assert problems == [], f"compressed capsule invalid: {problems}"


def test_sublinear_growth():
    """The property G2.4 exists for: tokens grow sub-linearly with task length."""
    sizes = []
    for n in (2, 4, 8, 12, 16):
        c = _busy_capsule(iterations=n)
        compressed = compress(c.data, budget_tokens=8000)
        sizes.append(estimate_tokens(json.dumps(compressed, sort_keys=True, ensure_ascii=False)))
    # growth from n=4 -> n=16 must be far below linear (linear would be ~4x)
    assert sizes[-1] < sizes[1] * 2.0, f"growth too steep: {sizes}"
    assert sizes[-1] <= 8000


def test_default_budget_is_8k():
    c = _busy_capsule(iterations=20, artifact_chars=6000)
    out = compress(c.data)  # no budget -> 8000 default
    tokens = estimate_tokens(json.dumps(out, sort_keys=True, ensure_ascii=False))
    assert tokens <= 8000
    assert out["meta"]["budget_tokens"] == 8000


def test_summarizer_hook_used_when_given():
    c = _busy_capsule(iterations=3)
    out = compress(c.data, budget_tokens=4000, summarizer=lambda entries, budget: "MODEL ROLLUP: " + str(len(entries)))
    assert out["decisions_log"][0]["decision"].startswith("MODEL ROLLUP")


def test_deterministic():
    c = _busy_capsule(iterations=5)
    a = compress(c.data, budget_tokens=3000)
    b = compress(c.data, budget_tokens=3000)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_growth_ratio_metric():
    c = _busy_capsule(iterations=8)
    raw_tokens = estimate_tokens(c.to_json())
    out = compress(c.data, budget_tokens=4000)
    ratio = growth_ratio(raw_tokens, estimate_tokens(json.dumps(out, sort_keys=True, ensure_ascii=False)))
    assert 0.0 < ratio < 1.0
