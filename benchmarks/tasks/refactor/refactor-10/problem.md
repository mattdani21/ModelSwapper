# Task: extract duplicated interest math

`solution.py` has two public functions, `simple_interest(principal, rate,
years)` and `compound_interest(principal, rate, years)`. Both inline the same
input validation and both convert the percentage rate the same way.

Refactor the module so that:

- Add a helper `_validate(principal, rate, years)` that raises the existing
  `ValueError`s (non-positive principal, negative rate, negative years). The
  three checks must appear exactly once in the file, inside this helper.
- Add a helper `_annual_rate(rate)` that converts a percentage to its decimal
  form (dividing by 100). The conversion must appear exactly once, inside
  this helper.
- `simple_interest` and `compound_interest` keep their signatures and exact
  results (rounded to 2 decimals) and must delegate validation and rate
  conversion to the helpers instead of inlining them.

Do not change behavior. Stdlib only.
