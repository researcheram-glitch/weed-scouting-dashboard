"""CLI-like entry point for the simple agronomy AI pipeline."""

from pathlib import Path

from agro_ai.io import read_scouting_csv
from agro_ai.risk import calculate_weed_risk_by_field
from agro_ai.viz_prep import prepare_field_risk_viz_data


def run_pipeline(csv_path: str | Path) -> dict[str, list[dict]]:
    scouting_df = read_scouting_csv(csv_path)
    field_risk_df = calculate_weed_risk_by_field(scouting_df)
    return prepare_field_risk_viz_data(field_risk_df)


if __name__ == "__main__":
    payload = run_pipeline("data/scouting_sample.csv")
    print(payload)
