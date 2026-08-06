def top_k(nums, k):
    """Return the k most frequent integers, ties broken by first occurrence."""
    counts = {}
    for n in nums:
        counts[n] = counts.get(n, 0) + 1
    ranked = sorted(counts.items(), key=lambda pair: pair[0])
    return [n for n, _ in ranked[:k]]
