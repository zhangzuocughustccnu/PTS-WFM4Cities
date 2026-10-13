"""WFM4Cities: DEM-inspired urban surface construction and threshold scanning."""

from ._version import __version__
from .core import (
    SimulationConfig,
    SurfaceModel,
    build_surface,
    interpolate_surface,
    normalize_surface,
    surface_from_grid,
)
from .pts import PTSResult, extract_features, progressive_threshold_scan

__all__ = [
    "PTSResult",
    "SimulationConfig",
    "SurfaceModel",
    "__version__",
    "build_surface",
    "extract_features",
    "interpolate_surface",
    "normalize_surface",
    "progressive_threshold_scan",
    "surface_from_grid",
]
