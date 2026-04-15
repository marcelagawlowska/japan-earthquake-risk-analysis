import pandas as pd


ALERT_PRIORITY = {
    "CRITICAL": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
}


def classify_event_alert(magnitude: float) -> str:
    if magnitude >= 7.0:
        return "CRITICAL"
    if magnitude >= 6.0:
        return "HIGH"
    if magnitude >= 5.0:
        return "MEDIUM"
    return "LOW"


def classify_risk_level(score: float) -> str:
    if score >= 0.75:
        return "CRITICAL"
    if score >= 0.55:
        return "HIGH"
    if score >= 0.35:
        return "MEDIUM"
    return "LOW"


def _normalize(series: pd.Series) -> pd.Series:
    max_value = float(series.max()) if not series.empty else 0.0
    if max_value <= 0:
        return pd.Series(0.0, index=series.index)
    return series.astype(float) / max_value


def enrich_events(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()
    enriched["alert_level"] = enriched["mag"].apply(classify_event_alert)
    enriched["priority"] = enriched["alert_level"].map(ALERT_PRIORITY).fillna(1).astype(int)
    enriched["is_strong"] = enriched["mag"] >= 5.5
    enriched["is_shallow"] = enriched["depth"] <= 70
    return enriched


def validate_risk_weights(weights: dict[str, float]) -> dict[str, float]:
    required_keys = {
        "event_count",
        "avg_magnitude",
        "recent_events",
        "shallow_ratio",
        "strong_event_ratio",
    }
    missing_keys = required_keys.difference(weights)
    if missing_keys:
        missing = ", ".join(sorted(missing_keys))
        raise ValueError(f"Missing risk weight keys: {missing}")

    total = sum(weights.values())
    if abs(total - 1.0) > 1e-9:
        raise ValueError("Risk weights must sum to 1.0")

    return weights


def summarize_grid_cell_risk(
    df: pd.DataFrame,
    recent_window_days: int,
    weights: dict[str, float],
) -> pd.DataFrame:
    latest_time = df["time"].max()
    recent_cutoff = latest_time - pd.Timedelta(days=recent_window_days)
    validated_weights = validate_risk_weights(weights)

    grouped = (
        df.groupby("grid_cell_key")
        .agg(
            event_count=("id", "count"),
            avg_magnitude=("mag", "mean"),
            max_magnitude=("mag", "max"),
            avg_depth=("depth", "mean"),
            shallow_ratio=("is_shallow", "mean"),
            strong_event_ratio=("is_strong", "mean"),
            recent_events=("time", lambda s: (s >= recent_cutoff).sum()),
            latitude_center=("latitude", "mean"),
            longitude_center=("longitude", "mean"),
        )
        .reset_index()
    )

    count_score = _normalize(grouped["event_count"])
    magnitude_score = _normalize(grouped["avg_magnitude"])
    recent_score = _normalize(grouped["recent_events"])
    shallow_score = grouped["shallow_ratio"].fillna(0.0)
    strong_score = grouped["strong_event_ratio"].fillna(0.0)

    grouped["risk_score"] = (
        validated_weights["event_count"] * count_score
        + validated_weights["avg_magnitude"] * magnitude_score
        + validated_weights["recent_events"] * recent_score
        + validated_weights["shallow_ratio"] * shallow_score
        + validated_weights["strong_event_ratio"] * strong_score
    ).round(4)
    grouped["risk_level"] = grouped["risk_score"].apply(classify_risk_level)
    grouped["risk_rank"] = grouped["risk_score"].rank(method="dense", ascending=False).astype(int)

    return grouped.sort_values(
        by=["risk_score", "event_count", "max_magnitude"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def summarize_monthly_activity(df: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        df.groupby(["year", "month"])
        .agg(
            event_count=("id", "count"),
            avg_magnitude=("mag", "mean"),
            max_magnitude=("mag", "max"),
            shallow_events=("is_shallow", "sum"),
            strong_events=("is_strong", "sum"),
        )
        .reset_index()
    )
    monthly["period"] = monthly["year"].astype(str) + "-" + monthly["month"].astype(str).str.zfill(2)
    return monthly.sort_values(["year", "month"]).reset_index(drop=True)
