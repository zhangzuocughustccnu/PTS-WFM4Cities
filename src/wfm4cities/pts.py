"""Progressive Threshold Scanning (PTS) metrics.

The implementation follows the definitions used in the associated manuscript:
projected-area ratio A(h), normalized excess volume V(h), eight-neighbor
component count N(h), and largest-component ratio L(h).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.ndimage import label

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]
ThresholdRule = Literal["inclusive", "strict"]

FEATURE_NAMES = (
    "V_0.2",
    "A_0.2",
    "A_0.4",
    "A_0.6",
    "V_0.4",
    "L_0.4",
    "N_0.4",
    "L_auc",
    "V_auc",
    "h_A10",
)


@dataclass(frozen=True)
class PTSResult:
    """Four PTS response trajectories evaluated at a common threshold vector."""

    thresholds: FloatArray
    area: FloatArray
    excess_volume: FloatArray
    component_count: IntArray
    largest_component_ratio: FloatArray
    rule: ThresholdRule
    connectivity: int

    def __post_init__(self) -> None:
        size = len(self.thresholds)
        arrays = (
            self.area,
            self.excess_volume,
            self.component_count,
            self.largest_component_ratio,
        )
        if self.thresholds.ndim != 1 or size < 2:
            raise ValueError(
                "thresholds must be a one-dimensional vector of length >= 2"
            )
        if any(array.shape != (size,) for array in arrays):
            raise ValueError("all PTS trajectories must match the threshold vector")

    @property
    def A(self) -> FloatArray:
        return self.area

    @property
    def V(self) -> FloatArray:
        return self.excess_volume

    @property
    def N(self) -> IntArray:
        return self.component_count

    @property
    def L(self) -> FloatArray:
        return self.largest_component_ratio

    def as_columns(self) -> dict[str, FloatArray | IntArray]:
        """Return stable column names for CSV or DataFrame construction."""

        return {
            "threshold": self.thresholds,
            "A": self.area,
            "V": self.excess_volume,
            "N": self.component_count,
            "L": self.largest_component_ratio,
        }


def threshold_vector(
    count: int = 51,
    *,
    minimum: float = 0.0,
    maximum: float = 0.95,
) -> FloatArray:
    """Create an evenly spaced threshold vector."""

    if count < 2:
        raise ValueError("count must be at least 2")
    if maximum <= minimum:
        raise ValueError("maximum must be greater than minimum")
    return np.asarray(np.linspace(minimum, maximum, count), dtype=float)


def progressive_threshold_scan(
    surface: ArrayLike,
    thresholds: ArrayLike | None = None,
    *,
    threshold_count: int = 51,
    threshold_min: float = 0.0,
    threshold_max: float = 0.95,
    rule: ThresholdRule = "inclusive",
    connectivity: int = 8,
    domain_mask: ArrayLike | None = None,
) -> PTSResult:
    """Scan a regular scalar surface across an ordered threshold domain.

    ``inclusive`` applies ``z >= h`` and is used for the controlled archetype
    analysis.  ``strict`` applies ``z > h`` and is useful when zero-valued
    background cells must be excluded at h=0, as in the manuscript's city
    image example.
    """

    z = np.asarray(surface, dtype=float)
    if z.ndim != 2:
        raise ValueError("surface must be two-dimensional")
    if not np.isfinite(z).all():
        raise ValueError("surface must contain only finite values")
    if np.any(z < 0.0):
        raise ValueError("surface values must be non-negative")
    if rule not in {"inclusive", "strict"}:
        raise ValueError("rule must be 'inclusive' or 'strict'")
    if connectivity not in {4, 8}:
        raise ValueError("connectivity must be 4 or 8")

    if thresholds is None:
        h = threshold_vector(
            threshold_count, minimum=threshold_min, maximum=threshold_max
        )
    else:
        h = np.asarray(thresholds, dtype=float)
    if h.ndim != 1 or len(h) < 2 or np.any(np.diff(h) <= 0.0):
        raise ValueError("thresholds must be a strictly increasing 1-D vector")
    if not np.isfinite(h).all():
        raise ValueError("thresholds must be finite")

    if domain_mask is None:
        domain = np.ones(z.shape, dtype=bool)
    else:
        domain = np.asarray(domain_mask, dtype=bool)
        if domain.shape != z.shape:
            raise ValueError("domain_mask must have the same shape as surface")
    domain_size = int(domain.sum())
    if domain_size == 0:
        raise ValueError("domain_mask contains no included cells")
    total_intensity = float(z[domain].sum())
    if total_intensity <= 0.0:
        raise ValueError("surface must have positive total intensity in the domain")

    area = np.empty(len(h), dtype=float)
    volume = np.empty(len(h), dtype=float)
    count = np.empty(len(h), dtype=np.int64)
    largest = np.empty(len(h), dtype=float)
    structure = (
        np.ones((3, 3), dtype=np.uint8)
        if connectivity == 8
        else np.asarray([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8)
    )

    for index, level in enumerate(h):
        retained = (z >= level) if rule == "inclusive" else (z > level)
        retained &= domain
        retained_size = int(retained.sum())
        area[index] = retained_size / domain_size
        volume[index] = (
            float(np.maximum(z[domain] - level, 0.0).sum()) / total_intensity
        )
        labels, number = label(retained, structure=structure)
        count[index] = number
        if number and retained_size:
            sizes = np.bincount(labels.ravel())[1:]
            largest[index] = float(sizes.max()) / retained_size
        else:
            largest[index] = 0.0

    return PTSResult(h, area, volume, count, largest, rule, connectivity)


def _linear_value(x: FloatArray, y: FloatArray, target: float) -> float:
    if not float(x[0]) <= target <= float(x[-1]):
        raise ValueError(f"target threshold {target} lies outside the scan domain")
    return float(np.interp(target, x, y))


def _first_crossing(x: FloatArray, y: FloatArray, target: float = 0.10) -> float:
    candidates = np.flatnonzero(y < target)
    if not len(candidates):
        return float("nan")
    upper = int(candidates[0])
    if upper == 0:
        return float(x[0])
    lower = upper - 1
    if y[upper] == y[lower]:
        return float(x[upper])
    fraction = (target - y[lower]) / (y[upper] - y[lower])
    return float(x[lower] + fraction * (x[upper] - x[lower]))


def extract_features(result: PTSResult) -> dict[str, float]:
    """Extract the manuscript's ten fixed PTS summary features."""

    h = result.thresholds
    a = result.area
    v = result.excess_volume
    n = result.component_count
    ell = result.largest_component_ratio
    nearest_04 = int(np.argmin(np.abs(h - 0.4)))
    width = float(h[-1] - h[0])
    trapezoid = getattr(np, "trapezoid", None)
    if trapezoid is None:  # NumPy < 2.0 compatibility
        trapezoid = np.trapz
    features = {
        "V_0.2": _linear_value(h, v, 0.2),
        "A_0.2": _linear_value(h, a, 0.2),
        "A_0.4": _linear_value(h, a, 0.4),
        "A_0.6": _linear_value(h, a, 0.6),
        "V_0.4": _linear_value(h, v, 0.4),
        "L_0.4": _linear_value(h, ell, 0.4),
        "N_0.4": float(n[nearest_04]),
        "L_auc": float(trapezoid(ell, h) / width),
        "V_auc": float(trapezoid(v, h) / width),
        "h_A10": _first_crossing(h, a, target=0.10),
    }
    return {name: features[name] for name in FEATURE_NAMES}
