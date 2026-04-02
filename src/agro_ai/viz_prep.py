"""Prepare processed data for charts/maps/dashboards."""

from __future__ import annotations


def prepare_field_risk_viz_data(
    field_risk_rows: list[dict[str, str | float]],
) -> dict[str, list[dict[str, str | float | int]]]:
    """Convert field-risk rows into frontend-friendly payloads."""
    bar_chart = [
        {
            "field_id": row["field_id"],
            "weed_risk_score": row["weed_risk_score"],
        }
        for row in field_risk_rows
    ]

    counts: dict[str, int] = {"low": 0, "medium": 0, "high": 0}
    for row in field_risk_rows:
        counts[str(row["risk_level"])] = counts.get(str(row["risk_level"]), 0) + 1

    risk_distribution = [
        {"risk_level": level, "field_count": count}
        for level, count in counts.items()
        if count > 0
    ]

    return {
        "bar_chart": bar_chart,
        "risk_distribution": risk_distribution,
    }
