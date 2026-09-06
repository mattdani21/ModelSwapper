"""Reason -> code -> review loop with Context Capsule handoff (Phase 1, ADR-0004).

Swap semantics: every phase transition loads its specialist fresh and evicts
it afterwards (start/stop per phase) — the measured swap is real, and the
capsule is the only thing carried across. REVIEW is two-stage: mechanical
(the sacred grader runs the candidate's tests) then, on failure, a model
critic that feeds the next CODE attempt.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import uuid
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
    out: Optional[GenerationResult] = None
    completed = False
    try:
        backend.start()
        out = backend.generate(prompt, max_tokens=max_tokens, temperature=temperature)
        completed = True
        return out
    finally:
        # SWAP-02: the phase owns this backend — exactly ONE stop() attempt
        # even when start() or generate() raised, and a stop() failure must
        # never mask the failure it accompanies.
        try:
            evict_s = backend.stop()
        except BaseException as cleanup_error:  # noqa: BLE001
            if completed:
                raise  # no prior failure in flight: the cleanup failure IS the error
            # else: a start/generate failure is propagating — keep it primary
        else:
            if out is not None:
                out.evict_s = evict_s


# KV checkpoint identity format version (SWAP-01, ADR-0006). Bump when the
# identity payload's field set or canonicalization changes meaning.
IDENTITY_FORMAT_VERSION = 1


def file_sha256(path: str) -> Optional[str]:
    """Full SHA-256 of a file's bytes (lowercase hex), read in a stream.

    Returns None — never a fabricated digest — when the artifact is missing
    or unreadable, so callers can disable checkpointing for it instead of
    silently hashing nothing.
    """
    digest = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                digest.update(chunk)
    except OSError:
        return None
    return digest.hexdigest()


def kv_checkpoint_name(model_sha256: Optional[str], task_id: str, problem: str,
                       starter: str, plan: str) -> Optional[str]:
    """Content-addressed slot-checkpoint filename (SWAP-01, ADR-0006).

    Identity is SHA-256 over a canonical, sorted JSON object containing
    identity format version 1, the full model artifact SHA-256, the task ID
    and the exact problem, starter and plan text, serialized with
    sort_keys=True and compact separators, explicitly UTF-8 encoded. The
    ENTIRE digest is used: ``kv-<64 hex>.bin``. Identity follows artifact
    CONTENT: two same-size artifacts with different bytes at the same path
    produce different names, and identical bytes at a different path produce
    the same name.

    Returns None when no model digest is available (missing/unreadable
    artifact): the caller must disable checkpoint restore/save for that
    model and run a normal generation — an empty or all-zero digest is never
    substituted for real content.
    """
    if not model_sha256:
        return None
    identity = json.dumps(
        {
            "identity_format_version": IDENTITY_FORMAT_VERSION,
            "model_sha256": model_sha256,
            "task_id": task_id,
            "problem": problem,
            "starter": starter,
            "plan": plan,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return f"kv-{digest}.bin"


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
        "prompt_n": out.prompt_n if out else None,
        "prompt_ms": out.prompt_ms if out else None,
        "kv_used": out.kv_used if out else False,
        "kv_saved": out.kv_saved if out else False,
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
    kv_cache_dir: Optional[str] = None,
    model_sha256s: Optional[dict] = None,
) -> TaskRunResult:
    """Run the reason->code->review loop for one task.

    handoff='capsule' (default): the Context Capsule is the only state carried
        between phases (Phase 1 semantics, ADR-0002).
    handoff='naive': prior phase outputs are carried as a FULL VERBATIM
        transcript in every prompt (the G2.3 ablation comparator).
    resident=True: one backend (models['reason']) serves every phase with no
        swaps at all — the single-model baseline arm of the G2.3 ablation.
    kv_cache_dir (G1.3, issue #16): cross-turn KV prefix cache for the CODE
        phase. After the first code attempt the slot state (task + starter +
        plan prefix, byte-identical across retries) is checkpointed to disk
        via llama-server's slot save API; every retry restores that checkpoint
        so only the feedback suffix is re-prefilled (FreeToken-style). Any
        restore failure falls back to a full prefill (correctness first).
        SWAP-01 (ADR-0006): the checkpoint name is content-addressed and the
        directory is a run-private namespace (see below).
    model_sha256s (SWAP-01): optional precomputed content digests per model
        role (e.g. {"code": "<64 hex>"}), hashed ONCE per run by the caller
        (run_pipeline hashes each artifact once per CLI run). When a role is
        absent the digest is computed here exactly once per run_task call —
        never rehashed per retry. A None digest (unreadable artifact)
        disables checkpointing for that model.
    """
    if handoff not in ("capsule", "naive"):
        raise ValueError(f"handoff must be 'capsule' or 'naive', got {handoff!r}")
    # SWAP-01 (ADR-0006): run-private cache namespace + once-per-run digest.
    # Runtime/build identity and context settings are NOT yet part of the
    # checkpoint identity, so each run_task call saves/restores under a fresh
    # private subdirectory: unknown runtime metadata can never cause reuse of
    # a checkpoint from another run. Retries within THIS call share the
    # namespace, which is what makes the cross-turn cache useful.
    code_model_sha256: Optional[str] = None
    if kv_cache_dir:
        kv_cache_dir = os.path.join(kv_cache_dir, f"run-{uuid.uuid4().hex[:12]}")
        os.makedirs(kv_cache_dir, exist_ok=True)
        # Model artifact digest: hashed ONCE per run per model — either
        # precomputed by the caller or computed here exactly once — then
        # reused by every retry (never rehash gigabytes per retry). A None
        # digest (missing/unreadable artifact) disables checkpointing for
        # that model; no empty/all-zero digest is substituted.
        if model_sha256s is not None and "code" in model_sha256s:
            code_model_sha256 = model_sha256s["code"]
        else:
            code_model_sha256 = file_sha256(models["code"])
    task_id = os.path.basename(task_dir)
    category = os.path.basename(os.path.dirname(task_dir))
    with open(os.path.join(task_dir, "problem.md"), encoding="utf-8") as f:
        problem = f.read()
    with open(os.path.join(task_dir, "starter", "solution.py"), encoding="utf-8") as f:
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
        port_counter[0] += 1

    def _generate(
        model: str, prompt: str, max_tokens: int, temperature: float, port: int,
        prefetch_model: Optional[str] = None,
        kv_restore: Optional[str] = None,
        kv_save: Optional[str] = None,
    ) -> GenerationResult:
        if resident_backend is not None:
            out = resident_backend.generate(
                prompt, max_tokens=max_tokens, temperature=temperature,
                prefetch_model=prefetch_model,
                kv_restore=kv_restore, kv_save=kv_save,
            )
            out.evict_s = 0.0
            return out
        backend = backend_factory(model, port)
        if kv_cache_dir and hasattr(backend, "configure_kv_cache"):
            backend.configure_kv_cache(kv_cache_dir)  # type: ignore[attr-defined]
        out: Optional[GenerationResult] = None
        completed = False
        try:
            backend.start()
            out = backend.generate(
                prompt, max_tokens=max_tokens, temperature=temperature,
                prefetch_model=prefetch_model,
                kv_restore=kv_restore, kv_save=kv_save,
            )
            completed = True
            return out
        finally:
            # SWAP-02: the phase owns this backend — exactly ONE stop()
            # attempt even when start() or generate() raised, and a stop()
            # failure must never mask the failure it accompanies (the
            # caller records the phase-named error from the original).
            try:
                evict_s = backend.stop()
            except BaseException as cleanup_error:  # noqa: BLE001
                if completed:
                    raise  # no prior failure in flight: the cleanup failure IS the error
                # else: a start/generate failure is propagating — keep it primary
            else:
                if out is not None:
                    out.evict_s = evict_s

    def _context_tokens_est() -> int:
        if handoff == "naive":
            return max(1, len(transcript) // 4)
        return max(1, capsule.bytes() // 4)

    result = {"passed": False, "tests_passed": 0, "tests_total": 0, "error": None}
    iteration = 0
    lifecycle_completed = False
    try:
        # SWAP-02: the resident backend is owned by the ENTIRE task lifecycle
        # below. Exactly one stop() attempt happens no matter how the task ends
        # - resident start failure, a phase failure, a grader exception,
        # budget exhaustion or a normal pass - and a stop() failure never
        # masks the task's own outcome (it is appended to the recorded error
        # when one exists; a propagating lifecycle failure stays primary).
        if resident_backend is not None:
            resident_backend.start()
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
                # G1.3 (issue #16): checkpoint after the FIRST code attempt and
                # restore on retries — the task+starter+plan prefix is byte-
                # identical across retries, only feedback changes, so the retry
                # only re-prefills the feedback suffix (FreeToken-style). SWAP-01
                # (ADR-0006): the name is content-addressed from the immutable
                # model digest (hashed once per run) + task/plan text; a None
                # digest (unreadable artifact) disables restore/save entirely.
                ckpt_name = None
                if code_model_sha256 is not None:
                    ckpt_name = kv_checkpoint_name(
                        code_model_sha256, task_id, problem, starter, plan)
                out = _generate(
                    models["code"],
                    code_prompt(task_id, problem, starter, plan, bounded_feedback,
                                transcript=transcript if handoff == "naive" else None),
                    max_tokens, temperature, port_counter[0],
                    prefetch_model=models["review"],  # G2.2: load the critic while CODE writes
                    kv_restore=ckpt_name if bounded_feedback is not None else None,
                    kv_save=ckpt_name if bounded_feedback is None else None,
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

        lifecycle_completed = True
    finally:
        if resident_backend is not None:
            try:
                resident_backend.stop()
            except BaseException as cleanup_error:  # noqa: BLE001
                if lifecycle_completed and not result["passed"] and result["error"] is not None:
                    # keep the phase-named failure as the primary error (SWAP-02)
                    result["error"] = f"{result['error']} (resident backend cleanup failed: {cleanup_error})"
                elif lifecycle_completed:
                    raise  # no earlier failure in flight: the cleanup failure IS the error
                # else: a lifecycle failure is propagating - keep it primary

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
