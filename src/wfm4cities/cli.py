"""Command-line interface for GUI and headless WFM4Cities workflows."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

import numpy as np

from ._version import __version__
from .core import (
    SimulationConfig,
    SurfaceModel,
    build_surface,
    interpolate_surface,
    local_neighbor_density,
    surface_from_grid,
)
from .io import (
    read_point_csv,
    read_surface_csv,
    write_json,
    write_points_csv,
    write_scan_csv,
    write_surface_csv,
)
from .pts import extract_features, progressive_threshold_scan


def _add_scan_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--threshold-count", type=int, default=51)
    parser.add_argument("--threshold-min", type=float, default=0.0)
    parser.add_argument("--threshold-max", type=float, default=0.95)
    parser.add_argument("--rule", choices=("inclusive", "strict"), default="inclusive")
    parser.add_argument("--connectivity", choices=(4, 8), type=int, default=8)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wfm4cities",
        description=(
            "Construct DEM-inspired urban scalar surfaces and run progressive "
            "threshold scanning (PTS)."
        ),
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    commands = parser.add_subparsers(dest="command")

    commands.add_parser("gui", help="launch the desktop graphical interface")

    demo = commands.add_parser("demo", help="run a deterministic synthetic example")
    demo.add_argument("--output-dir", type=Path, default=Path("wfm4cities_demo"))
    demo.add_argument("--seed", type=int, default=42)
    demo.add_argument("--num-points", type=int, default=100)
    demo.add_argument("--noise-ratio", type=float, default=0.50)
    demo.add_argument("--num-clusters", type=int, default=3)
    demo.add_argument("--cluster-std", type=float, default=1.0)
    demo.add_argument("--min-distance", type=float, default=1.0)
    demo.add_argument("--grid-size", type=int, default=100)
    demo.add_argument("--no-figure", action="store_true")
    _add_scan_options(demo)

    points = commands.add_parser(
        "points", help="interpolate an x/y[/value] CSV and scan the resulting surface"
    )
    points.add_argument("input", type=Path)
    points.add_argument("--output-dir", type=Path, default=Path("wfm4cities_points"))
    points.add_argument("--grid-size", type=int, default=100)
    points.add_argument("--domain-min", type=float, default=None)
    points.add_argument("--domain-max", type=float, default=None)
    points.add_argument("--density-radius", type=float, default=1.0)
    points.add_argument(
        "--method", choices=("nearest", "linear", "cubic"), default="cubic"
    )
    points.add_argument("--no-figure", action="store_true")
    _add_scan_options(points)

    scan = commands.add_parser("scan", help="scan a headerless numeric grid CSV")
    scan.add_argument("input", type=Path)
    scan.add_argument("--output-dir", type=Path, default=Path("wfm4cities_scan"))
    scan.add_argument("--keep-scale", action="store_true")
    scan.add_argument("--no-figure", action="store_true")
    _add_scan_options(scan)
    return parser


def _scan_from_args(model: SurfaceModel, args: argparse.Namespace):
    return progressive_threshold_scan(
        model.grid_z,
        threshold_count=args.threshold_count,
        threshold_min=args.threshold_min,
        threshold_max=args.threshold_max,
        rule=args.rule,
        connectivity=args.connectivity,
    )


def _write_outputs(
    output_dir: Path,
    model: SurfaceModel,
    result,
    *,
    include_points: bool,
    include_figure: bool,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    write_surface_csv(output_dir / "surface_normalized.csv", model)
    write_scan_csv(output_dir / "pts_response.csv", result)
    if include_points:
        write_points_csv(output_dir / "source_points.csv", model)
    try:
        extracted = extract_features(result)
        features = {
            name: (float(value) if np.isfinite(value) else None)
            for name, value in extracted.items()
        }
        feature_note = None
    except ValueError as exc:
        features = None
        feature_note = str(exc)
    write_json(
        output_dir / "pts_features.json",
        {
            "WFM4Cities_version": __version__,
            "threshold_rule": result.rule,
            "connectivity": result.connectivity,
            "features": features,
            "feature_note": feature_note,
        },
    )
    if include_figure:
        import matplotlib

        matplotlib.use("Agg")
        from .plotting import save_overview

        save_overview(output_dir / "wfm4cities_overview.png", model, result)


def _run_demo(args: argparse.Namespace) -> int:
    config = SimulationConfig(
        num_points=args.num_points,
        noise_ratio=args.noise_ratio,
        num_clusters=args.num_clusters,
        cluster_std=args.cluster_std,
        min_distance=args.min_distance,
        grid_size=args.grid_size,
        seed=args.seed,
    )
    model = build_surface(config)
    result = _scan_from_args(model, args)
    _write_outputs(
        args.output_dir,
        model,
        result,
        include_points=True,
        include_figure=not args.no_figure,
    )
    print(f"Wrote WFM4Cities demo results to {args.output_dir.resolve()}")
    return 0


def _run_points(args: argparse.Namespace) -> int:
    points, values = read_point_csv(args.input)
    observed = (
        values
        if values is not None
        else local_neighbor_density(points, radius=args.density_radius)
    )
    domain_min = float(np.min(points) if args.domain_min is None else args.domain_min)
    domain_max = float(np.max(points) if args.domain_max is None else args.domain_max)
    if domain_max <= domain_min:
        raise ValueError("domain_max must be greater than domain_min")
    grid_x, grid_y, grid_z = interpolate_surface(
        points,
        observed,
        grid_size=args.grid_size,
        domain_min=domain_min,
        domain_max=domain_max,
        method=args.method,
    )
    model = SurfaceModel(
        grid_x,
        grid_y,
        grid_z,
        points,
        np.asarray(observed, dtype=float),
        np.empty((0, 2), dtype=float),
    )
    result = _scan_from_args(model, args)
    _write_outputs(
        args.output_dir,
        model,
        result,
        include_points=True,
        include_figure=not args.no_figure,
    )
    print(f"Wrote point-to-surface results to {args.output_dir.resolve()}")
    return 0


def _run_scan(args: argparse.Namespace) -> int:
    grid = read_surface_csv(args.input)
    model = surface_from_grid(grid, normalize=not args.keep_scale)
    result = _scan_from_args(model, args)
    _write_outputs(
        args.output_dir,
        model,
        result,
        include_points=False,
        include_figure=not args.no_figure,
    )
    print(f"Wrote grid-scan results to {args.output_dir.resolve()}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the WFM4Cities command-line program."""

    parser = build_parser()
    arguments = list(sys.argv[1:] if argv is None else argv)
    if not arguments:
        arguments = ["gui"]
    args = parser.parse_args(arguments)
    try:
        if args.command == "gui":
            from .gui import run_gui

            run_gui()
            return 0
        if args.command == "demo":
            return _run_demo(args)
        if args.command == "points":
            return _run_points(args)
        if args.command == "scan":
            return _run_scan(args)
    except (ImportError, OSError, RuntimeError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")
    parser.print_help()
    return 0
