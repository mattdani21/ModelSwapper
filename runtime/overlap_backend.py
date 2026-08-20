"""OverlapBackend — ModelBackend adapter over the two-slot PrefetchEngine (G2.2).

One engine is shared by every role of a task; each OverlapBackend binds the
engine to one specialist path. generate():

  1. swap(model) — promote the prefetched standby, or sequential fallback
  2. prefetch(next_model) — non-blocking; the NEXT specialist's load overlaps
     this generation (the swap the pipeline pays for next phase is hidden)
  3. stream the completion against the active server

load_s in the result = what THIS phase actually paid: 0.0 on a promoted swap
(the load happened during the previous phase's generation), the real load
on a fallback. evict_s = the eviction the promotion forced.
"""
from __future__ import annotations

import json
import time
import urllib.request
from typing import Optional

from pipeline.contracts import GenerationResult, ModelBackend
from runtime.overlap import PrefetchEngine


class OverlapBackend(ModelBackend):
    def __init__(self, engine: PrefetchEngine, model_path: str):
        self.engine = engine
        self.model_path = model_path

    def start(self) -> None:
        pass  # the engine owns the servers

    def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.2,
        prefetch_model: Optional[str] = None,
    ) -> GenerationResult:
        swap_stats = self.engine.swap(self.model_path, 0)
        srv = self.engine.active()
        if srv is None:
            raise RuntimeError(f"overlap engine has no active server after swap for {self.model_path}")
        if prefetch_model:
            self.engine.prefetch(prefetch_model)

        body = json.dumps({
            "prompt": prompt,
            "n_predict": max_tokens,
            "temperature": temperature,
            "stream": True,
            "enable_thinking": False,
        }).encode()
        req = urllib.request.Request(
            f"http://127.0.0.1:{srv.port}/completion",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        t0 = time.monotonic()
        ttft = None
        tokens = 0
        chunks: list[str] = []
        with urllib.request.urlopen(req, timeout=900) as resp:
            for raw in resp:
                line = raw.decode().strip()
                if not line.startswith("data:"):
                    continue
                try:
                    chunk = json.loads(line[5:])
                except json.JSONDecodeError:
                    continue
                if chunk.get("content"):
                    if ttft is None:
                        ttft = round(time.monotonic() - t0, 3)
                    chunks.append(chunk["content"])
                tokens = chunk.get("timings", {}).get("predicted_n", tokens)
        return GenerationResult(
            text="".join(chunks),
            tokens=tokens,
            ttft_s=ttft,
            total_s=round(time.monotonic() - t0, 3),
            load_s=0.0 if swap_stats.get("promoted") else swap_stats.get("load_s"),
            evict_s=swap_stats.get("evict_s", 0.0),
        )

    def stop(self) -> float:
        return 0.0  # the engine stops once per task (run_pipeline), not per phase
