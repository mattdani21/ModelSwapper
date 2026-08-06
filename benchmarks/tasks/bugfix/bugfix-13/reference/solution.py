def camel_to_snake(s):
    """Convert a camelCase/PascalCase identifier to snake_case."""
    parts = []
    for i, c in enumerate(s):
        if c.isupper() and i > 0 and (
            s[i - 1].islower() or (i + 1 < len(s) and s[i + 1].islower())
        ):
            parts.append("_")
        parts.append(c.lower())
    return "".join(parts)
