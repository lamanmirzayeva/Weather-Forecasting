"""Chronological validation only: no fitting or selection uses 2024."""
from pathlib import Path
import json
import warnings
import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.stats.diagnostic import acorr_ljungbox

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports' / 'validation'


def fourier(dates, k):
    """Fixed calendar origin so gaps, leap days, and splits preserve phase."""
    t = (pd.DatetimeIndex(dates) - pd.Timestamp('2019-01-01')).days.to_numpy()
    cols = [np.ones(len(t))]
    for j in range(1, k + 1):
        cols.extend([np.sin(2*np.pi*j*t/365.25), np.cos(2*np.pi*j*t/365.25)])
    return np.column_stack(cols)


def rolling(result, y, x, start):
    """Forecast before revealing each new target; update states, never parameters."""
    rows = []
    state = result
    for i in range(start, len(y)):
        steps = min(7, len(y)-i)
        args = {'exog': x[i:i+steps]} if x is not None else {}
        fc = state.get_forecast(steps=steps, **args)
        mean = np.asarray(fc.predicted_mean)
        ci = np.asarray(fc.conf_int(alpha=.05))
        for h in (1, 7):
            if h <= steps:
                rows.append({'origin': y.index[i-1], 'target': y.index[i+h-1],
                             'horizon': h, 'actual': y.iloc[i+h-1],
                             'prediction': mean[h-1], 'lower': ci[h-1, 0],
                             'upper': ci[h-1, 1]})
        args = {'exog': x[i:i+1]} if x is not None else {}
        state = state.extend(y.iloc[i:i+1].to_numpy(), **args)
    return pd.DataFrame(rows)


