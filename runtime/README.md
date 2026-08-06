# runtime/ — the swap engine

Phase 0: `swap_runner.py` measures the G0.1/G0.2 baseline on real hardware
(llama.cpp `llama-server` subprocess: load → generate → evict → reload,
cold/warm, memory reclamation verified by process inspection). Results →
`benchmarks/results/swap_baseline-*.json`.

Phase 1+: the engine API (`load(model)`, `generate(prompt, capsule)`,
`evict(model)`, `residency(policy)`) evolves here behind ADR-0001.
