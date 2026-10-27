"""Plotly figure builders.

Every function takes an already-filtered DataFrame and returns a Plotly
figure with a title, labelled axes and a legend, ready for st.plotly_chart.
Colours come from src/config.py and are readable on both the light and dark
themes; Streamlit's chart theme supplies the matching text and grid colours.
"""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.colors import sample_colorscale

from src.config import (
    ACCENT_COLOR,
    CONTEXT_COLOR,
    DEPTH_COLORS,
    DEPTH_LABELS,
    DEPTH_PATTERNS,
    DEPTH_SYMBOLS,
    DEPTH_ZONE_COL,
    DIVERGING_SCALE,
    END_COLOR,
    FIT_LINE_COLOR,
    START_COLOR,
)
from src.colors import readable_text_on

DEPTH_ORDER = {DEPTH_ZONE_COL: DEPTH_LABELS}


def _finish(fig: go.Figure, title: str, legend_title: str = "") -> go.Figure:
    """Apply the shared title/legend/margin styling used by every chart."""
    fig.update_layout(
        # Title sits at the very top; the legend sits just above the plot area,
        # so the two never overlap even when the title is long.
        title={"text": title, "x": 0, "xanchor": "left", "yref": "container", "y": 0.98, "yanchor": "top"},
        legend={
            "title": {"text": legend_title},
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
        },
        margin={"l": 10, "r": 10, "t": 100, "b": 10},
        font={"size": 14},
        showlegend=True,
    )
    return fig


def time_series(df: pd.DataFrame, parameter: str, window: int, show_raw: bool = True) -> go.Figure:
    """Line chart of a parameter over time with a rolling-average overlay."""
    fig = go.Figure()
    if show_raw:
        fig.add_trace(
            go.Scatter(
                x=df["Timestamp"],
                y=df[parameter],
                mode="lines",
                name="Raw reading",
                line={"width": 1.5, "color": CONTEXT_COLOR},
            )
        )
    fig.add_trace(
        go.Scatter(
            x=df["Timestamp"],
            y=df[parameter].rolling(window, min_periods=1, center=True).mean(),
            mode="lines",
            name=f"{window}-reading rolling average",
            line={"width": 3, "color": ACCENT_COLOR},
        )
    )
    fig.update_xaxes(title_text="Time of day (Feb 4, 2022)", tickformat="%H:%M")
    fig.update_yaxes(title_text=parameter)
    fig.update_layout(hovermode="x unified")
    return _finish(fig, f"{parameter} over time", "Series")


def relationship(df: pd.DataFrame, x: str, y: str) -> go.Figure:
    """Scatter plot of two parameters by depth zone (colour + shape), with a linear fit."""
    fig = px.scatter(
        df,
        x=x,
        y=y,
        color=DEPTH_ZONE_COL,
        color_discrete_map=DEPTH_COLORS,
        symbol=DEPTH_ZONE_COL,
        symbol_map=DEPTH_SYMBOLS,
        category_orders=DEPTH_ORDER,
        opacity=0.85,
        hover_data={"Timestamp": "|%H:%M:%S", "Waypoint": True},
    )
    fig.update_traces(marker={"size": 8})
    # Least-squares trend line (numpy only, so no statsmodels dependency).
    clean = df[[x, y]].dropna()
    if len(clean) > 1 and clean[x].nunique() > 1:
        slope, intercept = np.polyfit(clean[x], clean[y], 1)
        xs = np.linspace(clean[x].min(), clean[x].max(), 50)
        r = clean[x].corr(clean[y])
        fig.add_trace(
            go.Scatter(
                x=xs,
                y=slope * xs + intercept,
                mode="lines",
                name=f"Linear fit (r = {r:.2f})",
                line={"color": FIT_LINE_COLOR, "width": 3, "dash": "dash"},
            )
        )
    fig.update_xaxes(title_text=x)
    fig.update_yaxes(title_text=y)
    return _finish(fig, f"{y} vs. {x}", "Depth zone")


def distribution(df: pd.DataFrame, parameter: str) -> go.Figure:
    """Stacked histogram of a parameter by depth zone (colour + pattern), with box plots on top."""
    fig = px.histogram(
        df,
        x=parameter,
        color=DEPTH_ZONE_COL,
        color_discrete_map=DEPTH_COLORS,
        pattern_shape=DEPTH_ZONE_COL,
        pattern_shape_map=DEPTH_PATTERNS,
        category_orders=DEPTH_ORDER,
        marginal="box",
        barmode="stack",
        nbins=40,
    )
    fig.update_layout(bargap=0.08)
    fig.update_xaxes(title_text=parameter, row=1, col=1)
    fig.update_yaxes(title_text="Number of readings", row=1, col=1)
    return _finish(fig, f"Distribution of {parameter} by depth zone", "Depth zone")


