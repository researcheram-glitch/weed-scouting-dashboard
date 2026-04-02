"""Input/output helpers for scouting datasets."""

from __future__ import annotations

import csv
from pathlib import Path

REQUIRED_COLUMNS = {
    "field_id",
    "weed_density",
    "weed_species_count",
    "crop_stage",
}


def _coerce_row_types(row: dict[str, str]) -> dict[str, str | float | int]:
    return {
        "field_id": row["field_id"],
        "weed_density": float(row["weed_density"]),
        "weed_species_count": int(row["weed_species_count"]),
        "crop_stage": row["crop_stage"],
    }


def read_scouting_csv(csv_path: str | Path) -> list[dict[str, str | float | int]]:
    """Read scouting CSV data and validate required columns."""
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = set(reader.fieldnames or [])

        missing = REQUIRED_COLUMNS - columns
        if missing:
            missing_cols = ", ".join(sorted(missing))
            raise ValueError(f"CSV missing required columns: {missing_cols}")

        return [_coerce_row_types(row) for row in reader]
