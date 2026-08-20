"""Reason -> code -> review loop with Context Capsule handoff (Phase 1, ADR-0004).

Swap semantics: every phase transition loads its specialist fresh and evicts
it afterwards (start/stop per phase) — the measured swap is real, and the
capsule is the only thing carried across. REVIEW is two-stage: mechanical
(the sacred grader runs the candidate's tests) then, on failure, a model
critic that feeds the next CODE attempt.
"""
from __future__ import annotations

import os
import sys
import time
from typing import Callable, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmarks.harness.grader import grade  # noqa: E402  (sacred — read-only use)
from capsule.capsule import Capsule  # noqa: E402
from router.rules import DeterministicRouter  # noqa: E402

from .contracts import GenerationResult, ModelBackend, TaskRunResult  # noqa: E402
from .prompts import (  # noqa: E402
    code_prompt,
    critic_prompt,
    extract_code,
    parse_plan,
    reason_prompt,
)


def _generate(
    backend_factory: Callable[[str, int], ModelBackend],
    model: str,
    prompt: str,
    max_tokens: int,
    temperature: float,
    port: int,
) -> GenerationResult:
    backend = backend_factory(model, port)
    backend.start()
    try:
        out = backend.generate(prompt, max_tokens=max_tokens, temperature=temperature)
    finally:
        out.evict_s = backend.stop()
    return out


def _log_phase(
    capsule: Capsule,
    phases: list,
    role: str,
    model: str,
    out: Optional[GenerationResult],
    outcome: str,
    extra: Optional[dict] = None,
) -> None:
    entry = {
        "role": role,
        "model": model,
        "outcome": outcome,
        "tokens": out.tokens if out else 0,
        "load_s": out.load_s if out else None,
        "evict_s": out.evict_s if out else None,
        "ttft_s": out.ttft_s if out else None,
        "total_s": out.total_s if out else None,
        "peak_rss_kb": out.peak_rss_kb if out else None,
    }
    if extra:
        entry.update(extra)
    phases.append(entry)
    capsule.complete_phase(
        role,
        model,
        outcome=outcome,
        swap_in_ms=round(out.load_s * 1000, 1) if out and out.load_s else None,
        swap_out_ms=round(out.evict_s * 1000, 1) if out and out.evict_s else None,
        tokens=out.tokens if out else 0,
    )


