# GitHub and PyPI release procedure

## First repository update

1. Download and extract the GitHub-ready archive.
2. Back up the current repository or create a new branch.
3. Replace the two-file repository contents with the extracted project
   contents, including hidden `.github` files.
4. Review `AUTHORS.md`, `LICENSE`, `CITATION.cff`, and project URLs.
5. Commit and push to GitHub.
6. Confirm that the CI workflow passes.

Recommended commands:

    git checkout -b release/3.0.0
    git add --all
    git commit -m "Prepare WFM4Cities 3.0.0"
    git push --set-upstream origin release/3.0.0

Open and merge a pull request after CI succeeds.

## Local release verification

    python -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -e ".[dev]"
    ruff check .
    pytest
    python -m build
    python -m twine check dist/*

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`.

## TestPyPI

Before the production release, upload the wheel and source distribution to
TestPyPI or configure a TestPyPI trusted publisher. Verify installation in a
fresh environment.

## Distribution name

The `WFM4Cities` project on PyPI belongs to a different account and cannot
receive uploads from the maintainers of this repository. Version 3.0.0 is
therefore published under the distribution name `PTS-WFM4Cities`, which is
owned by `zhangzuocughustccnu`. Wherever the notes below mention the
`WFM4Cities` project, read `PTS-WFM4Cities` for releases of this repository.

## Trusted publishing

The included `.github/workflows/publish.yml` uses PyPI trusted publishing and
does not store a long-lived API token. In PyPI:

1. create or select the `WFM4Cities` project;
2. add a trusted publisher for owner `zhangzuocughustccnu`, repository
   `WFM4Cities`, workflow `publish.yml`, environment `pypi`;
3. in GitHub, create the protected `pypi` environment and require manual
   approval;
4. publish a GitHub Release tagged `v3.0.0`.

The workflow builds, checks, and uploads the distributions after the release is
published.

## Permanent research archive

Connect the GitHub repository to Zenodo before creating the final GitHub
release. Zenodo can then archive the tagged release and mint a DOI. Add the
resulting DOI to `CITATION.cff`, the README, software manual, and manuscript
data/code statement in a subsequent patch release.

Do not insert a placeholder or guessed DOI.
