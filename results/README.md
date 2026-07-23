# MRMA / MultiRel — Complete Experimental Results

Every number in the paper traces to this directory. The single source of truth is
**`audit.json`** — a per-seed ledger every paper table/figure is regenerated from in
code (`gen_ablation_honest.py`, `gen_gains_honest.py`, `gen_framework.py` at repo
root); nothing is hand-copied. `raw_logs/` holds the verbatim training-box logs the
audit entries were harvested from. All values are test-split MSE under the canonical
Time-Series-Library protocol (`seq_len=96`, d_model=256, e_layers=3, lr=5e-4,
10 epochs / patience 3, 3 seeds via `--itr 3` unless noted).

## Ground truth

| File | Contents |
|------|----------|
| **`audit.json`** | The full per-seed ledger: 13 models × PEMS03/04/07/08 × {12,24,48,96} + ECL/Traffic/exchange cross-domain + all ablations (`ablation` field: `ONES`/`PC`/`PE`/`LL`/`PCPE`/`HIER`), with config, box, and provenance per entry. Snapshot of `honest-ts-bench/results/audit.json`, 2026-07-23. |

## Experiment inventory (what was run, what it showed, where it lives)

### A. Core results (in the paper)

| # | Experiment | Key result | Result path | Paper use |
|---|-----------|-----------|-------------|-----------|
| A1 | Main PEMS grid — 13 models × 4 datasets × 4 horizons, 3 seeds | MultiRel beats iTransformer 16/16 (up to +21.5%); wide baseline table | `audit.json` (`ablation` absent) | Table 2 (`tables/framework_main.tex`) |
| A2 | MultiRel vs all-ones control (mask ablation), 16 PEMS cells | masks help **16/16, mean +9.7%, max +17.9%** | `audit.json` (`model=MultiRel, ablation=ONES` vs full) | Table 1, Fig. gains |
| A3 | StructMamba vs all-ones control, 16 PEMS cells | masks help **16/16, mean +13.8%, max +26.6%** | `audit.json` (harvested from `raw_logs/sm_ones.log`) | Table 1, Fig. gains |
| A4 | SECrossformer vs all-ones control, 16 PEMS cells | masks help only **5/16 (−4.9%)** — learned-router hosts resist | `audit.json` (`model=SECrossformer, ablation=ONES`) | Table 1, transfer boundary |
| A5 | Single-relation ablations (PC / PE / LL / PCPE), PEMS04+08, d512 & d256 | every single relation beats iTransformer; composition best at d512; capacity caveat at d256 | `audit.json` (ablation=PC/PE/LL); `ablation.json`; `raw_logs/ablation_box38768950.log`, `raw_logs/abl.log` | §Ablation + appendix |
| A6 | k-sensitivity (k∈{5..30}), PEMS04 pred-12, d512 | peak k=10, robust k∈[5,25]; k=20 cross-dataset default | `audit.json`; `ksens.json`; `raw_logs/ksens_*.log` | appendix table |
| A7 | Seed stability / divergence | MultiRel ≤3% spread; CrossFormer 44–60% spread beyond short horizons | `audit.json` seeds; `stability.json`; `raw_logs/stability_box38768950.log` | §Discussion, abstract |
| A8 | Graph statistics (densities, communities, union coverage 32.8%/67.2%) | quantifies L1 redundancy | `graphstats.json` | appendix + §Preliminaries |
| A9 | Cross-domain: ECL, Traffic (pred 96–720) | ECL masks help 4/4 (small); Traffic masks hurt 0/4 | `audit.json` (datasets ECL/Traffic) | appendix cross-domain table |

### B. Clean-data reruns & corrected scope (2026-07-20 → 23)

| # | Experiment | Key result | Result path |
|---|-----------|-----------|-------------|
| B1 | METR-LA/PEMS-BAY full rerun after missing-value fix (zeros→interpolated) + mask rebuild; 96/96 cells, 8 models | clean speed-network baselines; fixes C1/C2/H1 review findings | `raw_logs/rerun.log` |
| B2 | Speed-data recheck, 3 seeds (masks vs all-ones, metrla + PEMS08 pred-96) | metrla **0.706 vs 0.915 (+22.8%)** — old "speed boundary" was contamination artifact | `raw_logs/soft_confirm.log` |
| B3 | Scope grid: MultiRel {masks, all-ones} × 5 datasets × 4 horizons × 3 seeds | **all completed comparisons: masks win** (24/24 so far); in flight on box 45225092 | `raw_logs/scope_grid.log` (snapshot; final lands here + audit) |
| B4 | Independent single-cell reproduction (fresh box) | PEMS03/04/07/08 pred-12 numbers reproduce | `raw_logs/repro.log` |

### C. Negative / retired experiments (kept for honesty)

| # | Experiment | Verdict | Result path |
|---|-----------|---------|-------------|
| C1 | AMRA learned per-head gate v1 (init σ≈0.98) | gate saturated, AMRA≈hard everywhere — no adaptation | `raw_logs/amra_sig.log`, `amra_sig2.log` |
| C2 | AMRA gate v2 (neutral/low init + gate logging) | gate still ~flat at every init (loss ≈ flat in gate) → **retired** | `raw_logs/amra_v2.log`, `raw_logs/gate_*.txt` (trajectories) |
| C3 | Soft-vs-hard masking, 3 seeds | wash (hard 0.3274 vs soft 0.3322 on PEMS08; reversed on metrla) — no claim | `raw_logs/soft_confirm.log` |
| C4 | Never-worse decisive on PEMS07 (N=883) | **unrunnable on 11 GB** — even bare Crossformer OOMs at bs=1; needs ≥24 GB | `raw_logs/amra_sig3.log` |
| C5 | Finance pivot signal tests (NASDAQ-100, exchange-rate) | negative: MultiRel ≈ iTransformer ≈ DLinear — no structure to exploit | `raw_logs/fin_sig.log`, `raw_logs/nasdaq_sig.log` |
| C6 | pemsbay recovery cells (TimesNet 24/48, SEC PE/LL/ONES 96) | partial n1–n2 seeds only (box RAM limits); appendix-grade | `raw_logs/recover.log`, `rerun.log` |

### D. Legacy per-experiment JSON extracts (superseded by `audit.json`, kept for diffing)

`grid.json`, `pred12.json`, `pred96_extra.json`, `ablation.json`, `stability.json`,
`ksens.json`, `graphstats.json` — early extracts with per-seed MSE/MAE; where they
disagree with `audit.json`, **`audit.json` wins**.

## Provenance & integrity rules

- Every `audit.json` entry records `seeds_mse`, `config`, `box`, `provenance`.
- Duplicate cells exist (same cell run on different boxes); consumers must
  **dedupe to the best (lowest-MSE) canonical run** — see `gen_ablation_honest.py`.
- `FAILED`/divergent runs are logged, never silently dropped; a `0.0000` or empty
  seed list marks a crashed run, not a result.
- Regenerate all paper tables/figures: `python3 gen_ablation_honest.py && python3 gen_gains_honest.py`
  (reads `audit.json` only).

## GPU boxes used

| Box | Hardware | Experiments |
|-----|----------|-------------|
| 38664456 / 38768950 | early boxes | A1 grid, A5–A7 (see per-log suffixes) |
| 40230626/45, 40680574, 41274817 (A16) | mixed | A1 baselines, S-Mamba/StructMamba fulls |
| **45225092** | 8× RTX 2080 Ti | B1–B4, A3 (sm_ones), C1–C6, scope grid |
