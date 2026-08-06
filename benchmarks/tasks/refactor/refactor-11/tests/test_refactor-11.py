import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import solution
from solution import classify, letter_grade


def _raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return
    raise AssertionError("expected %s" % exc.__name__)


def test_letter_boundaries():
    assert letter_grade(100) == "A"
    assert letter_grade(90) == "A"
    assert letter_grade(89) == "B"
    assert letter_grade(80) == "B"
    assert letter_grade(79) == "C"
    assert letter_grade(70) == "C"
    assert letter_grade(69) == "D"
    assert letter_grade(60) == "D"
    assert letter_grade(59) == "F"
    assert letter_grade(0) == "F"


def test_classify_boundaries():
    assert classify(95) == "excellent"
    assert classify(85) == "good"
    assert classify(75) == "fair"
    assert classify(65) == "poor"
    assert classify(55) == "failing"


def test_classify_matches_letter_grade():
    labels = {"A": "excellent", "B": "good", "C": "fair", "D": "poor", "F": "failing"}
    for score in (100, 90, 89, 80, 79, 70, 69, 60, 59, 0):
        assert classify(score) == labels[letter_grade(score)]


def test_range_validation():
    _raises(ValueError, letter_grade, -1)
    _raises(ValueError, classify, 101)


def test_helpers_exist():
    assert callable(getattr(solution, "_check_score", None))
    assert callable(getattr(solution, "_score_to_grade", None))


def test_helper_signatures():
    assert list(inspect.signature(solution._check_score).parameters) == ["score"]
    assert list(inspect.signature(solution._score_to_grade).parameters) == ["score"]


def test_boundaries_not_duplicated():
    src = inspect.getsource(solution)
    assert src.count("score >= 90") == 1
    assert src.count("score out of range") == 1
