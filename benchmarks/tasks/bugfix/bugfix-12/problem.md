# Task: top_k

Implement `top_k(nums, k)` in `solution.py`.

Given a list of integers, return a list of the `k` most frequent integers,
ordered by frequency from highest to lowest. Ties are broken by first
occurrence in `nums`. You may assume `1 <= k <= len(set(nums))`.

Examples:

- `top_k([1, 1, 1, 2, 2, 3], 2)` -> `[1, 2]`
- `top_k([1, 1, 2, 2, 3, 3, 3], 2)` -> `[3, 1]`
- `top_k([3, 3, 3, 1, 1, 2], 2)` -> `[3, 1]`
- `top_k([5], 1)` -> `[5]`

Do not change the function signature. Do not add prints.
