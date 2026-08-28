# Validation Report — [CLIENT] — [ENGAGEMENT ID] (Template)

> **TEMPLATE — structure only.** Replace every `[PLACEHOLDER]` with this
> engagement's real data. Rows marked **EXAMPLE** reproduce our own
> measured Step-0 baseline to illustrate table shape and are **NOT client
> results** — delete or replace them with the engagement's measured rows
> before this report leaves the building. The limits section (§5) travels
> with every number in this report (roadmap red line).

- Client: `[CLIENT]` · Engagement: `[ENGAGEMENT ID]`
- Program window: `[START]` – `[END]` · Suite version: `[suite version / freeze commit]`
- Run artifacts: `[run IDs / result JSON paths]`
- Baseline vendor: `[BASELINE VENDOR — one vendor, the red line]`

---

## 1. Methodology

### 1.1 Task suite — adapted from swapos-v1 to the client's tasks

The suite is **not** a fixed public benchmark. The client's own tasks
(`[SCOPE: client tasks, count, categories]`) were re-expressed in the
swapos-v1 task contract: a problem brief + starting code + a
tests-as-grader, single-file Python, stdlib only, verified **RED**
(fails on the starting state) and **GREEN** (passes on a reference)
before the run.

- Adaptation notes: `[what was adapted, which tasks mapped to which
  interview-canon class — bugfix / feature / refactor, what was scoped
  out and why]`
- Freeze: the suite and its graders were frozen at `[freeze commit /
  hash]` before any model saw them.

### 1.2 The symmetric protocol

The same loop — **REASON → CODE → grader → CRITIC → retry**, bounded
attempts — was run **identically** against a frontier API baseline on
the client's tasks:

| Protocol element | Setting |
|---|---|
| Loop | REASON → CODE → grader → CRITIC (test-output feedback, `[feedback bound chars]` bound) → retry, up to `[max attempts]` attempts |
| Prompts | `[verbatim from pipeline prompts / pinned prompt text]` |
| Temperature | `[temperature]` |
| Grader | `[grader name / commit hash — sacred, fixed before the run]` |
| Baseline | `[vendor, model]` — one baseline vendor |
| Arms | local pipeline; baseline with the same loop; baseline single-shot (for the pass@1 asymmetry check, parity-report Addendum 4) |

**pass@1 and final-with-retries are reported separately** — a headline
that hides the retry loop is not published.

### 1.3 Grader integrity statement (non-negotiable)

- All graders and checks were **defined before the run**, fixed in
  advance, and were **not tuned on results**.
- The suite and grader were frozen for the duration of the run; any
  change after the run is published as an **amendment**, never as a
  retrofit.
- RED/GREEN was re-verified at `[date]` with `[result]`; grader output
  for every task is attached (`[artifact path]`).
- Signed off: `[methodology owner — Matt]`, `[reviewer]`,
  `[date]`.

---

## 2. Results

> Every table below shows a placeholder row plus one clearly marked
> EXAMPLE row from our Step-0 symmetric baseline (source
> [docs/parity-report-phase1.md](../../docs/parity-report-phase1.md) Addendum 5;
> data
> [symmetric-baseline-deepseek-v4-pro-20260825-195414.json](../../benchmarks/results/symmetric-baseline-deepseek-v4-pro-20260825-195414.json)
> and
> [sequential-colab-27b-20260820-full50-8192.json](../../benchmarks/results/sequential-colab-27b-20260820-full50-8192.json)).

### 2.1 pass@1

| Model | pass@1 | rate | notes |
|---|---|---|---|
| `[LOCAL PIPELINE]` | `[n/N]` | `[%]` | `[notes]` |
| `[BASELINE — same loop]` | `[n/N]` | `[%]` | `[notes]` |
| `[BASELINE — single shot]` | `[n/N]` | `[%]` | required for the asymmetry check |
| **EXAMPLE (Step-0, not a client result)** — SwapOS pipeline | 41/50 | 82% | 27B+8B specialists, 8192 ctx |
| **EXAMPLE (Step-0, not a client result)** — frontier API, same loop | 46/50 | 92% | deepseek-v4-pro |
| **EXAMPLE (Step-0, not a client result)** — frontier API, single shot | 48/50 | 96% | original baseline score |

### 2.2 Final pass rate (with retries)

| Model | final | rate | retries taken |
|---|---|---|---|
| `[LOCAL PIPELINE]` | `[n/N]` | `[%]` | `[+N]` |
| `[BASELINE — same loop]` | `[n/N]` | `[%]` | `[+N]` |
| **EXAMPLE (Step-0, not a client result)** — SwapOS pipeline | 47/50 | 94% | +6 |
| **EXAMPLE (Step-0, not a client result)** — frontier API, same loop | 48/50 | 96% | +2 |

### 2.3 Retry rescues

Tasks that **failed at pass@1 and passed on a retry** — the retry loop's
measured contribution:

| Model | rescued by retry loop | pass@1 → final |
|---|---|---|
| `[LOCAL PIPELINE]` | `[+N]` | `[n/N] → [n/N]` |
| `[BASELINE — same loop]` | `[+N]` | `[n/N] → [n/N]` |
| **EXAMPLE (Step-0, not a client result)** — SwapOS pipeline | +6 | 41/50 → 47/50 |
| **EXAMPLE (Step-0, not a client result)** — frontier API, same loop | +2 | 46/50 → 48/50 |

> Secondary finding from our Step-0 example (not a client result): the
> loop rescued more for the small-model pipeline (+6) than for the
> frontier API (+2) — smaller specialists have more headroom for
> feedback loops. A client report states the same comparison only if
> this engagement measured it.

### 2.4 Discordant pairs and McNemar (exact binomial)

