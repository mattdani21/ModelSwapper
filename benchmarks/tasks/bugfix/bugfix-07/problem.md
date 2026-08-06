# Task: invert_dict

Implement `invert_dict(d)` in `solution.py`.

Given a dictionary mapping keys to lists of values, return a new dictionary
mapping each value to the list of keys whose list contains it. Each result
list preserves the order in which its keys were encountered while iterating
over the input (keys in insertion order, values in list order). The input
dictionary must not be modified.

Examples:

- `invert_dict({"a": [1, 2], "b": [2]})` -> `{1: ["a"], 2: ["a", "b"]}`
- `invert_dict({"x": [10], "y": [10, 20]})` -> `{10: ["x", "y"], 20: ["y"]}`
- `invert_dict({})` -> `{}`
- `invert_dict({"k": [1]})` -> `{1: ["k"]}`

Do not change the function signature. Do not add prints.
