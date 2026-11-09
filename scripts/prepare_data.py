"""Download and audit the proposal's NOAA GSOD candidate stations."""
from pathlib import Path
import hashlib
import io
import json
from datetime import datetime, timezone

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
OUT = ROOT / 'data' / 'processed'
REPORTS = ROOT / 'reports'
BASE = 'https://www.ncei.noaa.gov'
DATES = pd.date_range('2019-01-01', '2024-12-31', freq='D')


def download(session, url, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        response = session.get(url, timeout=(15, 90))
        response.raise_for_status()
        # Validate before caching: error HTML must never become a CSV input.
        frame = pd.read_csv(io.BytesIO(response.content), nrows=1)
        if not ({'USAF', 'WBAN'} <= set(frame.columns) or
                {'STATION', 'DATE', 'TEMP'} <= set(frame.columns)):
            raise ValueError(f'Unexpected CSV schema: {url}')
        path.write_bytes(response.content)
    return {'url': url, 'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def longest_gap(mask):
    groups = mask.ne(mask.shift()).cumsum()
    return int(mask.groupby(groups).sum().max())


def prepare_station(station, paths):
    raw = pd.concat([pd.read_csv(p, dtype={'STATION': str}) for p in paths],
                    ignore_index=True)
    if set(raw['STATION'].unique()) != {station}:
        raise ValueError(f'Station identity mismatch: {station}')
    raw['DATE'] = pd.to_datetime(raw['DATE'], errors='raise')
    duplicates = int(raw['DATE'].duplicated().sum())
    # Exact duplicates are safe to remove; conflicting observations need review.
    raw = raw.drop_duplicates()
    if raw['DATE'].duplicated().any():
        raise ValueError(f'Conflicting daily duplicates for {station}')
    raw = raw.set_index('DATE').sort_index().reindex(DATES)
    temp = pd.to_numeric(raw['TEMP'], errors='coerce')
    missing_sentinel = temp.eq(9999.9)
    count = pd.to_numeric(raw['TEMP_ATTRIBUTES'], errors='coerce')
    # TEMP_ATTRIBUTES is an observation count, not a temperature quality flag.
    # A supplied mean with zero contributing observations is invalid.
    invalid_count = temp.notna() & ~missing_sentinel & count.le(0)
    cleaned = temp.mask(missing_sentinel | invalid_count)
    out = pd.DataFrame({'temperature_c': (cleaned - 32) * 5 / 9,
                        'temperature_f_raw': temp,
                        'temperature_observation_count': count,
                        'missing_sentinel': missing_sentinel,
                        'invalid_observation_count': invalid_count}, index=DATES)
    out.index.name = 'date'
    out['split'] = ['train' if d.year <= 2022 else
                    'validation' if d.year == 2023 else 'test' for d in DATES]
    out.to_csv(OUT / f'{station}_daily.csv')
    rows = []
    for year, group in out.groupby(out.index.year):
        missing = group['temperature_c'].isna()
        rows.append({'station': station, 'year': int(year),
                     'expected_days': len(group), 'observed_days': int((~missing).sum()),
                     'missing_days': int(missing.sum()),
                     'coverage_percent': round(100 * (1 - missing.mean()), 3),
                     'longest_missing_run_days': longest_gap(missing)})
    return rows, {'station': station, 'duplicate_dates_in_raw': duplicates,
                  'missing_temperature_sentinels': int(missing_sentinel.sum()),
                  'invalid_observation_counts': int(invalid_count.sum()),
                  'missing_observation_counts_with_temperature': int((cleaned.notna() & count.isna()).sum()),
                  'attribute_columns': [c for c in raw.columns if 'ATTRIBUTES' in c],
                  'note': 'Retain other variable attributes in raw files; no imputation.'}


def main():
    for folder in (RAW, OUT, REPORTS):
        folder.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=Retry(
        total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])))
    manifest = [download(session, f'{BASE}/pub/data/noaa/isd-history.csv',
                         RAW / 'isd-history.csv')]
    history = pd.read_csv(RAW / 'isd-history.csv', dtype=str)
    candidates = history[history['STATION NAME'].str.contains(
        'PULLMAN|SPOKANE', case=False, na=False)]
    candidates.to_csv(REPORTS / 'station_candidates.csv', index=False)
    print(candidates.to_string(index=False), flush=True)
    # Identify using official metadata rather than guessing a station code.
    stations = []
    for pattern in ('PULLMAN', 'SPOKANE INTERNATIONAL'):
        matches = candidates[candidates['STATION NAME'].str.contains(pattern, na=False)]
        matches = matches[(matches['BEGIN'] <= '20190101') &
                          (matches['END'] >= '20241231')]
        if len(matches) != 1:
            raise ValueError(f'Expected one full-period station for {pattern}; review metadata')
        row = matches.iloc[0]
        stations.append(row['USAF'] + row['WBAN'])
    coverage, checks = [], []
    for station in stations:
        paths = []
        for year in range(2019, 2025):
            path = RAW / station / f'{year}.csv'
            print(f'Downloading/auditing {station} {year}', flush=True)
            manifest.append(download(session,
                f'{BASE}/data/global-summary-of-the-day/access/{year}/{station}.csv', path))
            paths.append(path)
        rows, check = prepare_station(station, paths)
        coverage.extend(rows)
        checks.append(check)
    pd.DataFrame(coverage).to_csv(REPORTS / 'station_coverage.csv', index=False)
    (REPORTS / 'data_quality.json').write_text(json.dumps(checks, indent=2))
    (REPORTS / 'download_manifest.json').write_text(json.dumps({
        'audit_time_utc': datetime.now(timezone.utc).isoformat(),
        'files': manifest}, indent=2))
    print(pd.DataFrame(coverage).to_string(index=False))


if __name__ == '__main__':
    main()
