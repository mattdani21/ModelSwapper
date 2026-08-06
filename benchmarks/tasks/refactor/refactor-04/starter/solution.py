"""Statistical helpers."""


def summarize(values):
    if not values:
        return None
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / len(values)
    return {"mean": mean, "variance": var}


def analyze(values):
    if not values:
        return None
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / len(values)
    return {"mean": mean, "variance": var, "count": len(values)}
