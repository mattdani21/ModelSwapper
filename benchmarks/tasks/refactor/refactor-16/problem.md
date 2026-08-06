# Task: split the report-generator pipeline

`solution.py` has one public function `generate_report(rows)` that does the
whole pipeline inline: parsing each row, aggregating the values, and building
the formatted output lines.

Refactor the module so that the pipeline has three stages, each a helper:

- `_parse_row(row)`: strips the row; blank rows return `None`; splits on
  `","` and requires exactly 2 cells (else `ValueError` with message
  `"bad row: <row>"`); strips the name; parses the value with `float`
  (failure raises `ValueError` with message `"bad value: <row>"`); returns
  `(name, value)`.
- `_aggregate(parsed)`: returns a dict with `count`, `total`, `mean`, `min`,
  and `max` over the parsed values. The aggregation must appear exactly once,
  inside this helper.
- `_format_report(parsed, stats)`: builds the output lines — one
  `"- {name}: {value:.2f}"` line per item, then `"total: ..."`, `"mean:
  ..."`, `"min: ..."`, `"max: ..."` lines (all numbers formatted with 2
  decimals) — and returns them joined with newlines. The line formatting must
  appear exactly once, inside this helper.
- `generate_report(rows)` keeps its signature and behavior (blank rows are
  skipped; an all-blank input returns `"no data"`) and must contain none of
  the parsing/aggregation/formatting logic itself — only calls to the three
  helpers.

Do not change behavior or error messages. Stdlib only.
