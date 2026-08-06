import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from solution import fizzbuzz


def test_one():
    assert fizzbuzz(1) == ["1"]


def test_three():
    assert fizzbuzz(3) == ["1", "2", "Fizz"]


def test_five():
    assert fizzbuzz(5) == ["1", "2", "Fizz", "4", "Buzz"]


def test_full_15():
    expected = [
        "1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz",
        "Buzz", "11", "Fizz", "13", "14", "FizzBuzz",
    ]
    assert fizzbuzz(15) == expected


def test_multiples_of_15():
    seq = fizzbuzz(30)
    assert seq[14] == "FizzBuzz"
    assert seq[29] == "FizzBuzz"


def test_boundary_multiples():
    seq = fizzbuzz(30)
    assert seq[5] == "Fizz"    # 6
    assert seq[9] == "Buzz"    # 10
    assert seq[17] == "Fizz"   # 18
    assert seq[19] == "Buzz"   # 20


def test_zero_raises():
    with pytest.raises(ValueError):
        fizzbuzz(0)


def test_negative_raises():
    with pytest.raises(ValueError):
        fizzbuzz(-3)
