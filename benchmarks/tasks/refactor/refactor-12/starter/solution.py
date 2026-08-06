"""Record lookup helpers."""


def find_by_name(records, name):
    if not name:
        raise ValueError("empty name")
    query = f"name={name}"
    results = []
    for r in records:
        if r.get("name") == name:
            results.append(r)
    return results


def find_by_tag(records, tag):
    if not tag:
        raise ValueError("empty tag")
    query = f"tag={tag}"
    results = []
    for r in records:
        if tag in r.get("tags", []):
            results.append(r)
    return results
