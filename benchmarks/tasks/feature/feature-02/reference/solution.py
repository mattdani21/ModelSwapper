def second_largest(numbers):
    """Return the second largest distinct integer in numbers,
    or None if fewer than two distinct values exist.
    """
    distinct = sorted(set(numbers))
    if len(distinct) < 2:
        return None
    return distinct[-2]
