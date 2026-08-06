# ADR-0002 — Context Capsule v0 schema

- Status: proposed for review (capsule agent's first deliverable; G0.3)
- Date: 2026-08-06
- Relates: ADR-0001; MASTER-PROMPT.md §1.1, G0.3, G2.3, G2.4

## Context

The pipeline hands state between specialists that are never co-resident. The handoff must (a) survive a weight swap, (b) be model-agnostic, (c) be inspectable/accountable (privacy pitch, audit), and (d) later compress sub-linearly (G2.4). A naive full-transcript handoff grows linearly with task length and leaks the "conversation" framing of a single model.

## Decision

Capsule v0 is a JSON document with a fixed top-level shape:

| Field | Type | Required | Meaning |
|---|---|---|---|
| `schema_version` | string | yes | `"0.1.0"` |
| `task_id` | string | yes | stable id for the task being executed |
| `goal` | string | yes | the objective, restated by the REASON phase |
| `constraints` | string[] | yes | non-negotiables discovered/derived |
| `plan` | array of `{step, status, notes}` | yes | the current plan; status ∈ planned/active/done/blocked |
| `artifacts` | array of `{path, content, kind}` | yes | code/diffs/patches produced; kind ∈ code/diff/test/other |
| `decisions_log` | array of `{at, phase, decision, rationale}` | yes | every material decision + why |
| `phase_history` | array of `{phase, model, started_at, finished_at, swap_in_ms, swap_out_ms, tokens, outcome}` | yes | per-phase telemetry; the swap ledger |
| `meta` | object | yes | created_at, updated_at, capsule_version, budget (max loop iterations, max tokens), run_id |

Serialization rules:

- JSON (UTF-8), one capsule per task run; atomic write (temp file + rename).
- `artifacts[].content` is raw text (code, diffs); binary artifacts are out of scope for v0 (referenced by path, content omitted).
- Capsules are append-only within a run: later phases extend `decisions_log`, `phase_history`, `artifacts`; earlier entries are never mutated in place (auditability).
- Token accounting for G2.4: `len(json.dumps(capsule))` and a tokenizer-based estimate are recorded in `phase_history` at each transition.

## Consequences

- Round-trip guarantee: serialize → deserialize → serialize must be byte-identical (tested in `capsule/tests/`).
- G2.3 ablation uses this capsule vs a naive transcript; the fixed top-level shape is what makes the comparison fair.
- The schema is versioned at the top level; the `capsule/` package owns load/save/validate so no other module pokes at the JSON directly.

## Alternatives considered

- *KV-cache carryover*: rejected — attention state is model-specific, stale across specialists, and memory-heavy; defeats the entire swap thesis (ADR-0001 §2.2).
- *Plain conversation transcript*: kept as the ablation baseline (G2.3), not the design.
- *Binary (msgpack/protobuf)*: rejected for v0 — JSON is inspectable, diffable, and the privacy pitch depends on showing users exactly what left the machine (nothing, at runtime).
