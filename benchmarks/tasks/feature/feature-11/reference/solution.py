import math


def format_bytes(n):
    """Format a byte count as a human-readable binary-unit string.

    Units: B, KB, MB, GB, TB (1024-based). Raises ValueError if n < 0.
    """
    if n < 0:
        raise ValueError("n must be >= 0")
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(n)
    unit = units[0]
    for u in units:
        if value < 1024 or u == units[-1]:
            unit = u
            break
        value /= 1024.0
    if unit == "B":
        return f"{n} B"
    rounded = math.floor(value * 10 + 0.5) / 10
    return f"{rounded:.1f} {unit}"
