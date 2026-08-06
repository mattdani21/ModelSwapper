import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import group_by


def test_parity_groups():
    assert group_by([1, 2, 3, 4, 5, 6], lambda x: x % 2) == {1: [1, 3, 5], 0: [2, 4, 6]}


def test_first_letter():
    assert group_by(["apple", "avocado", "banana"], lambda w: w[0]) == {
        "a": ["apple", "avocado"],
        "b": ["banana"],
    }


def test_empty():
    assert group_by([], lambda x: x) == {}


def test_len_key():
    assert group_by(["hi", "yo", "hey"], len) == {2: ["hi", "yo"], 3: ["hey"]}


def test_single_item():
    assert group_by([42], lambda x: "only") == {"only": [42]}


def test_order_preserved_within_groups():
    result = group_by([1, 3, 2, 4], lambda x: x % 2)
    assert result == {1: [1, 3], 0: [2, 4]}


def test_noncontiguous_groups():
    result = group_by(["a", "b", "a", "c", "b"], lambda w: w)
    assert result == {"a": ["a", "a"], "b": ["b", "b"], "c": ["c"]}
