import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from solution import evaluate_rpn


def test_simple_add():
    assert evaluate_rpn(["3", "4", "+"]) == 7


def test_multiply_after_add():
    assert evaluate_rpn(["2", "3", "+", "5", "*"]) == 25


def test_division():
    assert evaluate_rpn(["4", "2", "/"]) == 2


def test_division_truncates_toward_zero_negative():
    assert evaluate_rpn(["-7", "2", "/"]) == -3


def test_division_negative_divisor():
    assert evaluate_rpn(["7", "-3", "/"]) == -2


def test_division_both_negative():
    assert evaluate_rpn(["-4", "-2", "/"]) == 2


def test_complex_expression():
    assert evaluate_rpn(["2", "3", "11", "+", "5", "-", "*"]) == 18


def test_long_expression():
    assert evaluate_rpn(["5", "1", "2", "+", "4", "*", "+", "3", "-"]) == 14


def test_single_token():
    assert evaluate_rpn(["42"]) == 42


def test_negative_operand():
    assert evaluate_rpn(["-3", "-2", "*"]) == 6


def test_division_by_zero_raises():
    with pytest.raises(ValueError):
        evaluate_rpn(["5", "0", "/"])


def test_empty_raises():
    with pytest.raises(ValueError):
        evaluate_rpn([])


def test_invalid_token_raises():
    with pytest.raises(ValueError):
        evaluate_rpn(["3", "x", "+"])


def test_missing_operands_raises():
    with pytest.raises(ValueError):
        evaluate_rpn(["3", "+"])


def test_leftover_operands_raises():
    with pytest.raises(ValueError):
        evaluate_rpn(["3", "4", "+", "5"])
