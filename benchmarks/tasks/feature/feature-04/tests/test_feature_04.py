import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import reverse_words


def test_two_words():
    assert reverse_words("hello world") == "world hello"


def test_multiple_spaces():
    assert reverse_words("  the   quick brown  fox ") == "fox brown quick the"


def test_single_word():
    assert reverse_words("single") == "single"


def test_empty_string():
    assert reverse_words("") == ""


def test_whitespace_only():
    assert reverse_words("   \t ") == ""


def test_three_words():
    assert reverse_words("a b c") == "c b a"


def test_tabs_and_newlines():
    assert reverse_words("one\ttwo\nthree") == "three two one"


def test_punctuation_stays_attached():
    assert reverse_words("Hello, world!") == "world! Hello,"
