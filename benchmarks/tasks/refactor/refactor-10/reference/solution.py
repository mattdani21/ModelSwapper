"""Interest calculations."""


def _validate(principal, rate, years):
    if principal <= 0:
        raise ValueError("principal must be positive")
    if rate < 0:
        raise ValueError("rate must be non-negative")
    if years < 0:
        raise ValueError("years must be non-negative")


def _annual_rate(rate):
    return rate / 100


def simple_interest(principal, rate, years):
    _validate(principal, rate, years)
    return round(principal * (1 + _annual_rate(rate) * years), 2)


def compound_interest(principal, rate, years):
    _validate(principal, rate, years)
    return round(principal * (1 + _annual_rate(rate)) ** years, 2)
