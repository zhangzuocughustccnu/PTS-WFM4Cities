"""The four canonical structures exposed as one-click presets."""

import numpy as np
import pytest

from wfm4cities.core import (
    MODEL_LABELS,
    MODEL_PRESETS,
    build_model_surface,
    generate_point_pattern,
    model_config,
)

MODELS = ("M1", "M2", "M3", "M4")


@pytest.mark.parametrize("model", MODELS)
def test_every_model_builds_a_normalised_surface(model: str) -> None:
    surface = build_model_surface(model)
    assert surface.grid_z.shape == (100, 100)
    assert surface.grid_z.min() == pytest.approx(0.0)
    assert surface.grid_z.max() == pytest.approx(1.0)


def test_monocentric_models_have_exactly_one_centre() -> None:
    for model in ("M1", "M3"):
        _, centers = generate_point_pattern(model_config(model))
        assert len(centers) == 1


def test_polycentric_models_have_several_centres() -> None:
    for model in ("M2", "M4"):
        _, centers = generate_point_pattern(model_config(model))
        assert len(centers) >= 3


def test_presets_encode_the_two_dimensions() -> None:
    assert MODEL_PRESETS["M1"]["num_clusters"] == 1
    assert MODEL_PRESETS["M3"]["num_clusters"] == 1
    assert MODEL_PRESETS["M2"]["num_clusters"] > 1
    assert MODEL_PRESETS["M4"]["num_clusters"] > 1
    assert MODEL_PRESETS["M1"]["cluster_std"] < MODEL_PRESETS["M3"]["cluster_std"]
    assert MODEL_PRESETS["M2"]["cluster_std"] < MODEL_PRESETS["M4"]["cluster_std"]
    for key, label in MODEL_LABELS.items():
        assert key in label


def test_models_are_reproducible_and_can_be_overridden() -> None:
    first = build_model_surface("M2").grid_z
    second = build_model_surface("M2").grid_z
    assert np.allclose(first, second)
    assert not np.allclose(first, build_model_surface("M2", seed=7).grid_z)
    assert model_config("m1").num_clusters == 1
    assert model_config("M1", num_points=80).num_points == 80


def test_unknown_model_is_rejected() -> None:
    with pytest.raises(ValueError, match="unknown model"):
        model_config("M9")
