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

Findings: (1) eviction is nearly free — swap cost is dominated by weight loading; G2.1 (layer-priority streaming) is the right lever. (2) On 8 GB RAM, warm ≈ cold: the page cache cannot hold both models' weights, so the OS evicts the incoming model's cached pages during the outgoing load — warm advantage needs ≥ T0-size RAM. (3) Run-to-run variance 1.6–2.3 s cold / 2.7–4.5 s warm from OS cache state. Raw data: `benchmarks/results/swap_baseline-20260806-233738.json` + `swap_baseline-20260806-234540.json`. 8B-class measurement pending (download complete).

## Broken / incomplete

- `runtime/` — swap engine v0 exists (subprocess llama-server: load/generate/evict/measure); in-process engine (mmap, layer-priority, pre-fetch) is Phase 2.
- `pipeline/` and `router/` — empty stubs by design (Phase 1).
- Benchmark suite: 50 tasks authored (bugfix 17, refactor 16, feature 17 pending re-dispatch); RED/GREEN verified; baseline pass rates pending measurement.
- No T0 (24 GB) or T1 (48 GB) hardware available to the swarm yet — those numbers are open.

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
