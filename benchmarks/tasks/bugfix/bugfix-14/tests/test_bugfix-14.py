import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import valid_parentheses


def test_simple_round():
    assert valid_parentheses("()") is True


def test_mixed_pairs():
    assert valid_parentheses("()[]{}") is True


def test_nested():
    assert valid_parentheses("([{}])") is True


def test_nested_round():
    assert valid_parentheses("{[]}") is True


def test_empty():
    assert valid_parentheses("") is True


def test_crossed():
    assert valid_parentheses("([)]") is False


def test_wrong_type():
    assert valid_parentheses("(]") is False


def test_crossed_2():
    assert valid_parentheses("[(])") is False


def test_unmatched_close():
    assert valid_parentheses(")") is False


def test_unmatched_open():
    assert valid_parentheses("(") is False
