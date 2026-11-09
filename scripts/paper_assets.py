"""Generate publication-sized vector figures and tables from saved experiments."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import json
from validate_models import fourier

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'paper/figures'
OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.size':8,'axes.titlesize':9,'axes.labelsize':8,
                     'legend.fontsize':7,'xtick.labelsize':7,'ytick.labelsize':7})
names = {'arima':'ARIMA','combined':'Combined','persistence':'Persistence','seasonal':'Seasonal'}
data = pd.read_csv(ROOT/'data/processed/72785794129_daily.csv',parse_dates=['date'])
y = data.set_index('date').temperature_c.asfreq('D')
fig,ax=plt.subplots(figsize=(5.5,1.9),layout='constrained')
ax.plot(y.index,y,lw=.35)
ax.axvspan(pd.Timestamp('2023-01-01'),pd.Timestamp('2024-01-01'),alpha=.18,color='orange',label='Validation')
ax.axvspan(pd.Timestamp('2024-01-01'),pd.Timestamp('2025-01-01'),alpha=.12,color='green',label='Test')
ax.set(ylabel='Daily mean (°C)',xlabel='UTC date')
ax.legend(loc='upper left',ncol=2)
fig.savefig(OUT/'data.pdf'); plt.close(fig)

train=y.loc[:'2022-12-31']
meta=json.loads((ROOT/'reports/validation/combined_K3_101.json').read_text())
fit=SARIMAX(train.to_numpy(),exog=fourier(train.index,3),order=(1,0,1)).filter(meta['params'])
res=pd.Series(fit.filter_results.standardized_forecasts_error[0],index=train.index)
res.iloc[:30]=np.nan; res.loc[train.isna()]=np.nan
segment=max((g.dropna() for _,g in res.groupby(res.isna().cumsum())),key=len)
fig,axes=plt.subplots(1,2,figsize=(5.5,1.8),layout='constrained')
plot_acf(segment,lags=30,ax=axes[0],zero=False)
plot_pacf(segment,lags=30,ax=axes[1],zero=False,method='ywm')
for ax in axes: ax.set_ylim(-.15,.15); ax.set_xlabel('Lag (days)')
fig.savefig(OUT/'acf.pdf'); plt.close(fig)

scores=pd.read_csv(ROOT/'reports/test/test_metrics.csv')
fig,ax=plt.subplots(figsize=(5.5,2),layout='constrained')
pivot=scores.pivot(index='family',columns='horizon',values='rmse').reindex(['persistence','seasonal','arima','combined'])
pivot.index=[names[n] for n in pivot.index]
pivot.plot.bar(ax=ax,rot=0,color=['#336b9d','#cb7c35'])
ax.set(ylabel='Test RMSE (°C)',xlabel=''); ax.legend(title='Horizon (days)',ncol=2)
fig.savefig(OUT/'accuracy.pdf'); plt.close(fig)

f=pd.read_csv(ROOT/'reports/test/combined_K3_101.csv',parse_dates=['origin','target'])
fig,axes=plt.subplots(2,1,figsize=(5.5,3.6),layout='constrained',sharex=True)
for ax,h in zip(axes,[1,7]):
    g=f[f.horizon.eq(h)]
    ax.fill_between(g.target,g.lower,g.upper,alpha=.25,label='95% interval')
    ax.plot(g.target,g.actual,color='black',lw=.5,label='Observed')
    ax.plot(g.target,g.prediction,lw=.6,label='Forecast')
    ax.set(title=f'{h}-day horizon',ylabel='Temperature (°C)')
    ax.legend(ncol=3,loc='upper right')
axes[-1].set_xlabel('Target date, 2024')
fig.savefig(OUT/'forecasts.pdf'); plt.close(fig)

seasons=pd.read_csv(ROOT/'reports/test/seasonal_metrics.csv')
fig,axes=plt.subplots(1,2,figsize=(5.5,2.2),layout='constrained',sharey=True)
for ax,h in zip(axes,[1,7]):
    for model,label in [('persistence','Persistence'),('seasonal_K3_000','Seasonal'),('arima_K0_303','ARIMA'),('combined_K3_101','Combined')]:
        g=seasons[(seasons.horizon==h)&(seasons.model==model)].set_index('season').reindex(['DJF','MAM','JJA','SON'])
        ax.plot(g.index,g.rmse,'o-',ms=3,lw=.8,label=label)
    ax.set(title=f'{h}-day horizon',xlabel='Target-date season')
axes[0].set_ylabel('Test RMSE (°C)'); axes[-1].legend(fontsize=6)
fig.savefig(OUT/'seasons.pdf'); plt.close(fig)
print('Created five vector figures in paper/figures')
