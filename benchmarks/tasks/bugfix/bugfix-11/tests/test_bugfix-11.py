import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import run_length_encode


def test_single_char():
    assert run_length_encode("a") == "a1"


def test_single_run():
    assert run_length_encode("aaa") == "a3"


def test_two_runs():
    assert run_length_encode("aaab") == "a3b1"


def test_two_runs_equal():
    assert run_length_encode("aabb") == "a2b2"


def test_alternating():
    assert run_length_encode("abc") == "a1b1c1"


def test_mixed():
    assert run_length_encode("aabbbcc") == "a2b3c2"


def test_empty():
    assert run_length_encode("") == ""
