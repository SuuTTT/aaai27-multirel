#!/usr/bin/env python3
"""Generate fig_pred12.pdf, fig_horizon.pdf, fig_ablation.pdf.

Design rules:
- figsize width = IEEEtran column width (3.5") so fonts render at stated pt size.
- Standard academic style: upward bars, normal y-axis, value labels above bars.
- Single shared legend per figure in deterministically reserved space
  (subplots_adjust, not tight_layout guesswork).
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

COL = 3.5  # IEEEtran column width in inches

plt.rcParams.update({
    'pdf.fonttype': 42,        # TrueType, not Type 3 (IEEE PDF eXpress requirement)
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.linewidth': 0.6,
    'xtick.major.width': 0.6,
    'ytick.major.width': 0.6,
})

# ── colors ───────────────────────────────────────────────────────────────────
ITRANS_COLOR = '#4472C4'
MR_COLOR     = '#C00000'
GAIN_COLOR   = '#BE0000'   # matches the paper's table gain color (RGB 190,0,0)

MODEL_COLORS = {
    'DLinear':      '#FFD966',
    'PatchTST':     '#70AD47',
    'CrossFormer':  '#ED7D31',
    'iTransformer': ITRANS_COLOR,
    'MultiRel':     MR_COLOR,
}

ABL_COLORS = {
    'iT':   ITRANS_COLOR,
    'PC':   '#7FA7D4',
    'PE':   '#70AD47',
    'LL':   '#ED9B5A',
    'Full': MR_COLOR,
}

# ── data: loaded from audit.json (ground truth) — never hardcode results ─────
import json as _json
_AUDIT = '/home/ubuntu/honest-ts-bench/results/audit.json'
_R = _json.load(open(_AUDIT))['results']

def _canon(r):
    cfg = (r.get('config') or '').upper()
    return not any(k in cfg for k in ('PUBLISHED', 'EXACT OFFICIAL', 'PUBLISHED-STYLE',
                                      'INTERMEDIATE', 'D1024'))

def _get(model, ds, pl):
    for r in _R:
        if (r['model'] == model and r['dataset'] == ds and r['pred_len'] == pl
                and _canon(r) and r.get('ablation') is None
                and len(r.get('seeds_mse') or []) >= 3):
            return round(r['mean_mse'], 4)
    return None

DATASETS = ['PEMS03', 'PEMS04', 'PEMS07', 'PEMS08']
HORIZONS = [12, 24, 48, 96]
N_MAP    = {'PEMS03': 358, 'PEMS04': 307, 'PEMS07': 883, 'PEMS08': 170}

ITRANS      = {ds: {h: _get('iTransformer', ds, h) for h in HORIZONS} for ds in DATASETS}
MR_SE       = {ds: {h: _get('MultiRel', ds, h) for h in HORIZONS} for ds in DATASETS}
DLINEAR     = {ds: _get('DLinear', ds, 12) for ds in DATASETS}
PATCHTST    = {ds: _get('PatchTST', ds, 12) for ds in DATASETS}
CROSSFORMER = {ds: _get('Crossformer', ds, 12) for ds in DATASETS}
GAINS_12 = {ds: round((ITRANS[ds][12] - MR_SE[ds][12]) / ITRANS[ds][12] * 100, 1)
            for ds in DATASETS}


# ─────────────────────────────────────────────────────────────────────────────
# Fig 4: 2×2 bar chart — upward bars, black value labels above tips
# ─────────────────────────────────────────────────────────────────────────────
def gen_pred12():
    models = ['DLinear', 'PatchTST', 'CrossFormer', 'iTransformer', 'MultiRel']
    colors = [MODEL_COLORS[m] for m in models]
    data   = {
        'DLinear':      DLINEAR,
        'PatchTST':     PATCHTST,
        'CrossFormer':  CROSSFORMER,
        'iTransformer': {ds: ITRANS[ds][12] for ds in DATASETS},
        'MultiRel':     {ds: MR_SE[ds][12]  for ds in DATASETS},
    }

    fig, axes = plt.subplots(2, 2, figsize=(COL, 2.55))
    fig.subplots_adjust(left=0.13, right=0.985, top=0.925, bottom=0.13,
                        hspace=0.50, wspace=0.30)

    for idx, (ax, ds) in enumerate(zip(axes.flatten(), DATASETS)):
        vals = [data[m].get(ds) for m in models]
        x    = np.arange(len(models))
        vmax = max(v for v in vals if v is not None)

        ax.bar(x, [v or 0.0 for v in vals], color=colors,
               edgecolor='black', linewidth=0.3, width=0.68, zorder=3)

        for i, v in enumerate(vals):
            if v is None:
                # A missing audit cell is NOT an OOM — label it as absent. (An
                # earlier version wrote 'OOM' here, which misclassified any
                # unharvested cell as a baseline memory failure.)
                ax.text(i, vmax * 0.03, 'n/a', ha='center', va='bottom',
                        fontsize=5.5, color='#555555', rotation=90)
            else:
                ax.text(i, v + vmax * 0.025, f'{v:.3f}',
                        ha='center', va='bottom',
                        fontsize=5.5, color='black')

        # relative improvement over iTransformer, green up-arrow as in the tables
        mr = MR_SE[ds][12]
        ax.text(len(models) - 1, mr + vmax * 0.135,
                f'$\\uparrow${GAINS_12[ds]:.1f}%',
                ha='center', va='bottom',
                fontsize=6, color=GAIN_COLOR, fontweight='bold')

        ax.set_title(f'{ds}  ($N$={N_MAP[ds]})', fontsize=7.5, pad=2)
        ax.set_xticks([])
        ax.set_ylim(0, vmax * 1.30)
        ax.tick_params(axis='y', labelsize=6)
        if idx % 2 == 0:
            ax.set_ylabel('MSE', fontsize=7)
        ax.grid(axis='y', alpha=0.3, linewidth=0.4, zorder=0)
        ax.set_axisbelow(True)

    patches = [mpatches.Patch(facecolor=c, edgecolor='black', linewidth=0.3,
                              label=m) for m, c in zip(models, colors)]
    fig.legend(handles=patches, ncol=5, loc='lower center',
               bbox_to_anchor=(0.5, 0.0), fontsize=6,
               frameon=False, handlelength=1.0, handletextpad=0.35,
               columnspacing=0.55, borderaxespad=0.1)

    fig.savefig('fig_pred12.pdf', dpi=300)
    plt.close()
    print('Saved fig_pred12.pdf')


# ─────────────────────────────────────────────────────────────────────────────
# Fig 5: line plots — normal y-axis, equally spaced horizons, shared legend
# ─────────────────────────────────────────────────────────────────────────────
def gen_horizon():
    show_ds = ['PEMS03', 'PEMS04', 'PEMS08']
    xpos = np.arange(len(HORIZONS))   # categorical spacing: no tick collision

    fig, axes = plt.subplots(1, 3, figsize=(COL, 1.5))
    fig.subplots_adjust(left=0.135, right=0.985, top=0.87, bottom=0.38,
                        wspace=0.42)

    lines = {}
    for j, (ax, ds) in enumerate(zip(axes, show_ds)):
        it_v = [ITRANS[ds][h] for h in HORIZONS]
        mr_v = [MR_SE[ds][h]  for h in HORIZONS]

        l1, = ax.plot(xpos, it_v, 'o--', color=ITRANS_COLOR,
                      linewidth=1.2, markersize=3, label='iTransformer')
        l2, = ax.plot(xpos, mr_v, 's-',  color=MR_COLOR,
                      linewidth=1.2, markersize=3, label='MultiRel')
        lines['iTransformer'] = l1
        lines['MultiRel']     = l2

        ax.set_title(ds, fontsize=7.5, pad=2)
        ax.set_xticks(xpos)
        ax.set_xticklabels([str(h) for h in HORIZONS], fontsize=6)
        ax.tick_params(axis='y', labelsize=6)
        if j == 1:
            ax.set_xlabel('Prediction horizon $H$', fontsize=7)
        if j == 0:
            ax.set_ylabel('MSE', fontsize=7)
        ax.grid(alpha=0.3, linewidth=0.4)
        ax.set_axisbelow(True)

    fig.legend(handles=list(lines.values()), labels=list(lines.keys()),
               ncol=2, loc='lower center', bbox_to_anchor=(0.5, 0.0),
               fontsize=6.5, frameon=False,
               handlelength=1.6, handletextpad=0.4, columnspacing=1.2,
               borderaxespad=0.1)

    fig.savefig('fig_horizon.pdf', dpi=300)
    plt.close()
    print('Saved fig_horizon.pdf')


# ─────────────────────────────────────────────────────────────────────────────
# Fig 6: ablation bars — zoomed y-range, black labels above bars
# ─────────────────────────────────────────────────────────────────────────────
def gen_ablation():
    abl_keys   = ['iT', 'PC', 'PE', 'LL', 'Full']
    abl_labels = ['iTransformer', 'MR-PC', 'MR-PE', 'MR-LL', 'MultiRel']
    # INTENTIONALLY HARDCODED: these mirror the paper's tab:ablation, which is
    # the d=512 supplementary configuration (disclosed in its caption) — NOT the
    # d=256 canonical audit. Do not "fix" these to audit values: that would
    # desynchronize the figure from the table. At d=256 the audit shows a single
    # mask beating the composition (PC 0.0797 vs full 0.0817 on PEMS04 pred-12),
    # which the paper discloses in the ablation text.
    abl_data   = {
        'PEMS04': [0.0881, 0.0850, 0.0817, 0.0863, 0.0794],
        'PEMS08': [0.0799, 0.0792, 0.0776, 0.0791, 0.0774],
    }
    colors = [ABL_COLORS[k] for k in abl_keys]

    fig, axes = plt.subplots(1, 2, figsize=(COL * 0.92, 1.7))
    fig.subplots_adjust(left=0.165, right=0.985, top=0.89, bottom=0.19,
                        wspace=0.50)

    for ax, ds in zip(axes, ['PEMS04', 'PEMS08']):
        vals = abl_data[ds]
        x    = np.arange(len(abl_keys))
        r    = max(vals) - min(vals)
        ylo  = min(vals) - r * 0.15
        yhi  = max(vals) + r * 0.42

        ax.bar(x, vals, color=colors, edgecolor='black', linewidth=0.3,
               width=0.62, zorder=3)
        ax.axhline(vals[0], color=ITRANS_COLOR, linestyle='--',
                   linewidth=0.7, alpha=0.6, zorder=2)

        for i, v in enumerate(vals):
            ax.text(i, v + r * 0.05, f'{v:.4f}',
                    ha='center', va='bottom', rotation=90,
                    fontsize=5, color='black')

        ax.set_title(ds, fontsize=7.5, pad=2)
        ax.set_xticks([])
        ax.set_ylim(ylo, yhi)
        ax.tick_params(axis='y', labelsize=6)
        if ds == 'PEMS04':
            ax.set_ylabel('MSE', fontsize=7)
        ax.grid(axis='y', alpha=0.3, linewidth=0.4, zorder=0)
        ax.set_axisbelow(True)

    patches = [mpatches.Patch(facecolor=ABL_COLORS[k], edgecolor='black',
                              linewidth=0.3, label=lbl)
               for k, lbl in zip(abl_keys, abl_labels)]
    fig.legend(handles=patches, ncol=5, loc='lower center',
               bbox_to_anchor=(0.5, 0.0), fontsize=5.5,
               frameon=False, handlelength=0.9, handletextpad=0.3,
               columnspacing=0.45, borderaxespad=0.05)

    fig.savefig('fig_ablation.pdf', dpi=300)
    plt.close()
    print('Saved fig_ablation.pdf')


if __name__ == '__main__':
    gen_pred12()
    gen_horizon()
    gen_ablation()
    print('Done.')
