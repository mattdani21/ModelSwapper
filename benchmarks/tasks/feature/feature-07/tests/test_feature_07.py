import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import is_balanced


def test_simple_pairs():
    assert is_balanced("()") is True


def test_all_pair_types():
    assert is_balanced("()[]{}") is True


def test_deeply_nested():
    assert is_balanced("([{}])") is True


def test_mismatched():
    assert is_balanced("(]") is False


def test_interleaved_wrong_order():
    assert is_balanced("([)]") is False


def test_empty():
    assert is_balanced("") is True


def test_no_brackets():
    assert is_balanced("hello world") is True


def test_brackets_among_text():
    assert is_balanced("a(b)c") is True


def test_only_openings():
    assert is_balanced("(((") is False


def test_only_closings():
    assert is_balanced(")))") is False


def test_extra_closing():
    assert is_balanced("())") is False


def test_leftover_opening():
    assert is_balanced("(()") is False


def test_mixed_with_text():
    assert is_balanced("x([y]{z})w") is True
    assert is_balanced("x([y]z)w") is True
