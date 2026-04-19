"""Export dashboard_data.js directly from the master Excel workbook.

This script reads scouting records from ``data/scouting_master.xlsx`` and
produces ``dashboard_data.js`` in the same compact RAW_DATA format expected by
our HTML dashboard.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

# Source-of-truth workbook (requested path)
SOURCE_XLSX = Path("data/scouting_master.xlsx")

# Output file consumed by the HTML dashboard
OUTPUT_JS = Path("dashboard_data.js")

# Required input schema in Excel
REQUIRED_COLUMNS = [
    "Field_ID",
    "Field",
    "Farm",
    "Year",
    "Crop",
    "Weed",
    "WeedClass",
    "Pressure",
    "ScoutingDate",
    "Area_ac",
    "ScoutedBy",
]

# Pressure text -> score mapping used by existing KPI/chart logic
PRESSURE_TO_SCORE = {
    "very light": 1,
    "light": 2,
    "moderate": 3,
    "light patches": 3,
    "heavy": 4,
    "very heavy": 5,
    "heavy patches": 6,
}


def _pressure_to_score(value: object) -> int | None:
    """Convert Pressure text/number to dashboard PressureScore (1..6)."""
    if pd.isna(value):
        return None

    # Accept numeric pressures already in 1..6 form.
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.notna(numeric):
        integer_score = int(numeric)
        if 1 <= integer_score <= 6:
            return integer_score

    # Fall back to text mapping (case-insensitive).
    text_key = str(value).strip().lower()
    return PRESSURE_TO_SCORE.get(text_key)


def _as_iso_date(value: object) -> str:
    """Normalize Excel date values to YYYY-MM-DD for dashboard consistency."""
    if pd.isna(value):
        return ""
    dt = pd.to_datetime(value, errors="coerce")
    if pd.isna(dt):
        return ""
    return dt.strftime("%Y-%m-%d")


def _compact_record(row: pd.Series) -> dict[str, object]:
    """Convert one Excel row to compact keys expected by RAW_DATA."""
    return {
        "fi": str(row["Field_ID"]).strip(),
        "w": str(row["Weed"]).strip(),
        "wc": str(row["WeedClass"]).strip(),
        "pr": str(row["Pressure"]).strip(),
        "f": str(row["Field"]).strip(),
        "fm": str(row["Farm"]).strip(),
        "ar": float(row["Area_ac"]) if pd.notna(row["Area_ac"]) else 0.0,
        "cr": str(row["Crop"]).strip(),
        "sb": str(row["ScoutedBy"]).strip(),
        "yr": int(pd.to_numeric(row["Year"], errors="coerce")) if pd.notna(pd.to_numeric(row["Year"], errors="coerce")) else None,
        "sd": _as_iso_date(row["ScoutingDate"]),
        "ps": _pressure_to_score(row["Pressure"]),
    }


def main() -> int:
    """Run export pipeline and print maintenance guidance."""
    if not SOURCE_XLSX.exists():
        print("Missing file: data/scouting_master.xlsx")
        return 1

    # 1) Read directly from Excel (no CSV conversion step)
    frame = pd.read_excel(SOURCE_XLSX)

    # 2) Validate required columns early with a clear message
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing_columns:
        print("Missing required columns: " + ", ".join(missing_columns))
        return 1

    # 3) Keep only required columns for a stable transformation surface
    frame = frame[REQUIRED_COLUMNS].copy()

    # 4) Convert each row to the compact RAW_DATA schema used by dashboard logic
    records = [_compact_record(row) for _, row in frame.iterrows()]

    # 5) Preserve JS output shape consumed by HTML dashboard
    OUTPUT_JS.write_text(
        "const RAW_DATA = " + json.dumps(records, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )

    # 6) End-of-run operator guidance (requested)
    print(f"Source file: {SOURCE_XLSX}")
    print("Required columns: " + ", ".join(REQUIRED_COLUMNS))
    print(
        "Refresh steps: update data/scouting_master.xlsx, run `python export_dashboard_data.py`, "
        "then reload the HTML dashboard."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
