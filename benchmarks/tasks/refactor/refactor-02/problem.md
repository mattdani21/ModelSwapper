# Task: extract duplicated row formatting

`solution.py` renders simple text reports. `print_inventory(items)` and
`print_scores(scores)` both format every row with the same column layout
(name left-padded to 12 characters, one space, value right-padded to 6) and
both print the same separator line of 20 `=` characters.

Refactor the module so that:

- Add a helper `format_row(name, value)` that returns the formatted row line
  (12-character left-aligned name, one space, 6-character right-aligned
  value). The column-format logic must appear exactly once, inside this
  helper.
- `print_inventory(items)` and `print_scores(scores)` keep their signatures
  and exact output (header line, separator line, one formatted line per row,
  trailing blank line). They must delegate row formatting to `format_row` and
  must not contain the column-formatting themselves.

Do not change behavior. Stdlib only.
