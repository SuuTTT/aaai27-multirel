#!/usr/bin/env python3
"""Honest gains figure: FULL vs ONES mask ablation per instantiation, on PEMS.
Positive = the relation masks lower error vs the all-ones control (same model).
Recomputed from audit.json (best/lowest run per cell, dropping divergent dups).
Writes figs/fig_framework_gains.pdf
"""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AUDIT = "/home/ubuntu/honest-ts-bench/results/audit.json"
HERE = "/home/ubuntu/ltsf-cc/tslib/paper/multirel-overleaf"
PEMS = ["PEMS03", "PEMS04", "PEMS07", "PEMS08"]
HZ = [12, 24, 48, 96]
PAIRS = [("MultiRel", "MultiRel"), ("SECrossformer", "SECrossformer"),
         ("StructMamba", "StructMamba")]
res = json.load(open(AUDIT))["results"]

def best(model, ds, pl, ablset):
    v = [r["mean_mse"] for r in res if r["model"] == model and r["dataset"] == ds
         and r["pred_len"] == pl and r.get("ablation") in ablset
         and r.get("mean_mse") is not None]
    return min(v) if v else None

plt.rcParams.update({"font.size": 11, "axes.titlesize": 11, "axes.labelsize": 11,
                     "xtick.labelsize": 10, "ytick.labelsize": 10, "legend.fontsize": 9,
                     "font.family": "sans-serif", "axes.linewidth": 0.8, "pdf.fonttype": 42})
DS_COLOR = {"PEMS03": "#2a78d6", "PEMS04": "#1baf7a", "PEMS07": "#eda100", "PEMS08": "#4a3aa7"}
MARK = {"PEMS03": "o", "PEMS04": "s", "PEMS07": "^", "PEMS08": "D"}

fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.3), sharex=True)
for ax, (inst, _) in zip(axes, PAIRS):
    any_data = False
    mean_across = []
    for h in HZ:
        per = []
        for ds in PEMS:
            full = best(inst, ds, h, (None, "None"))
            ones = best(inst, ds, h, ("ONES",))
            if full is None or ones is None:
                continue
            g = (ones - full) / ones * 100.0
            per.append(g)
            ax.plot(HZ.index(h), g, MARK[ds], color=DS_COLOR[ds], markersize=6,
                    zorder=3, clip_on=False)
            any_data = True
        mean_across.append(sum(per) / len(per) if per else None)
    for ds in PEMS:
        ys, xs = [], []
        for i, h in enumerate(HZ):
            full = best(inst, ds, h, (None, "None")); ones = best(inst, ds, h, ("ONES",))
            if full is not None and ones is not None:
                ys.append((ones - full) / ones * 100.0); xs.append(i)
        if ys:
            ax.plot(xs, ys, "-", color=DS_COLOR[ds], lw=1.4, alpha=0.85, label=ds, zorder=2)
    mx = [(i, v) for i, v in enumerate(mean_across) if v is not None]
    if mx:
        ax.plot([i for i, _ in mx], [v for _, v in mx], "-", color="#0b0b0b",
                lw=2.4, label="Mean", zorder=4)
    ax.axhline(0, color="#999999", lw=0.8, ls="--", zorder=1)
    ax.set_title(f"{inst} vs all-ones")
    ax.set_xticks(range(len(HZ))); ax.set_xticklabels([str(h) for h in HZ])
    ax.set_xlabel("horizon")
    if not any_data:
        ax.text(0.5, 0.5, "ablation\nin progress", ha="center", va="center",
                transform=ax.transAxes, color="#888888", fontsize=11)
axes[0].set_ylabel("MSE reduction from masks (%)")
axes[0].legend(loc="upper left", frameon=False, ncol=1)
fig.tight_layout()
out = os.path.join(HERE, "figs", "fig_framework_gains.pdf")
fig.savefig(out, bbox_inches="tight")
print("wrote", out)
