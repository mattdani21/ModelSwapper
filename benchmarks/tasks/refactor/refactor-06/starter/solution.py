"""Loaders for tab-separated data files."""


def load_users(path):
    users = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("\t")]
            if len(parts) != 2:
                raise ValueError(f"bad row: {line}")
            users.append({"name": parts[0], "age": int(parts[1])})
    return users


def load_products(path):
    products = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("\t")]
            if len(parts) != 2:
                raise ValueError(f"bad row: {line}")
            products.append({"sku": parts[0], "price": float(parts[1])})
    return products
