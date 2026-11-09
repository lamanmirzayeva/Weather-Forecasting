# CPTS 570 submission handoff

Authors currently appear as **Jiayu and Laman**, matching the proposal.

## Deliverables

1. **Paper:** `output/pdf/CPTS570_Temperature_Forecasting_Academic_Revision.pdf`.
   Nine pages total, including references, using the supplied NeurIPS 2025 style.
   Editable source: `paper/main.tex`.
2. **Presentation:** `output/presentation/CPTS570_Temperature_Forecasting_Presentation.pptx`.
   Twelve slides with editable evidence and speaker notes. The plan allocates
   nine minutes to narration and one minute to the notebook demonstration.
3. **Python code and demo:** `scripts/` and
   `notebooks/temperature_forecasting_demo.ipynb`. Run instructions are in
   `README.md`; rehearsal guidance is in `notebooks/DEMO_GUIDE.md` and
   `presentation/speaker-notes.md`.

## Offline review

The submission ZIP includes processed temperatures and the original NOAA input
files used in this run. After extracting the archive, open a terminal in the
project folder and install the Python dependencies if necessary:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/verify_submission.py
python -m unittest discover -s scripts -p test_forecasting.py
python scripts/execute_demo.py
```

The notebook uses cached experiment outputs by default. Once dependencies are
installed, these checks and the default notebook need no data download.
Dependency installation requires network access. For macOS/Linux, activate with
`source .venv/bin/activate` instead. The recorded analysis environment is in
`reports/environment.txt`; requirements list supported version ranges.

To recompute metrics and figures from the frozen forecasts:

```powershell
python scripts/evaluate_test.py
python scripts/summarize_test.py
```

The saved models and forecasts are reused. Do not retune models against 2024.
`README.md` documents the full data/validation workflow. Paper compilation
requires a separate LaTeX installation and is not needed to execute the analysis.

## Review before submission

- Confirm whether references count within the instructor's nine-page limit.
  The provided proposal and screenshot do not resolve that detail.
- Confirm full author names and any required affiliation details. No additional
  author information has been inferred from computer or account metadata.
- Rehearse the presentation with both team members. Timings are a plan, not a
  measured human rehearsal or a guarantee of delivery time.
- Include the repository URL with the course submission:
  https://github.com/lamanmirzayeva/Weather-Forecasting.

The paper, notebook, PowerPoint, and package have not been submitted to the course.
The preceding paper draft is excluded from this ZIP to avoid version confusion.
The ZIP excludes the Python environment, downloaded compiler, Git metadata,
intermediate renders, and the ZIP itself. `MANIFEST.sha256` records every payload
file. The original NOAA inputs are included for reproducibility, with their
recorded source URLs and hashes.
