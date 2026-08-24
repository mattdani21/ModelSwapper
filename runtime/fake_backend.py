"""Scripted backend for pipeline loop tests (never used in real runs)."""
from __future__ import annotations

from typing import Callable, Optional

from pipeline.contracts import GenerationResult, ModelBackend


class FakeBackend(ModelBackend):
    """Returns scripted texts (a queue, or a callable(prompt) -> str). Records calls."""

    def __init__(
        self,
        model_path: str,
        responses: Optional[list] = None,
        callable_resp: Optional[Callable[[str], str]] = None,
    ):
        self.model_path = model_path
        self.responses = list(responses or [])
        self.callable_resp = callable_resp
        self.calls: list[str] = []
        self.prefetches: list = []
        self.kv_ops: list = []
        self.fail_restore = False
        self.loads = 0
        self.stops = 0

    def start(self) -> None:
        self.loads += 1

    def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.2,
        prefetch_model: Optional[str] = None,
        kv_restore: Optional[str] = None,
        kv_save: Optional[str] = None,
    ) -> GenerationResult:
        self.calls.append(prompt)
        self.prefetches.append(prefetch_model)
        if kv_restore is not None:
            self.kv_ops.append(("restore", kv_restore))
        if kv_save is not None:
            self.kv_ops.append(("save", kv_save))
        if self.callable_resp is not None:
            text = self.callable_resp(prompt)
        elif self.responses:
            text = self.responses.pop(0)
        else:
            text = ""
        kv_used = kv_restore is not None and not self.fail_restore
        return GenerationResult(
            text=text,
            tokens=max(1, len(text) // 3),
            ttft_s=0.01,
            total_s=0.05,
            load_s=0.1,
            evict_s=0.05,
            prompt_n=128 if kv_used else 300,
            prompt_ms=50.0 if kv_used else 300.0,
            kv_used=kv_used,
            kv_saved=kv_save is not None,
        )

    def stop(self) -> float:
        self.stops += 1
        return 0.05
