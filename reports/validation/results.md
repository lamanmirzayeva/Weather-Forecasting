# 2023 validation results

All parameters were fitted on 2019–2022. Forecast origins advance daily,
updating states without refitting. No 2024 values enter these experiments.

One specification per family was selected by the equal-weight mean of
one-day and seven-day validation RMSE, excluding nonconverged fits.
Ties follow deterministic grid order. This is a documented implementation
choice where the proposal does not prescribe a cross-horizon rule.

Origins start at 2022-12-31. Targets remain within 2023: 365 one-day
and 359 seven-day targets, identical across models. Seven-day targets
begin January 7. Forecasts use completed UTC-day observations and assume
those observations are available at the origin; archive publication delays
are not modeled.

## Selected model accuracy

| Family | Specification | Horizon | N | RMSE (C) | MAE (C) |
|---|---|---:|---:|---:|---:|
| seasonal | seasonal_K3_000 | 1 | 365 | 3.661 | 2.896 |
| seasonal | seasonal_K3_000 | 7 | 359 | 3.672 | 2.903 |
| arima | arima_K0_303 | 1 | 365 | 2.259 | 1.763 |
| arima | arima_K0_303 | 7 | 359 | 4.457 | 3.429 |
| combined | combined_K3_101 | 1 | 365 | 2.169 | 1.703 |
| combined | combined_K3_101 | 7 | 359 | 3.677 | 2.906 |
| persistence | persistence | 1 | 365 | 2.441 | 1.881 |
| persistence | persistence | 7 | 359 | 5.248 | 4.039 |

## Combined model intervals

| Horizon | Empirical coverage | Mean width (C) |
|---:|---:|---:|
| 1 | 95.9% | 9.490 |
| 7 | 95.0% | 15.019 |

Intervals are conditional on fitted parameter estimates and do not include
parameter uncertainty. Overlapping seven-day forecast errors are dependent.

## Training diagnostics

ADF tests reject a unit root in each Fourier-regression residual series;
KPSS does not reject level stationarity (reported p-value is bounded at 0.1).
Therefore combined models use d=0; d=1 is not justified by these diagnostics.
The nonseasonal ARIMA comparison searches d=0 and d=1 to allow annual
variation to be represented without Fourier terms.

Selected combined-model Ljung–Box p-values: {'14': 0.5173765714333021, '30': 0.16851348973049407}.
These use the longest continuous training residual segment after a 30-day
burn-in, so the missing day is never treated as an adjacent observation.
Degrees of freedom are adjusted for p+q. These are diagnostic checks,
not a guarantee of independent or normally distributed forecast errors.

## Reproduce

```powershell
python scripts/validate_models.py
python scripts/summarize_validation.py
python -m unittest discover -s scripts -p test_forecasting.py
```

Candidate-level forecasts, fitted parameters, convergence status, warnings,
and metrics are saved alongside this report. Cached candidates are reused.
If changing modeling code or inputs, use a fresh validation output directory.

ACF/PACF plots use the same continuous training segment. Next: review
remaining diagnostics, then refit selected models
on 2019–2023 and evaluate the frozen protocol on 2024. Validation scores
are selection results and must not be described as held-out test performance.

API reference: https://www.statsmodels.org/v0.14.6/generated/statsmodels.tsa.statespace.sarimax.SARIMAXResults.get_prediction.html
