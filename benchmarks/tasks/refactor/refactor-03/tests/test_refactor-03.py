import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import solution
from solution import distance_label, speed_label


def test_speed_metric_default():
    assert speed_label(100) == "100.0 km/h"


def test_distance_metric_default():
    assert distance_label(5) == "5.0 km"


def test_distance_fractional():
    assert distance_label(2.5) == "2.5 km"


def test_set_units_removed():
    assert not hasattr(solution, "set_units")


def test_global_state_removed():
    assert not hasattr(solution, "_units")


def test_helper_exists():
    assert callable(getattr(solution, "_to_imperial", None))


def test_signatures():
    sig = inspect.signature(solution.speed_label)
    assert list(sig.parameters) == ["kmh", "units"]
    assert sig.parameters["units"].default == "metric"
    sig = inspect.signature(solution.distance_label)
    assert list(sig.parameters) == ["km", "units"]
    assert sig.parameters["units"].default == "metric"


def test_conversion_factor_once():
    src = inspect.getsource(solution)
    assert src.count("0.621371") == 1
