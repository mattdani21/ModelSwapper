import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import two_sum


def test_basic():
    assert two_sum([2, 7, 11, 15], 9) == (0, 1)


def test_not_sorted():
    assert two_sum([3, 2, 4], 6) == (1, 2)


def test_duplicate_values():
    assert two_sum([3, 3], 6) == (0, 1)


def test_no_solution():
    assert two_sum([1, 2, 3], 10) is None


def test_single_element():
    assert two_sum([5], 5) is None


def test_empty():
    assert two_sum([], 0) is None


def test_no_self_pair():
    assert two_sum([3, 1], 6) is None


def test_negatives():
    assert two_sum([-3, 4, 3, 90], 0) == (0, 2)


def test_target_zero():
    assert two_sum([1, -1, 2], 0) == (0, 1)


def test_pair_at_end():
    assert two_sum([1, 2, 3, 4, 5], 9) == (3, 4)
