import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import sum_even_numbers


def test_mixed_list():
    assert sum_even_numbers([1, 2, 3, 4]) == 6


def test_all_even():
    assert sum_even_numbers([2, 4, 6]) == 12


def test_all_odd():
    assert sum_even_numbers([1, 3, 5]) == 0


def test_empty():
    assert sum_even_numbers([]) == 0


def test_zero():
    assert sum_even_numbers([0]) == 0


def test_negatives():
    assert sum_even_numbers([-2, 3, -4]) == -6
