# AGENTS.md — ModelSwapper operating contract

This file outranks convenience. Read `MASTER-PROMPT.md` (the constitution) before touching anything.

## 1. What this project is

A model swapper runtime that treats LLM weights like virtual memory pages: one specialist model resident at a time, working context carried as a structured **Context Capsule** (not stale KV cache), specialists streamed in/out per pipeline phase (REASON → CODE → REVIEW). One runtime, five hardware tiers (T0 24 GB → T4 8 GB edge). Local-only inference.

## 2. Non-negotiable rules

1. **Four numbers:** every PR must state which of the four numbers it moves (quality parity, swap latency, hardware floor, cost per task). No number moved → orchestrator rejects.
2. **Every PR references a goal ID** (e.g. "G1.3") in the title or body.
3. **Benchmarks are sacred.** Benchmark/task code is never modified to make results pass. It only gets harder or broader. This includes the task suite, the grader, and the baseline runner.
4. **No cloud dependency.** Core pipeline runs local inference only. API calls allowed solely to measure baselines.
5. **No giant-model crutches.** Specialists ≤ 32B class before quantization. If a phase "needs" a bigger model, the fix is a better specialist or a better capsule, not a bigger resident.
6. **Privacy is a feature.** No task data leaves the machine except explicit baseline API calls (which must be logged as such). Any leak is severity-1.
7. **Every architectural choice gets an ADR** in `docs/adr/` — future decisions must be re-derivable.
8. **Missing a target is data, not failure.** Log it, hypothesize, retry. Hiding a missed target is the only firing offense.
9. **Hardware reality beats paper.** Numbers assumed in the prompt get re-measured on the actual machine.
10. **Never weaken, skip, or delete a failing test** to make CI green.

## 3. Working in this repo

- Branch per goal: `autopilot/<slug>` or `orch/<n>-<slug>`; never push to main directly; PRs get gated by the orchestrator referee.
- Write `PR_SUMMARY.md` (what / why / how tested, 2–6 short sections) and use it as the PR body.
- Commit progress every 20–30 minutes. Never force-push. Never commit secrets, `.env`, or model files (`models/` is gitignored).
- Results belong in `benchmarks/results/` as JSON — measurements are committed, not narrated.
- Keep diffs focused (<500 lines) unless the task genuinely demands more — say so explicitly.

## 4. Escalation (contact the human ONLY for)

1. A decision you cannot make (scope, direction, ambiguous acceptance criteria).
2. A credential the task needs that you cannot obtain locally.
3. A GPU run (prepare fully — code, CPU-passing tests, ready-to-run notebook, run docs — then hand off; never execute GPU work on this Mac).
4. Danger / irreversible actions.
5. Roadmap complete (propose a new long-horizon multi-epic goal).

Otherwise: **keep working.** Silent progress.

## 5. Commands

```bash
uv run --with pytest pytest capsule/tests benchmarks/harness/tests pipeline/tests   # quality gate
python3 benchmarks/harness/validate_tasks.py --tasks-dir benchmarks/tasks   # structural check
python3 benchmarks/harness/validate_tasks.py --full   # RED/GREEN verification of every task (slow)
python3 runtime/swap_runner.py --help                 # swap baseline measurement (G0.1/G0.2)
python3 runtime/overlap.py --help                    # overlap engine A/B measurement (G2.2)
python3 benchmarks/harness/run_ablation.py --help    # capsule vs naive vs single ablation (G2.3)
python3 pipeline/run_pipeline.py --backend overlap   # pipeline on the two-slot prefetch engine (G2.2)
```

## 6. Layout

```
runtime/        # swap engine: eviction, streaming load, residency policy
capsule/        # Context Capsule schema + serialization + tests
pipeline/       # reason→code→review loop, phase contracts
router/         # always-on tiny model: phase detection, model selection
benchmarks/     # tasks/ (the 50-task suite), harness/ (grader + runners — sacred), results/ (JSON data)
hardware/       # per-tier configs and tuning profiles (tiers.yaml)
docs/adr/       # ADRs, one per non-obvious choice
```
