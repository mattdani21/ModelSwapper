# Task: extract a Cart class

`solution.py` is a shopping-cart module built on a module-level list `_cart`
with free functions `add_item`, `set_price`, `apply_discount`, `total`,
`clear`. The price-positivity check is duplicated inside `add_item` and
`set_price`, and every function reaches into the raw list.

Refactor the module so that:

- Add a class `Cart` whose instances hold the items in an `items` attribute.
  `Cart` provides methods `add(name, price, qty=1)`, `set_price(name, price)`,
  `apply_discount(percent)`, `total()`, and `clear()` with the current
  behavior of the free functions (same validations, same rounding, same
  `ValueError`/`KeyError` messages).
- The price-positivity validation must appear exactly once in the file,
  inside a private `Cart` method (e.g. `_validate_price`) used by both `add`
  and `set_price`.
- Keep the module-level functions `add_item`, `set_price`, `apply_discount`,
  `total`, `clear` with their exact signatures as thin wrappers that delegate
  to a single module-level default instance named `_store` of the new class.
- The raw module-level list `_cart` must be removed.

Do not change behavior. Stdlib only.
