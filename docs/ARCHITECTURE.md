# Architecture

PTS-WFM4Cities 3.1 separates numerical analysis from presentation.

| Module | Responsibility |
|---|---|
| `core.py` | synthetic points, local density, interpolation, normalization, the four canonical presets, affine point standardisation, basic diagnostics |
| `pts.py` | A(h), V(h), N(h), L(h), and fixed feature extraction |
| `io.py` | explicit CSV and JSON contracts, including the point table read by the import dialogue |
| `plotting.py` | non-interactive Matplotlib figures |
| `palette.py` | every colour of the interface, the command line and the exported figures |
| `i18n.py` | every interface string, in English and Chinese |
| `fonts.py` | Times New Roman for Latin and SimSun/STSong for Chinese, without redistributing a font file |
| `spatial.py` | optional GeoPandas/PySAL Moran diagnostic |
| `cli.py` | headless and GUI command routing |
| `gui.py` | lazily loaded Tk desktop interface |
| `src/WFM4Cities/` | compatibility namespace for 2.x installations |

The package import path never creates a Tk root, starts a main loop, changes a
Matplotlib backend, sets a system font, or modifies NumPy's random global state.

## Data flow

1. Read or generate observations.
2. Construct or load a regular scalar surface.
3. Normalize when relative morphology is intended.
4. Select threshold rule, domain, range, density, and connectivity.
5. Compute the four full response trajectories.
6. Optionally extract features, plot, and export.

Each stage can be independently replaced. Controlled grids may enter at stage
2 without interpolation.

## Compatibility

The distribution is named `PTS-WFM4Cities` from version 3.0 onwards; the
historical 2.6 release keeps the name `WFM4Cities` and belongs to a different
PyPI account. The canonical import namespace is lowercase `wfm4cities`, as
recommended for Python packages. The historical `WFM4Cities` namespace and
`WFM4Cities.Water_flooding_Model:main` entry remain as thin forwarders.
