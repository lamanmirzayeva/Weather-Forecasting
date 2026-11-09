"""Prepare exact experiment data for editable PGFPlots figures in the Beamer deck."""
from pathlib import Path
import shutil
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent/'assets'
OUT.mkdir(exist_ok=True)
y = pd.read_csv(ROOT/'data/processed/72785794129_daily.csv',parse_dates=['date']).set_index('date').temperature_c
monthly = y.resample('MS').mean().reset_index()
monthly['month'] = range(len(monthly))
monthly[['month','temperature_c']].to_csv(OUT/'monthly_temperature.csv',index=False)
scores = pd.read_csv(ROOT/'reports/test/test_metrics.csv')
names = ['persistence','seasonal','arima','combined']
pd.DataFrame({'model':range(4),
              'one_day':[scores[(scores.family==m)&(scores.horizon==1)].rmse.iloc[0] for m in names],
              'seven_day':[scores[(scores.family==m)&(scores.horizon==7)].rmse.iloc[0] for m in names]}).to_csv(OUT/'test_rmse.csv',index=False)
seasons = pd.read_csv(ROOT/'reports/test/seasonal_metrics.csv')
order = ['DJF','MAM','JJA','SON']
pd.DataFrame({'season':range(4),
              'one_day':[seasons[(seasons.model=='combined_K3_101')&(seasons.season==s)&(seasons.horizon==1)].rmse.iloc[0] for s in order],
              'seven_day':[seasons[(seasons.model=='combined_K3_101')&(seasons.season==s)&(seasons.horizon==7)].rmse.iloc[0] for s in order]}).to_csv(OUT/'seasonal_rmse.csv',index=False)
shutil.copy2(ROOT/'reports/notebook_preview.png',OUT/'demo_forecast.png')
print('Prepared plot data and the existing notebook forecast figure.')
