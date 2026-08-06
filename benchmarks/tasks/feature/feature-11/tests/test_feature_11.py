import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from solution import format_bytes


def test_zero():
    assert format_bytes(0) == "0 B"


def test_small():
    assert format_bytes(500) == "500 B"


def test_just_below_kb():
    assert format_bytes(1023) == "1023 B"


def test_exact_kb():
    assert format_bytes(1024) == "1.0 KB"


def test_one_and_a_half_kb():
    assert format_bytes(1536) == "1.5 KB"


def test_exact_mb():
    assert format_bytes(1048576) == "1.0 MB"


def test_one_and_a_half_mb():
    assert format_bytes(1572864) == "1.5 MB"


def test_gb():
    assert format_bytes(1610612736) == "1.5 GB"


def test_tb():
    assert format_bytes(1099511627776) == "1.0 TB"


def test_three_and_a_half_kb():
    assert format_bytes(3584) == "3.5 KB"


def test_negative_raises():
    with pytest.raises(ValueError):
        format_bytes(-1)
