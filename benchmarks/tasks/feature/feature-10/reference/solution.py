def prime_factors(n):
    """Return the prime factors of n in ascending order with multiplicity.

    Raises ValueError if n < 2.
    """
    if n < 2:
        raise ValueError("n must be >= 2")
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors
