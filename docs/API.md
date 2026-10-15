# API reference

## Surface construction

- `SimulationConfig`: validated synthetic-example settings.
- `build_surface(config)`: generate points, calculate local density, run cubic
  interpolation, fill boundaries, and normalize.
- `interpolate_surface(points, values, ...)`: point-to-grid conversion.
- `surface_from_grid(grid, ...)`: wrap an existing regular grid.
- `normalize_surface(grid)`: finite min--max normalization.

`SurfaceModel` stores `grid_x`, `grid_y`, `grid_z`, optional source
`points`, corresponding `point_values`, and synthetic cluster `centers`.

## Progressive threshold scan

- `progressive_threshold_scan(surface, ...)`
- `threshold_vector(count=51, minimum=0, maximum=0.95)`
- `extract_features(result)`

`PTSResult` stores the threshold vector and four trajectories. Long names and
paper notation are both available:

| Long property | Short property |
|---|---|
| `area` | `A` |
| `excess_volume` | `V` |
| `component_count` | `N` |
| `largest_component_ratio` | `L` |

## Canonical structures

- `MODEL_LABELS`: the four preset names, `M1`--`M4`.
- `MODEL_PRESETS`: their validated configurations.
- `model_config(key, **overrides)`: the configuration of one preset.
- `build_model_surface(key, **overrides)`: the points and surface of one preset.

## Importing an external point table

- `standardize_points(points, values, **kwargs)`: affine mapping onto the
  standard square domain plus min--max normalisation of the selected attribute.
- `StandardizationReport`: the scales and offsets that were applied.
- `read_point_table(path, ...)`: read a coordinate table; `list_csv_columns(path)`
  returns its column names for the import dialogue.

## Appearance

- `wfm4cities.palette`: `SURFACE_RAMP`, `DOMAIN_FILL`, `POINT_COLOR`,
  `CENTER_COLOR`, `N_CURVE_COLOR`, `SECTION_RAMP`, `surface_cmap()`,
  `section_cmap()`, `series_color()`, `series_marker()`.
- `wfm4cities.i18n`: `translate()`, `normalise()`, `DEFAULT_LANGUAGE`.
- `wfm4cities.fonts`: `apply()`, `register_font_files()`, `resolved_families()`,
  and the directory named by `PTS_FONT_DIR`.

## Input/output

- `read_point_csv`
- `read_surface_csv`
- `write_points_csv`
- `write_surface_csv`
- `write_scan_csv`
- `write_json`

## Plotting

- `plot_overview(model, result, threshold=0.4)`
- `save_overview(path, model, result, threshold=0.4)`

## Optional spatial diagnostic

`morans_i(points, values, k=15, permutations=999, seed=42)` requires the
`spatial` optional dependency group.
