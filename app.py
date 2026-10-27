"""Biscayne Bay Water Quality Explorer.

An interactive Streamlit app for exploring water quality readings collected
by an autonomous vehicle in northern Biscayne Bay, Miami, FL.

Run locally with:  streamlit run app.py
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import charts, map3d
from src.config import (
    ALL_PARAMETERS,
    CORE_PARAMETERS,
    DATA_PATH,
    DEPTH_LABELS,
    DEPTH_ZONE_COL,
    TAG_BACKGROUND,
    TAG_TEXT,
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


def apply_accessibility_styles() -> None:
    """Small CSS fixes for contrast problems the theme settings cannot reach."""
    st.html(
        f"""<style>
        [data-testid="stMultiSelectTagsContainer"] [data-tag] {{
            background-color: {TAG_BACKGROUND} !important;
            color: {TAG_TEXT} !important;
        }}
        /* Slider min/max labels are faded to ~4.2:1 by default; use full text colour. */
        [data-testid="stSliderTickBar"] {{
            color: inherit !important;
        }}
        /* Map credits ("© OpenStreetMap contributors") inherit the page text colour in
           the 3D map, which is unreadable on their white box in the dark theme. */
        .mapboxgl-ctrl-attrib, .maplibregl-ctrl-attrib,
        .mapboxgl-ctrl-attrib a, .maplibregl-ctrl-attrib a {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }}
        /* Let metric labels wrap instead of being cut off with "…" on narrow screens. */
        [data-testid="stMetricLabel"],
        [data-testid="stMetricLabel"] * {{
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: clip !important;
        }}
        </style>"""
    )


def show_chart(fig: go.Figure, table: pd.DataFrame, summary: str) -> None:
    """Draw a chart followed by a text summary and the same data as a table.

    The summary and table give screen-reader and keyboard users the
    information the chart shows visually (WCAG 1.1.1 non-text content).
    """
    st.plotly_chart(fig, width="stretch")
    summary_and_table(table, summary)


def summary_and_table(table: pd.DataFrame, summary: str) -> None:
    """Written summary plus an expandable data table for a chart or map."""
    st.markdown(f"**Chart summary:** {summary}")
    with st.expander("View the data behind this chart as a table"):
        st.dataframe(table, hide_index=True, width="stretch")


def note(text: str, container=st) -> None:
    """Secondary text in italics at full text colour.

    st.caption fades text to about 4.2:1 contrast, which is below the WCAG AA
    minimum of 4.5:1, so it is not used in this app.
    """
    container.markdown(f"*{text}*")


def describe_range(series: pd.Series) -> str:
    """'from 5.03 to 6.48 (average 5.37)' for a numeric column."""
    return f"from {series.min():,.2f} to {series.max():,.2f} (average {series.mean():,.2f})"


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def render_sidebar(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str], bool]:
    """Draw the filter widgets and return the filtered data and selectable parameters."""
    st.sidebar.header("🔎 Filters")
    note("Every section of the app updates when you change these filters.", st.sidebar)

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
    st.sidebar.metric("Readings selected", f"{len(filtered):,} of {len(df):,}")

    st.sidebar.divider()
    st.sidebar.header("🌓 Appearance")
    st.sidebar.markdown(
        "Switch between the **light** and **dark** themes from the **⋮ menu** at the top right of the "
        "page (**System**, **Light** or **Dark**). By default the app follows your device setting."
    )
    map_background = st.sidebar.radio(
        "Map background",
        ["Match app theme", "Light", "Dark"],
        help="Applies to the 2D and 3D maps. The street map is an image, so it can be switched "
        "separately. With 'Match app theme', the maps catch up with a theme change the next time "
        "you interact with the app.",
    )
    if map_background == "Match app theme":
        dark_map = st.context.theme.type == "dark"
    else:
        dark_map = map_background == "Dark"

    parameters = ALL_PARAMETERS if include_optical else CORE_PARAMETERS
    return filtered, parameters, dark_map


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------
def render_overview(df: pd.DataFrame) -> None:
    st.header("Overview")
    st.markdown(
        "Biscayne Bay is a shallow, subtropical lagoon next to Miami that supports seagrass beds, "
        "fisheries and coral habitat. On **February 4, 2022**, an autonomous vehicle equipped with a "
        "multi-parameter water quality sonde surveyed a small area of the northern bay, logging its GPS "
        "position, the water depth and water chemistry about once per second. This app lets you explore "
        "that survey: how conditions changed over time, how parameters relate to each other, and where "
        "along the route each reading was taken."
    )

    # Two rows of three, with units in the labels so the large values stay short
    # numbers that are never cut off. Bottom alignment keeps the numbers level
    # when a long label wraps onto two lines on narrow screens.
    top, bottom = st.columns(3, vertical_alignment="bottom"), st.columns(3, vertical_alignment="bottom")
    top[0].metric("Avg. temperature (°C)", f"{df['Temperature (°C)'].mean():.2f}")
    top[1].metric("Avg. salinity (ppt)", f"{df['Salinity (ppt)'].mean():.1f}")
    top[2].metric("Avg. dissolved oxygen (mg/L)", f"{df['Dissolved Oxygen (mg/L)'].mean():.2f}")
    bottom[0].metric("Avg. pH", f"{df['pH'].mean():.2f}")
    bottom[1].metric("Distance surveyed (m)", f"{track_distance_m(df):,.0f}")
    bottom[2].metric("Survey duration (min)", f"{survey_duration_min(df):.1f}")

    left, right = st.columns(2)
    with left:
        st.subheader("How to use this app")
        st.markdown(
            "1. Use the **Filters** in the sidebar to choose a time window, mission waypoints and depth zones.\n"
            "2. Browse the tabs above: **Data** shows the raw table, **Visualizations** has interactive "
            "Plotly charts, **Map** shows the vehicle's route and **Insights** summarizes the findings.\n"
            "3. Hover over any chart for exact values, drag to zoom, and double-click to reset.\n"
            "4. Every chart is followed by a written summary and a **View the data behind this chart** "
            "table, so the information is available without seeing the chart.\n"
            "5. Download the filtered data as a CSV from the **Data** tab.\n"
            "6. Prefer a light or dark screen? Open the **⋮ menu** (top right) and choose **Light** or "
            "**Dark**, or **System** to follow your device."
        )
    with right:
        st.subheader("What is measured")
        st.markdown("\n".join(f"- **{name}** — {desc}" for name, desc in ALL_PARAMETERS.items()))


def render_data(df: pd.DataFrame, parameters: dict[str, str]) -> None:
    st.header("Data Explorer")
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
        st.subheader("Summary statistics")
        note("Count, mean, standard deviation, minimum, quartiles and maximum for each numeric column.")
        st.dataframe(df[numeric].describe().T.round(3), width="stretch")


def render_visualizations(df: pd.DataFrame, parameters: dict[str, str]) -> None:
    st.header("Visualizations")
    names = list(parameters)

    st.subheader("Trend over time")
    st.markdown(
        "See how a parameter changed during the survey. The rolling average smooths out sensor noise "
        "so the overall trend is easier to read."
    )
    c1, c2, c3 = st.columns([2, 2, 1])
    param = c1.selectbox("Parameter", names, key="ts_param")
    window = c2.slider("Rolling average window (readings)", 1, 120, 30, step=1)
    show_raw = c3.checkbox("Show raw readings", value=True)
    note(parameters[param])
    show_chart(
        charts.time_series(df, param, window, show_raw),
        df[["Timestamp", param]],
        f"{param} ranged {describe_range(df[param])} between "
        f"{df['Timestamp'].min():%H:%M:%S} and {df['Timestamp'].max():%H:%M:%S}.",
    )

    st.divider()
    st.subheader("Relationships")
    st.markdown(
        "Compare two parameters. Each point is one reading; its colour and shape show the depth zone. The dashed line is a "
        "least-squares fit, and **r** in the legend is the Pearson correlation (−1 to 1)."
    )
    c1, c2 = st.columns(2)
    x = c1.selectbox("X axis", names, index=names.index("Temperature (°C)"), key="rel_x")
    y = c2.selectbox("Y axis", names, index=names.index("Salinity (ppt)"), key="rel_y")
    if x == y:
        st.info("Pick two different parameters to compare.")
    else:
        r = df[x].corr(df[y])
        show_chart(
            charts.relationship(df, x, y),
            df[["Timestamp", DEPTH_ZONE_COL, x, y]],
            f"{len(df):,} readings. The correlation between {x} and {y} is r = {r:.2f} "
            f"({'positive' if r > 0 else 'negative'}: as {x} rises, {y} tends to "
            f"{'rise' if r > 0 else 'fall'}).",
        )

    st.divider()
    st.subheader("Distribution")
    st.markdown(
        "How are the values spread out? The stacked histogram counts readings in each value range, split by "
        "depth zone (each zone has its own colour and fill pattern). The box plots above it mark the median, "
        "quartiles and outliers for each zone."
    )
    dist_param = st.selectbox("Parameter", names, index=names.index("Dissolved Oxygen (mg/L)"), key="dist")
    zone_stats = (
        df.groupby(DEPTH_ZONE_COL, observed=True)[dist_param]
        .describe()[["count", "min", "25%", "50%", "75%", "max"]]
        .round(2)
        .reset_index()
    )
    show_chart(
        charts.distribution(df, dist_param),
        zone_stats,
        f"{dist_param} ranged {describe_range(df[dist_param])}; the median was {df[dist_param].median():.2f}. "
        "The table lists the box-plot values for each depth zone.",
    )


def render_map(df: pd.DataFrame, parameters: dict[str, str], dark_map: bool) -> None:
    st.header("Survey Map")
    st.markdown(
        "See where along the vehicle's route each reading was taken. Choose a parameter to show on both "
        "maps below and spot where in the bay conditions change. The labels **Start** and **End** show "
        "where the selected data begins and ends. You can change the map background in the sidebar."
    )
    names = list(parameters)
    param = st.selectbox("Parameter to show on the maps", names, index=names.index("Water Depth (m)"), key="map_param")
    note(parameters[param])
    table = df[["Timestamp", "Latitude", "Longitude", "Waypoint", param]]

    st.subheader("2D street map")
    st.markdown("Each dot is one reading at the vehicle's GPS position, coloured by the selected parameter.")
    show_chart(
        charts.track_map(df, param, dark=dark_map),
        table,
        f"The vehicle travelled about {track_distance_m(df):,.0f} m. Along the route, {param} ranged "
        f"{describe_range(df[param])}.",
    )

    st.subheader("3D map")
    st.markdown(
        "The same readings as columns standing on a tilted map: **taller, brighter columns mean higher "
        f"{param}**. Drag to move the map, hold **Shift** (or right-click) and drag to rotate and tilt it, "
        "scroll to zoom, and hover over a column for its exact value. With a keyboard, click the map and "
        "use the **arrow keys** to move, **Shift + arrow keys** to rotate and tilt, and **+ / −** to zoom."
    )
    st.html(map3d.legend_html(df, param, dark=dark_map))
    high, low = df.loc[df[param].idxmax()], df.loc[df[param].idxmin()]
    summary_3d = (
        f"The tallest column ({param} {high[param]:,.2f}) was recorded at {high['Timestamp']:%H:%M:%S} "
        f"and the shortest ({low[param]:,.2f}) at {low['Timestamp']:%H:%M:%S}."
    )
    st.pydeck_chart(
        map3d.track_3d_map(df, param, dark=dark_map),
        height=560,
        alt=f"3D map of the survey route with one column per reading. {summary_3d}",
    )
    summary_and_table(table, summary_3d)


def render_insights(df: pd.DataFrame, parameters: dict[str, str]) -> None:
    st.header("Insights")
    st.markdown("Key findings, recalculated automatically for the data that matches your filters:")
    for text in generate_insights(df):
        st.markdown(f"- {text}")

    st.divider()
    st.subheader("Correlation matrix")
    st.markdown(
        "Each cell is the Pearson correlation (r) between two parameters, and its value is printed in the "
        "cell. Red cells rise together, blue cells move in opposite directions, and grey means there is no "
        "linear link."
    )
    corr = df[list(parameters)].corr().round(2)
    show_chart(
        charts.correlation_heatmap(df, list(parameters)),
        corr.reset_index(names="Parameter"),
        "A grid of correlations between every pair of parameters. The table shows the same values.",
    )

    st.divider()
    st.subheader("Compare depth zones")
    st.markdown("Does a parameter differ between shallow and deep water? Bars show the average in each zone.")
    names = list(parameters)
    param = st.selectbox("Parameter", names, index=names.index("Dissolved Oxygen (mg/L)"), key="zone")
    means = df.groupby(DEPTH_ZONE_COL, observed=True)[param].agg(["mean", "std", "count"]).round(2)
    show_chart(
        charts.zone_comparison(df, param),
        means.reset_index(),
        "Average " + param + ": "
        + "; ".join(f"{zone} {row['mean']:.2f}" for zone, row in means.iterrows()) + ".",
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    apply_accessibility_styles()
    st.title("🌊 Biscayne Bay Water Quality Explorer")
    note("Interactive analysis of autonomous-vehicle water quality data · Northern Biscayne Bay, Miami, FL")

    df_all = get_data()
    df, parameters, dark_map = render_sidebar(df_all)

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
        render_map(df, parameters, dark_map)
    with insights:
        render_insights(df, parameters)

    st.divider()
    note("Data: Biscayne Bay autonomous vehicle survey, Feb 4, 2022. Built with Streamlit and Plotly.")


if __name__ == "__main__":
    main()
