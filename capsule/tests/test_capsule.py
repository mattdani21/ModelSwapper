import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from capsule.capsule import Capsule, CapsuleError  # noqa: E402


def test_new_capsule_validates():
    c = Capsule.new("t1", "goal here", constraints=["no cloud"])
    assert c.validate() == []
    assert c.data["schema_version"] == "0.1.0"
    assert c.data["meta"]["run_id"]


def test_roundtrip_byte_identical():
    c = Capsule.new("t1", "goal", constraints=["no cloud"])
    c.set_plan([{"step": "plan a", "status": "done", "notes": ""}])
    c.add_artifact("solution.py", "print('hi')")
    c.add_decision("reason", "use pytest", "deterministic grading")
    c.complete_phase("reason", "qwen3-4b", outcome="ok", swap_in_ms=1500.0, tokens=120)
    s1 = c.to_json()
    c2 = Capsule.from_json(s1)
    assert c2.to_json() == s1  # byte-identical round trip


def test_load_save_roundtrip(tmp_path):
    c = Capsule.new("t2", "g")
    p = tmp_path / "cap.json"
    c.save(str(p))
    c2 = Capsule.load(str(p))
    assert c2.to_json() == c.to_json()


def test_validation_rejects_incomplete_capsule():
    bad = Capsule.from_json(json.dumps({"schema_version": "0.1.0", "task_id": "x"}))
    assert bad.validate() != []


def test_validation_rejects_wrong_schema_version():
    c = Capsule.new("t3", "g")
    c.data["schema_version"] = "9.9.9"
    assert any("schema_version" in p for p in c.validate())


def test_append_only_growth():
    c = Capsule.new("t4", "g")
    c.add_decision("code", "d1", "r1")
    c.add_decision("code", "d2", "r2")
    c.add_constraint("keep it local")
    assert len(c.data["decisions_log"]) == 2
    assert len(c.data["constraints"]) == 1


def test_invalid_outcome_rejected():
    c = Capsule.new("t5", "g")
    try:
        c.complete_phase("code", "m", outcome="maybe")
        raise AssertionError("should have raised")
    except CapsuleError:
        pass


def test_invalid_artifact_kind_rejected():
    c = Capsule.new("t6", "g")
    try:
        c.add_artifact("a", "b", kind="binary")
        raise AssertionError("should have raised")
    except CapsuleError:
        pass


def test_phase_history_records_capsule_size():
    c = Capsule.new("t7", "g")
    c.complete_phase("code", "m", outcome="ok", tokens=10)
    entry = c.data["phase_history"][-1]
    assert entry["capsule_bytes"] > 0
    assert entry["capsule_tokens_est"] > 0
