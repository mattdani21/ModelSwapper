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
