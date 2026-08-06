def invert_dict(d):
    """Return a new dict mapping each value to the list of keys that
    mapped to it, preserving insertion order. Does not modify d.
    """
    result = {}
    for key, value in d.items():
        result.setdefault(value, []).append(key)
    return result
