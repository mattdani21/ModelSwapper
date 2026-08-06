def merge_intervals(intervals):
    """Merge overlapping or touching [start, end] intervals.

    Returns merged intervals sorted by start. Raises ValueError if any
    interval has start > end.
    """
    for start, end in intervals:
        if start > end:
            raise ValueError("interval start must not exceed end")
    if not intervals:
        return []
    ordered = sorted(intervals, key=lambda iv: iv[0])
    merged = [list(ordered[0])]
    for start, end in ordered[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
