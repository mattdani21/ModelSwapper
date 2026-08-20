# G2.3 Ablation — Capsule vs naive transcript vs single-model

Status: **smoke results on T4 hardware (Apple M3 8 GB, Qwen3-4B Q4 + Qwen3-0.6B Q8)**;
full verdict pending the 27B-scale Colab run (notebook: `colab-phase2-eval.ipynb`).

## Smoke run 1 (2026-08-20, context 4096) — `ablation-local-4b-smoke.json`

| Arm | Pass | Wall/task | Context (mean) |
|---|---|---|---|
| capsule | 1/3 (33.3%) | 187.9 s | 2408 tok |
| naive | 0/3 (0.0%) | 67.7 s | 2335 tok |
| single | 2/3 (66.7%) | 193.1 s | 1473 tok |

Machine-emitted verdict: `capsule_ge_naive_quality: true`, `capsule_strictly_better_memory: false`.

### What the smoke actually showed

1. **Naive handoff overflowed the context (HTTP 400 on the first CODE phase in all 3 tasks).**
   REASON's plan text + problem + starter already exceeded the 4096-token
   window at 4B scale. It is not a fair quality comparison yet — but the
   overflow itself is the thesis's point: an unbounded transcript does not
   fit where a capsule does. The naive arm never grew its transcript because
   it died instantly — which is why the memory comparison is confounded
   (2335 vs 2408 is meaningless when one arm never retried).
2. **The capsule arm's retry path also overflowed**: the critic's full output
   (up to 2048 tokens) went into the next CODE prompt unbounded, while the
   capsule decision only stored 600 chars. Second attempts died with HTTP 400
   in every arm that reached them. **Fixed** (commit after run 1): the prompt
   now carries the same bounded 600-char feedback the capsule stores.
3. **Single-model beat capsule at the floor (2/3 vs 1/3)** — expected at this
   scale: the 0.6B critic is a weak reviewer, and single mode pays no
   context-rebuild cost. At 27B scale the 8B critic carried the retry loop
   (10/40 rescues in the Phase 1 parity run), so this ordering is a
   small-model artifact, not a verdict on the thesis.
4. peak_rss wasn't captured in run 1 (phase log now records it — run 2 has it).

## Smoke run 2 (2026-08-20, context 8192 + feedback-bounding fix) — `ablation-local-4b-smoke2.json`

| Arm | Pass | Wall/task | Context (mean) | Verdict input |
|---|---|---|---|---|
| capsule | **3/3 (100%)** | 230.3 s | **1352 tok** | quality ≥ naive ✓ |
| naive | 3/3 (100%) | 166.8 s | 2151 tok | memory: capsule strictly better ✓ |
| single | 3/3 (100%) | 207.9 s | 1610 tok | — |

Machine-emitted verdict: `capsule_ge_naive_quality: true`, `capsule_strictly_better_memory: true`.

**The thesis mechanism holds at the floor**: equal quality (100% both) with
the capsule carrying **37% less context** (1352 vs 2151 tok) — the structured
roll-up beats the verbatim transcript on memory without losing quality.

Honest caveats:
- naive was *faster* (166.8 vs 230.3 s/task): it passed every task on the
  first attempt while capsule+single needed retries (6 phases on 2 of 3
  tasks). Small sample at the floor — the bigger naive context may genuinely
  help the 4B's first attempt. The quality-vs-memory tradeoff at scale is
  what the 27B Colab run decides.
- RSS not captured in run 2 either (llama_backend now samples it — the
  Colab run will have real per-phase memory).

## What the 27B-scale run must show (G2.3 acceptance)

- capsule ≥ naive on pass rate (thesis half 1)
- capsule strictly better on memory: bounded context vs naive's linear growth
  (thesis half 2)
- single-model baseline: the resident-mode comparator (27B for everything)

If capsule loses to naive on quality at 27B scale: **stop and escalate**
(master prompt §2 — the thesis needs revision).

## 27B-scale Colab run (2026-08-20, RTX PRO 6000 Blackwell) — `ablation-colab-27b-20260820.json`

| Arm | Pass | Wall/task | Context | RSS |
|---|---|---|---|---|
| capsule | **7/8 (87.5%)** | 53.2 s | 1976 tok | 1.43 GB |
| naive | 3/8 (37.5%) | 37.1 s | 731 tok | 1.38 GB |
| single | **8/8 (100%)** | 37.6 s | 1003 tok | 1.91 GB |

Verdict: `capsule_ge_naive_quality: true` (87.5 vs 37.5 — capsule wins by 50
points), `capsule_strictly_better_memory: false` (1976 vs 731 tok).

**Confound, stated plainly**: the executed notebook ran at **4096** context
(stale Colab tab — the committed notebook has 8192). At 4096 the naive
transcript overflows on retry tasks and its context never grows — the naive
arm died early on 5/8 tasks, so (a) its 37.5% is context-handicapped and
(b) its 731-tok mean is a death artifact, not a memory win. The quality
direction is real (capsule finished retries where naive couldn't), but the
memory verdict is not settled by this run.

## Overlap A/B at 27B scale (same run) — `sequential-colab-27b-20260820.json` / `overlap-colab-27b-20260820.json`

| Backend | Pass | Mean wall | Mean load |
|---|---|---|---|
| sequential (Phase 1) | 6/8 (75%) | 50.05 s | 1.881 s |
| **overlap engine** | **8/8 (100%)** | **34.66 s (−30.8%)** | **1.04 s** |

- 8 of 24 overlap phases paid **zero** load (promoted standby); the rest were
  first-loads of the task. The ~2 s 27B loads are being hidden, as designed.
- Quality delta (8/8 vs 6/8) is partly sampling variance at temp 0.2 — the
  timing signal is the clean one.
- **G1.3 projection: 50 × 34.66 s = 1733 s vs API 965 s → 1.80×, under the
  2× bar.** The overlap engine is the G1.3 lever, now measured at 27B scale.
- RSS: single (27B resident) 1.91 GB > capsule 1.43 GB > naive 1.38 GB —
  process RSS is dominated by resident weights; the context-token story is
  the memory metric that matters and awaits the 8192 rerun.

## Outstanding

- **8192-context rerun** (fresh tab, notebook as committed) to settle the
  naive-arm quality + memory verdict cleanly.
- **50-task overlap run** to close G2.2 formally and G1.3 (projected 1.80×).
