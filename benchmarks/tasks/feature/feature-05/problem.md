# Task: invert_dict

Implement `invert_dict(d)` in `solution.py`.

Given a dictionary, return a NEW dictionary that maps each value to a list of all keys (in insertion order) that had that value. The original dictionary must not be modified.

Examples:

- `invert_dict({"a": 1, "b": 2})` -> `{1: ["a"], 2: ["b"]}`
- `invert_dict({"a": 1, "b": 1})` -> `{1: ["a", "b"]}`
- `invert_dict({})` -> `{}`
- `invert_dict({"x": "y"})` -> `{"y": ["x"]}`

Edge cases:

- When several keys share a value, their list preserves the original insertion order.
- An empty dict returns an empty dict.
- Keys and values may be any hashable type (strings, ints, tuples).

Do not change the function signature. Do not add prints.
