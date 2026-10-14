"""Ripley's K panel: the CSR band and the clustering signature."""

import numpy as np
import pytest

from wfm4cities.gui import ripley_envelope


def _clustered() -> np.ndarray:
    generator = np.random.default_rng(20261014)
    centres = np.array([[1.0, 1.0], [8.0, 2.0], [2.0, 8.0], [8.0, 8.0]])
    parts = [generator.normal(c, 0.35, size=(40, 2)) for c in centres]
    return np.clip(np.vstack(parts), 0.0, 10.0)


def test_envelope_shapes_and_band_ordering() -> None:
    points = _clustered()
    radii = np.linspace(0.2, 4.0, 30)
    observed, mean, low, high = ripley_envelope(points, radii)
    for array in (observed, mean, low, high):
        assert array.shape == radii.shape
    assert np.all(low <= mean)
    assert np.all(mean <= high)


def test_clustering_lifts_k_above_the_csr_reference() -> None:
    points = _clustered()
    radii = np.linspace(0.2, 4.0, 30)
    observed, mean, _, _ = ripley_envelope(points, radii)
    assert observed[5] > mean[5]


def test_envelope_needs_enough_points() -> None:
    with pytest.raises(ValueError, match="at least four"):
        ripley_envelope(np.array([[0.0, 0.0], [1.0, 1.0]]), np.linspace(0.1, 1.0, 5))


def test_envelope_is_reproducible() -> None:
    points = _clustered()
    radii = np.linspace(0.2, 4.0, 20)
    first = ripley_envelope(points, radii)[0]
    second = ripley_envelope(points, radii)[0]
    assert np.allclose(first, second)
