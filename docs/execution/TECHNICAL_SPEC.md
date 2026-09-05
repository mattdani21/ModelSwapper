# Technical specification

## Existing interfaces to preserve

`ModelBackend.start()` loads a backend; `generate(prompt, max_tokens, temperature, prefetch_model, kv_restore, kv_save)` returns `GenerationResult`; `stop()` returns eviction seconds. Optional cache support must not become mandatory for fakes or other backends. `TaskRunResult` keeps task ID, category, pass result, iterations, test counts, phases, capsule bytes, wall time and an optional error.

A successful task is decided by the mechanical grader. Model self-review cannot change `passed` to true. Preserve seconds for backend timing fields, milliseconds for capsule swap history and the existing `peak_rss_kb` field; do not equate a process RSS observation with total unified-memory usage.

## SWAP-01: cache identity and reuse

The checkpoint identity is SHA-256 over a canonical, sorted JSON object containing identity format version `1`, full model artifact SHA-256, task ID, exact problem, starter and plan text. UTF-8 encoding is explicit. Use the entire digest in `kv-<digest>.bin`. The backend compatibility namespace must additionally include runtime/build identity and context settings before cross-run reuse is enabled.

Hash model contents once per run/model and pass that immutable identity into checkpoint creation; do not rehash gigabytes on every retry. Use a run-private cache namespace initially so unknown runtime metadata cannot cause cross-run reuse. If an artifact cannot be read, disable checkpoint restore/save for it and perform normal generation; do not substitute an empty or all-zero digest. Existing cache files are optimization artifacts and may be ignored; no migration of result JSON is needed.

Fixtures: two temporary model files with the same byte count but different content; identical bytes copied to a different path; changed plan text; unreadable/missing file. No actual model weights are required. Expected identity follows content and prefix, not path alone. Existing correct behavior on cache failure still falls back to full prefill.

## SWAP-02: backend ownership

Every successfully constructed backend whose start is attempted receives exactly one cleanup attempt by its owning layer, including start failure, generation failure, grader exception and exhausted retry budget. A resident backend is owned by an outer `try/finally` around the task lifecycle; a per-phase backend is owned by that phase. An overlap engine retains its existing outer ownership in the runner; avoid double cleanup of a shared engine.

Preserve the original failure as the primary error if cleanup also fails. All failures remain failed tasks, and error evidence names the phase. Do not change grader semantics. Add `pipeline/tests` to the existing CI pytest invocation; preserve structural suite validation.

## SWAP-03: latency experiment contract

Prepare a comparison manifest containing commit, task-pack digest, complete model digests/quantization, llama.cpp build, hardware, context size, temperature, output budget, retry budget, warm/cold policy, baseline result reference, run IDs and commands. Hold all values except the declared treatment fixed. Use the same frozen tasks and an identical loop protocol. Keep failed tasks in denominators and record infrastructure failures distinctly.

Record per-task quality, total wall time, phase load/evict/generate/prefill timings and cache hit/miss evidence in new result files. Compare paired task outcomes and mean total time. State sampling uncertainty and the small-suite limitation; failure to reject a difference does not establish equivalence. G1.3 passes only at the original total-time bar, with its stated baseline and G1.2 maintained. Report subphase improvement separately.

## SWAP-04: hardware evidence contract

Follow the T0 runbook on a verified 24 GB host. Record host model, OS, memory capacity, model digests, runtime build, sampler/method and peak memory for every task. G1.5 requires peak unified-memory use below 20 GB for every task, with operating-system headroom; if the sampler measures only process RSS, label the gate unproven. OOM, swap pressure and unfinished tasks remain visible. A reduced suite or remote large-GPU run cannot certify T0.

## Compatibility and rollback

These tickets do not change benchmark tasks or historical result files. Cache naming can be reverted or disabled without affecting correctness. Lifecycle fixes preserve return schemas. Measurement outputs are append-only new artifacts; an invalid run is retained and labeled invalid rather than deleted.
