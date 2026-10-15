# Changelog

All notable changes follow the principles of
[Keep a Changelog](https://keepachangelog.com/) and semantic versioning.

## [3.1.24] - 2026-10-15

### Changed

- this release is published by `.github/workflows/publish.yml` with PyPI
  trusted publishing: the distributions are built by continuous integration from
  the tagged commit and uploaded with a short-lived OIDC token, so no long-lived
  API token is involved. The `pypi` environment requires the maintainer's
  approval before the upload starts;
- the package itself is unchanged from 3.1.23 apart from the version number.

## [3.1.23] - 2026-10-15

### Changed

- every page that is English by intent is now written in English only: the 3.1.21
  entry below no longer quotes the Chinese interface string, the readme link to
  the Chinese readme carries an English label, and the release notes of 3.1.22
  were corrected in place;
- the Chinese-language documents are declared in the readme and carry an English
  provenance header: `README_zh-CN.md`,
  `docs/GITHUB_UPLOAD_GUIDE_zh-CN.md` and `docs/REPOSITORY_AUDIT_zh-CN.md`. The
  Chinese release names of the authors in `AUTHORS.md` are kept;
- the Chinese assertion in `tests/test_interface_helpers.py` uses the escaped
  style of that file;
- `docs/RELEASE.md` documents the trusted-publishing path (the GitHub side is
  ready, the PyPI record is pending) next to the API-token fallback.

## [3.1.22] - 2026-10-15

### Changed

- the project is now hosted under a repository name that matches the
  distribution name: <https://github.com/zhangzuocughustccnu/PTS-WFM4Cities>.
  The original repository,
  <https://github.com/zhangzuocughustccnu/WFM4Cities>, is kept as an archive of
  the earlier single-file releases;
- the CI badge, the clone command, the project URLs of the package metadata and
  the citation file point to the new repository;
- the trusted-publisher note in `docs/RELEASE.md` names the new repository, and
  the issue templates speak of PTS-WFM4Cities.

## [3.1.21] - 2026-10-15

### Changed

- the status message that reports a generated structure now follows the
  interface language as well, so a Chinese interface no longer mixes an
  English model name into a Chinese sentence; the English wording of that
  message is unchanged.

### Added

- `wfm4cities.i18n.model_label()`, the single-line bilingual name of one of the
  four canonical structures, and the four `model_M1`--`model_M4` strings behind
  it.

## [3.1.20] - 2026-10-15

### Changed

- the design and API documentation is brought up to version 3.1: the module
  table of `docs/ARCHITECTURE.md` now lists `palette.py`, `i18n.py` and
  `fonts.py`, and `docs/API.md` documents the canonical-structure presets, the
  point-table import and the appearance modules;
- the Conda environment is named `pts-wfm4cities`;
- `docs/RELEASE.md` records the manual upload procedure used for the 3.1 series
  and the current release tag.

## [3.1.19] - 2026-10-15

### Changed

- the connected-component curve `N(h)` and its confidence band are drawn in the
  orange-red of the palette, while the largest-component share `L(h)` below it
  keeps the steel blue, so the two stacked panels are told apart at a glance;
- the *Import points* button is drawn in dark grey with white text, so the action
  that loads external data stands out from the other buttons;
- the window is centred on, and fitted to, the visible screen when it opens
  rather than taking the size of its own content, which could place it off-screen
  on a smaller display;
- `PTS_STRUCTURE` selects the structure shown when the window opens
  (`PTS_STRUCTURE=M2`), alongside the existing `PTS_LANGUAGE`;
- the package metadata, the citation file, the readme files and the licence now
  state the two-stage authorship of the toolkit: the early single-file
  `WFM4Cities` was developed by Zuo Zhang, Yukun Jiang and Zhe Wang, while
  `PTS-WFM4Cities` from 3.0 onwards is developed independently by Zuo Zhang.

### Added

- `wfm4cities.palette.N_CURVE_COLOR`, the orange-red of the `N(h)` curve;
- a design and feature overview in `README.md` and `README_zh-CN.md`.

## [3.1.18] - 2026-10-15

### Fixed

- the N(h) and L(h) panels keep their full width; only the geometric column is
  20% narrower, as asked.

### Changed

- the whole figure is scaled down by about 6% through one typography block, so
  every panel fits comfortably side by side.
## [3.1.17] - 2026-10-15

### Changed

- layout after the author's review of the interface: the geometric and the
  component-share columns are 20% narrower, the two vertical sections are 30%
  taller and their top and bottom edges align with the panels beside them;
- the N(h) and L(h) panels follow the selected structure only (clicking M1 shows
  M1, clicking M2 shows M2), so they stay consistent with the three-dimensional
  panel instead of comparing all four structures at once;
- the section fills use the ramp supplied by the author, orange at the top down
  to light blue at the bottom.
## [3.1.16] - 2026-10-15

### Fixed

- the window is painted before the four-structure curves are computed.  Since
  3.1.14 the computation ran before the event loop started, so the interface
  stayed invisible for many seconds and looked as if it had not opened;
- the curves are computed once, after first paint, on a modest grid, and
  cached; the two panels show a short placeholder while that happens.
## [3.1.15] - 2026-10-15

### Changed

- the vertical sections are filled below the profile with a gradient that
  follows the height of the surface, using the same colour-to-value rule as the
  three-dimensional panel; the profile is drawn in the high end of the ramp and
  the water level as a dashed line in the low end.
## [3.1.14] - 2026-10-15

### Changed

- the K(r) panel and the topological panel now show panels c1 and c2 of Figure 3
  of the accompanying study: the mean connected-component count N(h) and the
  mean largest-component share L(h) of the four canonical structures together,
  each with its 10--90% perturbation band, so the interface reports the
  controlled response comparison of the paper rather than a single structure.
## [3.1.13] - 2026-10-15

### Changed

- the middle column is 50% wider, so the geometric responses are wider and the
  three-dimensional surface has more room; every panel keeps its previous
  height, so the two rows stay aligned.
## [3.1.12] - 2026-10-15

### Changed

- the grid is fully uniform: equal column widths and equal row heights, so the
  K(r), geometric and topological panels have identical proportions;
- tighter title and label padding, so each panel fills its allotted box.
## [3.1.11] - 2026-10-15

### Changed

- panel spacing reduced to the practical minimum: gridspec and
  constrained-layout gaps, axes tick padding, and the gap between the two
  vertical sections.
## [3.1.10] - 2026-10-15

### Changed

- the two vertical sections sit closer together;
- the lower row is shorter, so the geometric and topological responses are
  closer to square while the sections keep the same height as the geometric
  panel beside them;
- the three-dimensional panel is widened slightly within the aligned grid.
## [3.1.9] - 2026-10-15

### Changed

- figure layout follows the author's sketch: two rows of three aligned
  columns -- point pattern, three-dimensional surface and Ripley's K on the
  first row; the two vertical sections stacked, the geometric responses and the
  topological responses on the second;
- the coordinate histograms are no longer part of the default figure;
- the section profiles are coloured by height with the surface ramp, from orange
  at the top to blue at the bottom, matching the three-dimensional panel.
## [3.1.8] - 2026-10-15

### Added

- vertical section analysis: two sliders place an X and a Y section through the
  surface and the two profiles are drawn with the submerged part shaded and the
  current water level marked;
- a view selector (ISO / Top / Side) for the three-dimensional panel, alongside
  the existing interactive rotation.

## [3.1.7] - 2026-10-15

### Fixed

- the project heading of the long description is now `PTS-WFM4Cities`, so the
  project page of the package carries the full name; 3.1.6 shipped the new
  colour scheme but still opened its description with the old short title.

## [3.1.6] - 2026-10-14

### Changed

- the point-pattern panel returns to the light-blue domain and orange
  observations sampled from the four-model figure of the accompanying study;
- the surface ramp runs from deep blue (low) to deep red (high), inheriting the
  colour bar of that figure; the water surface is the pale blue of its
  containers.

### Fixed

- the hierarchical two-by-four layout and the fixed three-dimensional box aspect
  announced for 3.1.5, which was prepared but never published.

## [3.1.5] - 2026-10-14

### Fixed

- the three-dimensional panel is drawn in a fixed box aspect instead of one
  derived from the data ranges, which had flattened the box whenever the
  vertical range was much smaller than the horizontal extent.

### Changed

- hierarchical two-by-four layout: the three-dimensional surface and the
  geometric responses span two columns each as the main panels, while the point
  pattern, Ripley's K, the topological responses and the histograms are the
  smaller statistics panels; panel gaps are minimal.

## [3.1.4] - 2026-10-14

### Changed

- compact figure layout: tighter panel padding, a wider three-dimensional
  panel zoomed to fill its cell, and the histogram pair brought together;
- one typography block in `fonts.apply()` gives the figures and the interface
  consistent compact sizes for titles, labels, ticks and legends.

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

[3.0.0]: https://github.com/zhangzuocughustccnu/PTS-WFM4Cities/releases/tag/v3.0.0
