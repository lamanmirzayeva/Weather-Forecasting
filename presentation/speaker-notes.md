# Slide 1

0:00–0:20, 20 seconds. Jiayu and Laman, CPTS 570. We study daily temperature at Pullman/Moscow Regional Airport. The question is whether annual seasonal regression and short-term ARMA dependence improve forecasts when combined. We evaluate the next day and seven days ahead. This is an empirical comparison of established statistical methods.

# Slide 2

0:20–1:00, 40 seconds. Temperature has an annual cycle, but consecutive days also share departures from the seasonal mean. We test whether these components offer complementary predictive information. We expect recent residuals to help especially at one day. At seven days, we test whether an advantage remains. We also examine uncertainty using interval coverage and width. These are predictive hypotheses, not statistical significance claims. Source: paper/main.tex.

# Slide 3

1:00–1:35, 35 seconds. Dynamic harmonic regression combines Fourier terms for long seasonality with ARMA errors. Hyndman and Khandakar motivate systematic ARIMA order selection. Our exhaustive bounded grid differs from their automatic stepwise approach. Taylor and Letham provide a related interpretable additive approach, but Prophet is not an evaluated baseline here. Our contribution is an audited station dataset and controlled horizon comparison. Sources: Hyndman and Athanasopoulos (2021), https://otexts.com/fpp3/dynamic-regression.html; Hyndman and Khandakar (2008), https://doi.org/10.18637/jss.v027.i03; Taylor and Letham (2018), https://doi.org/10.1080/00031305.2017.1380080.

# Slide 4

1:35–2:20, 45 seconds. We collected NOAA GSOD daily summaries for 2019 through 2024. Pullman has 2,191 observations on a 2,192-day calendar. Only December 31, 2021 is missing. It remains missing rather than interpolated. Spokane has complete coverage but is unnecessary as backup. We convert Fahrenheit to Celsius and preserve UTC dates and leap days. TEMP_ATTRIBUTES is an observation count rather than a quality flag. Source: reports/data_audit.md; NOAA field documentation, https://www.ncei.noaa.gov/data/global-summary-of-the-day/doc/readme.txt.

# Slide 5

2:20–3:20, 60 seconds. The model adds a seasonal mean to a correlated residual. Annual Fourier terms are known for every future date. K controls seasonal shape flexibility. We compute them from elapsed calendar days with period 365.25, preserving phase over missing observations. Residual ARMA dynamics use recent departures from the mean. We estimate the regression and error parameters jointly by maximum likelihood in statsmodels. Forecasts add the known future seasonal mean to a recursive residual forecast. Validation chooses three pairs with ARMA one-one errors. Training diagnostics do not justify differencing seasonal residuals. Sources: scripts/validate_models.py; https://www.statsmodels.org/v0.14.6/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html.

# Slide 6

3:20–4:15, 55 seconds. Fit initially on 2019 through 2022. Select one specification per family using the equal-weight average of one-day and seven-day validation RMSE in 2023. Refit through 2023 and freeze parameters for 2024. At each origin, issue both forecasts before revealing the next observation. Update only the latent state. Intervening observations never enter an earlier seven-day forecast. All models receive common targets. We assume summaries become available after each UTC day closes and do not simulate actual publication delays. Sources: reports/test/frozen_protocol.json and scripts/evaluate_test.py.

# Slide 7

4:15–4:55, 40 seconds. All 83 candidates converge. The combined grid searches K one through three and AR/MA orders zero through three. Seasonal regression selects K three, nonseasonal ARIMA selects three-zero-three, and the combined model selects K three with ARMA one-one. The table gives 2023 RMSE. The combined model is best at one day, but seasonal regression is marginally better at seven days. We keep this horizon distinction in the interpretation instead of claiming that residual modeling improves every forecast. Source: reports/validation/selected_metrics.csv.

# Slide 8

4:55–5:55, 60 seconds. The combined model has RMSE 2.405 Celsius at one day and 4.019 at seven days, and the lowest MAE at both horizons. Persistence gives RMSE 2.578 and 5.556. However, seasonal regression has seven-day RMSE 4.034. The combined gain is only about 0.015 Celsius, or 0.37 percent. Validation ranked those two in the opposite order. These descriptive comparisons do not establish statistical significance. The strongest evidence for residual modeling comes from one-day forecasting. Source: reports/test/test_metrics.csv.

# Slide 9

5:55–6:55, 60 seconds. These are prediction intervals for future temperatures rather than confidence intervals for a fitted mean. One-day coverage is 93.7 percent, below nominal 95. Seven-day coverage is 95.6 percent and the intervals are wider. They condition on fitted parameters and omit parameter uncertainty. Residual Ljung–Box checks do not reject at lags fourteen and thirty, but Jarque–Bera rejects normality and an ARCH test suggests changing variance. Point accuracy therefore does not guarantee calibrated uncertainty. We do not adjust intervals after inspecting the test. Sources: reports/test/test_metrics.csv and reports/test/refit_diagnostics.json.

# Slide 10

6:55–7:35, 40 seconds. Winter is the hardest season at both horizons. Combined seven-day winter RMSE reaches 5.616 Celsius, versus 2.977 in autumn. Winter interval coverage is only 87.1 percent despite annual coverage of 95.6 percent. DJF combines January and February with December 2024. Seven-day winter has eighty-five eligible targets. The January cold departure contributes to the difficulty but does not explain every winter error. Source: reports/test/seasonal_metrics.csv.

# Slide 11

7:35–9:20, 45 seconds of narration plus a 60-second live demo. Open notebook section six, keep RUN_PIPELINE false, and choose July first 2024 as ORIGIN. Run the forecast and plotting cells. The reconstruction loads frozen coefficients and filters only the history available through that date. It checks predictions and interval endpoints against saved rolling forecasts. Observed future values appear only after prediction for comparison. Comments, setup instructions, cached data, and protocol tests accompany the code. Use saved outputs if live execution is unavailable. Sources: notebooks/temperature_forecasting_demo.ipynb and notebooks/DEMO_GUIDE.md.

# Slide 12

9:20–10:00, 40 seconds after the demo. Short-term dependence helps the next-day forecast. Annual seasonality explains almost all seven-day performance. Interval evaluation reveals winter undercoverage. Future work should evaluate more stations and new years under a new validation protocol, and uncertainty models allowing changing variance or heavier tails. Meteorological predictors and realistic data-release timing would support a more operational comparison. We would test these extensions on new data rather than tune to 2024. Sources: paper/main.tex and reports/test/results.md.