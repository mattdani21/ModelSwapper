import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import solution
from solution import load_products, load_users


def _write(tmp_path, text):
    p = tmp_path / "data.tsv"
    p.write_text(text)
    return str(p)


def test_load_users(tmp_path):
    path = _write(tmp_path, "# users\n\nalice\t30\nbob\t25\n")
    assert load_users(path) == [
        {"name": "alice", "age": 30},
        {"name": "bob", "age": 25},
    ]


def test_load_products(tmp_path):
    path = _write(tmp_path, "# products\nsku-1\t1.50\nsku-2\t2.25\n")
    assert load_products(path) == [
        {"sku": "sku-1", "price": 1.5},
        {"sku": "sku-2", "price": 2.25},
    ]


def test_cells_are_stripped(tmp_path):
    path = _write(tmp_path, " alice \t 30 \n")
    assert load_users(path) == [{"name": "alice", "age": 30}]


def test_empty_file(tmp_path):
    path = _write(tmp_path, "# nothing\n\n")
    assert load_users(path) == []


def test_bad_row_raises(tmp_path):
    path = _write(tmp_path, "alice\t30\textra\n")
    try:
        load_users(path)
    except ValueError as e:
        assert str(e) == "bad row: alice\t30\textra"
    else:
        raise AssertionError("expected ValueError")


def test_helpers_exist():
    assert callable(getattr(solution, "_read_rows", None))
    assert callable(getattr(solution, "_split_row", None))


def test_helper_signatures():
    assert list(inspect.signature(solution._read_rows).parameters) == ["path"]
    assert list(inspect.signature(solution._split_row).parameters) == ["line"]


def test_parsing_not_duplicated():
    src = inspect.getsource(solution)
    assert src.count('line.startswith("#")') == 1
    assert src.count("bad row") == 1
