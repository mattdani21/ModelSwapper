# Symmetric baseline — Step 0 falsification result (2026-08-25)

## Question
Does giving deepseek-v4-pro (API) the pipeline's **identical loop** — grader
feedback → critic → retry, max 3 attempts — lift it above the single-shot
48/50, or change the comparison vs the local pipeline? Step 0 of
`docs/roadmap-to-revenue.md`: if the API with the loop scores ~50/50, Engine 2
(cloud API product) is the wrong shelf; if the gap stays inside noise, the
defensible claim is "statistically indistinguishable from frontier on this
suite".

## Method
New runner `benchmarks/run_symmetric_baseline.py`, executing the sacred code
**read-only**: `run_baseline`'s `SYSTEM_PROMPT`, `build_user_prompt`,
`extract_code`, and price constants; `grader.grade`; `pipeline.prompts`'
`CRITIC_SYSTEM`/`critic_prompt` verbatim; and `pipeline/loop.py`'s
bounded-feedback convention (`feedback[:600]`). Same 50 task prompts as
`run_baseline`; `deepseek-v4-pro` (api.deepseek.com) for **both** code and
critic; temperature 0.2, max_tokens 8192, max 3 code attempts, cost cap $2.
Run `2026-08-25T05:35:48Z`, 50/50 tasks, `partial: false`, no gates.

## Results
| Run | pass | pass@1 | rescued by loop | per-category (bugfix/feature/refactor) | failing tasks |
|---|---|---|---|---|---|
| API single-shot | 48/50 | 48 | — | 17/17, 16/17, 15/16 | feature-08, refactor-12 |
| API + loop | 48/50 | 46 | 2 | 17/17, 16/17, 15/16 | feature-08, refactor-12 |
| pipeline + loop | 47/50 | 41 | 6 | 17/17, 17/17, 13/16 | refactor-01, refactor-02, refactor-12 |

Symmetric-run detail (recomputed from the JSON): attempts histogram
{1: 46, 2: 2, 3: 2}; the 2 loop-rescued tasks are **bugfix-08, refactor-07** —
both passed single-shot; failures: **feature-08** (3 attempts, 0/0 tests,
3,554/26,194 tokens in/out, "budget exhausted after 3 code attempts") and
**refactor-12** (3 attempts, stuck at 8/9). Wall clock 1977.8 s ≈ 33 min.

## Paired statistics
Exact two-sided McNemar, binomial on discordant pairs
(p = 2·P(X ≤ min(b,c)), X ~ Bin(b+c, ½); b = A-pass/B-fail, c = B-pass/A-fail):

| Pair | b | c | p |
|---|---|---|---|
| (a) API+loop vs API single-shot | 0 | 0 | **1.0** |
| (b) API+loop vs pipeline+loop | 2 | 1 | **1.0** |
| (c) API+loop pass@1 (46) vs pipeline pass@1 (41) | 7 | 2 | **0.18** |
| (d) API single-shot pass@1 (48) vs pipeline pass@1 (41) | 7 | 0 | **0.016** |

- **(a)** has **zero discordant pairs**: the loop run's fail set is byte-identical
  to single-shot (feature-08, refactor-12) → p = 1.0. The loop changed nothing
  for the API.
- **(b)** pipeline's 3 fails (refactor-01, refactor-02, refactor-12) vs API's 2
  (feature-08, refactor-12): 3 discordant pairs → p = 1.0.
- **(c)** p = 0.18 — **not significant**. Power caveat: n = 50 with only 9
  discordant pairs; p > 0.05 does not prove equality, it means the observed
  gap is inside noise.
- **(d)** **discrepancy flag:** `docs/four-number-proof.md` §2.1 states
  "41/50 single-shot vs 48/50 single-shot (McNemar p ≈ 1.0)". Recomputation
  gives **p = 0.016** for that pass@1-only pair (7 API-only passes, 0
  pipeline-only, 2⁻⁷·2 = 0.0156): the pass@1 gap is *not* noise at n = 50.
  The p ≈ 1.0 result holds only for the **loop-equipped** comparison (47 vs
  48, test (b)); the four-number-proof's p≈1.0 does not transfer to pass@1.

## Verdict
- **The falsification attempt did NOT produce ~50/50.** The API with the
  identical loop scores exactly **48/50**, with the identical fail set to
  single-shot (feature-08, refactor-12). The loop adds **zero passes** to the
  API arm at ~$0.10 extra cost. The retry loop is not a frontier-leveling
  device per se; Engine-2 (cloud API + loop) would not reach ~50/50.
- **The parity claim SURVIVES.** Loop-equipped pipeline 47/50 vs API 48/50 →
  McNemar p = 1.0: "statistically indistinguishable from frontier on this
  suite" is still the defensible claim. pass@1 41 vs 46 → p = 0.18, inside
  noise. The pipeline's loop rescues 6 tasks; the API's loop rescues 2
  (bugfix-08, refactor-07) — both tasks that already passed single-shot: run
  noise, consistent with the suite's documented 19/50 flip instability.
- **Failure modes:** feature-08 burned the full 8192-token output budget on
  all 3 attempts (0/0 tests — no collectable output) and refactor-12 stuck at
  8/9 across all 3 attempts. These are the same two tasks that fail
  single-shot AND with the loop — the loop cannot rescue them for the API.
- **Engine-2 implication:** nothing in this experiment justifies a cloud-API
  product. The frontier API with the same loop costs ~$0.25/50 tasks (~$0.10
  more than the $0.146 single-shot) and gains nothing, while the local
  pipeline matches it (p = 1.0) at zero marginal cost and zero data egress.

## Cost accounting
At the **same constants as run_baseline** (PRICE_IN/OUT_PER_M = $0.50/$2.00
per 1M tokens): 35,119 in × 0.50/1M + 114,293 out × 2.00/1M = 0.0176 + 0.2286
= **$0.2461** (matches the JSON header; raw tokens recorded in the JSON for
recomputation — `price_notes`). Tokens by phase: code 30,397 in / 107,150 out;
critic 4,722 in / 7,143 out (sums equal totals). vs single-shot $0.1463
(22,410 in / 67,567 out): **+$0.0998**. $0.2461 < $1 Step-0 budget (runner
cost cap $2.0 not hit).

## Raw evidence
- `benchmarks/results/symmetric-baseline-20260825.json` (this run; all numbers
  above recomputed from it, plus `baseline-deepseek-v4-pro-20260807-001937.json`
  and `sequential-colab-27b-20260820-full50-8192.json`).
- Runner commit: `ce4ed25` ("Add symmetric-baseline runner (Step 0
  falsification experiment)").
- This doc: commit `DOC_COMMIT_PLACEHOLDER` — **git commit was blocked by the
  sandbox** (index.lock write outside the workspace; escalation unavailable),
  so the doc-hash placeholder stands. Commands to run outside the sandbox:
  `git add docs/symmetric-baseline.md && git commit -m "docs: symmetric-baseline Step 0 falsification evidence/verdict (48/50, loop adds zero passes, parity survives)"`.
