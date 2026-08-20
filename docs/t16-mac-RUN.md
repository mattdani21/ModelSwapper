# T4-16 Runbook — the very-small-Mac coding stack (16 GB)

Status: **PREPARED, not yet run.** The 16 GB Mac is the top of the T4 band
(master prompt §1.3: edge = 8–16 GB) and the first tier where the
**30B-class coding specialist** fits.

## The stack (all swap-fit for 16 GB, one resident at a time)

| Role | Model | Weights | Peak (weights + KV@8192 + overhead) |
|---|---|---|---|
| REASON | Qwen3-14B Q4_K_M | 9.0 GB | ~11 GB |
| CODE | **Qwen3-Coder-30B-A3B UD-IQ2_M** | **10.8 GB** | **~14 GB** |
| REVIEW | Qwen3-8B Q4_K_M | 5.0 GB | ~7 GB |

Why the A3B: 30B-class MoE with **3B active params** — the quality of a big
coder at small-hardware speeds. Q2-class quantization is the price of the
16 GB fit; the 14B Q4 alternative (`CODE_MODEL=qwen14b`) is the quality-per-
byte comparator, and the smoke run decides which one the full run uses.

Policy: **aggressive swap** — one specialist resident at a time (sequential
backend; `OVERLAP_CEILING_GB=13` so the two-slot engine correctly refuses
two residents on this tier). Context 8192, temp 0.2 — the Phase-2 config.

## How to run

```bash
git clone https://github.com/mattdani21/ModelSwapper.git
cd ModelSwapper
bash hardware/t16_mac_run.sh --smoke-only    # ~20-40 min
bash hardware/t16_mac_run.sh                 # full 50, overnight (~3-6 h)
```

The script installs what it needs, downloads all three GGUFs with size
guards, samples unified memory every 30 s to a CSV, and runs smoke → full.
Peak unified memory ceiling for this tier: **13 GB** (leave the OS ~3 GB).

## Expectations (honest priors)

- Pass rate: unknown until measured — this is a NEW model set (A3B at IQ2 is
  untested in our pipeline). Priors: 14B-Q4-class pipeline scored 7/10
  locally at the 8 GB floor; the A3B coder should beat a 14B dense coder on
  coding tasks if the Q2 quant doesn't eat the gains. The smoke (3 tasks)
  gives the first signal; the full run is the number.
- Wall: A3B's 3B-active MoE on Metal is fast (~2-4 min/task); 14B dense
  slower (~4-8 min/task).
- The point of this tier: **the cheapest Mac that runs the full pipeline** —
  it moves the hardware-floor number (north star #3) and the cost story.

## Send back

Push from the 16 GB machine (`git add benchmarks/results && git commit -m "t4-16 run" && git push`)
or copy `pipeline-t416-*.json` + `t416-memory-*.csv` over.
