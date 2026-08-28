# templates/validation-program — README

How the validation-program templates are used in the **partner-led
delivery flow** (roadmap Engine 1 — Services/Empyrean). These templates
are **starting points, not finished client deliverables**: every
placeholder must be replaced, every EXAMPLE row removed or replaced with
this engagement's measured data, and every page reviewed by the
methodology owner before it goes to a client.

## Roles (roadmap-to-revenue.md, Engine 1)

| Role | Carries |
|---|---|
| **Partner** (SA boutique risk/actuarial consultancy or SI) | procurement, compliance, PI cover, first-line support — all client-facing contact |
| **Matt** | the **named methodology owner** — 3–5 expert days per engagement, asynchronous by contract (48–72 h response, written deliverables), final pricing sign-off |
| Templates | structure only — never a substitute for either role's sign-off |

## Delivery flow

```
design-partner conversation → scope → adapt suite → run → report → re-run rights
```

1. **Design-partner conversation** (roadmap Gate 2 — the only gate that
   produces information you cannot generate alone). The conversation
   decides what "grade our actual [repo] with our harness" means for
   this client; the one-pager is the conversation's client-facing shape.
2. **Scope** — `[SCOPE: client tasks, count, categories]`, `[TIMELINE:
   weeks]`, `[PRICE]`. Price placeholders carry the roadmap-approved
   shape only: **program band R400–750k**, **embedded day-rate shape
   R12–18k**, final pricing is **Matt's sign-off**. No figures beyond
   those bands.
3. **Adapt suite** — re-express the client's own tasks in the swapos-v1
   contract (brief + starter + tests-as-grader, single-file Python,
   RED/GREEN-verified, frozen). Not a fixed public benchmark.
4. **Run** — the symmetric protocol: the identical loop (REASON → CODE →
   grader → CRITIC → retry, bounded attempts) on the local pipeline
   **and** on a frontier API baseline (one vendor) on the client's tasks.
5. **Report** — `validation-report.md` is the deliverable skeleton:
   methodology + grader-integrity statement, pass@1 / final / retry
   rescues / McNemar / per-category tables, cost accounting,
   limits-with-every-number, re-run rights, claims-discipline checklist.
6. **Re-run rights** — the 12-month re-run rights terms are part of the
   program deliverables; `[re-run window]`, `[task-suite refresh terms]`,
   `[re-run pricing — Matt's sign-off]`.

## Files

| File | Used when | By |
|---|---|---|
| `one-pager.md` | client-facing shape of the program — what is validated, the symmetric protocol, deliverables, honest limits, sovereignty framing, price/timeline placeholders, example table shape | partner leads, Matt reviews |
| `validation-report.md` | the report deliverable after a run | Matt authors, partner forwards |
| `README.md` (this file) | running the flow | both |

## Red lines that apply to every use (roadmap-to-revenue.md)

- **No cost-ratio claims** — no savings ratios, no cost multipliers; the
  previously floated cost-ratio claim is retracted. Sovereignty framing
  only: local execution, zero data egress, zero marginal cost per run.
- **Limits with every number** — single-file Python, interview-canon
  task classes (bugfix, feature, refactor), one baseline vendor. The
  limits section is non-negotiable and travels with every number.
- **No invented pricing** — program band R400–750k; embedded day-rate
  shape R12–18k; final pricing: Matt's sign-off.
- **No revenue pitch before the symmetric baseline result** — Step 0 is
  done (2026-08-25, measured 47/50 vs 48/50 under the identical loop);
  the templates' EXAMPLE rows reproduce that published result and are
  **never** presented as client results.
- **Negative results are reported** — missing a target is data, not
  failure. A template with the negative-results row deleted is not an
  improvement; it is a violation.

## Sources of truth

- [docs/roadmap-to-revenue.md](../../docs/roadmap-to-revenue.md) — Engine 1,
  price bands, gates, red lines (audited 2026-08-21).
- [docs/parity-report-phase1.md](../../docs/parity-report-phase1.md) —
  Addendum 4 (audit corrections: protocol asymmetry, retry-loop claim,
  cost framing) and Addendum 5 (symmetric baseline / roadmap Step 0
  measured results).
- [symmetric-baseline-deepseek-v4-pro-20260825-195414.json](../../benchmarks/results/symmetric-baseline-deepseek-v4-pro-20260825-195414.json)
  — the Step-0 measured data behind the EXAMPLE rows.
- Reviewer-approved amendment `commit 694eff7` — corrected exact
  McNemar p = 0.016 (b=7, c=0) for the pass@1 41/50 vs single-shot
  48/50 comparison.
