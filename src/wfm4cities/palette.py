"""Colour scheme for PTS-WFM4Cities 3.1.

The surface ramp runs from deep blue for the lowest value to deep red for the
highest, inheriting the colour bar of the four-model figure of the accompanying
study:

    low  #1B3A78 -> #4A8FC0 -> #7FC4A0 -> #F0C948 -> #B0291C  high

The categorical colours used for up to four series are the ones already used by
the city figure of that study, so a figure drawn here drops straight into the
manuscript.

Change a value in this module and the interface, the command line and the
exported figures follow, because all of them read it.
"""

from __future__ import annotations

from matplotlib.colors import LinearSegmentedColormap

#: Surface-height ramp, ordered from the lowest to the highest value.  The five
#: anchors are exactly the ones used by the accompanying study.
SURFACE_RAMP: tuple[str, ...] = (
    "#1B3A78",
    "#4A8FC0",
    "#7FC4A0",
    "#F0C948",
    "#B0291C",
)

#: Fill of the two-dimensional domain in the point-pattern panel: the light blue
#: of the four-model figure of the accompanying study.
DOMAIN_FILL = "#AACCEE"

#: Grey panel background used when panels are assembled into a composite figure.
FIGURE_PANEL = "#D9D9D9"

#: Primary colour of the point pattern: the orange sampled from the four-model
#: figure of the accompanying study, drawn on its light-blue domain.
POINT_COLOR = "#F08830"

#: Colour of the cluster centres: a deeper orange, so the centre still stands
#: out among the observations of the same hue.
CENTER_COLOR = "#D9721C"

#: Geometric responses: blue-black for the projected-area fraction and dark
#: orange for the normalised exceedance volume.
GEOMETRY_A_COLOR = "#16263D"
GEOMETRY_V_COLOR = "#C1440E"

#: Pale cyan of the water surface in the three-dimensional views, as in the
#: city figure of the accompanying study.
WATER_COLOR = "#CBE3F2"

#: Face colour of the result panels and of the drawing area.
PANEL_FACE = "#F7F7F7"

#: Grid lines and spines.
GRID_GRAY = "#B5B5B5"
SPINE_GRAY = "#4A4A4A"

#: Categorical colours and markers for up to four series (for example the four
#: example cities of the accompanying study).
CITY_COLORS: tuple[str, ...] = ("#4D79A8", "#E28E2D", "#59A14F", "#B07AA1")
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
