# Task: split the log-line monolith

`solution.py` has a single public function `process_log_line(line)` that does
everything inline: splitting/parsing the line, validating its fields, and
formatting the output.

Refactor the module so that parsing, validation, and formatting become three
separate helpers, and `process_log_line` only orchestrates them:

- `_parse_line(line)`: strips the line, splits on `"|"`, requires exactly 3
  fields (else `ValueError("malformed log line")`), strips each field, and
  returns `(level, ts, msg)`.
- `_validate(level, ts, msg)`: raises `ValueError` for an unknown level
  (allowed: INFO, WARN, ERROR), a timestamp that is empty or not exactly 8
  characters, or an empty message. Keep the existing error messages.
- `_format(level, ts, msg)`: returns the formatted line
  `"{ts} [{level}] {msg}"`.
- `process_log_line(line)` keeps its signature and behavior and must contain
  none of the parsing/validation/formatting logic itself — only calls to the
  three helpers.

Do not change behavior or error messages. Stdlib only.
