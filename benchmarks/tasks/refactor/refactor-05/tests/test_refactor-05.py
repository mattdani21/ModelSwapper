import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import solution
from solution import process_log_line


def _raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return
    raise AssertionError("expected %s" % exc.__name__)


def test_valid_info():
    assert process_log_line("INFO|12:00:00|hello") == "12:00:00 [INFO] hello"


def test_valid_error():
    assert process_log_line("ERROR|23:59:59|boom") == "23:59:59 [ERROR] boom"


def test_fields_are_stripped():
    assert process_log_line("  WARN | 09:30:00 | slow ") == "09:30:00 [WARN] slow"


def test_wrong_field_count():
    _raises(ValueError, process_log_line, "INFO|12:00:00")


def test_unknown_level():
    _raises(ValueError, process_log_line, "FATAL|12:00:00|x")


def test_bad_timestamp():
    _raises(ValueError, process_log_line, "INFO|12:00|x")


def test_empty_message():
    _raises(ValueError, process_log_line, "INFO|12:00:00|")


def test_helpers_exist():
    assert callable(getattr(solution, "_parse_line", None))
    assert callable(getattr(solution, "_validate", None))
    assert callable(getattr(solution, "_format", None))


def test_helper_signatures():
    assert list(inspect.signature(solution._parse_line).parameters) == ["line"]
    assert list(inspect.signature(solution._validate).parameters) == ["level", "ts", "msg"]
    assert list(inspect.signature(solution._format).parameters) == ["level", "ts", "msg"]


def test_main_function_is_pure_orchestration():
    src = inspect.getsource(solution.process_log_line)
    assert "INFO" not in src
    assert "malformed" not in src


def test_validation_messages_once():
    src = inspect.getsource(solution)
    assert src.count("malformed log line") == 1
    assert src.count("unknown level") == 1
