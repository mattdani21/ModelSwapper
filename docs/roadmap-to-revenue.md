# Roadmap to Revenue — ModelSwapper / io-ai (2026-08)

Honest premise: the runtime becomes sellable only after Phase 4 output
("a thing people run"). The validation methodology is sellable NOW as a
service. Two engines, one runway.

## Engine 1 — Services (revenue this quarter-to-next, Empyrean)

Independent validation of local/agentic AI for regulated finance. The
sacred 50-task suite + measured methodology + published numbers are the
product. The FreeToken/Ollama/llama.cpp wave makes this *the* open
question for insurers/banks: "which local stack actually works, and how
do we know?"

- Offer: validation report — a vendor's stack (or an internal candidate)
  run through the suite + methodology, with an actuarial-grade evidence
  file. Deliverable = the report + re-gradeable JSON.
- Pricing: fixed-fee per report (R80–150k range) or day-rate for
  embedded validation (R4–6k/day).
- Buyer: Sanlam-adjacent + South African insurers first (warm), Korean
  banks/insurers after the move (Dec 2026+). The apply-window job hunt
  and this share the same network.
- Gate: a template report + a one-pager (I can build both).

## Engine 2 — Product (revenue after Phase 4, bootstrapped)

Phase 4 (master prompt weeks 17–24) outputs:
1. **One-command install + `swapos run` CLI** (G4.1)
2. **Agent-harness integration** (G4.2) — Hermes-class agents calling the
   runtime as their inference backend
3. **Observability** (G4.3) — per-task reports: swaps, timings, capsule
   sizes, cost-equivalent vs API, Telegram hooks
4. **Public benchmark page + launch narrative** (G4.4) — the lead magnet:
   "frontier-class agentic coding on a laptop, offline, private"

Monetization of the product engine, in order of realism:

| Channel | What sells | Price band | When |
|---|---|---|---|
| Enterprise license (air-gapped) | The runtime for regulated/offline teams (banks, insurers, defense, legal) — privacy is the feature | R150–500k/yr per deployment + implementation days | After G4.1–G4.4 + one reference install (Q1–Q2 2027) |
| Premium support/implementation (Empyrean) | Install, tune, integrate into the buyer's agent stack | Day-rate + retainer | Same window |
| Edge/SLM line (T4-16 stack) | Cheap-Mac private coding agents for compliance-heavy niches | Hardware + license bundle | 2027+ (needs the T4-16 numbers) |
| Open-core funnel | Public runtime free; the benchmark page + reports convert inbound | Freemium → license | Continuous |

## Gates that must land first (hard dependencies)

1. **G1.5: the 24GB Air run** — the sellable claim ("94% parity offline on
   a laptop") is not pitchable before the owned-hardware measurement. In
   flight now.
2. **Phase 4 v1: CLI + benchmark page** — the buyer conversation opener.
   Benchmark page = static site from `benchmarks/results/` (cheap to
   build, I can do it).
3. **One reference engagement** — first enterprise install, even at cost,
   for the case study. The Air demo video is the sales artifact.

## Timeline (mapped to constraints)

- **Aug–Oct 2026**: Air run lands → G1.3 KV-cache lever → Phase 4 v1
  (CLI + benchmark page + observability) → validation-report template +
  one-pager. Pilot validation engagement if a warm conversation opens.
- **Nov–Dec 2026**: Korea applications (job watch silent until Dec 1);
  product polish continues; validation report #1 (paid) if pilot landed.
- **2027**: Seoul base; venture runs autonomously (his operating model);
  revenue mix: validation reports (portable, remote) + first license
  conversations from the benchmark page + io-ai SLM line (T4-16).

## Red lines (don't oversell)

- No revenue pitch before the Air measurement — the cost claim is a
  projection until then (state it as such in every deck).
- No fundraising assumption: consulting + license path is bootstrapped.
- The pipeline layer is the moat; the benchmark is the proof. If a
  ≥100B resident beats pipeline quality AND cost/task on 24GB-class
  hardware (positioning-freetoken.md red line), re-derive before selling.

## What I can build vs what is Matt's move

- Mine: report template, one-pager, benchmark page, CLI polish, T4-16
  cert numbers, observability reports.
- Matt's: the first buyer conversation (warm network), price sign-off,
  the launch post (LinkedIn drafts in ~/journey/).
