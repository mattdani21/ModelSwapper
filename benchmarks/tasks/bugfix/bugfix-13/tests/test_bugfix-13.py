import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution import camel_to_snake


def test_simple_camel():
    assert camel_to_snake("camelCase") == "camel_case"


def test_pascal():
    assert camel_to_snake("PascalCase") == "pascal_case"


def test_two_words():
    assert camel_to_snake("aB") == "a_b"


def test_lowercase_only():
    assert camel_to_snake("simple") == "simple"


def test_all_caps():
    assert camel_to_snake("ABC") == "abc"


def test_acronym_prefix():
    assert camel_to_snake("HTTPServer") == "http_server"


def test_acronym_prefix_parser():
    assert camel_to_snake("XMLParser") == "xml_parser"


def test_acronym_middle():
    assert camel_to_snake("XMLHttpRequest") == "xml_http_request"
