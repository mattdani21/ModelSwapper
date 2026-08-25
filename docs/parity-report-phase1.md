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

> **CORRECTED 2026-08-21 (Addendum 4):** the original claim below was wrong
> for this run — all 40 passes were pass@1 (`iterations == 1`); the 10
> retried tasks all failed. Retries rescued ZERO tasks in the 40/50 run.
> The retry loop demonstrably rescues tasks only in the post-fix config
> (47/50 run: 6 of 47 passes at iterations==2). See Addendum 4.

(Original text, retracted: "10 tasks needed the critic loop: 4 resolved in
2 iterations, 6 in 3 (max). Without the loop the raw single-shot rate was
~30/50; the REVIEW → CRITIC → CODE cycle recovered 10 tasks (25% of the
final score). This is the pipeline's structural advantage over a single
API call — the same loop applied to a frontier model would likely push
the baseline itself higher.")

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
2. Retry-loop contribution corrected in Addendum 4: 40/50 run was pass@1-
   only; the 47/50 run rescued 6/47 via retries. The loop is a real but
   modest lever post-fix, not a 25% differentiator.
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
- **Temperature sensitivity (downgraded per Addendum 4):** the 0.6 run's
  35/50 is confounded — 11 of its 15 failures were a code defect
  (NameError on server-start failure), not temperature. Direction
  plausible, clean measurement outstanding.
- **G1.3 remains a documented near-miss on both GPUs** (2.07× and 2.30× vs the 2× bar; API mean 19.3 s). Wall time is dominated by phase serialization + retries, not generation bandwidth — the bigger GPU did not move the mean. Lever: resident mode / fewer retries (Phase 2 work).
- **Stable core across all three runs:** the tasks that pass at both temperatures (29/50) and the two-0.2-run overlap bound the honest floor; the committed per-task JSONs make every number auditable.

---

## Addendum 3 — The 8192-context pipeline: 94% parity (2026-08-20, full suite)

Same models (27B Q4 + 8B Q4, temp 0.2), two changes vs the Phase 1 config:
context 4096 → **8192** and the critic-feedback bound (600 chars, bug fix).
Both unlocked the retry loop that 4096 was choking.

| Run | Pass | bugfix | feature | refactor | Mean wall | vs API |
|---|---|---|---|---|---|---|
| API baseline (deepseek-v4-pro) | 48/50 (96.0%) | 17/17 | 16/17 | 15/16 | 19.3 s | 1.0× |
| **sequential (8192)** | **47/50 (94.0%)** | **17/17** | **17/17** | 13/16 | 41.99 s | 2.18× |
| overlap engine (8192) | 45/50 (90.0%) | 15/17 | 17/17 | 13/16 | 40.83 s | 2.12× |

**G1.2 is now exceeded by ~17 points**: 94.0% vs the 76.8% bar — 97.9% of the
frontier baseline's rate, category-for-category (perfect on bugfix AND
feature, 2 behind on refactor). The 40/50 Phase-1-config numbers remain on
record; the 47/50 is the Phase-2-config result (ctx 8192 + bounded feedback).

**G2.2 at full suite**: load per phase 1.995 → 0.806 s (−60%), 80/195
phases (41%) at zero load; wall 41.99 → 40.83 s (−2.8%, −43.9 s over the
suite). Generation dominates at 27B scale — the swap tax is gone, the
remaining wall is tokens. Pass rates within run-to-run noise (45 vs 47).

**G1.3 still a near-miss**: 2.12× (overlap) vs the 2× bar. Hypotheses for
the gap: (a) the multi-arch build runs Blackwell via PTX JIT (sm_89→sm_100)
— a native-arch build (`100;120`) is the obvious next lever; (b) retry
storms. Not hidden — on record with the data.

---

## Addendum 4 — Audit corrections (2026-08-21, verified against committed JSONs)

An independent reasoner (claude-opus-5, opencode) audited the repo and
flagged claims that contradict the committed data. Every item below was
re-verified by hand against `benchmarks/results/` before this addendum
was written.

1. **The retry-rescue claim is inverted for the 40/50 run.** All 40 passes
   in `pipeline-colab-27b-20260819-40of50.json` have `iterations == 1`
   (pass@1). All 10 tasks with `iterations > 1` FAILED. The earlier
   "retry loop rescued 10 tasks (25% of the score)" claim (this report
   §2, closeout §3) is WRONG for that run and is retracted. In the later
   47/50 run (post-fix) the loop did rescue 6 tasks: 41 pass@1 + 6 at
   iterations==2.
2. **Three full runs were partly corrupted by a code defect**
   (`cannot access local variable 'out'` when a server start failed):
   5/10 failures in the 40/50 run, 8/11 in the 39/50 run, 11/15 in the
   35/50 run. The defect was fixed in the Phase-2 refactor. The
   "temperature is the dominant variance term" conclusion drawn from the
   0.6 run (35/50) is therefore NOT clean — 11 of its 15 failures were
   the crash, not temperature. The conclusion is downgraded to
   "temperature sensitivity: plausible direction, confounded by the
   defect; not cleanly measured".
3. **Protocol asymmetry:** pass@1 comparison is 41/50 (pipeline) vs
   48/50 (API baseline, single shot). The headline parity figure
   (47/50) includes retries the baseline was never given. Honest
   phrasing going forward: "pipeline pass@1 41/50 vs 48/50 single-shot
   — exact McNemar p = 0.016 (b=7 c=0), a significant gap at n=50, not
   inside noise; 47/50 with the retry loop vs 48/50 remains
   statistically indistinguishable (p = 1.0)." [p-values recomputed
   from `benchmarks/results/symmetric-baseline-20260825.json`,
   `benchmarks/results/baseline-deepseek-v4-pro-20260807-001937.json`,
   `benchmarks/results/sequential-colab-27b-20260820-full50-8192.json`]
4. **Cost:** the only measured cost comparison in the repo: API
   $0.15/suite vs pipeline ≈ $0.70/suite on rented L4 ≈ **4.7× the API**.
   The "1/50th cost" north-star claim is NOT supported by any committed
   measurement. The defensible claim is sovereignty, not savings:
   "zero marginal cost and zero data egress on hardware the user owns."
5. **Stability:** across four full runs at temp 0.2, 19/50 tasks flipped
   at least once; 30/50 passed in all four. Headline range 35–47/50.
   The stable-core (58%) framing stays the honest conservative read.
6. **Unchanged by the audit:** the capsule-vs-naive result (788 vs 1663
   tok, replicated twice) — real and mechanism-backed; the sacred suite
   untouched since 2026-08-07 (verified in git); RED/GREEN reproduces
   (50/50, re-run during the audit).
