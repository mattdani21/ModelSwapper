import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import reverse_list


def test_reversed_values():
    assert reverse_list([1, 2, 3]) == [3, 2, 1]


def test_four_elements():
    assert reverse_list([1, 2, 3, 4]) == [4, 3, 2, 1]


def test_empty():
    assert reverse_list([]) == []


def test_single():
    assert reverse_list([7]) == [7]


def test_input_not_mutated():
    original = [1, 2, 3]
    reverse_list(original)
    assert original == [1, 2, 3]


def test_repeated_calls_do_not_mutate():
    original = ["a", "b", "c"]
    reverse_list(original)
    reverse_list(original)
    assert original == ["a", "b", "c"]
