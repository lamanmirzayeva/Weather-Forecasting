# 2024 held-out test results

## Protocol

Model orders were selected using 2023 validation and frozen before this test.
Each model was refitted once on 2019–2023, including the missing training day
as an unobserved state-space observation. Parameters remain fixed throughout
2024. States update only after forecasts are issued, using newly available
daily observations. No model choice or interval adjustment uses test results.

The first origin is December 31, 2023. There are 366 one-day and 360
seven-day forecasts, with identical origins/targets across models. Seven-day
targets begin January 7, 2024. The unit is degrees Celsius; days are UTC.

## Accuracy

| Model | Horizon | N | RMSE (C) | MAE (C) |
|---|---:|---:|---:|---:|
| arima | 1 | 366 | 2.486 | 1.932 |
| arima | 7 | 360 | 4.903 | 3.787 |
| combined | 1 | 366 | 2.405 | 1.815 |
| combined | 7 | 360 | 4.019 | 3.022 |
| seasonal | 1 | 366 | 4.003 | 2.995 |
| seasonal | 7 | 360 | 4.034 | 3.028 |
| persistence | 1 | 366 | 2.578 | 1.978 |
| persistence | 7 | 360 | 5.556 | 4.371 |

## Combined-model intervals

| Horizon | Coverage | Mean width (C) |
|---:|---:|---:|
| 1 | 93.7% | 9.295 |
| 7 | 95.6% | 14.856 |

## Interpretation and limits

The combined model has the lowest RMSE and MAE at both test horizons.
At seven days its improvement over seasonal regression is small (about
0.015 C RMSE), so the evidence mainly favors short-term error modeling for
one-day forecasts. The ranking at seven days differs slightly from validation.
These are descriptive comparisons; statistical significance is not established.

One-day interval coverage is below the nominal 95%; seven-day coverage is
slightly above nominal. Gaussian intervals condition on fitted parameters and
omit parameter uncertainty. Training residual diagnostics are recorded in
`refit_diagnostics.json`; passing a dependence check does not establish
normality, constant variance, or adequate coverage for every season.

For the refitted combined model, Ljung–Box p-values are 0.459 at lag 14
and 0.158 at lag 30. Jarque–Bera rejects normality (p about 5.1e-13),
and the ARCH LM check indicates changing conditional variance (p=0.025).
These diagnostic limitations are reported without changing the frozen model.

This study uses one station and one test year. Seven-day errors overlap and
are dependent. Daily data are treated as available after each UTC day closes;
actual NOAA publication delays are not simulated. Seasonal tables describe
target-date seasons, with DJF combining January/February and December.

## Reproduce

```powershell
python scripts/evaluate_test.py
python scripts/summarize_test.py
python -m unittest discover -s scripts -p test_forecasting.py
```

Existing refits and forecast files are reused for reproducibility. The frozen
protocol rejects changes to selected specifications. Do not use this test
to retune models. Tables and plots can be regenerated from saved forecasts.

Forecast/state-update API documentation:
https://www.statsmodels.org/v0.14.6/generated/statsmodels.tsa.statespace.sarimax.SARIMAXResults.extend.html

The project also includes an executed demo notebook, an academic paper,
and a presentation. Repository:
https://github.com/lamanmirzayeva/Weather-Forecasting.
