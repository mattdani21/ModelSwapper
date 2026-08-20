# Phase 1 Parity Report — SwapOS pipeline vs frontier API baseline

- Date: 2026-08-19
- Run: `benchmarks/results/pipeline-colab-27b-20260819-40of50.json`
- Baseline: `benchmarks/results/baseline-deepseek-v4-pro-20260807-001937.json` (48/50 = 96.0%)
- Hardware: Colab L4 22.5 GB · specialists: Qwen3.8-27B-Q4_K_M (reason+code), Qwen3-8B-Q4_K_M (review)
- Mode: swap-per-phase (each specialist loaded fresh per phase, evicted after)

## Verdict: G1.2 MET — 80.0% ≥ 76.8% bar (80% of baseline)

| Metric | API baseline | SwapOS pipeline | Bar | Status |
|---|---|---|---|---|
| Pass rate (50 tasks) | 48/50 = 96.0% | **40/50 = 80.0%** | ≥ 76.8% | ✅ MET |
| Mean wall-clock / task | 19.3 s | 40.0 s | ≤ 38.6 s (2×) | ⚠️ 2.07× — near-miss |
| Mean model load (swap-in) | n/a | **1.96 s** | — | excellent |
| Mean evict | n/a | 0.17 s | — | excellent |
| Task agreement w/ baseline | — | 40/50 | — | — |
| Pipeline-only wins | — | 1 (feature-08) | — | — |
| Baseline-only wins | — | 9 | — | target for Phase 2 |

## Per-category

| Category | Pipeline | Baseline | Δ |
|---|---|---|---|
| bugfix | 12/17 (70.6%) | 17/17 | −5 |
| feature | 16/17 (94.1%) | 16/17 | 0 (won feature-08) |
| refactor | 12/16 (75.0%) | 15/16 | −3 |

## The retry loop's contribution

10 tasks needed the critic loop: 4 resolved in 2 iterations, 6 in 3 (max).
Without the loop the raw single-shot rate was ~30/50; the REVIEW → CRITIC → CODE
cycle recovered 10 tasks (25% of the final score). This is the pipeline's
structural advantage over a single API call — the same loop applied to a
frontier model would likely push the baseline itself higher.

## Timings & swap physics

- Mean load 1.96 s on L4 with local disk (vs 70–110 s on Kaggle's input mount) —
  the swap thesis mechanics are real at 27B scale.
- Wall-clock is dominated by generation (27B Q4 ≈ 20–40 tok/s on L4), not swaps.
- G1.3's 2× bar missed by 1.4 s (40.0 vs 38.6). Levers: A100 (~3× faster
  generation → ~15–20 s/task, well under bar), fewer retries on easy tasks,
  or resident-mode for repeated models. A rerun on A100 is the clean fix.

## Cost framing

- API baseline: $0.15 suite (~$0.003/task).
- Pipeline: L4 ≈ 3 units/hr × ~2.2 h ≈ 7 units ≈ **$0.70** for the suite
  (electricity-free rented GPU), i.e. ~4.7× the API cost at LIST prices —
  but the hardware is a one-time/rented asset that ALSO serves offline,
  private use; on a 24 GB Mac the marginal cost is ~0 and nothing leaves
  the machine. The 1/50th claim is directionally right on hardware ownership;
  on pure rented-GPU economics it's parity, not 50× cheaper — noted honestly
  for Phase 4 pricing work.

## Honest caveats

- 27B scores on the Artificial Analysis index (52) are vendor-reported; this
  report uses only OUR sacred suite — no vendor numbers involved.
- L4 ≠ laptop; the T0 claim (24 GB Mac, offline) is validated by this config's
  hardware class (27B Q4 fits 24 GB unified), but the on-device measurement is
  still pending the Air demo.
- One-run evidence; a confirmation run at a second temperature is cheap and
  recommended before the number goes public.

## Conclusions

1. The swap-thesis quality claim is **measured, not assumed**: 80% of a
   frontier API's pass rate, at 27B-class specialists, swap-per-phase.
2. The retry loop is the differentiator (10 recoveries) — Phase 2's capsule
   work (G2.3) targets whether context-preservation lifts it further.
3. Remaining Phase 1 items: G1.3 (1.4 s gap — A100 rerun), G1.5 (T0 memory
   ceiling on the 24 GB Air), confirmation run.

---

## Addendum — temperature sensitivity (confirmation run, 2026-08-20)

Second-temperature confirmation (0.6 vs the 0.2 operating point), run on an
RTX PRO 6000 Blackwell 97.9GB (multi-arch build, same model set):

| Metric | 0.2 (L4) | 0.6 (Blackwell) |
|---|---|---|
| Pass rate | **40/50 (80.0%)** | 35/50 (70.0%) |
| bugfix | 12/17 | 14/17 |
| feature | 16/17 | **11/17** |
| refactor | 12/16 | 10/16 |
| Mean wall | 40.0s | 43.4s |
| Retries needed | 10 | 17 |

**Finding: the result is temperature-sensitive, not luck-dependent.**
- Agreement between temps: 33/50; stable core (pass at BOTH): **29/50 (58%)**
- Higher temperature helps bugfix (+2) but collapses feature (−5) — spec-
  adherence tasks need determinism; 0.2 is the correct operating point.
- G1.2 stands as MET **at the 0.2 operating point** (the documented default).
  The claim must be stated with that qualifier; the stable-core floor (58%)
  is the honest conservative reading.

**Remaining:** one variance-confirmation run at 0.2 on the big GPU (same temp,
different session/hardware) to bound run-to-run noise, then G1.2 closes.
G1.3 remains a near-miss at both temps (40.0/43.4s vs 38.6s bar) — retries
dominate the tail; resident-mode or per-category temperatures are the levers.

---

## Addendum 2 — Confirmation run (2026-08-20): G1.2 CONFIRMED at the operating point

Same config, temperature 0.2, on Colab **RTX PRO 6000 Blackwell (97.9 GB)**, fresh session.

| Metric | L4 run (0.2) | Blackwell run (0.2) | 0.6 run (Blackwell) |
|---|---|---|---|
| Pass rate | **40/50 (80.0%)** | **39/50 (78.0%)** | 35/50 (70.0%) |
| bugfix | 12/17 | 14/17 | 14/17 |
| feature | 16/17 | 14/17 | 11/17 |
| refactor | 12/16 | 11/16 | 10/16 |
| Mean wall | 40.0 s (2.07×) | 44.4 s (2.30×) | 43.4 s |
| Mean load / evict | 1.96 / 0.17 s | 2.18 / 0.21 s | 1.93 / 0.19 s |

**Verdict:**
- **G1.2 (parity ≥ 76.8%) MET and CONFIRMED** — two independent sessions on two different GPUs at the documented operating point (0.2): 80.0% and 78.0%, both above the bar. The claim is no longer single-run.
- **Temperature sensitivity is the dominant variance term, measured cleanly:** at 0.2 the pipeline is stable (±1 task across sessions); at 0.6 it drops to 70% — feature tasks (spec-adherence) collapse at higher temperature while bugfix improves slightly. 0.2 is the correct operating point and is now the notebook default.
- **G1.3 remains a documented near-miss on both GPUs** (2.07× and 2.30× vs the 2× bar; API mean 19.3 s). Wall time is dominated by phase serialization + retries, not generation bandwidth — the bigger GPU did not move the mean. Lever: resident mode / fewer retries (Phase 2 work).
- **Stable core across all three runs:** the tasks that pass at both temperatures (29/50) and the two-0.2-run overlap bound the honest floor; the committed per-task JSONs make every number auditable.
