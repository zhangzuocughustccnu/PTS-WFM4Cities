"""Interpolate the bundled point CSV and export a PTS analysis."""

from pathlib import Path

import numpy as np

from wfm4cities.core import SurfaceModel, interpolate_surface
from wfm4cities.io import (
    read_point_csv,
    write_scan_csv,
    write_surface_csv,
)
from wfm4cities.pts import progressive_threshold_scan


def main() -> None:
    source = Path(__file__).with_name("data") / "sample_points.csv"
    output = Path("example_results")
    points, values = read_point_csv(source)
    if values is None:
        raise RuntimeError("the bundled example must contain a value column")
    grid_x, grid_y, grid_z = interpolate_surface(
        points,
        values,
        grid_size=60,
        domain_min=0.0,
        domain_max=10.0,
        method="cubic",
    )
    model = SurfaceModel(
        grid_x,
        grid_y,
        grid_z,
        points,
        values,
        np.empty((0, 2), dtype=float),
    )
    result = progressive_threshold_scan(model.grid_z)
    write_surface_csv(output / "surface_normalized.csv", model)
    write_scan_csv(output / "pts_response.csv", result)
    print(f"Wrote example results to {output.resolve()}")


if __name__ == "__main__":
    main()
