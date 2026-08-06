# Task: extract duplicated query logic

`solution.py` searches record lists. `find_by_name(records, name)` and
`find_by_tag(records, tag)` both inline the same argument check, build a
query string, and collect matching records with the same result-list loop.

Refactor the module so that:

- Add a helper `_check_value(field, value)` that raises
  `ValueError("empty " + field)` when `value` is falsy. The check must appear
  exactly once, inside this helper.
- Add a helper `_collect(records, predicate)` that returns the list of
  records for which `predicate(record)` is true, preserving order. The
  result-collection must appear exactly once, inside this helper.
- `find_by_name(records, name)` and `find_by_tag(records, tag)` keep their
  signatures and results; they must delegate to the helpers and must not
  contain the manual result-collection loop themselves.

Do not change behavior or error messages. Stdlib only.
