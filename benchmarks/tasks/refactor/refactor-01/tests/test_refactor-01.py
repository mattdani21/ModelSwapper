import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import solution
from solution import login_user, register_user


def _raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return
    raise AssertionError("expected %s" % exc.__name__)


def test_register_ok():
    assert register_user("  Alice  ", " Alice@Example.com ") == {
        "action": "register",
        "username": "Alice",
        "email": "alice@example.com",
    }


def test_login_ok():
    assert login_user("bob", "bob@site.io") == {
        "action": "login",
        "username": "bob",
        "email": "bob@site.io",
    }


def test_register_short_name_rejected():
    _raises(ValueError, register_user, "ab", "a@b.co")


def test_register_empty_email_rejected():
    _raises(ValueError, register_user, "alice", "")


def test_login_bad_email_rejected():
    _raises(ValueError, login_user, "bob", "a@b@c")


def test_name_with_inner_spaces_allowed():
    assert register_user("Ann Lee", "ann@x.io")["username"] == "Ann Lee"


def test_helper_exists():
    assert callable(getattr(solution, "validate_credentials", None))


def test_helper_signature():
    sig = inspect.signature(solution.validate_credentials)
    assert list(sig.parameters) == ["name", "email"]


def test_validation_not_duplicated():
    src = inspect.getsource(solution)
    assert src.count("isalnum") == 1
    assert src.count("invalid username") == 1


def test_public_functions_delegate():
    assert "isalnum" not in inspect.getsource(solution.register_user)
    assert "isalnum" not in inspect.getsource(solution.login_user)
