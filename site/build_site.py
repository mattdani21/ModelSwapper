#!/usr/bin/env python3
"""Deterministic benchmark page generator (roadmap gate 4).

Reads the committed evidence JSONs under benchmarks/results/ and emits
site/index.html. Every number on the page comes from exactly one of two
places:

  (a) parsed from a committed results JSON, or
  (b) the pipeline row (doc-sourced), from the DOC_SOURCED constants
      below, each of which cites its source document + commit hash and
      is asserted against the parsed evidence where overlap exists.

No placeholders, no fabricated numbers, no uncommitted claims, no
network access. Re-running this script must produce byte-identical
output (no timestamps, no nondeterminism).

Usage:
    python3 site/build_site.py        # writes site/index.html
"""
from __future__ import annotations

import html
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "site", "index.html")

# ---------------------------------------------------------------------------
# Evidence files (parsed at build time). Commit hash = last commit touching
# the file on the current lineage (verified with `git log --follow -1`).
# ---------------------------------------------------------------------------
CANONICAL = {
    "path": "benchmarks/results/symmetric-baseline-deepseek-v4-pro-20260825-195414.json",
    "commit": "8c7a7a3",
}
EARLIER = {
    "path": "benchmarks/results/symmetric-baseline-20260825.json",
    "commit": "cd8b703",  # wt/symmetric-baseline
}
PIPELINE_JSON = {
    "path": "benchmarks/results/sequential-colab-27b-20260820-full50-8192.json",
    "commit": "5d3fd0f",
}
BASELINE_JSON = {
    "path": "benchmarks/results/baseline-deepseek-v4-pro-20260807-001937.json",
    "commit": "e9fb21e",
}
RUNNER = {
    "path": "benchmarks/harness/run_symmetric_baseline.py",
    "commit": "6b610d0",
}
PARITY_REPORT = {"path": "docs/parity-report-phase1.md", "commit": "8c7a7a3"}
FOUR_NUMBER_PROOF = {
    "path": "docs/four-number-proof.md",  # lives on branch wt/amended-pass1
    "commit": "694eff7",
}
ROADMAP = {"path": "docs/roadmap-to-revenue.md", "commit": "3bea626"}

# ---------------------------------------------------------------------------
# DOC-SOURCED constants — the pipeline row (27B+8B, ctx 8192). These figures
# are not present as machine fields in the pipeline results JSON (the JSON
# records 47/50 but not pass@1 or retry rescues), so they are pinned here
# with their document source, and asserted against the JSON where overlap
# exists. Source: docs/parity-report-phase1.md Addendum 5 (commit 8c7a7a3),
# plus benchmarks/results/sequential-colab-27b-20260820-full50-8192.json
# (commit 5d3fd0f) for the parsed fields.
# ---------------------------------------------------------------------------
PIPELINE_DOC = {
    "label": "Pipeline — 27B+8B, ctx 8192",
    "final": "47/50 (94%)",
    "pass_at_1": "41/50 (82%)",
    "retry_rescues": "+6",
    "failed": "refactor-01, refactor-02, refactor-12",
    "final_note": "6 of the 47 passes came via the retry loop, so pass@1 is 41/50",
    "source": {
        "Addendum 5 table (all doc-sourced cells)": PARITY_REPORT,
        "tasks_passed 47 / per-category / wall-clock (parsed)": PIPELINE_JSON,
    },
}

# Loop-equipped comparison (Addendum 5, commit 8c7a7a3): discordant pairs
# 2 vs 3 (pipeline-only wins bugfix-08 + feature-08; API-only wins
# refactor-01/02/12) -> exact McNemar p ~= 1.0.
LOOP_MCNEMAR = {
    "pipeline_only": 2,
    "api_only": 3,
    "p": "p ≈ 1.0",
    "pipeline_only_tasks": "bugfix-08, feature-08",
    "api_only_tasks": "refactor-01, refactor-02, refactor-12",
    "quote": (
        "statistically indistinguishable from a frontier API on this suite "
        "under an identical loop protocol (47 vs 48), at zero marginal cost "
        "and zero data egress."
    ),
    "source": PARITY_REPORT,
}

