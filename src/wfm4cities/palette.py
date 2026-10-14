"""Colour scheme for PTS--WFM4Cities 3.1.

The stops follow the colour families of the four-model figure of the
accompanying study -- a blue-to-red surface ramp with an orange point accent --
but every stop is chosen so that it survives greyscale printing and stays
distinguishable for readers with colour-vision deficiency.

Change a value here and the GUI, the command line, and every exported figure
follow, because all of them read this single module.
"""

from __future__ import annotations

from matplotlib.colors import LinearSegmentedColormap

#: Surface-height ramp, ordered from the lowest to the highest value.
SURFACE_RAMP: tuple[str, ...] = (
    "#1B4F9C",
    "#2E8BC0",
    "#4FB08A",
    "#E3C64B",
    "#C8452F",
)

#: Primary colour of the point pattern.
POINT_COLOR = "#E8842B"

#: Colour of the cluster centres.
CENTER_COLOR = "#B03A2E"

#: Colour of the water surface in the three-dimensional views.
WATER_COLOR = "#7FC4E8"

#: Face colour of the result panels and of the drawing area.
PANEL_FACE = "#F4F4F4"

#: Grid lines and spines.
GRID_GRAY = "#B5B5B5"
SPINE_GRAY = "#595959"

#: Categorical colours and markers used for up to four series (for example the
#: four example cities of the accompanying study).
CITY_COLORS: tuple[str, ...] = ("#1B4F9C", "#E8842B", "#2E8B57", "#8E5AA8")
CITY_MARKERS: tuple[str, ...] = ("o", "s", "^", "D")


def surface_cmap(name: str = "pts_surface") -> LinearSegmentedColormap:
    """Return the publication colour map for surface height."""

    return LinearSegmentedColormap.from_list(name, list(SURFACE_RAMP), N=256)


def series_color(index: int) -> str:
    """Return the categorical colour for ``index``, cycling if necessary."""

    return CITY_COLORS[index % len(CITY_COLORS)]


def series_marker(index: int) -> str:
    """Return the marker for ``index``, cycling if necessary."""

    return CITY_MARKERS[index % len(CITY_MARKERS)]
