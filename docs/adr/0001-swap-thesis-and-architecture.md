# ADR-0001 — The swap thesis and system architecture

- Status: accepted (Phase 0)
- Date: 2026-08-06
- Relates: MASTER-PROMPT.md §1

## Context

Frontier agentic coding is assumed to require a monolithic hosted model. That assumption forces three costs: API per-token pricing, data egress (privacy), and a hardware ceiling that excludes edge devices. We propose the opposite: a pipeline of small, specialized models, each loaded into memory only for its phase, each handed the full working context as *structured state*, not as another model's stale attention state.

## Decision

1. **One specialist resident at a time, plus a tiny always-on router.** Weights are treated like virtual-memory pages: evict on phase transition, stream the next specialist from NVMe.
2. **Context is model-agnostic.** The working context travels as a **Context Capsule** — goal, constraints, artifacts, decisions log, plan, phase history — serialized to JSON. We do not keep weights loaded to preserve context; we preserve context by design so weights are free to swap. (Consequence: a capsule is the unit of checkpointing, migration across machines, and memory accounting.)
3. **Reference pipeline:** REASON (small reasoning model → plan + spec) → CODE (coding specialist) → REVIEW (critic; verifies with tests) → loop until pass or budget exhausted. Each phase is a contract between the runtime and a specialist model.
4. **One runtime, five tiers.** T0 (24 GB) through T4 (8–16 GB edge). Tier differences are residency *policy* (how many specialists stay resident, which quant) — never a code fork.
5. **Repo layout:** the constitution's §1.4 tree (`/swapos/runtime …`) is realized at the repo root (`runtime/`, `capsule/`, `pipeline/`, `router/`, `benchmarks/`, `hardware/`, `docs/`) because the repository itself *is* SwapOS; the prefix directory would be pure nesting.

## Consequences

- The swap engine's API surface is: `load(model)`, `generate(prompt, ctx)` with a capsule in, `evict(model)`, `residency(policy)`. Everything else is policy.
- Swap latency and peak memory become first-class, continuously measured numbers (G0.1/G0.2), not incidental properties.
- The Capsule schema is a contractual interface: pipeline, router, and runtime all consume it; changing it is a breaking change requiring an ADR.

## Non-decisions (deferred)

- Which llama.cpp vs MLX backend wins: Phase 0 measures llama.cpp (installed, Metal-capable); MLX is a Phase 2 candidate (G2.1 layer-priority loading may favor one).
- Specialist model *selection* per tier: Phase 3 (G3.4 model registry).
- Capsule compression: Phase 2 (G2.4).
