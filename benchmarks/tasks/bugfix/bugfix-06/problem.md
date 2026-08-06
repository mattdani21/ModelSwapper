# Task: merge_intervals

Implement `merge_intervals(intervals)` in `solution.py`.

Given a list of intervals, where each interval is a pair `[start, end]`
with `start <= end`, merge all intervals that overlap or touch. Two
intervals overlap if they share any point; they touch if one ends exactly
where the next begins (e.g. `[1, 2]` and `[2, 3]` touch). Return the merged
intervals as a list of `[start, end]` pairs sorted by start. The input may
be unsorted and must not be modified.

Examples:

- `merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]])` -> `[[1, 6], [8, 10], [15, 18]]`
- `merge_intervals([[1, 2], [2, 3]])` -> `[[1, 3]]`
- `merge_intervals([[1, 4], [4, 5]])` -> `[[1, 5]]`
- `merge_intervals([])` -> `[]`

Do not change the function signature. Do not add prints.
