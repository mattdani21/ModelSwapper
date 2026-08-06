import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import longest_unique_substring


def test_classic():
    assert longest_unique_substring("abcabcbb") == 3


def test_all_same():
    assert longest_unique_substring("bbbbb") == 1


def test_wwk():
    assert longest_unique_substring("pwwkew") == 3


def test_abba():
    assert longest_unique_substring("abba") == 2


def test_empty():
    assert longest_unique_substring("") == 0


def test_no_repeats():
    assert longest_unique_substring("abcdef") == 6


def test_short():
    assert longest_unique_substring("abc") == 3
