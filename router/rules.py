"""Deterministic v1 router (ADR-0004, G1.4).

Transitions are rules, not model calls: correct by construction (100%, the
G1.4 bar). A model-based router arrives with predictive pre-fetch in Phase 2
(G2.2) — until then the loop's control flow IS the router.
"""
from __future__ import annotations

PHASE_ORDER = ("reason", "code", "review")


class DeterministicRouter:
    def __init__(self, max_iterations: int = 3):
        self.max_iterations = max_iterations

    def initial_phase(self) -> str:
        return "reason"

    def next_phase(self, current: str, review_passed: bool, iteration: int) -> str:
        """iteration = number of code attempts so far (1-based on first code run)."""
        if current == "reason":
            return "code"
        if current == "code":
            return "review"
        if current == "review":
            if review_passed or iteration >= self.max_iterations:
                return "done"
            return "code"
        return "done"

    def model_for(self, phase: str, models: dict) -> str:
        role = {"reason": "reason", "code": "code", "review": "review", "critic": "review"}[phase]
        return models[role]
