# Land 2026-09-13: SWAP-03 preparation — G1.3 paired-experiment manifest + report scaffold (docs/execution packet 3) on main

## What

Landing of the reviewer-approved SWAP-03 preparation onto main (base
47d20c7; merge 214d7da; branch wt/op-modelswapper-2026-09-11 @ f785d6d).
Two new documents, no benchmark, harness, result or runtime file touched
(sacred scope empty):

- **`docs/g1.3-paired-manifest.md`** — pre-registered comparison manifest
  for G1.3. Fixes the frozen 50-task pack (digest `0a9f8804…`), model set
  (`Qwen3.8-27B-Q4_K_M` reason/code, `Qwen3-8B-Q4_K_M` review), runner
  commands, budgets and the two arms — **L** = local pipeline with the
  CODE-retry KV prefix cache, **F** = `deepseek-v4-pro` with the
  pipeline's exact loop — before any measurement. Bar pinned at
  **≤ 38.52 s** mean total time per task (2 × the committed 19.26 s API
  mean) — stricter than the repo's rounded 38.6 s statement. Failure
  semantics, invalidity rules and the run-time record (R1–R10) fixed in
  advance.
- **`docs/g1.3-paired-report.md`** — report scaffold; verdict line stays
  `NOT MEASURED — preparation complete, awaiting authorized hardware`.
  Every numeric cell carries `TO BE RECORDED AT RUN TIME` plus the field
  map that fills it from the two raw JSONs.

## Why

docs/execution ROADMAP order-2 packet: SWAP-03 is the controlled paired
latency experiment that decides G1.3 (mean total time per task ≤ 2× the
frontier API mean with G1.2 quality maintained). Its prerequisites
(SWAP-01, SWAP-02) are already on main; the measurement half remains
blocked on authorized hardware. Pre-registering the protocol before
results exist is what makes the eventual verdict non-moveable. G1.3 (#7)
and G1.5 (#9) stay open until their numerical bars are measured.

## Review trail

- Round 1 (t_5f4fc332): CHANGES REQUESTED — 6 required docs-only fixes.
- Round 2 (t_ceee6700): **APPROVED** — diff scope exact (2 docs, 10+/10−),
  each fix re-verified against committed JSONs, sha256 byte-exact, no
  fabricated value introduced.

## How tested

- `uv run --with pytest pytest capsule/tests benchmarks/harness/tests pipeline/tests` → **57 passed**
- `python3 benchmarks/harness/validate_tasks.py --tasks-dir benchmarks/tasks` → **structural OK: 50 tasks**
- Sacred diff (`benchmarks/tasks`, `benchmarks/harness`, `benchmarks/results`, `runtime/`) empty; landing diff = the two docs + STATE.md landing record + this summary.
- **No model was run and no API call was made**; both documents' verdict remains NOT MEASURED.

## Landing review

Independent review of this landing runs on the modelswapper board
(reviewer profile) against the landed main state; content-level approvals
are cited above.
