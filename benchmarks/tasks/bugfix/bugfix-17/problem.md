# Task: next_permutation

Implement `next_permutation(nums)` in `solution.py`.

Given a list of integers that may contain duplicates, return a **new** list
holding the next lexicographically greater permutation of the elements. If
no greater permutation exists (the elements are in descending order), return
the elements sorted in ascending order. The input list must not be modified.

Examples:

- `next_permutation([1, 2, 3])` -> `[1, 3, 2]`
- `next_permutation([3, 2, 1])` -> `[1, 2, 3]`
- `next_permutation([1, 1, 5])` -> `[1, 5, 1]`
- `next_permutation([1, 2, 1])` -> `[2, 1, 1]`
- `next_permutation([1])` -> `[1]`
- `next_permutation([])` -> `[]`

Do not change the function signature. Do not add prints.
