"""Statistical helpers."""


def _mean(values):
    return sum(values) / len(values)


def _variance(values):
    m = _mean(values)
    return sum((v - m) ** 2 for v in values) / len(values)


def summarize(values):
    if not values:
        return None
    return {"mean": _mean(values), "variance": _variance(values)}


def analyze(values):
    if not values:
        return None
    return {"mean": _mean(values), "variance": _variance(values), "count": len(values)}
