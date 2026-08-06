import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import solution
from solution import print_inventory, print_scores


def test_print_inventory(capsys):
    print_inventory([("apple", 3), ("pear", 12)])
    out = capsys.readouterr().out
    assert out.splitlines() == [
        "INVENTORY",
        "=" * 20,
        "apple" + " " * 13 + "3",
        "pear" + " " * 13 + "12",
        "",
    ]


def test_print_scores(capsys):
    print_scores([("ada", 98), ("lin", 100)])
    out = capsys.readouterr().out
    assert out.splitlines() == [
        "SCORES",
        "=" * 20,
        "ada" + " " * 14 + "98",
        "lin" + " " * 13 + "100",
        "",
    ]


def test_empty_input(capsys):
    print_inventory([])
    print_scores([])
    assert capsys.readouterr().out.splitlines() == ["INVENTORY", "=" * 20, "", "SCORES", "=" * 20, ""]


def test_format_row_basic():
    fn = getattr(solution, "format_row", None)
    assert fn is not None
    assert fn("apple", 3) == "apple" + " " * 13 + "3"


def test_format_row_long_name():
    fn = getattr(solution, "format_row", None)
    assert fn is not None
    assert fn("watermelon", 7) == "watermelon" + " " * 8 + "7"


def test_format_row_big_value():
    fn = getattr(solution, "format_row", None)
    assert fn is not None
    assert fn("x", 12345) == "x" + " " * 13 + "12345"


def test_format_row_exists():
    assert callable(getattr(solution, "format_row", None))


def test_format_row_signature():
    fn = getattr(solution, "format_row", None)
    assert fn is not None
    sig = inspect.signature(fn)
    assert list(sig.parameters) == ["name", "value"]


def test_formatting_not_duplicated():
    src = inspect.getsource(solution)
    assert src.count("{name:<12} {value:>6}") == 1
