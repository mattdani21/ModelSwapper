# Task: merge_intervals

Implement `merge_intervals(intervals)` in `solution.py`.

Given a list of intervals, where each interval is a pair `[start, end]` of integers (inclusive bounds), merge all intervals that overlap or touch, and return the merged intervals sorted by start. Intervals may be given in any order. If any interval has `start > end`, raise `ValueError`.

Examples:

- `merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]])` -> `[[1, 6], [8, 10], [15, 18]]`
- `merge_intervals([[1, 4], [4, 5]])` -> `[[1, 5]]` (touching intervals merge)
- `merge_intervals([[1, 4], [0, 2]])` -> `[[0, 4]]` (unsorted input)
- `merge_intervals([[1, 10], [2, 3]])` -> `[[1, 10]]` (contained interval)
- `merge_intervals([])` -> `[]`
- `merge_intervals([[5, 5]])` -> `[[5, 5]]`
- `merge_intervals([[3, 1]])` raises `ValueError`

Edge cases:

- Empty input returns an empty list.
- Intervals that only touch (`end` of one equals `start` of the next) merge.
- Fully contained intervals are absorbed.
- Output is always sorted by start, and every output interval satisfies `start <= end`.

Do not change the function signature. Do not add prints.
