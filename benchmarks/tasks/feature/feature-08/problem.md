# Task: parse_csv_line

Implement `parse_csv_line(line)` in `solution.py`.

Parse a single CSV line into a list of fields. The rules:

- Fields are separated by commas.
- A field may be enclosed in double quotes. Inside a quoted field, a pair of double quotes (`""`) represents one literal double-quote character.
- Commas inside quoted fields do not separate fields.
- Unquoted fields have surrounding whitespace trimmed.
- Quoted fields keep their content exactly (no trimming).

Examples:

- `parse_csv_line("a,b,c")` -> `["a", "b", "c"]`
- `parse_csv_line('"a,b",c')` -> `["a,b", "c"]`
- `parse_csv_line('"a ""quoted"" word",x')` -> `['a "quoted" word', "x"]`
- `parse_csv_line("  a  ,  b  ")` -> `["a", "b"]`
- `parse_csv_line('" spaced out ",plain')` -> `[" spaced out ", "plain"]`
- `parse_csv_line('""')` -> `[""]`
- `parse_csv_line("")` -> `[""]`
- `parse_csv_line("a,")` -> `["a", ""]`

Edge cases:

- An empty line is a single empty field.
- A trailing comma yields a trailing empty field.
- An empty quoted field `""` is an empty string.
- Whitespace inside quotes is preserved; whitespace outside quotes is trimmed.

Do not change the function signature. Do not add prints.
