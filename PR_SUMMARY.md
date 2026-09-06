# SWAP-01: content-addressed KV checkpoint identity (G1.3 prerequisite)

## What

KV checkpoint identity is now content-addressed. `kv_checkpoint_name` no
longer mixes model path + file size into a truncated 20-hex digest; the
checkpoint filename is `kv-<sha256>.bin` over a canonical, sorted JSON
identity object — `identity_format_version: 1`, full model artifact SHA-256,
task ID, exact problem, starter and plan text — explicitly UTF-8 encoded,
entire digest used. Two same-size artifacts with different bytes can no
longer share a checkpoint name, so a stale KV cache derived from different
model bytes is never restored.

Supporting changes: the artifact is hashed **once per run per model**
(`run_pipeline` computes the digest at startup and passes the immutable
identity into `run_task`; the loop falls back to one hash per `run_task`
call, never per retry); each `run_task` saves/restores under a **run-private
namespace** subdirectory until runtime/build identity + context settings
join the identity; an unreadable/missing artifact **disables** checkpoint
restore/save for it (no empty/all-zero digest is substituted) while normal
generation continues. Existing `kv-*.bin` files are ignored optimization
artifacts; no result JSON migration; `ModelBackend`/`GenerationResult`/
`TaskRunResult` are unchanged, so cache support stays optional for fakes and
other backends. New ADR: `docs/adr/0006-content-addressed-kv-checkpoint-identity.md`.

## Why

SWAP-01 (docs/execution packet 1, TECHNICAL_SPEC SWAP-01): the previous
size-mixed identity meant two different same-size artifacts at the same path
produced the same checkpoint identity (review finding 2 in
`docs/execution/CONTEXT.md`). G1.3's KV prefix cache is a reliability lever;
its identity must bind to artifact content, not path/size heuristics.

## How tested

New fixtures/tests in `pipeline/tests/test_loop.py` (no real model weights —
tiny temp artifact files): same byte count / different content → different
names; identical bytes at a different path → same name; changed
plan/problem/starter/task → different name; canonical-identity contract pin;
missing artifact → restore/save disabled and normal retried generation still
passes; digest computed exactly once per run (retry never rehashes); a
caller-supplied digest is used without touching the artifact; two runs
against one cache dir get distinct private namespaces.

Gates (from repo root):

1. `python3 -m pytest -q pipeline/tests` → **21 passed**
2. `uv run --with pytest pytest capsule/tests benchmarks/harness/tests pipeline/tests` → **43 passed**
   (uv's cache dir had to point at a writable temp dir — the default
   `~/.cache/uv` is outside this session's file sandbox)
3. `python3 benchmarks/harness/validate_tasks.py --tasks-dir benchmarks/tasks` → **structural OK: 50 tasks**

Benchmark tasks, the grader/harness and historical result JSON were not
touched (only `pipeline/loop.py`, `pipeline/run_pipeline.py`,
`pipeline/tests/test_loop.py`, `docs/adr/0006-*.md`).
