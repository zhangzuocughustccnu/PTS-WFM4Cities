# Changelog

All notable changes follow the principles of
[Keep a Changelog](https://keepachangelog.com/) and semantic versioning.

## [3.1.3] - 2026-10-14

### Changed

- the point pattern is drawn in the deep red of the shaded surface and the
  cluster centres in the orange of the ramp;
- the geometric responses use blue-black for A(h) and dark orange for V(h);
- the topological panel carries a legend for N(h) and L(h);
- the three-dimensional panel is wider, its panes are lighter and its grid is
  finer, thinner and paler.

### Added

- a Ripley's K(r) panel with a 95% complete-spatial-randomness band, and a
  coordinate-histogram panel, restoring the statistics of the 2.6 console.

## [3.1.2] - 2026-10-14

### Changed

- the surface ramp is now the black-to-yellow ramp of the accompanying study's
  city figure and supplementary city map, so the package and the manuscript
  share one palette; the categorical colours stay as in the manuscript.

## [3.1.1] - 2026-10-14

### Fixed

- documented the 3.1 features on the project page; 3.1.0 shipped the code but
  the long description was published before the sections below were written.

## [3.1.0] - 2026-10-14

### Added

- the four canonical structures of the accompanying study as one-click presets:
  `MODEL_PRESETS`, `MODEL_LABELS`, `model_config()` and `build_model_surface()`
  cover monocentric-concentrated (M1), polycentric-concentrated (M2),
  monocentric-dispersed (M3) and polycentric-dispersed (M4);
- `standardize_points()`, which removes the external margin of imported
  observations and affinely maps their extent onto the standard square domain
  while min--max normalising the selected attribute, plus a
  `StandardizationReport` recording the applied scales;
- `io.list_csv_columns()` and `io.read_point_table()` for importing arbitrary
  point tables with caller-chosen x, y and attribute columns;
- `wfm4cities.palette`, the single source of truth for the figure colours;
- `wfm4cities.i18n` and a *Language* button: the interface defaults to English
  and switches to Chinese, labels, panel titles and status messages included;
- `wfm4cities.fonts`: Times New Roman for Latin and SimSun/STSong for Chinese,
  taken from the system (no proprietary font file is redistributed) with
  `PTS_FONT_DIR` as an override for machines that lack them.

### Changed

- the desktop interface and the figure code read every colour from
  `wfm4cities.palette` instead of hard-coded values;
- the colour scheme follows the four-model figure of the accompanying study;
- the three-dimensional panel is hill-shaded so the relief is visible;
- the topological curves are drawn with a display-only moving average that
  keeps both anchors; exported values are never smoothed.

## [3.0.0] - 2026-08-08

### Added

- import-safe lowercase `wfm4cities` package;
- validated point-pattern and point-to-surface API;
- cubic interpolation with nearest-neighbor boundary filling;
- explicit 51-level PTS implementation for A(h), V(h), N(h), and L(h);
- fixed ten-feature extraction used by the associated study;
- headless `demo`, `points`, and `scan` commands;
- single-window bilingual Tk interface with threshold animation;
- CSV/JSON exports and reproducible overview figures;
- optional GeoPandas/PySAL Moran diagnostic;
- tests, CI, trusted-publishing workflow, citation metadata, and release guide;
- compatibility namespace and command for 2.x users;
- unmodified 2.6 single-file script in `legacy/` for provenance.

### Changed

- internal code is separated into numerical, PTS, I/O, plotting, optional
  spatial, CLI, and GUI modules;
- supported Python is now 3.10--3.13;
- runtime dependencies use compatible ranges rather than exact historical pins;
- the canonical version is consistently 3.0.0;
- the PyPI distribution is published as `PTS-WFM4Cities`; the historical 2.6
  release stays under the shorter name `WFM4Cities`.

### Fixed

- importing the package no longer creates Tk roots or starts a main loop;
- Matplotlib's backend and system font are no longer changed at import time;
- the PyPI homepage points to the real GitHub repository;
- CLI routing no longer depends on GUI global variables;
- impossible cluster-center settings fail with an actionable error;
- distribution metadata now includes the license, README, source distribution,
  wheel, and citation information.

## [2.6] - 2025-01-22

- historical PyPI release containing the original desktop script.

[3.0.0]: https://github.com/zhangzuocughustccnu/WFM4Cities/releases/tag/v3.0.0
