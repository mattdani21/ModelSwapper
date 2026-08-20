"""Capsule v1 compression stage (G2.4).

Carried context must grow SUB-LINEARLY with task length, capped at a fixed
token budget (default 8k). Strategy:

- Kept verbatim: schema/task identity, goal, constraints, plan head, meta.
- Artifacts: newest artifact kept in full (up to a budget share); older ones
  reduce to path + one-line summary (code is the biggest consumer).
- decisions_log: rolled up per phase into one-line summaries; the last two
  entries stay verbatim (recent feedback matters most).
- phase_history: last 3 entries verbatim + a count summary of older ones.
- If the result still exceeds the budget, oldest artifacts/decisions are
  truncated further — never goal, constraints, or the newest artifact.

Token estimation is the same heuristic the capsule uses (chars // 4); a
pluggable ``summarizer`` hook allows a model-based roll-up later (the REASON
specialist), but the deterministic roll-up is correct on its own.

This module is a pure function of capsule data: no I/O, no model calls.
"""
from __future__ import annotations

import copy
from typing import Any, Callable, Optional

DEFAULT_BUDGET_TOKENS = 8000

# How much of the budget each section may claim before the model-generated
# context is even considered. Sum < 1.0 so the prompt builder always has room.
SECTION_SHARES = {
    "artifacts": 0.45,
    "decisions": 0.15,
    "history": 0.10,
    "plan": 0.10,
    "verbatim": 0.10,  # goal + constraints
    "slack": 0.10,
}

Summarizer = Callable[[list[dict[str, Any]], int], str]


