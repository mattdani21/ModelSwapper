from datetime import date


def days_between(date_a, date_b):
    """Return the absolute number of days between two YYYY-MM-DD dates.

    Raises ValueError for malformed strings or non-existent dates.
    """
    a = date.fromisoformat(date_a)
    b = date.fromisoformat(date_b)
    return abs((b - a).days)
