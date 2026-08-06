import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import second_largest


def test_basic():
    assert second_largest([3, 1, 4, 1, 5, 9, 2, 6]) == 6


def test_with_duplicates():
    assert second_largest([5, 5, 4]) == 4


def test_all_equal():
    assert second_largest([10, 10, 10]) is None


def test_single_element():
    assert second_largest([7]) is None


def test_empty():
    assert second_largest([]) is None


def test_two_distinct():
    assert second_largest([1, 2]) == 1


def test_negatives():
    assert second_largest([-1, -2, -3]) == -2


def test_zero_and_duplicates():
    assert second_largest([0, 0, 1]) == 0


def test_unsorted_mixed():
    assert second_largest([1, 100, 50, 50, 2]) == 50
