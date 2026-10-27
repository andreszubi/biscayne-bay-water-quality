"""Biscayne Bay Water Quality Explorer.

An interactive Streamlit app for exploring water quality readings collected
by an autonomous vehicle in northern Biscayne Bay, Miami, FL.

Run locally with:  streamlit run app.py
"""
import pandas as pd
import streamlit as st

from src import charts
from src.config import (
    ALL_PARAMETERS,
    CORE_PARAMETERS,
    DATA_PATH,
    DEPTH_LABELS,
    DEPTH_ZONE_COL,
)
from src.data_loader import filter_data, load_data, survey_duration_min, track_distance_m
from src.insights import generate_insights

st.set_page_config(
    page_title="Biscayne Bay Water Quality Explorer",
    page_icon="🌊",
    layout="wide",
)


@st.cache_data
def get_data() -> pd.DataFrame:
    """Load the CSV once and reuse it across reruns."""
    return load_data(DATA_PATH)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def render_sidebar(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    """Draw the filter widgets and return the filtered data and selectable parameters."""
    st.sidebar.header("🔎 Filters")
    st.sidebar.caption("Every section of the app updates when you change these filters.")

    start, end = df["Timestamp"].min().to_pydatetime(), df["Timestamp"].max().to_pydatetime()
    time_range = st.sidebar.slider(
        "Time window",
        min_value=start,
        max_value=end,
        value=(start, end),
        format="HH:mm:ss",
        help="Limit the analysis to part of the survey.",
    )

    wp_min, wp_max = int(df["Waypoint"].min()), int(df["Waypoint"].max())
    waypoint_range = st.sidebar.slider(
        "Mission waypoints",
        min_value=wp_min,
        max_value=wp_max,
        value=(wp_min, wp_max),
        help="The vehicle follows a numbered list of waypoints. Pick a range of mission legs.",
    )

    depth_zones = st.sidebar.multiselect(
        "Depth zones",
        options=DEPTH_LABELS,
        default=DEPTH_LABELS,
        help="Water depth measured from the surface to the bay floor.",
    )

    include_optical = st.sidebar.checkbox(
        "Include uncalibrated optical sensors",
        value=False,
        help="Turbidity, chlorophyll and blue-green algae readings are offset below zero "
        "in this file, so they are hidden by default.",
    )

    filtered = filter_data(df, time_range, waypoint_range, depth_zones)
    st.sidebar.divider()
    st.sidebar.metric("Readings selected", f"{len(filtered):,}", f"of {len(df):,} total", delta_color="off")

    parameters = ALL_PARAMETERS if include_optical else CORE_PARAMETERS
    return filtered, parameters


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------
def render_overview(df: pd.DataFrame) -> None:
    st.subheader("Overview")
    st.markdown(
        "Biscayne Bay is a shallow, subtropical lagoon next to Miami that supports seagrass beds, "
        "fisheries and coral habitat. On **February 4, 2022**, an autonomous vehicle equipped with a "
        "multi-parameter water quality sonde surveyed a small area of the northern bay, logging its GPS "
        "position, the water depth and water chemistry about once per second. This app lets you explore "
        "that survey: how conditions changed over time, how parameters relate to each other, and where "
        "along the route each reading was taken."
    )

    cols = st.columns(5)
    cols[0].metric("Avg. temperature", f"{df['Temperature (°C)'].mean():.2f} °C")
    cols[1].metric("Avg. salinity", f"{df['Salinity (ppt)'].mean():.1f} ppt")
    cols[2].metric("Avg. dissolved oxygen", f"{df['Dissolved Oxygen (mg/L)'].mean():.2f} mg/L")
    cols[3].metric("Avg. pH", f"{df['pH'].mean():.2f}")
    cols[4].metric(
        "Distance surveyed",
        f"{track_distance_m(df):,.0f} m",
        f"{survey_duration_min(df):.1f} min",
        delta_color="off",
    )

    left, right = st.columns(2)
    with left:
        st.markdown("#### How to use this app")
        st.markdown(
            "1. Use the **Filters** in the sidebar to choose a time window, mission waypoints and depth zones.\n"
            "2. Browse the tabs above: **Data** shows the raw table, **Visualizations** has interactive "
            "Plotly charts, **Map** shows the vehicle's route and **Insights** summarizes the findings.\n"
            "3. Hover over any chart for exact values, drag to zoom, and double-click to reset.\n"
            "4. Download the filtered data as a CSV from the **Data** tab."
        )
    with right:
        st.markdown("#### What is measured")
        st.markdown("\n".join(f"- **{name}** — {desc}" for name, desc in ALL_PARAMETERS.items()))


def render_data(df: pd.DataFrame, parameters: dict[str, str]) -> None:
    st.subheader("Data Explorer")
    st.markdown(
        "The table below shows the cleaned readings that match your filters. Raw sensor column names "
        "were renamed to plain-language names with units, and each reading was assigned a depth zone."
    )

    base_cols = ["Timestamp", "Latitude", "Longitude", "Waypoint", DEPTH_ZONE_COL]
    columns = st.multiselect(
        "Columns to display",
        options=base_cols + list(parameters),
        default=["Timestamp", DEPTH_ZONE_COL, *list(parameters)[:5]],
    )
    if not columns:
        st.info("Select at least one column to display the table.")
        return

    st.dataframe(df[columns], hide_index=True, width="stretch", height=380)
    st.download_button(
        "⬇️ Download filtered data (CSV)",
        data=df[columns].to_csv(index=False).encode("utf-8"),
        file_name="biscayne_bay_filtered.csv",
        mime="text/csv",
    )

    numeric = [c for c in columns if pd.api.types.is_numeric_dtype(df[c])]
    if numeric:
        st.markdown("#### Summary statistics")
        st.caption("Count, mean, standard deviation, minimum, quartiles and maximum for each numeric column.")
        st.dataframe(df[numeric].describe().T.round(3), width="stretch")


def render_visualizations(df: pd.DataFrame, parameters: dict[str, str]) -> None:
    st.subheader("Visualizations")
    names = list(parameters)

    st.markdown("#### Trend over time")
    st.markdown(
        "See how a parameter changed during the survey. The rolling average smooths out sensor noise "
        "so the overall trend is easier to read."
    )
    c1, c2, c3 = st.columns([2, 2, 1])
    param = c1.selectbox("Parameter", names, key="ts_param")
    window = c2.slider("Rolling average window (readings)", 1, 120, 30, step=1)
    show_raw = c3.checkbox("Show raw readings", value=True)
    st.plotly_chart(charts.time_series(df, param, window, show_raw), width="stretch")
    st.caption(parameters[param])

    st.divider()
    st.markdown("#### Relationships")
    st.markdown(
        "Compare two parameters. Each dot is one reading, coloured by depth zone. The dashed line is a "
        "least-squares fit, and **r** in the legend is the Pearson correlation (−1 to 1)."
    )
    c1, c2 = st.columns(2)
    x = c1.selectbox("X axis", names, index=names.index("Temperature (°C)"), key="rel_x")
    y = c2.selectbox("Y axis", names, index=names.index("Salinity (ppt)"), key="rel_y")
    if x == y:
        st.info("Pick two different parameters to compare.")
    else:
        st.plotly_chart(charts.relationship(df, x, y), width="stretch")

    st.divider()
    st.markdown("#### Distribution")
    st.markdown(
        "How are the values spread out? The histogram counts readings in each value range, and the box "
        "plot above it marks the median, quartiles and outliers for each depth zone."
    )
    dist_param = st.selectbox("Parameter", names, index=names.index("Dissolved Oxygen (mg/L)"), key="dist")
    st.plotly_chart(charts.distribution(df, dist_param), width="stretch")


def render_map(df: pd.DataFrame, parameters: dict[str, str]) -> None:
    st.subheader("Survey Map")
    st.markdown(
        "Each dot is a reading at the vehicle's GPS position. Choose a parameter to colour the route and "
        "spot where in the bay conditions change. Green marks where the selected data starts and red "
        "where it ends."
    )
    names = list(parameters)
    param = st.selectbox("Colour the track by", names, index=names.index("Water Depth (m)"), key="map_param")
    st.plotly_chart(charts.track_map(df, param), width="stretch")
    st.caption(parameters[param])


def render_insights(df: pd.DataFrame, parameters: dict[str, str]) -> None:
    st.subheader("Insights")
    st.markdown("Key findings, recalculated automatically for the data that matches your filters:")
    for text in generate_insights(df):
        st.markdown(f"- {text}")

    st.divider()
    st.markdown("#### Correlation matrix")
    st.markdown(
        "Each cell is the Pearson correlation between two parameters. Red cells rise together, blue cells "
        "move in opposite directions, and white means there is no linear link."
    )
    st.plotly_chart(charts.correlation_heatmap(df, list(parameters)), width="stretch")

    st.divider()
    st.markdown("#### Compare depth zones")
    st.markdown("Does a parameter differ between shallow and deep water? Bars show the average in each zone.")
    names = list(parameters)
    param = st.selectbox("Parameter", names, index=names.index("Dissolved Oxygen (mg/L)"), key="zone")
    st.plotly_chart(charts.zone_comparison(df, param), width="stretch")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    st.title("🌊 Biscayne Bay Water Quality Explorer")
    st.caption("Interactive analysis of autonomous-vehicle water quality data · Northern Biscayne Bay, Miami, FL")

    df_all = get_data()
    df, parameters = render_sidebar(df_all)

    if len(df) < 2:
        st.warning("No data matches the current filters. Widen the time window, waypoints or depth zones.")
        st.stop()

    overview, data, visuals, survey_map, insights = st.tabs(
        ["📋 Overview", "🗂️ Data", "📈 Visualizations", "🗺️ Map", "💡 Insights"]
    )
    with overview:
        render_overview(df)
    with data:
        render_data(df, parameters)
    with visuals:
        render_visualizations(df, parameters)
    with survey_map:
        render_map(df, parameters)
    with insights:
        render_insights(df, parameters)

    st.divider()
    st.caption("Data: Biscayne Bay autonomous vehicle survey, Feb 4, 2022 (CIS 3590 course dataset). Built with Streamlit and Plotly.")


if __name__ == "__main__":
    main()
