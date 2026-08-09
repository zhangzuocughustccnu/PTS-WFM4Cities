# Migrating from WFM4Cities 2.6 to 3.0

## What remains compatible

- distribution name: `WFM4Cities`;
- historical command: `WFM4Cities`;
- historical module path: `WFM4Cities.Water_flooding_Model`;
- top-level launcher: `python WFM4Cities.py`.

Each now forwards to maintained code.

## Recommended new usage

Use lowercase imports:

    import wfm4cities

Launch the interface with:

    wfm4cities gui

Run reproducible analyses without a display:

    wfm4cities demo
    wfm4cities points observations.csv
    wfm4cities scan surface.csv

## Intentional changes

- No window opens during import.
- No Matplotlib backend is forced during import.
- Random generation uses a local `numpy.random.Generator` with an explicit
  seed.
- Cubic interpolation boundaries are filled by nearest-neighbor values.
- PTS metrics and threshold rules are explicit and independently callable.
- Heavy GeoPandas/PySAL dependencies are optional.

The historical script is in `legacy/WFM4Cities_2.6_original.py`. It is not
imported, tested, or installed.
