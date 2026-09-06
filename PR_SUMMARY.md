# SWAP-02: guaranteed backend cleanup ownership + pipeline tests in CI (G1.3/G1.5 prerequisite)

## What

SWAP-02 (docs/execution packet 2, TECHNICAL_SPEC SWAP-02) guarantees that
every successfully constructed backend whose `start()` is attempted receives
**exactly one `stop()` attempt by its owning layer** — including on start
failure, generation failure, a grader exception and an exhausted retry
budget — and that a cleanup failure never masks the failure it accompanies.
All changes are in `pipeline/loop.py`; no backend, grader, retry policy or
residency architecture changed, and all result/schema shapes are preserved
(`stop()` still returns eviction seconds).

- **Resident backend** (`run_task`, resident=True): `start()` and the whole
  task lifecycle (reason/code/review loop) now sit inside one outer
  `try/finally`. The single owned stop is attempted on every exit path —
  previously `resident_backend.stop()` only ran on the normal path, so a
  grader exception or any mid-task error leaked the resident backend.
- **Per-phase backend**: both `_generate` helpers (the module-level one and
  `run_task`'s) now call `start()` inside the protected region and attempt
  the phase's single `stop()` in a `finally`-equivalent, so a `start()`
  failure or `generate()` failure still gets its one cleanup attempt. The
  module-level helper previously called `start()` before the `try` (start
  failure never stopped) and referenced `out` in the `finally` after a
  failed `generate()` (masking the original error).
- **Stop-failure semantics**: when `stop()` also fails, the original failure
  stays the primary error. On a completed task with a recorded phase-named
  failure, the resident cleanup error is appended to that error rather than
  replacing it; when a lifecycle exception (e.g. grader exception, resident
  start failure) is propagating, a failing stop is never allowed to mask it.
  A failing stop is never retried (exactly one attempt). Failed tasks are
  never marked passed; error evidence still names the phase ("reason phase
  failed" / "code phase failed" / "critic phase failed" / "budget exhausted
  ..." preserved verbatim).
- **Overlap engine**: untouched — `run_pipeline.py` keeps its existing outer
  `engine.stop()` ownership (no per-phase double cleanup of the shared
  engine; `OverlapBackend.stop()` remains a 0.0 no-op).
- **CI**: the pytest invocation now runs `capsule/tests
  benchmarks/harness/tests pipeline/tests`; benchmark task structural
  validation stays.

## Why

G1.3/G1.5 reliability prerequisite (docs/execution WORK_PACKETS SWAP-02):
failed tasks must release backend resources, and the CI must actually
exercise the runtime loop. A leaked resident backend or a leaked per-phase
server turns any reliability measurement into a resource-accounting
experiment; this packet makes cleanup ownership structural and CI-visible.

## How tested

14 new tests in `pipeline/tests/test_loop.py` using instrumented fakes only
(no models, providers or network): `_FaultyBackend` records `loads`/`stops`
and can raise on `start()`/`generate()`/`stop()`, counting a stop attempt
even when the stop itself raises. Verified exactly one owned stop on:
normal completion (per-phase and resident), start failure, generation
failure, a monkeypatched grader exception (resident — the former leak — and
per-phase), and exhausted retry budget; plus original-error-visible-when-
stop-also-fails on the start, generate, resident and grader paths, and the
module-level `_generate`. All 21 pre-existing loop tests still pass
unchanged.

Gates (run from the repo root):

1. `uv run --with pytest pytest capsule/tests benchmarks/harness/tests pipeline/tests` → **57 passed**
   (uv's cache dir pointed at a writable workspace dir — the default
   `~/.cache/uv` is outside this session's file sandbox)
2. `python3 benchmarks/harness/validate_tasks.py --tasks-dir benchmarks/tasks` → **structural OK: 50 tasks**

Sacred scope untouched: no edits to `benchmarks/tasks/`,
`benchmarks/harness/` or any historical result JSON. No number claimed:
this packet is a measurement-integrity prerequisite for G1.3/G1.5.
