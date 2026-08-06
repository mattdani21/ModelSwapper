# benchmarks/ — SACRED (MASTER-PROMPT.md §4, ADR-0003)

Parity + latency harness. **Nothing in here is ever modified to make results pass. It only gets harder or broader.**

- `tasks/` — the 50-task suite (bugfix/feature/refactor) + `_EXAMPLE/`. Authoring spec: `tasks/README.md`.
- `harness/` — grader (the single grading contract), baseline runner, task validator.
- `results/` — every run as JSON, committed. A run without a results file did not happen.

Commands:

```bash
python3 benchmarks/harness/validate_tasks.py --tasks-dir benchmarks/tasks          # structural (CI)
python3 benchmarks/harness/validate_tasks.py --full --tasks-dir benchmarks/tasks   # RED/GREEN gate
DEEPSEEK_API_KEY=... python3 benchmarks/harness/run_baseline.py --model deepseek-v4-pro
```
