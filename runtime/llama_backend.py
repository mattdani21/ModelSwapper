"""Llama.cpp llama-server backend for the pipeline (Phase 1, ADR-0004).

Reuses runtime/swap_runner.Server for process lifecycle + RSS accounting,
and adds a parameterized streaming generate (temperature / max_tokens).
Same HTTP protocol works on Metal (Mac) and CUDA (Kaggle) builds.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime.swap_runner import Server  # noqa: E402

from pipeline.contracts import GenerationResult, ModelBackend  # noqa: E402


class LlamaBackend(ModelBackend):
    def __init__(self, model_path: str, port: int):
        self.model_path = model_path
        self.port = port
        self._server: Optional[Server] = None

    def start(self) -> None:
        self._server = Server(self.model_path, self.port)
        self._server.start()

    def generate(
        self, prompt: str, max_tokens: int = 2048, temperature: float = 0.2
    ) -> GenerationResult:
        if self._server is None:
            raise RuntimeError("backend not started")
        body = json.dumps({
            "prompt": prompt,
            "n_predict": max_tokens,
            "temperature": temperature,
            "stream": True,
        }).encode()
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/completion",
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
            load_s=self._server.load_s,
        )

    def stop(self) -> float:
        if self._server is None:
            return 0.0
        dt = self._server.stop()
        self._server = None
        return dt
