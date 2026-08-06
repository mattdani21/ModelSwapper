import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import workdays_between


def test_monday_to_friday():
    assert workdays_between(date(2024, 1, 1), date(2024, 1, 5)) == 4


def test_friday_to_monday():
    assert workdays_between(date(2024, 1, 5), date(2024, 1, 8)) == 1


def test_weekend_only():
    assert workdays_between(date(2024, 1, 6), date(2024, 1, 7)) == 0


def test_same_day():
    assert workdays_between(date(2024, 1, 1), date(2024, 1, 1)) == 0


def test_full_week():
    assert workdays_between(date(2024, 1, 1), date(2024, 1, 8)) == 5


def test_two_days():
    assert workdays_between(date(2024, 1, 2), date(2024, 1, 3)) == 1


def test_reversed_dates():
    assert workdays_between(date(2024, 1, 5), date(2024, 1, 1)) == 0
