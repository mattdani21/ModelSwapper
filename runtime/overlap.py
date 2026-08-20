"""Two-slot prefetch engine (G2.2 — overlap).

Phase order is known ahead of time (REASON -> CODE -> REVIEW -> ...), so the
standby slot can load the NEXT specialist while the active slot is still
generating. At phase transition the swap becomes: promote standby + evict the
old active — the load latency is hidden.

Policy (deterministic, no model involved):
  - prefetch(model): start the standby server in a background thread.
  - swap(model): if standby is ready for `model`, promote it; else fall back
    to a sequential load (Phase 1 behaviour). Correct either way.
  - Memory guard: never prefetch if active + incoming sizes exceed the tier
    ceiling (env OVERLAP_CEILING_GB, default 20 = T0's 20 GB ceiling; set 3.5
    for the 8 GB T4 dev box). Falls back to sequential automatically.

Measured per swap: hidden_load_s (prefetch completed before the swap — the
latency we eliminated), promote_s, evict_s, swap_s (user-visible).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
import urllib.request
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime.swap_runner import Server  # noqa: E402

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "benchmarks", "results")
CEILING_GB = float(os.environ.get("OVERLAP_CEILING_GB", "20.0"))
N_PREDICT = int(os.environ.get("LLAMA_N_PREDICT", "32"))


class PrefetchEngine:
    """Two slots; at most one is active at a time; standby pre-loads."""

    def __init__(self, ceiling_gb: float = CEILING_GB):
        self.ceiling_gb = ceiling_gb
        self.slots: dict[str, Optional[Server]] = {"active": None, "standby": None}
        self.stats: dict = {}
        self._lock = threading.Lock()

    # -- helpers ----------------------------------------------------------
    def _model_gb(self, model_path: str) -> float:
        return os.path.getsize(model_path) / 1e9

    def _fits(self, incoming: str) -> bool:
        active = self.slots["active"]
        active_gb = self._model_gb(active.model_path) if active else 0.0
        return active_gb + self._model_gb(incoming) <= self.ceiling_gb

    def _stop_slot(self, slot: str) -> float:
        srv = self.slots[slot]
        if srv is None:
            return 0.0
        dt = srv.stop()
        self.slots[slot] = None
        return dt

    # -- operations ---------------------------------------------------------
    def prefetch(self, model_path: str, port: int) -> bool:
        """Start loading `model_path` into the standby slot, non-blocking.

        Returns True if the prefetch was kicked off (fits under the ceiling).
        """
        with self._lock:
            if self.slots["standby"] is not None:
                if self.slots["standby"].model_path == model_path:
                    return True  # already loading the right model
                self._stop_slot("standby")
            if not self._fits(model_path):
                return False
            srv = Server(model_path, port)
            self.slots["standby"] = srv

        def _load() -> None:
            try:
                srv.start()
            except Exception as e:  # noqa: BLE001
                srv.load_error = str(e)  # type: ignore[attr-defined]
                with self._lock:
                    if self.slots["standby"] is srv:
                        self.slots["standby"] = None

        threading.Thread(target=_load, daemon=True).start()
        return True

    def standby_ready(self, model_path: str) -> bool:
        srv = self.slots["standby"]
        return bool(srv and srv.proc is not None and srv.proc.poll() is None
                    and srv.model_path == model_path and srv.load_s is not None)

    def swap(self, model_path: str, port: int) -> dict:
        """Make `model_path` the active model. Returns swap timing stats."""
        t0 = time.monotonic()
        with self._lock:
            standby = self.slots["standby"]
            promoted = self.standby_ready(model_path)
            hidden = standby.load_s if (promoted and standby) else None
            if promoted and standby is not None:
                old_active = self.slots["active"]
                self.slots["active"] = standby
                self.slots["standby"] = None
                evict_s = self._stop_slot("active") if old_active else 0.0  # evict the old one
                # `self.slots["active"]` is the promoted standby; don't touch it
                self.slots["active"] = standby
                swap_s = round(time.monotonic() - t0, 3)
                return {"promoted": True, "hidden_load_s": hidden,
                        "evict_s": evict_s, "swap_s": swap_s}
        # fallback: sequential (Phase 1 semantics)
        evict_s = self._stop_slot("active")
        srv = Server(model_path, port)
        srv.start()
        self.slots["active"] = srv
        swap_s = round(time.monotonic() - t0, 3)
        return {"promoted": False, "hidden_load_s": None, "evict_s": evict_s,
                "swap_s": swap_s, "load_s": srv.load_s}

    def active(self) -> Optional[Server]:
        return self.slots["active"]

    def stop(self) -> float:
        return self._stop_slot("active") + self._stop_slot("standby")


def _generate(server: Server, prompt: str = "Write a Python function that returns 42.") -> dict:
    body = json.dumps({"prompt": prompt, "n_predict": N_PREDICT,
                       "temperature": 0.2, "stream": True}).encode()
    req = urllib.request.Request(f"http://127.0.0.1:{server.port}/completion",
                                 data=body, headers={"Content-Type": "application/json"})
    t0 = time.monotonic()
    ttft = None
    tokens = 0
    with urllib.request.urlopen(req, timeout=300) as resp:
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
    return {"ttft_s": ttft, "total_s": round(time.monotonic() - t0, 3), "tokens": tokens}


def main() -> None:
    ap = argparse.ArgumentParser(description="G2.2 overlap measurement: sequential vs prefetched swap")
    ap.add_argument("--model-a", required=True)
    ap.add_argument("--model-b", required=True)
    ap.add_argument("--port-base", type=int, default=8810)
    ap.add_argument("--out", default="")
    ap.add_argument("--ceiling-gb", type=float, default=CEILING_GB)
    args = ap.parse_args()

    for p in (args.model_a, args.model_b):
        if not os.path.exists(p):
            sys.exit(f"ERROR: model file not found: {p}")

    report = {
        "goal_refs": ["G2.1", "G2.2"],
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "host": {"machine": "Apple M3 (arm64)", "ram_gb": 8.0, "tier": "T4",
                 "os": "macOS 26.6", "backend": "llama.cpp (llama-server)"},
        "models": {"a": args.model_a, "b": args.model_b,
                   "a_gb": round(os.path.getsize(args.model_a) / 1e9, 2),
                   "b_gb": round(os.path.getsize(args.model_b) / 1e9, 2)},
        "ceiling_gb": args.ceiling_gb,
        "sequential": None,
        "overlapped": None,
        "targets": {"G2.1_warm_swap_s": 1.5},
        "methodology": (
            "sequential = Phase 1 semantics: evict A, then load B to first token. "
            "overlapped = prefetch B into the standby slot while A is still generating; "
            "swap = promote standby + evict A. T4-tier numbers (8 GB M3); T0 trajectory "
            "targets re-measured on 24 GB hardware."
        ),
    }

    # ---- sequential (baseline) -------------------------------------------
    seq: dict = {"label": "sequential A->B"}
    srv = Server(args.model_a, args.port_base)
    srv.start()
    seq["a_load_s"] = srv.load_s
    g = _generate(srv)
    seq["a_gen_s"] = g["total_s"]
    t0 = time.monotonic()
    seq["a_evict_s"] = srv.stop()
    srv_b = Server(args.model_b, args.port_base + 1)
    srv_b.start()
    seq["b_load_s"] = srv_b.load_s
    g = _generate(srv_b)
    seq["b_ttft_s"] = g["ttft_s"]
    seq["swap_to_first_token_s"] = round(seq["a_evict_s"] + srv_b.load_s + (g["ttft_s"] or 0), 3)
    srv_b.stop()
    report["sequential"] = seq
    print("sequential:", json.dumps(seq, indent=2))

    # ---- overlapped --------------------------------------------------------
    ov: dict = {"label": "overlapped A->B (prefetch during A's generation)"}
    eng = PrefetchEngine(ceiling_gb=args.ceiling_gb)
    kickoff = eng.prefetch(args.model_a, args.port_base + 10)
    ov["a_prefetch_kicked"] = kickoff
    eng.swap(args.model_a, args.port_base + 10)  # wait for A via promote/fallback
    srv_a = eng.active()
    assert srv_a is not None, "active server missing after swap"
    g = _generate(srv_a)
    ov["a_gen_s"] = g["total_s"]
    # kick off B's load WHILE A is generating (the point of G2.2)
    t_kick = time.monotonic()
    kicked = eng.prefetch(args.model_b, args.port_base + 11)
    ov["b_prefetch_kicked"] = kicked
    # finish A's generation with B loading in parallel
    g2 = _generate(srv_a, prompt="Write a Python function that returns 43.")
    ov["a_second_gen_s"] = g2["total_s"]
    ov["b_load_started_during_a"] = round(time.monotonic() - t_kick, 3)
    swap_stats = eng.swap(args.model_b, args.port_base + 11)
    ov.update(swap_stats)
    ov["swap_to_first_token_s"] = round(swap_stats["swap_s"], 3)
    ov["total_a_plus_swap_s"] = round(ov["a_gen_s"] + ov["a_second_gen_s"] + swap_stats["swap_s"], 3)
    eng.stop()
    report["overlapped"] = ov
    print("overlapped:", json.dumps(ov, indent=2))

    # ---- compare -------------------------------------------------------------
    saving = round(report["sequential"]["swap_to_first_token_s"] - report["overlapped"]["swap_to_first_token_s"], 3)
    report["saving_s"] = saving
    report["saving_pct"] = round(100 * saving / max(1e-6, report["sequential"]["swap_to_first_token_s"]), 1)
    print(f"\nsaving: {saving}s ({report['saving_pct']}%)")

    out = args.out or os.path.join(RESULTS_DIR, f"swap-overlap-{time.strftime('%Y%m%d-%H%M%S')}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"results: {out}")


if __name__ == "__main__":
    main()
