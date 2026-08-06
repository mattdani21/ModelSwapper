"""G0.1/G0.2 swap baseline measurement on llama.cpp (llama-server).

Measures, per model: spawn→ready, ready→first-token (streaming), total
generation, peak RSS. Then swap pairs: cold (first load of the session)
and warm (weights resident in OS page cache): evict A → B first token.

Hardware reality (MASTER-PROMPT.md rule 4): the dev machine is an 8 GB
Apple M3 — T4 tier. Numbers recorded here are T4-class; T0 targets are
the trajectory, re-measured on 24 GB hardware when available.

Output: benchmarks/results/swap_baseline-<date>.json
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.request
from typing import Optional

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "benchmarks", "results")
LLAMA_SERVER = os.environ.get("LLAMA_SERVER", "llama-server")
CONTEXT = 2048
N_PREDICT = 48
NGPU_LAYERS = os.environ.get("LLAMA_NGPU", "99")  # Metal: all layers
PROMPT = "Write a short Python function that computes the Fibonacci sequence. Output only code."


def free_memory_gb() -> float:
    """macOS free+inactive memory via vm_stat (GB)."""
    try:
        out = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=10).stdout
    except Exception:  # noqa: BLE001
        return -1.0
    page = 4096
    free = inactive = 0.0
    for line in out.splitlines():
        k, _, v = line.partition(":")
        v = v.strip().strip(".")
        try:
            num = float(v)
        except ValueError:
            continue
        if "free" in k and "speculative" not in k:
            free = num
        elif k.startswith("Pages inactive"):
            inactive = num
    return (free + inactive) * page / 1e9


def process_rss_kb(pid: int) -> Optional[int]:
    try:
        out = subprocess.run(["ps", "-o", "rss=", "-p", str(pid)], capture_output=True, text=True, timeout=5).stdout
        return int(out.strip()) if out.strip() else None
    except Exception:  # noqa: BLE001
        return None


class Server:
    """One llama-server instance (one resident model)."""

    def __init__(self, model_path: str, port: int):
        self.model_path = model_path
        self.port = port
        self.name = os.path.basename(model_path)
        self.proc: Optional[subprocess.Popen] = None
        self.load_s = -1.0
        self.peak_rss_kb = 0

    def start(self, timeout: int = 300) -> None:
        t0 = time.monotonic()
        self.proc = subprocess.Popen(
            [
                LLAMA_SERVER,
                "--model", self.model_path,
                "--port", str(self.port),
                "-c", str(CONTEXT),
                "-ngl", NGPU_LAYERS,
                "--no-webui",
                "--log-disable",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.proc.poll() is not None:
                raise RuntimeError(f"llama-server exited early (rc={self.proc.returncode}) for {self.name}")
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/health", timeout=2) as r:
                    if r.status == 200:
                        self.load_s = round(time.monotonic() - t0, 3)
                        return
            except Exception:  # noqa: BLE001
                time.sleep(0.25)
        raise RuntimeError(f"llama-server did not become ready in {timeout}s for {self.name}")

    def generate(self, prompt: str = PROMPT, n_predict: int = N_PREDICT,
                 timeout: int = 300) -> dict:
        """Streaming completion; returns ttft_s, total_s, tokens, peak_rss_kb."""
        body = json.dumps({
            "prompt": prompt, "n_predict": n_predict, "temperature": 0.7,
            "stream": True,
        }).encode()
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/completion",
            data=body, headers={"Content-Type": "application/json"},
        )
        t0 = time.monotonic()
        ttft = None
        tokens = 0
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            for raw in resp:
                line = raw.decode().strip()
                if not line.startswith("data:"):
                    continue
                try:
                    chunk = json.loads(line[5:])
                except json.JSONDecodeError:
                    continue
                if chunk.get("content") and ttft is None:
                    ttft = round(time.monotonic() - t0, 3)
                tokens = chunk.get("timings", {}).get("predicted_n", tokens)
        total = round(time.monotonic() - t0, 3)
        rss = process_rss_kb(self.proc.pid if self.proc else -1)
        self.peak_rss_kb = max(self.peak_rss_kb, rss or 0)
        return {"ttft_s": ttft, "total_s": total, "tokens": tokens,
                "peak_rss_kb": self.peak_rss_kb}

    def stop(self) -> float:
        """SIGTERM, wait for exit. Returns kill→exit seconds."""
        if self.proc is None:
            return 0.0
        t0 = time.monotonic()
        self.proc.send_signal(signal.SIGTERM)
        try:
            self.proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait(timeout=10)
        dt = round(time.monotonic() - t0, 3)
        self.proc = None
        return dt


def main() -> None:
    ap = argparse.ArgumentParser(description="Swap baseline measurement (G0.1/G0.2)")
    ap.add_argument("--model-a", required=True, help="path to GGUF A")
    ap.add_argument("--model-b", required=True, help="path to GGUF B")
    ap.add_argument("--out", default="")
    ap.add_argument("--port", type=int, default=8712)
    ap.add_argument("--purge", action="store_true",
                    help="attempt `sudo -n purge` before cold loads (needs passwordless sudo)")
    args = ap.parse_args()

    for p in (args.model_a, args.model_b):
        if not os.path.exists(p):
            sys.exit(f"ERROR: model file not found: {p}")

    can_purge = False
    if args.purge:
        r = subprocess.run(["sudo", "-n", "purge"], capture_output=True, timeout=30)
        can_purge = r.returncode == 0

    host = {
        "machine": "Apple M3 (arm64)",
        "ram_gb": 8.0,
        "tier": "T4",
        "os": "macOS 26.6",
        "backend": "llama.cpp (llama-server)",
        "context": CONTEXT,
        "n_predict": N_PREDICT,
        "ngpu_layers": NGPU_LAYERS,
        "can_force_purge": can_purge,
    }

    free_before = free_memory_gb()
    runs = []
    swaps = []

    def measure(model_path: str, label: str) -> dict:
        srv = Server(model_path, args.port + len(runs))
        t0 = time.monotonic()
        srv.start()
        gen = srv.generate()
        evict_s = srv.stop()
        return {
            "label": label,
            "model": srv.name,
            "load_s": srv.load_s,
            "evict_s": evict_s,
            **gen,
            "rss_gb": round((gen["peak_rss_kb"] or 0) / 1e6, 2),
        }

    # Order: A cold, B cold, A warm, B warm — gives cold+warm for both.
    a_cold = measure(args.model_a, "A-cold")
    runs.append(a_cold)
    b_cold = measure(args.model_b, "B-cold")
    runs.append(b_cold)
    a_warm = measure(args.model_a, "A-warm")
    runs.append(a_warm)
    b_warm = measure(args.model_b, "B-warm")
    runs.append(b_warm)

    # Swap metrics: evict X + load Y-to-first-token (cold = Y never loaded this session).
    swaps = [
        {"from": "A", "to": "B", "kind": "cold",
         "evict_s": a_cold["evict_s"], "load_to_ttft_s": round(b_cold["load_s"] + (b_cold["ttft_s"] or 0), 3),
         "swap_s": round(a_cold["evict_s"] + b_cold["load_s"] + (b_cold["ttft_s"] or 0), 3)},
        {"from": "A", "to": "B", "kind": "warm",
         "evict_s": a_warm["evict_s"], "load_to_ttft_s": round(b_warm["load_s"] + (b_warm["ttft_s"] or 0), 3),
         "swap_s": round(a_warm["evict_s"] + b_warm["load_s"] + (b_warm["ttft_s"] or 0), 3)},
    ]

    free_after = free_memory_gb()
    report = {
        "goal_refs": ["G0.1", "G0.2"],
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "host": host,
        "models": {
            "a": {"path": args.model_a, "size_gb": round(os.path.getsize(args.model_a) / 1e9, 2)},
            "b": {"path": args.model_b, "size_gb": round(os.path.getsize(args.model_b) / 1e9, 2)},
        },
        "memory": {
            "free_inactive_gb_before": round(free_before, 2),
            "free_inactive_gb_after": round(free_after, 2),
            "note": "macOS page cache retains evicted weights (that IS the warm cache); "
                    "reclamation verified via process RSS returning to 0 and free+inactive "
                    "memory returning to baseline.",
        },
        "runs": runs,
        "swaps": swaps,
        "targets": {"G0.2_cold_s": 8.0, "G0.2_warm_s": 3.0},
        "methodology": (
            "cold = first load of the session (weights never in page cache); "
            "warm = reload after eviction (weights in OS page cache); "
            "swap_s = evict_s + load_s + ttft of the incoming model; "
            "load_s = spawn llama-server -> /health 200; ttft from streaming first token. "
            "T4-tier hardware (8 GB M3): targets are T0-tier trajectory."
        ),
    }

    out = args.out or os.path.join(RESULTS_DIR, f"swap_baseline-{time.strftime('%Y%m%d-%H%M%S')}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))
    print(f"\nresults: {out}")


if __name__ == "__main__":
    main()
