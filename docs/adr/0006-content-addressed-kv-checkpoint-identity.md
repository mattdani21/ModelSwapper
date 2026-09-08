# ADR-0006 — Content-addressed KV checkpoint identity

- Status: accepted (execution packet SWAP-01)
- Date: 2026-09-06
- Relates: ADR-0004 (loop v1), ADR-0002 (capsule),
  docs/execution/TECHNICAL_SPEC.md (SWAP-01), docs/g1.3-kv-prefix-cache.md, G1.3

## Context

The cross-turn KV prefix cache (G1.3, issue #16, `docs/g1.3-kv-prefix-cache.md`)
checkpoints the CODE phase slot after the first code attempt and restores it
on retries. The checkpoint filename previously mixed the model *path*, the
model *file size*, the task ID and the problem/starter/plan text, truncated
to a 20-hex digest.

That identity is not content-addressed: two different artifacts of the same
size at the same path (a swapped GGUF, a re-downloaded file, a rebuilt
quantization) produce the same checkpoint identity, so a stale KV checkpoint
derived from different model bytes could be restored. Review finding 2 in
`docs/execution/CONTEXT.md` records the gap without claiming a reproduced
failure; SWAP-01 specifies the correction.

## Decision

1. **Checkpoint identity is content.** The checkpoint filename is `kv-<sha256>.bin`
   where the digest is SHA-256 over a canonical, sorted JSON object containing
   exactly: identity format version (`"identity_format_version": 1`), the full
   model artifact SHA-256 (`"model_sha256"`), the task ID, and the exact
   problem, starter and plan text. Canonical serialization is
   `json.dumps(payload, sort_keys=True, separators=(",", ":"))`, explicitly
   UTF-8 encoded; the ENTIRE 64-hex digest is used in the filename. Path and
   file size play no role: identical bytes at another path produce the same
   name, and same-size different bytes never collide.
2. **Hash once per run per model.** The model artifact is hashed once per run
   (per CLI invocation in `run_pipeline.py`) and the immutable digest is
   passed into checkpoint creation; `run_task` falls back to computing it once
   per call when no digest is supplied. Retries within a task never rehash the
   artifact.
3. **Run-private cache namespace.** Runtime/build identity and context
   settings are not yet part of the checkpoint identity, so each `run_task`
   call saves/restores under a fresh private subdirectory
   (`<kv-cache-dir>/run-<uuid>`). Unknown runtime metadata can therefore never
   cause cross-run reuse; retries within one run share the namespace, which is
   what makes the cross-turn cache useful. Cross-run reuse becomes safe only
   when a backend compatibility namespace (runtime/build identity + context
   settings) is added to the identity — deferred.
4. **Unreadable artifact disables the cache.** If a model artifact cannot be
   read (missing/unreadable file), checkpoint restore/save is disabled for it
   and generation proceeds normally. An empty or all-zero digest is never
   substituted for real content.
5. **No migration.** Existing `kv-*.bin` files are optimization artifacts and
   are ignored; no result JSON is migrated. `ModelBackend`/`GenerationResult`/
   `TaskRunResult` contracts are unchanged; optional cache support remains
   optional for fakes and other backends.

## Consequences

- A checkpoint can only be restored when the artifact bytes, task text and
  plan that produced it are identical — the stale-same-size-reuse failure
  class is closed by construction.
- One full-artifact read per model per run is the only hashing cost of the
  cache; retries and per-task loops add none.
- Cache files from runs under older identities simply never match a new
  run's namespace/name; deleting them is optional cleanup.
- Identity format versioning means future field additions or canonicalization
  changes are explicit and do not silently invalidate or reuse old
  checkpoints.

## Non-decisions (deferred)

- A backend compatibility namespace (llama.cpp build, context settings,
  quant/template metadata) that would allow safe cross-run cache reuse.
- Cross-model KV reuse; migration of existing cache files; benchmark edits.
