# Task: workdays_between

Implement `workdays_between(d1, d2)` in `solution.py`.

Given two `datetime.date` objects, return the number of weekdays
(Monday through Friday) in the half-open interval `[d1, d2)`: `d1` is
counted, `d2` is **not** counted. If `d2` is on or before `d1`, return 0.

Examples (2024-01-01 is a Monday):

- `workdays_between(date(2024, 1, 1), date(2024, 1, 5))` -> `4`
- `workdays_between(date(2024, 1, 5), date(2024, 1, 8))` -> `1`
- `workdays_between(date(2024, 1, 6), date(2024, 1, 7))` -> `0`
- `workdays_between(date(2024, 1, 1), date(2024, 1, 1))` -> `0`

Do not change the function signature. Do not add prints.
