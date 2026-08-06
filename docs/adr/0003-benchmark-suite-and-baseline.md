# ADR-0003 — Benchmark suite v1 and the frontier-API baseline

- Status: accepted (Phase 0)
- Date: 2026-08-06
- Relates: MASTER-PROMPT.md §2 (G0.4, G1.1, G1.2), §4 (benchmarks are sacred)

## Context

Parity (number 1) needs a denominator measured now: the frontier API's pass rate on the same tasks the pipeline will run. The suite must be auto-graded, deterministic, and impossible to game — and the sacred rule must be structural, not aspirational: *benchmark code is never modified to make results pass.*

## Decision

1. **Suite: 50 tasks, 3 categories** — bugfix (17), feature (17), refactor (16). All Python (the v1 pipeline's specialist set is strongest here; other languages are a later extension). Every task is a small, self-contained repo: a single solution file plus a pytest grader.
2. **Task layout** (`benchmarks/tasks/<category>/<task_id>/`):
   - `problem.md` — the brief given to the model (includes file layout + requirements)
   - `starter/solution.py` — the starting state (buggy / stubbed / unrefactored)
   - `tests/test_<task_id>.py` — the grader (RED on starter, GREEN on reference)
   - `reference/solution.py` — reference fix; used only to validate the task, NEVER shown to a model
   - `meta.json` — category, difficulty, task_id
3. **Uniform grading contract:** replace `starter/solution.py` with the model's output, run pytest, all tests green = pass. Bugfix/feature/refactor all satisfy RED-on-starter (refactor tasks carry structural hidden tests that fail on the unrefactored code), so one grader handles all 50.
4. **Baseline model: `deepseek-v4-pro`** (DeepSeek API, OpenAI-compatible). Rationale: it is the frontier-class API available to the swarm today (existing key), it is cheap enough to re-run the baseline often, and the constitution allows API calls *only* for baseline measurement. The baseline file records model, date, prompt template, and raw token counts so a different frontier API can be swapped in without invalidating the method.
5. **Results are data, committed.** Every run writes JSON to `benchmarks/results/` (`baseline-<model>-<date>.json`, later `pipeline-<date>.json`). A run without a results file did not happen.
6. **Sacred-rule enforcement:** `validate_tasks.py --full` re-checks RED/GREEN on every task (CI runs the structural check; the full check is a release gate before any pipeline parity claim).

## Consequences

- A pass rate is only comparable within one suite version; suite edits (harder/broader only) bump the suite version in `meta.json` and results carry it.
- The baseline is a moving target: any new frontier API available to the swarm can be measured the same way.
- Cost-per-task (number 4) is computed from the same run's token counts — one harness feeds both numbers.

## Alternatives considered

- *SWE-bench-style real-issue tasks*: rejected for v1 — heavyweight environments, flaky grading, too slow per task on an 8 GB machine; our tasks are purpose-built, deterministic, and equally valid for the parity claim.
- *HumanEval-style function completion*: too narrow — no multi-step bugfix/refactor surface, and it under-sells the pipeline.
