"""Distance and speed formatting with a module-level unit setting."""

_units = "metric"


def set_units(units):
    global _units
    _units = units


def speed_label(kmh):
    if _units == "metric":
        return f"{kmh:.1f} km/h"
    return f"{kmh * 0.621371:.1f} mph"


def distance_label(km):
    if _units == "metric":
        return f"{km:.1f} km"
    return f"{km * 0.621371:.1f} miles"
