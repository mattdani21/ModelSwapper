def factorial(n):
    """Return n! for a non-negative integer n."""
    result = 1
    for i in range(1, n):
        result *= i
    return result
