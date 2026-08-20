# STATE.md — ModelSwapper (SwapOS)

## Current state

- **Phase 0 — Foundation: in progress (kickoff).** Repo skeleton, governance docs, ADRs 0001–0003, Capsule v0 schema + round-trip tests, benchmark harness + 50-task suite, frontier-API baseline run, and first swap-baseline measurements all landing in this pass.
- **Hardware reality:** development machine is an **Apple M3, 8 GB unified memory** (`sysctl hw.memsize` = 8.0 GB) — that is the **T4 edge tier**, not the T0 target. All Phase 0 swap numbers are measured on this machine as T4-class data; T0 (24 GB) targets remain the trajectory and must be re-measured on real T0 hardware when available.
- **Frontier baseline:** `deepseek-v4-pro` via DeepSeek API (only provider available with an existing key; frontier-class, used strictly for baseline measurement — the core pipeline stays local per §4).
- **Backend:** llama.cpp (Homebrew, Metal-capable) installed on the dev machine. Model candidates (official Qwen GGUFs): Qwen3-4B-Q4_K_M (2.5 GB), Qwen3-8B-Q4_K_M (5.0 GB), Qwen3-0.6B-Q8_0 (0.64 GB, router-class).

## Phase 0 numbers (measured 2026-08-06, T4 tier: 8 GB Apple M3, llama.cpp Metal)

| Metric | Run 1 (v1 sampler) | Run 2 (v2 RSS sampler) | G0.2 T0 target |
|---|---|---|---|
| Cold swap (4B → 0.6B first token) | 2.25 s | **1.64 s** | ≤ 8 s ✓ |
| Warm swap (page-cache reload) | 2.70 s | 4.46 s | ≤ 3 s (met in run 1) |
| Eviction time | 0.06–0.48 s | 0.07–0.19 s | — |
| Peak RSS (4B Q4_K_M) | 1.74 GB | 1.53 GB | T4 ceiling 6.5 GB ✓ |
| Peak RSS (0.6B Q8) | 0.94 GB | 0.92–0.94 GB | ✓ |
| 8B Q4_K_M on 8 GB | — | FAILS (Metal alloc: `failed to fit params to free device memory`) | T4 floor: 4B-class max |

Findings: (1) eviction is nearly free — swap cost is dominated by weight loading; G2.1 (layer-priority streaming) is the right lever. (2) On 8 GB RAM, warm ≈ cold: the page cache cannot hold both models' weights, so the OS evicts the incoming model's cached pages during the outgoing load — warm advantage needs ≥ T0-size RAM. (3) Run-to-run variance 1.6–2.3 s cold / 2.7–4.5 s warm from OS cache state. (4) 8B Q4 does not fit the T4 tier (hardware floor). Raw data: `benchmarks/results/swap_baseline-20260806-233738.json`, `-233855.json` (4B↔0.6B), `-234241.json` (4B↔8B, failure recorded).

## Frontier baseline (measured 2026-08-07, deepseek-v4-pro, suite swapos-v1)

- **48/50 tasks passed (96.0%)** — bugfix 17/17, feature 16/17, refactor 15/16
- Mean 19.3 s/task, est cost **$0.15 for the whole suite (~$0.003/task)**
- Fails: feature-08 (9/10), refactor-12 (8/9) — both single-test near-misses
- Raw data: `benchmarks/results/baseline-deepseek-v4-pro-20260807-001937.json`
- **Phase 1 parity target derived:** ≥ 80% of 96% → pipeline must pass ≥ 76.8% absolute (G1.2)
- **Phase 1 result (2026-08-19, Colab L4, 27B Q4 + 8B Q4, swap-per-phase):**
  **40/50 = 80.0% — G1.2 MET** (bar 76.8%). bugfix 12/17, feature 16/17
  refactor 12/16; mean wall 40.0s = 2.07× API (bar 2× → G1.3 near-miss by
  1.4s), mean load 1.96s, mean evict 0.17s. Retry loop recovered 10 tasks.
  Report: docs/parity-report-phase1.md.
- **Confirmation run (2026-08-20, Colab RTX PRO 6000 97.9GB, same config, temp 0.2):**
  **39/50 = 78.0% — G1.2 CONFIRMED** (two independent sessions/hardware at the
  operating point: 80.0% + 78.0%). bugfix 14/17, feature 14/17, refactor 11/16;
  mean wall 44.4s = 2.30× API, mean load 2.18s, mean evict 0.21s. Temperature
  sensitivity measured (0.6 → 35/50, feature collapses): 0.2 is the operating
  point. G1.2 CLOSED. G1.3 near-miss stands on both GPUs (2.07× / 2.30× vs 2×
  bar) — lever is resident-mode/fewer retries (Phase 2). G1.5 pending 24 GB Air.

## Broken / incomplete

- `runtime/` — swap engine v0 exists (subprocess llama-server: load/generate/evict/measure); in-process engine (mmap, layer-priority, pre-fetch) is Phase 2.
- `pipeline/` and `router/` — empty stubs by design (Phase 1).
- Benchmark suite: **50/50 tasks authored + RED/GREEN verified**; frontier baseline measured (48/50, 96.0%)
- No T0 (24 GB) or T1 (48 GB) hardware available to the swarm yet — those numbers are open.

## Phase 2 (active) — engineering down the swap

- **G2.3 CLOSED (2026-08-20, 27B scale, 8192 ctx)**: capsule 8/8 (100%) @ 788
  tok vs naive 7/8 (87.5%) @ 1663 tok vs single 8/8 (100%) @ 999 tok — verdict
  both halves TRUE (quality ≥, memory strictly better, −53% context). Capsule
  also the fastest arm (20.9 s/task). Report: docs/ablation-capsule-vs-naive.md.
- **G2.2 overlap engine**: mechanics proven at 27B scale (load hiding
  consistent across two A/B runs: 1.04/0.842 vs 1.881/2.099 s/phase; promoted
  swaps pay 0). Wall-clock A/B noisy at n=8 — formal close + G1.3 need the
  full 50-task overlap run (notebook colab-phase2-eval.ipynb, ABLATION_LIMIT=50).
- **G2.4 capsule compression v1**: done (8k budget, sub-linear growth, tests).
- **G2.1 (warm swap ≤ 1.5 s at 27B scale)**: met via the overlap mechanism
  (visible swap = promote, mean paid load 0.842 s); raw sequential 27B load
  remains ~2 s (never paid under overlap).
- Issues: G2.3 (#14) closed; G2.1/G2.2/G2.4 = #12/#13/#15 open (milestone
  "Phase 2 — Engineering down the swap").
- ADR-0005 accepted.

## Blockers

- None. (T0/T1 hardware numbers are scheduling items, not blockers — mechanics are measured on T4 hardware now.)

## Test command

```bash
uv run --with pytest pytest capsule/tests benchmarks/harness/tests
```

## Run command

```bash
# Frontier-API baseline (needs DEEPSEEK_API_KEY from ~/supplementary/.env)
uv run --with pytest benchmarks/harness/run_baseline.py --model deepseek-v4-pro

# Swap baseline on local hardware (needs llama.cpp + downloaded GGUFs in models/)
python3 runtime/swap_runner.py --model-a models/Qwen3-4B-Q4_K_M.gguf --model-b models/Qwen3-8B-Q4_K_M.gguf
```