def run_task(
    task_dir: str,
    models: dict,
    backend_factory: Callable[[str, int], ModelBackend],
    max_iterations: int = 3,
    max_tokens: int = 2048,
    temperature: float = 0.2,
    port_base: int = 8900,
    capsule_dir: Optional[str] = None,
    handoff: str = "capsule",
    resident: bool = False,
) -> TaskRunResult:
    """Run the reason->code->review loop for one task.

    handoff='capsule' (default): the Context Capsule is the only state carried
        between phases (Phase 1 semantics, ADR-0002).
    handoff='naive': prior phase outputs are carried as a FULL VERBATIM
        transcript in every prompt (the G2.3 ablation comparator).
    resident=True: one backend (models['reason']) serves every phase with no
        swaps at all — the single-model baseline arm of the G2.3 ablation.
    """
    if handoff not in ("capsule", "naive"):
        raise ValueError(f"handoff must be 'capsule' or 'naive', got {handoff!r}")
    task_id = os.path.basename(task_dir)
    category = os.path.basename(os.path.dirname(task_dir))
    with open(os.path.join(task_dir, "problem.md")) as f:
        problem = f.read()
    with open(os.path.join(task_dir, "starter", "solution.py")) as f:
        starter = f.read()

    capsule = Capsule.new(task_id=task_id, goal=problem[:2000])
    router = DeterministicRouter(max_iterations=max_iterations)
    phases: list = []
    plan = ""
    feedback: Optional[str] = None
    transcript = ""  # naive handoff accumulator (verbatim, no roll-up)
    t0 = time.monotonic()
    port_counter = [port_base]

    resident_backend: Optional[ModelBackend] = None
    if resident:
        resident_backend = backend_factory(models["reason"], port_counter[0])
        resident_backend.start()
        port_counter[0] += 1

    def _generate(
        model: str, prompt: str, max_tokens: int, temperature: float, port: int,
        prefetch_model: Optional[str] = None,
    ) -> GenerationResult:
        if resident_backend is not None:
            out = resident_backend.generate(
                prompt, max_tokens=max_tokens, temperature=temperature,
                prefetch_model=prefetch_model,
            )
            out.evict_s = 0.0
            return out
        backend = backend_factory(model, port)
        out: Optional[GenerationResult] = None
        try:
            backend.start()
            out = backend.generate(
                prompt, max_tokens=max_tokens, temperature=temperature,
                prefetch_model=prefetch_model,
            )
            return out
        finally:
            evict_s = backend.stop()
            if out is not None:
                out.evict_s = evict_s

    def _context_tokens_est() -> int:
        if handoff == "naive":
            return max(1, len(transcript) // 4)
        return max(1, capsule.bytes() // 4)

    result = {"passed": False, "tests_passed": 0, "tests_total": 0, "error": None}
    iteration = 0
    while iteration < max_iterations:
        # REASON — once per task (iteration 0)
        if iteration == 0:
            try:
                out = _generate(
                    models["reason"], reason_prompt(task_id, problem, starter),
                    max_tokens, temperature, port_counter[0],
                    prefetch_model=models["code"],  # G2.2: load CODE while REASON plans
                )
            except Exception as e:  # noqa: BLE001
                result["error"] = f"reason phase failed: {e}"
                break
            plan = out.text
            capsule.set_plan(parse_plan(plan))
            if handoff == "naive":
                transcript += f"\n[REASON PLAN]\n{plan}\n"
            _log_phase(capsule, phases, "reason", models["reason"], out, "ok",
                       extra={"context_tokens_est": _context_tokens_est()})
            port_counter[0] += 1

        # CODE
        try:
            # feedback is bounded (600 chars) in BOTH the capsule decision and
            # the prompt — an unbounded critic output can overflow the context
            # on retries (observed: HTTP 400 at 4096 ctx with a 2048-token
            # critic response). The capsule's own convention is 600.
            bounded_feedback = feedback[:600] if feedback is not None else None
            out = _generate(
                models["code"],
                code_prompt(task_id, problem, starter, plan, bounded_feedback,
                            transcript=transcript if handoff == "naive" else None),
                max_tokens, temperature, port_counter[0],
                prefetch_model=models["review"],  # G2.2: load the critic while CODE writes
            )
        except Exception as e:  # noqa: BLE001
            result["error"] = f"code phase failed: {e}"
            break
        candidate = extract_code(out.text)
        capsule.add_artifact("solution.py", candidate, kind="code")
        if handoff == "naive":
            transcript += f"\n[CODE ATTEMPT]\n{candidate}\n"
        _log_phase(capsule, phases, "code", models["code"], out, "ok",
                   extra={"context_tokens_est": _context_tokens_est()})
        port_counter[0] += 1

        # REVIEW (mechanical — the sacred grader)
        g = grade(task_dir, solution_text=candidate)
        passed = bool(g["pass"])
        result["tests_passed"] = g["tests_passed"]
        result["tests_total"] = g["tests_total"]
        _log_phase(
            capsule, phases, "review", "grader", None,
            "ok" if passed else "retry",
            extra={"tests_passed": g["tests_passed"], "tests_total": g["tests_total"],
                   "context_tokens_est": _context_tokens_est()},
        )
        if passed:
            result["passed"] = True
            break

        # budget exhausted -> fail
        if iteration + 1 >= max_iterations:
            result["error"] = f"budget exhausted after {max_iterations} code attempts"
            break

        # CRITIC (model) -> feedback for the next CODE attempt
        try:
            out2 = _generate(
                models["review"],
                critic_prompt(task_id, problem, candidate, g["output_tail"],
                              transcript=transcript if handoff == "naive" else None),
                max_tokens, temperature, port_counter[0],
                prefetch_model=models["code"],  # G2.2: load CODE while the critic reviews
            )
        except Exception as e:  # noqa: BLE001
            result["error"] = f"critic phase failed: {e}"
            break
        feedback = out2.text
        capsule.add_decision("review", "retry", feedback[:600])
        if handoff == "naive":
            transcript += f"\n[CRITIC FEEDBACK]\n{feedback}\n"
        _log_phase(capsule, phases, "critic", models["review"], out2, "ok",
                   extra={"context_tokens_est": _context_tokens_est()})
        port_counter[0] += 1
        iteration += 1

    if resident_backend is not None:
        resident_backend.stop()

    if capsule_dir:
        os.makedirs(capsule_dir, exist_ok=True)
        capsule.save(os.path.join(capsule_dir, f"{task_id}.json"))

    return TaskRunResult(
        task_id=task_id,
        category=category,
        passed=result["passed"],
        iterations=iteration + (1 if result["passed"] or iteration > 0 else 0),
        tests_passed=result["tests_passed"],
        tests_total=result["tests_total"],
        phases=phases,
        capsule_bytes=capsule.bytes(),
        wall_clock_s=round(time.monotonic() - t0, 2),
        error=result["error"],
    )
