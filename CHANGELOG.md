# Changelog

All notable changes follow the principles of
[Keep a Changelog](https://keepachangelog.com/) and semantic versioning.

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
- the canonical version is consistently 3.0.0.

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
