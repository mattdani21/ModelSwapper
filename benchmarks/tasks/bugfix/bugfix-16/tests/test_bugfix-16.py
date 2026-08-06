import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import my_atoi


def test_positive():
    assert my_atoi("42") == 42


def test_negative_with_spaces():
    assert my_atoi("   -42") == -42


def test_positive_sign():
    assert my_atoi("+7") == 7


def test_digits_then_words():
    assert my_atoi("4193 with words") == 4193


def test_words_then_digits():
    assert my_atoi("words and 987") == 0


def test_empty():
    assert my_atoi("") == 0


def test_overflow_positive():
    assert my_atoi("2147483648") == 2147483647


def test_overflow_negative():
    assert my_atoi("-2147483649") == -2147483648


def test_huge():
    assert my_atoi("99999999999999") == 2147483647
