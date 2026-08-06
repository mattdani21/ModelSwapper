# Task: my_atoi

Implement `my_atoi(s)` in `solution.py`.

Convert a string to a 32-bit signed integer:

1. Skip any leading whitespace.
2. Optionally read a `+` or `-` sign.
3. Read digits until a non-digit character is reached; stop there.
4. If no digits were read, the result is 0.
5. Clamp the result to the signed 32-bit range
   `[-2147483648, 2147483647]`.

Examples:

- `my_atoi("42")` -> `42`
- `my_atoi("   -42")` -> `-42`
- `my_atoi("4193 with words")` -> `4193`
- `my_atoi("words and 987")` -> `0`
- `my_atoi("")` -> `0`
- `my_atoi("2147483648")` -> `2147483647`
- `my_atoi("-2147483649")` -> `-2147483648`

Do not change the function signature. Do not add prints.
