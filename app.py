"""Professional Streamlit dashboard entrypoint for weed scouting analysis.

This version keeps the existing backend aggregation pipeline (`build_dashboard_data`)
while modernizing the UI/UX with custom styling, Plotly charts, and richer
field-level drill-downs.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.agro_ai import build_dashboard_data

DATA_PATH = Path("data/data_scout_ggdl.csv")

# -----------------------------------------------------------------------------
# Changed: explicit wide layout and collapsed sidebar for a more dashboard-like
# first impression.
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Weed Scouting Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------------------------------------------------
# Changed: global CSS theme for polished hierarchy, cards, containers, sidebar,
# and risk/weed-class badges.
# -----------------------------------------------------------------------------
def inject_custom_css() -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg-main: #f4f7fb;
                --panel-bg: #ffffff;
                --ink-900: #10243f;
                --ink-700: #355070;
                --ink-500: #6b7c93;
                --border: #dce5f0;
                --brand: #2a6fdb;
                --accent: #7db7ff;
                --low: #f4c542;
                --moderate: #f28c28;
                --high: #d7263d;
                --grass: #2f9e44;
                --broadleaf: #7b2cbf;
            }

            .stApp {
                background: linear-gradient(180deg, #f6f9fd 0%, #eef4fb 100%);
                color: var(--ink-900);
            }

            .block-container {
                padding-top: 1.2rem;
                padding-bottom: 2.0rem;
            }

            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #12233d 0%, #1d3557 100%);
                border-right: 1px solid rgba(255, 255, 255, 0.15);
            }

            [data-testid="stSidebar"] * {
                color: #edf3ff !important;
            }

            .top-header {
                background: linear-gradient(100deg, #12315a 0%, #245ea8 70%, #3b82f6 100%);
                border-radius: 18px;
                padding: 1.3rem 1.6rem;
                color: #ffffff;
                box-shadow: 0 12px 30px rgba(19, 49, 90, 0.22);
                margin-bottom: 1rem;
            }

            .top-header h1 {
                margin: 0;
                font-size: 1.75rem;
                font-weight: 700;
                letter-spacing: 0.2px;
            }

            .top-header p {
                margin: 0.3rem 0 0;
                color: #dfe9ff;
                font-size: 0.96rem;
            }

            .kpi-card {
                background: var(--panel-bg);
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 1rem;
                box-shadow: 0 4px 16px rgba(12, 35, 64, 0.08);
                min-height: 96px;
            }

            .kpi-label {
                font-size: 0.82rem;
                color: var(--ink-500);
                text-transform: uppercase;
                letter-spacing: 0.08em;
                margin-bottom: 0.35rem;
                font-weight: 600;
            }

            .kpi-value {
                font-size: 1.8rem;
                color: var(--ink-900);
                font-weight: 750;
                line-height: 1.1;
            }

            .chart-shell, .section-shell {
                background: var(--panel-bg);
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 0.9rem 1rem 0.6rem;
                box-shadow: 0 4px 16px rgba(12, 35, 64, 0.08);
                margin-bottom: 1rem;
            }

            .chart-title {
                margin: 0 0 0.55rem;
                font-size: 1.02rem;
                font-weight: 650;
                color: var(--ink-900);
            }

            .risk-badge, .weed-badge {
                display: inline-block;
                border-radius: 999px;
                font-size: 0.75rem;
                padding: 0.2rem 0.6rem;
                margin-right: 0.35rem;
                font-weight: 700;
                line-height: 1.5;
                border: 1px solid rgba(0,0,0,0.08);
            }

            .risk-low { background: rgba(244,197,66,0.22); color: #7b5a00; }
            .risk-moderate { background: rgba(242,140,40,0.22); color: #8a3f00; }
            .risk-high { background: rgba(215,38,61,0.18); color: #8b1022; }
            .weed-grass { background: rgba(47,158,68,0.2); color: #125d24; }
            .weed-broadleaf { background: rgba(123,44,191,0.18); color: #4d1578; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def risk_level(score: float) -> str:
    if score <= 30:
        return "low"
    if score <= 60:
        return "moderate"
    return "high"


def render_header() -> None:
    st.markdown(
        """
        <div class="top-header">
            <h1>🌱 Weed Scouting Intelligence Hub</h1>
            <p>Interactive agronomy analytics for field risk diagnostics, weed pressure monitoring, and management prioritization.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_data(
    farms: list[str] | None = None,
    years: list[int] | None = None,
    crops: list[str] | None = None,
    weed_classes: list[str] | None = None,
):
    # Preserved backend logic: still relies on existing project aggregation APIs.
    return build_dashboard_data(
        csv_path=DATA_PATH,
        farms=farms,
        years=years,
        crops=crops,
        weed_classes=weed_classes,
    )


