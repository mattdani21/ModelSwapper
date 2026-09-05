# Code and review context

## Sources

| Path | Responsibility / observation |
| --- | --- |
| `MASTER-PROMPT.md`, `AGENTS.md` | Goals, four metrics, hardware rules and benchmark ownership |
| `pipeline/contracts.py` | `ModelBackend`, `GenerationResult`, `TaskRunResult` |
| `pipeline/loop.py` | `run_task`, capsule handoff, bounded critic feedback, checkpoint naming |
| `runtime/llama_backend.py`, `runtime/overlap_backend.py`, `runtime/overlap.py` | Process and two-slot backend implementations |
| `capsule/capsule.py`, `capsule/compress.py` | Capsule 0.1.0, atomic persistence and separate compression mechanism |
| `router/rules.py` | Deterministic phase routing; inspect actual use before asserting G1.4 coverage |
| `pipeline/run_pipeline.py` | Runner and persisted summary aggregation |
| `benchmarks/harness/`, `benchmarks/tasks/` | Grader, baseline code and frozen 50-task suite |
| `docs/methodology-standard.md`, `docs/symmetric-baseline.md` | Comparison protocol and historical evidence |
| `hardware/tiers.yaml`, `docs/t0-air-RUN.md` | Hardware configuration and uncompleted T0 measurement |

## Findings from source inspection

1. The pipeline and router contain implementation; the older STATE statement calling them empty stubs is stale.
2. `kv_checkpoint_name` includes a model path and file size, but not a content digest. Two different same-size artifacts at the same path can produce the same checkpoint identity. SWAP-01 specifies a correction without claiming a reproduced inference failure.
3. Nonresident generation has a `finally` cleanup; resident-mode cleanup is after the loop. An unexpected exception from grading or downstream processing can bypass that final stop. SWAP-02 specifies lifecycle coverage.
4. CI runs capsule and grader tests, but omits `pipeline/tests`, despite the broader gate in AGENTS. SWAP-02 closes that coverage gap.
5. Compression is deliberately not wired into the loop; do not treat that design choice as an accidental omission.

## Commands and prerequisites

From repository root, with Python 3.11+, pytest and jsonschema installed:

```bash
python3 -m pytest -q capsule/tests benchmarks/harness/tests pipeline/tests
python3 benchmarks/harness/validate_tasks.py --tasks-dir benchmarks/tasks
python3 pipeline/run_pipeline.py --help
```

Real inference requires llama.cpp and explicitly supplied model artifacts. No GPU/model download or external API run is needed for the first two packets. Follow the existing hardware runbook for real measurements, preserving its complete command, model identity and host details.

## Review evidence

The 50-task structural validation passed in this review environment. After installing isolated CPU test dependencies, the capsule, grader and pipeline suites passed: 37 tests. The command used the isolated dependency directory on PYTHONPATH. No GPU run, new cost benchmark, T0 memory measurement or baseline API call was performed. Existing JSON results were inspected as historical evidence.
