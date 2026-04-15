import argparse
from pathlib import Path

from earthquake_risk import run_analysis


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a small historical earthquake risk analysis for Japan."
    )
    parser.add_argument(
        "--data-file",
        type=Path,
        default=Path("earthquake_data/japan_2000_2023_query.csv"),
        help="CSV file used for the analysis.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs"),
        help="Folder for generated results.",
    )
    parser.add_argument(
        "--grid-size",
        type=float,
        default=0.5,
        help="Grid cell size in degrees.",
    )
    parser.add_argument(
        "--recent-window-days",
        type=int,
        default=365,
        help="How many recent days count as recent activity in the score.",
    )
    parser.add_argument(
        "--top-cells",
        "--top-regions",
        dest="top_cells",
        type=int,
        default=5,
        help="How many top grid cells should be printed.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run_analysis(
        data_file=args.data_file,
        output_dir=args.output_dir,
        grid_size=args.grid_size,
        recent_window_days=args.recent_window_days,
        top_cells=args.top_cells,
    )

    print("Analysis completed.")
    print(f"Records analyzed: {summary['records']}")
    print(f"Grid size: {summary['grid_size']} degrees")
    print(f"Recent activity window: {summary['recent_window_days']} days")
    print(
        "Time range: "
        f"{summary['time_range']['from']} -> {summary['time_range']['to']}"
    )
    print("Alert counts:")
    for alert, count in summary["top_alert_counts"].items():
        print(f"  {alert}: {count}")

    print("Top grid cells:")
    for grid_cell in summary["top_risk_grid_cells"]:
        print(
            f"  {grid_cell['grid_cell_key']} | "
            f"rank={grid_cell['risk_rank']} | "
            f"score={grid_cell['risk_score']} | "
            f"level={grid_cell['risk_level']} | "
            f"events={int(grid_cell['event_count'])} | "
            f"max_mag={grid_cell['max_magnitude']}"
        )

    print("Saved files:")
    for file_name in summary["generated_files"]:
        print(f"  {file_name}")


if __name__ == "__main__":
    main()
