# Task: extract duplicated statistics math

`solution.py` has two public functions, `summarize(values)` and
`analyze(values)`. Both compute the same mean and population-variance
formulas inline — the math is copy-pasted between them.

Refactor the module so that:

- Add a helper `_mean(values)` that returns the mean (the sum of the values
  divided by the number of values). The formula must appear exactly once,
  inside this helper.
- Add a helper `_variance(values)` that returns the population variance (the
  mean of the squared deviations from the mean). It must call `_mean` rather
  than re-implementing the mean. The variance formula must appear exactly
  once, inside this helper.
- `summarize(values)` keeps its signature and returns
  `{"mean": ..., "variance": ...}` (or `None` for empty input); it must not
  compute the formulas itself — delegate to the helpers.
- `analyze(values)` keeps its signature and returns the same dict plus a
  `"count"` key (or `None` for empty input); it must also delegate to the
  helpers.

Do not change behavior. Stdlib only.
