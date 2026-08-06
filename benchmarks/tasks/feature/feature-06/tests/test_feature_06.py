import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from solution import days_between


def test_same_month():
    assert days_between("2024-01-01", "2024-01-10") == 9


def test_leap_year_february():
    assert days_between("2024-03-01", "2024-02-01") == 29


def test_cross_year_leap():
    assert days_between("2023-03-01", "2024-03-01") == 366


def test_non_leap_year():
    assert days_between("2023-01-01", "2023-12-31") == 364


def test_reversed_order():
    assert days_between("2024-01-10", "2024-01-01") == 9


def test_same_date():
    assert days_between("2024-06-15", "2024-06-15") == 0


def test_leap_day_valid():
    assert days_between("2024-02-29", "2024-03-01") == 1


def test_feb_29_non_leap_raises():
    with pytest.raises(ValueError):
        days_between("2023-02-29", "2024-01-01")


def test_bad_separator_raises():
    with pytest.raises(ValueError):
        days_between("2024/01/01", "2024-01-02")


def test_bad_month_raises():
    with pytest.raises(ValueError):
        days_between("2024-13-01", "2024-01-01")


def test_bad_day_raises():
    with pytest.raises(ValueError):
        days_between("2024-04-31", "2024-01-01")


def test_garbage_raises():
    with pytest.raises(ValueError):
        days_between("not-a-date", "2024-01-01")
