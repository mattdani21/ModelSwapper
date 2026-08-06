import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import solution
from solution import process_command


def _raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return
    raise AssertionError("expected %s" % exc.__name__)


def test_add():
    ctx = {}
    assert process_command("add", ["k", "v"], ctx) == "added k"
    assert ctx == {"k": "v"}


def test_add_overwrites():
    ctx = {"k": "old"}
    assert process_command("add", ["k", "new"], ctx) == "added k"
    assert ctx == {"k": "new"}


def test_del():
    ctx = {"k": "v"}
    assert process_command("del", ["k"], ctx) == "deleted k"
    assert ctx == {}


def test_set():
    ctx = {"k": "old"}
    assert process_command("set", ["k", "new"], ctx) == "updated k"
    assert ctx == {"k": "new"}


def test_del_missing_key():
    _raises(KeyError, process_command, "del", ["k"], {})


def test_set_missing_key():
    _raises(KeyError, process_command, "set", ["k", "v"], {})


def test_arity_errors():
    try:
        process_command("add", ["only-one"], {})
    except ValueError as e:
        assert str(e) == "add expects 2 arguments"
    else:
        raise AssertionError("expected ValueError")
    _raises(ValueError, process_command, "del", ["a", "b"], {})
    _raises(ValueError, process_command, "set", ["a"], {})


def test_unknown_command():
    try:
        process_command("rm", [], {})
    except ValueError as e:
        assert str(e) == "unknown command rm"
    else:
        raise AssertionError("expected ValueError")


def test_helpers_exist():
    for name in ("_validate_args", "_require_key", "_handle_add", "_handle_del", "_handle_set"):
        assert callable(getattr(solution, name, None))


def test_dispatch_tables():
    handlers = getattr(solution, "_HANDLERS", None)
    arity = getattr(solution, "_ARITY", None)
    assert isinstance(handlers, dict)
    assert set(handlers) == {"add", "del", "set"}
    assert arity == {"add": 2, "del": 1, "set": 2}


def test_main_function_is_dispatch_only():
    src = inspect.getsource(solution.process_command)
    assert "added " not in src
    assert "deleted " not in src
    assert "updated " not in src
    assert "KeyError" not in src


def test_logic_not_duplicated():
    src = inspect.getsource(solution)
    assert src.count("expects ") == 1
    assert src.count("raise KeyError(key)") == 1
