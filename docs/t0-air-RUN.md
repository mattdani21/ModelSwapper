# T0 Runbook — ModelSwapper on a 24 GB MacBook Air (G1.5 / launch demo)

Status: **PREPARED, not yet run** — this is the measurement that turns the
cost/hardware-floor claim from projected into measured.

## Why this run matters

Every headline number so far (40/50, 47/50, 45/50) came from rented Colab
GPUs. The master prompt's north star is a laptop: **the same pipeline at
frontier-class quality, offline, private, on owned hardware.** This run:

1. Closes **G1.5** — peak unified memory < 20 GB on the 24 GB machine,
   measured every 30 s.
2. Gives the **launch demo number** — pass rate of the exact 47/50 config
   (27B Q4 + 8B Q4, 8192 ctx, temp 0.2) on Metal.
3. Grounds the **cost claim** (owned hardware vs API at list prices).
4. Re-measures swap/load on a real T0 box (hardware reality beats paper).

## How to run (on the 24 GB Air)

```bash
git clone https://github.com/mattdani21/ModelSwapper.git
cd ModelSwapper
bash hardware/t0_air_run.sh            # smoke (3 tasks) then full 50
```

The script installs what it needs (brew llama.cpp, a python venv with
pytest), downloads the GGUFs with size guards, samples memory to a CSV, and
runs smoke → full. **The full 50-task run takes ~4–8 h on Metal** (27B Q4 at
~8–15 tok/s) — run it overnight. Use `--smoke-only` to validate first
(~20–40 min).

### Expected numbers (honest priors)

| Metric | Expectation | Source |
|---|---|---|
| Pass rate (Q4, 8192 ctx) | 40–47/50 | GPU runs: 47/50 sequential; Metal quality ≈ same models, slower wall |
| Peak unified memory (Q4) | **19–21 GB — borderline vs the 20 GB ceiling** | 16.8 GB weights + ~2 GB KV + buffers |
| Peak unified memory (Q3_K_M) | ~15–16 GB — comfortably under | 12.6 GB weights |
| Wall per task | 4–8 min | Metal token rates |
| Mean load per phase | ~2–4 s (local NVMe, sequential backend) | Phase 0 local baselines |

### Decision tree

1. Smoke passes and peak memory < 20 GB → the Q4 full run IS the demo.
2. Peak memory ≥ 20 GB on smoke → rerun with the Q3 fallback:
   `MODEL_Q=Q3_K_M bash hardware/t0_air_run.sh` (quality at Q3 typically
   within 1–3 tasks of Q4; the parity claim is re-derived from the Q3
   number, honestly).
3. Smoke fails → save the log (`tee` the output) and report back: which
   task, what error, the memory CSV.

## What to send back

After the run, either push from the Air:

```bash
git add benchmarks/results && git commit -m "t0 air run $(date +%F)" && git push
```

or copy these two files over:
- `benchmarks/results/pipeline-air-t0-<date>.json`
- `benchmarks/results/air-memory-<date>.csv`

## Notes

- The Air needs ~25 GB free disk and a ~22 GB download (Q4) or ~18 GB (Q3).
- The pipeline runs fully offline once models are downloaded — task data
  never leaves the machine (privacy is a feature, severity-1 if broken).
- `LLAMA_NGPU=99` offloads all layers to Metal; if the Air reports Metal
  allocation failures with Q4, use Q3 (same as the 8 GB box's 8B failure
  class, documented in `hardware/tiers.yaml` T4).
