"""Refit validation-selected specifications and evaluate frozen 2024 forecasts."""
import hashlib
import json
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
from scipy.stats import jarque_bera
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
from statsmodels.tsa.statespace.sarimax import SARIMAX
from validate_models import fourier, rolling, metrics

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'reports/test'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    source = ROOT/'reports/validation/selected_models.csv'
    selections = pd.read_csv(source)
    specs = []
    for row in selections.itertuples():
        if row.family != 'persistence':
            meta = json.loads((ROOT/f'reports/validation/{row.model}.json').read_text())
            specs.append({key: meta[key] for key in ['model','family','k','p','d','q']})
    protocol = {'selection_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'fit_end': '2023-12-31', 'test_start': '2024-01-01', 'test_end': '2024-12-31',
                'specifications': specs, 'horizons': [1,7], 'refit_during_test': False,
                'origin_start': '2023-12-31', 'interval_alpha': .05}
    protocol_path = OUT/'frozen_protocol.json'
    if protocol_path.exists() and json.loads(protocol_path.read_text()) != protocol:
        raise ValueError('Frozen protocol changed; do not retune against test results')
    protocol_path.write_text(json.dumps(protocol, indent=2))
    y = pd.read_csv(ROOT/'data/processed/72785794129_daily.csv', parse_dates=['date'])
    y = y.set_index('date').temperature_c.asfreq('D')
    n = len(y.loc[:'2023-12-31'])
    train = y.iloc[:n]
    frames, summary, diagnostics = {}, [], []
    for spec in specs:
        label = spec['model']
        x = fourier(y.index, spec['k']) if spec['k'] else None
        if x is not None and spec['d']:
            x = x[:,1:]
        model = SARIMAX(train.to_numpy(), exog=x[:n] if x is not None else None,
                        order=(spec['p'],spec['d'],spec['q']),
                        trend='c' if spec['k']==0 and spec['d']==0 else 'n',
                        enforce_stationarity=True, enforce_invertibility=True)
        fit_path = OUT/f'{label}_fit.json'
        if fit_path.exists():
            meta = json.loads(fit_path.read_text())
            result = model.filter(meta['params'])
        else:
            with warnings.catch_warnings(record=True) as caught:
                result = model.fit(disp=False, maxiter=300)
                if not result.mle_retvals['converged']:
                    result = model.fit(start_params=result.params, method='powell', disp=False, maxiter=300)
                    result = model.fit(start_params=result.params, disp=False, maxiter=300)
            if not result.mle_retvals['converged']:
                raise RuntimeError(f'{label}: refit failed; stop before test evaluation')
            meta = {**spec, 'converged': True, 'params': result.params.tolist(),
                    'param_names': result.param_names, 'aic': float(result.aic),
                    'warnings': [str(w.message) for w in caught]}
            fit_path.write_text(json.dumps(meta, indent=2))
        residual = pd.Series(result.filter_results.standardized_forecasts_error[0])
        residual.iloc[:30] = np.nan
        residual.loc[train.isna().to_numpy()] = np.nan
        segment = max((g.dropna() for _,g in residual.groupby(residual.isna().cumsum())), key=len)
        diagnostics.append({'model': label, 'continuous_segment_n': len(segment),
            'ljung_box_p': acorr_ljungbox(segment, lags=[14,30], model_df=spec['p']+spec['q']).lb_pvalue.to_dict(),
            'jarque_bera_p': float(jarque_bera(segment).pvalue),
            'arch_lm_p': float(het_arch(segment, nlags=14, ddof=spec['p']+spec['q'])[1])})
        path = OUT/f'{label}.csv'
        if path.exists():
            frame = pd.read_csv(path, parse_dates=['origin','target'])
        else:
            frame = rolling(result, y, x, n)
            frame.to_csv(path, index=False)
        frames[label] = frame
        for row in metrics(frame):
            summary.append({**spec, **row})
        print(label, 'complete', flush=True)
    frame = frame.copy()
    frame['prediction'] = [y.loc[pd.Timestamp(t)] for t in frame.origin]
    frame[['lower','upper']] = np.nan
    frame.to_csv(OUT/'persistence.csv', index=False)
    frames['persistence'] = frame
    for row in metrics(frame):
        row['coverage'] = np.nan
        summary.append({'model': 'persistence', 'family': 'persistence', **row})
    ref = frame[['origin','target','horizon','actual']]
    assert all(f[['origin','target','horizon','actual']].equals(ref) for f in frames.values())
    assert frame.groupby('horizon').size().to_dict() == {1:366,7:360}
    assert ((frame.target-frame.origin).dt.days == frame.horizon).all()
    seasonal = []
    for label, f in frames.items():
        f = f.copy()
        f['season'] = f.target.dt.month.map({12:'DJF',1:'DJF',2:'DJF',3:'MAM',4:'MAM',5:'MAM',6:'JJA',7:'JJA',8:'JJA',9:'SON',10:'SON',11:'SON'})
        for season, g in f.groupby('season'):
            for row in metrics(g):
                seasonal.append({'model':label,'season':season,**row})
    pd.DataFrame(seasonal).to_csv(OUT/'seasonal_metrics.csv', index=False)
    (OUT/'refit_diagnostics.json').write_text(json.dumps(diagnostics, indent=2))
    summary = pd.DataFrame(summary)
    summary.to_csv(OUT/'test_metrics.csv', index=False)
    print(summary[['family','horizon','n','rmse','mae','coverage','mean_width']].to_string(index=False))


if __name__ == '__main__':
    main()
