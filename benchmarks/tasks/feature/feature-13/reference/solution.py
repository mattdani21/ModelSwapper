import re


def camel_to_snake(name):
    """Convert a camelCase/PascalCase identifier to snake_case.

    Raises ValueError if name is empty.
    """
    if not name:
        raise ValueError("name must not be empty")
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()
