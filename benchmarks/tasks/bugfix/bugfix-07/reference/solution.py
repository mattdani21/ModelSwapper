def invert_dict(d):
    """Invert a dict of key -> list-of-values into value -> list-of-keys."""
    result = {}
    for key, values in d.items():
        for v in values:
            result.setdefault(v, []).append(key)
    return result
