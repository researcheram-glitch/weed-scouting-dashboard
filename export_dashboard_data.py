"""Export dashboard_data.js directly from the master Excel workbook.

This script reads scouting records from ``data/scouting_master.xlsx`` and
produces ``dashboard_data.js`` in the same compact RAW_DATA format expected by
our HTML dashboard.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
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

# Columns that define whether a row has real scouting business data.
BUSINESS_COLUMNS = [
    "Field_ID",
    "Field",
    "Farm",
    "Year",
    "Crop",
    "Weed",
    "WeedClass",
    "Pressure",
]

# Text columns that should be trimmed before emptiness checks/export.
TEXT_COLUMNS = [
    "Field_ID",
    "Field",
    "Farm",
    "Crop",
    "Weed",
    "WeedClass",
    "Pressure",
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


def _cleanup_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Drop trailing/blank rows and rows missing key business columns."""
    cleaned = frame.copy()

    # Normalize text columns first so whitespace-only cells become truly empty.
    for column in TEXT_COLUMNS:
        if column in cleaned.columns:
            cleaned[column] = cleaned[column].apply(
                lambda value: value.strip() if isinstance(value, str) else value
            )
            cleaned[column] = cleaned[column].replace("", pd.NA)

    # Normalize "empty-like" values in every required column.
    # This catches cells that come from formulas returning "", non-breaking spaces, etc.
    for column in REQUIRED_COLUMNS:
        cleaned[column] = cleaned[column].apply(
            lambda value: value.strip() if isinstance(value, str) else value
        )
        cleaned[column] = cleaned[column].replace(
            to_replace=[r"^\s*$", ""],
            value=pd.NA,
            regex=True,
        )

    # Remove rows where all required columns are empty (typical trailing Excel rows).
    cleaned = cleaned.dropna(subset=REQUIRED_COLUMNS, how="all")

    # Treat Year as empty when it cannot be parsed.
    business_view = cleaned[BUSINESS_COLUMNS].copy()
    business_view["Year"] = pd.to_numeric(business_view["Year"], errors="coerce")
    business_empty_mask = business_view.isna().all(axis=1)
    cleaned = cleaned.loc[~business_empty_mask].copy()

    return cleaned


def write_dashboard_data_js(records: list[dict[str, object]], output_path: Path = OUTPUT_JS) -> None:
    """Write compact records to dashboard_data.js using dashboard-compatible format."""
    payload = "const RAW_DATA = " + json.dumps(
        records,
        ensure_ascii=False,
        separators=(",", ":"),
    ) + ";\n"
    output_path.write_text(payload, encoding="utf-8")


def main() -> int:
    """Run export pipeline from Excel to dashboard_data.js."""
    if not SOURCE_XLSX.exists():
        print("ERROR: Missing input file: data/scouting_master.xlsx")
        return 1

    # 1) Read directly from Excel (no CSV conversion step)
    frame = pd.read_excel(SOURCE_XLSX)
    rows_read = len(frame)

    # 2) Validate required columns early with a clear message
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing_columns:
        print("ERROR: Missing required columns in data/scouting_master.xlsx:")
        for column in missing_columns:
            print(f"  - {column}")
        print("Export aborted. dashboard_data.js was not updated.")
        return 1

    # 3) Keep only required columns for a stable transformation surface
    frame = frame[REQUIRED_COLUMNS].copy()
    frame = _cleanup_frame(frame)
    rows_kept = len(frame)

    # 4) Convert each row to the compact RAW_DATA schema used by dashboard logic
    records = [_compact_record(row) for _, row in frame.iterrows()]
    unique_fields_exported = frame["Field"].astype(str).str.strip().nunique()

    # 5) Overwrite output every successful run
    write_dashboard_data_js(records, OUTPUT_JS)

    # 6) Success summary
    now_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print("dashboard_data.js updated")
    print(f"rows read from Excel: {rows_read}")
    print(f"rows kept after cleanup: {rows_kept}")
    print(f"rows exported: {len(records)}")
    print(f"unique fields exported: {unique_fields_exported}")
    print(f"timestamp: {now_utc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
