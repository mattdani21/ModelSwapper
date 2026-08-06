import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import solution
from solution import compound_interest, simple_interest


def _raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return
    raise AssertionError("expected %s" % exc.__name__)


def test_simple_basic():
    assert simple_interest(1000, 5, 2) == 1100.0


def test_compound_basic():
    assert compound_interest(1000, 5, 2) == 1102.5


def test_zero_rate():
    assert simple_interest(500, 0, 3) == 500.0
    assert compound_interest(500, 0, 3) == 500.0


def test_zero_years():
    assert simple_interest(500, 5, 0) == 500.0
    assert compound_interest(500, 5, 0) == 500.0


def test_simple_rounding():
    assert simple_interest(100, 3, 1) == 103.0


def test_validation():
    _raises(ValueError, simple_interest, 0, 5, 1)
    _raises(ValueError, compound_interest, -100, 5, 1)
    _raises(ValueError, simple_interest, 100, -1, 1)
    _raises(ValueError, compound_interest, 100, 5, -1)


def test_helpers_exist():
    assert callable(getattr(solution, "_validate", None))
    assert callable(getattr(solution, "_annual_rate", None))


def test_helper_signatures():
    assert list(inspect.signature(solution._validate).parameters) == ["principal", "rate", "years"]
    assert list(inspect.signature(solution._annual_rate).parameters) == ["rate"]


def test_math_not_duplicated():
    src = inspect.getsource(solution)
    assert src.count("principal must be positive") == 1
    assert src.count("rate / 100") == 1
