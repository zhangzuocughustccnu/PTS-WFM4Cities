"""Column-selected point tables, as used by the import wizard."""

from pathlib import Path

import numpy as np
import pytest

from wfm4cities.io import list_csv_columns, read_point_table

CONTENT = "id,x_coord,y_coord,price\n1,0,0,10\n2,4,0,20\n3,4,3,30\n4,0,3,40\n"


def _write(tmp_path: Path, text: str = CONTENT) -> Path:
    path = tmp_path / "points.csv"
    path.write_text(text, encoding="utf-8")
    return path


def test_lists_the_header(tmp_path: Path) -> None:
    assert list_csv_columns(_write(tmp_path)) == ["id", "x_coord", "y_coord", "price"]


def test_reads_the_selected_columns(tmp_path: Path) -> None:
    points, values = read_point_table(_write(tmp_path), "x_coord", "y_coord", "price")
    assert points.shape == (4, 2)
    assert np.allclose(points[2], [4.0, 3.0])
    assert np.allclose(values, [10, 20, 30, 40])


def test_value_column_is_optional(tmp_path: Path) -> None:
    points, values = read_point_table(_write(tmp_path), "x_coord", "y_coord")
    assert values is None
    assert points.shape == (4, 2)


def test_unknown_column_is_reported(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="not in"):
        read_point_table(_write(tmp_path), "x_coord", "nope")


def test_non_numeric_cell_is_reported(tmp_path: Path) -> None:
    path = _write(tmp_path, "x,y,z\n0,0,1\n1,1,abc\n")
    with pytest.raises(ValueError, match="not numeric"):
        read_point_table(path, "x", "y", "z")


def test_blank_lines_are_skipped(tmp_path: Path) -> None:
    path = _write(tmp_path, "x,y,z\n0,0,1\n\n2,2,3\n")
    points, values = read_point_table(path, "x", "y", "z")
    assert len(points) == 2
    assert values is not None and np.allclose(values, [1.0, 3.0])
