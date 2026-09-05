# Bounded work packets

These are proposed implementation tickets, not claims of completed work. `Ready` means sufficiently specified to begin local work. `Blocked` names an unmet dependency or decision. Historical task ledgers retain completed-task evidence.

## SWAP-01 — Make KV checkpoint identity content-addressed

**Readiness:** Ready. **Depends on:** None. **Parent goal:** G1.3 reliability prerequisite.

**Outcome:** Prevent reuse of a cache derived from different model bytes.

**Read:** `pipeline/loop.py`, `runtime/llama_backend.py`, `pipeline/tests/test_loop.py`.

**Implementation ownership:** `pipeline/loop.py`, `pipeline/run_pipeline.py`, `runtime/llama_backend.py` only as required to pass identity; new ADR under `docs/adr/`.

**Verifier ownership:** New identity fixtures/tests in `pipeline/tests/`.

**Contract:** TECHNICAL_SPEC SWAP-01.

**Acceptance criteria:**

1. **AC1:** Same-size different bytes produce different names; unchanged bytes/prefix in the same compatible namespace produce the same name.
2. **AC2:** Missing identity disables reuse while normal generation remains available.
3. **AC3:** Digest work occurs once per model per run, and existing cache fallback tests still pass.

**Verification:** `python3 -m pytest -q pipeline/tests` then the root quality gate.

**Non-goals:** Cross-model KV reuse, benchmark edits, GPU runs.

**Failure/rollback:** Disable the optional cache or revert naming changes; do not delete historical results.

## SWAP-02 — Guarantee backend cleanup and include pipeline tests in CI

**Readiness:** Ready; serialize after SWAP-01 if both are selected. **Depends on:** None. **Parent goal:** G1.3 / G1.5 reliability prerequisite.

**Outcome:** Ensure failed tasks release backend resources and CI exercises the runtime loop.

**Read:** `pipeline/loop.py`, `pipeline/run_pipeline.py`, `.github/workflows/ci.yml`.

**Implementation ownership:** `pipeline/loop.py`, `pipeline/run_pipeline.py`, `.github/workflows/ci.yml`.

**Verifier ownership:** `pipeline/tests/test_loop.py` and new test fakes there.

**Contract:** TECHNICAL_SPEC SWAP-02.

**Acceptance criteria:**

1. **AC1:** Instrumented fakes observe one owned stop on normal completion, start/generate failure, grading exception and exhausted budget.
2. **AC2:** The original error remains visible if stop also fails; failed work is never marked passed.
3. **AC3:** CI runs capsule, grader and pipeline suites and retains task structural validation.

**Verification:** Full root quality gate; injected failures use no models or providers.

**Non-goals:** Changing task oracles, retry policy or residency architecture.

**Failure/rollback:** Revert the lifecycle patch if ownership regressions appear; preserve failing tests and error evidence.

## SWAP-03 — Prepare and execute a controlled G1.3 comparison

**Readiness:** Preparation ready; measurement blocked on authorized hardware. **Depends on:** SWAP-01, SWAP-02 for the corrected-cache comparison. **Parent goal:** G1.3.

**Outcome:** Determine whether the chosen treatment reduces whole-task latency while preserving quality.

**Read:** `docs/methodology-standard.md`, `docs/symmetric-baseline.md`, `pipeline/run_pipeline.py`.

**Implementation ownership:** New experiment manifest/report in `docs/`; new immutable JSON under `benchmarks/results/`.

**Verifier ownership:** Verifier owns manifest audit, paired analysis and full-gate evidence.

**Contract:** TECHNICAL_SPEC SWAP-03.

**Acceptance criteria:**

1. **AC1:** Manifest fixes task pack, models, runtime and budgets; only the treatment varies.
2. **AC2:** Every task, failed attempt and infrastructure failure appears in the evidence.
3. **AC3:** Report states total-time ratio and quality denominators; G1.3 is closed only if its bar is actually met.

**Verification:** Existing runner command recorded verbatim in the manifest; raw result paths and paired calculations attached after the hardware run.

**Non-goals:** Benchmark mutation, cherry-picking tasks, automatic paid compute.

**Failure/rollback:** Mark an invalid experiment invalid and schedule a corrected run; keep original raw evidence.

## SWAP-04 — Run the T0 memory certification protocol

**Readiness:** Blocked on an authorized 24 GB host; runbook preparation ready. **Depends on:** SWAP-02 before relying on the updated lifecycle. **Parent goal:** G1.5.

**Outcome:** Establish the 24 GB hardware floor using directly measured memory.

**Read:** `docs/t0-air-RUN.md`, `hardware/t0_air_run.sh`, `hardware/tiers.yaml`.

**Implementation ownership:** T0 runbook amendments and new `benchmarks/results/` evidence only.

**Verifier ownership:** Verifier owns host/sampler audit and per-task gate assessment.

**Contract:** TECHNICAL_SPEC SWAP-04.

**Acceptance criteria:**

1. **AC1:** Host capacity and sampling method are recorded; RSS and unified memory are distinguished.
2. **AC2:** All 50 task outcomes and memory peaks are retained.
3. **AC3:** Every task remains below the existing 20 GB ceiling before G1.5 is marked satisfied.

**Verification:** Run the existing T0 command on the named host; attach raw observations and the full report.

**Non-goals:** Hardware purchase, estimated certification, broad tier implementation.

**Failure/rollback:** An unsupported sampler or incomplete run leaves certification blocked; no thresholds are weakened.
