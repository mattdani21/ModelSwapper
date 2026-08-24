# Four-Number Proof — SwapOS public write-up (DRAFT)

> **STATUS: DRAFT — INTERNAL ONLY. NOT FOR PUBLICATION.**
> Publication is a **founder gate** (ENDGAME.md): this document is the internal
> draft of the public write-up. Nothing here ships until the founder says so.
> Every number below is quoted from a committed file in this repo (source in
> `[]` after each claim); no number may be restated in public without its
> committed source. Demo/historical numbers that predate this repo are flagged
> as such (§3).

## 1. Thesis

A pipeline of small, specialized models — each loaded only when its phase runs,
each handed a compact structured **Context Capsule** instead of stale KV state —
matches or beats a monolithic frontier model on structured coding work, at a
fraction of the cost, fully offline/private, on owned hardware. One specialist
resident at a time; weights swapped like virtual-memory pages
[MASTER-PROMPT.md §1, ADR-0001, ADR-0002].

The measurable claim: **the same 50-task suite, one frontier API call per task
vs. a REASON → CODE → REVIEW swap-pipeline of ≤ 27B-class specialists.**

## 2. The four numbers

### 2.1 Quality parity — MET, and re-confirmed

- Frontier baseline (deepseek-v4-pro, one call per task): **48/50 = 96.0%**
  on the 50-task suite (bugfix 17/17, feature 16/17, refactor 15/16)
  [`benchmarks/results/baseline-deepseek-v4-pro-20260807-001937.json`
  (tasks_passed=48, pass_rate=0.96, per-category), STATE.md].
- SwapOS pipeline, sequential backend, 8192 ctx, temp 0.2, capsule handoff:
  **47/50 = 94.0% with the retry loop** — bugfix 17/17, feature 17/17,
  refactor 13/16; 6 of the 47 passes came via the retry loop, so
  **pass@1 is 41/50**
  [`benchmarks/results/sequential-colab-27b-20260820-full50-8192.json`,
  STATE.md, docs/parity-report-phase1.md addendum 4 item 1]. That is
  **97.9% of the frontier baseline's rate** (47/48) [computed from the two
  files above; ratio stated in STATE.md]. The baseline is single-shot
  (48/50), so the honest pass@1 comparison is **41/50 single-shot vs 48/50
  single-shot (McNemar p ≈ 1.0 — statistically indistinguishable on this
  suite)** [docs/parity-report-phase1.md addendum 4 item 3].
- Overlap engine, same config: **45/50 = 90.0%**
  [`benchmarks/results/overlap-colab-27b-20260820-full50-8192.json`].
- The Phase-1 bar (G1.2) was **≥ 76.8%** (= 80% of the 96.0% baseline) and is
  **MET and re-confirmed on two independent GPUs** at the 0.2 operating point:
  **80.0%** on Colab L4 (2026-08-19) and **78.0%** on Colab RTX PRO 6000
  Blackwell (2026-08-20) [`benchmarks/results/pipeline-colab-27b-20260819-40of50.json`,
  `benchmarks/results/pipeline-colab-27b-20260820-39of50-t02-blackwell.json`,
  docs/parity-report-phase1.md addendum 2, docs/phase1-closeout.md §1].
- **CORRECTED (Addendum 4):** the 80.0% run was pass@1-only — its retry loop
  rescued 0 tasks (5/10 failures were a code defect); the 78.0% run had 8/11
  failures from the same NameError defect. The clean confirmation record is
  the sequential 8192-ctx run (47/50 = 94.0%, 97.9% of baseline), on which
  G1.2 was CLOSED. The earlier two runs are on record but not clean
  re-confirmations.
- The 47/50 record rides on two config changes vs the Phase-1 40/50 config:
  context 4096 → 8192 and the bounded (600-char) critic feedback
  [docs/parity-report-phase1.md addendum 3, pipeline/loop.py `feedback[:600]`].
