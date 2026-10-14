"""PTS--WFM4Cities.

Progressive threshold scanning (PTS) on DEM-inspired urban scalar surfaces.
The import is free of graphical side effects; the colour scheme lives in
:mod:`wfm4cities.palette` and is loaded only when a figure is drawn.
"""

from ._version import __version__
from .core import (
    MODEL_LABELS,
    MODEL_PRESETS,
    SimulationConfig,
    StandardizationReport,
    SurfaceModel,
    build_model_surface,
    build_surface,
    interpolate_surface,
    model_config,
    normalize_surface,
    standardize_points,
    surface_from_grid,
)
from .pts import PTSResult, extract_features, progressive_threshold_scan

__all__ = [
    "MODEL_LABELS",
    "MODEL_PRESETS",
    "PTSResult",
    "SimulationConfig",
    "StandardizationReport",
    "SurfaceModel",
    "__version__",
    "build_model_surface",
    "build_surface",
    "extract_features",
    "interpolate_surface",
    "model_config",
    "normalize_surface",
    "progressive_threshold_scan",
    "standardize_points",
    "surface_from_grid",
]
