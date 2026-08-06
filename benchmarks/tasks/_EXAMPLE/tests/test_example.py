import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import most_common_word


def test_most_common_basic():
    assert most_common_word("the cat and the dog") == "the"


def test_second_word_wins():
    assert most_common_word("one two two three") == "two"


def test_tie_breaks_by_first_occurrence():
    assert most_common_word("a b a b") == "a"


def test_case_insensitive():
    assert most_common_word("Apple apple") == "apple"


def test_punctuation_stripped():
    assert most_common_word("Hello, world! Hello world.") == "hello"


def test_empty_input():
    assert most_common_word("") is None
