import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import solution
from solution import keyword_counts, top_words


def test_top_words_basic():
    assert top_words("a b a c", 2) == ["a", "b"]


def test_top_words_tie_alphabetical():
    assert top_words("b a c", 3) == ["a", "b", "c"]


def test_top_words_limit():
    assert top_words("one two two three three three", 2) == ["three", "two"]


def test_top_words_empty():
    assert top_words("", 5) == []


def test_punctuation_ignored():
    assert top_words("Hello, world! Hello world.", 1) == ["hello"]


def test_keyword_counts():
    assert keyword_counts("a b a", ["a", "b", "z"]) == {"a": 2, "b": 1, "z": 0}


def test_helpers_exist():
    assert callable(getattr(solution, "_normalize", None))
    assert callable(getattr(solution, "_tally", None))


def test_helper_signatures():
    assert list(inspect.signature(solution._normalize).parameters) == ["text"]
    assert list(inspect.signature(solution._tally).parameters) == ["words"]


def test_logic_not_duplicated():
    src = inspect.getsource(solution)
    assert src.count("counts.get(w, 0) + 1") == 1
    assert src.count("_WORD_RE.finditer(text.lower())") == 1
