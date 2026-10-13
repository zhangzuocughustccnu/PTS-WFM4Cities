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
