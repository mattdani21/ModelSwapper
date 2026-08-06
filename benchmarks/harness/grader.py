"""Benchmark grader — SACRED (ADR-0003, MASTER-PROMPT.md §4).

Grading contract: replace starter/solution.py with the candidate output,
run pytest on tests/, ALL tests green = PASS. This code is never modified
to make results pass; it only gets harder or broader.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Optional

REQUIRED_FILES = ["problem.md", "starter/solution.py", "reference/solution.py", "meta.json"]
SOLUTION_FILE = "solution.py"


def task_dir_ok(task_dir: str) -> list[str]:
    """Structural check of a task dir; returns list of problems (empty = ok)."""
    problems = []
    for rel in REQUIRED_FILES:
        if not os.path.exists(os.path.join(task_dir, rel)):
            problems.append(f"missing {rel}")
    tests_dir = os.path.join(task_dir, "tests")
    if not os.path.isdir(tests_dir):
        problems.append("missing tests/ dir")
    else:
        test_files = [f for f in os.listdir(tests_dir) if f.startswith("test_") and f.endswith(".py")]
        if not test_files:
            problems.append("tests/ has no test_*.py files")
    meta_path = os.path.join(task_dir, "meta.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path) as f:
                json.load(f)
        except Exception as e:  # noqa: BLE001
            problems.append(f"meta.json invalid: {e}")
    return problems


def load_meta(task_dir: str) -> dict:
    with open(os.path.join(task_dir, "meta.json")) as f:
        return json.load(f)


def _run_pytest(sandbox: str, timeout: int) -> tuple[int, str, float]:
    t0 = time.monotonic()
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q", "--no-header", "-p", "no:cacheprovider"],
        cwd=sandbox,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    dt = time.monotonic() - t0
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    return proc.returncode, out, dt


def parse_pytest_summary(out: str) -> tuple[int, int]:
    passed = failed = 0
    m = re.search(r"(\d+) passed", out)
    if m:
        passed = int(m.group(1))
    m = re.search(r"(\d+) failed", out)
    if m:
        failed = int(m.group(1))
    return passed, failed


def grade(
    task_dir: str,
    solution_text: Optional[str] = None,
    solution_path: Optional[str] = None,
    timeout: int = 120,
) -> dict:
    """Grade one candidate solution. Pass exactly one of text/path."""
    if (solution_text is None) == (solution_path is None):
        raise ValueError("pass exactly one of solution_text/solution_path")
    problems = task_dir_ok(task_dir)
    if problems:
        return {"pass": False, "error": "invalid task: " + "; ".join(problems)}
    with tempfile.TemporaryDirectory(prefix="swapos-grade-") as tmp:
        sandbox = os.path.join(tmp, "task")
        shutil.copytree(os.path.join(task_dir, "starter"), sandbox)
        shutil.copytree(os.path.join(task_dir, "tests"), os.path.join(sandbox, "tests"))
        target = os.path.join(sandbox, SOLUTION_FILE)
        if solution_path is not None:
            shutil.copyfile(solution_path, target)
        else:
            with open(target, "w") as f:
                f.write(solution_text)
        try:
            rc, out, dt = _run_pytest(sandbox, timeout)
        except subprocess.TimeoutExpired:
            return {"pass": False, "error": "grader timeout", "grader_latency_s": timeout}
        passed, failed = parse_pytest_summary(out)
        return {
            "pass": rc == 0 and failed == 0 and passed > 0,
            "tests_passed": passed,
            "tests_total": passed + failed,
            "grader_latency_s": round(dt, 3),
            "output_tail": out[-1500:],
        }


def grade_starter(task_dir: str, timeout: int = 120) -> dict:
    return grade(task_dir, solution_path=os.path.join(task_dir, "starter", SOLUTION_FILE), timeout=timeout)


def grade_reference(task_dir: str, timeout: int = 120) -> dict:
    return grade(task_dir, solution_path=os.path.join(task_dir, "reference", SOLUTION_FILE), timeout=timeout)


def verify_task(task_dir: str, timeout: int = 120) -> dict:
    """RED/GREEN verification: starter must FAIL, reference must PASS."""
    result = {"task": os.path.basename(task_dir), "ok": False}
    starter = grade_starter(task_dir, timeout)
    ref = grade_reference(task_dir, timeout)
    result["starter"] = {
        "pass": starter["pass"],
        "tests_passed": starter["tests_passed"],
        "tests_total": starter["tests_total"],
    }
    result["reference"] = {
        "pass": ref["pass"],
        "tests_passed": ref["tests_passed"],
        "tests_total": ref["tests_total"],
    }
    if starter["pass"]:
        result["error"] = "starter must FAIL (RED) but passed"
    elif not ref["pass"]:
        result["error"] = f"reference must PASS (GREEN) but failed: {ref.get('error')}"
    else:
        result["ok"] = True
    return result
