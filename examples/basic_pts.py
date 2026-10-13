"""Minimal in-memory WFM4Cities analysis."""

from wfm4cities import (
    SimulationConfig,
    build_surface,
    extract_features,
    progressive_threshold_scan,
)


def main() -> None:
    model = build_surface(
        SimulationConfig(num_points=120, num_clusters=3, grid_size=80, seed=42)
    )
    result = progressive_threshold_scan(model.grid_z)
    for name, value in extract_features(result).items():
        print(f"{name}: {value:.6g}")


if __name__ == "__main__":
    main()
