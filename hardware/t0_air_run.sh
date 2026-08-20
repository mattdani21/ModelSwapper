#!/usr/bin/env bash
# =============================================================================
# T0 runbook — ModelSwapper pipeline on a 24 GB MacBook Air (G1.5 / launch demo)
#
# Runs the EXACT Phase-2 config that scored 47/50 (94.0%) on the rented GPU:
#   Qwen3.8-27B Q4 (reason+code) + Qwen3-8B Q4 (critic), sequential backend,
#   context 8192, temp 0.2, 3 max iterations, 2048 max tokens.
# On Metal this is slower but the QUALITY and MEMORY numbers are the point:
#   - pass rate on the same 50-task suite (the parity claim on a laptop)
#   - peak unified memory (G1.5 ceiling: < 20 GB)
#
# Usage:
#   bash hardware/t0_air_run.sh            # smoke (3 tasks) then full 50
#   bash hardware/t0_air_run.sh --smoke-only
#   MODEL_Q=Q3_K_M bash hardware/t0_air_run.sh   # fallback quant (12.6 GB)
#
# Prereqs (checked/installed by the script): brew + llama.cpp, python3 venv,
# ~25 GB free disk, ~22 GB download (Q4) or ~18 GB (Q3).
# =============================================================================
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${VENV:-$HOME/swapos-venv}"
MODELS_DIR="$REPO_DIR/models"
RESULTS_DIR="$REPO_DIR/benchmarks/results"
DATE="$(date +%Y%m%d-%H%M%S)"
Q="${MODEL_Q:-Q4_K_M}"
SMOKE_ONLY="${1:-}"

TOTAL_GB="$(sysctl -n hw.memsize | awk '{print int($1/1073741824)}')"
echo "== ModelSwapper T0 run on $(hostname) | RAM ${TOTAL_GB}GB | quant ${Q} | $(date)"

# keep the Mac awake for the whole run (overnight runs)
caffeinate -dims -w $$ &>/dev/null &
echo "== caffeinate active (Mac won't sleep while this runs)"

# --- 1. llama-server (Metal) -------------------------------------------------
if ! command -v llama-server >/dev/null 2>&1; then
  echo "== installing llama.cpp via brew (one-time)..."
  brew install llama.cpp
fi
llama-server --version 2>/dev/null | head -1 || true

# --- 2. python venv with pytest (grader needs it) -----------------------------
if [ ! -x "$VENV/bin/python" ]; then
  echo "== creating venv at $VENV ..."
  python3 -m venv "$VENV"
fi
"$VENV/bin/python" -m pip install --quiet pytest 2>/dev/null || \
  "$VENV/bin/python" -m pip install pytest
echo "== venv python: $("$VENV/bin/python" --version)"

# --- 3. models ----------------------------------------------------------------
mkdir -p "$MODELS_DIR"
BASE27="https://huggingface.co/lmstudio-community/Qwen3.8-27B-GGUF/resolve/main"
BASE27Q3="https://huggingface.co/bartowski/Qwen3.8-27B-GGUF/resolve/main"
F27="Qwen3.8-27B-${Q}.gguf"
F8="Qwen3-8B-Q4_K_M.gguf"
EXP27_Q4=16700000000
EXP27_Q3=12000000000
EXP8=5000000000

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

if [ "$Q" = "Q4_K_M" ]; then EXP27=$EXP27_Q4; URL27="$BASE27/$F27"; else EXP27=$EXP27_Q3; URL27="$BASE27Q3/$F27"; fi
dl "$URL27" "$MODELS_DIR/$F27" "$EXP27"
dl "https://huggingface.co/Qwen/Qwen3-8B-GGUF/resolve/main/$F8" "$MODELS_DIR/$F8" "$EXP8"
echo "== models ready: $F27 + $F8"

# --- 4. repo up to date -------------------------------------------------------
git -C "$REPO_DIR" pull --ff-only --quiet 2>/dev/null || true

# --- 5. memory sampler (unified memory: 24 - (free+inactive)) -----------------
MEM_CSV="$RESULTS_DIR/air-memory-$DATE.csv"
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

# --- 6. pipeline (smoke then full) --------------------------------------------
export LLAMA_CONTEXT=8192 LLAMA_NGPU=99
MODELS_JSON="{\"reason\":\"$MODELS_DIR/$F27\",\"code\":\"$MODELS_DIR/$F27\",\"review\":\"$MODELS_DIR/$F8\"}"

echo "== SMOKE (3 tasks) =="
"$VENV/bin/python" "$REPO_DIR/pipeline/run_pipeline.py" \
  --models-json "$MODELS_JSON" --limit 3 \
  --out "$RESULTS_DIR/pipeline-air-smoke-$DATE.json" \
  --capsule-dir "$RESULTS_DIR/air-capsules-smoke-$DATE" \
  --categories bugfix,feature,refactor \
  --temperature 0.2 --port-base 8900 --max-iterations 3 --max-tokens 2048

if [ "$SMOKE_ONLY" = "--smoke-only" ]; then
  echo "== smoke only — full run skipped"
  exit 0
fi

echo "== FULL 50-TASK RUN (expect 4-8 h on Metal — run overnight) =="
"$VENV/bin/python" "$REPO_DIR/pipeline/run_pipeline.py" \
  --models-json "$MODELS_JSON" --limit 0 \
  --out "$RESULTS_DIR/pipeline-air-t0-$DATE.json" \
  --capsule-dir "$RESULTS_DIR/air-capsules-$DATE" \
  --categories bugfix,feature,refactor \
  --temperature 0.2 --port-base 8900 --max-iterations 3 --max-tokens 2048

# --- 7. summary -----------------------------------------------------------------
kill $SAMPLER_PID 2>/dev/null || true
PEAK_USED="$(awk -F, -v t="$TOTAL_GB" 'NR>1 {u=t-$2; if (u>m) m=u} END {printf "%.1f", m}' "$MEM_CSV")"
echo ""
echo "== DONE =="
echo "results: $RESULTS_DIR/pipeline-air-t0-$DATE.json"
echo "memory csv: $MEM_CSV (peak unified memory used: ${PEAK_USED} GB of ${TOTAL_GB} GB)"
echo ""
echo "Next: commit and push from the Air (or copy the two files to the Mac):"
echo "  git -C $REPO_DIR add benchmarks/results && git -C $REPO_DIR commit -m 't0 air run' && git -C $REPO_DIR push"
