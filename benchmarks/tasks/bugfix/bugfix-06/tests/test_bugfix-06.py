import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import merge_intervals


def test_basic_merge():
    assert merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]


def test_touching_intervals_merge():
    assert merge_intervals([[1, 2], [2, 3]]) == [[1, 3]]


def test_touching_reversed_order():
    assert merge_intervals([[1, 4], [4, 5]]) == [[1, 5]]


def test_disjoint_intervals():
    assert merge_intervals([[1, 2], [3, 4]]) == [[1, 2], [3, 4]]


def test_unsorted_input():
    assert merge_intervals([[3, 4], [1, 2], [2, 5]]) == [[1, 5]]


def test_empty():
    assert merge_intervals([]) == []


def test_single():
    assert merge_intervals([[5, 5]]) == [[5, 5]]
