# Draft verification

- Compiled with the unmodified NeurIPS 2025 style from the supplied ZIP,
  using the preprint option.
- Final PDF contains exactly nine pages, including references.
- Rendered and visually inspected all nine final pages.
- No overfull LaTeX boxes or unresolved references in the final build log.
- All validation/test RMSE and MAE values in the paper match saved CSV values
  rounded to three decimals.
- Figures are vector PDFs generated directly from saved data and predictions.
- Reported coverage, interval widths, residual diagnostics, and seasonal scores
  were checked against the experiment outputs.
- Forecast specifications and test predictions were not retuned for writing.
- Missing interval coverage is represented as unavailable for persistence,
  including seasonal tables; no persistence intervals are claimed in the paper.
- Refreshed the executed demo notebook after that reporting check. All 10 code
  cells and both forecasting protocol tests pass.

Current deliverable: `output/pdf/CPTS570_Temperature_Forecasting_Academic_Revision.pdf`.

The academic prose revision preserves all four tabular result blocks and all
five figure inclusions. RMSE/MAE values were rechecked against the CSV outputs.
References now use linked LaTeX citations and are numbered in citation order.
The final nine pages were rendered and visually reviewed; no overfull boxes or
unresolved citations/references occur. The preceding prose is archived in
`paper/archive/main_before_academic_revision.tex`.

Before course submission, review the prose, author details, and instructor rules
about reference-page counting. The repository URL has been supplied. The live
presentation has 12 slides with timed notes and a one-minute notebook demo slot.
