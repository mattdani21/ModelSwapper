"""Distance and speed formatting. Units are explicit; no module state."""


def _to_imperial(value):
    return value * 0.621371


def speed_label(kmh, units="metric"):
    if units == "metric":
        return f"{kmh:.1f} km/h"
    return f"{_to_imperial(kmh):.1f} mph"


def distance_label(km, units="metric"):
    if units == "metric":
        return f"{km:.1f} km"
    return f"{_to_imperial(km):.1f} miles"
