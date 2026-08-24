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
    def __init__(self, model_path: str, port: int,
                 kv_cache_dir: Optional[str] = None):
        self.model_path = model_path
        self.port = port
        self.kv_cache_dir = kv_cache_dir
        self._server: Optional[Server] = None

    def configure_kv_cache(self, kv_cache_dir: str) -> None:
        """Enable cross-turn KV prefix caching (G1.3, issue #16).

        Checkpoint files (llama-server slot save/restore) live under
        kv_cache_dir; servers are started with --slot-save-path so the
        POST /slots/0?action=save|restore endpoints are available.
        """
        self.kv_cache_dir = kv_cache_dir

    def _kv_call(self, action: str, filename: str, timeout: int = 60) -> dict:
        """POST /slots/0?action=<save|restore> with {"filename": ...}.

        Returns the parsed response on success, or raises RuntimeError.
        """
        if self._server is None:
            raise RuntimeError("backend not started")
        body = json.dumps({"filename": filename}).encode()
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/slots/0?action={action}",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except Exception as e:  # noqa: BLE001
            raise RuntimeError(f"slot {action} failed for {filename!r}: {e}") from e

    def start(self) -> None:
        self._server = Server(self.model_path, self.port,
                              slot_save_path=self.kv_cache_dir)
        self._server.start()

    def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.2,
        prefetch_model: Optional[str] = None,
        kv_restore: Optional[str] = None,
        kv_save: Optional[str] = None,
    ) -> GenerationResult:
        if self._server is None:
            raise RuntimeError("backend not started")
        kv_used = False
        if kv_restore is not None:
            try:
                self._kv_call("restore", kv_restore)
                kv_used = True
            except Exception as e:  # noqa: BLE001
                # correctness first: full prefill on any restore failure
                print(f"    [kv] restore fallback (full prefill): {e}", flush=True)
        body = json.dumps({
            "prompt": prompt,
            "n_predict": max_tokens,
            "temperature": temperature,
            "stream": True,
            # Qwen3 chat templates think by default; the pipeline wants direct
            # answers (thinking tokens are pure overhead at our speeds and they
            # blew the plan/code budgets on the first Kaggle run). Non-Qwen3
            # templates ignore this field.
            "enable_thinking": False,
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
        timings: dict = {}
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
                if chunk.get("timings"):
                    timings = chunk["timings"]
                tokens = chunk.get("timings", {}).get("predicted_n", tokens)
        kv_saved = False
        if kv_save is not None:
            try:
                self._kv_call("save", kv_save)
                kv_saved = True
            except Exception as e:  # noqa: BLE001
                # a failed save only costs the next retry its fast path
                print(f"    [kv] save failed (next retry falls back): {e}", flush=True)
        # point-sample RSS after generation (Server's own sampler only runs in
        # swap_runner's CLI path) — good enough for the G2.3 memory arm
        from runtime.swap_runner import process_rss_kb as _rss
        pid = self._server.proc.pid if self._server.proc else None
        rss = _rss(pid) if pid else None
        if rss:
            self._server.peak_rss_kb = max(self._server.peak_rss_kb, rss)
        return GenerationResult(
            text="".join(chunks),
            tokens=tokens,
            ttft_s=ttft,
            total_s=round(time.monotonic() - t0, 3),
            load_s=self._server.load_s,
            peak_rss_kb=self._server.peak_rss_kb,
            prompt_n=timings.get("prompt_n"),
            prompt_ms=timings.get("prompt_ms"),
            kv_used=kv_used,
            kv_saved=kv_saved,
        )

    def stop(self) -> float:
        if self._server is None:
            return 0.0
        dt = self._server.stop()
        self._server = None
        return dt
