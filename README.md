# Japan Earthquake Risk Analysis

Python analysis of historical earthquake data in Japan with grid-based risk scoring, reports, and simple charts.

This project started as a simple exploratory script and was later cleaned up into a small Python pipeline. It uses historical earthquake records for Japan and compares seismic activity across geographic grid cells.

## What this project is

This is not a prediction model for the exact next earthquake.

What it does:

- reads a CSV dataset with earthquake events,
- cleans missing values,
- groups events into grid cells,
- classifies event severity from magnitude,
- builds a simple risk score for each grid cell,
- saves results as tables, a short report and two basic charts.

## Main idea

The score is based on a few readable factors:

- how many events happened in a grid cell,
- how strong they were on average,
- how many happened in the recent window,
- how many were shallow,
- how many were relatively strong.

The point of the project is comparison inside the same dataset, not official hazard assessment.

## Why I chose this approach

- I wanted something simple enough to explain during a review or interview.
- The source data is event-based, so a regular grid was easier to use than tectonic zones.
- I kept the scoring heuristic on purpose, because the goal here was a clear analysis pipeline, not a black-box model.

## Default dataset

By default the project runs on:

- `earthquake_data/japan_2000_2023_query.csv`

Other files inside `earthquake_data/` come from earlier exploration and are not used by the default run.

## Project files

- `main.py` - main entry point
- `Earthquake Alert Classification and Monitoring System (Japan).py` - small wrapper kept for compatibility with the original filename
- `earthquake_risk/` - analysis code
- `tests/` - unit tests
- `outputs/` - generated results

## How to run

Default run:

```powershell
python main.py
```

Example with explicit options:

```powershell
python main.py --data-file earthquake_data/japan_2000_2023_query.csv --grid-size 0.5 --recent-window-days 365 --top-cells 5
```

## Output files

After a run, the project creates:

- `cleaned_earthquakes.csv`
- `grid_cell_risk_summary.csv`
- `monthly_activity_summary.csv`
- `analysis_summary.json`
- `analysis_report.md`
- `alert_distribution.svg`
- `monthly_activity.svg`

## Current limits

-The score is not exact.
-The grid only shows the area roughly.
-Only compare scores from the same data and the same settings.
