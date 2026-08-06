# Task: run_length_encode

Implement `run_length_encode(s)` in `solution.py`.

Compress a string by replacing each maximal run of identical characters
with the character followed by its run length. Every run is encoded,
including runs of length 1. The empty string encodes to the empty string.

Examples:

- `run_length_encode("aaabcc")` -> `"a3b1c2"`
- `run_length_encode("a")` -> `"a1"`
- `run_length_encode("abc")` -> `"a1b1c1"`
- `run_length_encode("")` -> `""`

Do not change the function signature. Do not add prints.
