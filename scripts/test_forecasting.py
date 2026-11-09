"""Protocol checks: calendar phase, exact horizons, and no future leakage."""
import unittest
import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from validate_models import fourier, rolling, metrics


class ForecastProtocolTests(unittest.TestCase):
    def test_calendar_phase_across_leap_day_and_split(self):
        dates = pd.date_range('2020-02-27', periods=5)
        np.testing.assert_allclose(fourier(dates, 3)[2:], fourier(dates[2:], 3))
        self.assertEqual(fourier(dates, 3).shape, (5, 7))

    def test_forecast_precedes_observation(self):
        rng = np.random.default_rng(42)
        y = pd.Series(rng.normal(size=60), index=pd.date_range('2022-01-01', periods=60))
        y.iloc[15] = np.nan
        x = fourier(y.index, 1)
        result = SARIMAX(y.iloc[:50].to_numpy(), exog=x[:50], order=(1,0,0)).fit(disp=False)
        params = result.params.copy()
        first = rolling(result, y, x, 50)
        altered = y.copy()
        altered.iloc[50:] += 1000
        second = rolling(result, altered, x, 50)
        # Every forecast made at the initial origin must ignore all future observations.
        np.testing.assert_allclose(first.iloc[:2].prediction, second.iloc[:2].prediction)
        np.testing.assert_array_equal(params, result.params)
        offsets = (pd.to_datetime(first.target)-pd.to_datetime(first.origin)).dt.days
        np.testing.assert_array_equal(offsets, first.horizon)
        self.assertEqual(len(first[first.horizon == 1]), 10)
        self.assertEqual(len(first[first.horizon == 7]), 4)
        self.assertTrue((first.upper > first.lower).all())
        no_intervals = first.copy()
        no_intervals[['lower','upper']] = np.nan
        self.assertTrue(all(np.isnan(row['coverage']) for row in metrics(no_intervals)))


if __name__ == '__main__':
    unittest.main()
