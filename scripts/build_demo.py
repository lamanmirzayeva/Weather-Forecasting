"""Build the portable demo notebook without a notebook-authoring dependency."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
cells = []


def md(source):
    cells.append({'cell_type':'markdown','metadata':{},'source':source.splitlines(True)})


def code(source):
    cells.append({'cell_type':'code','metadata':{},'source':source.splitlines(True),
                  'execution_count':None,'outputs':[]})


md('''# Daily Temperature Forecasting
### CPTS 570 · Jiayu and Laman

**Question:** Does annual Fourier seasonality combined with short-term ARMA errors
improve daily mean temperature forecasting?

This demo follows the proposal: NOAA GSOD 2019–2024, chronological splits,
1-day and 7-day forecasts, component comparisons, and 95% prediction intervals.
All reported test results use models chosen before inspecting test performance.

## 1. Setup and reproducibility

From the repository root, create a Python environment and run:

```powershell
python -m pip install -r requirements.txt
python scripts/prepare_data.py
python scripts/validate_models.py
python scripts/summarize_validation.py
python scripts/evaluate_test.py
python scripts/summarize_test.py
jupyter lab notebooks/temperature_forecasting_demo.ipynb
```

The full validation search may take several minutes. The default notebook uses
saved experiment results and reconstructs a forecast from frozen parameters.
Raw/processed data are not tracked in Git; run preparation before opening this
notebook on another machine. Do not change the model choices after seeing 2024.
''')
code('''from pathlib import Path
import sys, json, hashlib, subprocess
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from IPython.display import display, Image, Markdown
from statsmodels.tsa.statespace.sarimax import SARIMAX

ROOT = Path.cwd().resolve()
if not (ROOT / "scripts/validate_models.py").exists():
    ROOT = ROOT.parent
assert (ROOT / "scripts/validate_models.py").exists(), "Start from the project or notebooks directory"
sys.path.insert(0, str(ROOT / "scripts"))
from validate_models import fourier, metrics
pd.set_option("display.max_columns", 12)
print("Project:", ROOT)
print("Python:", sys.version.split()[0])
''')
md('''## 2. Optional full reproduction

Leave `RUN_PIPELINE=False` for a quick demo. Set it to `True` to run preparation
and all analysis scripts. Existing cached experiments are reused. The scripts
never refit parameters during test forecasting. Changing source/data requires
reviewing cache validity, not silently reusing results.
''')
code('''RUN_PIPELINE = False
if RUN_PIPELINE:
    for script in ["prepare_data", "validate_models", "summarize_validation", "evaluate_test", "summarize_test"]:
        subprocess.run([sys.executable, str(ROOT / "scripts" / f"{script}.py")], cwd=ROOT, check=True)
print("Using saved results" if not RUN_PIPELINE else "Pipeline complete")
''')
md('''## 3. Station coverage and chronological splits

We use Pullman/Moscow Regional Airport, station **72785794129**. Spokane is the
audited backup. Temperatures are converted from Fahrenheit to Celsius. Calendar
gaps stay missing, and missing targets are excluded from evaluation.
GSOD dates represent UTC days. `TEMP_ATTRIBUTES` is a contributing observation
count, not a temperature quality flag.
''')
code('''data = pd.read_csv(ROOT / "data/processed/72785794129_daily.csv", parse_dates=["date"])
y = data.set_index("date").temperature_c.asfreq("D")
display(pd.read_csv(ROOT / "reports/station_coverage.csv"))
display(data.groupby("split").agg(calendar_days=("date", "size"), observed=("temperature_c", "count")))
print("Missing dates:", y[y.isna()].index.strftime("%Y-%m-%d").tolist())
assert len(y) == 2192 and y.index.is_unique
''')
code('''fig, ax = plt.subplots(figsize=(11, 3.5))
ax.plot(y.index, y, linewidth=.6, color="steelblue")
ax.axvline(pd.Timestamp("2023-01-01"), color="orange", label="Validation starts")
ax.axvline(pd.Timestamp("2024-01-01"), color="red", label="Test starts")
ax.set(title="Pullman daily mean temperature", ylabel="Temperature (°C)", xlabel="UTC date")
ax.legend()
plt.tight_layout()
plt.show()
''')
md(r'''## 4. Model and selection

The combined model is

$$y_t=\beta_0+\sum_{k=1}^{K}\left[a_k\sin(2\pi kt/365.25)+b_k\cos(2\pi kt/365.25)\right]+u_t,$$

where $u_t$ follows ARMA$(p,q)$. Calendar time is measured from a fixed origin,
so leap days and missing observations do not shift seasonal phase. Regression
and error parameters are jointly estimated by maximum likelihood.

We searched $K=1,2,3$ and $p,q=0,1,2,3$. Training residual stationarity checks
did not justify differencing for the combined model. The nonseasonal comparison
searched $d=0,1$. One specification per family was chosen using the equal-weight
average of validation RMSE across the two horizons. All 83 candidate fits converged.
''')
code('''display(pd.read_csv(ROOT / "reports/validation/selected_models.csv"))
display(pd.read_csv(ROOT / "reports/validation/selected_metrics.csv")[["family","horizon","n","rmse","mae"]].round(3))
display(Image(filename=str(ROOT / "reports/validation/training_residual_acf_pacf.png")))
''')
md('''## 5. Frozen held-out evaluation

After selection, refit on **2019–2023** and freeze parameters. Issue forecasts at
daily origins before revealing the next observation; then update the latent state.
Use identical origins and observed targets across models. The test contains
366 one-day forecasts and 360 seven-day forecasts (seven-day targets begin January 7).
The first origin is December 31, 2023. Publication delays are not modeled.
''')
code('''protocol = json.loads((ROOT / "reports/test/frozen_protocol.json").read_text())
display(protocol)
test_scores = pd.read_csv(ROOT / "reports/test/test_metrics.csv")
display(test_scores[["family","horizon","n","rmse","mae"]].round(3))
display(test_scores.loc[test_scores.family.eq("combined"), ["horizon","coverage","mean_width"]].round(3))
display(Image(filename=str(ROOT / "reports/test/test_accuracy.png")))
''')
md('''## 6. Reconstruct an individual forecast

Change `ORIGIN` to any test forecast origin through December 24, 2024. We load
the parameters fitted through 2023 and filter **only observations up to the origin**.
Known future calendar terms are allowed. Future temperatures are used only
after forecasting, to display observed targets. This reproduces saved rolling
forecasts rather than fitting a model on test observations.
''')
code('''ORIGIN = pd.Timestamp("2024-07-01")
assert pd.Timestamp("2023-12-31") <= ORIGIN <= pd.Timestamp("2024-12-24")
meta = json.loads((ROOT / "reports/test/combined_K3_101_fit.json").read_text())
history = y.loc[:ORIGIN]
future = pd.date_range(ORIGIN + pd.Timedelta(days=1), periods=7)
model = SARIMAX(history.to_numpy(), exog=fourier(history.index, meta["k"]),
                order=(meta["p"],meta["d"],meta["q"]),
                enforce_stationarity=True, enforce_invertibility=True)
filtered = model.filter(meta["params"])
fc = filtered.get_forecast(steps=7, exog=fourier(future, meta["k"]))
interval = np.asarray(fc.conf_int(alpha=.05))
forecast = pd.DataFrame({"prediction": np.asarray(fc.predicted_mean),
                         "lower": interval[:,0], "upper": interval[:,1]}, index=future)
forecast["observed_after_forecast"] = y.reindex(future)
display(forecast.iloc[[0,6]].round(3))
saved = pd.read_csv(ROOT / "reports/test/combined_K3_101.csv", parse_dates=["origin","target"])
for h in (1,7):
    row = saved[(saved.origin == ORIGIN) & (saved.horizon == h)].iloc[0]
    np.testing.assert_allclose(forecast.iloc[h-1][["prediction","lower","upper"]].to_numpy(),
                               row[["prediction","lower","upper"]].to_numpy(dtype=float), atol=1e-8)
print("Reconstructed forecasts and intervals match saved evaluation.")
''')
code('''fig, ax = plt.subplots(figsize=(10, 4))
recent = history.iloc[-21:]
ax.plot(recent.index, recent, color="black", label="Available history")
ax.fill_between(future, forecast.lower, forecast.upper, alpha=.25, label="95% prediction interval")
ax.plot(future, forecast.prediction, "o-", label="Forecast")
ax.plot(future, forecast.observed_after_forecast, "x--", color="black", label="Observed afterward")
ax.axvline(ORIGIN, color="gray", linestyle=":")
ax.set(title=f"Forecast issued after {ORIGIN.date()} (UTC)", ylabel="Temperature (°C)")
locator = mdates.AutoDateLocator(minticks=4, maxticks=7)
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
ax.legend(fontsize=8)
plt.tight_layout()
plt.show()
''')
md('''## 7. Seasonal errors and uncertainty limitations

The combined model has the lowest test RMSE/MAE at both horizons, but its
seven-day RMSE advantage over seasonal regression is only about **0.015°C**.
Validation slightly favored seasonal regression at seven days. We do not claim
statistical significance from this descriptive comparison.

One-day interval coverage is **93.7%**, below nominal 95%; seven-day coverage is
**95.6%**. Refitted combined residuals pass the two Ljung–Box checks, but reject
normality and show evidence of changing conditional variance. Gaussian intervals
omit parameter uncertainty. We report these limitations without retuning on 2024.
Winter is particularly difficult. One station, one test year, and dependent
overlapping seven-day errors limit generalization.
''')
code('''display(Image(filename=str(ROOT / "reports/test/test_errors_by_season.png")))
display(pd.read_json(ROOT / "reports/test/refit_diagnostics.json"))
''')
md('''## 8. Verification and references

The protocol tests check phase continuity across leap days, exact horizon
alignment, frozen parameters, and that altering future observations cannot
change earlier forecasts. File hashes link results to data and analysis code.

- [NOAA GSOD data](https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/)
- [NOAA field documentation](https://www.ncei.noaa.gov/data/global-summary-of-the-day/doc/readme.txt)
- [Dynamic harmonic regression, Forecasting: Principles and Practice](https://otexts.com/fpp3/dhr.html)
- [statsmodels state updates](https://www.statsmodels.org/v0.14.6/generated/statsmodels.tsa.statespace.sarimax.SARIMAXResults.extend.html)

The paper, presentation, and GitHub publication remain separate deliverables.
''')
code('''hashes = json.loads((ROOT / "reports/test/reproduction_hashes.json").read_text())
for relative, expected in hashes.items():
    assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected, relative
subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "scripts", "-p", "test_forecasting.py"],
               cwd=ROOT, check=True)
print("Hashes and forecasting protocol tests passed.")
''')

notebook = {'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},
              'language_info':{'name':'python','version':'3.13'}},'nbformat':4,'nbformat_minor':5}
for i, cell in enumerate(cells):
    cell['id'] = f'demo-{i:02}'
folder = ROOT/'notebooks'
folder.mkdir(exist_ok=True)
(folder/'temperature_forecasting_demo.ipynb').write_text(json.dumps(notebook,indent=1),encoding='utf-8')
print('Built demo notebook:', len(cells), 'cells')
