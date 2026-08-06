# Task: two_sum

Implement `two_sum(nums, target)` in `solution.py`.

Given a list of integers and a target integer, return the indices `(i, j)` of the two distinct elements that add up to the target, with `i < j`. At most one solution exists. Return `None` if no two distinct elements sum to the target.

Examples:

- `two_sum([2, 7, 11, 15], 9)` -> `(0, 1)`
- `two_sum([3, 2, 4], 6)` -> `(1, 2)`
- `two_sum([3, 3], 6)` -> `(0, 1)`
- `two_sum([1, 2, 3], 10)` -> `None`
- `two_sum([5], 5)` -> `None`
- `two_sum([], 0)` -> `None`

Edge cases:

- Duplicate values can form the answer (`[3, 3]`).
- A single element or empty list always returns `None`.
- A number may not be paired with itself: `[3, 1], 6` -> `None`.
- The returned tuple always has the smaller index first.

Do not change the function signature. Do not add prints.
