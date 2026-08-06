# Benchmark task authoring — SwapOS suite v1 (SACRED)

Suite: **50 tasks** — bugfix (17) · feature (17) · refactor (16). All Python, stdlib only.

## Task layout

```
benchmarks/tasks/<category>/<task_id>/
  problem.md            # the brief given to the model (markdown)
  starter/solution.py   # starting state: buggy / stubbed / unrefactored
  tests/test_<task_id>.py  # the grader — RED on starter, GREEN on reference
  reference/solution.py # reference fix (NEVER shown to any model)
  meta.json             # {"task_id": ..., "category": ..., "difficulty": 1|2|3, "description": ...}
```

`task_id` format: `<category>-<nn>` (e.g. `bugfix-07`, `feature-03`, `refactor-11`).
Task ids are unique across the suite.

## The grading contract (what "pass" means)

1. The model receives `problem.md` + the current `starter/solution.py`.
2. The model's output **replaces `solution.py` entirely** (single-file contract).
3. Grader runs `python3 -m pytest tests/ -q`. **All tests green = PASS.**

Therefore every task must satisfy:
- **RED**: `starter/solution.py` FAILS the tests (at least one failing assertion).
- **GREEN**: `reference/solution.py` PASSES all tests.
- Tests are deterministic and fast (< 2 s total). No sleeps, no randomness, no network.
- **stdlib only** in starter, reference, and tests (the grader runs plain python3; no numpy/pytest-plugins/installs).
- Tests must import the solution robustly. Start every test file with:
  ```python
  import os
  import sys

  sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

  from solution import <name>
  ```

## Category guidance

- **bugfix** (17): starter contains ONE realistic, subtle bug — off-by-one, wrong
  comparison operator, aliasing/mutation, wrong default, off-by-one in slice,
  incorrect edge-case handling, etc. The task is findable by reading, not by
  guessing. `problem.md` describes correct behavior and may give examples —
  it must NOT point at the bug location or leak the fix. Difficulty spread:
  ~5 easy / ~9 medium / ~3 hard.
- **feature** (17): starter is a stub (`raise NotImplementedError`) with a clear
  spec in `problem.md`: behavior, examples, edge cases. Tests encode the spec,
  including edge cases (empty input, single element, boundaries, type errors).
  Difficulty spread: ~5 easy / ~9 medium / ~3 hard.
- **refactor** (16): starter WORKS (all existing behavior tests pass) but is
  messy: duplicated logic, globals, no helper functions, mixed responsibilities.
  The grader includes **structural tests that FAIL on the starter** and PASS on
  the reference — e.g. `assert hasattr(solution, "process")`, specific function
  signatures, absence of duplicated blocks (test greps the source), required
  helper existence. `problem.md` describes the required structure. Difficulty
  spread: ~5 easy / ~8 medium / ~3 hard.

## Hard rules

- Never modify `benchmarks/harness/` (sacred — ADR-0003).
- Never commit `reference/solution.py` content into `problem.md` or tests.
- `problem.md` never contains "the bug is in…" hints.
- Every task is self-contained; no imports across tasks.
- Before finishing, verify locally per task:
  1. `cd <task_dir> && python3 -m pytest tests/ -q` against a copy of `starter/solution.py` → **must fail**
  2. same against `reference/solution.py` → **must pass**
  (Use the grader: `python3 benchmarks/harness/validate_tasks.py --full --tasks-dir benchmarks/tasks` once at the end.)
- Do NOT run git commands and do NOT commit — leave the files in the working tree.
