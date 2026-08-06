# Task: evaluate_rpn

Implement `evaluate_rpn(tokens)` in `solution.py`.

Evaluate a Reverse Polish Notation (postfix) expression given as a list of tokens. Tokens are either operands or one of the operator strings `"+"`, `"-"`, `"*"`, `"/"`. Operands are given as integers or decimal numeric strings (e.g. `3` or `"3"`). Each operator pops two operands, applies the operation, and pushes the result. Integer division truncates toward zero (e.g. `-7 / 2 == -3`).

Raise `ValueError` for:

- an empty token list,
- an invalid token (not a valid operand and not a known operator),
- an operator applied with fewer than two operands available,
- an expression that leaves more than one value on the stack,
- division by zero.

Examples:

- `evaluate_rpn(["3", "4", "+"])` -> `7`
- `evaluate_rpn(["2", "3", "+", "5", "*"])` -> `25`
- `evaluate_rpn(["4", "2", "/"])` -> `2`
- `evaluate_rpn(["-7", "2", "/"])` -> `-3`
- `evaluate_rpn(["7", "-3", "/"])` -> `-2`
- `evaluate_rpn(["2", "3", "11", "+", "5", "-", "*"])` -> `18`
- `evaluate_rpn(["5", "1", "2", "+", "4", "*", "+", "3", "-"])` -> `14`
- `evaluate_rpn(["42"])` -> `42`
- `evaluate_rpn(["5", "0", "/"])` raises `ValueError`
- `evaluate_rpn([])` raises `ValueError`

Edge cases:

- A single-token expression is valid.
- Division truncates toward zero, not toward negative infinity: `-7 / 2` is `-3` (not `-4`).
- Leftover operands and missing operands are both errors.

Do not change the function signature. Do not add prints.
