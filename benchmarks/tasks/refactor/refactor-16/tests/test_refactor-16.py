import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import solution
from solution import generate_report


def _raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return
    raise AssertionError("expected %s" % exc.__name__)


def test_basic_report():
    rows = ["apple,1.5", "banana,2.5", "cherry,4.0"]
    expected = "\n".join([
        "- apple: 1.50",
        "- banana: 2.50",
        "- cherry: 4.00",
        "total: 8.00",
        "mean: 2.67",
        "min: 1.50",
        "max: 4.00",
    ])
    assert generate_report(rows) == expected


def test_blank_rows_skipped():
    rows = ["", "apple,1.5", "   ", "banana,2.5"]
    expected = "\n".join([
        "- apple: 1.50",
        "- banana: 2.50",
        "total: 4.00",
        "mean: 2.00",
        "min: 1.50",
        "max: 2.50",
    ])
    assert generate_report(rows) == expected


def test_all_blank():
    assert generate_report(["", "  "]) == "no data"


def test_empty_input():
    assert generate_report([]) == "no data"


def test_single_item():
    expected = "\n".join([
        "- only: 7.00",
        "total: 7.00",
        "mean: 7.00",
        "min: 7.00",
        "max: 7.00",
    ])
    assert generate_report(["only,7"]) == expected


def test_negative_values():
    expected = "\n".join([
        "- a: -2.50",
        "- b: 1.50",
        "total: -1.00",
        "mean: -0.50",
        "min: -2.50",
        "max: 1.50",
    ])
    assert generate_report(["a,-2.5", "b,1.5"]) == expected


def test_bad_row_raises():
    _raises(ValueError, generate_report, ["a,1,b"])


def test_bad_value_raises():
    _raises(ValueError, generate_report, ["a,xyz"])


def test_whitespace_in_cells():
    expected = "\n".join([
        "- apple: 1.50",
        "total: 1.50",
        "mean: 1.50",
        "min: 1.50",
        "max: 1.50",
    ])
    assert generate_report(["  apple , 1.5 "]) == expected


def test_helpers_exist():
    for name in ("_parse_row", "_aggregate", "_format_report"):
        assert callable(getattr(solution, name, None))


def test_helper_signatures():
    assert list(inspect.signature(solution._parse_row).parameters) == ["row"]
    assert list(inspect.signature(solution._aggregate).parameters) == ["parsed"]
    assert list(inspect.signature(solution._format_report).parameters) == ["parsed", "stats"]


def test_main_function_is_pipeline_only():
    src = inspect.getsource(solution.generate_report)
    assert ".2f" not in src
    assert "float(" not in src
    assert "bad row" not in src
    assert "min(" not in src
