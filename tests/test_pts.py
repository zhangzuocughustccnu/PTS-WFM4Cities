import numpy as np
import pytest

from wfm4cities.pts import (
    FEATURE_NAMES,
    extract_features,
    progressive_threshold_scan,
)


def test_area_and_volume_are_nonincreasing() -> None:
    surface = np.asarray([[0.0, 0.2, 0.4], [0.1, 0.5, 0.9], [0.0, 0.6, 1.0]])
    result = progressive_threshold_scan(surface)
    assert np.all(np.diff(result.A) <= 1e-12)
    assert np.all(np.diff(result.V) <= 1e-12)
    assert np.all((0.0 <= result.L) & (result.L <= 1.0))
    assert np.issubdtype(result.N.dtype, np.integer)


def test_strict_rule_excludes_zero_background_at_h_zero() -> None:
    surface = np.asarray([[0.0, 0.0], [0.0, 1.0]])
    thresholds = np.asarray([0.0, 0.5])
    inclusive = progressive_threshold_scan(surface, thresholds)
    strict = progressive_threshold_scan(surface, thresholds, rule="strict")
    assert inclusive.A[0] == pytest.approx(1.0)
    assert strict.A[0] == pytest.approx(0.25)


def test_connectivity_rule_changes_diagonal_components() -> None:
    surface = np.asarray([[1.0, 0.0], [0.0, 1.0]])
    thresholds = np.asarray([0.5, 0.9])
    four = progressive_threshold_scan(surface, thresholds, connectivity=4)
    eight = progressive_threshold_scan(surface, thresholds, connectivity=8)
    assert four.N[0] == 2
    assert eight.N[0] == 1


def test_feature_contract_and_finite_values() -> None:
    axis = np.linspace(-1.0, 1.0, 40)
    x, y = np.meshgrid(axis, axis)
    surface = np.exp(-4.0 * (x**2 + y**2))
    result = progressive_threshold_scan(surface)
    features = extract_features(result)
    assert tuple(features) == FEATURE_NAMES
    assert all(np.isfinite(value) for value in features.values())


def test_domain_mask_controls_area_denominator() -> None:
    surface = np.ones((3, 3))
    domain = np.zeros((3, 3), dtype=bool)
    domain[:2, :2] = True
    result = progressive_threshold_scan(
        surface, [0.0, 0.5], domain_mask=domain, rule="strict"
    )
    assert result.A[0] == pytest.approx(1.0)
    assert result.N[0] == 1
