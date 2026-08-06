"""Record lookup helpers."""


def _check_value(field, value):
    if not value:
        raise ValueError(f"empty {field}")


def _collect(records, predicate):
    return [r for r in records if predicate(r)]


def find_by_name(records, name):
    _check_value("name", name)
    return _collect(records, lambda r: r.get("name") == name)


def find_by_tag(records, tag):
    _check_value("tag", tag)
    return _collect(records, lambda r: tag in r.get("tags", []))
