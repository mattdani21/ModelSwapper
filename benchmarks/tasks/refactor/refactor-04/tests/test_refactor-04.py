import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import solution
from solution import analyze, summarize


def test_summarize_basic():
    assert summarize([1, 2, 3, 4]) == {"mean": 2.5, "variance": 1.25}


def test_summarize_single_value():
    assert summarize([7]) == {"mean": 7.0, "variance": 0.0}


def test_summarize_empty():
    assert summarize([]) is None


def test_analyze_basic():
    assert analyze([2, 4, 6]) == {"mean": 4.0, "variance": 8.0 / 3.0, "count": 3}


def test_analyze_empty():
    assert analyze([]) is None


def test_helpers_exist():
    assert callable(getattr(solution, "_mean", None))
    assert callable(getattr(solution, "_variance", None))


def test_helper_signatures():
    assert list(inspect.signature(solution._mean).parameters) == ["values"]
    assert list(inspect.signature(solution._variance).parameters) == ["values"]


def test_math_not_duplicated():
    src = inspect.getsource(solution)
    assert src.count("sum(values) / len(values)") == 1
    assert src.count("** 2 for v in values") == 1
