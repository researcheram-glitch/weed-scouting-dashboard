"""Data loading and transformation helpers for weed scouting dashboards."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = [
    "Field_ID",
    "Weed",
    "WeedClass",
    "Pressure",
    "Field",
    "Farm",
    "Area_ac",
    "Crop",
    "ScoutedBy",
    "Year",
    "ScoutingDate",
    "PressureScore",
]


@dataclass(frozen=True)
class DashboardData:
    """Container for dashboard-ready dataframes."""

    raw: pd.DataFrame
    filtered: pd.DataFrame
    field_metrics: pd.DataFrame
    weed_metrics: pd.DataFrame


def _normalize_column_name(column_name: str) -> str:
    """Normalize names safely to improve tolerance for minor schema variations."""
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in column_name).strip("_")


def _canonical_name_map(columns: list[str]) -> dict[str, str]:
    """Map normalized columns back to the project canonical names."""
    normalized_to_original = {_normalize_column_name(name): name for name in columns}
    map_result: dict[str, str] = {}

    for required in REQUIRED_COLUMNS:
        normalized_required = _normalize_column_name(required)
        if normalized_required in normalized_to_original:
            map_result[normalized_to_original[normalized_required]] = required

    return map_result


def load_scouting_data(csv_path: str | Path) -> pd.DataFrame:
    """Load the scouting CSV with UTF-8 BOM handling and schema validation."""
    path = Path(csv_path)
    frame = pd.read_csv(path, encoding="utf-8-sig")

    rename_map = _canonical_name_map(frame.columns.tolist())
    frame = frame.rename(columns=rename_map)

    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(
            "CSV is missing required columns: " + ", ".join(missing)
        )

    frame = frame[REQUIRED_COLUMNS].copy()

    frame["PressureScore"] = pd.to_numeric(frame["PressureScore"], errors="coerce")
    frame["Year"] = pd.to_numeric(frame["Year"], errors="coerce").astype("Int64")
    frame["ScoutingDate"] = pd.to_datetime(frame["ScoutingDate"], errors="coerce")

    return frame.dropna(subset=["Field_ID", "PressureScore"])


def apply_filters(
    frame: pd.DataFrame,
    farms: list[str] | None = None,
    years: list[int] | None = None,
    crops: list[str] | None = None,
    weed_classes: list[str] | None = None,
) -> pd.DataFrame:
    """Filter records based on selected dashboard options."""
    filtered = frame.copy()

    if farms:
        filtered = filtered[filtered["Farm"].isin(farms)]
    if years:
        filtered = filtered[filtered["Year"].isin(years)]
    if crops:
        filtered = filtered[filtered["Crop"].isin(crops)]
    if weed_classes:
        filtered = filtered[filtered["WeedClass"].isin(weed_classes)]

    return filtered


def aggregate_field_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    """Build field-level aggregation grouped by Field_ID."""
    if frame.empty:
        return pd.DataFrame(
            columns=[
                "Field_ID",
                "Field",
                "Farm",
                "Crop",
                "avg_pressure_score",
                "max_pressure_score",
                "unique_weed_species_count",
                "total_observations",
                "overall_weed_risk_score",
            ]
        )

    aggregated = (
        frame.groupby("Field_ID", as_index=False)
        .agg(
            Field=("Field", "first"),
            Farm=("Farm", "first"),
            Crop=("Crop", "first"),
            avg_pressure_score=("PressureScore", "mean"),
            max_pressure_score=("PressureScore", "max"),
            unique_weed_species_count=("Weed", pd.Series.nunique),
            total_observations=("Weed", "count"),
        )
    )

    # Weed Risk Score (WRS) formula:
    # Step 1: per (Field_ID, Weed) average PressureScore
    # Step 2: avgPS(field) = average of per-weed averages
    # Step 3: High%(field) = share of weed species with avgPS >= 4
    # Step 4: WRS = (avgPS / 6 * 50) + (High% * 50)
    weed_level = (
        frame.groupby(["Field_ID", "Weed"], as_index=False)
        .agg(weed_avg_ps=("PressureScore", "mean"))
    )

    wrs_by_field = (
        weed_level.groupby("Field_ID", as_index=False)
        .agg(
            avg_ps_by_weed=("weed_avg_ps", "mean"),
            high_pct=("weed_avg_ps", lambda s: (s >= 4).mean()),
        )
    )
    wrs_by_field["overall_weed_risk_score"] = (
        (wrs_by_field["avg_ps_by_weed"] / 6.0) * 50.0
        + (wrs_by_field["high_pct"] * 50.0)
    )

    aggregated = aggregated.merge(
        wrs_by_field[["Field_ID", "overall_weed_risk_score"]],
        on="Field_ID",
        how="left",
    )

    return aggregated.sort_values("overall_weed_risk_score", ascending=False)


def aggregate_weed_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    """Aggregate weeds by average pressure score for charting."""
    if frame.empty:
        return pd.DataFrame(columns=["Weed", "avg_pressure_score", "observations"])

    return (
        frame.groupby("Weed", as_index=False)
        .agg(
            avg_pressure_score=("PressureScore", "mean"),
            observations=("PressureScore", "count"),
        )
        .sort_values("avg_pressure_score", ascending=False)
    )


def build_dashboard_data(
    csv_path: str | Path,
    farms: list[str] | None = None,
    years: list[int] | None = None,
    crops: list[str] | None = None,
    weed_classes: list[str] | None = None,
) -> DashboardData:
    """Load, filter, and aggregate dataset for dashboard consumption."""
    raw = load_scouting_data(csv_path)
    filtered = apply_filters(raw, farms=farms, years=years, crops=crops, weed_classes=weed_classes)
    return DashboardData(
        raw=raw,
        filtered=filtered,
        field_metrics=aggregate_field_metrics(filtered),
        weed_metrics=aggregate_weed_metrics(filtered),
    )
