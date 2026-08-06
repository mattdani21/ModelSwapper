# Task: remove module-level unit state

`solution.py` formats speeds and distances. It keeps a mutable module-level
setting `_units` plus a `set_units(units)` function that mutates it, and the
two formatting functions read that global. Module-level mutable state makes
the module hard to test and reason about.

Refactor the module so that:

- Delete `set_units` and the module-level `_units` variable entirely.
- `speed_label(kmh, units="metric")` and `distance_label(km, units="metric")`
  keep their behavior but take `units` as an explicit keyword parameter with
  default `"metric"`.
- Extract the miles-per-unit conversion into a helper `_to_imperial(value)`
  that multiplies by the conversion factor used today (0.621371), so the
  conversion factor appears exactly once in the file.
- Output strings are unchanged: metric `"{value:.1f} km/h"` / `"{value:.1f}
  km"`, imperial `"{value:.1f} mph"` / `"{value:.1f} miles"`.

Do not change the formatted output strings. Stdlib only.
