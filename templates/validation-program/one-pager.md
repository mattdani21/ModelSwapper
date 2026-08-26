# Validation Program — One-Pager (Template)

> **TEMPLATE — structure only, not a finished pitch.** Replace every
> `[PLACEHOLDER]` before this page goes to a client. The only concrete
> numbers this page may carry are (a) placeholders and (b) the clearly
> marked EXAMPLE block at the bottom, which reproduces our own measured
> Step-0 baseline to illustrate table shape and is **NOT a client result**.

## What is validated — the client's own tasks

This program validates **[SCOPE: client tasks, count, categories]** — the
client's **own** tasks, adapted to the swapos-v1 methodology. It is a
**task-suite adaptation**, not a fixed public benchmark administered
as-is.

- The client's tasks are re-expressed in the swapos-v1 task contract:
  a problem brief + starting code + a tests-as-grader, with every task
  verified RED (fails on the starting state) and GREEN (passes on a
  reference) **before** the run.
- Task classes covered are the interview-canon classes — **bugfix,
  feature, refactor** — wherever the client's tasks fit them. Tasks
  outside those classes are scoped out or adapted explicitly; they are
  never silently assumed away (see Honest limits).
- We do **not** run a generic public benchmark and claim it generalizes
  to the client. The claim, if any, is about *these* tasks, *this* run,
  *this* protocol.

## The symmetric protocol — the comparison that makes results defensible

The same loop — **REASON → CODE → grader → CRITIC → retry**, bounded
attempts — is run **identically** on the client's tasks, twice:

1. **The local pipeline**, on hardware the client owns or controls.
2. **A frontier API baseline** with the *same* loop: same prompts, same
   temperature, same attempt bound, same grader — `[BASELINE VENDOR:
   one vendor — the red line; any additional vendor is an expansion,
   agreed and priced separately]`.

The only differences are the model and where it runs. That is what makes
the comparison defensible: any gap is attributable to the systems under
test, not confounded by protocol. **pass@1 and final-with-retries are
reported separately** (protocol-asymmetry correction, parity-report
Addendum 4) — a headline that hides the retry loop is not published.

## Deliverables

1. **Adapted task suite** — `[SCOPE]` re-expressed in the swapos-v1
   contract, RED/GREEN-verified, frozen for the run.
2. **The run** — both arms of the symmetric protocol on the client's
   tasks, with run artifacts (per-task results, prompts, grader output).
3. **The report** — pass@1, final pass rate, retry rescues, discordant
   pairs with exact McNemar p-values, per-category breakdown, cost
   accounting, and the limits section attached to every number.
4. **12-month re-run rights** — the frozen suite can be re-run within
   `[re-run window]` without re-purchase; `[task-suite refresh terms]`
   and `[re-run pricing — Matt's sign-off]` per contract.

## Honest limits — stated with every number (non-negotiable)

The methodology measures what it measures, and the limits travel with
every number in this document and in the report (roadmap red line):

- **Single-file Python tasks only** — stdlib, no packages, no multi-file
  repos, no non-Python services.
- **Interview-canon task classes only** — bugfix, feature, refactor.
  This is not a general validator for other task classes or languages.
- **One baseline vendor** — results are comparisons against a single
  frontier API vendor, not a vendor landscape.

If the client's tasks fall outside these limits, the program is adapted
or scoped out — never quietly re-labeled. This section is
non-negotiable: a version of this page without it is not published.

## Sovereignty — local execution, zero data egress, zero marginal cost

- Runs **locally** on hardware the client owns or controls.
- **Zero data egress**: no task data leaves the machine except the
  explicit baseline API calls, which are logged as such.
- **Zero marginal cost per run**: re-runs cost nothing beyond
  electricity.
- The claim is **sovereignty, not savings**: no cost-ratio claims are
  made, ever (a previously floated cost-ratio claim is retracted —
  roadmap red line).

## Price and timeline (placeholders)

| Field | Placeholder |
|---|---|
| Scope | [SCOPE: client tasks, count, categories] |
| Timeline | [TIMELINE: weeks] |
| Price | [PRICE] |

Price shape — roadmap-approved facts only; **do not invent figures
beyond these bands**:

- **Program band: R400–750k** per validation program.
- **Embedded day-rate shape: R12–18k** per day.
- **Final pricing: Matt's sign-off** — `[PRICE: Matt to confirm]`.

## EXAMPLE — Step-0 measured numbers from our own symmetric baseline, shown to illustrate table shape; NOT a client result

> Every figure below comes from our published Step-0 symmetric baseline
> (2026-08-25; [docs/parity-report-phase1.md](../../docs/parity-report-phase1.md)
> Addendum 5, source data
> [symmetric-baseline-deepseek-v4-pro-20260825-195414.json](../../benchmarks/results/symmetric-baseline-deepseek-v4-pro-20260825-195414.json)).
> It exists only to show the table shape a client report would carry.
> It says nothing about any client's tasks.

| Metric | SwapOS pipeline (local) | Frontier API with the same loop |
|---|---|---|
| pass@1 | 41/50 (82%) | 46/50 (92%) |
| retry rescues | +6 | +2 |
| **final (with retries)** | **47/50 (94%)** | **48/50 (96%)** |

- Discordant pairs, loop comparison (final 47/50 vs 48/50): 2
  pipeline-only passes (bugfix-08, feature-08) vs 3 API-only passes
  (refactor-01, refactor-02, refactor-12) → exact McNemar **p ≈ 1.0**
  (statistically indistinguishable under the identical loop protocol).
- pass@1 41/50 vs the API's single-shot 48/50: exact McNemar
  **p = 0.016** (b=7, c=0) — a significant gap at n=50, per the
  reviewer-approved amendment (`commit 694eff7`; recomputed from the
  three committed result JSONs cited there).
- Claim shape this example illustrates (our own published claim, source
  [docs/roadmap-to-revenue.md](../../docs/roadmap-to-revenue.md) Step 0):
  "statistically indistinguishable
  from a frontier API on this suite under an identical loop protocol
  (47 vs 48), at zero marginal cost and zero data egress."

---

*Template source: `templates/validation-program/one-pager.md`. Red-line
reminders: no cost-ratio claims; limits with every number; price bands
are R400–750k (program) and R12–18k/day (embedded) only; final pricing
is Matt's sign-off.*
