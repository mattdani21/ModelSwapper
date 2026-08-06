import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import invert_dict


def test_basic_invert():
    assert invert_dict({"a": [1, 2], "b": [2]}) == {1: ["a"], 2: ["a", "b"]}


def test_shared_value_keys():
    assert invert_dict({"x": [10], "y": [10, 20]}) == {10: ["x", "y"], 20: ["y"]}


def test_disjoint_values():
    assert invert_dict({"a": [1], "b": [2]}) == {1: ["a"], 2: ["b"]}


def test_same_value_repeated():
    assert invert_dict({"a": [1], "b": [1]}) == {1: ["a", "b"]}


def test_empty():
    assert invert_dict({}) == {}


def test_single_key():
    assert invert_dict({"k": [1]}) == {1: ["k"]}
