"""Batch report generator."""


def _parse_row(row):
    row = row.strip()
    if not row:
        return None
    parts = row.split(",")
    if len(parts) != 2:
        raise ValueError(f"bad row: {row}")
    name = parts[0].strip()
    try:
        value = float(parts[1])
    except ValueError:
        raise ValueError(f"bad value: {row}") from None
    return name, value


def _aggregate(parsed):
    values = [v for _, v in parsed]
    total = sum(values)
    return {
        "count": len(values),
        "total": total,
        "mean": total / len(values),
        "min": min(values),
        "max": max(values),
    }


def _format_report(parsed, stats):
    lines = [f"- {name}: {v:.2f}" for name, v in parsed]
    lines.append(f"total: {stats['total']:.2f}")
    lines.append(f"mean: {stats['mean']:.2f}")
    lines.append(f"min: {stats['min']:.2f}")
    lines.append(f"max: {stats['max']:.2f}")
    return "\n".join(lines)


def generate_report(rows):
    parsed = [p for p in (_parse_row(r) for r in rows) if p is not None]
    if not parsed:
        return "no data"
    return _format_report(parsed, _aggregate(parsed))
