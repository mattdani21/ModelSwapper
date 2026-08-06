# Task: flatten

Implement `flatten(nested)` in `solution.py`.

Given a list that may contain arbitrarily nested lists, return a flat list
of all non-list elements in depth-first order.

Examples:

- `flatten([[1, 2], [3, [4]]])` -> `[1, 2, 3, 4]`
- `flatten([1, [2, [3, [4]]]])` -> `[1, 2, 3, 4]`
- `flatten([])` -> `[]`
- `flatten([[],[[]]])` -> `[]`
- `flatten([1, 2, 3])` -> `[1, 2, 3]`

Do not change the function signature. Do not add prints.
