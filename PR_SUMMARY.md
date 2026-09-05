# Agent execution documentation — G1.3 / G1.5

Existing plans and status notes do not consistently match the implemented repository. Agents need a reliable source map and bounded contracts before taking implementation tickets.

This documentation change adds intent, a dependency roadmap, reviewed context/findings, technical specifications and developer/test work packets under `docs/execution/`. It adds two repository-scoped skills and links the package from root instructions. Historical evidence and existing domain constraints are preserved; stale status statements are qualified with a dated review checkpoint.

The work packets identify implementation ownership, independent verification, input/output/error behavior, acceptance criteria, dependencies and rollback. Readiness is separate from future implementation completion. This PR does not implement the proposed application fixes or claim that their acceptance tests already pass.

Validation: 37 capsule/grader/pipeline tests passed with isolated CPU dependencies; 50 benchmark tasks passed structural validation. No hardware or API baseline run.

All 12 repository-scoped skills across this six-repository review passed the skill validator. New documentation links and bounded packet structure were checked locally. No merge, deployment, training, external send or customer-data operation is included.

Goal references: G1.3 and G1.5. Four-number impact: this user-requested documentation prepares quality, latency and hardware-floor measurements; it records no new numerical improvement. It preserves the frozen task/grader/baseline boundaries.
