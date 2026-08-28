# Roadmap to Revenue — ModelSwapper / io-ai (2026-08)

**Audited 2026-08-21 by an independent reasoner (claude-opus-5, opencode)
with every claim verified against committed data. This revision absorbs
the audit. See docs/parity-report-phase1.md Addendum 4 for the data
corrections it forced (retry-loop claim inverted, bug-corrupted runs,
pass@1 asymmetry, 4.7× cost).**

Honest premise: the runtime becomes sellable only after Phase 4 output
("a thing people run"). The validation methodology is sellable NOW as a
service. Two engines, one runway. The binding constraint is DEMAND
(zero recorded buyer conversations), not engineering.

## Step 0 — the falsification experiment — **DONE (2026-08-25, $0.45)**

Symmetric baseline executed: deepseek-v4-pro with the pipeline's exact
loop (REASON → CODE → grader → CRITIC → retry, 3 attempts, same prompts,
temp 0.2) scored **48/50 (pass@1 46/50, retries +2)** vs the pipeline
**47/50 (pass@1 41/50, retries +6)**. The frontier model with the same
loop did NOT reach ~50/50 — the thesis survived its hardest test.
Discordant pairs 2 vs 3 (McNemar p≈1.0). The defensible claim is now
MEASURED: "statistically indistinguishable from frontier on this suite
under an identical loop protocol (47 vs 48), at zero marginal cost and
zero data egress." Secondary finding: the retry loop is worth +6 to the
small-model pipeline vs +2 to the API — smaller specialists have more
headroom for feedback loops. Evidence: parity-report Addendum 5 +
`symmetric-baseline-deepseek-v4-pro-20260825-195414.json`. Publish the
method + numbers (including the negative results) as the marketing.

## Gate 0 — employment conflict, resolved in writing, BEFORE any buyer conversation

The services engine sells to the employer's peer set through the same
network as the job hunt. SA insurer contracts routinely carry IP
assignment + moonlighting clauses. This is a potential ownership and
runway risk. Resolve (written clearance / scope note) before the first
conversation. [Matt's move — the single most important one]

## Engine 1 — Services (Empyrean; partner-led, artifact-first)

Validation program, not a report: methodology + adaptation of the suite
to the CLIENT'S OWN tasks + report + 12-month re-run rights.
**R400–750k** per program (R80–150k reports sit in the procurement dead
zone — too big for discretionary spend, too small for vendor
onboarding). Day rate for embedded work **R12–18k** (R4–6k is
commodity-dev pricing for an actuary's credential). Distribution:
SA boutique risk/actuarial consultancy or SI carries procurement,
compliance, PI cover, first-line support; Matt is the named methodology
owner doing 3–5 expert days per engagement (~half the revenue, the only
shape that survives a day job + Korea). Asynchronous by contract
(48–72 h response, written deliverables — it is a Korean work visa
question whether independent consulting is even permitted; verify
before pricing).

## Engine 2 — Product (after Phase 4, bootstrapped, partner-carried)

| Channel | What sells | Price band | When |
|---|---|---|---|
| Enterprise license (air-gapped) | Runtime for regulated/offline teams — SOVEREIGNTY is the feature (zero marginal cost, zero egress), NOT savings (measured: 4.7× the API on rented GPU; the 1/50th claim has no committed measurement and is retracted from all pitches) | **R1.2–2.5m/yr per deployment**, sold through a partner who carries procurement/SLA/compliance — do not sell an SLA that cannot be honored from Seoul | After Phase 4 v1 + one reference install |
| Edge/SLM line (T4-16) | Cheap-Mac private coding agents | Hardware + license bundle | 2027+ (needs T4-16 numbers) |
| Open funnel | Methodology + suite + honest numbers published as a standard (the runtime stays closed — but the METHODOLOGY is the scarce asset and publishing it is the only distribution available to 10 h/week) | converts inbound | continuous |

## Gates (hard dependencies, corrected order)

0. Employment conflict in writing → 1. Symmetric baseline (~$1, this week)
→ 2. **One design-partner conversation** (the only gate that produces
information you cannot generate alone: "grade our actual Java repo with
our harness" changes everything upstream) → 3. G1.5 on a rented M-series
instance (~$1–2/h, 4–8 h run — not blocked on hardware you don't own;
the Air run is a demo, the rented run is the measurement) → 4. Benchmark
page + methodology writeup (~2 days static site; the only Phase-4 piece
Engine 1 needs) → 5. CLI/installer ONLY once a buyer exists.

## Red lines

- No "1/50th cost" anywhere — retracted; sovereignty framing only.
- No revenue pitch before the symmetric baseline result.
- No direct enterprise sales from Seoul; partner-carried or not at all.
- The benchmark suite's limits are stated with every number (single-file
  Python, interview-canon tasks, one baseline vendor — expand vendors
  and task classes before calling it a general validator).
- If a ≥100B resident beats pipeline quality AND cost/task on 24GB-class
  hardware (positioning-freetoken.md red line), re-derive before selling.

## Timeline

- **Aug–Oct 2026**: employment clearance → symmetric baseline (published)
  → design-partner conversation → rented-Mac G1.5 → benchmark page +
  methodology standard → validation program pilot (partner-led).
- **Nov–Dec**: Korea applications (job watch silent until Dec 1);
  report #1 if pilot landed.
- **2027**: Seoul base; venture autonomous: validation programs
  (partner-distributed, portable) + license conversations from the
  published standard + the SLM line. Alternative branch, priced
  honestly: the published methodology IS the credential — "the person
  who built the independent evaluation standard for local LLMs in
  regulated finance" is itself a Seoul hiring/speaking asset compatible
  with the day job, no entity, no insurance, no visa gymnastics.

## What I can build vs what is Matt's move

- Mine: symmetric-baseline runner, benchmark page, methodology writeup,
  report/one-pager templates, T4-16 cert numbers, pricing pack.
- Matt's: employment clearance (gate 0), the design-partner conversation,
  price sign-off, the launch post.
