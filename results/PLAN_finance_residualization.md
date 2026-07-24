# Preregistered plan: finance residualization × alignment diagnostic

Registered 2026-07-24, BEFORE running. Motivation: the diffuse-regime finding
("masks neutral when one factor dominates") is exactly the quant maxim "everything
is beta; structure lives in the residual". We test whether the alignment diagnostic
responds to *removing* the common factor — a manipulation of the diagnostic
variable, not just an observation across datasets.

## Experiments

**F1 — Residualization manipulation (nasdaq, N=82; no new data needed).**
1. Compute market factor m_t = first principal component of training-split returns.
2. Residualize: X̃ = X − β m (per-channel OLS beta on the training split).
3. Recompute the diagnostic on raw vs residualized: top-eig-share, PC/PE/LL
   densities and pairwise Jaccard overlaps.
4. GPU: MultiRel masks-vs-all-ones on RAW and RESID nasdaq, pl ∈ {24, 96}, 3 seeds
   (masks rebuilt from the residualized training split for the RESID arm).

**F2 (optional, best-effort) — broader panel.** Fetch ~100 liquid US equities
(daily adjusted close, 2015–2024) via yfinance if installable on the box; else skip.
Same protocol as F1.

## Preregistered predictions

- P1 (high confidence): residualization drops top-eig-share substantially
  (raw ≈ 0.47 → resid ≲ 0.25, i.e., into the range where traffic sits).
- P2 (high confidence): graph overlaps decrease / relation graphs decollapse
  (jac(PC,PE) drops), because sector/idiosyncratic structure differs by relation type.
- P3 (medium confidence): the masks-vs-all-ones gap improves on RESID relative to
  RAW (raw ≈ neutral ±1%; resid: masks ≥ all-ones, possibly small positive).
- P4 (falsifier): if top-eig-share drops but the mask benefit does NOT move,
  the diagnostic is incomplete (factor dominance alone doesn't determine benefit)
  — reported as-is.

## Interpretation rules (fixed in advance)

- "Benefit moved" = sign( gain_resid − gain_raw ) > 0 with |Δ| > combined seed spread.
- No cherry-picking horizons: both pl=24 and pl=96 reported.
- All numbers land in audit.json with config tag FINANCE-RESID; provenance finq.log.
