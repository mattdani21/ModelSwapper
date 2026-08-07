"""Phase prompt builders + solution extraction (Phase 1, ADR-0004).

The Context Capsule is the ONLY state carried between phases (ADR-0002):
prompts are built from the capsule content + task files, never from raw
conversation transcripts of another model.
"""
from __future__ import annotations

import re
from typing import Optional

REASON_SYSTEM = (
    "You are the REASON phase of a local model-swapping pipeline. You never write code. "
    "Given a coding task brief and the current starter file, produce a concise plan: "
    "numbered steps, the key constraints and edge cases, and how the result will be "
    "verified. Plain text, no markdown fences."
)

CODE_SYSTEM = (
    "You are the CODE phase: a senior Python engineer in a model-swapping pipeline. "
    "Given the task brief, the current starter file, the plan and (on retries) reviewer "
    "feedback, produce the COMPLETE new contents of solution.py. Output ONLY the code — "
    "no explanations, no markdown fences, no diff markers. The file must be runnable as-is."
)

CRITIC_SYSTEM = (
    "You are the REVIEW phase: a meticulous code reviewer. The candidate solution failed "
    "its test suite. Diagnose the failure from the test output and the candidate code: "
    "state the most likely root cause and give concrete, specific fix instructions for "
    "the CODE phase. Do not dump code; the fix belongs to the next CODE run."
)


def reason_prompt(task_id: str, problem: str, starter: str) -> str:
    return (
        f"# Task: {task_id}\n\n{problem}\n\n"
        f"# Current solution.py\n```python\n{starter}\n```\n\n"
        "Plan this implementation."
    )


def code_prompt(
    task_id: str, problem: str, starter: str, plan: str, feedback: Optional[str]
) -> str:
    parts = [
        f"# Task: {task_id}\n\n{problem}\n\n"
        f"# Current solution.py\n```python\n{starter}\n```"
    ]
    if plan:
        parts.append(f"# Plan\n{plan}")
    if feedback is not None:
        hint = feedback or "(none provided — re-examine the task spec and the failing tests)"
        parts.append(f"# Reviewer feedback from the last attempt\n{hint}")
    parts.append("Produce the complete new solution.py (code only).")
    return "\n\n".join(parts)


def critic_prompt(task_id: str, problem: str, candidate: str, test_output_tail: str) -> str:
    return (
        f"# Task: {task_id}\n\n{problem}\n\n"
        f"# Candidate solution.py\n```python\n{candidate}\n```\n\n"
        f"# Test output (tail)\n```\n{test_output_tail}\n```\n\n"
        "Diagnose the failure and give the CODE phase concrete fix instructions."
    )


def parse_plan(text: str) -> list:
    """Very small plan parser: numbered/bulleted lines become capsule plan steps."""
    steps = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        m = re.match(r"^(?:\d+[.)]|[-*])\s+(.*)$", s)
        if m:
            steps.append({"step": m.group(1)[:200], "status": "planned", "notes": ""})
    if not steps:
        steps = [{"step": (text.strip()[:500] or "implement the task"), "status": "planned", "notes": ""}]
    return steps[:20]


def extract_code(text: str) -> str:
    """Best-effort extraction of the solution file from a model response.

    Mirrors the baseline runner's extraction (benchmarks/harness is sacred —
    that copy stays untouched; this is the pipeline-side twin).
    """
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
