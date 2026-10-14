"""Anchors proving that the PTS numerics are unchanged by the 3.1 release."""

import numpy as np
import pytest

from wfm4cities import progressive_threshold_scan


def _block_surface() -> np.ndarray:
    surface = np.zeros((10, 10))
    surface[4:6, 4:6] = 1.0
    return surface


def test_known_block_surface_anchor() -> None:
    """Four of one hundred cells, one component, half the volume left at 0.5."""

    result = progressive_threshold_scan(_block_surface(), np.array([0.0, 0.5, 1.0]))
    index = int(np.argmin(np.abs(result.thresholds - 0.5)))
    assert result.thresholds[index] == pytest.approx(0.5)
    assert result.A[index] == pytest.approx(4 / 100)
    assert result.V[index] == pytest.approx(0.5)
    assert result.N[index] == 1
    assert result.L[index] == pytest.approx(1.0)


def test_end_points_of_the_response_trajectories() -> None:
    result = progressive_threshold_scan(_block_surface(), np.array([0.0, 0.5]))
    assert result.A[0] == pytest.approx(1.0)
    assert result.V[0] == pytest.approx(1.0)


def test_strict_rule_excludes_the_zero_background() -> None:
    inclusive = progressive_threshold_scan(
        _block_surface(), np.array([0.0, 0.5]), rule="inclusive"
    )
    strict = progressive_threshold_scan(
        _block_surface(), np.array([0.0, 0.5]), rule="strict"
    )
    assert inclusive.A[0] == pytest.approx(1.0)
    assert strict.A[0] == pytest.approx(4 / 100)