def metrics(frame):
    rows = []
    for h, g in frame.groupby('horizon'):
        g = g.dropna(subset=['actual', 'prediction'])
        error = g.prediction-g.actual
        intervals = g.dropna(subset=['lower', 'upper'])
        rows.append({'horizon': int(h), 'n': len(g),
                     'rmse': float(np.sqrt(np.mean(error**2))),
                     'mae': float(np.mean(np.abs(error))),
                     'coverage': float(((intervals.actual >= intervals.lower) &
                                        (intervals.actual <= intervals.upper)).mean()),
                     'mean_width': float((intervals.upper-intervals.lower).mean())})
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(ROOT/'data/processed/72785794129_daily.csv', parse_dates=['date'])
    # Truncate immediately; test observations never enter the experiment.
    y = data.set_index('date').temperature_c.loc[:'2023-12-31'].asfreq('D')
    n = len(y.loc[:'2022-12-31'])
    train = y.iloc[:n]
    diagnostics = []
    for k in (1, 2, 3):
        x = fourier(train.index, k)
        valid = train.notna().to_numpy()
        coef = np.linalg.lstsq(x[valid], train.to_numpy()[valid], rcond=None)[0]
        residual = train.to_numpy()[valid]-x[valid]@coef
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            diagnostics.append({'k': k, 'adf_p': float(adfuller(residual)[1]),
                                'kpss_p': float(kpss(residual, regression='c', nlags='auto')[1])})
    (OUT/'stationarity.json').write_text(json.dumps(diagnostics, indent=2))
    # d=1 is considered only for seasonal residuals with evidence from BOTH tests.
    integrated_k = {r['k'] for r in diagnostics if r['adf_p'] > .05 and r['kpss_p'] < .05}
    specs = [('seasonal', k, 0, 0, 0) for k in (1, 2, 3)]
    specs += [('arima', 0, p, d, q) for d in (0, 1) for p in range(4) for q in range(4)]
    specs += [('combined', k, p, d, q) for k in (1, 2, 3)
              for d in ([0, 1] if k in integrated_k else [0])
              for p in range(4) for q in range(4)]
    scores, fits = [], []
    for family, k, p, d, q in specs:
        label = f'{family}_K{k}_{p}{d}{q}'
        cache = OUT/f'{label}.csv'
        meta_path = OUT/f'{label}.json'
        if cache.exists() and meta_path.exists():
            meta = json.loads(meta_path.read_text())
            frame = pd.read_csv(cache)
        else:
            x = fourier(y.index, k) if k else None
            if x is not None and d:
                x = x[:, 1:]
            try:
                model = SARIMAX(train.to_numpy(), exog=x[:n] if x is not None else None,
                                order=(p,d,q), trend='c' if not k and d==0 else 'n',
                                enforce_stationarity=True, enforce_invertibility=True)
                with warnings.catch_warnings(record=True) as caught:
                    result = model.fit(disp=False, maxiter=300)
                    if not result.mle_retvals['converged']:
                        result = model.fit(start_params=result.params, method='powell',
                                           disp=False, maxiter=300)
                        result = model.fit(start_params=result.params, disp=False, maxiter=300)
                meta = {'model': label, 'family': family, 'k': k, 'p': p, 'd': d, 'q': q,
                        'converged': bool(result.mle_retvals['converged']),
                        'aic': float(result.aic), 'params': result.params.tolist(),
                        'warnings': list(dict.fromkeys(str(w.message) for w in caught))}
                # Keep original calendar for residual diagnostics: never close the missing gap.
                resid = np.asarray(result.filter_results.standardized_forecasts_error[0])
                resid[:max(30, result.loglikelihood_burn)] = np.nan
                resid[train.isna().to_numpy()] = np.nan
                # Longest continuous observed segment avoids artificial adjacent residuals.
                segments = pd.Series(resid).groupby(pd.Series(np.isnan(resid)).cumsum())
                segment = max((g.dropna() for _, g in segments), key=len)
                lb = acorr_ljungbox(segment, lags=[14, 30], model_df=p+q, return_df=True)
                meta['ljung_box_p'] = {str(i): float(v) for i,v in lb.lb_pvalue.items()}
                frame = rolling(result, y, x, n)
                frame.to_csv(cache, index=False)
                meta_path.write_text(json.dumps(meta, indent=2))
            except (ValueError, np.linalg.LinAlgError) as exc:
                print(label, 'FAILED', exc, flush=True)
                fits.append({'model': label, 'converged': False, 'error': str(exc)})
                continue
        fits.append(meta)
        for row in metrics(frame):
            scores.append({'model': label, 'family': family, 'k': k, 'p': p, 'd': d, 'q': q,
                           'converged': meta['converged'], **row})
        print(label, 'converged='+str(meta['converged']), flush=True)
        pd.DataFrame(scores).to_csv(OUT/'candidate_metrics.csv', index=False)
    # Persistence uses exactly the same origins and target dates as other models.
    frame = frame.copy()
    frame['prediction'] = [y.loc[pd.Timestamp(t)] for t in frame.origin]
    frame[['lower','upper']] = np.nan
    frame.to_csv(OUT/'persistence.csv', index=False)
    for row in metrics(frame):
        row['coverage'] = np.nan
        scores.append({'model': 'persistence', 'family': 'persistence', 'converged': True, **row})
    scores = pd.DataFrame(scores)
    scores.to_csv(OUT/'candidate_metrics.csv', index=False)
    (OUT/'fit_diagnostics.json').write_text(json.dumps(fits, indent=2))
    # One specification per family, selected by equal-weight average RMSE of both horizons.
    eligible = scores[scores.converged].groupby(['family','model']).rmse.mean().reset_index()
    selected = eligible.loc[eligible.groupby('family').rmse.idxmin()].copy()
    selected.rename(columns={'rmse': 'mean_validation_rmse'}, inplace=True)
    selected.to_csv(OUT/'selected_models.csv', index=False)
    summary = scores[scores.model.isin(selected.model)]
    summary.to_csv(OUT/'selected_metrics.csv', index=False)
    print(summary[['family','model','horizon','n','rmse','mae','coverage','mean_width']].to_string(index=False))


if __name__ == '__main__':
    main()
