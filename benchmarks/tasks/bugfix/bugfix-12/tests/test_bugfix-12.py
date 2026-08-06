import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import top_k


def test_basic():
    assert top_k([1, 1, 1, 2, 2, 3], 2) == [1, 2]


def test_tie_by_first_occurrence():
    assert top_k([1, 1, 2, 2, 3, 3, 3], 2) == [3, 1]


def test_frequency_order():
    assert top_k([3, 3, 3, 1, 1, 2], 2) == [3, 1]


def test_negative_and_positive():
    assert top_k([4, 4, 5, 5, 6, 6, 6], 2) == [6, 4]


def test_distinct():
    assert top_k([1, 2, 3, 4], 2) == [1, 2]


def test_single():
    assert top_k([5], 1) == [5]


def test_k_equals_distinct():
    assert top_k([1, 1, 2], 3) == [1, 2]
