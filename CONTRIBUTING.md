# Contributing

Thank you for helping improve WFM4Cities.

## Before opening a change

1. Search existing issues.
2. For method changes, state the mathematical convention being changed and why.
3. Do not silently change threshold inequalities, connectivity, normalization,
   interpolation, random seeds, or output field names.
4. Add or update tests for every behavior change.

## Development setup

    python -m venv .venv
    source .venv/bin/activate
    python -m pip install -e ".[dev]"

Use `.venv\Scripts\Activate.ps1` on Windows PowerShell.

Run:

    ruff check .
    pytest
    python -m build
    python -m twine check dist/*

## Pull requests

- keep each pull request focused;
- explain scientific and software consequences;
- update CHANGELOG.md for user-visible changes;
- preserve backwards compatibility where practical;
- do not commit generated environments, caches, credentials, or large
  unpublished research data;
- confirm that you have the right to contribute all included code and data.

## Reproducible bug reports

Include operating system, Python version, WFM4Cities version, installation
command, minimal input or script, full error message, and expected behavior.
