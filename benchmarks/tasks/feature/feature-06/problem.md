# Task: days_between

Implement `days_between(date_a, date_b)` in `solution.py`.

Given two dates as strings in `YYYY-MM-DD` format, return the absolute number of days between them. The order of the arguments does not matter. Raise `ValueError` for malformed strings or non-existent dates (e.g. month 13, day 32, or February 30 in a non-leap year).

Examples:

- `days_between("2024-01-01", "2024-01-10")` -> `9`
- `days_between("2024-03-01", "2024-02-01")` -> `29` (2024 is a leap year, so February has 29 days)
- `days_between("2023-03-01", "2024-03-01")` -> `366` (spans Feb 29, 2024, a leap day)
- `days_between("2024-01-10", "2024-01-01")` -> `9` (order does not matter)
- `days_between("2024-06-15", "2024-06-15")` -> `0`
- `days_between("2024-02-29", "2024-03-01")` -> `1` (leap day is a real date)
- `days_between("2023-02-29", "2024-01-01")` raises `ValueError` (2023 is not a leap year)
- `days_between("2024/01/01", "2024-01-02")` raises `ValueError`

Edge cases:

- Same date returns `0`.
- Leap years: February 29 exists only in leap years; crossing Feb 29 adds a day.
- Malformed format, out-of-range months/days, and non-existent dates all raise `ValueError`.

Do not change the function signature. Do not add prints.
