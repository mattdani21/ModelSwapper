import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import solution
from solution import print_csv, print_table


def test_table_basic(capsys):
    print_table([(1, 2), (3, 4)])
    assert capsys.readouterr().out.splitlines() == ["| 1 | 2 |", "| 3 | 4 |"]


def test_table_mixed_types(capsys):
    print_table([("a", 1)])
    assert capsys.readouterr().out.splitlines() == ["| a | 1 |"]


def test_csv_basic(capsys):
    print_csv([(1, 2), (3, 4)])
    assert capsys.readouterr().out.splitlines() == ["1,2", "3,4"]


def test_csv_mixed_types(capsys):
    print_csv([("a", 2.5)])
    assert capsys.readouterr().out.splitlines() == ["a,2.5"]


def test_empty_rows(capsys):
    print_table([])
    print_csv([])
    assert capsys.readouterr().out == ""


def test_render_row_direct():
    fn = getattr(solution, "_render_row", None)
    assert fn is not None
    assert fn([1, "x"], "|") == "1|x"
    assert fn([1, 2], ",", wrap=" ") == " 1 , 2 "


def test_render_row_signature():
    fn = getattr(solution, "_render_row", None)
    assert fn is not None
    sig = inspect.signature(fn)
    assert list(sig.parameters) == ["cells", "sep", "wrap"]
    assert sig.parameters["wrap"].default is None


def test_conversion_not_duplicated():
    src = inspect.getsource(solution)
    assert src.count("str(c) for c in") == 1
