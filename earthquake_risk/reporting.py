import json
from pathlib import Path

import pandas as pd


def save_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def save_summary_json(summary: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")


def save_markdown_report(summary: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    top_cells_lines = []
    for cell in summary["top_risk_grid_cells"]:
        top_cells_lines.append(
            f"- `{cell['grid_cell_key']}`: rank {cell['risk_rank']}, "
            f"score {cell['risk_score']}, level {cell['risk_level']}, "
            f"events {int(cell['event_count'])}, max magnitude {cell['max_magnitude']}"
        )

    strongest_event_lines = []
    for event in summary["strongest_events"][:5]:
        strongest_event_lines.append(
            f"- `{event['time']}` | {event['place']} | "
            f"M {event['mag']} | depth {event['depth']} km | {event['alert_level']}"
        )

    notes = []
    top_cells = summary["top_risk_grid_cells"]
    if top_cells:
        strongest_cell = top_cells[0]
        notes.append(
            f"- The highest-scoring cell in this run was `{strongest_cell['grid_cell_key']}` "
            f"with score `{strongest_cell['risk_score']}`."
        )

    if "CRITICAL" in summary["top_alert_counts"]:
        notes.append(
            f"- The dataset contains `{summary['top_alert_counts']['CRITICAL']}` events classified as `CRITICAL`."
        )

    report = "\n".join(
        [
            "# Analysis Report",
            "",
            "This is a short summary generated from the current dataset and run settings.",
            "",
            "## Run settings",
            "",
            f"- dataset: `{summary['data_file']}`",
            f"- records analyzed: `{summary['records']}`",
            f"- grid size: `{summary['grid_size']}` degrees",
            f"- recent activity window: `{summary['recent_window_days']}` days",
            f"- time range: `{summary['time_range']['from']}` to `{summary['time_range']['to']}`",
            "",
            "## Alert counts",
            "",
            *[
                f"- `{level}`: {count}"
                for level, count in summary["top_alert_counts"].items()
            ],
            "",
            "## Quick notes",
            "",
            *(notes or ["- No extra notes were generated for this run."]),
            "",
            "## Top grid cells",
            "",
            *top_cells_lines,
            "",
            "## Strongest events",
            "",
            *strongest_event_lines,
            "",
        ]
    )
    path.write_text(report, encoding="utf-8")


def save_svg_bar_chart(
    values: dict[str, int | float],
    title: str,
    path: Path,
    width: int = 720,
    height: int = 420,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    margin_left = 80
    margin_bottom = 70
    margin_top = 60
    margin_right = 30
    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom

    labels = list(values.keys())
    data = [float(value) for value in values.values()]
    max_value = max(data) if data else 1.0
    bar_width = chart_width / max(len(data), 1)

    bars = []
    for index, (label, value) in enumerate(zip(labels, data)):
        scaled_height = 0 if max_value == 0 else (value / max_value) * (chart_height - 10)
        x = margin_left + index * bar_width + 10
        y = margin_top + chart_height - scaled_height
        current_bar_width = max(bar_width - 20, 10)

        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{current_bar_width:.1f}" '
            f'height="{scaled_height:.1f}" fill="#2563eb" rx="6" />'
        )
        bars.append(
            f'<text x="{x + current_bar_width / 2:.1f}" y="{margin_top + chart_height + 24}" '
            f'font-size="13" text-anchor="middle" fill="#1f2937">{label}</text>'
        )
        bars.append(
            f'<text x="{x + current_bar_width / 2:.1f}" y="{y - 8:.1f}" '
            f'font-size="12" text-anchor="middle" fill="#111827">{int(value)}</text>'
        )

    svg = "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<rect width="100%" height="100%" fill="#f8fafc" />',
            f'<text x="{width / 2}" y="32" font-size="22" text-anchor="middle" fill="#0f172a">{title}</text>',
            f'<line x1="{margin_left}" y1="{margin_top + chart_height}" x2="{width - margin_right}" y2="{margin_top + chart_height}" stroke="#94a3b8" stroke-width="2" />',
            f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + chart_height}" stroke="#94a3b8" stroke-width="2" />',
            *bars,
            "</svg>",
        ]
    )
    path.write_text(svg, encoding="utf-8")


def save_svg_line_chart(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: str,
    path: Path,
    width: int = 900,
    height: int = 420,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    margin_left = 70
    margin_bottom = 70
    margin_top = 60
    margin_right = 30
    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom

    values = df[y_column].astype(float).tolist()
    labels = df[x_column].astype(str).tolist()
    max_value = max(values) if values else 1.0
    min_value = min(values) if values else 0.0
    value_range = max(max_value - min_value, 1.0)

    points = []
    for index, value in enumerate(values):
        x = margin_left + (chart_width * index / max(len(values) - 1, 1))
        y = margin_top + chart_height - ((value - min_value) / value_range) * chart_height
        points.append((x, y))

    polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    markers = [
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="#dc2626" />'
        for x, y in points
    ]

    x_labels = []
    if labels:
        step = max(len(labels) // 6, 1)
        for index in range(0, len(labels), step):
            x = margin_left + (chart_width * index / max(len(labels) - 1, 1))
            x_labels.append(
                f'<text x="{x:.1f}" y="{margin_top + chart_height + 24}" font-size="11" '
                f'text-anchor="middle" fill="#1f2937">{labels[index]}</text>'
            )

    svg = "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<rect width="100%" height="100%" fill="#f8fafc" />',
            f'<text x="{width / 2}" y="32" font-size="22" text-anchor="middle" fill="#0f172a">{title}</text>',
            f'<line x1="{margin_left}" y1="{margin_top + chart_height}" x2="{width - margin_right}" y2="{margin_top + chart_height}" stroke="#94a3b8" stroke-width="2" />',
            f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + chart_height}" stroke="#94a3b8" stroke-width="2" />',
            f'<polyline fill="none" stroke="#2563eb" stroke-width="3" points="{polyline}" />' if polyline else "",
            *markers,
            *x_labels,
            "</svg>",
        ]
    )
    path.write_text(svg, encoding="utf-8")
