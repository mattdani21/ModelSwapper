def two_sum(nums, target):
    """Return (i, j) with i < j of the two distinct elements summing to
    target, or None if no such pair exists.
    """
    seen = {}
    for j, x in enumerate(nums):
        need = target - x
        if need in seen:
            return (seen[need], j)
        seen[x] = j
    return None
