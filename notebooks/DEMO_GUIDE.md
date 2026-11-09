# Demo guide

Open `temperature_forecasting_demo.ipynb` in JupyterLab. Saved outputs are included;
to run cells, select the Python environment containing `requirements.txt` packages.
Run the data preparation script first on a fresh checkout.

## Suggested 3-minute walkthrough

1. **Question and data (30 seconds):** Explain the one-station forecasting task.
   Show calendar splits and the single missing training day. No interpolation.
2. **Method (30 seconds):** Fourier terms represent annual seasonality. ARMA
   errors represent short-term deviations. Validation selected K=3, ARMA(1,1).
3. **Evaluation (40 seconds):** Show the frozen test table. Parameters are fitted
   through 2023; daily state updates use only observations available at the origin.
   The seven-day advantage over seasonal regression is small.
4. **Forecast demonstration (50 seconds):** Change `ORIGIN` in section 6 and run
   its two cells. The forecast uses only history through that date and matches
   the saved rolling evaluation. Future observations are displayed afterward.
5. **Limitations (30 seconds):** One-day interval coverage falls below 95%.
   Residuals are not normal and show changing variance. Results concern one
   station and one test year; no statistical significance claim is made.

## Before presenting

- Keep `RUN_PIPELINE=False` for the short demo; do the full analysis beforehand.
- Use an origin from 2023-12-31 through 2024-12-24; later dates lack all seven
  observed future targets within the dataset.
- Leave model orders and fitted parameters unchanged after the test evaluation.
- Open the executed notebook in advance and verify the selected kernel.
- Saved outputs allow a walkthrough if the network is unavailable.

## Verification completed

The notebook executed all 10 code cells in order without errors. It reconstructs
one forecast from fixed parameters and causal history, checks its point forecasts
and intervals against saved results, verifies reproduction hashes, and runs the
two forecasting protocol tests. Tables and figures are embedded in the notebook.

Rebuild and execute from the repository root:

```powershell
python scripts/build_demo.py
python scripts/execute_demo.py
```

The execution script writes its kernel configuration beneath `.venv/`. Local
process and socket access are needed for Jupyter execution.
