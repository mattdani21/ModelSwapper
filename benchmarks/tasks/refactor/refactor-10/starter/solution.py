"""Interest calculations."""


def simple_interest(principal, rate, years):
    if principal <= 0:
        raise ValueError("principal must be positive")
    if rate < 0:
        raise ValueError("rate must be non-negative")
    if years < 0:
        raise ValueError("years must be non-negative")
    return round(principal * (1 + rate / 100 * years), 2)


def compound_interest(principal, rate, years):
    if principal <= 0:
        raise ValueError("principal must be positive")
    if rate < 0:
        raise ValueError("rate must be non-negative")
    if years < 0:
        raise ValueError("years must be non-negative")
    return round(principal * (1 + rate / 100) ** years, 2)
