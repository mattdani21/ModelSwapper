import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from solution import prime_factors


def test_composite():
    assert prime_factors(12) == [2, 2, 3]


def test_prime():
    assert prime_factors(17) == [17]


def test_perfect_square():
    assert prime_factors(100) == [2, 2, 5, 5]


def test_two():
    assert prime_factors(2) == [2]


def test_three_distinct_primes():
    assert prime_factors(30) == [2, 3, 5]


def test_360():
    assert prime_factors(360) == [2, 2, 2, 3, 3, 5]


def test_seven_squared():
    assert prime_factors(49) == [7, 7]


def test_power_of_two():
    assert prime_factors(1024) == [2] * 10


def test_large_prime():
    assert prime_factors(97) == [97]


def test_negative_raises():
    with pytest.raises(ValueError):
        prime_factors(-5)


def test_zero_raises():
    with pytest.raises(ValueError):
        prime_factors(0)


def test_one_raises():
    with pytest.raises(ValueError):
        prime_factors(1)
