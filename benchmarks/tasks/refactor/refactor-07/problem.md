# Task: extract shared row rendering

`solution.py` renders data rows in two formats. `print_table(rows)` prints
rows as `| a | b |` and `print_csv(rows)` prints rows as `a,b`. Both inline
the same cell-to-string conversion and join logic.

Refactor the module so that:

- Add a helper `_render_row(cells, sep, wrap=None)` that converts each cell
  with `str(...)`, optionally wraps each converted cell in the `wrap` string
  (when `wrap` is not None), and joins the results with `sep`.
- The cell conversion must appear exactly once in the file (inside
  `_render_row`).
- `print_table(rows)` and `print_csv(rows)` keep their signatures and exact
  output; they must delegate all row rendering to `_render_row`.

Do not change behavior. Stdlib only.
