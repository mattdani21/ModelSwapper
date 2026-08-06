import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from grader import grade, grade_reference, grade_starter, task_dir_ok, verify_task

EXAMPLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tasks", "_EXAMPLE")


def test_example_structural_ok():
    assert task_dir_ok(EXAMPLE) == []


def test_example_starter_red():
    r = grade_starter(EXAMPLE)
    assert r["pass"] is False
    assert r["tests_total"] > 0


def test_example_reference_green():
    r = grade_reference(EXAMPLE)
    assert r["pass"] is True
    assert r["tests_passed"] == r["tests_total"] >= 5


def test_example_verify_ok():
    assert verify_task(EXAMPLE)["ok"] is True


def test_grade_requires_exactly_one_source():
    try:
        grade(EXAMPLE)
        raise AssertionError("should have raised")
    except ValueError:
        pass
