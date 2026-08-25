"""Symmetric-baseline runner — Step 0 falsification experiment.

docs/roadmap-to-revenue.md Step 0 asks whether the LOCAL pipeline's retry
loop — sacred-grader feedback -> model critic -> retry, max 3 code attempts
(pipeline/loop.py) — is what produces its results. This runner gives the
frontier API model (deepseek-v4-pro via the DeepSeek API) the IDENTICAL loop,
using the SAME model for the CODE and critic phases ("symmetric"), so the
loop's contribution is measured against the single-shot frontier baseline
(benchmarks/harness/run_baseline.py).

Everything here is READ-ONLY reuse of the sacred code:
  * benchmarks/harness/run_baseline.py — build_user_prompt, SYSTEM_PROMPT,
    extract_code and the price constants are IMPORTED, so the prompt shape,
    the extraction regex and the cost math cannot drift from the baseline;
  * benchmarks/harness/grader.py — grade() is IMPORTED (sacred, never
    modified);
  * pipeline/prompts.py — CRITIC_SYSTEM and critic_prompt are IMPORTED
    verbatim, so the critic phase matches the pipeline exactly;
  * pipeline/loop.py — the bounded-feedback convention (feedback[:600]) and
    the "budget exhausted after N code attempts" failure string are mirrored.

NO existing file is modified, moved or deleted by this runner; it only
imports and reads. API calls are the only cloud use and exist solely to
measure the baseline parity denominator (AGENTS.md §4).

Experiment summary: suite 'swapos-v1-symmetric'. If pass rate with the
symmetric retry loop ≈ run_baseline's single-shot pass rate, the retry loop
is not what makes the local pipeline competitive; if it is materially higher,
the loop itself is a first-class contributor and must be kept in the parity
denominator.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Optional

# --- read-only imports of the sacred code -----------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)
sys.path.insert(0, os.path.join(_REPO, "benchmarks", "harness"))  # grader + run_baseline
sys.path.insert(0, _REPO)  # pipeline package
from grader import grade  # noqa: E402  (sacred — read-only use)
from run_baseline import (  # noqa: E402  (sacred — read-only use)
    PRICE_IN_PER_M,
    PRICE_OUT_PER_M,
    SYSTEM_PROMPT,
    build_user_prompt,
    extract_code,
)
from pipeline.prompts import CRITIC_SYSTEM, critic_prompt  # noqa: E402  (verbatim)

DEFAULT_API_BASE = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-pro"
FEEDBACK_BOUND = 600  # bounded-feedback convention from pipeline/loop.py


def call_api(
    api_base: str, api_key: str, model: str, system: str, prompt: str,
    max_tokens: int, temperature: float, timeout: int = 300,
) -> tuple[str, int, int, Optional[int], float]:
    """Same urllib pattern as run_baseline.call_api, system prompt parameterized.

    Returns (content, prompt_tokens, completion_tokens, reasoning_tokens, latency_s).
    reasoning_tokens is None when the provider does not report it separately.
    """
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
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
            return (
                content,
                usage.get("prompt_tokens", 0),
                usage.get("completion_tokens", 0),
                usage.get("reasoning_tokens"),
                dt,
            )
        except (urllib.error.HTTPError, urllib.error.URLError, KeyError) as e:
            last_err = e
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"API call failed after 3 attempts: {last_err}")


def _cost_usd(tokens_in: int, tokens_out: int) -> float:
    """Estimated cost with the SAME constants as run_baseline."""
    return tokens_in / 1e6 * PRICE_IN_PER_M + tokens_out / 1e6 * PRICE_OUT_PER_M


def main() -> None:
    ap = argparse.ArgumentParser(
        description="SwapOS symmetric-baseline runner (Step 0 falsification): "
                    "deepseek-v4-pro gets the pipeline's identical grader->critic->retry loop")
    ap.add_argument("--tasks-dir", default=os.path.join(_HERE, "..", "benchmarks", "tasks"))
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--api-base", default=DEFAULT_API_BASE)
    ap.add_argument("--key", default=os.environ.get("DEEPSEEK_API_KEY", ""))
    ap.add_argument("--out", default="")
    ap.add_argument("--limit", type=int, default=0, help="0 = all tasks")
    ap.add_argument("--max-tokens", type=int, default=8192)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--max-attempts", type=int, default=3)
    ap.add_argument("--cost-cap-usd", type=float, default=2.0,
                    help="hard stop once cumulative estimated cost exceeds this")
    args = ap.parse_args()

    if not args.key:
        sys.exit("ERROR: no API key (set DEEPSEEK_API_KEY or pass --key)")
    if args.max_attempts < 1:
        sys.exit("ERROR: --max-attempts must be >= 1")

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
    tokens_by_phase = {"code_in": 0, "code_out": 0, "critic_in": 0, "critic_out": 0}
    partial = False
    partial_reason = ""
    t0_all = time.monotonic()

    for i, tdir in enumerate(tasks, 1):
        task_id = os.path.basename(tdir)
        category = os.path.basename(os.path.dirname(tdir))
        print(f"[{i}/{len(tasks)}] {task_id} ...", flush=True)
        row = {
            "task_id": task_id,
            "category": category,
            "pass": False,
            "attempts_used": 0,
            "tests_passed": 0,
            "tests_total": 0,
            "tokens_in": 0,
            "tokens_out": 0,
            "error": None,
        }
        try:
            with open(os.path.join(tdir, "problem.md")) as f:
                problem = f.read()
            base_prompt = build_user_prompt(tdir)  # EXACT run_baseline shape
            feedback: Optional[str] = None
            for attempt in range(1, args.max_attempts + 1):
                # Attempt 1 = the baseline prompt. Attempts N>1 = the SAME base
                # prompt plus the bounded critic feedback section, exactly as the
                # pipeline's code_prompt appends it (pipeline/loop.py: feedback[:600]).
                if attempt == 1:
                    prompt = base_prompt
                else:
                    prompt = (
                        base_prompt
                        + "\n\n# Reviewer feedback from the last attempt\n"
                        + (feedback or "")[:FEEDBACK_BOUND]
                        + "\n\nProduce the complete new solution.py (code only)."
                    )
                content, tok_in, tok_out, tok_reason, dt = call_api(
                    args.api_base, args.key, args.model, SYSTEM_PROMPT, prompt,
                    args.max_tokens, args.temperature, args.timeout,
                )
                row["tokens_in"] += tok_in
                row["tokens_out"] += tok_out
                tokens_by_phase["code_in"] += tok_in
                tokens_by_phase["code_out"] += tok_out
                extra = f" reasoning={tok_reason}" if tok_reason is not None else ""
                print(f"    [code attempt {attempt}/{args.max_attempts}] "
                      f"tokens in={tok_in} out={tok_out}{extra} in {dt:.1f}s", flush=True)

                solution = extract_code(content)  # SAME regex as run_baseline
                g = grade(tdir, solution_text=solution, timeout=args.timeout)
                row["attempts_used"] = attempt
                row["tests_passed"] = g["tests_passed"]
                row["tests_total"] = g["tests_total"]
                print(f"    -> {'PASS' if g['pass'] else 'FAIL'} "
                      f"({g['tests_passed']}/{g['tests_total']}) "
                      f"attempt {attempt}/{args.max_attempts} in {dt:.1f}s", flush=True)
                if g["pass"]:
                    row["pass"] = True
                    break
                if g.get("error"):
                    row["error"] = g["error"]
                if attempt >= args.max_attempts:
                    row["error"] = f"budget exhausted after {args.max_attempts} code attempts"
                    print(f"    -> BUDGET EXHAUSTED after {args.max_attempts} code attempts", flush=True)
                    break

                # CRITIC — same model, CRITIC_SYSTEM + critic_prompt verbatim.
                cprompt = critic_prompt(task_id, problem, solution, g.get("output_tail", ""))
                try:
                    ctext, ctok_in, ctok_out, ctok_reason, cdt = call_api(
                        args.api_base, args.key, args.model, CRITIC_SYSTEM, cprompt,
                        args.max_tokens, args.temperature, args.timeout,
                    )
                except Exception as e:  # noqa: BLE001
                    row["error"] = f"critic phase failed: {e}"
                    print(f"    -> CRITIC FAILED: {e}", flush=True)
                    break
                row["tokens_in"] += ctok_in
                row["tokens_out"] += ctok_out
                tokens_by_phase["critic_in"] += ctok_in
                tokens_by_phase["critic_out"] += ctok_out
                extra = f" reasoning={ctok_reason}" if ctok_reason is not None else ""
                print(f"    [critic] tokens in={ctok_in} out={ctok_out}{extra} "
                      f"in {cdt:.1f}s", flush=True)
                feedback = ctext  # bounded to FEEDBACK_BOUND in the next CODE prompt
        except Exception as e:  # noqa: BLE001  — per-task robustness, keep going
            row["error"] = str(e)
            print(f"    -> ERROR {e}", flush=True)
        results.append(row)

        # HARD COST CAP — stop immediately once cumulative estimate exceeds it.
        cumulative = sum(_cost_usd(r["tokens_in"], r["tokens_out"]) for r in results)
        if cumulative > args.cost_cap_usd:
            partial = True
            partial_reason = "cost cap exceeded"
            print(f"COST CAP: estimated ${cumulative:.4f} > ${args.cost_cap_usd:.2f} "
                  f"— stopping, partial results written", flush=True)
            break

    passed = sum(1 for r in results if r["pass"])
    total_in = sum(r["tokens_in"] for r in results)
    total_out = sum(r["tokens_out"] for r in results)
    cost = _cost_usd(total_in, total_out)
    pass_at_1 = sum(1 for r in results if r["pass"] and r["attempts_used"] == 1)
    pass_with_retries = sum(1 for r in results if r["pass"] and r["attempts_used"] > 1)
    attempts_histogram: dict = {}
    for r in results:
        attempts_histogram[r["attempts_used"]] = attempts_histogram.get(r["attempts_used"], 0) + 1
    per_category: dict = {}
    for r in results:
        c = per_category.setdefault(r["category"], {"total": 0, "passed": 0})
        c["total"] += 1
        c["passed"] += 1 if r["pass"] else 0

    summary = {
        "suite": "swapos-v1-symmetric",
        "model": args.model,
        "api_base": args.api_base,
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "wall_clock_s": round(time.monotonic() - t0_all, 1),
        "tasks_total": len(results),
        "tasks_passed": passed,
        "pass_rate": round(passed / len(results), 4),
        "pass_at_1": pass_at_1,
        "pass_with_retries": pass_with_retries,
        "attempts_histogram": attempts_histogram,
        "per_category": per_category,
        "tokens_in": total_in,
        "tokens_out": total_out,
        "tokens_by_phase": tokens_by_phase,
        "cost_estimate_usd": round(cost, 4),
        "price_notes": "PRICE_IN/OUT_PER_M are estimates; raw tokens recorded for recomputation",
        "partial": partial,
        "partial_reason": partial_reason,
        "max_attempts": args.max_attempts,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "results": results,
    }

    out = args.out or os.path.join(
        _HERE, "results",
        f"symmetric-baseline-{time.strftime('%Y%m%d-%H%M%S')}.json",
    )
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nDONE: {passed}/{len(results)} passed ({summary['pass_rate']:.1%})  "
          f"est cost ${cost:.4f}  partial={partial}")
    print(f"results: {out}")


if __name__ == "__main__":
    main()
