# Task: format_bytes

Implement `format_bytes(n)` in `solution.py`.

Given a non-negative integer byte count, return a human-readable string. Units are binary (1024-based): `B`, `KB`, `MB`, `GB`, `TB`. Counts below 1024 are rendered as the integer followed by ` B`. Larger counts are divided by 1024 repeatedly until the value is below 1024 (or the largest unit `TB` is reached), then rendered with exactly one decimal place, rounded half-up. Raise `ValueError` for negative input.

Examples:

- `format_bytes(0)` -> `"0 B"`
- `format_bytes(500)` -> `"500 B"`
- `format_bytes(1023)` -> `"1023 B"`
- `format_bytes(1024)` -> `"1.0 KB"`
- `format_bytes(1536)` -> `"1.5 KB"`
- `format_bytes(1048576)` -> `"1.0 MB"`
- `format_bytes(1572864)` -> `"1.5 MB"`
- `format_bytes(1610612736)` -> `"1.5 GB"`
- `format_bytes(1099511627776)` -> `"1.0 TB"`
- `format_bytes(-1)` raises `ValueError`

Edge cases:

- Zero and values below 1024 use plain integer formatting.
- Exactly 1024 is `"1.0 KB"`, not `"1024 B"`.
- One decimal place is always shown for KB and above, even when the value is exact.
- Values at unit boundaries (1024, 1048576, ...) convert exactly.

Do not change the function signature. Do not add prints.
