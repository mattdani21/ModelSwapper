# ADR-0004 — Pipeline loop v1 and the deterministic router

- Status: accepted (Phase 1)
- Date: 2026-08-07
- Relates: ADR-0001 (architecture), ADR-0002 (capsule), MASTER-PROMPT.md §1.2, G1.1–G1.5

## Context

Phase 1 must prove the REASON → CODE → REVIEW loop completes the 50-task suite at ≥ 76.8% absolute pass rate (80% of the 96.0% measured frontier baseline), with wall-clock ≤ 2× the API baseline (19.3 s/task) and per-swap timing breakdowns. The loop is the first real consumer of the capsule, so its design must respect the swap thesis: no model sees another model's conversation.

## Decision

1. **Phase order:** REASON (plan + spec into the capsule) → CODE (complete `solution.py` from capsule + task files) → REVIEW. REVIEW is two-stage: (a) *mechanical* — the sacred grader runs the candidate's tests (the only pass/fail authority); (b) on failure, a *critic* model diagnoses the test output and feeds the next CODE attempt. Loop until green or budget exhausted (default 3 code attempts).
2. **Swap semantics per phase:** every phase transition starts its specialist fresh and evicts it after generation (start/stop per phase). The swap is real, measured per phase (`load_s`, `evict_s`, `ttft_s` in the phase log — the G1.3 timing breakdown), and the capsule is the only thing carried across. No KV cache, no transcript — ADR-0002.
3. **Router v1 is deterministic rules**, not a model: transitions (reason→code→review→{code|done}) are control flow, correct by construction — G1.4's ≥ 95% bar is met trivially and honestly stated. A model-based router arrives only with predictive pre-fetch (G2.2), where it earns its keep by deciding *which* specialist and *when to pre-load*.
4. **Prompts are built from the capsule + task files** (goal, constraints, plan, artifacts, decisions log), never from another model's raw output stream. The critic's feedback is recorded as a capsule *decision*, not as conversation.
5. **Checkpointed results:** the runner rewrites its results JSON after every task, so a killed/timeout run yields its completed tasks (kernel time limits are a real risk on the GPU eval).

## Consequences

- The pass/fail authority is the grader; the critic only *informs* the next attempt — the loop cannot "talk itself into passing" (benchmarks stay sacred).
- Each task's capsule is a complete audit trail (plan, attempts, critic feedback, per-phase swap timings) — this is the data for G2.3 (capsule vs naive handoff) and G2.4 (compression).
- The first GPU eval runs the same code path as the local dry-run — only the model files differ (14B / 30B-A3B vs 4B / 0.6B).

## Non-decisions (deferred)

- Predictive pre-fetch / overlap (G2.2), layer-priority loading (G2.1), capsule compression (G2.4): Phase 2.
- Multi-specialist residency policies per tier (G3.1): the runtime API (`--resident` vs `--swap`) is future work; v1 is swap-per-phase everywhere.
