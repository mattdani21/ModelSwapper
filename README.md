# SwapOS / ModelSwapper

A research runtime for local specialist-model pipelines with Context Capsule handoff.

Start with [the execution package](docs/execution/README.md) for reviewed intent,
source context, a dependency roadmap, technical contracts, and bounded developer/test tickets.

Read [AGENTS.md](AGENTS.md) and [MASTER-PROMPT.md](MASTER-PROMPT.md) before code changes.
The [methodology standard](docs/methodology-standard.md) explains benchmark interpretation;
[STATE.md](STATE.md) records progress and outstanding measurements.

## Local verification

With Python 3.11+, pytest and jsonschema installed, from the repository root:

```bash
python3 -m pytest -q capsule/tests benchmarks/harness/tests pipeline/tests
python3 benchmarks/harness/validate_tasks.py --tasks-dir benchmarks/tasks
```

Actual inference requires the appropriate local runtime and model artifacts. Hardware
certification and performance claims require measured evidence on the stated host.
