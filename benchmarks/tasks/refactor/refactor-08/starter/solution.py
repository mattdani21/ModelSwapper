"""Shopping cart helpers backed by a module-level list."""

_cart = []


def add_item(name, price, qty=1):
    if price <= 0:
        raise ValueError("price must be positive")
    if qty <= 0:
        raise ValueError("qty must be positive")
    _cart.append({"name": name, "price": price, "qty": qty})


def set_price(name, price):
    if price <= 0:
        raise ValueError("price must be positive")
    for item in _cart:
        if item["name"] == name:
            item["price"] = price
            return
    raise KeyError(name)


def apply_discount(percent):
    if percent <= 0 or percent > 100:
        raise ValueError("percent out of range")
    for item in _cart:
        item["price"] = round(item["price"] * (1 - percent / 100), 2)


def total():
    return round(sum(item["price"] * item["qty"] for item in _cart), 2)


def clear():
    _cart.clear()
