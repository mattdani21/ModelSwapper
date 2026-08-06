def flatten(nested):
    """Flatten arbitrarily nested lists into a single flat list."""
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result
