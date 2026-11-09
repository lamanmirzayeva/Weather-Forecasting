# Daily Temperature Forecasting

CPTS 570, Fall 2026 — Jiayu and Laman.

Research question: does annual Fourier seasonality combined with ARMA/ARIMA
errors improve daily temperature forecasts and prediction intervals?

## Proposal protocol

- NOAA GSOD, 2019–2024; Pullman station preferred, Spokane backup.
- Daily mean temperature in Celsius; preserve calendar gaps without imputation.
- Train: 2019–2022. Validate: 2023. Test: 2024.
- Fourier period: 365.25 calendar days; K = 1, 2, 3.
- ARMA orders: p, q = 0, 1, 2, 3. Consider d = 1 only if diagnostics justify it;
  omit the redundant regression intercept for that case.
- Compare persistence, independent-error seasonal regression, nonseasonal ARIMA,
  and the combined seasonal regression with ARMA/ARIMA errors.
- Evaluate exact 1-day and 7-day horizons using daily forecast origins.
- Select using training diagnostics and chronological validation RMSE. Refit on
  2019–2023, freeze parameters, and update states during the 2024 test.
- Report RMSE, MAE, and combined-model 95% interval coverage and mean width.
- Exclude missing targets and compare models on common eligible targets.

## Setup and first stage

Python 3.11 or newer:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/prepare_data.py
```

The preparation script retrieves official station metadata, identifies full-period
Pullman and Spokane International candidates, and audits both. Raw files are cached
under `data/raw/`; processed daily series go to `data/processed/`. These directories
are excluded from Git. Audit summaries and SHA-256 checksums go to `reports/`.
Cached files are reused; remove a specific cached file to download it again.
NOAA TEMP uses Fahrenheit and 9999.9 for missing values. TEMP_ATTRIBUTES records
the number of contributing observations, not a quality flag. Other attribute
columns are retained in the source files for inspection.

Sources:
- https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/
- https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv
- https://www.ncei.noaa.gov/data/global-summary-of-the-day/doc/readme.txt

## Completed analysis stages

1. Review coverage and document station choice.
2. Implement Fourier terms and the three baseline models.
3. Fit combined models; validate and diagnose residuals.
4. Freeze selection and run the held-out test once.
5. Produce figures, a reproducible demo notebook, 9-page NeurIPS-format paper,
   and 10-minute presentation.

## Validation experiments

```powershell
python scripts/validate_models.py
python scripts/summarize_validation.py
python -m unittest discover -s scripts -p test_forecasting.py
```

Validation uses only 2019–2023. It searches the proposal's complete K/p/q grid,
records convergence and diagnostics, and compares exact 1-day and 7-day forecasts.
Select one specification per family using the equal-weight average of both
horizons' validation RMSE. Training stationarity diagnostics determine whether
seasonal residuals justify considering d=1. The nonseasonal comparison tries d=0,1.
Read `reports/validation/results.md` for results, assumptions, and limitations.
Model-level CSV/JSON files cache experiments; use a fresh output directory if code
or input data change.

## Frozen held-out test

```powershell
python scripts/evaluate_test.py
python scripts/summarize_test.py
```

Selected specifications are saved before evaluation in
`reports/test/frozen_protocol.json`. Models are refitted on 2019–2023 and their
parameters remain fixed while states update daily in 2024. Saved forecasts and
refits are reused on subsequent runs. Read `reports/test/results.md` for test
metrics, figures, limitations, and reproducibility information. Do not retune
against the test results.

Station selection is based on the coverage audit, never held-out forecast accuracy.

## Demo notebook

Open `notebooks/temperature_forecasting_demo.ipynb` in JupyterLab after preparing
data and running the analysis above. The notebook walks through coverage,
chronological splits, the model equation, validation, frozen test results,
seasonal errors, and limitations. Change `ORIGIN` to reconstruct a historical
forecast using only information available at that origin. It checks the result
against saved rolling forecasts, including prediction intervals.

The optional `RUN_PIPELINE` switch reuses cached analyses. It defaults to false
for a short presentation demo. To rebuild the notebook source and execute all
cells from the project root:

```powershell
python scripts/build_demo.py
python scripts/execute_demo.py
```

Execution uses a project-local kernel specification and saves displayed tables
and figures inside the notebook. Rebuilding clears previous notebook outputs.

## Paper draft

The nine-page paper draft (including references) is at
`output/pdf/CPTS570_Temperature_Forecasting_Academic_Revision.pdf`.
Editable LaTeX source and the supplied NeurIPS 2025 style are in `paper/`.
See `paper/README.md` for build steps and formatting assumptions, and
`paper/VERIFICATION.md` for completed checks. Figures are regenerated with
`python scripts/paper_assets.py`.

## Presentation

The live editable presentation has 12 slides, covering objectives, literature,
data, methods, validation, test results, uncertainty, the Python demo, and future
work. Its timed notes reserve nine minutes for narration and one minute for the
notebook demonstration. A copy of the rehearsal notes is in
`presentation/speaker-notes.md`. The source authoring module is
`presentation/build.mjs`; it uses the artifact presentation API, not the Python
forecasting pipeline. All forecasting implementations are Python.

GitHub repository: https://github.com/lamanmirzayeva/Weather-Forecasting

## Submission handoff

`output/submission/CPTS570_Submission_Package.zip` contains the current paper,
an exported PowerPoint, executed notebook, Python code, results, and cached NOAA
inputs. It excludes the local environment, compiler, Git metadata, and obsolete
PDF drafts. Read `SUBMISSION_README.md` for the recommended review order,
offline reproduction, and unresolved course-specific details.

Git preserves file bytes through `.gitattributes` so checkout line-ending changes
do not invalidate the byte-level scientific hashes. Manifest paths use forward
slashes for portability. Model orders and forecast results remain frozen.

The submission ZIP is a local handoff artifact rather than a checked-in file.
Run `python scripts/package_submission.py` to recreate it after preparing data.
