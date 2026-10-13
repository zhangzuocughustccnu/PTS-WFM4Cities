"""Small, explicit input/output helpers for WFM4Cities."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from .core import SurfaceModel
from .pts import PTSResult

FloatArray = NDArray[np.float64]


def read_point_csv(path: str | Path) -> tuple[FloatArray, FloatArray | None]:
    """Read case-insensitive x/y columns and an optional value/density/z column."""

    source = Path(path)
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("point CSV has no header")
        field_map = {name.strip().lower(): name for name in reader.fieldnames}
        if "x" not in field_map or "y" not in field_map:
            raise ValueError("point CSV must contain x and y columns")
        value_key = next(
            (
                field_map[name]
                for name in ("value", "density", "z")
                if name in field_map
            ),
            None,
        )
        coordinates: list[tuple[float, float]] = []
        values: list[float] = []
        for line_number, row in enumerate(reader, start=2):
            try:
                coordinates.append(
                    (float(row[field_map["x"]]), float(row[field_map["y"]]))
                )
                if value_key is not None:
                    values.append(float(row[value_key]))
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"invalid numeric value on CSV line {line_number}"
                ) from exc
    points = np.asarray(coordinates, dtype=float)
    if points.ndim != 2 or points.shape[1] != 2 or len(points) == 0:
        raise ValueError("point CSV contains no valid points")
    observed = np.asarray(values, dtype=float) if value_key is not None else None
    return points, observed


def read_surface_csv(path: str | Path) -> FloatArray:
    """Read a headerless numeric surface matrix."""

    data = np.loadtxt(Path(path), delimiter=",", dtype=float)
    if data.ndim != 2 or min(data.shape) < 2:
        raise ValueError("surface CSV must be a numeric matrix of at least 2 x 2")
    if not np.isfinite(data).all():
        raise ValueError("surface CSV contains NaN or infinite values")
    return np.asarray(data, dtype=float)


def write_surface_csv(path: str | Path, surface: SurfaceModel | FloatArray) -> Path:
    """Write a regular grid as a headerless numeric CSV matrix."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    values = (
        surface.grid_z if isinstance(surface, SurfaceModel) else np.asarray(surface)
    )
    np.savetxt(target, values, delimiter=",", fmt="%.10g")
    return target


def write_points_csv(path: str | Path, model: SurfaceModel) -> Path:
    """Write source x, y, and point-value columns when a point pattern exists."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["x", "y", "value"])
        for (x_value, y_value), value in zip(
            model.points, model.point_values, strict=True
        ):
            writer.writerow([f"{x_value:.10g}", f"{y_value:.10g}", f"{value:.10g}"])
    return target


def write_scan_csv(path: str | Path, result: PTSResult) -> Path:
    """Write the five-column PTS response table."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["threshold", "A", "V", "N", "L"])
        for row in zip(
            result.thresholds,
            result.area,
            result.excess_volume,
            result.component_count,
            result.largest_component_ratio,
            strict=True,
        ):
            writer.writerow(
                [
                    f"{row[0]:.10g}",
                    f"{row[1]:.10g}",
                    f"{row[2]:.10g}",
                    int(row[3]),
                    f"{row[4]:.10g}",
                ]
            )
    return target


def write_json(path: str | Path, payload: dict[str, Any]) -> Path:
    """Write UTF-8 JSON with deterministic key ordering."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(
            payload,
            handle,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        handle.write("\n")
    return target