# Honest pass@1 comparison (reviewer-approved amendment, commit 694eff7,
# branch wt/amended-pass1): pipeline pass@1 41/50 vs API single-shot 48/50
# -> exact McNemar p = 0.016 (b=7 c=0), a significant gap at n=50.
# p ≈ 1.0 applies ONLY to the loop-equipped comparison above.
PASS1_MCNEMAR = {
    "pipeline": "41/50",
    "api_single_shot": "48/50",
    "p": "p = 0.016",
    "discordant": "b=7, c=0",
    "verdict": "a significant gap at n=50, not inside noise",
    "source": FOUR_NUMBER_PROOF,
    "source2": PARITY_REPORT,  # Addendum 4 item 3
}

# Retry-loop mechanism finding (Addendum 5, commit 8c7a7a3).
RETRY_FINDING = {
    "pipeline": "+6 (41 → 47)",
    "api": "+2 (46 → 48)",
    "note": (
        "the frontier model is already near its ceiling at pass@1, while "
        "smaller specialists have headroom that feedback loops capture"
    ),
    "source": PARITY_REPORT,
}

# Headline (roadmap Step 0 verdict wording, commit 8c7a7a3 + cd8b703).
HEADLINE = "48/50 on two independent runs, $0.25–$0.45 per suite"
HEADLINE_STATS = [
    ("48/50", "final, both independent runs"),
    ("46/50", "pass@1, both independent runs"),
    ("$0.25–$0.45", "measured API cost per suite"),
]


def load(evidence: dict) -> dict:
    with open(os.path.join(REPO, evidence["path"])) as fh:
        return json.load(fh)


def e(value: object) -> str:
    """HTML-escape for safe interpolation."""
    return html.escape(str(value))


def fmt_usd(value: float) -> str:
    return f"${value:,.4f}"


def fmt_int(value: int) -> str:
    return f"{value:,}"


