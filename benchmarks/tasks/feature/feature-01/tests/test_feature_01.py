import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import is_palindrome


def test_basic_palindrome():
    assert is_palindrome("racecar") is True


def test_non_palindrome():
    assert is_palindrome("hello") is False


def test_ignores_punctuation_and_spaces():
    assert is_palindrome("A man, a plan, a canal: Panama") is True


def test_ignores_case():
    assert is_palindrome("RaceCar") is True


def test_question_mark_sentence():
    assert is_palindrome("Was it a car or a cat I saw?") is True


def test_near_miss():
    assert is_palindrome("race a car") is False


def test_empty_string():
    assert is_palindrome("") is True


def test_whitespace_only():
    assert is_palindrome("   ") is True


def test_single_character():
    assert is_palindrome("z") is True


def test_digits_are_significant():
    assert is_palindrome("12321") is True
    assert is_palindrome("123") is False


def test_apostrophes_ignored():
    assert is_palindrome("No 'x' in Nixon") is True
