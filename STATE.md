# STATE.md — ModelSwapper (SwapOS)

## Current state

- **Phase 0 — Foundation: in progress (kickoff).** Repo skeleton, governance docs, ADRs 0001–0003, Capsule v0 schema + round-trip tests, benchmark harness + 50-task suite, frontier-API baseline run, and first swap-baseline measurements all landing in this pass.
- **Hardware reality:** development machine is an **Apple M3, 8 GB unified memory** (`sysctl hw.memsize` = 8.0 GB) — that is the **T4 edge tier**, not the T0 target. All Phase 0 swap numbers are measured on this machine as T4-class data; T0 (24 GB) targets remain the trajectory and must be re-measured on real T0 hardware when available.
- **Frontier baseline:** `deepseek-v4-pro` via DeepSeek API (only provider available with an existing key; frontier-class, used strictly for baseline measurement — the core pipeline stays local per §4).
- **Backend:** llama.cpp (Homebrew, Metal-capable) installed on the dev machine. Model candidates (official Qwen GGUFs): Qwen3-4B-Q4_K_M (2.5 GB), Qwen3-8B-Q4_K_M (5.0 GB), Qwen3-0.6B-Q8_0 (0.64 GB, router-class).

## Broken / incomplete

- `runtime/` — no swap engine yet; `swap_runner.py` scaffold is the first measured baseline (G0.1/G0.2).
- `pipeline/` and `router/` — empty stubs by design (Phase 1).
- Benchmark suite: 50 tasks authored; RED/GREEN verified locally; baseline pass rates pending measurement.
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
