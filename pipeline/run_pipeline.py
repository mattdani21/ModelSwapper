"""CLI: run the reason->code->review pipeline over benchmark tasks (Phase 1).

Usage:
  python3 pipeline/run_pipeline.py \
      --models-json '{"reason":"models/A.gguf","code":"models/B.gguf","review":"models/A.gguf"}' \
      [--limit N] [--out PATH] [--max-iterations 3] [--port-base 8900]

Checkpointing: after every task the full results are rewritten to --out, so a
killed/timed-out run still yields its completed tasks. Results land in
benchmarks/results/pipeline-<date>.json by default.

Swap semantics: each phase starts its specialist fresh and evicts it after
generation (start/stop per phase) — swap timings are recorded per phase and
are part of the results (G1.3).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.contracts import TaskRunResult  # noqa: E402
from pipeline.loop import run_task  # noqa: E402
from runtime.llama_backend import LlamaBackend  # noqa: E402

CATEGORIES = ("bugfix", "feature", "refactor")


def collect_tasks(tasks_dir: str, categories: tuple) -> list:
    tasks = []
    for cat in categories:
        cat_dir = os.path.join(tasks_dir, cat)
        if not os.path.isdir(cat_dir):
            continue
        for name in sorted(os.listdir(cat_dir)):
            tdir = os.path.join(cat_dir, name)
            if os.path.isdir(tdir):
                tasks.append(tdir)
    return tasks


def result_to_dict(r: TaskRunResult) -> dict:
    return {
        "task_id": r.task_id,
        "category": r.category,
        "passed": r.passed,
        "iterations": r.iterations,
        "tests_passed": r.tests_passed,
        "tests_total": r.tests_total,
        "phases": r.phases,
        "capsule_bytes": r.capsule_bytes,
        "wall_clock_s": r.wall_clock_s,
        "error": r.error,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="SwapOS pipeline eval (G1.1-G1.3)")
    ap.add_argument("--tasks-dir", default="benchmarks/tasks")
    ap.add_argument("--models-json", required=True,
                    help='{"reason": path, "code": path, "review": path}')
    ap.add_argument("--out", default="")
    ap.add_argument("--limit", type=int, default=0, help="0 = all tasks")
    ap.add_argument("--max-iterations", type=int, default=3)
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--port-base", type=int, default=8900)
    ap.add_argument("--capsule-dir", default="", help="write per-task Context Capsules here")
    ap.add_argument("--categories", default="bugfix,feature,refactor")
    ap.add_argument("--handoff", choices=["capsule", "naive"], default="capsule",
                    help="capsule = structured handoff (Phase 1); naive = full verbatim transcript (G2.3 ablation)")
    ap.add_argument("--resident", action="store_true",
                    help="one model (reason) serves every phase, no swaps — single-model ablation arm")
    ap.add_argument("--backend", choices=["llama", "overlap"], default="llama",
                    help="llama = per-phase start/stop (Phase 1); overlap = two-slot prefetch engine (G2.2)")
    args = ap.parse_args()

    models = json.loads(args.models_json)
    for role in ("reason", "code", "review"):
        if role not in models:
            sys.exit(f"ERROR: --models-json missing role {role!r}")
        if not os.path.exists(models[role]):
            sys.exit(f"ERROR: model file not found: {models[role]}")

    tasks = collect_tasks(args.tasks_dir, tuple(args.categories.split(",")))
    if args.limit:
        tasks = tasks[: args.limit]
    if not tasks:
        sys.exit("ERROR: no tasks found")

    out = args.out or os.path.join(
        "benchmarks", "results", f"pipeline-{time.strftime('%Y%m%d-%H%M%S')}.json"
    )
    os.makedirs(os.path.dirname(out), exist_ok=True)

    run_meta = {
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "models": models,
        "max_iterations": args.max_iterations,
        "max_tokens": args.max_tokens,
        "temperature": args.temperature,
        "tasks_total": len(tasks),
        "mode": "swap-per-phase (each phase loads its specialist fresh, evicts after)",
        "handoff": args.handoff,
        "resident": args.resident,
        "backend": args.backend,
    }

    results = []
    t0_all = time.monotonic()
    for i, tdir in enumerate(tasks, 1):
        task_id = os.path.basename(tdir)
        print(f"[{i}/{len(tasks)}] {task_id} ...", flush=True)
        engine = None
        try:
            if args.backend == "overlap":
                from runtime.overlap import PrefetchEngine
                from runtime.overlap_backend import OverlapBackend
                ceiling = float(os.environ.get("OVERLAP_CEILING_GB", "20.0"))
                task_engine = PrefetchEngine(ceiling_gb=ceiling,
                                             port_base=args.port_base + i * 50)
                engine = task_engine
                memo: dict = {}

                def factory(model_path: str, port: int):
                    if model_path not in memo:
                        memo[model_path] = OverlapBackend(task_engine, model_path)
                    return memo[model_path]
            else:
                factory = LlamaBackend
            r = run_task(
                tdir,
                models,
                factory,
                max_iterations=args.max_iterations,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
                port_base=args.port_base,
                capsule_dir=args.capsule_dir or None,
                handoff=args.handoff,
                resident=args.resident,
            )
        except Exception as e:  # noqa: BLE001
            print(f"    -> ERROR {e}", flush=True)
            r = TaskRunResult(
                task_id=task_id,
                category=os.path.basename(os.path.dirname(tdir)),
                passed=False,
                iterations=0,
                tests_passed=0,
                tests_total=0,
                error=str(e),
            )
        finally:
            if engine is not None:
                engine.stop()
        results.append(result_to_dict(r))
        print(f"    -> {'PASS' if r.passed else 'FAIL'} ({r.tests_passed}/{r.tests_total}) "
              f"in {r.wall_clock_s}s, {len(r.phases)} phases, {r.iterations} iterations", flush=True)
        # checkpoint
        summary = build_summary(run_meta, results, time.monotonic() - t0_all)
        with open(out, "w") as f:
            json.dump(summary, f, indent=2)

    summary = build_summary(run_meta, results, time.monotonic() - t0_all)
    with open(out, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nDONE: {summary['tasks_passed']}/{summary['tasks_total']} passed "
          f"({summary['pass_rate']:.1%})  wall {summary['wall_clock_s']}s")
    print(f"results: {out}")


def build_summary(run_meta: dict, results: list, wall_s: float) -> dict:
    passed = sum(1 for r in results if r["passed"])
    by_cat: dict = {}
    for r in results:
        c = by_cat.setdefault(r["category"], {"passed": 0, "total": 0})
        c["total"] += 1
        if r["passed"]:
            c["passed"] += 1
    loads = [p["load_s"] for r in results for p in r["phases"] if p.get("load_s") is not None]
    evicts = [p["evict_s"] for r in results for p in r["phases"] if p.get("evict_s") is not None]
    ttfts = [p["ttft_s"] for r in results for p in r["phases"] if p.get("ttft_s") is not None]
    mean_wall = sum(r["wall_clock_s"] for r in results) / max(1, len(results))
    return {
        **run_meta,
        "results": results,
        "tasks_passed": passed,
        "pass_rate": round(passed / len(results), 4),
        "per_category": by_cat,
        "mean_wall_clock_s": round(mean_wall, 2),
        "wall_clock_s": round(wall_s, 1),
        "mean_load_s": round(sum(loads) / len(loads), 3) if loads else None,
        "mean_evict_s": round(sum(evicts) / len(evicts), 3) if evicts else None,
        "mean_ttft_s": round(sum(ttfts) / len(ttfts), 3) if ttfts else None,
    }


if __name__ == "__main__":
    main()
