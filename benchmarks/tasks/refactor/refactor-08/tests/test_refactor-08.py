import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import solution
from solution import add_item, apply_discount, clear, set_price, total


def _raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return
    raise AssertionError("expected %s" % exc.__name__)


def test_add_and_total():
    clear()
    add_item("apple", 1.5, 2)
    add_item("pear", 2.0)
    assert total() == 5.0


def test_set_price():
    clear()
    add_item("apple", 1.5, 2)
    set_price("apple", 2.5)
    assert total() == 5.0


def test_apply_discount():
    clear()
    add_item("apple", 20.0, 3)
    apply_discount(10)
    assert total() == 54.0


def test_clear():
    clear()
    add_item("apple", 1.0)
    clear()
    assert total() == 0.0


def test_add_rejects_bad_price():
    clear()
    _raises(ValueError, add_item, "apple", 0)
    _raises(ValueError, add_item, "apple", -1)


def test_add_rejects_bad_qty():
    clear()
    _raises(ValueError, add_item, "apple", 1.0, 0)


def test_set_price_rejects_bad_price():
    clear()
    add_item("apple", 1.0)
    _raises(ValueError, set_price, "apple", 0)


def test_set_price_missing_key():
    clear()
    _raises(KeyError, set_price, "nope", 1.0)


def test_discount_out_of_range():
    clear()
    add_item("apple", 1.0)
    _raises(ValueError, apply_discount, 0)
    _raises(ValueError, apply_discount, 101)


def test_cart_class_exists():
    assert inspect.isclass(getattr(solution, "Cart", None))
    for m in ("add", "set_price", "apply_discount", "total", "clear"):
        assert callable(getattr(solution.Cart, m, None))


def test_default_store_is_cart_instance():
    store = getattr(solution, "_store", None)
    cart_cls = getattr(solution, "Cart", None)
    assert cart_cls is not None
    assert isinstance(store, cart_cls)


def test_raw_global_removed():
    assert not hasattr(solution, "_cart")


def test_price_validation_once():
    src = inspect.getsource(solution)
    assert src.count("price must be positive") == 1
