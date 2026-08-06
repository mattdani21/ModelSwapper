import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import count_vowels


def test_lowercase():
    assert count_vowels("hello") == 2


def test_uppercase():
    assert count_vowels("HELLO") == 2


def test_mixed_case():
    assert count_vowels("hEllO") == 2


def test_all_vowels():
    assert count_vowels("aeiou") == 5


def test_all_vowels_upper():
    assert count_vowels("AEIOU") == 5


def test_no_vowels():
    assert count_vowels("xyz") == 0


def test_empty():
    assert count_vowels("") == 0
