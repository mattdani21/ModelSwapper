# PR_SUMMARY — 2026-08-28 landing: Step-0 symmetric baseline + p-value amendment + benchmark page (gate 4) + validation-program templates (Engine 1)

Branch: `wt/land-2026-08-28` (merged onto main as commit) · goal refs: **Step 0 / Gate 4 / Engine 1** (docs/roadmap-to-revenue.md, audited 2026-08-21)

## What

Four reviewer-approved strands merged onto main in one landing, plus the one
review-required page fix:

1. **Step 0 symmetric baseline (review t_d24fd5e4 APPROVED)** — the falsification
   experiment: `benchmarks/run_symmetric_baseline.py` (deepseek-v4-pro with the
   pipeline's identical REASON → CODE → grader → CRITIC → retry loop),
   evidence `benchmarks/results/symmetric-baseline-20260825.json`
   (48/50, pass@1 46, $0.2461), narrative `docs/symmetric-baseline.md`.
   Verdict: falsification did NOT produce ~50/50; parity claim survives
   (47 vs 48, McNemar p≈1.0).
2. **pass@1 p-value amendment (t_fd73b8df)** — `docs/four-number-proof.md` §2.1
   and `docs/parity-report-phase1.md` Addendum 4 item 3 corrected to exact
   McNemar p = 0.016 (b=7 c=0) for the pass@1-only comparison (was p≈1.0).
3. **Benchmark page + methodology standard (gate 4, review t_23f2732a — 1
   required fix applied, see below)** — `docs/methodology-standard.md`
   (open-funnel validation methodology), `site/build_site.py` + `site/index.html`
   (deterministic static parity-evidence page, zero external assets),
   canonical run evidence `benchmarks/results/symmetric-baseline-deepseek-v4-pro-20260825-195414.json`
   (48/50, pass@1 46, $0.4539), and the reconciliation note ($0.25–$0.45 per suite).
4. **Validation-program templates (review t_2e6095e4 APPROVED)** — Engine 1
   deliverables `templates/validation-program/{one-pager,validation-report,README}.md`
   (partner-led validation program shape, roadmap-approved price bands only,
   EXAMPLE blocks with measured numbers).

**Required review fix applied in this landing (t_23f2732a):** `site/build_site.py`
PIPELINE_DOC.failed and LOOP_MCNEMAR.api_only_tasks now list `refactor-02`
(pipeline's real third failure, per committed JSON) instead of `refactor-11`
(passed 7/7, iteration 1). Recommended fixes also applied: build now asserts
pipeline failed-task ids against the parsed JSON, and `docs/parity-report-phase1.md`
Addendum 5 pipeline-failed cell aligned to `refactor-02`.

## Why

The 08-27 operating cycle was blocked by a DeepSeek billing 402 before creating
anything — three reviewer-approved strands had been sitting off-main for 1–3
cycles. This landing closes that stranding and delivers the roadmap's
publication-critical pieces (Step-0 verdict, page, methodology) plus the
Engine-1 sales templates onto main.

## How tested (gate steps, real output)

1. **Quality gate:** `uv run --with pytest pytest capsule/tests benchmarks/harness/tests pipeline/tests` → **37 passed** (rerun independently by wrapper after the fix).
2. **Sacred rule:** `git diff main..HEAD -- benchmarks/tasks benchmarks/harness` = **0 lines** (only NEW files added under benchmarks/: the runner + two result JSONs).
3. **Build determinism:** `python3 site/build_site.py` run twice → **byte-identical index.html**; page asserts invariants against committed JSONs (incl. the new failed-task invariant).
4. **Serve check:** `python3 -m http.server -d site` + curl → headline "48/50 on two independent runs, $0.25–$0.45 per suite" renders.
5. **Merge hygiene:** both lineage-A (approved base b762749) and lineage-B (page/templates base 3bea626) strands merged; only conflict was PR_SUMMARY.md (add/add) — resolved as this combined summary; parity-report Addendum 4 amendment + Addendum 5 both present; roadmap Step 0 DONE recorded; g2.4/notebooks intact.

## Reconciliation note

Two Step-0 runs are published on the page, both 48/50: canonical
`symmetric-baseline-deepseek-v4-pro-20260825-195414.json` ($0.4539) and
reproduction `symmetric-baseline-20260825.json` ($0.2461) — headline "$0.25–$0.45
per suite". No "1/50th cost" or any cost-ratio claim anywhere (retracted red
line); hardware floor (G1.5) stated as open item, no placeholders; zero external
assets.
