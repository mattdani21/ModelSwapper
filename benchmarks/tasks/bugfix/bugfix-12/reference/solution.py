def top_k(nums, k):
    """Return the k most frequent integers, ties broken by first occurrence."""
    counts = {}
    order = []
    for n in nums:
        if n not in counts:
            counts[n] = 0
            order.append(n)
        counts[n] += 1
    ranked = sorted(order, key=lambda n: counts[n], reverse=True)
    return ranked[:k]