def estimate_tokens(text: str) -> int:
    """Heuristic consistent with capsule.py (chars // 4)."""
    return max(1, len(text) // 4)


def _truncate(text: str, limit_chars: int) -> str:
    if len(text) <= limit_chars:
        return text
    head = text[: max(1, limit_chars - 60)]
    return f"{head}\n...[truncated by Capsule v1 compression]"


def _roll_up_decisions(entries: list[dict[str, Any]], keep_verbatim: int = 2) -> list[dict[str, Any]]:
    """One summary line per phase; the newest `keep_verbatim` entries stay full."""
    if not entries:
        return []
    out: list[dict[str, Any]] = []
    by_phase: dict[str, list[dict[str, Any]]] = {}
    for e in entries:
        by_phase.setdefault(e.get("phase", "?"), []).append(e)
    for phase, group in by_phase.items():
        newest = group[-1]
        summary = {
            "at": newest.get("at", ""),
            "phase": phase,
            "decision": newest.get("decision", ""),
            "rationale": f"{len(group)} entries rolled up; newest: {newest.get('rationale', '')}",
            "rolled_up": True,
        }
        out.append(summary)
    # newest verbatim entries last (so they survive truncation last)
    verbatim = [
        {"at": e.get("at", ""), "phase": e.get("phase", "?"),
         "decision": e.get("decision", ""), "rationale": e.get("rationale", ""),
         "rolled_up": False}
        for e in entries[-keep_verbatim:]
    ]
    return out[:-keep_verbatim] + verbatim if keep_verbatim else out


def compress(
    capsule_data: dict[str, Any],
    budget_tokens: int = DEFAULT_BUDGET_TOKENS,
    summarizer: Optional[Summarizer] = None,
) -> dict[str, Any]:
    """Return a v1-compressed capsule dict (same schema keys, smaller payload).

    Deterministic: same input -> same output. ``summarizer``, when given, is
    called with (decisions_entries, budget_tokens) and its return replaces the
    deterministic decision roll-up.
    """
    d = copy.deepcopy(capsule_data)
    budget_chars = budget_tokens * 4

    # -- verbatim core (never truncated) ----------------------------------
    verbatim_chars = len(d.get("goal", "")) + sum(len(c) for c in d.get("constraints", []))
    art_share = int(budget_chars * SECTION_SHARES["artifacts"])
    dec_share = int(budget_chars * SECTION_SHARES["decisions"])
    hist_share = int(budget_chars * SECTION_SHARES["history"])
    plan_share = int(budget_chars * SECTION_SHARES["plan"])

    # -- plan: keep the head ------------------------------------------------
    plan = d.get("plan", [])
    kept_steps: list[dict[str, Any]] = []
    used = 0
    for step in plan:
        s = str(step.get("step", ""))
        if used + len(s) > plan_share:
            break
        kept_steps.append(step)
        used += len(s)
    d["plan"] = kept_steps

    # -- artifacts: newest full, older reduced -------------------------------
    artifacts = d.get("artifacts", [])
    if artifacts:
        newest = artifacts[-1]
        d["artifacts"] = [
            {
                "path": a.get("path", ""),
                "content": _truncate(a.get("content", ""), art_share // max(1, len(artifacts))),
                "kind": a.get("kind", "code"),
                "compressed": True,
            }
            for a in artifacts[:-1]
        ]
        new_content = newest.get("content", "")
        if len(new_content) > art_share:
            new_content = _truncate(new_content, art_share)
            newest = {**newest, "content": new_content, "compressed": True}
        d["artifacts"].append(newest)

    # -- decisions: roll-up (deterministic) or model summarizer --------------
    decisions = d.get("decisions_log", [])
    if summarizer is not None and decisions:
        try:
            rolled = {"phase": "rollup", "decision": summarizer(decisions, dec_share // 4),
                      "rationale": f"model roll-up of {len(decisions)} entries", "rolled_up": True}
            d["decisions_log"] = [rolled]
        except Exception:  # noqa: BLE001 — summarizer failure must not break the capsule
            d["decisions_log"] = _roll_up_decisions(decisions)
    else:
        d["decisions_log"] = _roll_up_decisions(decisions)
    # enforce section budget on the roll-up (oldest first)
    kept_dec: list[dict[str, Any]] = []
    used = 0
    for entry in reversed(d["decisions_log"]):
        s = str(entry.get("rationale", "")) + str(entry.get("decision", ""))
        if used + len(s) > dec_share and kept_dec:
            break
        kept_dec.append(entry)
        used += len(s)
    d["decisions_log"] = list(reversed(kept_dec))

    # -- phase history: last 3 verbatim + count summary ----------------------
    history = d.get("phase_history", [])
    if len(history) > 3:
        head = history[:-3]
        summary_entry = {
            "phase": "…",
            "model": "",
            "started_at": head[0].get("started_at", ""),
            "finished_at": head[-1].get("finished_at", ""),
            "outcome": f"{len(head)} earlier phases rolled up",
            "swap_in_ms": None,
            "swap_out_ms": None,
            "tokens": sum(h.get("tokens") or 0 for h in head),
            "capsule_bytes": None,
            "capsule_tokens_est": None,
            "compressed": True,
        }
        d["phase_history"] = [summary_entry] + history[-3:]

    # -- final safety: enforce the budget, oldest-first, never the core -------
    while estimate_tokens(__import__("json").dumps(d, sort_keys=True, ensure_ascii=False)) > budget_tokens:
        shrunk = False
        arts = d.get("artifacts", [])
        for a in arts[:-1]:  # oldest artifacts first
            c = a.get("content", "")
            if len(c) > 200:
                a["content"] = c[: len(c) // 2]
                shrunk = True
                break
        if not shrunk and arts:  # last resort: shrink the newest artifact
            a = arts[-1]
            c = a.get("content", "")
            if len(c) > 200:
                a["content"] = c[: len(c) // 2]
                shrunk = True
        if not shrunk:
            for e in reversed(d.get("decisions_log", [])):
                r = e.get("rationale", "")
                if len(r) > 100:
                    e["rationale"] = r[: len(r) // 2]
                    shrunk = True
                    break
        if not shrunk:
            break  # nothing left without touching goal/constraints

    d.setdefault("meta", {})["capsule_version"] = "1.0.0"
    d["meta"]["compressed"] = True
    d["meta"]["budget_tokens"] = budget_tokens
    return d


def growth_ratio(uncompressed_tokens: int, compressed_tokens: int) -> float:
    """Compression ratio — < 1.0 means the stage is doing work."""
    return compressed_tokens / max(1, uncompressed_tokens)
