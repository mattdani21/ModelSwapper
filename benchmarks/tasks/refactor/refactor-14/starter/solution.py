"""Event logger with module-level state."""

_level = "INFO"
_entries = []
_sequence = 0


def set_level(level):
    global _level
    if level not in ("DEBUG", "INFO", "WARN", "ERROR"):
        raise ValueError("bad level")
    _level = level


def log(level, msg):
    global _sequence
    if level not in ("DEBUG", "INFO", "WARN", "ERROR"):
        raise ValueError("bad level")
    if _level == "ERROR" and level != "ERROR":
        return
    if _level == "WARN" and level not in ("WARN", "ERROR"):
        return
    if _level == "INFO" and level not in ("INFO", "WARN", "ERROR"):
        return
    _sequence += 1
    _entries.append({"seq": _sequence, "level": level, "message": msg})


def summary():
    counts = {}
    for e in _entries:
        counts[e["level"]] = counts.get(e["level"], 0) + 1
    return counts


def recent(n):
    out = []
    for e in _entries[-n:]:
        out.append(f"[{e['seq']:03d}] {e['level']}: {e['message']}")
    return out


def drain():
    out = list(_entries)
    _entries.clear()
    return out
