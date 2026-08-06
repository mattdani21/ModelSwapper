"""Frontier-API baseline runner (G0.4 / MASTER-PROMPT first-actions #4).

Sends each task brief to the frontier API (default: deepseek-v4-pro via
DeepSeek), grades the returned solution with the sacred grader, writes JSON
to benchmarks/results/. API calls are the ONLY permitted cloud use (§4) —
they exist solely to measure the parity denominator.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grader import grade  # noqa: E402

DEFAULT_API_BASE = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-pro"
# Price estimates per 1M tokens (USD). Results carry raw token counts so
# cost can be recomputed when provider pricing is known.
PRICE_IN_PER_M = 0.50
PRICE_OUT_PER_M = 2.00

SYSTEM_PROMPT = (
    "You are a senior software engineer. You will be given a coding task and the "
    "current contents of the file you must modify. Produce ONLY the complete new "
    "contents of that single file — no explanations, no markdown fences, no diff "
    "markers. The file must be runnable as-is."
)


def build_user_prompt(task_dir: str) -> str:
    with open(os.path.join(task_dir, "problem.md")) as f:
        problem = f.read()
    with open(os.path.join(task_dir, "starter", "solution.py")) as f:
        starter = f.read()
    return (
        f"# Task: {os.path.basename(task_dir)}\n\n"
        f"{problem}\n\n"
        f"# Current contents of solution.py\n"
        f"```python\n{starter}\n```\n"
    )


def extract_code(text: str) -> str:
    """Best-effort extraction of the solution file from a model response."""
    fences = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if fences:
        return fences[-1].strip() + "\n"
    if "```" in text:
        idx = text.rfind("```python")
        if idx >= 0:
            return text[idx + len("```python"):].strip() + "\n"
        idx = text.rfind("```")
        if idx >= 0:
            return text[idx + 3:].strip() + "\n"
    return text.strip() + "\n"


def call_api(
    api_base: str, api_key: str, model: str, prompt: str,
    max_tokens: int, temperature: float, timeout: int = 300,
) -> tuple[str, int, int, float]:
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }).encode()
    req = urllib.request.Request(
        f"{api_base}/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
    )
    t0 = time.monotonic()
    last_err: Optional[Exception] = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode())
            dt = time.monotonic() - t0
            usage = data.get("usage", {})
            content = data["choices"][0]["message"]["content"]
            return content, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0), dt
        except (urllib.error.HTTPError, urllib.error.URLError, KeyError) as e:
            last_err = e
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"API call failed after 3 attempts: {last_err}")


def main() -> None:
    ap = argparse.ArgumentParser(description="SwapOS frontier-API baseline (ADR-0003)")
    ap.add_argument("--tasks-dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tasks"))
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--api-base", default=DEFAULT_API_BASE)
    ap.add_argument("--key", default=os.environ.get("DEEPSEEK_API_KEY", ""))
    ap.add_argument("--out", default="")
    ap.add_argument("--limit", type=int, default=0, help="0 = all tasks")
    ap.add_argument("--max-tokens", type=int, default=4096)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--timeout", type=int, default=300)
    args = ap.parse_args()

    if not args.key:
        sys.exit("ERROR: no API key (set DEEPSEEK_API_KEY or pass --key)")

    tasks = []
    for cat in ("bugfix", "feature", "refactor"):
        cat_dir = os.path.join(args.tasks_dir, cat)
        if not os.path.isdir(cat_dir):
            continue
        for name in sorted(os.listdir(cat_dir)):
            tdir = os.path.join(cat_dir, name)
            if os.path.isdir(tdir):
                tasks.append(tdir)
    if args.limit:
        tasks = tasks[: args.limit]
    if not tasks:
        sys.exit("ERROR: no tasks found under --tasks-dir")

    results = []
    t0_all = time.monotonic()
    for i, tdir in enumerate(tasks, 1):
        task_id = os.path.basename(tdir)
        print(f"[{i}/{len(tasks)}] {task_id} ...", flush=True)
        row = {"task_id": task_id, "category": os.path.basename(os.path.dirname(tdir))}
        try:
            prompt = build_user_prompt(tdir)
            content, tok_in, tok_out, latency = call_api(
                args.api_base, args.key, args.model, prompt, args.max_tokens, args.temperature, args.timeout
            )
            solution = extract_code(content)
            g = grade(tdir, solution_text=solution, timeout=args.timeout)
            row.update({
                "pass": g["pass"],
                "tests_passed": g["tests_passed"],
                "tests_total": g["tests_total"],
                "tokens_in": tok_in,
                "tokens_out": tok_out,
                "latency_s": round(latency, 2),
                "grader_latency_s": g["grader_latency_s"],
            })
            if not g["pass"] and g.get("error"):
                row["error"] = g["error"]
            print(f"    -> {'PASS' if g['pass'] else 'FAIL'} ({g['tests_passed']}/{g['tests_total']}) in {latency:.1f}s", flush=True)
        except Exception as e:  # noqa: BLE001
            row["pass"] = False
            row["error"] = str(e)
            print(f"    -> ERROR {e}", flush=True)
        results.append(row)

    passed = sum(1 for r in results if r["pass"])
    total_in = sum(r.get("tokens_in", 0) for r in results)
    total_out = sum(r.get("tokens_out", 0) for r in results)
    mean_latency = sum(r.get("latency_s", 0) for r in results) / max(1, len(results))
    cost = total_in / 1e6 * PRICE_IN_PER_M + total_out / 1e6 * PRICE_OUT_PER_M

    summary = {
        "suite": "swapos-v1",
        "model": args.model,
        "api_base": args.api_base,
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "wall_clock_s": round(time.monotonic() - t0_all, 1),
        "tasks_total": len(results),
        "tasks_passed": passed,
        "pass_rate": round(passed / len(results), 4),
        "mean_latency_s": round(mean_latency, 2),
        "tokens_in": total_in,
        "tokens_out": total_out,
        "cost_estimate_usd": round(cost, 4),
        "price_notes": "PRICE_IN/OUT_PER_M are estimates; raw tokens recorded for recomputation",
        "system_prompt": SYSTEM_PROMPT,
        "prompt_template": "problem.md + starter/solution.py embedded in markdown; model returns full file",
        "results": results,
    }

    out = args.out or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "results",
        f"baseline-{args.model}-{time.strftime('%Y%m%d-%H%M%S')}.json",
    )
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nDONE: {passed}/{len(results)} passed ({summary['pass_rate']:.1%})  "
          f"mean {mean_latency:.1f}s/task  est cost ${cost:.4f}")
    print(f"results: {out}")


if __name__ == "__main__":
    main()
