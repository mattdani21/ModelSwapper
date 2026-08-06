import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import solution
from solution import drain, log, recent, set_level, summary


def _raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return
    raise AssertionError("expected %s" % exc.__name__)


def test_log_and_recent():
    set_level("DEBUG")
    drain()
    log("INFO", "hello")
    log("WARN", "careful")
    lines = recent(2)
    assert len(lines) == 2
    assert lines[0].endswith("INFO: hello")
    assert lines[1].endswith("WARN: careful")
    seqs = [int(line[1:4]) for line in lines]
    assert seqs[1] == seqs[0] + 1
    assert lines[0] == f"[{seqs[0]:03d}] INFO: hello"


def test_summary():
    set_level("DEBUG")
    drain()
    log("INFO", "a")
    log("ERROR", "b")
    log("INFO", "c")
    assert summary() == {"INFO": 2, "ERROR": 1}


def test_drain_returns_and_clears():
    set_level("DEBUG")
    drain()
    log("INFO", "x")
    log("ERROR", "y")
    entries = drain()
    assert [e["message"] for e in entries] == ["x", "y"]
    assert [e["level"] for e in entries] == ["INFO", "ERROR"]
    assert summary() == {}


def test_sequence_continues_across_drain():
    set_level("DEBUG")
    drain()
    log("INFO", "first")
    first = drain()
    log("INFO", "second")
    second = drain()
    assert second[0]["seq"] == first[0]["seq"] + 1


def test_level_filter_info():
    set_level("INFO")
    drain()
    log("DEBUG", "hidden")
    log("INFO", "shown")
    log("ERROR", "boom")
    assert summary() == {"INFO": 1, "ERROR": 1}


def test_level_filter_warn():
    set_level("WARN")
    drain()
    log("INFO", "a")
    log("WARN", "b")
    log("ERROR", "c")
    assert summary() == {"WARN": 1, "ERROR": 1}


def test_level_filter_error():
    set_level("ERROR")
    drain()
    log("INFO", "a")
    log("ERROR", "b")
    assert summary() == {"ERROR": 1}


def test_recent_beyond_available():
    set_level("DEBUG")
    drain()
    log("INFO", "only")
    assert recent(5) == recent(1)


def test_bad_level():
    _raises(ValueError, set_level, "FATAL")
    _raises(ValueError, log, "FATAL", "x")


def test_logger_class_exists():
    assert inspect.isclass(getattr(solution, "Logger", None))
    for m in ("set_level", "log", "summary", "recent", "drain"):
        assert callable(getattr(solution.Logger, m, None))


def test_default_store_is_logger():
    store = getattr(solution, "_store", None)
    logger_cls = getattr(solution, "Logger", None)
    assert logger_cls is not None
    assert isinstance(store, logger_cls)


def test_globals_removed():
    assert not hasattr(solution, "_level")
    assert not hasattr(solution, "_entries")
    assert not hasattr(solution, "_sequence")


def test_severity_mapping_exists():
    sev = getattr(solution, "_SEVERITY", None)
    assert isinstance(sev, dict)
    assert sev["DEBUG"] < sev["INFO"] < sev["WARN"] < sev["ERROR"]


def test_level_validation_once():
    src = inspect.getsource(solution)
    assert src.count('raise ValueError("bad level")') == 1
