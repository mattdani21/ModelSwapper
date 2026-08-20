"""G2.3 — Context-preservation ablation: capsule vs naive vs single-model.

Runs the SAME task list through three arms:
  capsule — Context Capsule handoff (Phase 1 semantics)
  naive   — full verbatim transcript handoff (no structure, no roll-up)
  single  — one model resident for all phases, no swaps at all

The sacred suite and grader are untouched — this runner only orchestrates
the pipeline with different handoff modes. Numbers per arm: pass rate,
mean wall-clock, mean context tokens carried between phases, mean peak RSS.

Usage:
  python3 benchmarks/harness/run_ablation.py \
      --models-json '{"reason": "models/X.gguf", "code": "models/Y.gguf", "review": "models/Z.gguf"}' \
      [--limit 6] [--arms capsule,naive,single] [--out ...]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pipeline.contracts import TaskRunResult  # noqa: E402
from pipeline.loop import run_task  # noqa: E402
from pipeline.run_pipeline import collect_tasks, result_to_dict  # noqa: E402
from runtime.llama_backend import LlamaBackend  # noqa: E402

ARMS = ("capsule", "naive", "single")


def _arm_config(arm: str) -> dict:
    if arm == "capsule":
        return {"handoff": "capsule", "resident": False}
    if arm == "naive":
        return {"handoff": "naive", "resident": False}
    if arm == "single":
        return {"handoff": "capsule", "resident": True}  # resident = no swaps
    raise ValueError(arm)


def run_arm(arm: str, tasks: list, models: dict, port_base: int,
            max_iterations: int, max_tokens: int, temperature: float,
            capsule_dir: str) -> dict:
    cfg = _arm_config(arm)
    results: list[dict] = []
    for i, tdir in enumerate(tasks, 1):
        task_id = os.path.basename(tdir)
        print(f"  [{arm}] [{i}/{len(tasks)}] {task_id} ...", flush=True)
        try:
            r: TaskRunResult = run_task(
                tdir, models, LlamaBackend,
                max_iterations=max_iterations, max_tokens=max_tokens,
                temperature=temperature, port_base=port_base,
                capsule_dir=capsule_dir or None,
                **cfg,
            )
        except Exception as e:  # noqa: BLE001
            print(f"    -> ERROR {e}", flush=True)
            r = TaskRunResult(task_id=task_id, category=os.path.basename(os.path.dirname(tdir)),
                              passed=False, iterations=0, tests_passed=0, tests_total=0,
                              error=str(e))
        results.append(result_to_dict(r))
        print(f"    -> {'PASS' if r.passed else 'FAIL'} ({r.tests_passed}/{r.tests_total}) "
              f"in {r.wall_clock_s}s, {len(r.phases)} phases", flush=True)
        port_base += 1
    return summarize_arm(arm, results)


def summarize_arm(arm: str, results: list[dict]) -> dict:
    passed = sum(1 for r in results if r["passed"])
    walls = [r["wall_clock_s"] for r in results if r["wall_clock_s"]]
    ctxs = [p.get("context_tokens_est") for r in results for p in r["phases"]
            if p.get("context_tokens_est")]
    rss = [p.get("peak_rss_kb") for r in results for p in r["phases"]
           if p.get("peak_rss_kb")]
    return {
        "arm": arm,
        "tasks_total": len(results),
        "tasks_passed": passed,
        "pass_rate": round(passed / max(1, len(results)), 4),
        "mean_wall_clock_s": round(sum(walls) / len(walls), 2) if walls else None,
        "mean_context_tokens_est": round(sum(ctxs) / len(ctxs)) if ctxs else None,
        "mean_peak_rss_kb": round(sum(rss) / len(rss)) if rss else None,
        "results": results,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="G2.3 ablation: capsule vs naive vs single-model")
    ap.add_argument("--tasks-dir", default="benchmarks/tasks")
    ap.add_argument("--models-json", required=True)
    ap.add_argument("--limit", type=int, default=6, help="tasks per arm (0 = all)")
    ap.add_argument("--arms", default="capsule,naive,single")
    ap.add_argument("--out", default="")
    ap.add_argument("--port-base", type=int, default=8950)
    ap.add_argument("--max-iterations", type=int, default=3)
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--capsule-dir", default="", help="per-task capsules (arm capsule)")
    args = ap.parse_args()

    models = json.loads(args.models_json)
    for role in ("reason", "code", "review"):
        if role not in models or not os.path.exists(models[role]):
            sys.exit(f"ERROR: --models-json missing/invalid role {role!r}")

    tasks = collect_tasks(args.tasks_dir, ("bugfix", "feature", "refactor"))
    if args.limit:
        tasks = tasks[: args.limit]
    if not tasks:
        sys.exit("ERROR: no tasks found")

    report = {
        "goal_refs": ["G2.3"],
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "host": {"machine": "Apple M3 (arm64)", "ram_gb": 8.0, "tier": "T4",
                 "os": "macOS 26.6"},
        "models": models,
        "max_iterations": args.max_iterations,
        "max_tokens": args.max_tokens,
        "temperature": args.temperature,
        "arms": {},
        "verdict": None,
    }
    for arm in args.arms.split(","):
        arm = arm.strip()
        if arm not in ARMS:
            sys.exit(f"ERROR: unknown arm {arm!r} (use {','.join(ARMS)})")
        report["arms"][arm] = run_arm(arm, tasks, models, args.port_base,
                                      args.max_iterations, args.max_tokens,
                                      args.temperature, args.capsule_dir)

    # verdict: capsule >= naive on quality AND strictly better on memory
    a = report["arms"]
    if "capsule" in a and "naive" in a:
        cap, naive = a["capsule"], a["naive"]
        quality_ok = cap["pass_rate"] >= naive["pass_rate"]
        mem_cap = cap["mean_context_tokens_est"] or 0
        mem_naive = naive["mean_context_tokens_est"] or 0
        mem_ok = mem_cap < mem_naive
        report["verdict"] = {
            "capsule_ge_naive_quality": quality_ok,
            "capsule_strictly_better_memory": mem_ok,
            "pass_capsule": cap["pass_rate"], "pass_naive": naive["pass_rate"],
            "ctx_capsule": mem_cap, "ctx_naive": mem_naive,
        }

    out = args.out or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "results",
        f"ablation-{time.strftime('%Y%m%d-%H%M%S')}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(report, f, indent=2)

    print("\n=== ABLATION SUMMARY ===")
    for arm, s in report["arms"].items():
        print(f"  {arm:8s} pass {s['tasks_passed']}/{s['tasks_total']} "
              f"({s['pass_rate']:.1%})  wall {s['mean_wall_clock_s']}s  "
              f"ctx {s['mean_context_tokens_est']} tok  rss {s['mean_peak_rss_kb']} KB")
    if report["verdict"]:
        print("  verdict:", json.dumps(report["verdict"]))
    print(f"results: {out}")


if __name__ == "__main__":
    main()
