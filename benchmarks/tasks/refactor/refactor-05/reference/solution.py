"""Log line processing."""

_LEVELS = ("INFO", "WARN", "ERROR")


def _parse_line(line):
    parts = line.strip().split("|")
    if len(parts) != 3:
        raise ValueError("malformed log line")
    return [p.strip() for p in parts]


def _validate(level, ts, msg):
    if level not in _LEVELS:
        raise ValueError("unknown level")
    if not ts or len(ts) != 8:
        raise ValueError("bad timestamp")
    if not msg:
        raise ValueError("empty message")


def _format(level, ts, msg):
    return f"{ts} [{level}] {msg}"


def process_log_line(line):
    level, ts, msg = _parse_line(line)
    _validate(level, ts, msg)
    return _format(level, ts, msg)
