# Positioning vs FreeToken (competitive note, 2026-08-21)

Source: arXiv:2608.16157 "FreeToken: Efficient Edge-Native MoE Serving with
Bandwidth-Adaptive Execution" (Yang et al.; Han, Zaharia, Stoica et al.).
Tweet: @Andy_ShuoYang 2026-08-21 (3–4× decode / 6–30× prefill vs Ollama).

## What FreeToken is

An edge-native MoE **serving engine**: expert-level residency (hot experts on
GPU, LRU expert cache, bandwidth-adaptive split — move q* = m·B_PCIe/B_Host
experts over PCIe, compute the rest on CPU), full-layer double-buffered
prefill, and semantic-aware KV checkpoints across agent turns (re-prefill
only the suffix). Claimed: 35B on an 8GB laptop → 284B on a gaming desktop →
753B on one workstation GPU. 20+ MoE models supported.

## Threat matrix

| Dimension | Verdict |
|---|---|
| Hardware-floor narrative | **Threat** — "one big model fits" is the naive alternative to "many small specialists"; their number (284B) is bigger than ours (27B) |
| Swap granularity | **Threat** — expert-level is finer than model-level for fitting ONE model; ours is model-agnostic (dense + MoE, any GGUF), theirs is MoE-only |
| Pipeline/orchestration | **Not a threat** — they serve ONE model; no specialist division, no capsule, no retry loop. Complementary layer: a faster substrate makes our specialists faster |
| Quality parity | **Not a threat** — parity is a pipeline property (94% measured: division of labor + capsule + retry + operating point). Serving engines don't provide it |
| Context efficiency | **Ours wins by design** — capsule grows sub-linearly (8k cap); their KV cache grows linearly with turns |
| Verification | **Their claims unreproduced** — ours are committed, re-gradeable JSON |
| Speed at the floor | **Ours wins by design** — 3B-active A3B coder vs CPU-expert-swapped big MoE per token |

## The red line (testable, not assumed)

If an engine ships that runs a ≥100B-class resident model on 24 GB-class
hardware AND beats the pipeline on quality AND cost-per-task on the same
benchmark suite, the single-model-resident assumption must be re-derived:
run it as the "single" arm of the G2.3 ablation at scale. Until then, the
measured position stands: pipeline 94% parity, capsule > naive > resident
on context efficiency.

## Response (in motion)

1. **Adopt cross-turn KV prefix caching for retry phases** (their suffix-only
   re-prefill = our critic→code retry pattern) — the G1.3 timing lever.
   Issue #16. Does not violate the capsule design: intra-model KV state.
2. **Benchmark FreeToken on the sacred suite when it ships** (GGUF + API →
   new ModelBackend, A/B vs llama.cpp). Also the independent-validation
   offering (regulated-finance angle).
3. **Narrative**: the category is validated by A-list research; the pipeline
   layer + measured claims are the differentiator.

## Standing conclusion

FreeToken threatens the *hardware-floor* story at the margin, not the
*pipeline* story. The moat is orchestration + measurement, not fit.
