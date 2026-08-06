# Task: extract duplicated grade boundaries

`solution.py` has two public functions, `letter_grade(score)` and
`classify(score)`. Both inline the same range check and the same five-way
score boundary chain (90/80/70/60), then map the band to a label.

Refactor the module so that:

- Add a helper `_check_score(score)` that raises
  `ValueError("score out of range")` for scores below 0 or above 100. The
  range check must appear exactly once, inside this helper.
- Add a helper `_score_to_grade(score)` containing the boundary chain exactly
  once and returning the letter `"A"`, `"B"`, `"C"`, `"D"`, or `"F"`.
- `letter_grade(score)` keeps its signature and returns the result of
  `_score_to_grade(score)` after the range check.
- `classify(score)` keeps its signature and returns the same labels as today
  (excellent/good/fair/poor/failing for A/B/C/D/F). Implement it by mapping
  the letter grade to a label (a module-level dict is fine); it must not
  repeat the boundary chain.

Do not change behavior. Stdlib only.
