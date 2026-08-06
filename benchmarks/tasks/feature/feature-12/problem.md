# Task: group_by

Implement `group_by(items, key_fn)` in `solution.py`.

Given a list of items and a key function, return a new dictionary mapping each distinct key to the list of items (in their original order) for which `key_fn(item)` equals that key.

Examples:

- `group_by([1, 2, 3, 4, 5, 6], lambda x: x % 2)` -> `{1: [1, 3, 5], 0: [2, 4, 6]}`
- `group_by(["apple", "avocado", "banana"], lambda w: w[0])` -> `{"a": ["apple", "avocado"], "b": ["banana"]}`
- `group_by([], lambda x: x)` -> `{}`
- `group_by(["hi", "yo", "hey"], len)` -> `{2: ["hi", "yo"], 3: ["hey"]}`

Edge cases:

- Empty input returns an empty dict.
- Items keep their relative order within each group.
- Keys may be any hashable value (ints, strings, etc.).

Do not change the function signature. Do not add prints.
