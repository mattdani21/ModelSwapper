import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from solution import spiral_order


def test_3x3():
    assert spiral_order([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [1, 2, 3, 6, 9, 8, 7, 4, 5]


def test_3x4():
    assert spiral_order([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]) == [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]


def test_2x2():
    assert spiral_order([[1, 2], [3, 4]]) == [1, 2, 4, 3]


def test_1x1():
    assert spiral_order([[1]]) == [1]


def test_single_row():
    assert spiral_order([[1, 2, 3, 4]]) == [1, 2, 3, 4]


def test_single_column():
    assert spiral_order([[1], [2], [3]]) == [1, 2, 3]


def test_empty_matrix():
    assert spiral_order([]) == []


def test_empty_row():
    assert spiral_order([[]]) == []


def test_2x3():
    assert spiral_order([[1, 2, 3], [4, 5, 6]]) == [1, 2, 3, 6, 5, 4]


def test_4x4():
    matrix = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 16],
    ]
    assert spiral_order(matrix) == [1, 2, 3, 4, 8, 12, 16, 15, 14, 13, 9, 5, 6, 7, 11, 10]


def test_ragged_raises():
    with pytest.raises(ValueError):
        spiral_order([[1, 2], [3]])
