import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import is_palindrome


def test_simple_palindrome():
    assert is_palindrome("racecar") is True


def test_case_insensitive():
    assert is_palindrome("Racecar") is True


def test_non_palindrome():
    assert is_palindrome("hello") is False


def test_punctuation_and_spaces_ignored():
    assert is_palindrome("A man, a plan, a canal: Panama") is True


def test_spaces_ignored():
    assert is_palindrome("never odd or even") is True


def test_punctuation_only_palindrome():
    assert is_palindrome("no lemon, no melon") is True


def test_digits_kept():
    assert is_palindrome("12321") is True


def test_empty_string():
    assert is_palindrome("") is True
