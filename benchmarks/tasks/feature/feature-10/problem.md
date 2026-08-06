# Task: prime_factors

Implement `prime_factors(n)` in `solution.py`.

Given an integer `n >= 2`, return the list of its prime factors, sorted ascending, with multiplicity (each factor appears as many times as it divides `n`). Raise `ValueError` for `n < 2`.

Examples:

- `prime_factors(12)` -> `[2, 2, 3]`
- `prime_factors(17)` -> `[17]`
- `prime_factors(100)` -> `[2, 2, 5, 5]`
- `prime_factors(2)` -> `[2]`
- `prime_factors(360)` -> `[2, 2, 2, 3, 3, 5]`
- `prime_factors(1)` raises `ValueError`
- `prime_factors(0)` raises `ValueError`
- `prime_factors(-5)` raises `ValueError`

Edge cases:

- Primes factor to themselves.
- Perfect squares list each factor twice: `prime_factors(49)` -> `[7, 7]`.
- Large powers of small primes: `prime_factors(1024)` -> ten `2`s.
- `n < 2` (including negatives and zero) raises `ValueError`.

Do not change the function signature. Do not add prints.
