import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import factorial


def test_zero():
    assert factorial(0) == 1


def test_one():
    assert factorial(1) == 1


def test_two():
    assert factorial(2) == 2


def test_three():
    assert factorial(3) == 6


def test_five():
    assert factorial(5) == 120


def test_ten():
    assert factorial(10) == 3628800
