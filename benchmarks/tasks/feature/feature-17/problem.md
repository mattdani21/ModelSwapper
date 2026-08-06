# Task: spiral_order

Implement `spiral_order(matrix)` in `solution.py`.

Given a rectangular matrix (a list of lists of integers), return a list of all its elements in clockwise spiral order, starting from the top-left corner. An empty matrix (`[]`) or a matrix whose rows are empty (`[[]]`) returns `[]`. If the rows have different lengths, raise `ValueError`.

Examples:

- `spiral_order([[1, 2, 3], [4, 5, 6], [7, 8, 9]])` -> `[1, 2, 3, 6, 9, 8, 7, 4, 5]`
- `spiral_order([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])` -> `[1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]`
- `spiral_order([[1, 2], [3, 4]])` -> `[1, 2, 4, 3]`
- `spiral_order([[1]])` -> `[1]`
- `spiral_order([[1, 2, 3, 4]])` -> `[1, 2, 3, 4]`
- `spiral_order([[1], [2], [3]])` -> `[1, 2, 3]`
- `spiral_order([])` -> `[]`
- `spiral_order([[]])` -> `[]`
- `spiral_order([[1, 2], [3]])` raises `ValueError`

Edge cases:

- Single row and single column matrices are valid.
- Empty matrix and empty rows return an empty list.
- Ragged (non-rectangular) input raises `ValueError`.

Do not change the function signature. Do not add prints.
