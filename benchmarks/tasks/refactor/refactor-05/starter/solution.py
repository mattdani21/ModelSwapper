"""Log line processing."""


def process_log_line(line):
    parts = line.strip().split("|")
    if len(parts) != 3:
        raise ValueError("malformed log line")
    level = parts[0].strip()
    if level not in ("INFO", "WARN", "ERROR"):
        raise ValueError("unknown level")
    ts = parts[1].strip()
    if not ts or len(ts) != 8:
        raise ValueError("bad timestamp")
    msg = parts[2].strip()
    if not msg:
        raise ValueError("empty message")
    return f"{ts} [{level}] {msg}"
