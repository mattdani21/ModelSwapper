# Task: reverse_words

Implement `reverse_words(sentence)` in `solution.py`.

Given a string, return a new string with the words in reverse order, joined by single spaces. Words are maximal runs of non-whitespace characters. Leading, trailing, and repeated whitespace are ignored.

Examples:

- `reverse_words("hello world")` -> `"world hello"`
- `reverse_words("  the   quick brown  fox ")` -> `"fox brown quick the"`
- `reverse_words("single")` -> `"single"`
- `reverse_words("")` -> `""`
- `reverse_words("   ")` -> `""`
- `reverse_words("a b c")` -> `"c b a"`

Edge cases:

- Empty and whitespace-only input returns an empty string.
- Tabs and newlines count as whitespace: `"one\ttwo\nthree"` -> `"three two one"`.
- A single word is returned unchanged.
- Punctuation stays attached to its word: `"Hello, world!"` -> `"world! Hello,"`.

Do not change the function signature. Do not add prints.