def main() -> None:
    canonical = load(CANONICAL)
    earlier = load(EARLIER)
    pipeline_json = load(PIPELINE_JSON)
    baseline = load(BASELINE_JSON)

    # --- invariants: refuse to build on evidence drift ---------------------
    checks = [
        (canonical["tasks_passed"], 48, "canonical tasks_passed"),
        (canonical["pass_at_1"], 46, "canonical pass_at_1"),
        (earlier["tasks_passed"], 48, "earlier tasks_passed"),
        (earlier["pass_at_1"], 46, "earlier pass_at_1"),
        (pipeline_json["tasks_passed"], 47, "pipeline JSON tasks_passed"),
        (baseline["tasks_passed"], 48, "baseline tasks_passed"),
        (round(canonical["cost_estimate_usd"], 4), 0.4539, "canonical cost"),
        (round(earlier["cost_estimate_usd"], 4), 0.2461, "earlier cost"),
        (canonical["wall_clock_s"], 3236.0, "canonical wall clock"),
        (canonical["mean_phase_latency_s"], 28.24, "canonical phase latency"),
        (canonical["tokens_in"], 70180, "canonical tokens_in"),
        (canonical["tokens_out"], 209424, "canonical tokens_out"),
    ]
    for got, want, label in checks:
        assert got == want, f"evidence drift: {label}: got {got}, want {want}"
    for run, label in ((canonical, "canonical"), (earlier, "earlier")):
        per = run["per_category"]
        total = sum(v["passed"] for v in per.values())
        assert total == run["tasks_passed"], f"{label}: per-category sum mismatch"

    failed_canonical = [r["task_id"] for r in canonical["results"] if not r["passed"]]
    failed_earlier = [r["task_id"] for r in earlier["results"] if not r["pass"]]
    failed_baseline = [r["task_id"] for r in baseline["results"] if not r["pass"]]
    assert failed_canonical == ["bugfix-08", "feature-08"], failed_canonical
    assert failed_earlier == ["feature-08", "refactor-12"], failed_earlier
    assert failed_baseline == ["feature-08", "refactor-12"], failed_baseline
    # pipeline row is doc-sourced; pin it to the parsed JSON so the doc
    # cannot drift from the evidence (review t_23f2732a)
    failed_pipeline = [r["task_id"] for r in pipeline_json["results"] if not r["passed"]]
    assert ", ".join(failed_pipeline) == PIPELINE_DOC["failed"], (
        f"pipeline JSON failed tasks ({', '.join(failed_pipeline)}) drift from "
        f"PIPELINE_DOC['failed'] ({PIPELINE_DOC['failed']})"
    )

    c = canonical
    x = earlier
    pj = pipeline_json
    b = baseline

    ctx = {
        "headline": HEADLINE,
        "headline_stats": HEADLINE_STATS,
        # main comparison table
        "pipe": PIPELINE_DOC,
        "api_loop_final": f"{c['tasks_passed']}/{c['tasks_total']} ({c['pass_rate']:.0%})",
        "api_loop_pass1": f"{c['pass_at_1']}/{c['tasks_total']} ({c['pass_at_1'] / c['tasks_total']:.0%})",
        "api_loop_retries": "+2",
        "api_loop_failed": ", ".join(failed_canonical),
        "api_loop_wall": f"{c['wall_clock_s']:.1f} s",
        "api_loop_latency": f"{c['mean_phase_latency_s']:.2f} s",
        "api_loop_tokens": f"{fmt_int(c['tokens_in'])} / {fmt_int(c['tokens_out'])}",
        "api_loop_cost": fmt_usd(c["cost_estimate_usd"]),
        "single_final": f"{b['tasks_passed']}/{b['tasks_total']} ({b['pass_rate']:.0%})",
        "single_pass1": f"{b['tasks_passed']}/{b['tasks_total']} ({b['pass_rate']:.0%})",
        "single_retries": "—",
        "single_failed": ", ".join(failed_baseline),
        "single_wall": f"{b['wall_clock_s']:.1f} s",
        "single_latency": "—",
        "single_tokens": f"{fmt_int(b['tokens_in'])} / {fmt_int(b['tokens_out'])}",
        "single_cost": fmt_usd(b["cost_estimate_usd"]),
        "pipe_wall": f"{pj['wall_clock_s']:.1f} s",
        # two Step-0 runs table
        "c_run_at": c["run_at"], "x_run_at": x["run_at"],
        "c_wall": f"{c['wall_clock_s']:.1f} s", "x_wall": f"{x['wall_clock_s']:.1f} s",
        "c_latency": f"{c['mean_phase_latency_s']:.2f} s", "x_latency": "—",
        "c_tokens": f"{fmt_int(c['tokens_in'])} / {fmt_int(c['tokens_out'])}",
        "x_tokens": f"{fmt_int(x['tokens_in'])} / {fmt_int(x['tokens_out'])}",
        "c_cost": fmt_usd(c["cost_estimate_usd"]), "x_cost": fmt_usd(x["cost_estimate_usd"]),
        "c_failed": ", ".join(failed_canonical), "x_failed": ", ".join(failed_earlier),
        "c_pcat": (f"bugfix {c['per_category']['bugfix']['passed']}/{c['per_category']['bugfix']['total']} · "
                   f"feature {c['per_category']['feature']['passed']}/{c['per_category']['feature']['total']} · "
                   f"refactor {c['per_category']['refactor']['passed']}/{c['per_category']['refactor']['total']}"),
        "x_pcat": (f"bugfix {x['per_category']['bugfix']['passed']}/{x['per_category']['bugfix']['total']} · "
                   f"feature {x['per_category']['feature']['passed']}/{x['per_category']['feature']['total']} · "
                   f"refactor {x['per_category']['refactor']['passed']}/{x['per_category']['refactor']['total']}"),
        # statistics
        "loop": LOOP_MCNEMAR,
        "pass1": PASS1_MCNEMAR,
        "retry": RETRY_FINDING,
        # sources
        "src_canonical": CANONICAL, "src_earlier": EARLIER,
        "src_pipeline_json": PIPELINE_JSON, "src_baseline": BASELINE_JSON,
        "src_runner": RUNNER, "src_parity": PARITY_REPORT,
        "src_four": FOUR_NUMBER_PROOF, "src_roadmap": ROADMAP,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        fh.write(render(ctx))
    print(f"wrote {os.path.relpath(OUT, REPO)}")


# ---------------------------------------------------------------------------
# Template
# ---------------------------------------------------------------------------
CSS = """
:root{--bg:#0b0e14;--panel:#12161f;--panel2:#0f131c;--line:#232a37;--fg:#d7dde8;
--mut:#8b94a7;--acc:#4cc2ff;--ok:#3fb950;--warn:#d29922;--bad:#f85149;}
*{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--fg);font:14px/1.55 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;padding:40px 20px;}
main{max-width:1040px;margin:0 auto;}
a{color:var(--acc);text-decoration:none;} a:hover{text-decoration:underline;}
.kicker{color:var(--mut);font-size:11px;letter-spacing:.14em;text-transform:uppercase;margin-bottom:14px;}
h1{font-size:26px;font-weight:700;letter-spacing:-.01em;}
h2{font-size:15px;font-weight:700;margin:44px 0 14px;padding-top:22px;border-top:1px solid var(--line);letter-spacing:.02em;text-transform:uppercase;color:var(--acc);}
h3{font-size:13px;margin:18px 0 8px;color:var(--fg);}
p{margin:10px 0;}
.mut{color:var(--mut);} .ok{color:var(--ok);} .warn{color:var(--warn);} .bad{color:var(--bad);}
.headline{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:28px 30px;margin:22px 0 8px;}
.headline .hl{font-size:30px;font-weight:700;line-height:1.3;letter-spacing:-.01em;}
.headline .hl .hlsub{font-size:20px;}
.stats{display:flex;gap:14px;flex-wrap:wrap;margin-top:20px;}
.stat{flex:1;min-width:170px;background:var(--panel2);border:1px solid var(--line);border-radius:6px;padding:14px 16px;}
.stat .n{font-size:26px;font-weight:700;color:var(--acc);}
.stat .l{font-size:11px;color:var(--mut);margin-top:4px;}
table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:8px;overflow:hidden;margin:10px 0 6px;}
th,td{padding:9px 12px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top;font-size:13px;}
th{background:var(--panel2);color:var(--mut);font-weight:600;letter-spacing:.04em;text-transform:uppercase;font-size:11px;}
tr:last-child td{border-bottom:none;}
td.metric{color:var(--mut);white-space:nowrap;}
.quote{border-left:3px solid var(--acc);background:var(--panel2);padding:12px 16px;margin:14px 0;font-style:italic;color:var(--fg);}
.limits li{margin:8px 0 8px 18px;}
.foot{color:var(--mut);font-size:11px;margin-top:44px;padding-top:14px;border-top:1px solid var(--line);}
.note{font-size:12px;color:var(--mut);}
code{background:var(--panel2);border:1px solid var(--line);border-radius:4px;padding:1px 5px;font-size:12px;}
"""


def src_cell(evidence: dict, label: str = "") -> str:
    name = evidence["path"].split("/")[-1]
    if label:
        return f'<code>{e(label)}</code> <span class="mut">—</span> <code>{e(evidence["path"])}</code> <span class="mut">@</span> <code>{e(evidence["commit"])}</code>'
    return f'<code>{e(evidence["path"])}</code> <span class="mut">@</span> <code>{e(evidence["commit"])}</code>'


def render(c: dict) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SwapOS — swapos-v1 benchmark · roadmap Step 0 (falsification experiment)</title>
<style>{CSS}</style>
</head>
<body>
<main>

<header>
  <div class="kicker">SwapOS / ModelSwapper · open-funnel benchmark · roadmap gate 4 — Step 0 falsification experiment</div>
  <h1>swapos-v1 · the symmetric baseline</h1>
  <div class="headline">
    <div class="hl">{e(c["headline"])}</div>
    <p class="mut">The frontier API run through the pipeline's <em>identical</em> loop scored 48/50 on two
    independent runs — the falsification experiment did not falsify. Methodology:
    <a href="../docs/methodology-standard.md">docs/methodology-standard.md</a>.</p>
    <div class="stats">
      {"".join(f'<div class="stat"><div class="n">{e(n)}</div><div class="l">{e(l)}</div></div>' for n, l in c["headline_stats"])}
    </div>
  </div>
</header>

<section>
  <h2>1 · Comparison — pipeline vs frontier API, same loop</h2>
  <p class="note">The API arm ran the pipeline's identical loop — REASON plan → CODE → sacred grader → CRITIC
  (600-char bounded test-output feedback) → retry, max 3 attempts, temperature 0.2, prompts verbatim from
  <code>pipeline/prompts.py</code> — via the single harness runner
  {src_cell(c["src_runner"])}. The single-shot column is the original frontier baseline
  (one call per task, no loop).</p>
  <table>
    <tr><th>Metric</th><th>Pipeline (27B+8B, ctx 8192)</th><th>API deepseek-v4-pro — identical loop (canonical)</th><th>API deepseek-v4-pro — single shot (baseline)</th></tr>
    <tr><td class="metric">Final pass rate</td><td class="ok">{e(c["pipe"]["final"])}</td><td class="ok">{e(c["api_loop_final"])}</td><td class="ok">{e(c["single_final"])}</td></tr>
    <tr><td class="metric">pass@1</td><td>{e(c["pipe"]["pass_at_1"])}</td><td>{e(c["api_loop_pass1"])}</td><td>{e(c["single_pass1"])} <span class="note">(single-shot by construction)</span></td></tr>
    <tr><td class="metric">Retry rescues</td><td class="ok">{e(c["pipe"]["retry_rescues"])}</td><td>{e(c["api_loop_retries"])}</td><td>{e(c["single_retries"])} <span class="note">(no loop)</span></td></tr>
    <tr><td class="metric">Failed tasks</td><td>{e(c["pipe"]["failed"])}</td><td class="bad">{e(c["api_loop_failed"])}</td><td class="bad">{e(c["single_failed"])}</td></tr>
    <tr><td class="metric">Suite wall clock</td><td>{e(c["pipe_wall"])}</td><td>{e(c["api_loop_wall"])}</td><td>{e(c["single_wall"])}</td></tr>
    <tr><td class="metric">Mean phase latency</td><td>—</td><td>{e(c["api_loop_latency"])}</td><td>{e(c["single_latency"])}</td></tr>
    <tr><td class="metric">Tokens in / out</td><td>—</td><td>{e(c["api_loop_tokens"])}</td><td>{e(c["single_tokens"])}</td></tr>
    <tr><td class="metric">Cost estimate (USD)</td><td class="ok">$0 <span class="note">(local; zero marginal API cost)</span></td><td>{e(c["api_loop_cost"])}</td><td>{e(c["single_cost"])}</td></tr>
  </table>
  <p class="note">{e(c["pipe"]["final_note"])} — {src_cell(c["src_parity"])} Addendum 5 (all doc-sourced pipeline cells) · {src_cell(c["src_pipeline_json"])} (parsed 47/50, per-category, wall-clock).</p>
</section>

<section>
  <h2>2 · The two Step-0 runs — both 48/50</h2>
  <p class="note">Two independent runs of the symmetric baseline agree on the headline: 48/50, pass@1 46/50.
  The cost difference ($0.45 vs $0.25) is timing/pricing of the same protocol — the honest range is
  <strong>$0.25–$0.45 per suite</strong>.</p>
  <table>
    <tr><th>Metric</th><th>Canonical run · {e(c["c_run_at"])}</th><th>Earlier reproduction · {e(c["x_run_at"])}</th></tr>
    <tr><td class="metric">Final</td><td class="ok">48/50</td><td class="ok">48/50</td></tr>
    <tr><td class="metric">pass@1</td><td>46/50</td><td>46/50</td></tr>
    <tr><td class="metric">Per category</td><td>{e(c["c_pcat"])}</td><td>{e(c["x_pcat"])}</td></tr>
    <tr><td class="metric">Failed tasks</td><td class="bad">{e(c["c_failed"])}</td><td class="bad">{e(c["x_failed"])}</td></tr>
    <tr><td class="metric">Wall clock</td><td>{e(c["c_wall"])}</td><td>{e(c["x_wall"])}</td></tr>
    <tr><td class="metric">Mean phase latency</td><td>{e(c["c_latency"])}</td><td>{e(c["x_latency"])} <span class="note">(not recorded)</span></td></tr>
    <tr><td class="metric">Tokens in / out</td><td>{e(c["c_tokens"])}</td><td>{e(c["x_tokens"])}</td></tr>
    <tr><td class="metric">Cost estimate (USD)</td><td>{e(c["c_cost"])}</td><td>{e(c["x_cost"])}</td></tr>
    <tr><td class="metric">Evidence JSON</td><td>{src_cell(c["src_canonical"])}</td><td>{src_cell(c["src_earlier"])}</td></tr>
  </table>
</section>

<section>
  <h2>3 · Statistics — what is defensible</h2>

  <h3>3.1 Loop-equipped comparison: statistically indistinguishable</h3>
  <p>Discordant pairs {e(c["loop"]["pipeline_only"])} vs {e(c["loop"]["api_only"])} (pipeline-only wins:
  {e(c["loop"]["pipeline_only_tasks"])}; API-only wins: {e(c["loop"]["api_only_tasks"])}) — exact McNemar
  <strong class="ok">{e(c["loop"]["p"])}</strong>. The measured, defensible claim:</p>
  <div class="quote">"{e(c["loop"]["quote"])}"</div>
  <p class="note">Source: {src_cell(c["src_parity"])} Addendum 5.</p>

  <h3>3.2 pass@1 comparison: honest, and significant</h3>
  <p>Pipeline pass@1 {e(c["pass1"]["pipeline"])} vs API single-shot {e(c["pass1"]["api_single_shot"])} — exact
  McNemar <strong class="bad">{e(c["pass1"]["p"])}</strong> (discordant {e(c["pass1"]["discordant"])}):
  {e(c["pass1"]["verdict"])}. <span class="warn">{e(c["loop"]["p"])} applies ONLY to the loop-equipped
  comparison in 3.1 — never to this one.</span></p>
  <p class="note">Source: {src_cell(c["src_four"], "§2.1")} + {src_cell(c["src_parity"])} Addendum 4 item 3
  (reviewer-approved amendment, branch <code>wt/amended-pass1</code>). API single-shot 48/50:
  {src_cell(c["src_baseline"])}.</p>

  <h3>3.3 Retry-loop mechanism</h3>
  <p>The loop is worth {e(c["retry"]["pipeline"])} to the pipeline vs {e(c["retry"]["api"])} to the API —
  {e(c["retry"]["note"])}. Source: {src_cell(c["src_parity"])} Addendum 5.</p>
</section>

<section>
  <h2>4 · Honest limitations</h2>
  <ul class="limits">
    <li><strong>Hardware floor (G1.5) — open item.</strong> The hardware-floor numbers (rented G1.5, T4 tier)
    are <span class="warn">NOT yet measured on rented hardware</span>; this page makes no hardware claim and
    shows no placeholder or invented specs. See roadmap gate 3 ({src_cell(c["src_roadmap"])}).</li>
    <li><strong>Suite scope:</strong> swapos-v1 is single-file Python tasks only (interview-canon, one file per
    task, self-contained), n = 50, with one baseline vendor (deepseek-v4-pro). The suite is a screening
    instrument, not a general validator — expand vendors and task classes before generalizing.</li>
    <li><strong>pass@1 is a real gap:</strong> the pipeline needs its retry loop to reach parity (3.2); the
    headline parity claim is the <em>loop-equipped</em> comparison (3.1).</li>
    <li><strong>Cost framing — sovereignty only:</strong> API runs measured $0.25–$0.45 per suite; pipeline runs
    locally with zero marginal API cost and zero data egress. No "1/50th cost" or any other cost-ratio claim is
    made anywhere on this page (retracted red line, {src_cell(c["src_roadmap"])}).</li>
    <li><strong>Sacred evidence:</strong> every figure above is parsed from a committed results JSON or quoted
    from the cited documents (table 5); the grader and suite are never modified to make results pass — any
    change to suite or grader invalidates the comparison (docs/methodology-standard.md §§1–2).</li>
  </ul>
</section>

<section>
  <h2>5 · Source citations — every figure → file + commit</h2>
  <table>
    <tr><th>Figure</th><th>Source (file @ commit)</th></tr>
    <tr><td>Canonical symmetric run: 48/50, pass@1 46, cost {e(c["c_cost"])}, wall {e(c["c_wall"])}, mean phase latency {e(c["c_latency"])}, tokens {e(c["c_tokens"])}, per-category {e(c["c_pcat"])}, failed {e(c["c_failed"])}</td><td>{src_cell(c["src_canonical"])} · runner {src_cell(c["src_runner"])}</td></tr>
    <tr><td>Earlier reproduction: 48/50, pass@1 46, cost {e(c["x_cost"])}, wall {e(c["x_wall"])}, tokens {e(c["x_tokens"])}, failed {e(c["x_failed"])} (byte-identical copy of the original evidence file)</td><td>{src_cell(c["src_earlier"])}</td></tr>
    <tr><td>Pipeline row: 47/50 (94%), pass@1 41/50 (82%), retry rescues +6, failed {e(c["pipe"]["failed"])} — doc-sourced cells</td><td>{src_cell(c["src_parity"])} Addendum 5 · {src_cell(c["src_pipeline_json"])} (parsed 47/50)</td></tr>
    <tr><td>Loop-equipped McNemar {e(c["loop"]["p"])} (discordant {e(c["loop"]["pipeline_only"])} vs {e(c["loop"]["api_only"])}) and the 3.1 quote</td><td>{src_cell(c["src_parity"])} Addendum 5</td></tr>
    <tr><td>pass@1 McNemar {e(c["pass1"]["p"])} ({e(c["pass1"]["discordant"])})</td><td>{src_cell(c["src_four"])} §2.1 · {src_cell(c["src_parity"])} Addendum 4 item 3 (amendment {e(c["src_four"]["commit"])}, branch wt/amended-pass1)</td></tr>
    <tr><td>API single-shot 48/50, cost {e(c["single_cost"])}, failed {e(c["single_failed"])}</td><td>{src_cell(c["src_baseline"])}</td></tr>
    <tr><td>Retry mechanism +6 vs +2</td><td>{src_cell(c["src_parity"])} Addendum 5</td></tr>
    <tr><td>Cost framing / no cost-ratio red line / hardware-floor open item</td><td>{src_cell(c["src_roadmap"])}</td></tr>
    <tr><td>Methodology standard (suite definition, sacred grader, symmetric protocol)</td><td><code>docs/methodology-standard.md</code> <span class="mut">@</span> this commit (roadmap gate 4)</td></tr>
  </table>
</section>

<div class="foot">SwapOS / ModelSwapper · swapos-v1 · generated deterministically by
<code>site/build_site.py</code> from committed evidence — no placeholders, no fabricated numbers, no network.</div>

</main>
</body>
</html>
"""


if __name__ == "__main__":
    main()
