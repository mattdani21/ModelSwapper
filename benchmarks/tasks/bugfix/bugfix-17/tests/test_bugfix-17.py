import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import next_permutation


def test_basic():
    assert next_permutation([1, 2, 3]) == [1, 3, 2]


def test_descending():
    assert next_permutation([3, 2, 1]) == [1, 2, 3]


def test_duplicate_simple():
    assert next_permutation([1, 1, 5]) == [1, 5, 1]


def test_duplicate_two():
    assert next_permutation([1, 2, 2]) == [2, 1, 2]


def test_duplicate_three():
    assert next_permutation([2, 1, 2]) == [2, 2, 1]


def test_duplicate_tricky():
    assert next_permutation([1, 2, 1]) == [2, 1, 1]


def test_duplicate_four():
    assert next_permutation([1, 3, 2, 1]) == [2, 1, 1, 3]


def test_single():
    assert next_permutation([1]) == [1]


def test_empty():
    assert next_permutation([]) == []