def render_kpi_card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def field_year_trend(field_rows: pd.DataFrame) -> pd.DataFrame:
    if field_rows.empty:
        return pd.DataFrame(columns=["Year", "avg_pressure", "max_pressure", "observations"])
    trend = (
        field_rows.groupby("Year", as_index=False)
        .agg(
            avg_pressure=("PressureScore", "mean"),
            max_pressure=("PressureScore", "max"),
            observations=("PressureScore", "count"),
        )
        .sort_values("Year")
    )
    return trend


def as_badge(text: str, css_class: str) -> str:
    return f'<span class="{css_class}">{text}</span>'


inject_custom_css()
render_header()

if not DATA_PATH.exists():
    st.error(f"Dataset not found at: {DATA_PATH}. Add the real CSV and rerun the app.")
    st.stop()

base_data = load_data()

st.sidebar.markdown("### Dashboard Filters")
selected_farms = st.sidebar.multiselect(
    "Farm",
    sorted(base_data.raw["Farm"].dropna().astype(str).unique()),
)
selected_years = st.sidebar.multiselect(
    "Year",
    sorted(base_data.raw["Year"].dropna().astype(int).unique()),
)
selected_crops = st.sidebar.multiselect(
    "Crop",
    sorted(base_data.raw["Crop"].dropna().astype(str).unique()),
)
selected_weed_classes = st.sidebar.multiselect(
    "WeedClass",
    sorted(base_data.raw["WeedClass"].dropna().astype(str).unique()),
)

result = load_data(
    farms=selected_farms,
    years=selected_years,
    crops=selected_crops,
    weed_classes=selected_weed_classes,
)

# Changed: custom KPI card row for stronger visual hierarchy.
k1, k2, k3, k4 = st.columns(4)
with k1:
    render_kpi_card("Observations", f"{len(result.filtered):,}")
with k2:
    render_kpi_card("Fields", f"{result.field_metrics['Field_ID'].nunique():,}")
with k3:
    render_kpi_card("Unique Weeds", f"{result.filtered['Weed'].nunique():,}")
with k4:
    avg_ps = result.filtered["PressureScore"].mean() if not result.filtered.empty else 0
    render_kpi_card("Avg PressureScore", f"{avg_ps:.2f}")

