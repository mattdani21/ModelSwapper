import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import parse_csv_line


def test_plain_fields():
    assert parse_csv_line("a,b,c") == ["a", "b", "c"]


def test_quoted_field_with_comma():
    assert parse_csv_line('"a,b",c') == ["a,b", "c"]


def test_escaped_quotes():
    assert parse_csv_line('"a ""quoted"" word",x') == ['a "quoted" word', "x"]


def test_unquoted_whitespace_trimmed():
    assert parse_csv_line("  a  ,  b  ") == ["a", "b"]


def test_quoted_whitespace_preserved():
    assert parse_csv_line('" spaced out ",plain') == [" spaced out ", "plain"]


def test_empty_quoted_field():
    assert parse_csv_line('""') == [""]


def test_empty_line():
    assert parse_csv_line("") == [""]


def test_trailing_comma():
    assert parse_csv_line("a,") == ["a", ""]


def test_multi_quoted():
    assert parse_csv_line('a,"b,c",d') == ["a", "b,c", "d"]


def test_quoted_field_containing_quotes_and_comma():
    assert parse_csv_line('"say ""hi"", then go",x') == ['say "hi", then go', 'x']
