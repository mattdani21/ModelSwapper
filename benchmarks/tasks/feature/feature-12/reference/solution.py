def group_by(items, key_fn):
    """Group items by key_fn(item), preserving original order within groups.

    Returns a dict mapping key -> list of items.
    """
    result = {}
    for item in items:
        result.setdefault(key_fn(item), []).append(item)
    return result
