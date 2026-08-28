"""Symmetric baseline runner (roadmap Step 0 — the falsification experiment).

Gives the frontier API the IDENTICAL loop the pipeline gets:
  REASON (plan) -> CODE (solution) -> sacred grader -> on failure CRITIC
  (test-output feedback) -> retry, up to max_iterations=3.

Design rules (symmetry):
- Prompt builders: pipeline/prompts.py verbatim (reason_prompt, code_prompt,
  critic_prompt) — the same composed text the pipeline's models receive.
  The pipeline sends raw completion prompts (its role SYSTEM constants are
  unreferenced); the API arm therefore sends the composed prompt as the
  single user message, no extra system framing.
- Feedback bound: the pipeline passes feedback[:600] into the code prompt
  (loop.py bounded_feedback); same here.
- Grader: the sacred grader, unchanged.
- Budget: max_tokens 8192 (the baseline's setting — deepseek-v4-pro counts
  reasoning_content toward the budget, unlike the pipeline's
  enable_thinking=False 2048-token budget). Recorded in meta.
- Temperature 0.2 (baseline + pipeline operating point).

SACRED files are untouched; this is a NEW runner (the baseline runner and
grader are never modified). Results: benchmarks/results/symmetric-baseline-<date>.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_baseline import (  # noqa: E402  (sacred — read-only import)
    DEFAULT_API_BASE,
    DEFAULT_MODEL,
    PRICE_IN_PER_M,
    PRICE_OUT_PER_M,
    call_api,
    extract_code,
)
from grader import grade  # noqa: E402  (sacred — read-only use)
from pipeline.prompts import code_prompt, critic_prompt, reason_prompt  # noqa: E402


def collect_tasks(tasks_dir: str) -> list:
    tasks = []
    for cat in ("bugfix", "feature", "refactor"):
        cat_dir = os.path.join(tasks_dir, cat)
        if not os.path.isdir(cat_dir):
            continue
        for name in sorted(os.listdir(cat_dir)):
            tdir = os.path.join(cat_dir, name)
            if os.path.isdir(tdir):
                tasks.append(tdir)
    return tasks


def run_one(
    task_dir: str,
    api_base: str, api_key: str, model: str,
    max_tokens: int, temperature: float, max_iterations: int, timeout: int,
) -> dict:
    task_id = os.path.basename(task_dir)
    category = os.path.basename(os.path.dirname(task_dir))
    with open(os.path.join(task_dir, "problem.md")) as f:
        problem = f.read()
    with open(os.path.join(task_dir, "starter", "solution.py")) as f:
        starter = f.read()

    phases: list = []
    plan = ""
    feedback: Optional[str] = None
    passed = False
    tests_passed = tests_total = 0
    error = None

    for iteration in range(max_iterations):
        if iteration == 0:  # REASON — once per task
            content, ti, to, lat = call_api(
                api_base, api_key, model,
                reason_prompt(task_id, problem, starter),
                max_tokens, temperature, timeout,
            )
            plan = content
            phases.append({"role": "reason", "tokens_in": ti, "tokens_out": to, "latency_s": round(lat, 2)})

        # CODE
        bounded_feedback = feedback[:600] if feedback is not None else None
        content, ti, to, lat = call_api(
            api_base, api_key, model,
            code_prompt(task_id, problem, starter, plan, bounded_feedback),
            max_tokens, temperature, timeout,
        )
        candidate = extract_code(content)
        phases.append({"role": "code", "tokens_in": ti, "tokens_out": to, "latency_s": round(lat, 2)})

        # REVIEW — mechanical (the sacred grader)
        g = grade(task_dir, solution_text=candidate, timeout=timeout)
        tests_passed, tests_total = g["tests_passed"], g["tests_total"]
        if g["pass"]:
            passed = True
            break

        if iteration + 1 >= max_iterations:
            error = f"budget exhausted after {max_iterations} code attempts"
            break

        # CRITIC — diagnose and feed the next CODE attempt
        content2, ti2, to2, lat2 = call_api(
            api_base, api_key, model,
            critic_prompt(task_id, problem, candidate, g["output_tail"]),
            max_tokens, temperature, timeout,
        )
        feedback = content2
        phases.append({"role": "critic", "tokens_in": ti2, "tokens_out": to2, "latency_s": round(lat2, 2)})

    return {
        "task_id": task_id,
        "category": category,
        "passed": passed,
        "iterations": len([p for p in phases if p["role"] == "code"]),
        "tests_passed": tests_passed,
        "tests_total": tests_total,
        "phases": phases,
        "error": error,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Symmetric baseline: frontier API with the pipeline's loop (roadmap Step 0)")
    ap.add_argument("--tasks-dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tasks"))
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--api-base", default=DEFAULT_API_BASE)
    ap.add_argument("--key", default=os.environ.get("DEEPSEEK_API_KEY", ""))
    ap.add_argument("--out", default="")
    ap.add_argument("--limit", type=int, default=0, help="0 = all tasks")
    ap.add_argument("--max-tokens", type=int, default=8192,
                    help="output budget incl. reasoning_content (baseline setting; v4-pro is a reasoning model)")
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--max-iterations", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=300)
    args = ap.parse_args()

    if not args.key:
        sys.exit("ERROR: no API key (set DEEPSEEK_API_KEY or pass --key)")

    tasks = collect_tasks(args.tasks_dir)
    if args.limit:
        tasks = tasks[: args.limit]
    if not tasks:
        sys.exit("ERROR: no tasks found")

    results = []
    t0_all = time.monotonic()
    for i, tdir in enumerate(tasks, 1):
        task_id = os.path.basename(tdir)
        print(f"[{i}/{len(tasks)}] {task_id} ...", flush=True)
        try:
            row = run_one(tdir, args.api_base, args.key, args.model,
                          args.max_tokens, args.temperature, args.max_iterations, args.timeout)
        except Exception as e:  # noqa: BLE001
            row = {"task_id": task_id, "category": os.path.basename(os.path.dirname(tdir)),
                   "passed": False, "iterations": 0, "tests_passed": 0, "tests_total": 0,
                   "phases": [], "error": str(e)}
        results.append(row)
        print(f"    -> {'PASS' if row['passed'] else 'FAIL'} ({row['tests_passed']}/{row['tests_total']}) "
              f"iterations={row['iterations']}", flush=True)
        # checkpoint after every task (killed runs keep completed tasks)
        with open(_out_path(args), "w") as f:
            json.dump(_summary(args, results, time.monotonic() - t0_all), f, indent=2)

    summary = _summary(args, results, time.monotonic() - t0_all)
    with open(_out_path(args), "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nDONE: {summary['tasks_passed']}/{summary['tasks_total']} passed "
          f"({summary['pass_rate']:.1%})  pass@1: {summary['pass_at_1']}/"
          f"{summary['tasks_total']}  est cost ${summary['cost_estimate_usd']:.4f}")
    print(f"results: {_out_path(args)}")


def _out_path(args) -> str:
    return args.out or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "results",
        f"symmetric-baseline-{args.model}-{time.strftime('%Y%m%d-%H%M%S')}.json",
    )


def _summary(args, results: list, wall_s: float) -> dict:
    passed = sum(1 for r in results if r["passed"])
    pass1 = sum(1 for r in results if r["passed"] and r["iterations"] == 1)
    total_in = sum(p["tokens_in"] for r in results for p in r["phases"])
    total_out = sum(p["tokens_out"] for r in results for p in r["phases"])
    latencies = [p["latency_s"] for r in results for p in r["phases"] if p.get("latency_s")]
    by_cat: dict = {}
    for r in results:
        c = by_cat.setdefault(r["category"], {"passed": 0, "total": 0})
        c["total"] += 1
        if r["passed"]:
            c["passed"] += 1
    return {
        "goal_refs": ["roadmap Step 0 — symmetric baseline (falsification experiment)"],
        "suite": "swapos-v1",
        "model": args.model,
        "api_base": args.api_base,
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "wall_clock_s": round(wall_s, 1),
        "tasks_total": len(results),
        "tasks_passed": passed,
        "pass_rate": round(passed / len(results), 4),
        "pass_at_1": pass1,
        "per_category": by_cat,
        "mean_phase_latency_s": round(sum(latencies) / len(latencies), 2) if latencies else None,
        "tokens_in": total_in,
        "tokens_out": total_out,
        "cost_estimate_usd": round(total_in / 1e6 * PRICE_IN_PER_M + total_out / 1e6 * PRICE_OUT_PER_M, 4),
        "price_notes": "same PRICE_IN/OUT_PER_M estimates as run_baseline.py; raw tokens recorded",
        "config": {
            "max_tokens": args.max_tokens,
            "temperature": args.temperature,
            "max_iterations": args.max_iterations,
            "prompts": "pipeline/prompts.py builders verbatim (single user message, no system framing — matches the pipeline's raw completion prompts)",
            "feedback_bound_chars": 600,
            "grader": "sacred benchmarks/harness/grader.py",
        },
        "results": results,
    }


if __name__ == "__main__":
    main()
