# Task: second_largest

Implement `second_largest(numbers)` in `solution.py`.

Given a list of integers, return the second largest **distinct** value. If there are fewer than two distinct values, return `None`.

Examples:

- `second_largest([3, 1, 4, 1, 5, 9, 2, 6])` -> `6`
- `second_largest([10, 10, 10])` -> `None`
- `second_largest([5, 5, 3])` -> `3`
- `second_largest([7])` -> `None`
- `second_largest([])` -> `None`
- `second_largest([-1, -2, -3])` -> `-2`

Edge cases:

- Empty list returns `None`.
- Single-element list returns `None`.
- All-equal lists return `None` (no second *distinct* value).
- Duplicates are ignored when ranking: `[5, 5, 4]` -> `4`.
- Negative values behave normally.

Do not change the function signature. Do not add prints.
