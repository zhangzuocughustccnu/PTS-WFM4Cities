"""Matplotlib figures for surfaces and PTS responses."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from .core import SurfaceModel
from .pts import PTSResult


def _threshold_index(result: PTSResult, threshold: float) -> int:
    return int(np.argmin(np.abs(result.thresholds - threshold)))


def plot_overview(
    model: SurfaceModel,
    result: PTSResult,
    *,
    threshold: float = 0.40,
    title: str = "WFM4Cities analysis",
) -> Figure:
    """Create a six-panel point/surface/PTS diagnostic figure."""

    figure = plt.figure(figsize=(12, 8), constrained_layout=True)
    grid = figure.add_gridspec(2, 3)

    point_ax = figure.add_subplot(grid[0, 0])
    if len(model.points):
        point_ax.scatter(
            model.points[:, 0],
            model.points[:, 1],
            c=model.point_values,
            s=18,
            cmap="viridis",
            edgecolors="none",
        )
        if len(model.centers):
            point_ax.scatter(
                model.centers[:, 0],
                model.centers[:, 1],
                marker="x",
                s=55,
                color="#c43c39",
                label="Cluster centers",
            )
            point_ax.legend(frameon=False, fontsize=8)
        point_ax.set_title("Source point pattern")
    else:
        point_ax.text(0.5, 0.5, "Regular-grid input", ha="center", va="center")
        point_ax.set_title("Input type")
    point_ax.set_xlabel("x")
    point_ax.set_ylabel("y")
    point_ax.set_aspect("equal", adjustable="box")

    map_ax = figure.add_subplot(grid[0, 1])
    image = map_ax.pcolormesh(
        model.grid_x, model.grid_y, model.grid_z, shading="auto", cmap="viridis"
    )
    figure.colorbar(image, ax=map_ax, shrink=0.78, label="Normalized intensity")
    map_ax.set_title("Interpolated scalar surface")
    map_ax.set_xlabel("x")
    map_ax.set_ylabel("y")
    map_ax.set_aspect("equal", adjustable="box")

    surface_ax = figure.add_subplot(grid[0, 2], projection="3d")
    surface_ax.plot_surface(
        model.grid_x,
        model.grid_y,
        model.grid_z,
        cmap="viridis",
        linewidth=0,
        antialiased=True,
        alpha=0.95,
    )
    plane = np.full_like(model.grid_z, threshold)
    surface_ax.plot_surface(
        model.grid_x,
        model.grid_y,
        plane,
        color="#77aadd",
        alpha=0.32,
        linewidth=0,
    )
    surface_ax.set_zlim(0.0, max(1.0, float(model.grid_z.max())))
    surface_ax.set_title(f"3-D surface and h={threshold:.2f}")
    surface_ax.set_xlabel("x")
    surface_ax.set_ylabel("y")
    surface_ax.set_zlabel("z")

    mask_ax = figure.add_subplot(grid[1, 0])
    retained = (
        model.grid_z >= threshold
        if result.rule == "inclusive"
        else model.grid_z > threshold
    )
    mask_ax.imshow(
        retained,
        origin="lower",
        extent=model.extent,
        cmap="Greys",
        vmin=0,
        vmax=1,
        interpolation="nearest",
    )
    mask_ax.set_title("Projected superlevel set")
    mask_ax.set_xlabel("x")
    mask_ax.set_ylabel("y")
    mask_ax.set_aspect("equal", adjustable="box")

    geometry_ax = figure.add_subplot(grid[1, 1])
    geometry_ax.plot(result.thresholds, result.area, label="A(h)", linewidth=2)
    geometry_ax.plot(result.thresholds, result.excess_volume, label="V(h)", linewidth=2)
    geometry_ax.axvline(threshold, color="0.6", linestyle="--", linewidth=1)
    geometry_ax.set_xlim(float(result.thresholds[0]), float(result.thresholds[-1]))
    geometry_ax.set_ylim(0.0, 1.02)
    geometry_ax.set_xlabel("Threshold h")
    geometry_ax.set_ylabel("Normalized response")
    geometry_ax.set_title("Geometric responses")
    geometry_ax.legend(frameon=False)

    topology_ax = figure.add_subplot(grid[1, 2])
    topology_ax.plot(
        result.thresholds,
        result.component_count,
        color="#aa4466",
        label="N(h)",
        linewidth=2,
    )
    topology_ax.set_xlabel("Threshold h")
    topology_ax.set_ylabel("Components N(h)", color="#aa4466")
    topology_ax.tick_params(axis="y", labelcolor="#aa4466")
    topology_ax.axvline(threshold, color="0.6", linestyle="--", linewidth=1)
    dominance_ax = topology_ax.twinx()
    dominance_ax.plot(
        result.thresholds,
        result.largest_component_ratio,
        color="#4477aa",
        label="L(h)",
        linewidth=2,
    )
    dominance_ax.set_ylabel("Largest-component ratio L(h)", color="#4477aa")
    dominance_ax.tick_params(axis="y", labelcolor="#4477aa")
    dominance_ax.set_ylim(0.0, 1.02)
    topology_ax.set_title("Topological responses")

    index = _threshold_index(result, threshold)
    component_summary = (
        f"N={result.component_count[index]}, "
        f"L={result.largest_component_ratio[index]:.3f}"
    )
    title_summary = (
        f"{title} | A={result.area[index]:.3f}, "
        f"V={result.excess_volume[index]:.3f}, {component_summary}"
    )
    figure.suptitle(
        title_summary,
        fontsize=13,
    )
    return figure


def save_overview(
    path: str | Path,
    model: SurfaceModel,
    result: PTSResult,
    *,
    threshold: float = 0.40,
    dpi: int = 200,
) -> Path:
    """Create and save an overview figure, then close it."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    figure = plot_overview(model, result, threshold=threshold)
    figure.savefig(target, dpi=dpi, bbox_inches="tight")
    plt.close(figure)
    return target
