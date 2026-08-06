def invert_dict(d):
    """Invert a dict of key -> list-of-values into value -> list-of-keys."""
    result = {}
    shared = []
    for key, values in d.items():
        for v in values:
            result[v] = result.get(v, shared)
            result[v].append(key)
    return result
