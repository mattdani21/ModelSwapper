import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import solution
from solution import find_by_name, find_by_tag


def _raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return
    raise AssertionError("expected %s" % exc.__name__)


def test_find_by_name():
    records = [{"name": "a"}, {"name": "b"}, {"name": "a"}]
    assert find_by_name(records, "a") == [{"name": "a"}, {"name": "a"}]


def test_find_by_name_no_match():
    records = [{"name": "a"}]
    assert find_by_name(records, "z") == []


def test_find_by_name_ignores_missing_key():
    records = [{"name": "a"}, {"other": 1}]
    assert find_by_name(records, "a") == [{"name": "a"}]


def test_find_by_tag():
    records = [
        {"name": "x", "tags": ["red", "big"]},
        {"name": "y", "tags": ["red"]},
        {"name": "z"},
    ]
    assert find_by_tag(records, "red") == [
        {"name": "x", "tags": ["red", "big"]},
        {"name": "y", "tags": ["red"]},
    ]


def test_find_by_tag_missing_tags_key():
    records = [{"name": "z"}, {"name": "w", "tags": ["blue"]}]
    assert find_by_tag(records, "blue") == [{"name": "w", "tags": ["blue"]}]


def test_empty_value_rejected():
    _raises(ValueError, find_by_name, [], "")
    _raises(ValueError, find_by_tag, [], "")


def test_helpers_exist():
    assert callable(getattr(solution, "_check_value", None))
    assert callable(getattr(solution, "_collect", None))


def test_helper_signatures():
    assert list(inspect.signature(solution._check_value).parameters) == ["field", "value"]
    assert list(inspect.signature(solution._collect).parameters) == ["records", "predicate"]


def test_loop_not_duplicated():
    src = inspect.getsource(solution)
    assert src.count("results = []") == 0
    assert src.count('raise ValueError(f"empty {field}")') == 1