def zone_comparison(df: pd.DataFrame, parameter: str) -> go.Figure:
    """Bar chart of a parameter's mean (± 1 std) in each depth zone."""
    stats = (
        df.groupby(DEPTH_ZONE_COL, observed=True)[parameter]
        .agg(["mean", "std", "count"])
        .reindex(DEPTH_LABELS)
        .dropna(subset=["mean"])
        .reset_index()
    )
    fig = px.bar(
        stats,
        x=DEPTH_ZONE_COL,
        y="mean",
        error_y="std",
        color=DEPTH_ZONE_COL,
        color_discrete_map=DEPTH_COLORS,
        category_orders=DEPTH_ORDER,
        text_auto=".2f",
        hover_data={"count": True},
    )
    # Each bar is named on the x axis, so no fill pattern is needed here (it
    # would also hide the value labels). Black labels reach 4.5:1 on every bar.
    fig.update_traces(
        textposition="inside",
        insidetextanchor="middle",
        textfont={"size": 16, "color": "#000000"},
        error_y={"color": CONTEXT_COLOR, "thickness": 2},
    )
    fig.update_xaxes(title_text="Depth zone")
    fig.update_yaxes(title_text=f"Mean {parameter}")
    return _finish(fig, f"Average {parameter} by depth zone (error bars = ±1 std)", "Depth zone")


def correlation_heatmap(df: pd.DataFrame, parameters: list[str]) -> go.Figure:
    """Pearson correlation matrix between the selected parameters."""
    corr = df[parameters].corr().round(2)
    fig = px.imshow(
        corr,
        zmin=-1,
        zmax=1,
        color_continuous_scale=DIVERGING_SCALE,
        aspect="auto",
    )
    fig.update_traces(xgap=2, ygap=2)
    # Label each cell in black or white depending on the cell colour, so the
    # numbers stay readable whatever the page theme is.
    for row in corr.index:
        for col in corr.columns:
            value = corr.loc[row, col]
            if pd.isna(value):
                continue
            fill = sample_colorscale(DIVERGING_SCALE, (value + 1) / 2)[0]
            fig.add_annotation(
                x=col, y=row, text=f"{value:.2f}", showarrow=False,
                font={"color": readable_text_on(fill), "size": 13},
            )
    fig.update_xaxes(title_text="Parameter", tickangle=-30)
    fig.update_yaxes(title_text="Parameter")
    fig.update_coloraxes(colorbar_title_text="Correlation (r)")
    fig.update_layout(height=560)
    fig = _finish(fig, "Correlation between water quality parameters")
    # A heatmap's legend is its colour bar; there are no discrete traces to list.
    fig.update_layout(showlegend=False)
    return fig


def track_map(df: pd.DataFrame, parameter: str, dark: bool = False) -> go.Figure:
    """Vehicle GPS track on a street map, coloured by the chosen parameter.

    `dark` picks a dark basemap and trims the colour scale so that no marker
    colour blends into the map behind it.
    """
    viridis = px.colors.sequential.Viridis
    fig = px.scatter_map(
        df,
        lat="Latitude",
        lon="Longitude",
        color=parameter,
        # Drop the darkest colours on a dark map and the yellow end on a light one.
        color_continuous_scale=viridis[3:] if dark else viridis[:8],
        hover_data={"Timestamp": "|%H:%M:%S", "Waypoint": True, "Water Depth (m)": ":.2f"},
        center={"lat": df["Latitude"].mean(), "lon": df["Longitude"].mean()},
        zoom=17.5,
        map_style="carto-darkmatter" if dark else "carto-positron",
    )
    # The colour bar explains the readings; the legend lists the start/end markers.
    fig.update_traces(marker={"size": 9}, name="Reading", showlegend=False)
    # Start/end markers carry a text label, so they are not told apart by colour alone.
    # The labels sit on opposite sides because the route often ends where it began.
    label_color = "#FFFFFF" if dark else "#000000"
    markers = (
        ("Start", df.iloc[0], START_COLOR, "bottom left"),
        ("End", df.iloc[-1], END_COLOR, "top right"),
    )
    for label, row, color, position in markers:
        fig.add_trace(
            go.Scattermap(
                lat=[row["Latitude"]],
                lon=[row["Longitude"]],
                mode="markers+text",
                marker={"size": 18, "color": color},
                text=[label],
                textposition=position,
                textfont={"size": 15, "color": label_color},
                name=f"{label} ({row['Timestamp']:%H:%M:%S})",
            )
        )
    fig.update_coloraxes(colorbar_title_text=parameter)
    fig.update_layout(height=560)
    return _finish(fig, f"Vehicle track coloured by {parameter}", "Markers")
