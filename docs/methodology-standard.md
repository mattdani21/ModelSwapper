# Validation Methodology Standard — SwapOS Open Funnel

Status: published with roadmap gate 4 (benchmark page, 2026-08). This
document is the reusable validation methodology behind the open funnel:
the same harness, the same protocol, and the same honesty rules are used
for every model, vendor, or configuration claim — ours and anyone else's
who adopts the standard.

The rules below exist because the repo's own history forced them: an
independent audit (docs/parity-report-phase1.md Addendum 4) found
inverted retry claims, bug-corrupted runs, an asymmetric protocol, and an
unsupported cost ratio. Every rule in this standard is a scar from a
corrected mistake. Numbers without a committed source are not numbers.

---

## 1. Suite definition — swapos-v1

- **Name:** `swapos-v1`.
- **Size:** 50 tasks — **17 bugfix / 17 feature / 16 refactor**.
- **Shape:** single-file Python, stdlib only. Each task is one directory
  under `benchmarks/tasks/<category>/<task_id>/` containing
  `problem.md` (the brief), `starter/solution.py` (RED on the tests),
  `reference/solution.py` (GREEN, never shown to any model), and
  `tests/test_<task_id>.py` (the spec).
- **Character:** interview-canon — canonical interview-style problems
  (palindrome, dedupe, LRU, etc.), one file per task, self-contained
  (no network, no sleeps, no randomness; each test file bootstraps
  `sys.path` itself).
- **Task-id format:** `<category>-<nn>` (e.g. `bugfix-07`), unique across
  the suite.

## 2. The sacred grader

- `benchmarks/harness/grader.py` is the **sole pass/fail authority**
  (ADR-0003, MASTER-PROMPT.md §4). Grading contract: replace the task's
  `starter/solution.py` with the candidate output, run `python3 -m pytest
  tests/ -q`; **all tests green = PASS**, anything else = FAIL.
- The grader is **never modified to make results pass**; it only gets
  harder or broader. Any change to the suite (tasks) or to the grader
  **invalidates the comparison** — a result is comparable only against
  the exact suite + grader revision it was measured on. The task suite
  has been untouched since 2026-08-07 (verified in git during the audit).

## 3. Symmetric protocol

Both sides of any comparison run the **identical loop**:

```
REASON (plan) → CODE (solution) → sacred grader → CRITIC
(test-output feedback) → retry
```

- **Attempts:** max 3 code attempts per task.
- **Temperature:** 0.2 (the documented operating point).
- **Critic feedback bound:** 600 characters of test output
  (`feedback[:600]`, the pipeline's `bounded_feedback`).
- **Prompts:** taken **verbatim** from `pipeline/prompts.py`
  (`reason_prompt`, `code_prompt`, `critic_prompt`) — the same composed
  text both sides receive, no extra system framing.
- **One harness runner executes both sides:**
  `benchmarks/harness/run_symmetric_baseline.py`. It is a NEW runner
  written for symmetry; the sacred grader and baseline runner are never
  modified.

The asymmetry that motivated this: the original parity comparison gave
the pipeline retries and the API baseline none. Under the symmetric
protocol the retry loop is available to both sides or to neither — never
one.

## 4. Cost accounting

- Every run records **measured token counts** (`tokens_in` / `tokens_out`
  per run, and per phase where the schema allows).
- The cost estimate (`cost_estimate_usd`) is computed from the measured
  tokens **with explicit price notes recorded in the results JSON**
  (`price_notes` field): which price-per-million-token estimates were
  used, and the raw tokens kept for recomputation. A cost figure without
  its `price_notes` is not publishable.
- **Pipeline runs:** local inference, **zero marginal API cost and zero
  data egress** — this is the sovereignty claim, the only cost framing
  permitted (roadmap red line: no "1/50th cost" or any other cost-ratio
  claim anywhere; see docs/roadmap-to-revenue.md, "Red lines").

## 5. Honesty rules (non-negotiable)

1. Every figure is published **with its committed source**: results JSON
   file path + commit hash (see the benchmark page's source-citation
   table for the pattern).
2. **pass@1 is stated separately from final-with-retries.** The loop's
   contribution is its own reported number (`retry rescues`), on both
   sides.
3. Statistical claims are computed on the **discordant pairs only**
   (exact McNemar), and the p-value is attached to the exact comparison
   it was computed for — never reused across comparisons.
4. **Negative results are published.** Missing a target is data, not
   failure; hiding one is the only firing offense.
5. A claim measured on one run is labeled one-run; a headline claim
   needs independent runs (the page headline requires two).

## 6. Stated suite limits

Every published number ships with these limits, verbatim in spirit:

- **Single-file Python tasks only** — no multi-file repos, no
  non-Python languages, no integration scenarios.
- **One baseline vendor** — deepseek-v4-pro (expand vendors before
  calling this a general validator).
- **n = 50** — the suite is a screening instrument, not a population
  sample; category-level splits (17/17/16) are the granularity the
  sample supports.

## 7. Running the standard

```bash
# structural check (fast)
python3 benchmarks/harness/validate_tasks.py --tasks-dir benchmarks/tasks

# full RED/GREEN verification of every task (slow)
python3 benchmarks/harness/validate_tasks.py --full

# symmetric baseline: frontier API through the identical loop
python3 benchmarks/harness/run_symmetric_baseline.py --help

# quality gate (must stay green)
uv run --with pytest pytest capsule/tests benchmarks/harness/tests pipeline/tests

# publish the benchmark page from the committed evidence
python3 site/build_site.py
```

Results belong in `benchmarks/results/` as committed JSON — a run without
a results file did not happen (ADR-0003).

## 8. Revision history

- 2026-08 — v1.0 with roadmap gate 4: published as the open-funnel
  methodology standard, paired with the benchmark page (`site/`).
