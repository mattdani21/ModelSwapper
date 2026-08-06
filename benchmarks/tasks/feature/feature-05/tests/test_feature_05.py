import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import invert_dict


def test_basic():
    assert invert_dict({"a": 1, "b": 2}) == {1: ["a"], 2: ["b"]}


def test_duplicate_values():
    assert invert_dict({"a": 1, "b": 1}) == {1: ["a", "b"]}


def test_empty():
    assert invert_dict({}) == {}


def test_string_values():
    assert invert_dict({"x": "y"}) == {"y": ["x"]}


def test_insertion_order_preserved():
    assert invert_dict({"z": 1, "a": 1, "m": 1}) == {1: ["z", "a", "m"]}


def test_original_not_modified():
    original = {"a": 1, "b": 2}
    invert_dict(original)
    assert original == {"a": 1, "b": 2}


def test_mixed_types():
    result = invert_dict({1: "one", 2: "two"})
    assert result == {"one": [1], "two": [2]}


def test_tuple_keys():
    assert invert_dict({("a", 1): 5}) == {5: [("a", 1)]}
