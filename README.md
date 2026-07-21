# MRMA — AAAI-27 submission (7-page main paper)

**Structure for Free: Multi-Relational Attention Masks Improve Multivariate Forecasting**

Multi-Relational Masked Attention (MRMA): three precomputed relation graphs
(partial-correlation, Pearson, and a 2D-structural-entropy lead-lag partition) used as
zero-parameter binary attention masks. Primary instantiation **MultiRel = iTransformer +
MRMA** beats an all-ones-mask control in all 16 PEMS cells (mean +9.7%); a transfer study
characterises where the mechanism helps across backbones.

## Build
`main.tex` compiles as-is (pdfLaTeX + BibTeX). The AAAI-27 author kit (`aaai2027.sty`,
`aaai2027.bst`) is vendored so it builds on a fresh checkout with no manual steps.

- **Body: 7 pages** (AAAI-27 limit) + references + Technical Appendix.
- Figure 1 (`fig_teaser.pdf`): the three dependency types (motivation).
- Figure 2 (`fig_framework_icde.pdf`): iTransformer full attention vs MRMA masked heads (method).
- Extended tables/figures, algorithms, and the formal analysis live in the appendix
  (`_supp_*.tex`).

## Overleaf
New Project → Import from GitHub → `SuuTTT/aaai27-multirel`. Compiler: pdfLaTeX;
Main document: `main.tex`.

## Provenance
All result numbers are recomputed from `results/` via `gen_ablation_honest.py` /
`gen_gains_honest.py`. Nothing is hardcoded.
