"""Shopping cart backed by a Cart class with a default instance."""


class Cart:
    def __init__(self):
        self.items = []

    def _validate_price(self, price):
        if price <= 0:
            raise ValueError("price must be positive")

    def _validate_qty(self, qty):
        if qty <= 0:
            raise ValueError("qty must be positive")

    def add(self, name, price, qty=1):
        self._validate_price(price)
        self._validate_qty(qty)
        self.items.append({"name": name, "price": price, "qty": qty})

    def set_price(self, name, price):
        self._validate_price(price)
        for item in self.items:
            if item["name"] == name:
                item["price"] = price
                return
        raise KeyError(name)

    def apply_discount(self, percent):
        if percent <= 0 or percent > 100:
            raise ValueError("percent out of range")
        for item in self.items:
            item["price"] = round(item["price"] * (1 - percent / 100), 2)

    def total(self):
        return round(sum(item["price"] * item["qty"] for item in self.items), 2)

    def clear(self):
        self.items.clear()


_store = Cart()


def add_item(name, price, qty=1):
    _store.add(name, price, qty)


def set_price(name, price):
    _store.set_price(name, price)


def apply_discount(percent):
    _store.apply_discount(percent)


def total():
    return _store.total()


def clear():
    _store.clear()
