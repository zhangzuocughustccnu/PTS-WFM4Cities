# Architecture

WFM4Cities 3.0 separates numerical analysis from presentation.

| Module | Responsibility |
|---|---|
| `core.py` | synthetic points, local density, interpolation, normalization, basic diagnostics |
| `pts.py` | A(h), V(h), N(h), L(h), and fixed feature extraction |
| `io.py` | explicit CSV and JSON contracts |
| `plotting.py` | non-interactive Matplotlib figures |
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

The distribution remains named `WFM4Cities`. The canonical import namespace
is lowercase `wfm4cities`, as recommended for Python packages. The historical
`WFM4Cities` namespace and `WFM4Cities.Water_flooding_Model:main` entry
remain as thin forwarders.
