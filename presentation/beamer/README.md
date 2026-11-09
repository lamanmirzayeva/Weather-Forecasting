# Washington State University styled Beamer presentation

This is the current presentation design. It supersedes the earlier PowerPoint
design. It is a custom LaTeX Beamer theme using Madrid as a base, with section
headers, slide numbers, formal equations, and WSU crimson/gray styling.
It is not represented as an official WSU presentation template.

Brand colors follow WSU's published palette:
https://brand.wsu.edu/colors/ — crimson `#A60F2D`, gray `#4D4D4D`.
The university's downloadable presentation templates require a WSU login:
https://brand.wsu.edu/downloads/. No university logo has been recreated.

## Contents

- `main.tex`: editable presentation source, including speaker notes.
- `assets/`: plot data and the existing notebook demonstration figure.
- `prepare_assets.py`: derives chart data from the saved experiments.
- Final PDF: `output/presentation/CPTS570_WSU_Beamer_Presentation.pdf`.

There are twelve frames. The content and timed notes cover a ten-minute slot,
including one minute for the notebook demonstration. The existing
`presentation/speaker-notes.md` remains a plain-text rehearsal companion.

## Build

From the repository root:

```powershell
python presentation/beamer/prepare_assets.py
cd presentation/beamer
pdflatex main.tex
pdflatex main.tex
```

Alternatively use Tectonic:

```powershell
cd presentation/beamer
../../.tools/tectonic/tectonic.exe -X compile main.tex --keep-logs
```

PGFPlots, Beamer, and Latin Modern are standard TeX packages. The CSV-backed
charts and typeset equations remain editable in the LaTeX source. Data and
scientific findings match the paper. `hide notes` keeps notes out of the slide
PDF; switch to `show notes` to compile a notes version if needed.
