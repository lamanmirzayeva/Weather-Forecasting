# NOAA GSOD data audit

## Station decision

Use **Pullman/Moscow Regional Airport**, NOAA GSOD station **72785794129**
(USAF 727857, WBAN 94129; ICAO KPUW). Official station metadata lists coordinates
46.744 N, 117.116 W and elevation 775.7 m. This is the proposal's preferred location.

Pullman has 2,191 observed temperatures in the 2,192-day calendar for 2019–2024
(99.954% coverage). The only missing day is **2021-12-31**. Retain that day as
missing for state-space estimation. There are no duplicate dates, 9999.9 temperature
sentinels, or nonpositive temperature observation counts in the downloaded records.

| Split | Calendar dates | Calendar days | Observed temperatures |
|---|---|---:|---:|
| Training | 2019-01-01 through 2022-12-31 | 1,461 | 1,460 |
| Validation | 2023-01-01 through 2023-12-31 | 365 | 365 |
| Test | 2024-01-01 through 2024-12-31 | 366 | 366 |

Spokane International Airport (72785024157) was audited as the planned backup and
has complete coverage. Pullman's coverage is adequate; no switch is needed.
This choice uses data availability only, not held-out forecast accuracy.

## Preparation and checks

- Retained original station-year CSVs and recorded source URLs and SHA-256 hashes.
- Verified station identity and checked duplicate dates before calendar reindexing.
- Converted Fahrenheit to Celsius using `(TEMP - 32) * 5 / 9`.
- Preserved all 2,192 calendar dates, including both leap days.
- Kept the missing observation unfilled; no smoothing or interpolation was used.
- Preserved TEMP_ATTRIBUTES observation counts and source variable attributes.
- Verified the calendar is unique, daily, and has the expected split sizes.
- Recorded installed analysis-library versions in `environment.txt`.

NOAA documentation identifies TEMP_ATTRIBUTES as the observation count used to
calculate the daily mean, not a quality flag. The raw input receives NOAA quality
control; the downloaded temperature field does not provide a separate quality flag.
GSOD daily summaries use GMT/UTC days, which should be stated in the paper.

## Reproduce

Run `python scripts/prepare_data.py` from the project root. Existing raw downloads
are reused. Inspect `station_coverage.csv`, `data_quality.json`, and
`download_manifest.json`. Processed data are in
`data/processed/72785794129_daily.csv`.

## Next stage

Implement Fourier calendar features and baselines, then rolling-origin validation.
Keep the 2024 values out of fitting and model selection. No forecast experiments
or accuracy results have been produced at this stage.

## Sources

- Station inventory: https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv
- GSOD files: https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/
- Field documentation: https://www.ncei.noaa.gov/data/global-summary-of-the-day/doc/readme.txt
