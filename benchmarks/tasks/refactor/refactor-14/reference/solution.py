"""Event logger. State lives in a Logger instance; module keeps one for compatibility."""

_SEVERITY = {"DEBUG": 0, "INFO": 1, "WARN": 2, "ERROR": 3}


class Logger:
    def __init__(self, level="INFO"):
        self.level = self._check_level(level)
        self._entries = []
        self._sequence = 0

    def _check_level(self, level):
        if level not in _SEVERITY:
            raise ValueError("bad level")
        return level

    def _passes(self, level):
        return _SEVERITY[level] >= _SEVERITY[self.level]

    def set_level(self, level):
        self.level = self._check_level(level)

    def log(self, level, msg):
        level = self._check_level(level)
        if not self._passes(level):
            return
        self._sequence += 1
        self._entries.append({"seq": self._sequence, "level": level, "message": msg})

    def summary(self):
        counts = {}
        for e in self._entries:
            counts[e["level"]] = counts.get(e["level"], 0) + 1
        return counts

    def recent(self, n):
        out = []
        for e in self._entries[-n:]:
            out.append(f"[{e['seq']:03d}] {e['level']}: {e['message']}")
        return out

    def drain(self):
        out = list(self._entries)
        self._entries.clear()
        return out


_store = Logger()


def set_level(level):
    _store.set_level(level)


def log(level, msg):
    _store.log(level, msg)


def summary():
    return _store.summary()


def recent(n):
    return _store.recent(n)


def drain():
    return _store.drain()
