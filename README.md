# PTS-WFM4Cities

[![CI](https://github.com/zhangzuocughustccnu/WFM4Cities/actions/workflows/ci.yml/badge.svg)](https://github.com/zhangzuocughustccnu/WFM4Cities/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/PTS-WFM4Cities.svg)](https://pypi.org/project/PTS-WFM4Cities/)
[![Python](https://img.shields.io/pypi/pyversions/PTS-WFM4Cities.svg)](https://pypi.org/project/PTS-WFM4Cities/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

PTS-WFM4Cities is a research-oriented Python package for constructing
DEM-inspired urban scalar surfaces and analyzing them with Progressive
Threshold Scanning (PTS). It supports a transparent point-to-surface workflow, a headless API and
command-line interface, and an optional bilingual desktop interface.

[简体中文说明](README_zh-CN.md)

## Design and feature overview

### Design rules

1. **One scalar surface, one threshold axis.** Any urban attribute carried by a
   two-dimensional support -- night-time-light intensity, population density,
   building volume -- becomes a continuous surface, and every result is
   reported as a curve over the threshold \(h\), never as a single unexplained
   number.
2. **Reproducible by construction.** Point patterns, surfaces, threshold
   sequences and figures are rebuilt from an explicit seed and an explicit
   configuration, so any run can be repeated exactly.
3. **One implementation behind the interface and the API.** The desktop window,
   the command line and the library call the same functions; a figure produced
   by hand can be reproduced by script.
4. **One place for the appearance.** Colours live in `wfm4cities.palette`,
   strings in `wfm4cities.i18n` and fonts in `wfm4cities.fonts`, so the
   interface, the exported figures and the manuscript always agree.

### Feature overview

| Area | What version 3.1 offers |
| --- | --- |
| Structures | the four canonical models `M1`--`M4` of the accompanying study, as one-click presets |
| Own data | import of any table of two-dimensional coordinates plus one attribute column |
| Surface | cubic interpolation, nearest-neighbour fill outside the interpolation hull, min--max normalisation to \([0,1]\) |
| Scan | an ordered threshold sequence with an explicit `inclusive` or `strict` rule |
| Curves | projected area \(A(h)\), normalised excess volume \(V(h)\), connected components \(N(h)\), largest-component share \(L(h)\) |
| Views | threshold slider, cut planes in \(x\) and \(y\), ISO/Top/Side viewing angles, animation |
| Figures | point pattern, three-dimensional surface, gradient-filled vertical sections, geometric responses, \(N(h)\) and \(L(h)\) panels |
| Interface | bilingual (English by default, Chinese at one click) with Times New Roman and SimSun/STSong typography |
| Automation | headless API, command-line interface, CSV and JSON export |

The window is laid out as the six panels of the accompanying study: the point
pattern, the three-dimensional surface, the connected-component count, the two
vertical sections, the geometric responses and the largest-component share.

## What the package does

- checks and visualizes point patterns;
- generates the four canonical structures `M1`--`M4` as one-click presets;
- interpolates scattered observations with
  `scipy.interpolate.griddata(method="cubic")`;
- fills cells outside the cubic interpolation hull with nearest-neighbor values;
- min--max normalizes an analytical surface to \([0,1]\);
- scans an ordered threshold sequence;
- calculates projected area \(A(h)\), normalized excess volume \(V(h)\),
  connected-component count \(N(h)\), and largest-component ratio \(L(h)\);
- imports any table of two-dimensional coordinates plus one attribute column
  and maps it onto the standard square domain;
- exports regular grids, full response trajectories, fixed summary features,
  and overview figures;
- provides optional GeoPandas/PySAL spatial diagnostics.

WFM4Cities treats the vertical coordinate as the value of a specified urban
attribute (for example, density, activity intensity, or building volume). It
does **not** infer the meaning of that variable.

## Scientific scope

The water-flooding metaphor is an explanatory analogy for moving a horizontal
threshold through a scalar surface. WFM4Cities is **not** a hydrodynamic flood
model, a general DEM-production system, or an operational planning platform.
Threshold order is not time. Hydrological applications require additional
terrain, rainfall, drainage, flow-path, water-depth, and exposure information.

## Installation

Python 3.10--3.13 is supported. Python 3.11 is the recommended reference
environment.

### Install from the repository

    git clone https://github.com/zhangzuocughustccnu/WFM4Cities.git
    cd WFM4Cities
    python -m venv .venv

Activate the environment:

    # Windows PowerShell
    .venv\Scripts\Activate.ps1

    # macOS/Linux
    source .venv/bin/activate

Then install:

    python -m pip install --upgrade pip
    python -m pip install -e .

### Install the released package

    python -m pip install PTS-WFM4Cities

The PyPI distribution is named `PTS-WFM4Cities`. The historical 2.6 release is
still published under the shorter name `WFM4Cities`, which belongs to a
different PyPI account, so `pip install WFM4Cities` installs that older
release. Always install `PTS-WFM4Cities` to get version 3.1.

### Optional spatial diagnostics

    python -m pip install "PTS-WFM4Cities[spatial]"

### Conda environment

    conda env create -f environment.yml
    conda activate wfm4cities-3.0

Tkinter is included with standard Python on Windows and macOS. On some Linux
distributions it is a separate operating-system package (for example,
`sudo apt install python3-tk` on Debian/Ubuntu).

## Quick start

### Desktop interface

    wfm4cities gui

Running `wfm4cities` with no subcommand also opens the interface. The
historical `WFM4Cities` command remains available after installation; the
`python WFM4Cities.py` launcher also remains available in a source checkout.

Two environment variables configure the window when it opens:
`PTS_LANGUAGE` selects `en` or `zh`, and `PTS_STRUCTURE` selects the
structure shown first (`M1`, `M2`, `M3` or `M4`, default `M1`).

### Deterministic headless demonstration

    wfm4cities demo --output-dir demo_results --seed 42

This writes:

- `source_points.csv`;
- `surface_normalized.csv`;
- `pts_response.csv`;
- `pts_features.json`;
- `wfm4cities_overview.png`.

### Analyze an existing grid

The input must be a headerless numeric CSV matrix:

    wfm4cities scan my_surface.csv --output-dir scan_results

Use strict thresholding to exclude zero background cells at \(h=0\):

    wfm4cities scan my_surface.csv --rule strict --output-dir scan_results

### Construct a surface from points

The CSV must contain `x` and `y` columns. An optional column named
`value`, `density`, or `z` supplies the vertical value. If it is absent,
WFM4Cities calculates a local neighbor count.

    wfm4cities points observations.csv --grid-size 100 --method cubic

## Python API

    from wfm4cities import (
        SimulationConfig,
        build_surface,
        extract_features,
        progressive_threshold_scan,
    )

    config = SimulationConfig(
        num_points=150,
        noise_ratio=0.30,
        num_clusters=4,
        grid_size=100,
        seed=2026,
    )
    model = build_surface(config)
    result = progressive_threshold_scan(
        model.grid_z,
        threshold_count=51,
        threshold_min=0.0,
        threshold_max=0.95,
        rule="inclusive",
        connectivity=8,
    )
    features = extract_features(result)
    print(features)

The main response arrays are available as `result.A`, `result.V`,
`result.N`, and `result.L`.


## Canonical structures (M1--M4)

The four canonical structures of the accompanying study are available as
one-click presets.  One cluster means monocentric and several clusters mean
polycentric; a small cluster standard deviation means concentrated and a large
one means dispersed.

| Preset | Structure |
| --- | --- |
| `M1` | monocentric-concentrated |
| `M2` | polycentric-concentrated |
| `M3` | monocentric-dispersed |
| `M4` | polycentric-dispersed |

    from wfm4cities import MODEL_LABELS, build_model_surface

    surface = build_model_surface("M3")      # or "M1", "M2", "M4"
    print(MODEL_LABELS["M3"])                # M3 monocentric-dispersed

The presets are the stochastic counterparts of the deterministic benchmark
surfaces: they generate point patterns with the characteristic signature of each
structure, not the archived benchmark grids themselves.  In the desktop
interface they are the four buttons of the *Canonical structures* panel.

## Importing your own observations

Any table of two-dimensional coordinates plus one attribute can be imported.
The external margin is removed, the extent is affinely mapped onto the standard
square domain (0--100 by default) and the attribute is min--max normalised to
0--1, mirroring the night-time-light preparation of the accompanying study.  The
aspect ratio is not preserved unless `preserve_aspect=True`, and the applied
scales are always reported.

    import numpy as np
    from wfm4cities import standardize_points

    points = np.array([[0, 0], [4, 0], [4, 3], [0, 3]])
    values = np.array([1.0, 2.0, 3.0, 4.0])
    mapped, normalised, report = standardize_points(points, values)
    print(report.scale_x, report.scale_y)

In the desktop interface choose *Import points* and pick the x, y and attribute
columns; the status bar reports the mapping that was applied.

## Interface language

The desktop interface starts in English and the *Language* button switches it to
Chinese; every label, panel title and status message follows.  The strings live
in `wfm4cities.i18n`, so a further language is a table away.

## Fonts and colour scheme

`wfm4cities.fonts` selects Times New Roman for Latin text and SimSun/STSong for
Chinese, using the copies already installed on the system, and registers extra
font files from the folder named by `PTS_FONT_DIR`.  No proprietary font file is
redistributed with the package.

Every colour lives in `wfm4cities.palette`, so the interface, the command line
and the exported figures always agree.

    from wfm4cities.palette import SURFACE_RAMP, surface_cmap

## Threshold conventions

Two explicit rules are available:

- `inclusive`: retain cells satisfying \(z \ge h\). This is the default and
  matches the controlled archetype analysis.
- `strict`: retain cells satisfying \(z > h\). This excludes zero-valued
  background cells when \(h=0\).

The denominator of \(A(h)\) is the fixed analysis domain, not the number of
currently positive cells. Components use eight-neighbor connectivity by
default; four-neighbor connectivity is also available. \(V(h)\) is normalized
by total intensity at \(h=0\).

See [Method conventions](docs/METHOD.md) for the exact definitions.

## Project structure

    WFM4Cities/
    ├── src/wfm4cities/       # maintained implementation
    ├── src/WFM4Cities/       # compatibility namespace for 2.x users
    ├── tests/                # automated regression tests
    ├── examples/             # executable examples and sample data
    ├── docs/                 # method, API, architecture, and release notes
    ├── legacy/               # unmodified historical single-file script
    ├── pyproject.toml        # package metadata and dependencies
    ├── environment.yml       # recommended Conda environment
    ├── CITATION.cff          # machine-readable software citation
    └── LICENSE               # MIT license

The maintained package does not create Tk windows or force a Matplotlib backend
when imported. GUI code is loaded only when requested.

## Reproducibility and testing

Create a development environment and run:

    python -m pip install -e ".[dev]"
    ruff check .
    pytest
    python -m build
    python -m twine check dist/*

`requirements-tested.txt` records the exact numerical library versions used
for the 3.0.0 release-candidate verification. `pyproject.toml` remains the
authoritative dependency specification.

## Method demonstration

The physical immersion demonstration used to explain the threshold analogy is
available at [YouTube](https://youtu.be/tMdRVbR-JpQ). It is explanatory only
and does not define the numerical algorithm.

## Authors

The early single-file version of this toolkit, **WFM4Cities**, was developed
jointly by **Zuo Zhang, Yukun Jiang, and Zhe Wang**.

The current package, **PTS-WFM4Cities** (3.0 onwards), is developed
independently by **Zuo Zhang**. See [AUTHORS.md](AUTHORS.md) for details.

## Citation

Use GitHub's “Cite this repository” control or the metadata in
[CITATION.cff](CITATION.cff). Add the article DOI to the citation metadata after
the associated paper is published; no DOI is invented in this repository.

## Contributing and support

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request.
Reproducible bug reports can be filed through the repository's issue templates.
Security-sensitive reports should follow [SECURITY.md](SECURITY.md).

## License

PTS-WFM4Cities is distributed under the [MIT License](LICENSE). The
historical single-file releases are retained for provenance and are covered
by the same repository licence.
