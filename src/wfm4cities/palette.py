"""Colour scheme for PTS-WFM4Cities 3.1.

The surface ramp is the black-to-yellow ramp of the accompanying study's
city figure and its supplementary city map, so that the package, the desktop
interface and every exported figure use one palette:

    low  #000000 -> #5E140B -> #C14220 -> #F29E2D -> #F8DD34  high

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
    "#000000",
    "#5E140B",
    "#C14220",
    "#F29E2D",
    "#F8DD34",
)

#: Fill of the two-dimensional domain in the point-pattern panel: a light warm
#: tone that keeps the observations legible against the black low end of the
#: ramp.
DOMAIN_FILL = "#F5EFE6"

#: Grey panel background used when panels are assembled into a composite figure.
FIGURE_PANEL = "#D9D9D9"

#: Primary colour of the point pattern (the orange of the ramp).
POINT_COLOR = "#F29E2D"

#: Colour of the cluster centres.
CENTER_COLOR = "#C14220"

#: Pale cyan of the water surface in the three-dimensional views, as in the
#: city figure of the accompanying study.
WATER_COLOR = "#BFE3F0"

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