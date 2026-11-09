# Paper draft

`main.tex` is the editable paper source. It uses the unmodified NeurIPS
2025 style supplied in `Styles (1).zip`, in preprint mode, with named authors and no claim of conference
acceptance. The draft has **nine pages total, including references**, following
the proposal's nine-page target. No separate course rubric has been supplied;
instructor-specific rules about whether references count should be checked
before submission.

The author names follow the proposal (Jiayu and Laman). Full names and any
required affiliations await confirmation. Repository:
https://github.com/lamanmirzayeva/Weather-Forecasting.

## Build

With a TeX distribution containing the required packages:

```powershell
python scripts/paper_assets.py
cd paper
pdflatex main.tex
pdflatex main.tex
```

The local build used Tectonic 0.17.0 instead:

```powershell
cd paper
../.tools/tectonic/tectonic.exe -X compile main.tex --keep-logs
```

The project-local compiler is excluded from Git. A first build may need network
access to download TeX packages. Publication figures are generated as vector
PDFs directly from the saved data and experiments by `scripts/paper_assets.py`.
The current academic revision is delivered as
`output/pdf/CPTS570_Temperature_Forecasting_Academic_Revision.pdf`.
The earlier draft remains available separately. The current `main.tex` contains
the revised academic prose and linked bibliography; the preceding source is
preserved in `archive/main_before_academic_revision.tex`.

## Sources and scope

- Course-supplied style: `Styles/neurips_2025.sty` from `Styles (1).zip`.
- NOAA field documentation:
  https://www.ncei.noaa.gov/data/global-summary-of-the-day/doc/readme.txt
- Dynamic harmonic regression:
  https://otexts.com/fpp3/dynamic-regression.html
- Model implementation:
  https://www.statsmodels.org/v0.14.6/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html

This is a course-project draft, not a NeurIPS submission. It reports the
completed experiments and their limitations, including winter undercoverage,
non-Gaussian residuals, changing variance, and the small seven-day advantage.
No model was retuned to improve the paper's test results.

The expanded literature review compares dynamic harmonic regression, systematic
ARIMA selection, and interpretable additive forecasting, with five references.
