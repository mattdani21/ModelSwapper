# Phase 1 Closeout — Single-Pipeline Proof (2026-08-20)

Phase 1 (weeks 3–6 of the master plan) is closed as a *measured* phase.
This document is the archive: what was claimed, what was measured, what
failed, and what Phase 2 inherits.

## 1. Goal ledger

| Goal | Target | Result | Status |
|---|---|---|---|
| G1.1 | 50 coding tasks end-to-end, zero human input | 40/50 + 39/50 (two full runs) | ✅ CLOSED |
| G1.2 | Pass rate ≥ 76.8% (= 80% of the 96.0% frontier baseline) | 80.0% (L4) + 78.0% (Blackwell), both ≥ bar | ✅ CLOSED, two-run confirmed |
| G1.3 | Mean wall-clock ≤ 2× frontier API | 2.07× (L4), 2.30× (Blackwell) | ⏳ near-miss, lever = Phase 2 (resident/overlap) |
| G1.4 | Router triggers transitions ≥ 95% | Deterministic router, 100% (no misroutes in 3 full runs) | ✅ CLOSED |
| G1.5 | Peak memory < 20 GB (T0) / < 6.5 GB (T4) | Not yet measured on 24 GB Air | ⏳ OPEN — the launch demo |

## 2. The numbers (committed, auditable)

Frontier API baseline (deepseek-v4-pro, 50 tasks): **48/50 = 96.0%**, mean 19.3 s/task.

SwapOS pipeline (Qwen3.8-27B Q4 reason+code, Qwen3-8B Q4 review, swap-per-phase):

| Run | Hardware | Temp | Pass rate | Mean wall | Load | Evict |
|---|---|---|---|---|---|---|
| 2026-08-19 | Colab L4 | 0.2 | **40/50 = 80.0%** | 40.0 s | 1.96 s | 0.17 s |
| 2026-08-20 | Colab RTX PRO 6000 | 0.2 | **39/50 = 78.0%** | 44.4 s | 2.18 s | 0.21 s |
| 2026-08-20 | Colab RTX PRO 6000 | 0.6 | 35/50 = 70.0% | 43.4 s | 1.93 s | 0.19 s |

Per-category at the operating point (0.2): bugfix 14/17, feature 14–16/17,
refactor 11–12/16. Stable core across all runs: 29/50 pass at both temperatures.

Evidence files (`benchmarks/results/`):
- `baseline-deepseek-v4-pro-20260807-001937.json` — 48/50 baseline
- `pipeline-colab-27b-20260819-40of50.json` — the parity run (L4, 0.2)
- `pipeline-colab-27b-20260820-39of50-t02-blackwell.json` — the confirmation (0.2)
- `pipeline-colab-27b-20260820-35of50-t06.json` — the temperature finding (0.6)
- `pipeline-local-4b-dryrun.json` — 7/10 local T4-floor dry run (4B/0.6B)
- 3 swap-baseline files from Phase 0

Reports: `docs/parity-report-phase1.md` (main + 2 addenda), this closeout.

## 3. What Phase 1 proved

1. **Parity is real, not aspirational**: 80% / 78% of the frontier baseline's
   pass rate on the same 50-task suite, on rented ~$1/hr GPUs, with a 27B-class
   specialist set and a 19 s→40 s wall-clock cost. The "you need the cloud"
   argument now has measured counter-evidence.
2. **Swap-per-phase works at scale**: 27B weights in/out in ~2 s load / 0.2 s
   evict per phase on Colab-class NVMe-backed infra; the pipeline completed
   every run without a single memory-pressure failure.
3. **The retry loop is the differentiator**: REVIEW→CRITIC→CODE cycles rescued
   10 of 40 passes on the L4 run (~25% of the score). Single-shot would have
   been ≈ 30/50 — below the bar.
4. **The deterministic router is correct-by-construction**: 100% of phase
   transitions correct across ~900 phases; the always-on tiny model is not
   needed until Phase 3/4.
5. **Temperature is the dominant variance term**: 0.2 stable (±1 task across
   sessions/GPUs), 0.6 collapses (feature −5). Operating point: 0.2, now the
   notebook default.

## 4. Failure classes found and fixed (worth their weight)

| Class | Symptom | Fix |
|---|---|---|
| Drive cache drops exec bit | 0/50, "Permission denied" on llama-server | `chmod 0o755` after every cache restore |
| llama.cpp DeltaNet CUDA bug (#27164) | 0/50, SIGABRT rc=-6 in decode | Rebuild from current master (cache v2) |
| CUDA arch lock (Ada vs Ampere vs Blackwell) | 0/50, kernel launch abort | Multi-arch build `75;80;89` + PTX JIT (cache v3) — ran on L4, A100-class, and RTX PRO 6000 |
| Truncated GGUF downloads | silent load crash | Exact-size guards (0.98 × expected) |
| Stale Colab sessions / auto-commits | clone exit 128, rebase conflicts | Fresh tab per run; `--theirs` on "Created using Colab" |

## 5. Handoff to Phase 2 (swap engineering)

- **G1.3's gap is a serialization problem, not a bandwidth problem**: the
  bigger GPU (97.9 GB Blackwell) did not move the mean wall-clock. Wall time =
  phase loads + evicts + retry cycles. Levers: G2.1 (warm swap ≤ 1.5 s),
  G2.2 (overlap/prefetch — load B while A generates).
- **G2.3 ablation needs a single-model baseline**: the 27B Q4 on everything is
  the natural comparator (it already exists in the specialist set).
- **G2.4 capsule growth**: per-task capsules are committed (`capsules.zip` in
  Drive, capsule-dir in the pipeline) — the growth curve vs task length can be
  measured from existing data before the compression stage is even built.
- **G1.5 (24 GB Air) is the launch demo** and the north-star story; it can run
  in parallel with Phase 2 (same runtime, T0 residency policy).

## 6. Where things live

- Notebook (the eval engine): `notebooks/colab-phase1-eval.ipynb`
- Pipeline: `pipeline/` (loop, contracts, prompts, run_pipeline.py)
- Router: `router/rules.py` (deterministic v1)
- Runtime: `runtime/` (llama_backend, swap_runner, fake_backend)
- Capsule: `capsule/` (schema v0)
- Suite (SACRED): `benchmarks/tasks/` (50 tasks), `benchmarks/harness/`
- ADRs: `docs/adr/` (0001–0004)
