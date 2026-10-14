"""Numerical building blocks for WFM4Cities.

This module has no graphical side effects.  It can therefore be imported in
notebooks, batch jobs, tests, and headless servers without opening a window or
selecting a Matplotlib backend.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.interpolate import griddata
from scipy.spatial.distance import cdist, pdist, squareform
from sklearn.datasets import make_blobs

FloatArray = NDArray[np.float64]
InterpolationMethod = Literal["nearest", "linear", "cubic"]


@dataclass(frozen=True)
class SimulationConfig:
    """Settings used to generate the synthetic point-pattern demonstration."""

    num_points: int = 100
    noise_ratio: float = 0.50
    num_clusters: int = 3
    cluster_std: float = 1.0
    min_distance: float = 1.0
    density_radius: float = 1.0
    grid_size: int = 100
    domain_min: float = 0.0
    domain_max: float = 10.0
    interpolation_method: InterpolationMethod = "cubic"
    seed: int = 42

    def __post_init__(self) -> None:
        if self.num_points < 2:
            raise ValueError("num_points must be at least 2")
        if not 0.0 <= self.noise_ratio < 1.0:
            raise ValueError("noise_ratio must be in [0, 1)")
        if self.num_clusters < 1:
            raise ValueError("num_clusters must be at least 1")
        clustered = self.num_points - int(self.noise_ratio * self.num_points)
        if clustered < self.num_clusters:
            raise ValueError(
                "the number of clustered points must be at least num_clusters"
            )
        if self.cluster_std <= 0.0:
            raise ValueError("cluster_std must be positive")
        if self.min_distance < 0.0:
            raise ValueError("min_distance cannot be negative")
        if self.density_radius <= 0.0:
            raise ValueError("density_radius must be positive")
        if self.grid_size < 8:
            raise ValueError("grid_size must be at least 8")
        if self.domain_max <= self.domain_min:
            raise ValueError("domain_max must be greater than domain_min")
        if self.interpolation_method not in {"nearest", "linear", "cubic"}:
            raise ValueError("unsupported interpolation_method")


@dataclass(frozen=True)
class SurfaceModel:
    """A regular scalar surface and, when available, its source point pattern."""

    grid_x: FloatArray
    grid_y: FloatArray
    grid_z: FloatArray
    points: FloatArray
    point_values: FloatArray
    centers: FloatArray

    def __post_init__(self) -> None:
        if (
            self.grid_x.shape != self.grid_y.shape
            or self.grid_x.shape != self.grid_z.shape
        ):
            raise ValueError("grid_x, grid_y, and grid_z must have identical shapes")
        if self.grid_z.ndim != 2:
            raise ValueError("grid_z must be two-dimensional")
        if not np.isfinite(self.grid_z).all():
            raise ValueError("grid_z must be finite; fill missing boundaries first")
        if self.points.ndim != 2 or self.points.shape[1] != 2:
            raise ValueError("points must have shape (n, 2), including when n is zero")
        if self.point_values.shape != (self.points.shape[0],):
            raise ValueError("point_values must contain one value per point")

    @property
    def shape(self) -> tuple[int, int]:
        return self.grid_z.shape

    @property
    def extent(self) -> tuple[float, float, float, float]:
        return (
            float(np.min(self.grid_x)),
            float(np.max(self.grid_x)),
            float(np.min(self.grid_y)),
            float(np.max(self.grid_y)),
        )


def normalize_surface(values: ArrayLike) -> FloatArray:
    """Min--max normalize finite values to [0, 1]."""

    z = np.asarray(values, dtype=float)
    if z.ndim != 2:
        raise ValueError("surface must be two-dimensional")
    if not np.isfinite(z).all():
        raise ValueError("surface contains NaN or infinite values")
    minimum = float(z.min())
    maximum = float(z.max())
    if maximum <= minimum:
        return np.zeros_like(z, dtype=float)
    return np.asarray((z - minimum) / (maximum - minimum), dtype=float)


def generate_cluster_centers(
    num_clusters: int,
    min_distance: float,
    *,
    domain_min: float = 0.0,
    domain_max: float = 10.0,
    rng: np.random.Generator | None = None,
    max_attempts: int = 50_000,
) -> FloatArray:
    """Generate centers with rejection sampling and a clear feasibility failure."""

    if num_clusters < 1:
        raise ValueError("num_clusters must be at least 1")
    if min_distance < 0.0:
        raise ValueError("min_distance cannot be negative")
    if domain_max <= domain_min:
        raise ValueError("domain_max must be greater than domain_min")
    generator = rng if rng is not None else np.random.default_rng()
    centers = [generator.uniform(domain_min, domain_max, size=2)]
    attempts = 0
    while len(centers) < num_clusters and attempts < max_attempts:
        candidate = generator.uniform(domain_min, domain_max, size=2)
        distance = np.linalg.norm(np.asarray(centers) - candidate, axis=1)
        if np.all(distance > min_distance):
            centers.append(candidate)
        attempts += 1
    if len(centers) != num_clusters:
        raise ValueError(
            "could not place all cluster centers; reduce min_distance or "
            "num_clusters, or enlarge the domain"
        )
    return np.asarray(centers, dtype=float)


def generate_point_pattern(config: SimulationConfig) -> tuple[FloatArray, FloatArray]:
    """Generate clustered points plus uniformly distributed background noise."""

    rng = np.random.default_rng(config.seed)
    centers = generate_cluster_centers(
        config.num_clusters,
        config.min_distance,
        domain_min=config.domain_min,
        domain_max=config.domain_max,
        rng=rng,
    )
    noise_count = int(config.noise_ratio * config.num_points)
    clustered_count = config.num_points - noise_count
    noise = rng.uniform(config.domain_min, config.domain_max, size=(noise_count, 2))
    random_state = int(rng.integers(0, np.iinfo(np.int32).max))
    clustered, _ = make_blobs(
        n_samples=clustered_count,
        centers=centers,
        cluster_std=config.cluster_std,
        random_state=random_state,
    )
    clustered = np.clip(clustered, config.domain_min, config.domain_max)
    points = np.vstack((noise, clustered))
    return np.asarray(points, dtype=float), centers


def local_neighbor_density(points: ArrayLike, radius: float = 1.0) -> FloatArray:
    """Count neighbors within ``radius`` for every point, including the point itself."""

    coordinates = np.asarray(points, dtype=float)
    if coordinates.ndim != 2 or coordinates.shape[1] != 2:
        raise ValueError("points must have shape (n, 2)")
    if len(coordinates) < 1:
        raise ValueError("at least one point is required")
    if radius <= 0.0:
        raise ValueError("radius must be positive")
    distances = cdist(coordinates, coordinates)
    return np.asarray(np.sum(distances < radius, axis=1), dtype=float)


def interpolate_surface(
    points: ArrayLike,
    values: ArrayLike,
    *,
    grid_size: int = 100,
    domain_min: float = 0.0,
    domain_max: float = 10.0,
    method: InterpolationMethod = "cubic",
    fill_boundaries: bool = True,
    normalize: bool = True,
) -> tuple[FloatArray, FloatArray, FloatArray]:
    """Interpolate scattered observations onto a regular square grid.

    Cubic interpolation follows the manuscript workflow.  Values outside the
    convex hull are filled from a nearest-neighbor interpolation by default.
    """

    coordinates = np.asarray(points, dtype=float)
    observed = np.asarray(values, dtype=float)
    if coordinates.ndim != 2 or coordinates.shape[1] != 2:
        raise ValueError("points must have shape (n, 2)")
    if observed.shape != (coordinates.shape[0],):
        raise ValueError("values must contain one number per point")
    if len(coordinates) < 4 and method == "cubic":
        raise ValueError("cubic interpolation requires at least four points")
    if not np.isfinite(coordinates).all() or not np.isfinite(observed).all():
        raise ValueError("points and values must be finite")
    if grid_size < 2:
        raise ValueError("grid_size must be at least 2")
    axis = np.linspace(domain_min, domain_max, grid_size)
    grid_x, grid_y = np.meshgrid(axis, axis, indexing="xy")
    try:
        grid_z = griddata(coordinates, observed, (grid_x, grid_y), method=method)
    except Exception as exc:  # SciPy emits several Qhull exception subclasses.
        raise ValueError(
            f"{method} interpolation failed; check that points are not collinear"
        ) from exc
    if fill_boundaries and np.isnan(grid_z).any():
        nearest = griddata(coordinates, observed, (grid_x, grid_y), method="nearest")
        grid_z = np.where(np.isnan(grid_z), nearest, grid_z)
    if np.isnan(grid_z).any():
        raise ValueError(
            "interpolation left missing cells; enable fill_boundaries "
            "or revise the domain"
        )
    result = np.asarray(grid_z, dtype=float)
    if normalize:
        result = normalize_surface(result)
    return np.asarray(grid_x, dtype=float), np.asarray(grid_y, dtype=float), result


def build_surface(config: SimulationConfig | None = None) -> SurfaceModel:
    """Generate a complete synthetic point-to-surface example."""

    settings = config if config is not None else SimulationConfig()
    points, centers = generate_point_pattern(settings)
    density = local_neighbor_density(points, settings.density_radius)
    grid_x, grid_y, grid_z = interpolate_surface(
        points,
        density,
        grid_size=settings.grid_size,
        domain_min=settings.domain_min,
        domain_max=settings.domain_max,
        method=settings.interpolation_method,
        fill_boundaries=True,
        normalize=True,
    )
    return SurfaceModel(grid_x, grid_y, grid_z, points, density, centers)


def surface_from_grid(
    grid_z: ArrayLike,
    *,
    domain_min: float = 0.0,
    domain_max: float = 1.0,
    normalize: bool = True,
) -> SurfaceModel:
    """Create a :class:`SurfaceModel` from an already regularized grid."""

    z = np.asarray(grid_z, dtype=float)
    if z.ndim != 2 or min(z.shape) < 2:
        raise ValueError("grid_z must be a two-dimensional grid of at least 2 x 2")
    if not np.isfinite(z).all():
        raise ValueError("grid_z must be finite")
    if normalize:
        z = normalize_surface(z)
    y_axis = np.linspace(domain_min, domain_max, z.shape[0])
    x_axis = np.linspace(domain_min, domain_max, z.shape[1])
    grid_x, grid_y = np.meshgrid(x_axis, y_axis, indexing="xy")
    empty_points = np.empty((0, 2), dtype=float)
    return SurfaceModel(
        np.asarray(grid_x, dtype=float),
        np.asarray(grid_y, dtype=float),
        np.asarray(z, dtype=float),
        empty_points,
        np.empty(0, dtype=float),
        empty_points.copy(),
    )


def cavity_volume(
    grid_x: ArrayLike,
    grid_y: ArrayLike,
    grid_z: ArrayLike,
    *,
    baseline: float | None = None,
) -> float:
    """Approximate the volume between a regular surface and a horizontal baseline."""

    x = np.asarray(grid_x, dtype=float)
    y = np.asarray(grid_y, dtype=float)
    z = np.asarray(grid_z, dtype=float)
    if x.shape != y.shape or x.shape != z.shape or z.ndim != 2:
        raise ValueError("grid_x, grid_y, and grid_z must be matching 2-D arrays")
    reference = float(np.nanmin(z) if baseline is None else baseline)
    heights = np.maximum(z - reference, 0.0)
    cell_mean = (
        heights[:-1, :-1] + heights[1:, :-1] + heights[:-1, 1:] + heights[1:, 1:]
    ) / 4.0
    dx = np.abs(x[:-1, 1:] - x[:-1, :-1])
    dy = np.abs(y[1:, :-1] - y[:-1, :-1])
    return float(np.sum(cell_mean * dx * dy))


def ripley_k(
    points: ArrayLike,
    radii: ArrayLike,
    *,
    area: float | None = None,
) -> FloatArray:
    """Compute an uncorrected planar Ripley's K estimate.

    This diagnostic is intentionally simple and does not apply an edge
    correction; users should interpret values near the study boundary with
    caution.
    """

    coordinates = np.asarray(points, dtype=float)
    r = np.asarray(radii, dtype=float)
    if coordinates.ndim != 2 or coordinates.shape[1] != 2 or len(coordinates) < 2:
        raise ValueError("points must have shape (n, 2) with n >= 2")
    if r.ndim != 1 or np.any(r < 0.0):
        raise ValueError("radii must be a non-negative one-dimensional array")
    if area is None:
        width = np.ptp(coordinates[:, 0])
        height = np.ptp(coordinates[:, 1])
        area = float(width * height)
    if area <= 0.0:
        raise ValueError("area must be positive")
    distances = squareform(pdist(coordinates))
    np.fill_diagonal(distances, np.inf)
    n = len(coordinates)
    counts = np.asarray([(distances <= radius).sum() for radius in r], dtype=float)
    return np.asarray(float(area) * counts / (n * (n - 1)), dtype=float)


# ---------------------------------------------------------------------------
# The four canonical structures (M1--M4)
# ---------------------------------------------------------------------------

#: Labels of the four canonical structures of the accompanying study.  The
#: two dimensions are monocentric versus polycentric and concentrated versus
#: dispersed (following Meijers and Burger, 2010).
MODEL_LABELS: dict[str, str] = {
    "M1": "M1 monocentric-concentrated",
    "M2": "M2 polycentric-concentrated",
    "M3": "M3 monocentric-dispersed",
    "M4": "M4 polycentric-dispersed",
}

#: Preset parameters reproducing the characteristic point pattern of each
#: canonical structure.  One cluster means monocentric and several clusters
#: mean polycentric; a small ``cluster_std`` means concentrated and a large one
#: means dispersed.  The values are the stochastic counterparts of the
#: deterministic benchmark surfaces used to evaluate PTS.
MODEL_PRESETS: dict[str, dict[str, float]] = {
    "M1": {
        "num_points": 150,
        "num_clusters": 1,
        "cluster_std": 0.55,
        "noise_ratio": 0.15,
        "min_distance": 0.0,
        "seed": 42,
    },
    "M2": {
        "num_points": 200,
        "num_clusters": 4,
        "cluster_std": 0.50,
        "noise_ratio": 0.15,
        "min_distance": 4.0,
        "seed": 42,
    },
    "M3": {
        "num_points": 300,
        "num_clusters": 1,
        "cluster_std": 3.20,
        "noise_ratio": 0.40,
        "min_distance": 0.0,
        "seed": 42,
    },
    "M4": {
        "num_points": 350,
        "num_clusters": 5,
        "cluster_std": 2.60,
        "noise_ratio": 0.40,
        "min_distance": 4.0,
        "seed": 42,
    },
}


def model_config(model: str, **overrides: float) -> SimulationConfig:
    """Return the :class:`SimulationConfig` of a canonical structure.

    ``model`` is one of ``M1``--``M4``.  Any preset value may be overridden
    through keyword arguments, which is what the four buttons of the desktop
    interface use.
    """

    key = str(model).strip().upper()
    if key not in MODEL_PRESETS:
        raise ValueError(
            f"unknown model {model!r}; expected one of {sorted(MODEL_PRESETS)}"
        )
    settings: dict[str, float] = dict(MODEL_PRESETS[key])
    settings.update(overrides)
    settings["num_points"] = int(settings["num_points"])
    settings["num_clusters"] = int(settings["num_clusters"])
    settings["seed"] = int(settings["seed"])
    return SimulationConfig(**settings)


def build_model_surface(model: str, **overrides: float) -> SurfaceModel:
    """Generate the point pattern and surface of a canonical structure."""

    return build_surface(model_config(model, **overrides))


@dataclass(frozen=True)
class StandardizationReport:
    """Record of the affine standardisation applied to imported observations."""

    source_extent: tuple[float, float, float, float]
    target_extent: tuple[float, float, float, float]
    scale_x: float
    scale_y: float
    value_range: tuple[float, float]
    preserve_aspect: bool


def standardize_points(
    points: ArrayLike,
    values: ArrayLike,
    *,
    domain_max: float = 100.0,
    preserve_aspect: bool = False,
) -> tuple[FloatArray, FloatArray, StandardizationReport]:
    """Map imported observations onto the standard square domain.

    The external margin is removed and the observed extent is affinely mapped
    onto ``[0, domain_max]`` on both axes, mirroring the night-time-light
    preparation of the accompanying study: after standardisation, data sets of
    different extent, shape, and units are computationally comparable.  The
    attribute values are min--max normalised to ``[0, 1]`` so that the threshold
    scan and the response measurements are unaffected by the original units.

    The aspect ratio is not preserved unless ``preserve_aspect`` is set, and
    the applied scales are always reported in the returned
    :class:`StandardizationReport`.
    """

    coordinates = np.asarray(points, dtype=float)
    observed = np.asarray(values, dtype=float)
    if coordinates.ndim != 2 or coordinates.shape[1] != 2:
        raise ValueError("points must have shape (n, 2)")
    if observed.shape != (coordinates.shape[0],):
        raise ValueError("values must contain one number per point")
    if not np.isfinite(coordinates).all() or not np.isfinite(observed).all():
        raise ValueError("points and values must be finite")
    if coordinates.shape[0] < 4:
        raise ValueError("at least four observations are required to build a surface")
    if domain_max <= 0.0:
        raise ValueError("domain_max must be positive")

    x_min, y_min = coordinates.min(axis=0)
    x_max, y_max = coordinates.max(axis=0)
    width = float(x_max - x_min)
    height = float(y_max - y_min)
    if width <= 0.0 or height <= 0.0:
        raise ValueError("the observations must span a non-degenerate extent")

    if preserve_aspect:
        scale = domain_max / max(width, height)
        scale_x = scale_y = float(scale)
        offset_x = 0.5 * (domain_max - width * scale)
        offset_y = 0.5 * (domain_max - height * scale)
    else:
        scale_x = float(domain_max / width)
        scale_y = float(domain_max / height)
        offset_x = offset_y = 0.0

    standardized = np.column_stack(
        (
            (coordinates[:, 0] - x_min) * scale_x + offset_x,
            (coordinates[:, 1] - y_min) * scale_y + offset_y,
        )
    )

    value_min = float(observed.min())
    value_max = float(observed.max())
    if value_max <= value_min:
        raise ValueError(
            "the selected attribute is constant and carries no vertical structure"
        )
    normalized = (observed - value_min) / (value_max - value_min)

    report = StandardizationReport(
        source_extent=(float(x_min), float(x_max), float(y_min), float(y_max)),
        target_extent=(0.0, float(domain_max), 0.0, float(domain_max)),
        scale_x=scale_x,
        scale_y=scale_y,
        value_range=(value_min, value_max),
        preserve_aspect=bool(preserve_aspect),
    )
    return (
        np.asarray(standardized, dtype=float),
        np.asarray(normalized, dtype=float),
        report,
    )
