import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import solution
from solution import handle_request


def _raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return
    raise AssertionError("expected %s" % exc.__name__)


def test_success_alice():
    assert handle_request("tok-1|alice|10") == "alice:90.00"


def test_success_bob():
    assert handle_request("tok-2|bob|12.5") == "bob:37.50"


def test_fields_stripped():
    assert handle_request(" tok-1 | alice | 10 ") == "alice:90.00"


def test_exact_balance_allowed():
    assert handle_request("tok-1|alice|100") == "alice:0.00"


def test_malformed():
    _raises(ValueError, handle_request, "tok-1|alice")


def test_bad_token():
    _raises(PermissionError, handle_request, "wrong|alice|10")


def test_unknown_account():
    _raises(PermissionError, handle_request, "tok-9|mallory|1")


def test_bad_amount():
    _raises(ValueError, handle_request, "tok-1|alice|abc")
    _raises(ValueError, handle_request, "tok-1|alice|-5")


def test_insufficient_funds():
    _raises(ValueError, handle_request, "tok-1|alice|101")


def test_helpers_exist():
    for name in ("_parse", "_authorize", "_apply", "_format"):
        assert callable(getattr(solution, name, None))


def test_helper_signatures():
    assert list(inspect.signature(solution._parse).parameters) == ["raw"]
    assert list(inspect.signature(solution._authorize).parameters) == ["account", "token"]
    assert list(inspect.signature(solution._apply).parameters) == ["account", "amount"]
    assert list(inspect.signature(solution._format).parameters) == ["account", "new_balance"]


def test_main_function_is_orchestration_only():
    src = inspect.getsource(solution.handle_request)
    assert "bad token" not in src
    assert "insufficient funds" not in src
    assert "float(" not in src
