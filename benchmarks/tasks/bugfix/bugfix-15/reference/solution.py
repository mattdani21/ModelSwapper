def longest_unique_substring(s):
    """Return the length of the longest substring without repeating chars."""
    seen = {}
    start = 0
    best = 0
    for i, c in enumerate(s):
        if c in seen and seen[c] >= start:
            start = seen[c] + 1
        seen[c] = i
        best = max(best, i - start + 1)
    return best
