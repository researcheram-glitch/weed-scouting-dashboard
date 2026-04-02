"""Risk scoring logic for weed pressure by field."""

from __future__ import annotations

from collections import defaultdict

# Relative crop-stage sensitivity factors.
CROP_STAGE_FACTOR = {
    "emergence": 1.3,
    "vegetative": 1.1,
    "reproductive": 0.9,
    "maturity": 0.7,
}


def _row_risk_score(row: dict[str, str | float | int]) -> float:
    stage_factor = CROP_STAGE_FACTOR.get(str(row["crop_stage"]).lower(), 1.0)

    score = (
        0.6 * float(row["weed_density"]) + 8.0 * float(row["weed_species_count"])
    ) * stage_factor
    return max(0.0, min(score, 100.0))


def _risk_level(score: float) -> str:
    if score <= 30:
        return "low"
    if score <= 60:
        return "medium"
    return "high"


def calculate_weed_risk_by_field(
    scouting_rows: list[dict[str, str | float | int]],
) -> list[dict[str, str | float]]:
    """Calculate average weed risk score for each field."""
    grouped_scores: dict[str, list[float]] = defaultdict(list)

    for row in scouting_rows:
        field_id = str(row["field_id"])
        grouped_scores[field_id].append(_row_risk_score(row))

    output: list[dict[str, str | float]] = []
    for field_id, scores in sorted(grouped_scores.items()):
        avg_score = round(sum(scores) / len(scores), 2)
        output.append(
            {
                "field_id": field_id,
                "weed_risk_score": avg_score,
                "risk_level": _risk_level(avg_score),
            }
        )

    return output
