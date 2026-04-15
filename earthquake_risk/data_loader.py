from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"time", "latitude", "longitude", "mag", "depth", "place", "type", "id"}


def load_earthquake_data(csv_path: Path, grid_size: float = 1.0) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"Data file not found: {csv_path}")
    if grid_size <= 0:
        raise ValueError("grid_size must be greater than 0")

    df = pd.read_csv(csv_path)
    missing_columns = REQUIRED_COLUMNS.difference(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Dataset is missing required columns: {missing}")

    df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True)
    df = df.dropna(subset=["time", "latitude", "longitude", "mag", "depth"])
    df = df[df["type"].fillna("earthquake").eq("earthquake")].copy()

    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month
    df["day"] = df["time"].dt.day

    # Group events into configurable spatial cells instead of fixed whole-degree buckets.
    df["grid_lat"] = ((df["latitude"] / grid_size).round() * grid_size).round(3)
    df["grid_lon"] = ((df["longitude"] / grid_size).round() * grid_size).round(3)
    df["grid_cell_key"] = (
        df["grid_lat"].map(lambda value: f"{value:.3f}")
        + "_"
        + df["grid_lon"].map(lambda value: f"{value:.3f}")
    )

    return df.sort_values("time").reset_index(drop=True)
