"""Legacy-compatible launcher.

Prefer ``wfm4cities gui`` or ``python -m wfm4cities`` after installation.
"""

from wfm4cities import __version__ as __version__
from wfm4cities.gui import run_gui

if __name__ == "__main__":
    run_gui()
