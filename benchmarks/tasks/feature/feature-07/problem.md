# Task: is_balanced

Implement `is_balanced(s)` in `solution.py`.

Given a string, return `True` if all bracket characters are balanced and properly nested. The bracket pairs are `()`, `[]`, and `{}`. All other characters are ignored.

Examples:

- `is_balanced("()")` -> `True`
- `is_balanced("()[]{}")` -> `True`
- `is_balanced("([{}])")` -> `True`
- `is_balanced("(]")` -> `False`
- `is_balanced("([)]")` -> `False`
- `is_balanced("")` -> `True`
- `is_balanced("a(b)c")` -> `True`
- `is_balanced("(((")` -> `False`
- `is_balanced("())")` -> `False`

Edge cases:

- Empty string and strings without brackets are balanced.
- Closing brackets must match the most recent unmatched opening bracket (proper nesting).
- Unmatched opening or closing brackets make the result `False`.

Do not change the function signature. Do not add prints.