For each pair of arms, count discordant tasks only: **b** = tasks the
first arm passed and the second failed; **c** = tasks the second arm
passed and the first failed. The exact two-sided binomial McNemar
p-value is computed on `min(b, c)` with `n = b + c`, p = 0.5. A p-value
below `[significance threshold, default 0.05]` means the gap is larger
than noise at this suite size.

| Comparison | b | c | exact McNemar p | reading |
|---|---|---|---|---|
| `[pipeline final]` vs `[baseline final]` | `[b]` | `[c]` | `[p]` | `[significant / indistinguishable]` |
| `[pipeline pass@1]` vs `[baseline single-shot]` | `[b]` | `[c]` | `[p]` | `[significant / indistinguishable]` |
| **EXAMPLE (Step-0, not a client result)** — pipeline final 47/50 vs API-with-same-loop 48/50 | 2 | 3 | ≈ 1.0 | indistinguishable under the identical loop protocol (discordant pairs: 2 pipeline-only — bugfix-08, feature-08; 3 API-only — refactor-01/02/12) |
| **EXAMPLE (Step-0, not a client result)** — pipeline pass@1 41/50 vs API single-shot 48/50 | 7 | 0 | 0.016 | significant gap at n=50, not inside noise — per reviewer-approved amendment `commit 694eff7` |

> The Step-0 example shows the honest shape: the loop-equipped
> comparison is statistically indistinguishable, while the pass@1 gap
> against single-shot is real and must be reported, not buried.
> (The p = 0.016 figure follows the reviewer-approved amendment
> `commit 694eff7`.)

### 2.5 Per-category breakdown

| Category | `[PIPELINE]` | `[BASELINE]` | Δ |
|---|---|---|---|
| bugfix | `[n/N]` | `[n/N]` | `[Δ]` |
| feature | `[n/N]` | `[n/N]` | `[Δ]` |
| refactor | `[n/N]` | `[n/N]` | `[Δ]` |
| **EXAMPLE (Step-0, not a client result)** — pipeline 47/50 run | bugfix 17/17, feature 17/17, refactor 13/16 | — | — |
| **EXAMPLE (Step-0, not a client result)** — frontier API, same loop | — | bugfix 16/17, feature 16/17, refactor 16/16 | — |

---

## 3. Cost accounting

### 3.1 Measured tokens and API cost

| Run | input tokens | output tokens | API cost | price notes |
|---|---|---|---|---|
| `[baseline arm — single shot]` | `[n]` | `[n]` | `[USD]` | `[price notes]` |
| `[baseline arm — same loop]` | `[n]` | `[n]` | `[USD]` | `[price notes]` |
| **EXAMPLE (Step-0, not a client result)** — frontier API, same loop | 70,180 | 209,424 | $0.45 | same price estimates as `run_baseline.py`; raw tokens recorded |
| **EXAMPLE (Step-0, not a client result)** — frontier API, single shot | `[see baseline result JSON]` | `[see baseline result JSON]` | $0.15 | measured 2026-08-07 baseline |

### 3.2 Local-run cost note (sovereignty framing only)

- The local pipeline arm ran on `[hardware]` with **zero marginal cost
  per run** and **zero data egress** — no task data left the machine
  except the explicit baseline API calls, which were logged as such.
- The claim is sovereignty, not savings: **no cost-ratio claims** are
  made in this report (a previously floated cost-ratio claim is
  retracted — roadmap red line).

---

## 4. Limits — stated with every number (non-negotiable, roadmap red line)

Every number above carries these limits:

- **Single-file Python tasks only** — stdlib, no packages, no multi-file
  repos, no non-Python services.
- **Interview-canon task classes only** — bugfix, feature, refactor.
  Not a general validator for other task classes or languages.
- **One baseline vendor** — comparisons are against a single frontier
  API vendor, not a vendor landscape.

Missing a target is data, not failure — but a number published without
its limits is not publishable.

---

## 5. 12-month re-run rights (placeholders)

| Term | Value |
|---|---|
| Re-run window | `[re-run window — within 12 months of report date]` |
| Task-suite refresh terms | `[task-suite refresh terms — e.g. suite frozen at report version; refresh = new adaptation, priced as a new scope]` |
| Re-run pricing | `[re-run pricing — Matt's sign-off]` |

---

## 6. Claims-discipline checklist

- [ ] **Only measured claims may be published** — every number in this
      report traces to a committed run artifact (`[result JSON paths]`).
- [ ] **Negative results are reported** — missing a target is data, not
      failure; nothing is hidden, amended silently, or retrofitted.
- [ ] **No cost-ratio claims** — no savings ratios, no cost multipliers.
- [ ] **Limits travel with every number** — §4 is attached wherever any
      number from this report is quoted.
- [ ] **pass@1 and final-with-retries reported separately** — no
      headline that hides the retry loop.
- [ ] **Amendments are amendments** — any post-run change to graders,
      prompts, or scoring is published as a dated amendment with its own
      review.
- [ ] Methodology owner sign-off: `[Matt — date]`.

---

*Template source: `validation-report.md` (this file). Companion:
[`one-pager.md`](one-pager.md) (client-facing shape), [`README.md`](README.md)
(delivery flow). Source data for EXAMPLE rows:
[docs/parity-report-phase1.md](../../docs/parity-report-phase1.md) Addenda 4–5
and
[benchmarks/results/symmetric-baseline-deepseek-v4-pro-20260825-195414.json](../../benchmarks/results/symmetric-baseline-deepseek-v4-pro-20260825-195414.json)
(+ [sequential-colab-27b-20260820-full50-8192.json](../../benchmarks/results/sequential-colab-27b-20260820-full50-8192.json)).*
