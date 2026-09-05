# Intent

Enable a developer to run a reason → code → mechanical review → critic/retry workflow using local specialist models and a portable Context Capsule. Success is measured on the same frozen tasks against an explicitly identified baseline.

## Users and value

The first user is a technical evaluator with local compute and privacy requirements. The immediate deliverable is a reproducible runtime evaluation: code output, test outcome, phase timings, memory observations and a complete run manifest. Installation and licensing follow evidence and a validated user need.

## Outcomes

- Quality: satisfy the G1.2 ratio on the frozen suite; report absolute counts and denominators, including all failed runs.
- Latency: close G1.3 using measured total task time, not only a faster subphase.
- Hardware: independently measure G1.5 on the specified 24 GB machine; an 8 GB or large GPU run is a different evidence lane.
- Economics: preserve actual cost basis and unknown values; the historical 1/50th-cost thesis is not an established result.

## Boundaries

The core uses local inference and specialists at most 32B class. Explicit API baselines are separate experiments. Capsule handoff must remain model-agnostic; a KV checkpoint is an optional optimization for a compatible model and prefix. Frozen oracles are never changed to rescue a candidate.

The master prompt defines the long-term research goals. This package sequences reliability and measurement work within those goals. It does not authorize publication, paid compute, additional hardware or a new commercial commitment.
