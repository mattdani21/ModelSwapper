# Dependency roadmap

| Order | Packet / milestone | Dependency | Exit evidence |
| --- | --- | --- | --- |
| 1 | SWAP-01: bind checkpoints to artifact identity | None | Same-size replacement cannot restore a stale checkpoint; fake-backed tests |
| 1 | SWAP-02: close lifecycle and CI coverage gaps | None, but serialize shared `pipeline/loop.py` edits with SWAP-01 | All success/failure paths stop owned backends; pipeline suite runs in CI |
| 2 | SWAP-03: paired latency experiment for G1.3 | SWAP-01 + SWAP-02; authorized hardware | Immutable run pair, whole-task latency, failures and quality comparison |
| 2 | SWAP-04: T0 certification for G1.5 | Reliable runner + actual 24 GB host | Full-suite memory/timing evidence on the stated host |
| 3 | G3 tier and registry work | Review measured hardware findings | Reproducible configs, model manifests and ADR-backed residency rules |
| 4 | G4 install and external harness integration | Measurement gates and user need | Unaided install and task completion by an external evaluator |

SWAP-01/02 are small code tickets. SWAP-03/04 permit local preparation now, but the measurement portions remain blocked on actual hardware and the existing execution authorization. Do not turn that prerequisite into fabricated estimates. Work beyond these four packets needs a newly bounded specification before delegation.

Keep G1.3 and G1.5 open until their existing numerical bars are measured. Documentation or a passing CPU fake is insufficient. Historical G2 closure is preserved; newly observed limitations must be recorded with evidence, not silently used to rewrite prior measurements.