c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="chart-shell"><h3 class="chart-title">Top Risky Fields</h3>', unsafe_allow_html=True)
    top_fields = result.field_metrics.head(12).copy()
    if top_fields.empty:
        st.info("No data available for selected filters.")
    else:
        top_fields = top_fields.sort_values("overall_weed_risk_score")
        fig_fields = px.bar(
            top_fields,
            x="overall_weed_risk_score",
            y="Field_ID",
            color="overall_weed_risk_score",
            color_continuous_scale=["#f4c542", "#f28c28", "#d7263d"],
            orientation="h",
            labels={"overall_weed_risk_score": "Weed Risk Score", "Field_ID": "Field"},
        )
        fig_fields.update_layout(height=390, margin=dict(l=8, r=8, t=8, b=8), coloraxis_showscale=False)
        st.plotly_chart(fig_fields, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="chart-shell"><h3 class="chart-title">Top Weeds by Avg PressureScore</h3>', unsafe_allow_html=True)
    top_weeds = result.weed_metrics.head(12).copy()
    if top_weeds.empty:
        st.info("No data available for selected filters.")
    else:
        top_weeds = top_weeds.sort_values("avg_pressure_score")
        fig_weeds = px.bar(
            top_weeds,
            x="avg_pressure_score",
            y="Weed",
            color="avg_pressure_score",
            color_continuous_scale=["#f4c542", "#f28c28", "#d7263d"],
            orientation="h",
            labels={"avg_pressure_score": "Avg PressureScore"},
        )
        fig_weeds.update_layout(height=390, margin=dict(l=8, r=8, t=8, b=8), coloraxis_showscale=False)
        st.plotly_chart(fig_weeds, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="chart-shell"><h3 class="chart-title">Farm Comparison (Avg Field Risk)</h3>', unsafe_allow_html=True)
if result.field_metrics.empty:
    st.info("No farm comparison available.")
else:
    farm_comp = (
        result.field_metrics.groupby("Farm", as_index=False)
        .agg(
            avg_field_risk=("overall_weed_risk_score", "mean"),
            fields=("Field_ID", "nunique"),
        )
        .sort_values("avg_field_risk", ascending=False)
    )
    fig_farm = px.bar(
        farm_comp,
        x="Farm",
        y="avg_field_risk",
        color="avg_field_risk",
        color_continuous_scale=["#f4c542", "#f28c28", "#d7263d"],
        text="fields",
        labels={"avg_field_risk": "Avg Field Risk Score", "fields": "Field Count"},
    )
    fig_farm.update_traces(texttemplate="%{text} fields", textposition="outside")
    fig_farm.update_layout(height=340, margin=dict(l=8, r=8, t=8, b=8), coloraxis_showscale=False)
    st.plotly_chart(fig_farm, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="section-shell"><h3 class="chart-title">Field Metrics Table</h3>', unsafe_allow_html=True)
if result.field_metrics.empty:
    st.info("No field metrics available for selected filters.")
else:
    display_table = result.field_metrics.copy()
    display_table["RiskLevel"] = display_table["overall_weed_risk_score"].apply(risk_level).str.title()
    numeric_cols = ["avg_pressure_score", "max_pressure_score", "overall_weed_risk_score"]
    display_table[numeric_cols] = display_table[numeric_cols].round(2)
    st.dataframe(
        display_table.rename(
            columns={
                "avg_pressure_score": "AvgPressure",
                "max_pressure_score": "MaxPressure",
                "overall_weed_risk_score": "WeedRiskScore",
                "unique_weed_species_count": "UniqueWeeds",
                "total_observations": "Observations",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="section-shell"><h3 class="chart-title">Interactive Field Summary</h3>', unsafe_allow_html=True)
if result.field_metrics.empty:
    st.info("Select filters with available fields to view details.")
else:
    field_options = result.field_metrics[["Field_ID", "Field"]].drop_duplicates()
    field_labels = [f"{row.Field_ID} — {row.Field}" for row in field_options.itertuples()]
    selected_label = st.selectbox("Select a field", field_labels)
    selected_field_id = selected_label.split(" — ")[0]

    field_rows = result.filtered[result.filtered["Field_ID"] == selected_field_id].copy()
    field_summary = result.field_metrics[result.field_metrics["Field_ID"] == selected_field_id].iloc[0]
    level = risk_level(float(field_summary["overall_weed_risk_score"]))

    risk_badge = as_badge(level.title(), f"risk-badge risk-{level}")
    st.markdown(f"**Risk Level:** {risk_badge}", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Weed Risk Score", f"{field_summary['overall_weed_risk_score']:.2f}")
    m2.metric("Average Pressure", f"{field_summary['avg_pressure_score']:.2f}")
    m3.metric("Max Pressure", f"{field_summary['max_pressure_score']:.2f}")
    m4.metric("Total Records", f"{int(field_summary['total_observations']):,}")

    info_left, info_right = st.columns([1, 2])
    with info_left:
        st.markdown("**Field Profile**")
        st.write(f"**Field:** {field_summary['Field']}")
        st.write(f"**Field ID:** {field_summary['Field_ID']}")
        st.write(f"**Farm:** {field_summary['Farm']}")
        st.write(f"**Crop:** {field_summary['Crop']}")

    with info_right:
        st.markdown("**Top Weeds in Selected Field**")
        top_field_weeds = (
            field_rows.groupby(["Weed", "WeedClass"], as_index=False)
            .agg(
                avg_pressure=("PressureScore", "mean"),
                max_pressure=("PressureScore", "max"),
                observations=("PressureScore", "count"),
            )
            .sort_values("avg_pressure", ascending=False)
            .head(10)
        )
        if top_field_weeds.empty:
            st.info("No weeds found for selected field.")
        else:
            top_field_weeds["avg_pressure"] = top_field_weeds["avg_pressure"].round(2)
            top_field_weeds["max_pressure"] = top_field_weeds["max_pressure"].round(2)
            top_field_weeds["WeedClass"] = top_field_weeds["WeedClass"].apply(
                lambda wc: as_badge(str(wc), "weed-badge weed-grass")
                if str(wc).lower() == "grass"
                else as_badge(str(wc), "weed-badge weed-broadleaf")
            )
            st.markdown(
                top_field_weeds.to_html(index=False, escape=False),
                unsafe_allow_html=True,
            )

    trend = field_year_trend(field_rows)
    if len(trend) > 1:
        st.markdown("**Year Trend (Selected Field)**")
        trend_long = trend.melt(
            id_vars="Year",
            value_vars=["avg_pressure", "max_pressure"],
            var_name="Metric",
            value_name="PressureScore",
        )
        fig_trend = px.line(
            trend_long,
            x="Year",
            y="PressureScore",
            color="Metric",
            markers=True,
            labels={"PressureScore": "PressureScore", "Metric": "Series"},
        )
        fig_trend.update_layout(height=300, margin=dict(l=8, r=8, t=8, b=8))
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("Year trend is not available for this field (insufficient multi-year data).")

st.markdown("</div>", unsafe_allow_html=True)
