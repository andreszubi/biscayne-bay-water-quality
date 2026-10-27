"""Plotly figure builders.

Every function takes an already-filtered DataFrame and returns a Plotly
figure with a title, labelled axes and a legend, ready for st.plotly_chart.
"""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.config import DEPTH_COLORS, DEPTH_LABELS, DEPTH_ZONE_COL, MAP_CENTER


def _finish(fig: go.Figure, title: str, legend_title: str = "") -> go.Figure:
    """Apply the shared title/legend/margin styling used by every chart."""
    fig.update_layout(
        title={"text": title, "x": 0, "xanchor": "left"},
        legend={
            "title": {"text": legend_title},
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.0,
            "xanchor": "right",
            "x": 1,
        },
        margin={"l": 10, "r": 10, "t": 70, "b": 10},
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
                line={"width": 1, "color": "#9DB4C8"},
            )
        )
    fig.add_trace(
        go.Scatter(
            x=df["Timestamp"],
            y=df[parameter].rolling(window, min_periods=1, center=True).mean(),
            mode="lines",
            name=f"{window}-reading rolling average",
            line={"width": 3, "color": "#1F6FB2"},
        )
    )
    fig.update_xaxes(title_text="Time of day (Feb 4, 2022)", tickformat="%H:%M")
    fig.update_yaxes(title_text=parameter)
    return _finish(fig, f"{parameter} over time", "Series")


def relationship(df: pd.DataFrame, x: str, y: str) -> go.Figure:
    """Scatter plot of two parameters, coloured by depth zone, with a linear fit."""
    fig = px.scatter(
        df,
        x=x,
        y=y,
        color=DEPTH_ZONE_COL,
        color_discrete_map=DEPTH_COLORS,
        category_orders={DEPTH_ZONE_COL: DEPTH_LABELS},
        opacity=0.75,
        hover_data={"Timestamp": "|%H:%M:%S", "Waypoint": True},
    )
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
                line={"color": "#E4572E", "width": 2, "dash": "dash"},
            )
        )
    fig.update_xaxes(title_text=x)
    fig.update_yaxes(title_text=y)
    return _finish(fig, f"{y} vs. {x}", "Depth zone")


def distribution(df: pd.DataFrame, parameter: str) -> go.Figure:
    """Overlaid histograms of a parameter per depth zone, with a box plot on top."""
    fig = px.histogram(
        df,
        x=parameter,
        color=DEPTH_ZONE_COL,
        color_discrete_map=DEPTH_COLORS,
        category_orders={DEPTH_ZONE_COL: DEPTH_LABELS},
        marginal="box",
        barmode="overlay",
        opacity=0.7,
        nbins=40,
    )
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
        text_auto=".2f",
        hover_data={"count": True},
    )
    fig.update_xaxes(title_text="Depth zone")
    fig.update_yaxes(title_text=f"Mean {parameter}")
    return _finish(fig, f"Average {parameter} by depth zone (error bars = ±1 std)", "Depth zone")


def correlation_heatmap(df: pd.DataFrame, parameters: list[str]) -> go.Figure:
    """Pearson correlation matrix between the selected parameters."""
    corr = df[parameters].corr().round(2)
    fig = px.imshow(
        corr,
        text_auto=True,
        zmin=-1,
        zmax=1,
        color_continuous_scale="RdBu_r",
        aspect="auto",
    )
    fig.update_xaxes(title_text="Parameter", tickangle=-30)
    fig.update_yaxes(title_text="Parameter")
    fig.update_coloraxes(colorbar_title_text="Correlation (r)")
    fig = _finish(fig, "Correlation between water quality parameters")
    # A heatmap's legend is its colour bar; there are no discrete traces to list.
    fig.update_layout(showlegend=False)
    return fig


def track_map(df: pd.DataFrame, parameter: str) -> go.Figure:
    """Vehicle GPS track on a street map, coloured by the chosen parameter."""
    fig = px.scatter_map(
        df,
        lat="Latitude",
        lon="Longitude",
        color=parameter,
        color_continuous_scale="Viridis",
        hover_data={"Timestamp": "|%H:%M:%S", "Waypoint": True, "Water Depth (m)": ":.2f"},
        center=MAP_CENTER,
        zoom=16,
        map_style="carto-positron",
    )
    fig.update_traces(marker={"size": 8}, name="Reading", showlegend=True)
    # Start and end markers make the direction of travel obvious.
    for label, row, color in (("Start", df.iloc[0], "#2CA02C"), ("End", df.iloc[-1], "#D62728")):
        fig.add_trace(
            go.Scattermap(
                lat=[row["Latitude"]],
                lon=[row["Longitude"]],
                mode="markers",
                marker={"size": 16, "color": color},
                name=f"{label} ({row['Timestamp']:%H:%M:%S})",
            )
        )
    fig.update_coloraxes(colorbar_title_text=parameter)
    fig.update_layout(height=560)
    return _finish(fig, f"Vehicle track coloured by {parameter}", "Markers")
