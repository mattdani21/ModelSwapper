#!/usr/bin/env bash
# =============================================================================
# T4-16 runbook — ModelSwapper coding stack on a 16 GB Mac (T4 band top)
#
# The "very small Mac" tier: aggressive swap, one specialist resident at a
# time. The stack (all swap-fit for 16 GB):
#   REASON: Qwen3-14B Q4_K_M        (9.0 GB, peak ~11 GB)
#   CODE:   Qwen3-Coder-30B-A3B UD-IQ2_M  (10.8 GB, peak ~14 GB — the coding
#           specialist: 30B-class MoE with 3B active params -> fast on Metal)
#   REVIEW: Qwen3-8B Q4_K_M         (5.0 GB, peak ~7 GB)
#
# Context 8192 (the quality unlock), temp 0.2, sequential swap-per-phase
# (overlap would need two residents — this tier's policy is aggressive swap).
#
# Usage:
#   bash hardware/t16_mac_run.sh            # smoke (3) then full 50
#   bash hardware/t16_mac_run.sh --smoke-only
#   CODE_MODEL=qwen14b bash hardware/t16_mac_run.sh   # alt: 14B Q4 as coder
#
# Prereqs: brew + llama.cpp, python3 venv, ~30 GB free disk, ~25 GB download.
# =============================================================================
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${VENV:-$HOME/swapos-venv}"
MODELS_DIR="$REPO_DIR/models"
RESULTS_DIR="$REPO_DIR/benchmarks/results"
DATE="$(date +%Y%m%d-%H%M%S)"
SMOKE_ONLY="${1:-}"
CODE_MODEL="${CODE_MODEL:-a3b}"   # a3b (default) | qwen14b

TOTAL_GB="$(sysctl -n hw.memsize | awk '{print int($1/1073741824)}')"
echo "== ModelSwapper T4-16 run on $(hostname) | RAM ${TOTAL_GB}GB | code=${CODE_MODEL} | $(date)"
[ "$TOTAL_GB" -ge 16 ] || { echo "ERROR: this tier needs >= 16 GB RAM (found ${TOTAL_GB} GB)"; exit 1; }

# --- 1. llama-server (Metal) -------------------------------------------------
if ! command -v llama-server >/dev/null 2>&1; then
  echo "== installing llama.cpp via brew (one-time)..."
  brew install llama.cpp
fi

# --- 2. python venv with pytest ----------------------------------------------
if [ ! -x "$VENV/bin/python" ]; then
  echo "== creating venv at $VENV ..."
  python3 -m venv "$VENV"
fi
"$VENV/bin/python" -m pip install --quiet pytest 2>/dev/null || \
  "$VENV/bin/python" -m pip install pytest

# --- 3. models ----------------------------------------------------------------
mkdir -p "$MODELS_DIR"
F14="Qwen3-14B-Q4_K_M.gguf"
F8="Qwen3-8B-Q4_K_M.gguf"
FA3B="Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_M.gguf"
EXP14=9000000000
EXP8=5000000000
EXPA3B=10800000000

dl() { # dl <url> <dest> <minbytes>
  if [ -f "$2" ] && [ "$(stat -f%z "$2")" -gt "$3" ]; then
    echo "  cached: $2 ($(du -h "$2" | cut -f1))"
  else
    echo "  downloading $2 ..."
    curl -L --fail --progress-bar -o "$2.tmp" "$1"
    mv "$2.tmp" "$2"
    sz="$(stat -f%z "$2")"
    [ "$sz" -gt "$3" ] || { echo "ERROR: $2 too small ($sz bytes)"; exit 1; }
  fi
}

dl "https://huggingface.co/lmstudio-community/Qwen3-14B-GGUF/resolve/main/$F14" "$MODELS_DIR/$F14" "$EXP14"
dl "https://huggingface.co/Qwen/Qwen3-8B-GGUF/resolve/main/$F8" "$MODELS_DIR/$F8" "$EXP8"
if [ "$CODE_MODEL" = "a3b" ]; then
  dl "https://huggingface.co/unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF/resolve/main/$FA3B" "$MODELS_DIR/$FA3B" "$EXPA3B"
  CODE="$MODELS_DIR/$FA3B"
else
  CODE="$MODELS_DIR/$F14"   # alt: the 14B dense doubles as coder
fi
echo "== models ready: reason=$F14 code=$(basename "$CODE") review=$F8"

# --- 4. repo up to date -------------------------------------------------------
git -C "$REPO_DIR" pull --ff-only --quiet 2>/dev/null || true

# --- 5. memory sampler ----------------------------------------------------------
MEM_CSV="$RESULTS_DIR/t416-memory-$DATE.csv"
(
  while true; do
    vs="$(vm_stat | awk '/Pages free/{f=$3} /Pages inactive/{i=$3}
          END{gsub(/\./,"",f); gsub(/\./,"",i); printf "%.2f", (f+i)*4096/1073741824}')"
    echo "$(date +%s),$vs"
    sleep 30
  done
) > "$MEM_CSV" &
SAMPLER_PID=$!
trap 'kill $SAMPLER_PID 2>/dev/null || true' EXIT

# --- 6. pipeline (smoke then full) ----------------------------------------------
export LLAMA_CONTEXT=8192 LLAMA_NGPU=99 OVERLAP_CEILING_GB=13   # aggressive swap tier
MODELS_JSON="{\"reason\":\"$MODELS_DIR/$F14\",\"code\":\"$CODE\",\"review\":\"$MODELS_DIR/$F8\"}"

echo "== SMOKE (3 tasks) =="
"$VENV/bin/python" "$REPO_DIR/pipeline/run_pipeline.py" \
  --models-json "$MODELS_JSON" --limit 3 \
  --out "$RESULTS_DIR/pipeline-t416-smoke-$DATE.json" \
  --capsule-dir "$RESULTS_DIR/t416-capsules-smoke-$DATE" \
  --categories bugfix,feature,refactor \
  --temperature 0.2 --port-base 8900 --max-iterations 3 --max-tokens 2048

if [ "$SMOKE_ONLY" = "--smoke-only" ]; then
  echo "== smoke only — full run skipped"
  exit 0
fi

echo "== FULL 50-TASK RUN (expect ~3-6 h on Metal — run overnight) =="
"$VENV/bin/python" "$REPO_DIR/pipeline/run_pipeline.py" \
  --models-json "$MODELS_JSON" --limit 0 \
  --out "$RESULTS_DIR/pipeline-t416-$DATE.json" \
  --capsule-dir "$RESULTS_DIR/t416-capsules-$DATE" \
  --categories bugfix,feature,refactor \
  --temperature 0.2 --port-base 8900 --max-iterations 3 --max-tokens 2048

# --- 7. summary -------------------------------------------------------------------
kill $SAMPLER_PID 2>/dev/null || true
PEAK_USED="$(awk -F, -v t="$TOTAL_GB" 'NR>1 {u=t-$2; if (u>m) m=u} END {printf "%.1f", m}' "$MEM_CSV")"
echo ""
echo "== DONE =="
echo "results: $RESULTS_DIR/pipeline-t416-$DATE.json"
echo "memory csv: $MEM_CSV (peak unified memory used: ${PEAK_USED} GB of ${TOTAL_GB} GB)"
echo ""
echo "Next: push from this machine, or copy the two files to the other Mac:"
echo "  git -C $REPO_DIR add benchmarks/results && git -C $REPO_DIR commit -m 't4-16 run' && git -C $REPO_DIR push"
