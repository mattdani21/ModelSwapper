# ADR-0005 — Phase 2 swap engineering: overlap engine, capsule compression, handoff ablation

- Status: accepted (Phase 2)
- Date: 2026-08-20
- Relates: ADR-0001 (architecture), ADR-0002 (capsule), ADR-0004 (loop v1),
  MASTER-PROMPT.md §2 Phase 2, G1.3, G2.1–G2.4

## Context

Phase 1 closed with parity proven (80.0% / 78.0% vs the 76.8% bar) but two
open items pointed at the same root cause:

- **G1.3 near-miss**: mean wall 40.0–44.4 s vs the 38.6 s (2×) bar. The
  97.9 GB Blackwell GPU did not move the mean — wall time is phase
  serialization (load + evict + TTFT per phase) and retry cycles, not
  generation bandwidth.
- **Capsule growth**: capsule bytes grow linearly with task length; carried
  context will eventually dominate prompts on long tasks.

Phase 2 must make the swap invisible (G2.1 ≤ 1.5 s warm, G2.2 overlap) and
prove context preservation is real (G2.3 ablation), with capsule v1
compression (G2.4) as the sub-linear-growth mechanism.

## Decision

1. **Overlap by process-level slots, not llama.cpp surgery.** The phase order
   is known ahead of time (REASON → CODE → REVIEW → …), so the router's
   pre-fetch policy is deterministic lookahead: while phase N generates, phase
   N+1's weights load into a standby `llama-server` process. Swap becomes
   promote + evict. Layer-priority loading (first layers first) is deferred —
   it requires a llama.cpp patch and its benefit is bounded by the same
   latency we already hide with two slots.
2. **Unique per-server ports** (`PrefetchEngine._alloc_port`): a standby can
   never race a fallback on the same port. Prefetch threads that lose their
   slot reap their own server. Sequential fallback remains correct when the
   ceiling forbids two residents (memory guard, env `OVERLAP_CEILING_GB`,
   default 20 = T0's ceiling).
3. **G2.3 ablation = three arms, one runner** (`benchmarks/harness/run_ablation.py`):
   capsule (Phase 1 semantics) vs naive (full verbatim transcript in every
   prompt) vs single (one model resident, no swaps). The sacred suite and
   grader are untouched; the runner only changes handoff mode. Verdict is
   machine-emitted: capsule ≥ naive on quality AND strictly better on context
   memory. If capsule loses on quality → stop and escalate (master prompt §2).
4. **Capsule v1 compression is deterministic-first** (`capsule/compress.py`):
   verbatim core (goal, constraints, newest artifact) + roll-ups (decisions,
   phase history, old artifacts) under a fixed token budget (default 8k), with
   a pluggable summarizer hook for the REASON model later. Token estimate uses
   the existing chars/4 heuristic so numbers stay comparable across versions.
5. **Resident mode** (`--resident`) is the single-model ablation arm and the
   T0 residency policy prototype: one backend serves every phase, no swaps.

## Consequences

- Measured on T4 hardware (Apple M3 8 GB, 4B→0.6B, warm cache):
  sequential swap-to-first-token 0.851 s → overlapped **0.063 s (92.6% of the
  swap hidden)**; the 0.905 s load fully overlapped with generation
  (`benchmarks/results/swap-overlap-20260820-112658.json`). At 27B scale the
  ~2 s Colab load becomes invisible the same way — G1.3's 1.4 s gap closes by
  construction once the pipeline runs on the overlap engine.
- Two-slot residency costs memory: policy falls back to sequential when
  active + incoming exceed the tier ceiling. T0 (20 GB) fits 27B Q4 + 8B Q4
  (≈ 22 GB at Q4… borderline — may require 27B Q3 or evict-before-prefetch at
  the margin; measured at G1.5).
- Naive handoff is intentionally naive: no roll-up, no cap. It is the
  comparator, not a contender — the ablation decides if the thesis holds.
- The ablation's full 27B-scale run is a Colab job (same notebook pattern);
  the local 4B smoke gives the directional signal first.
