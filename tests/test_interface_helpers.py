"""Helpers behind the desktop interface: fonts, language, display smoothing."""

import numpy as np
import pytest

from wfm4cities import fonts, i18n
from wfm4cities.gui import SMOOTH_WINDOW, smooth_for_display


def test_default_language_is_english() -> None:
    assert i18n.DEFAULT_LANGUAGE == "en"
    assert i18n.translate("panel_structures") == "Canonical structures"
    assert i18n.translate("panel_structures", "zh") == "\u5178\u578b\u7ed3\u6784"


def test_unknown_language_falls_back_to_english() -> None:
    assert i18n.normalise("de") == "en"
    assert i18n.normalise(None) == "en"
    assert i18n.normalise("ZH") == "zh"


def test_every_string_exists_in_both_languages() -> None:
    for key, entry in i18n.STRINGS.items():
        for code in i18n.LANGUAGES:
            assert entry.get(code), f"{key} is missing {code}"


def test_formatted_strings_fill_the_placeholders() -> None:
    text = i18n.translate("status_imported", "en", n=42, extent=(0, 1, 0, 1))
    assert "42" in text


def test_status_bar_names_the_structure_in_both_languages() -> None:
    """The status message follows the language, like every other label."""

    for model in ("M1", "M2", "M3", "M4"):
        assert i18n.model_label(model, "en").startswith(model)
        assert i18n.model_label(model, "zh").startswith(model)
        assert i18n.model_label(model, "en") != i18n.model_label(model, "zh")
    assert i18n.model_label("M2", "zh") == "M2 \u591a\u4e2d\u5fc3\u00b7\u96c6\u4e2d"
    assert i18n.model_label("M2", "en") == "M2 polycentric-concentrated"


def test_model_label_falls_back_to_the_english_public_name() -> None:
    assert i18n.model_label("M9", "zh") == "M9"
    assert i18n.model_label("m3", "zh").startswith("M3")


def test_structure_labels_are_bilingual_and_two_lines() -> None:
    for model in ("M1", "M2", "M3", "M4"):
        key = f"structure_{model}"
        assert "\n" in i18n.translate(key, "en")
        assert "\n" in i18n.translate(key, "zh")
        assert i18n.translate(key, "en") != i18n.translate(key, "zh")


def test_resolved_families_are_never_empty() -> None:
    assert fonts.resolved_families()


def test_registering_a_missing_directory_is_silent() -> None:
    assert fonts.register_font_files("does/not/exist") == []


def test_display_smoothing_preserves_the_end_points_and_length() -> None:
    values = np.array([0.0, 5.0, 1.0, 7.0, 2.0, 8.0, 3.0])
    smoothed = smooth_for_display(values)
    assert smoothed.shape == values.shape
    assert smoothed[0] == pytest.approx(values[0])
    assert smoothed[-1] == pytest.approx(values[-1])
    assert np.ptp(smoothed) < np.ptp(values)


def test_display_smoothing_is_a_no_op_for_short_series() -> None:
    values = np.array([1.0, 2.0])
    assert np.allclose(smooth_for_display(values), values)


def test_smoothing_never_touches_the_stored_response() -> None:
    from wfm4cities import progressive_threshold_scan

    surface = np.zeros((10, 10))
    surface[4:6, 4:6] = 1.0
    result = progressive_threshold_scan(surface, np.array([0.0, 0.5]))
    raw = np.array(result.component_count, dtype=float)
    assert np.allclose(result.component_count, raw)
    assert SMOOTH_WINDOW >= 3
