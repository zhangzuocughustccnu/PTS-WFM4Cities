"""Affine standardisation of imported point observations."""

import numpy as np
import pytest

from wfm4cities import standardize_points


def _sample() -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(0)
    points = np.column_stack((rng.uniform(-3, 7, 40), rng.uniform(100, 140, 40)))
    return points, rng.uniform(5, 25, 40)


def test_affine_mapping_fills_the_standard_square() -> None:
    points, values = _sample()
    mapped, normalised, report = standardize_points(points, values)
    assert np.min(mapped[:, 0]) == pytest.approx(0.0)
    assert np.max(mapped[:, 0]) == pytest.approx(100.0)
    assert np.min(mapped[:, 1]) == pytest.approx(0.0)
    assert np.max(mapped[:, 1]) == pytest.approx(100.0)
    assert np.min(normalised) == pytest.approx(0.0)
    assert np.max(normalised) == pytest.approx(1.0)
    assert report.source_extent[0] == pytest.approx(np.min(points[:, 0]))
    assert report.scale_x != pytest.approx(report.scale_y)


def test_preserve_aspect_keeps_the_ratio() -> None:
    points, values = _sample()
    mapped, _, report = standardize_points(points, values, preserve_aspect=True)
    before = np.ptp(points[:, 0]) / np.ptp(points[:, 1])
    after = np.ptp(mapped[:, 0]) / np.ptp(mapped[:, 1])
    assert after == pytest.approx(before)
    assert report.scale_x == pytest.approx(report.scale_y)
    assert mapped.min() >= -1e-9
    assert mapped.max() <= 100.0 + 1e-9


def test_constant_attribute_is_rejected() -> None:
    points, _ = _sample()
    with pytest.raises(ValueError, match="constant"):
        standardize_points(points, np.full(len(points), 3.0))


def test_degenerate_extent_is_rejected() -> None:
    points = np.array([[0.0, 0.0], [0.0, 1.0], [0.0, 2.0], [0.0, 3.0]])
    with pytest.raises(ValueError, match="degenerate"):
        standardize_points(points, np.arange(4.0))


def test_too_few_observations_are_rejected() -> None:
    with pytest.raises(ValueError, match="at least four"):
        standardize_points(np.array([[0.0, 0.0], [1.0, 1.0]]), np.array([1.0, 2.0]))


def test_standardisation_is_idempotent() -> None:
    points, values = _sample()
    mapped, normalised, _ = standardize_points(points, values)
    again, values_again, _ = standardize_points(mapped, normalised)
    assert np.allclose(mapped, again)
    assert np.allclose(normalised, values_again)
