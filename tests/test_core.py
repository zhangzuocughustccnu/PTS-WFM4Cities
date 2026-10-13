import numpy as np
import pytest

from wfm4cities.core import (
    SimulationConfig,
    build_surface,
    cavity_volume,
    generate_cluster_centers,
    interpolate_surface,
    normalize_surface,
    ripley_k,
)


def test_normalize_surface_range() -> None:
    result = normalize_surface([[2.0, 4.0], [6.0, 10.0]])
    assert result.min() == pytest.approx(0.0)
    assert result.max() == pytest.approx(1.0)


def test_constant_surface_normalizes_to_zero() -> None:
    assert np.array_equal(normalize_surface(np.ones((3, 3))), np.zeros((3, 3)))


def test_synthetic_surface_is_deterministic_and_finite() -> None:
    config = SimulationConfig(
        num_points=60,
        noise_ratio=0.25,
        num_clusters=3,
        grid_size=32,
        seed=2026,
    )
    first = build_surface(config)
    second = build_surface(config)
    assert first.grid_z.shape == (32, 32)
    assert np.isfinite(first.grid_z).all()
    assert np.array_equal(first.points, second.points)
    assert np.array_equal(first.grid_z, second.grid_z)


def test_cubic_interpolation_fills_boundaries() -> None:
    points = np.asarray([[1.0, 1.0], [1.0, 9.0], [9.0, 1.0], [9.0, 9.0], [5.0, 5.0]])
    values = np.asarray([0.0, 0.2, 0.4, 0.6, 1.0])
    _, _, grid = interpolate_surface(points, values, grid_size=24)
    assert grid.shape == (24, 24)
    assert np.isfinite(grid).all()
    assert 0.0 <= grid.min() <= grid.max() <= 1.0


def test_impossible_center_spacing_has_actionable_error() -> None:
    with pytest.raises(ValueError, match="reduce min_distance"):
        generate_cluster_centers(
            5,
            20.0,
            domain_min=0.0,
            domain_max=1.0,
            rng=np.random.default_rng(1),
            max_attempts=50,
        )


def test_cavity_volume_of_unit_plane() -> None:
    axis = np.asarray([0.0, 1.0])
    x, y = np.meshgrid(axis, axis)
    assert cavity_volume(x, y, np.ones((2, 2)), baseline=0.0) == pytest.approx(1.0)


def test_ripley_k_shape_and_zero_radius() -> None:
    points = np.asarray([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    result = ripley_k(points, [0.0, 1.1], area=1.0)
    assert result.shape == (2,)
    assert result[0] == pytest.approx(0.0)
    assert result[1] > 0.0
