import csv
import json
import sys
from pathlib import Path

from wfm4cities.cli import main
from wfm4cities.io import read_point_csv, read_surface_csv


def test_import_has_no_tk_or_pyplot_side_effect() -> None:
    assert "tkinter" not in sys.modules
    assert "matplotlib.pyplot" not in sys.modules


def test_read_point_csv_case_insensitive(tmp_path: Path) -> None:
    source = tmp_path / "points.csv"
    source.write_text("X,Y,Value\n0,1,2\n3,4,5\n", encoding="utf-8")
    points, values = read_point_csv(source)
    assert points.tolist() == [[0.0, 1.0], [3.0, 4.0]]
    assert values is not None
    assert values.tolist() == [2.0, 5.0]


def test_cli_demo_writes_expected_headless_outputs(tmp_path: Path) -> None:
    output = tmp_path / "demo"
    exit_code = main(
        [
            "demo",
            "--output-dir",
            str(output),
            "--num-points",
            "50",
            "--grid-size",
            "24",
            "--no-figure",
        ]
    )
    assert exit_code == 0
    expected = {
        "source_points.csv",
        "surface_normalized.csv",
        "pts_response.csv",
        "pts_features.json",
    }
    assert expected == {path.name for path in output.iterdir()}
    grid = read_surface_csv(output / "surface_normalized.csv")
    assert grid.shape == (24, 24)
    payload = json.loads((output / "pts_features.json").read_text(encoding="utf-8"))
    assert payload["WFM4Cities_version"] == "3.0.0"

    with (output / "pts_response.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 51
    assert set(rows[0]) == {"threshold", "A", "V", "N", "L"}


def test_legacy_namespace_import() -> None:
    import WFM4Cities

    assert WFM4Cities.__version__ == "3.0.0"


def test_short_scan_domain_writes_valid_feature_note(tmp_path: Path) -> None:
    grid_path = tmp_path / "grid.csv"
    grid_path.write_text("0,0.2,0.4\n0.1,0.5,0.8\n0.2,0.7,1\n", encoding="utf-8")
    output = tmp_path / "short_scan"
    exit_code = main(
        [
            "scan",
            str(grid_path),
            "--output-dir",
            str(output),
            "--threshold-max",
            "0.5",
            "--no-figure",
        ]
    )
    assert exit_code == 0
    payload = json.loads((output / "pts_features.json").read_text(encoding="utf-8"))
    assert payload["features"] is None
    assert "outside the scan domain" in payload["feature_note"]
