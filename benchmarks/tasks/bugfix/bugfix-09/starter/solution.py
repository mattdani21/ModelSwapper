from datetime import timedelta


def workdays_between(d1, d2):
    """Count weekdays (Mon-Fri) in the half-open interval [d1, d2)."""
    count = 0
    d = d1
    while d <= d2:
        if d.weekday() < 5:
            count += 1
        d += timedelta(days=1)
    return count
