import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import flatten


def test_one_level():
    assert flatten([[1, 2], [3, 4]]) == [1, 2, 3, 4]


def test_deeply_nested():
    assert flatten([1, [2, [3, 4]]]) == [1, 2, 3, 4]


def test_three_levels():
    assert flatten([[1, [2, [3]]]]) == [1, 2, 3]


def test_empty_nested():
    assert flatten([[], [[]]]) == []


def test_flat_input():
    assert flatten([1, 2, 3]) == [1, 2, 3]


def test_empty():
    assert flatten([]) == []
