# Phase 1 — pipeline eval on Kaggle GPU (G1.1–G1.3)

Prepared on the Mac (code + CPU-passing tests); executed on Kaggle (muscle).

## What runs

The REASON → CODE → REVIEW pipeline (ADR-0004) over the full 50-task suite,
with swap-per-phase semantics (each specialist loaded fresh per phase, evicted
after — the swap timings are part of the results).

## Specialists (thesis-aligned set)

| Role | Model | File | Size |
|---|---|---|---|
| REASON | Qwen3-14B | `Qwen3-14B-Q4_K_M.gguf` (Qwen/Qwen3-14B-GGUF) | 9.0 GB |
| CODE | Qwen3-Coder-30B-A3B (MoE, 3B active) | `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf` (unsloth) — **or** `-Q3_K_M` if the kernel gets a single 16 GB GPU | 18.6 / 14.7 GB |
| REVIEW | Qwen3-14B (same file as REASON) | — | — |

The notebook adapts automatically: `nvidia-smi` memory total ≥ 30 GB → Q4_K_M,
else Q3_K_M (single T4). Specialists ≤ 32B class pre-quantization (constitution §4).

## Steps (in the notebook, `notebooks/phase1-pipeline-eval.ipynb`)

1. Print `nvidia-smi`; clone `mattdani21/ModelSwapper` at the pinned commit (below).
2. Build `llama-server` with CUDA: `git clone --depth 1 https://github.com/ggml-org/llama.cpp && cmake -B build -DGGML_CUDA=ON -DCMAKE_BUILD_TYPE=Release && cmake --build build -j --target llama-server`
3. `pip install pytest` (the sacred grader shells out to pytest).
4. Download the GGUFs from Hugging Face (public repos; HF_TOKEN env used only if set).
5. Run:
   ```
   LLAMA_CONTEXT=4096 python3 pipeline/run_pipeline.py \
     --models-json '{"reason":"<14B>","code":"<coder>","review":"<14B>"}' \
     --out /kaggle/working/pipeline-results.json \
     --capsule-dir /kaggle/working/capsules \
     --port-base 8950
   ```
   Checkpointing: results are rewritten after every task, so a timeout still
   yields completed tasks.
6. Zip `/kaggle/working/pipeline-results.json` + `capsules/` → `results.zip`.

## Estimated GPU time

~50 tasks × 3–5 phases × (load 30–90 s + generation 15–90 s) ≈ **1.5–4 h**.
Kaggle GPU quota: 30 h/week free; swarm cap 8 h/week (registry `gpu_usage`).

## What comes back

- `benchmarks/results/pipeline-<date>.json` — pass rate (vs 96.0% baseline →
  G1.2 bar = 76.8%), per-category breakdown, per-phase swap timings (G1.3),
  capsule sizes, tokens
- `capsules/*.json` — the audit trail (plan, attempts, critic feedback) for G2.3
- The numbers are committed to the repo by the orchestrator after the run.

## Local gates (already green on the Mac)

- `pytest pipeline/tests capsule/tests benchmarks/harness/tests` → 20 passed
- Local dry-run on 10 tasks with the 4B/0.6B set → `benchmarks/results/pipeline-local-4b-dryrun.json`

## Pinned commit

Set at push time (the kernel clones exactly this commit).
