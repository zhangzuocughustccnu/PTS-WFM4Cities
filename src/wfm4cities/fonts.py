"""Publication fonts: Times New Roman for Latin, SimSun/STSong for Chinese.

The font files are deliberately **not** shipped with the package.  Times New
Roman and SimSun are proprietary and may not be redistributed, so the module
uses the copies that are already installed on the system.  On a machine without
them (typically Linux) set the ``PTS_FONT_DIR`` environment variable to a folder
holding the font files and they are registered at import time.
"""

from __future__ import annotations

import os
from pathlib import Path

#: Preferred Latin family, as used by the accompanying study.
LATIN_FONT = "Times New Roman"

#: Handwriting-free Chinese families, in order of preference.
CJK_FONTS: tuple[str, ...] = (
    "SimSun",
    "STSong",
    "NSimSun",
    "SimHei",
    "Microsoft YaHei",
    "Noto Sans CJK SC",
    "Source Han Sans SC",
)

#: Last resort for machines that have none of the families above.
FALLBACK_FONT = "DejaVu Sans"

_FONT_SUFFIXES = {".ttf", ".ttc", ".otf"}


def register_font_files(directory: str | os.PathLike[str] | None = None) -> list[str]:
    """Register every font file in ``directory`` with Matplotlib.

    ``directory`` defaults to the ``PTS_FONT_DIR`` environment variable.  The
    function is a no-op when the directory does not exist, so it is safe to call
    on every start.
    """

    from matplotlib import font_manager

    target = (
        Path(directory)
        if directory is not None
        else Path(os.environ.get("PTS_FONT_DIR", ""))
    )
    if not str(target) or not target.is_dir():
        return []
    registered: list[str] = []
    for path in sorted(target.iterdir()):
        if path.suffix.lower() in _FONT_SUFFIXES:
            try:
                font_manager.fontManager.addfont(str(path))
                registered.append(path.name)
            except Exception:  # pragma: no cover - unreadable font file
                continue
    return registered


def resolved_families() -> list[str]:
    """Return the font families that are actually available, in order."""

    from matplotlib import font_manager

    available = {font.name for font in font_manager.fontManager.ttflist}
    families = [name for name in (LATIN_FONT, *CJK_FONTS) if name in available]
    if FALLBACK_FONT in available and FALLBACK_FONT not in families:
        families.append(FALLBACK_FONT)
    return families or [FALLBACK_FONT]


def apply(directory: str | os.PathLike[str] | None = None) -> list[str]:
    """Register the extra fonts, set the Matplotlib families, and report them.

    Matplotlib resolves missing glyphs by walking the family list, so Latin text
    is drawn with Times New Roman and Chinese text falls through to SimSun.
    """

    from matplotlib import rcParams

    extra = register_font_files(directory)
    families = resolved_families()
    rcParams["font.family"] = families
    rcParams["font.serif"] = families
    rcParams["axes.unicode_minus"] = False
    # Compact publication typography: the panels of the desktop interface and of
    # the exported figures are dense, so the defaults are tightened here once.
    rcParams["axes.titlesize"] = 10.0
    rcParams["axes.labelsize"] = 8.5
    rcParams["xtick.labelsize"] = 7.5
    rcParams["ytick.labelsize"] = 7.5
    rcParams["legend.fontsize"] = 7.5
    rcParams["axes.titlepad"] = 2.5
    rcParams["axes.labelpad"] = 1.5
    if extra:
        families = [*families, "registered: " + ", ".join(extra)]
    return families
