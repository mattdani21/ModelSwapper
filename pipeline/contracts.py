"""Pipeline contracts (Phase 1, ADR-0004)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

ROLES = ("reason", "code", "review")


@dataclass
class GenerationResult:
    text: str
    tokens: int = 0
    ttft_s: Optional[float] = None
    total_s: float = 0.0
    load_s: Optional[float] = None
    evict_s: Optional[float] = None


class ModelBackend(ABC):
    """One model behind one llama-server process (swap semantics per phase)."""

    model_path: str

    @abstractmethod
    def start(self) -> None:
        """Load weights; load_s recorded internally."""

    @abstractmethod
    def generate(
        self, prompt: str, max_tokens: int = 2048, temperature: float = 0.2
    ) -> GenerationResult:
        """Streaming generation with timings."""

    @abstractmethod
    def stop(self) -> float:
        """Evict (kill the server); return eviction seconds."""


@dataclass
class TaskRunResult:
    task_id: str
    category: str
    passed: bool
    iterations: int
    tests_passed: int
    tests_total: int
    phases: list = field(default_factory=list)
    capsule_bytes: int = 0
    wall_clock_s: float = 0.0
    error: Optional[str] = None
