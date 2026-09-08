# Land 2026-09-08: SWAP-01 + SWAP-02 (docs/execution packets 1–2) on main

## What

Landing of the two reviewer-approved G1.3/G1.5 measurement-integrity
prerequisites onto main (base 929fbdd). No benchmark, harness, result or
runtime file touched (sacred scope empty).

- **SWAP-01 — content-addressed KV checkpoint identity** (merge 2e80f40,
  branch wt/swap-01 @ da0b1f6): KV checkpoint names derive from a 64-hex
  digest over canonical sorted JSON (spec + model bytes), so same-size
  different bytes can never restore a stale cache; missing/permission-denied
  identity disables save/restore end-to-end while generation keeps working;
  digest computed once per model per run. ADR-0006 added.
- **SWAP-02 — guaranteed backend cleanup ownership + pipeline tests in CI**
  (merge 5dfc7d1, branch wt/swap-02 @ e921082): every started backend
  receives exactly one owned `stop()` attempt on ALL exit paths (normal,
  start failure, generation failure, grader exception, exhausted budget);
  stop failures never mask the primary error and failed tasks are never
  marked passed. CI pytest invocation now runs capsule + harness + pipeline
  suites; task structural validation retained.

## Why

docs/execution ROADMAP order-1 tickets: reliability prerequisites before
SWAP-03 (corrected-cache G1.3 comparison) and SWAP-04 (T0 G1.5
certification) can be measured on authorized hardware. G1.3 (#7) and
G1.5 (#9) stay open until their numerical bars are measured.

## How tested

- Independent verify lanes: t_cb8dac13 (SWAP-01 PASS), t_115aeca6 (SWAP-02 PASS)
- Independent reviews APPROVED: t_3510735a (SWAP-01), t_bb27e02b (SWAP-02)
- Gates re-run by the wrapper on the merged tree (this landing):
  `uv run --with pytest pytest capsule/tests benchmarks/harness/tests pipeline/tests`
  → **57 passed**; `validate_tasks.py --tasks-dir benchmarks/tasks` →
  structural OK: 50 tasks; sacred diff (benchmarks/tasks, harness, results,
  runtime) empty.

## Landing review

Independent review of this landing runs on the modelswapper board
(reviewer profile) against the landed main state; content-level approvals
are cited above.
