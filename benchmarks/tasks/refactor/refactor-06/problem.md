# Task: extract duplicated TSV parsing

`solution.py` loads tab-separated data files. `load_users(path)` and
`load_products(path)` both inline the same reading loop: open the file, strip
each line, skip blank lines and lines starting with `#`, split on tabs, strip
each cell, and require exactly 2 cells per row (else a `ValueError` whose
message is `"bad row: <line>"`).

Refactor the module so that:

- Add a generator helper `_read_rows(path)` that yields the cleaned non-empty,
  non-comment lines of the file. The blank-line/comment skip logic must appear
  exactly once, inside this helper.
- Add a helper `_split_row(line)` that splits on tabs, strips each cell, and
  raises `ValueError("bad row: <line>")` unless there are exactly 2 cells.
  The row-arity check must appear exactly once, inside this helper.
- `load_users(path)` and `load_products(path)` keep their signatures and
  results (users: `{"name": str, "age": int}`; products:
  `{"sku": str, "price": float}`). They must build their records by iterating
  `_read_rows(path)` and converting the result of `_split_row(line)`; they
  must not contain the file-reading or cell-splitting logic themselves.

Do not change behavior. Stdlib only.
