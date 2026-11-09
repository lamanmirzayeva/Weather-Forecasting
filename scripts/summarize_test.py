"""Generate test tables and figures without changing fitted models."""
from pathlib import Path
import json
import hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'reports/test'


def main():
    scores = pd.read_csv(OUT/'test_metrics.csv')
    combined = pd.read_csv(OUT/'combined_K3_101.csv', parse_dates=['origin','target'])
    fig, axes = plt.subplots(1,2,figsize=(10,4),layout='constrained')
    for ax, metric in zip(axes,['rmse','mae']):
        scores.pivot(index='family',columns='horizon',values=metric).plot.bar(ax=ax,rot=20)
        ax.set_ylabel(f'{metric.upper()} (Celsius)')
        ax.set_xlabel('')
        ax.set_title('2024 held-out test')
        ax.legend(title='Horizon (days)')
    fig.savefig(OUT/'test_accuracy.png',dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(2,1,figsize=(12,7),layout='constrained')
    for ax,h in zip(axes,[1,7]):
        g = combined[combined.horizon.eq(h)]
        ax.fill_between(g.target,g.lower,g.upper,alpha=.25,label='95% prediction interval')
        ax.plot(g.target,g.actual,color='black',linewidth=.8,label='Observed')
        ax.plot(g.target,g.prediction,linewidth=.8,label='Forecast')
        ax.set_title(f'Combined model: {h}-day forecasts, 2024')
        ax.set_ylabel('Temperature (Celsius)')
        ax.legend(ncol=3,fontsize=8)
    fig.savefig(OUT/'test_forecasts.png',dpi=160)
    plt.close(fig)
    seasonal = pd.read_csv(OUT/'seasonal_metrics.csv')
    fig, axes = plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for ax,h in zip(axes,[1,7]):
        seasonal[seasonal.horizon.eq(h)].pivot(index='season',columns='model',values='rmse').reindex(['DJF','MAM','JJA','SON']).plot.bar(ax=ax,rot=0)
        ax.set_title(f'{h}-day horizon, 2024')
        ax.set_ylabel('RMSE (Celsius)')
        ax.set_xlabel('Target-date season')
        ax.legend(fontsize=7)
    fig.savefig(OUT/'test_errors_by_season.png',dpi=160)
    plt.close(fig)
    lines = ['# 2024 held-out test results','','## Protocol','',
        'Model orders were selected using 2023 validation and frozen before this test.',
        'Each model was refitted once on 2019–2023, including the missing training day',
        'as an unobserved state-space observation. Parameters remain fixed throughout',
        '2024. States update only after forecasts are issued, using newly available',
        'daily observations. No model choice or interval adjustment uses test results.', '',
        'The first origin is December 31, 2023. There are 366 one-day and 360',
        'seven-day forecasts, with identical origins/targets across models. Seven-day',
        'targets begin January 7, 2024. The unit is degrees Celsius; days are UTC.', '',
        '## Accuracy','','| Model | Horizon | N | RMSE (C) | MAE (C) |',
        '|---|---:|---:|---:|---:|']
    for r in scores.itertuples():
        lines.append(f'| {r.family} | {r.horizon} | {r.n} | {r.rmse:.3f} | {r.mae:.3f} |')
    lines += ['','## Combined-model intervals','','| Horizon | Coverage | Mean width (C) |',
              '|---:|---:|---:|']
    for r in scores[scores.family.eq('combined')].itertuples():
        lines.append(f'| {r.horizon} | {100*r.coverage:.1f}% | {r.mean_width:.3f} |')
    lines += ['','## Interpretation and limits','',
        'The combined model has the lowest RMSE and MAE at both test horizons.',
        'At seven days its improvement over seasonal regression is small (about',
        '0.015 C RMSE), so the evidence mainly favors short-term error modeling for',
        'one-day forecasts. The ranking at seven days differs slightly from validation.',
        'These are descriptive comparisons; statistical significance is not established.', '',
        'One-day interval coverage is below the nominal 95%; seven-day coverage is',
        'slightly above nominal. Gaussian intervals condition on fitted parameters and',
        'omit parameter uncertainty. Training residual diagnostics are recorded in',
        '`refit_diagnostics.json`; passing a dependence check does not establish',
        'normality, constant variance, or adequate coverage for every season.', '',
        'For the refitted combined model, Ljung–Box p-values are 0.459 at lag 14',
        'and 0.158 at lag 30. Jarque–Bera rejects normality (p about 5.1e-13),',
        'and the ARCH LM check indicates changing conditional variance (p=0.025).',
        'These diagnostic limitations are reported without changing the frozen model.', '',
        'This study uses one station and one test year. Seven-day errors overlap and',
        'are dependent. Daily data are treated as available after each UTC day closes;',
        'actual NOAA publication delays are not simulated. Seasonal tables describe',
        'target-date seasons, with DJF combining January/February and December.', '',
        '## Reproduce','','```powershell','python scripts/evaluate_test.py',
        'python scripts/summarize_test.py',
        'python -m unittest discover -s scripts -p test_forecasting.py','```','',
        'Existing refits and forecast files are reused for reproducibility. The frozen',
        'protocol rejects changes to selected specifications. Do not use this test',
        'to retune models. Tables and plots can be regenerated from saved forecasts.', '',
        'Forecast/state-update API documentation:',
        'https://www.statsmodels.org/v0.14.6/generated/statsmodels.tsa.statespace.sarimax.SARIMAXResults.extend.html','',
        'The project also includes an executed demo notebook, an academic paper,',
        'and a presentation. Repository:',
        'https://github.com/lamanmirzayeva/Weather-Forecasting.']
    (OUT/'results.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    paths = [ROOT/'data/processed/72785794129_daily.csv',
             ROOT/'scripts/validate_models.py', ROOT/'scripts/evaluate_test.py',
             OUT/'frozen_protocol.json', OUT/'test_metrics.csv']
    (OUT/'reproduction_hashes.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():
        hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2))


if __name__ == '__main__':
    main()