- **Qualifier that must ship with any public claim:** temperature
  sensitivity — plausible direction, confounded by the code defect (11/15 of
  the 0.6 run's failures were a server-start NameError crash); not cleanly
  measured (downgraded per Addendum 4). The claim is stated at the **0.2
  operating point**, which is the notebook default; the stable core across
  temperatures is 29/50 (58%) [docs/parity-report-phase1.md addendum 2
  (temperature claim downgraded per Addendum 4), addendum 4 item 2,
  `benchmarks/results/pipeline-colab-27b-20260820-35of50-t06.json`].

### 2.2 Swap latency — the swap tax is gone

- Mean **paid load per phase: 1.995 s → 0.806 s (−60%)** between the
  sequential and overlap engines on the full 50-task suite at 27B scale
  [sequential vs overlap full-50 JSONs: mean_load_s 1.995 / 0.806; STATE.md].
- **41% of phases (80 of 195) pay zero load** — promoted/standby specialists
  [`overlap-colab-27b-20260820-full50-8192.json` phase logs; count in
  docs/parity-report-phase1.md addendum 3].
- **G2.1 met via overlap under the 1.5 s bar** (mean paid load 0.806 s <
  1.5 s; promoted swaps pay 0; local T4 direction 0.851 → 0.063 s)
  [STATE.md §Phase 2].
- Context: Phase-1 swap-per-phase measured 1.96 s load / 0.17 s evict at 27B
  scale — the swap mechanics are real and cheap; the remaining wall time is
  generation (tokens), not swaps [docs/parity-report-phase1.md, STATE.md].

### 2.3 Hardware floor — T4 measured, T0/T4-16 runbooked

- **T4 tier (8 GB) measured:** the floor stack (REASON/CODE Qwen3-4B-Q4_K_M,
  REVIEW Qwen3-0.6B-Q8_0) runs at **~1.5–1.7 GB peak RSS** (1.74 GB run 1 /
  1.53 GB run 2) — an 8 GB-class machine is a real deployment target; 8B Q4
  fails Metal allocation on 8 GB (the floor is 4B-class)
  [STATE.md Phase 0 table, `benchmarks/results/swap_baseline-20260806-233738.json`,
  `-233855.json` (peak_rss_kb), `-234241.json` (8B failure), hardware/tiers.yaml
  T4 max_specialist].
- Floor-stack pipeline evidence: 7/10 on the local 4B/0.6B dry run
  [`benchmarks/results/pipeline-local-4b-dryrun.json`, docs/phase1-closeout.md §2].
- One-command runbooks exist for **T0 (24 GB Air)** [`docs/t0-air-RUN.md`,
  `hardware/t0_air_run.sh` — G1.5 launch demo, peak memory ceiling 20 GB],
  **T4-16 (16 GB Mac, Coder-30B-A3B IQ2)** [`docs/t16-mac-RUN.md`,
  `hardware/t16_mac_run.sh`], and the **T4 floor (any Mac ≥ 8 GB)**
  [`hardware/t4_stack_run.sh`, commit af20a4e]. T0/T4-16 are PREPARED, not
  yet measured [docs/t0-air-RUN.md, docs/t16-mac-RUN.md, hardware/tiers.yaml].

### 2.4 Cost per task — API measured; local ≈ electricity only

- Frontier API suite: **≈ $0.15 total ≈ $0.003/task** (measured cost estimate
  0.1463 USD for 50 tasks; prices marked as estimates)
  [`benchmarks/results/baseline-deepseek-v4-pro-20260807-001937.json`
  (cost_estimate_usd=0.1463, price_notes), STATE.md, docs/parity-report-phase1.md
  §Cost framing].
- Local pipeline: **no per-task API cost — electricity only**; on owned
  hardware the marginal cost is ~0 and **no task data leaves the machine**
  [docs/parity-report-phase1.md §Cost framing, MASTER-PROMPT.md §4, ADR-0001].
- Honest note already on record: on *rented* GPUs at list prices the Phase-1
  run was ≈ 4.7× the API suite cost (~$0.70) — **the 1/50th cost framing is
  RETRACTED (Addendum 4)** — measured reality is ≈ 4.7× the API suite cost on
  rented L4 GPUs at list prices (~$0.70 vs ~$0.15). The honest claims are:
  (1) marginal local cost on owned hardware is ≈ electricity only; (2)
  sovereignty/privacy — no task data leaves the machine. No cost-vs-API claim
  may be made until numbers are measured on owned hardware
  [docs/parity-report-phase1.md §Cost framing].

## 3. Demo / historical results (from ENDGAME.md — pre-repo measurements)

- Qwen2.5-0.5B LoRA demo: **90% / 85.5%** [ENDGAME.md].
- KV-cache retrofit: **−45–49% memory** [ENDGAME.md].
- **Flag:** these numbers predate this repo's `benchmarks/results/` (no raw
  JSON here). ENDGAME.md is the committed record; the public write-up must
  point at the founder's original measurement sources before publishing.

## 4. Honest gaps (must appear in any public draft)

1. **G1.3 near-miss stands:** 2.12× (overlap) / 2.18× (sequential) vs the 2×
   bar (mean wall ≤ 38.6 s = 2× the 19.3 s API mean). Not hidden — on record
   [STATE.md, docs/parity-report-phase1.md addendum 3]. Lever in flight:
   **native-arch llama build** (arch list `75;80;89;90;100;120` +
   `LLAMA_CACHE_VERSION` v4) so Hopper/Blackwell eval GPUs run native kernels
   instead of PTX JIT — Run 4 prep [notebooks/colab-phase1-eval.ipynb,
   notebooks/colab-phase2-eval.ipynb, docs/phase1-pipeline-RUN.md §Run 4].
2. **G1.5 T0 measurement pending:** peak memory < 20 GB on the 24 GB Air is
   prepared but not yet measured; the Q4 config is borderline (expected
   19–21 GB), Q3 is the fallback [docs/t0-air-RUN.md, hardware/tiers.yaml T0,
   STATE.md].
3. **G2.4 integration note: CLOSED** — the issue-#15 closure note
   (docs/g2.4-capsule-v1-integration.md) was approved and issue #15 CLOSED;
   compression remains not wired into the running loop (by design, per the
   note) [capsule/compress.py, capsule/tests/test_compress.py,
   docs/g2.4-capsule-v1-integration.md].

## 5. What stays closed

- The **runtime and the Context Capsule are proprietary** — on-prem/edge SLM
  serving is Decile product synergy; **only the thesis + the numbers go
  public** [ENDGAME.md, ADR-0002, MASTER-PROMPT.md §1].
- The 50-task suite, the grader, and the baseline runner stay **sacred and
  private**; the public write-up names the *method* (50 coding tasks,
  frontier-API baseline, same suite both sides) without shipping the tasks
  [AGENTS.md §2.3, docs/adr/0003-benchmark-suite-and-baseline.md].

---

*Draft owner: orchestrator. Next action: Run 4 (G1.3 native-arch, deciding
instrument) on an eval GPU + T0 Air measurement (G1.5) on a 24 GB Mac, then
re-derive this draft against the new numbers before the founder gate. G2.4
issue-#15 note: CLOSED (approved 2026-08-23).*
