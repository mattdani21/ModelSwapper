"""Batch report generator."""


def generate_report(rows):
    parsed = []
    for row in rows:
        row = row.strip()
        if not row:
            continue
        parts = row.split(",")
        if len(parts) != 2:
            raise ValueError(f"bad row: {row}")
        name = parts[0].strip()
        try:
            value = float(parts[1])
        except ValueError:
            raise ValueError(f"bad value: {row}") from None
        parsed.append((name, value))
    if not parsed:
        return "no data"
    total = 0.0
    for _, v in parsed:
        total += v
    count = len(parsed)
    mean = total / count
    lo = parsed[0][1]
    hi = parsed[0][1]
    for _, v in parsed:
        if v < lo:
            lo = v
        if v > hi:
            hi = v
    lines = []
    for name, v in parsed:
        lines.append(f"- {name}: {v:.2f}")
    lines.append(f"total: {total:.2f}")
    lines.append(f"mean: {mean:.2f}")
    lines.append(f"min: {lo:.2f}")
    lines.append(f"max: {hi:.2f}")
    return "\n".join(lines)
