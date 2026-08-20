#!/usr/bin/env bash
# =============================================================================
# T4 stack runbook — the 8 GB-box swapper (4B/0.6B), run on ANY Mac >= 8 GB
#
# The exact T4 floor stack, now runnable comfortably on the 24 GB Air (peak
# ~4 GB — no memory pressure, machine stays usable). This is the first FULL
# 50-task run of the floor stack (the 8 GB box only ever did 10-task dry
# runs + 3-task ablations).
#
#   REASON: Qwen3-4B-Q4_K_M    (2.5 GB)
#   CODE:   Qwen3-4B-Q4_K_M    (2.5 GB)
#   REVIEW: Qwen3-0.6B-Q8_0    (0.6 GB)   <- the known weak link at the floor
#
# Options:
#   REVIEW_MODEL=8b    upgrade the critic to Qwen3-8B-Q4_K_M (5 GB — fixes
#                      the 0.6B weak link; free on a 24 GB machine)
#   BACKEND=overlap    run the two-slot prefetch engine (fits: 4B+0.6B=3.2 GB)
#   --smoke-only       just the 3-task validation
#
# Usage:
#   bash hardware/t4_stack_run.sh [--smoke-only]
#   REVIEW_MODEL=8b BACKEND=overlap bash hardware/t4_stack_run.sh
# =============================================================================
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${VENV:-$HOME/swapos-venv}"
MODELS_DIR="$REPO_DIR/models"
RESULTS_DIR="$REPO_DIR/benchmarks/results"
DATE="$(date +%Y%m%d-%H%M%S)"
SMOKE_ONLY="${1:-}"
REVIEW_MODEL="${REVIEW_MODEL:-0.6b}"   # 0.6b (floor) | 8b (upgrade)
BACKEND="${BACKEND:-llama}"            # llama (sequential) | overlap

TOTAL_GB="$(sysctl -n hw.memsize | awk '{print int($1/1073741824)}')"
echo "== ModelSwapper T4 stack on $(hostname) | RAM ${TOTAL_GB}GB | review=${REVIEW_MODEL} | backend=${BACKEND} | $(date)"

# keep the Mac awake for the whole run (overnight runs)
caffeinate -dims -w $$ &>/dev/null &
echo "== caffeinate active (Mac won't sleep while this runs)"

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

# --- 3. models (small — already on the 8 GB Mac; copy over or re-download) ------
mkdir -p "$MODELS_DIR"
F4="Qwen3-4B-Q4_K_M.gguf"
F06="Qwen3-0.6B-Q8_0.gguf"
F8="Qwen3-8B-Q4_K_M.gguf"
EXP4=2490000000
EXP06=630000000
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

dl "https://huggingface.co/lmstudio-community/Qwen3-4B-GGUF/resolve/main/$F4" "$MODELS_DIR/$F4" "$EXP4"
if [ "$REVIEW_MODEL" = "8b" ]; then
  dl "https://huggingface.co/Qwen/Qwen3-8B-GGUF/resolve/main/$F8" "$MODELS_DIR/$F8" "$EXP8"
  REVIEW="$MODELS_DIR/$F8"
else
  dl "https://huggingface.co/Qwen/Qwen3-0.6B-GGUF/resolve/main/$F06" "$MODELS_DIR/$F06" "$EXP06"
  REVIEW="$MODELS_DIR/$F06"
fi
echo "== models ready: 4B x2 + $(basename "$REVIEW")"

# --- 4. repo up to date -------------------------------------------------------
git -C "$REPO_DIR" pull --ff-only --quiet 2>/dev/null || true

# --- 5. memory sampler ----------------------------------------------------------
MEM_CSV="$RESULTS_DIR/t4-memory-$DATE.csv"
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
export LLAMA_CONTEXT=8192 LLAMA_NGPU=99 OVERLAP_CEILING_GB=13
MODELS_JSON="{\"reason\":\"$MODELS_DIR/$F4\",\"code\":\"$MODELS_DIR/$F4\",\"review\":\"$REVIEW\"}"
BACKEND_ARGS=()
[ "$BACKEND" = "overlap" ] && BACKEND_ARGS=(--backend overlap)

echo "== SMOKE (3 tasks) =="
"$VENV/bin/python" "$REPO_DIR/pipeline/run_pipeline.py" \
  --models-json "$MODELS_JSON" --limit 3 \
  --out "$RESULTS_DIR/pipeline-t4-smoke-$DATE.json" \
  --capsule-dir "$RESULTS_DIR/t4-capsules-smoke-$DATE" \
  --categories bugfix,feature,refactor \
  --temperature 0.2 --port-base 8900 --max-iterations 3 --max-tokens 2048 \
  "${BACKEND_ARGS[@]}"

if [ "$SMOKE_ONLY" = "--smoke-only" ]; then
  echo "== smoke only — full run skipped"
  exit 0
fi

echo "== FULL 50-TASK RUN (small models — expect ~1.5-3 h) =="
"$VENV/bin/python" "$REPO_DIR/pipeline/run_pipeline.py" \
  --models-json "$MODELS_JSON" --limit 0 \
  --out "$RESULTS_DIR/pipeline-t4-$DATE.json" \
  --capsule-dir "$RESULTS_DIR/t4-capsules-$DATE" \
  --categories bugfix,feature,refactor \
  --temperature 0.2 --port-base 8900 --max-iterations 3 --max-tokens 2048 \
  "${BACKEND_ARGS[@]}"

# --- 7. summary -------------------------------------------------------------------
kill $SAMPLER_PID 2>/dev/null || true
PEAK_USED="$(awk -F, -v t="$TOTAL_GB" 'NR>1 {u=t-$2; if (u>m) m=u} END {printf "%.1f", m}' "$MEM_CSV")"
echo ""
echo "== DONE =="
echo "results: $RESULTS_DIR/pipeline-t4-$DATE.json"
echo "memory csv: $MEM_CSV (peak unified memory used: ${PEAK_USED} GB of ${TOTAL_GB} GB)"
echo ""
echo "Next: push from this machine, or copy the two files to the other Mac:"
echo "  git -C $REPO_DIR add benchmarks/results && git -C $REPO_DIR commit -m 't4 stack run' && git -C $REPO_DIR push"
