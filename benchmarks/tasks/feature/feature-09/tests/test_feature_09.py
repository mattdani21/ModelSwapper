import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from solution import merge_intervals


def test_basic_merge():
    assert merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]


def test_touching_merge():
    assert merge_intervals([[1, 4], [4, 5]]) == [[1, 5]]


def test_unsorted_input():
    assert merge_intervals([[1, 4], [0, 2]]) == [[0, 4]]


def test_contained_interval():
    assert merge_intervals([[1, 10], [2, 3]]) == [[1, 10]]


def test_empty():
    assert merge_intervals([]) == []


def test_single_interval():
    assert merge_intervals([[5, 5]]) == [[5, 5]]


def test_disjoint_sorted_output():
    result = merge_intervals([[10, 12], [1, 2], [5, 6]])
    assert result == [[1, 2], [5, 6], [10, 12]]


def test_overlapping_chain():
    assert merge_intervals([[1, 2], [2, 3], [3, 4]]) == [[1, 4]]


def test_invalid_raises():
    with pytest.raises(ValueError):
        merge_intervals([[3, 1]])


def test_zero_length_and_negative():
    assert merge_intervals([[0, 0], [-2, -1]]) == [[-2, -1], [0, 0]]
