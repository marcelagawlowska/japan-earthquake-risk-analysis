from pathlib import Path

from .config import AnalysisConfig, DEFAULT_DATA_FILE, DEFAULT_OUTPUT_DIR, DEFAULT_RISK_WEIGHTS
from .data_loader import load_earthquake_data
from .reporting import (
    save_csv,
    save_markdown_report,
    save_summary_json,
    save_svg_bar_chart,
    save_svg_line_chart,
)
from .risk_model import enrich_events, summarize_grid_cell_risk, summarize_monthly_activity


def run_analysis(
    data_file: Path | None = None,
    output_dir: Path | None = None,
    grid_size: float = 1.0,
    recent_window_days: int = 365,
    top_cells: int = 5,
    risk_weights: dict[str, float] | None = None,
) -> dict:
    if recent_window_days <= 0:
        raise ValueError("recent_window_days must be greater than 0")
    if top_cells <= 0:
        raise ValueError("top_cells must be greater than 0")

    config = AnalysisConfig(
        data_file=Path(data_file) if data_file else DEFAULT_DATA_FILE,
        output_dir=Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR,
        grid_size=grid_size,
        recent_window_days=recent_window_days,
        top_cells=top_cells,
        risk_weights=risk_weights or DEFAULT_RISK_WEIGHTS,
    )

    df = load_earthquake_data(config.data_file, grid_size=config.grid_size)
    enriched = enrich_events(df)
    grid_cell_risk = summarize_grid_cell_risk(
        enriched,
        config.recent_window_days,
        config.risk_weights or DEFAULT_RISK_WEIGHTS,
    )
    monthly_activity = summarize_monthly_activity(enriched)

    save_csv(enriched, config.output_dir / "cleaned_earthquakes.csv")
    save_csv(grid_cell_risk, config.output_dir / "grid_cell_risk_summary.csv")
    save_csv(monthly_activity, config.output_dir / "monthly_activity_summary.csv")
    save_svg_bar_chart(
        enriched["alert_level"].value_counts().to_dict(),
        title="Alert Level Distribution",
        path=config.output_dir / "alert_distribution.svg",
    )
    save_svg_line_chart(
        monthly_activity,
        x_column="period",
        y_column="event_count",
        title="Monthly Earthquake Activity",
        path=config.output_dir / "monthly_activity.svg",
    )

    summary = {
        "data_file": str(config.data_file),
        "records": int(len(enriched)),
        "grid_size": config.grid_size,
        "recent_window_days": config.recent_window_days,
        "risk_weights": config.risk_weights,
        "time_range": {
            "from": enriched["time"].min().isoformat(),
            "to": enriched["time"].max().isoformat(),
        },
        "top_alert_counts": enriched["alert_level"].value_counts().to_dict(),
        "top_risk_grid_cells": grid_cell_risk.head(config.top_cells).to_dict(orient="records"),
        "strongest_events": (
            enriched.sort_values(["mag", "time"], ascending=[False, False])
            .head(10)[["time", "place", "mag", "depth", "alert_level"]]
            .assign(time=lambda frame: frame["time"].astype(str))
            .to_dict(orient="records")
        ),
        "generated_files": [
            "cleaned_earthquakes.csv",
            "grid_cell_risk_summary.csv",
            "monthly_activity_summary.csv",
            "analysis_summary.json",
            "analysis_report.md",
            "alert_distribution.svg",
            "monthly_activity.svg",
        ],
    }

    save_summary_json(summary, config.output_dir / "analysis_summary.json")
    save_markdown_report(summary, config.output_dir / "analysis_report.md")
    return summary
