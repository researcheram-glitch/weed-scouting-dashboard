"""Streamlit dashboard entrypoint for weed scouting analysis."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.agro_ai import build_dashboard_data

DATA_PATH = Path("data/data_scout_ggdl.csv")

st.set_page_config(page_title="Weed Scouting Dashboard", layout="wide")
st.title("🌱 Weed Scouting Dashboard")
st.caption("Field-level weed risk analysis from scouting observations")


@st.cache_data(show_spinner=False)
def load_data(
    farms: list[str] | None = None,
    years: list[int] | None = None,
    crops: list[str] | None = None,
    weed_classes: list[str] | None = None,
):
    return build_dashboard_data(
        csv_path=DATA_PATH,
        farms=farms,
        years=years,
        crops=crops,
        weed_classes=weed_classes,
    )


if not DATA_PATH.exists():
    st.error(f"Dataset not found at: {DATA_PATH}. Add the real CSV and rerun the app.")
    st.stop()

base_data = load_data()

st.sidebar.header("Filters")
selected_farms = st.sidebar.multiselect("Farm", sorted(base_data.raw["Farm"].dropna().astype(str).unique()))
selected_years = st.sidebar.multiselect(
    "Year",
    sorted(base_data.raw["Year"].dropna().astype(int).unique()),
)
selected_crops = st.sidebar.multiselect("Crop", sorted(base_data.raw["Crop"].dropna().astype(str).unique()))
selected_weed_classes = st.sidebar.multiselect(
    "WeedClass", sorted(base_data.raw["WeedClass"].dropna().astype(str).unique())
)

result = load_data(
    farms=selected_farms,
    years=selected_years,
    crops=selected_crops,
    weed_classes=selected_weed_classes,
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Observations", f"{len(result.filtered):,}")
col2.metric("Fields", f"{result.field_metrics['Field_ID'].nunique():,}")
col3.metric("Unique Weeds", f"{result.filtered['Weed'].nunique():,}")
col4.metric("Avg PressureScore", f"{result.filtered['PressureScore'].mean():.2f}" if not result.filtered.empty else "0.00")

left, right = st.columns(2)

with left:
    st.subheader("Top Risky Fields")
    top_fields = result.field_metrics.head(10)
    if top_fields.empty:
        st.info("No data available for selected filters.")
    else:
        st.bar_chart(
            top_fields.set_index("Field_ID")["overall_weed_risk_score"],
            use_container_width=True,
        )

with right:
    st.subheader("Top Weeds by Avg PressureScore")
    top_weeds = result.weed_metrics.head(10)
    if top_weeds.empty:
        st.info("No data available for selected filters.")
    else:
        st.bar_chart(
            top_weeds.set_index("Weed")["avg_pressure_score"],
            use_container_width=True,
        )

st.subheader("Field Metrics")
if result.field_metrics.empty:
    st.info("No field metrics available for selected filters.")
else:
    display_table = result.field_metrics.copy()
    numeric_cols = [
        "avg_pressure_score",
        "max_pressure_score",
        "overall_weed_risk_score",
    ]
    display_table[numeric_cols] = display_table[numeric_cols].round(2)
    st.dataframe(display_table, use_container_width=True)

st.subheader("Field Detail")
if result.field_metrics.empty:
    st.info("Select filters with available fields to view details.")
else:
    selected_field = st.selectbox("Choose Field_ID", result.field_metrics["Field_ID"].tolist())
    field_rows = result.filtered[result.filtered["Field_ID"] == selected_field].copy()

    field_summary = result.field_metrics[result.field_metrics["Field_ID"] == selected_field]
    st.write("Selected field metrics")
    st.dataframe(field_summary, use_container_width=True)

    st.write("Weed observations for selected field")
    if field_rows.empty:
        st.info("No observations found for selected field.")
    else:
        detail_table = field_rows[
            [
                "ScoutingDate",
                "Weed",
                "WeedClass",
                "Pressure",
                "PressureScore",
                "ScoutedBy",
            ]
        ].sort_values("ScoutingDate", ascending=False)

        detail_table["ScoutingDate"] = pd.to_datetime(detail_table["ScoutingDate"]).dt.date
        st.dataframe(detail_table, use_container_width=True)
