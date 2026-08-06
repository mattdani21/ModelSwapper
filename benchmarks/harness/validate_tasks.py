"""Validate the benchmark task suite.

Default: structural check (CI-safe, fast).
--full: additionally run RED/GREEN verification on every task (slow;
        a release gate before any parity claim — ADR-0003).
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grader import task_dir_ok, verify_task  # noqa: E402

CATEGORIES = ("bugfix", "feature", "refactor")


def collect_tasks(tasks_dir: str) -> list[str]:
    tasks = []
    for cat in CATEGORIES:
        cat_dir = os.path.join(tasks_dir, cat)
        if not os.path.isdir(cat_dir):
            continue
        for name in sorted(os.listdir(cat_dir)):
            tdir = os.path.join(cat_dir, name)
            if os.path.isdir(tdir):
                tasks.append(tdir)
    return tasks


def main() -> None:
    ap = argparse.ArgumentParser(description="SwapOS benchmark task validation")
    ap.add_argument("--tasks-dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tasks"))
    ap.add_argument("--full", action="store_true", help="run RED/GREEN verification on every task (slow)")
    ap.add_argument("--timeout", type=int, default=120)
    args = ap.parse_args()

    tasks = collect_tasks(args.tasks_dir)
    if not tasks:
        print(f"ERROR: no tasks found under {args.tasks_dir}")
        sys.exit(1)

    failures = []
    for tdir in tasks:
        problems = task_dir_ok(tdir)
        if problems:
            failures.append((tdir, "; ".join(problems)))
    if failures:
        for tdir, msg in failures:
            print(f"STRUCTURAL FAIL {tdir}: {msg}")
        sys.exit(1)
    print(f"structural OK: {len(tasks)} tasks")

    if args.full:
        bad = 0
        for tdir in tasks:
            r = verify_task(tdir, timeout=args.timeout)
            status = "OK  " if r["ok"] else "FAIL"
            print(f"  {status} {r['task']:22s} starter={r['starter']['pass']} ref={r['reference']['pass']}")
            if not r["ok"]:
                bad += 1
                print(f"       {r.get('error')}")
        if bad:
            print(f"ERROR: {bad}/{len(tasks)} tasks failed RED/GREEN")
            sys.exit(1)
        print(f"RED/GREEN OK: all {len(tasks)} tasks")


if __name__ == "__main__":
    main()
