import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import parse_csv


def test_simple():
    assert parse_csv("a,b,c") == [["a", "b", "c"]]


def test_quoted_comma():
    assert parse_csv('"x,y",z') == [["x,y", "z"]]


def test_escaped_quote():
    assert parse_csv('"a""b",c') == [['a"b', "c"]]


def test_only_escaped_quotes():
    assert parse_csv('"a""b""c"') == [['a"b"c']]


def test_quote_in_unquoted_field():
    assert parse_csv('ab"cd,e') == [['ab"cd', "e"]]


def test_empty_field():
    assert parse_csv('"",x') == [["", "x"]]


def test_multiline():
    assert parse_csv("a,b\nc,d") == [["a", "b"], ["c", "d"]]


def test_empty_input():
    assert parse_csv("") == []
