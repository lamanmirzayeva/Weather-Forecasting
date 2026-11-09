"""Create readable validation results and figures from completed experiments."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from validate_models import fourier

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'reports/validation'


def main():
    scores = pd.read_csv(OUT/'selected_metrics.csv')
    selected = pd.read_csv(OUT/'selected_models.csv')
    label = selected.loc[selected.family.eq('combined'), 'model'].iloc[0]
    forecasts = pd.read_csv(OUT/f'{label}.csv', parse_dates=['origin','target'])
    meta = json.loads((OUT/f'{label}.json').read_text())
    train = pd.read_csv(ROOT/'data/processed/72785794129_daily.csv', parse_dates=['date'])
    train = train.set_index('date').temperature_c.loc[:'2022-12-31'].asfreq('D')
    x = fourier(train.index, meta['k'])
    if meta['d']:
        x = x[:, 1:]
    fitted = SARIMAX(train.to_numpy(), exog=x, order=(meta['p'],meta['d'],meta['q'])).filter(meta['params'])
    resid = pd.Series(fitted.filter_results.standardized_forecasts_error[0], index=train.index)
    resid.iloc[:30] = np.nan
    resid.loc[train.isna()] = np.nan
    segment = max((g.dropna() for _,g in resid.groupby(resid.isna().cumsum())), key=len)
    fig, axes = plt.subplots(1, 2, figsize=(10,4), layout='constrained')
    plot_acf(segment, lags=40, ax=axes[0], zero=False)
    plot_pacf(segment, lags=40, ax=axes[1], zero=False, method='ywm')
    fig.suptitle('Selected combined model: continuous training residual segment')
    fig.savefig(OUT/'training_residual_acf_pacf.png', dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(10,4), layout='constrained')
    for ax, metric in zip(axes, ['rmse','mae']):
        scores.pivot(index='family', columns='horizon', values=metric).plot.bar(ax=ax, rot=20)
        ax.set_ylabel(f'{metric.upper()} (Celsius)')
        ax.set_xlabel('')
        ax.legend(title='Horizon (days)')
        ax.set_title('2023 validation')
    fig.savefig(OUT/'validation_accuracy.png', dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(2, 1, figsize=(11,6), layout='constrained')
    for ax, h in zip(axes, [1,7]):
        g = forecasts[forecasts.horizon.eq(h)].set_index('target').loc['2023-01-01':'2023-03-31']
        ax.fill_between(g.index, g.lower, g.upper, alpha=.22, label='95% prediction interval')
        ax.plot(g.index, g.actual, color='black', linewidth=1, label='Observed')
        ax.plot(g.index, g.prediction, linewidth=1, label='Forecast')
        ax.set_title(f'{h}-day horizon, selected combined model; first validation quarter')
        ax.set_ylabel('Temperature (Celsius)')
        ax.legend(loc='upper left', fontsize=8, ncol=3)
    fig.savefig(OUT/'validation_forecasts.png', dpi=160)
    plt.close(fig)
    lines = ['# 2023 validation results', '',
             'All parameters were fitted on 2019–2022. Forecast origins advance daily,',
             'updating states without refitting. No 2024 values enter these experiments.', '',
             'One specification per family was selected by the equal-weight mean of',
             'one-day and seven-day validation RMSE, excluding nonconverged fits.',
             'Ties follow deterministic grid order. This is a documented implementation',
             'choice where the proposal does not prescribe a cross-horizon rule.', '',
             'Origins start at 2022-12-31. Targets remain within 2023: 365 one-day',
             'and 359 seven-day targets, identical across models. Seven-day targets',
             'begin January 7. Forecasts use completed UTC-day observations and assume',
             'those observations are available at the origin; archive publication delays',
             'are not modeled.', '',
             '## Selected model accuracy', '',
             '| Family | Specification | Horizon | N | RMSE (C) | MAE (C) |',
             '|---|---|---:|---:|---:|---:|']
    for r in scores.itertuples():
        lines.append(f'| {r.family} | {r.model} | {r.horizon} | {r.n} | {r.rmse:.3f} | {r.mae:.3f} |')
    lines += ['', '## Combined model intervals', '',
              '| Horizon | Empirical coverage | Mean width (C) |', '|---:|---:|---:|']
    for r in scores[scores.family.eq('combined')].itertuples():
        lines.append(f'| {r.horizon} | {100*r.coverage:.1f}% | {r.mean_width:.3f} |')
    lines += ['', 'Intervals are conditional on fitted parameter estimates and do not include',
              'parameter uncertainty. Overlapping seven-day forecast errors are dependent.', '',
              '## Training diagnostics', '',
              'ADF tests reject a unit root in each Fourier-regression residual series;',
              'KPSS does not reject level stationarity (reported p-value is bounded at 0.1).',
              'Therefore combined models use d=0; d=1 is not justified by these diagnostics.',
              'The nonseasonal ARIMA comparison searches d=0 and d=1 to allow annual',
              'variation to be represented without Fourier terms.', '',
              f'Selected combined-model Ljung–Box p-values: {meta["ljung_box_p"]}.',
              'These use the longest continuous training residual segment after a 30-day',
              'burn-in, so the missing day is never treated as an adjacent observation.',
              'Degrees of freedom are adjusted for p+q. These are diagnostic checks,',
              'not a guarantee of independent or normally distributed forecast errors.', '',
              '## Reproduce', '', '```powershell',
              'python scripts/validate_models.py', 'python scripts/summarize_validation.py',
              'python -m unittest discover -s scripts -p test_forecasting.py', '```', '',
              'Candidate-level forecasts, fitted parameters, convergence status, warnings,',
              'and metrics are saved alongside this report. Cached candidates are reused.',
              'If changing modeling code or inputs, use a fresh validation output directory.', '',
              'ACF/PACF plots use the same continuous training segment. Next: review',
              'remaining diagnostics, then refit selected models',
              'on 2019–2023 and evaluate the frozen protocol on 2024. Validation scores',
              'are selection results and must not be described as held-out test performance.', '',
              'API reference: https://www.statsmodels.org/v0.14.6/generated/statsmodels.tsa.statespace.sarimax.SARIMAXResults.get_prediction.html']
    (OUT/'results.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
