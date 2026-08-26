# PR_SUMMARY — Validation-program documentation templates

## What

Adds `templates/validation-program/` — three documentation templates for
the partner-led validation program (roadmap Engine 1, Services/Empyrean),
built on the audit-corrected record: `docs/roadmap-to-revenue.md`
(audited 2026-08-21) and `docs/parity-report-phase1.md` Addenda 4–5
(symmetric baseline / roadmap Step 0 measured results), plus the
reviewer-approved amendment `commit 694eff7` (corrected pass@1 McNemar
p-value).

- `templates/validation-program/one-pager.md` — client-facing shape
  (structure only, placeholders): what is validated (the client's own
  tasks adapted to the swapos-v1 methodology — not a fixed public
  benchmark), the symmetric protocol (identical REASON → CODE → grader →
  CRITIC → retry loop vs a frontier API baseline), deliverables
  (adapted suite + run + report + 12-month re-run rights), honest-limits
  (single-file Python, interview-canon task classes, one baseline
  vendor), sovereignty/zero-egress framing (no cost-ratio claims),
  `[SCOPE]` / `[TIMELINE]` / `[PRICE]` placeholders carrying only the
  roadmap-approved price shape (program band R400–750k; embedded
  day-rate shape R12–18k; final pricing: Matt's sign-off), and one
  clearly marked EXAMPLE block with the Step-0 measured numbers.
- `templates/validation-program/validation-report.md` — the report
  deliverable skeleton: methodology incl. grader-integrity statement
  (graders fixed before the run, not tuned on results), pass@1 / final /
  retry-rescue / exact-binomial-McNemar / per-category tables (each with
  a marked EXAMPLE row), cost accounting (measured tokens + API cost;
  local-run zero-marginal-cost note), limits section, 12-month re-run
  rights placeholders, claims-discipline checklist (only measured claims
  published; negative results reported — "missing a target is data, not
  failure"; no cost-ratio claims; limits travel with every number).
- `templates/validation-program/README.md` — partner-led delivery flow
  (design-partner conversation → scope → adapt suite → run → report →
  re-run rights), roles (partner: procurement/compliance/first-line
  support; Matt: named methodology owner), red lines, sources of truth.

## Why

The validation methodology is sellable now (roadmap Step 0 done
2026-08-25: 47/50 vs 48/50 under the identical loop). These templates
are the "report/one-pager templates" deliverable the roadmap assigns to
the build side; they make every client-facing number carry the red-line
limits and keep the retracted cost-ratio claim out of all future
pitches.

## How tested

- Documentation-only change: no code in `pipeline/`, `runtime/`,
  `router/`, `benchmarks/`, `models/` was touched (`git status` shows
  only the three new template files).
- Quality gate run: `pytest capsule/tests benchmarks/harness/tests
  pipeline/tests -q` → **37 passed**.
- Benchmark structural check: `validate_tasks.py --tasks-dir
  benchmarks/tasks` → **structural OK: 50 tasks**.
- Markdown structure validated programmatically: table column counts
  consistent, separator rows present, all relative links resolve
  (`../../docs/...`, `../../benchmarks/results/...`), headers valid.
- Forbidden-content check: no retracted cost-ratio claim (and no
  cost-ratio claim of any kind) anywhere in the templates; price figures
  are only the roadmap-approved bands.

## Files

```
templates/validation-program/one-pager.md
templates/validation-program/validation-report.md
templates/validation-program/README.md
```

## Commit

- Branch: `wt/validation-templates` (base 3bea626)
- Commit: `a01430d` — `docs: validation-program templates — one-pager + report + README (Engine 1 / roadmap Step 0)` (3 files, +439).
- This PR_SUMMARY.md follows in the next commit.

## Independent verification (wrapper, 2026-08-26)

- Re-read all three templates; red lines hold: no cost-ratio claim ("1/50th"
  appears nowhere; the only "1/50" substrings are pass-rate fractions like
  41/50), price placeholders carry only the roadmap bands (R400–750k program,
  R12–18k day rate) plus "final pricing: Matt", all EXAMPLE rows are labeled
  "not a client result".
- Re-derived the EXAMPLE numbers from the committed JSONs:
  `symmetric-baseline-deepseek-v4-pro-20260825-195414.json` (tokens_in 70,180 /
  tokens_out 209,424 / cost $0.4539 → "$0.45"; pass@1 46, final 48; per-category
  16/17, 16/17, 16/16) and `sequential-colab-27b-20260820-full50-8192.json`
  (pass@1 41, final 47; per-category 17/17, 17/17, 13/16) and
  `baseline-deepseek-v4-pro-20260807-001937.json` (cost $0.1463 → "$0.15").
  All match the template EXAMPLE rows.
- Discordant pairs recomputed from the JSONs: pipeline-only passes
  bugfix-08 + feature-08 (2); API-with-loop-only passes refactor-01,
  refactor-02, refactor-12 (3); both-fail 0; exact McNemar p = 1.0 (min(2,3),
  n=5) — matches the templates' p≈1.0 row.
- **Flag for reviewer (docs inconsistency, not a number change):**
  `docs/parity-report-phase1.md` Addendum 5 prose lists the pipeline's third
  failed task as `refactor-11`, but the committed result JSONs show
  `refactor-02`. Counts (2 vs 3) and p-value are identical either way. The
  templates use the JSON-verified id (refactor-02) and cite Addendum 5 as the
  source — an Addendum 5 text fix may be warranted in a later card.

## Notes

- **The templates carry examples of table shape only.** Every EXAMPLE
  row reproduces this repo's own published Step-0 measured numbers
  (pipeline 47/50 final vs API-with-same-loop 48/50; pass@1 41/50 vs
  46/50; retries +6 vs +2; McNemar p≈1.0 loop comparison, discordant
  pairs 2 vs 3; exact p=0.016 for pass@1 41/50 vs API single-shot 48/50,
  b=7, c=0, per `commit 694eff7`) and is explicitly labeled **NOT a
  client result**. No client-facing claim is made from them.
- Four numbers: none moved by this docs-only change; it packages the
  already-measured Step-0 quality-parity claim for Engine 1 revenue.
