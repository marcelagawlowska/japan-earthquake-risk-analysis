from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AnalysisConfig:
    data_file: Path
    output_dir: Path
    grid_size: float = 1.0
    recent_window_days: int = 365
    top_cells: int = 5
    risk_weights: dict[str, float] | None = None


DEFAULT_DATA_FILE = Path("earthquake_data/japan_2000_2023_query.csv")
DEFAULT_OUTPUT_DIR = Path("outputs")
DEFAULT_RISK_WEIGHTS = {
    "event_count": 0.30,
    "avg_magnitude": 0.25,
    "recent_events": 0.20,
    "shallow_ratio": 0.15,
    "strong_event_ratio": 0.10,
}
