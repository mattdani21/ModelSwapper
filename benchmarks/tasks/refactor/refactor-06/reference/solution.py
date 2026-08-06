"""Loaders for tab-separated data files."""


def _read_rows(path):
    """Yield cleaned non-empty, non-comment lines from a TSV file."""
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            yield line


def _split_row(line):
    parts = [p.strip() for p in line.split("\t")]
    if len(parts) != 2:
        raise ValueError(f"bad row: {line}")
    return parts


def load_users(path):
    users = []
    for line in _read_rows(path):
        name, age = _split_row(line)
        users.append({"name": name, "age": int(age)})
    return users


def load_products(path):
    products = []
    for line in _read_rows(path):
        sku, price = _split_row(line)
        products.append({"sku": sku, "price": float(price)})
    return products
