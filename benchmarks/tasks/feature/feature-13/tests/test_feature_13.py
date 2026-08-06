import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from solution import camel_to_snake


def test_camel_case():
    assert camel_to_snake("camelCase") == "camel_case"


def test_pascal_case():
    assert camel_to_snake("PascalCase") == "pascal_case"


def test_acronym_prefix():
    assert camel_to_snake("HTTPResponse") == "http_response"


def test_acronym_mid_word():
    assert camel_to_snake("getHTTPResponseCode") == "get_http_response_code"


def test_simple_word():
    assert camel_to_snake("simple") == "simple"


def test_all_caps_word():
    assert camel_to_snake("ABC") == "abc"


def test_single_letter():
    assert camel_to_snake("A") == "a"


def test_digits():
    assert camel_to_snake("version2Value") == "version2_value"


def test_digits_no_trigger():
    assert camel_to_snake("v2") == "v2"


def test_lowercase_first_with_acronym():
    assert camel_to_snake("parseXMLFile") == "parse_xml_file"


def test_empty_raises():
    with pytest.raises(ValueError):
        camel_to_snake("")
