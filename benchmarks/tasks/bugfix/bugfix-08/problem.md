# Task: parse_csv

Implement `parse_csv(text)` in `solution.py`.

Parse a CSV string into a list of rows, where each row is a list of field
strings. Fields are separated by commas. A field may be wrapped in double
quotes, in which case commas inside it are literal. A double quote inside a
quoted field is escaped by doubling it (`""`). A double quote that appears
inside an unquoted field is treated as a literal character. Rows are
separated by newlines. An empty input string yields an empty list.

Examples:

- `parse_csv("a,b,c")` -> `[["a", "b", "c"]]`
- `parse_csv('"x,y",z')` -> `[["x,y", "z"]]`
- `parse_csv('"a""b",c')` -> `[["a\"b", "c"]]`
- `parse_csv("a,b\nc,d")` -> `[["a", "b"], ["c", "d"]]`
- `parse_csv("")` -> `[]`

Do not change the function signature. Do not add prints.
