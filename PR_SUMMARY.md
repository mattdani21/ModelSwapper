# PR — benchmark page + validation methodology standard (roadmap gate 4, G4.4)

Branch: `wt/benchmark-page` · base `3bea626` · goal ref: **G4.4** (roadmap-to-revenue.md gate 4: "Benchmark page + methodology writeup").

## What

- **`docs/methodology-standard.md`** (new) — the reusable validation methodology for the open funnel: suite definition (`swapos-v1`, 50 tasks = 17 bugfix / 17 feature / 16 refactor, single-file Python, interview-canon), the sacred grader (`benchmarks/harness/grader.py` — sole pass/fail authority, never modified to make results pass; any change to suite or grader invalidates the comparison), the symmetric protocol (REASON → CODE → sacred grader → CRITIC, 600-char bounded feedback, max 3 attempts, temp 0.2, prompts verbatim from `pipeline/prompts.py`, one runner for both sides: `benchmarks/harness/run_symmetric_baseline.py`), cost accounting (measured `tokens_in`/`tokens_out`, cost estimate with explicit `price_notes` in the results JSON; pipeline runs locally with zero marginal API cost and zero data egress), and stated suite limits (single-file Python only, one baseline vendor deepseek-v4-pro, n=50).
- **`site/`** (new) — deterministic static benchmark page. `site/build_site.py` reads the evidence JSONs under `benchmarks/results/` and emits `site/index.html` (pure HTML/CSS/JS, zero external assets, dark dev-tool aesthetic). Every number is either parsed from a committed results JSON or (pipeline row, doc-sourced) pinned constants with source doc + commit cited on the page; the build asserts invariants against the evidence and fails on drift. Page includes the headline figure area ("48/50 on two independent runs, $0.25–$0.45 per suite"), a comparison table (pipeline vs API-with-identical-loop vs API single-shot), both Step-0 runs, the McNemar statistics (loop-equipped p ≈ 1.0; honest pass@1 p = 0.016, b=7 c=0, per amendment 694eff7), a source-citation footnote table (every figure → file + commit), and an honest-limitations section (hardware floor explicitly an open item — no placeholder numbers).
- **`benchmarks/results/symmetric-baseline-20260825.json`** (added) — the ONLY change under `benchmarks/`: a byte-identical copy of the earlier Step-0 reproduction (48/50, pass@1 46, $0.2461). No changes to `benchmarks/tasks/**` or `benchmarks/harness/**` (sacred, untouched).

## Why

Roadmap gate 4 (`docs/roadmap-to-revenue.md`, "Gates"): the benchmark page + methodology writeup is the only Phase-4 piece the validation-services engine needs, and the open-funnel distribution ("methodology + suite + honest numbers published as a standard"). The page publishes the Step-0 falsification verdict — including the negative results (pass@1 gap, hardware floor unmeasured) — as the marketing, per the roadmap.

## How tested (gate steps, real output)

1. **Quality gate:** `uv run --with pytest pytest capsule/tests benchmarks/harness/tests pipeline/tests` → **37 passed in 1.78s** (capsule 17, compress 8, grader 5, loop 15; exit 0).
2. **Build:** `python3 site/build_site.py` → `wrote site/index.html` (161 lines), run twice and diffed → **byte-identical (deterministic)**; evidence-drift assertions all pass.
3. **Serve check:** `cd site && python3 -m http.server 8000` (background) → `curl -s http://localhost:8000/ | grep -o "48/50" | head -1` → **`48/50`**; server killed after check.
4. **Content audit:** all required figures verified present verbatim (48/50 ×2 runs, pass@1 46/50 ×2, $0.4539 / $0.2461, 3236.0 s / 1977.8 s, 28.24 s, tokens 70,180/209,424 and 35,119/114,293, p ≈ 1.0, p = 0.016 (b=7 c=0), headline + quote); no external assets, no placeholders, no cost-ratio claims.

## Reconciliation note

Both Step-0 runs are shown: canonical `symmetric-baseline-deepseek-v4-pro-20260825-195414.json` (commit 8c7a7a3, run 2026-08-25T18:48:10Z, 48/50, pass@1 46, $0.4539) and the earlier reproduction `symmetric-baseline-20260825.json` (commit cd8b703, run 2026-08-25T05:35:48Z, 48/50, pass@1 46, $0.2461). Both agree on 48/50 and pass@1 46; the $0.45 vs $0.25 difference is timing/pricing, presented honestly as the **$0.25–$0.45 per suite** range (headline wording). The pass@1 comparison (pipeline 41/50 vs API single-shot 48/50, p = 0.016) is stated honestly per reviewer-approved amendment 694eff7; p ≈ 1.0 is attached only to the loop-equipped comparison, never to pass@1. No "1/50th cost" or any other cost-ratio claim appears anywhere (retracted red line); sovereignty/zero-egress framing only.
