"""Optional GeoPandas/PySAL diagnostics.

The core package does not require the geospatial stack.  Install
``PTS-WFM4Cities[spatial]`` before calling this module.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike


@dataclass(frozen=True)
class MoranResult:
    statistic: float
    expected: float
    p_sim: float
    permutations: int


def morans_i(
    points: ArrayLike,
    values: ArrayLike,
    *,
    k: int = 15,
    permutations: int = 999,
    seed: int = 42,
) -> MoranResult:
    """Calculate global Moran's I with adaptive kernel weights."""

    try:
        import geopandas as gpd
        import libpysal
        from esda import Moran
        from shapely.geometry import Point
    except ImportError as exc:
        raise ImportError(
            "optional spatial dependencies are missing; install PTS-WFM4Cities[spatial]"
        ) from exc

    coordinates = np.asarray(points, dtype=float)
    observed = np.asarray(values, dtype=float)
    if coordinates.ndim != 2 or coordinates.shape[1] != 2:
        raise ValueError("points must have shape (n, 2)")
    if observed.shape != (len(coordinates),):
        raise ValueError("values must contain one number per point")
    if len(coordinates) <= k:
        raise ValueError("number of points must be greater than k")
    frame = gpd.GeoDataFrame(
        {"value": observed},
        geometry=[Point(xy) for xy in coordinates],
    )
    weights = libpysal.weights.Kernel.from_dataframe(frame, fixed=False, k=k)
    random_state = np.random.get_state()
    try:
        np.random.seed(seed)
        result = Moran(observed, weights, permutations=permutations)
    finally:
        np.random.set_state(random_state)
    return MoranResult(
        statistic=float(result.I),
        expected=float(result.EI),
        p_sim=float(result.p_sim),
        permutations=permutations,
    )
