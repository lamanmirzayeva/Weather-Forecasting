# CPTS 570 presentation

Current design: `beamer/main.tex`, with final PDF at
`output/presentation/CPTS570_WSU_Beamer_Presentation.pdf`.
See `beamer/README.md` for build instructions and WSU brand references.

Previous live design: `artifact_f0dDQGV9HyRLaJAeJcng7MuhuLe4Z7dc`.

The current deck contains 12 Beamer slides with editable equations and plot data. Speaker notes
include timings, source citations, and a short notebook demonstration. Read
`speaker-notes.md` when rehearsing without the slide viewer.

## Timing

| Slide | Topic | Seconds |
|---:|---|---:|
| 1 | Title | 20 |
| 2 | Objectives and hypotheses | 40 |
| 3 | Literature | 35 |
| 4 | Data | 45 |
| 5 | Model | 60 |
| 6 | Protocol | 55 |
| 7 | Validation | 40 |
| 8 | Held-out results | 60 |
| 9 | Prediction intervals | 60 |
| 10 | Winter performance | 40 |
| 11 | Demo explanation | 45 |
| 11 | Notebook demonstration | 60 |
| 12 | Conclusions and follow-up | 40 |
| | Total | 600 |

Rehearse at a natural pace. Timing is a speaking plan, not a measured recording.
The notebook demonstration uses section 6 with `ORIGIN=2024-07-01`. Keep
`RUN_PIPELINE=False`. Saved notebook outputs provide a fallback.

## Source

`build.mjs` exports `build(presentation)` for an empty artifact presentation
session. The deck uses 1280-by-720 slides and Arial. The forecasting algorithms
and demo remain entirely Python; this JavaScript module authors only the slides.
Study evidence comes from the saved validation/test reports. Research references
appear in the relevant slide notes and in the paper.
