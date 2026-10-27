"""3D map of the survey built with pydeck (deck.gl), which ships with Streamlit.

Each reading is drawn as a column standing on a tilted street map. A column's
height AND colour both show the selected parameter, so the value is never
carried by colour alone. deck.gl has no built-in legend, so `legend_html`
returns one to place next to the map.
"""
import pandas as pd
import pydeck as pdk
from plotly.colors import sample_colorscale, unlabel_rgb

from src.config import END_COLOR, MAP_SCALE_DARK, MAP_SCALE_LIGHT, START_COLOR

MIN_HEIGHT_M = 3  # lowest value still shows as a visible stub
MAX_HEIGHT_M = 25  # highest value; tall enough to compare, short enough to stay in view
# Readings are only ~0.5 m apart, so thin columns form a "curtain" along the
# route whose changing height is easy to follow.
COLUMN_RADIUS_M = 0.8


def _scale(dark: bool) -> list[str]:
    return MAP_SCALE_DARK if dark else MAP_SCALE_LIGHT


def _normalise(values: pd.Series) -> pd.Series:
    """Rescale to 0–1; a constant column maps to the middle."""
    span = values.max() - values.min()
    if span == 0 or pd.isna(span):
        return pd.Series(0.5, index=values.index)
    return (values - values.min()) / span


def _hex_to_rgba(hex_color: str, alpha: int = 255) -> list[int]:
    hex_color = hex_color.lstrip("#")
    return [int(hex_color[i : i + 2], 16) for i in (0, 2, 4)] + [alpha]


def column_data(df: pd.DataFrame, parameter: str, dark: bool = False) -> pd.DataFrame:
    """One row per reading with the position, height, colour and tooltip text deck.gl needs."""
    t = _normalise(df[parameter])
    colours = sample_colorscale(_scale(dark), t.tolist())
    return pd.DataFrame(
        {
            "lon": df["Longitude"],
            "lat": df["Latitude"],
            "height": MIN_HEIGHT_M + t * (MAX_HEIGHT_M - MIN_HEIGHT_M),
            "color": [[int(c) for c in unlabel_rgb(rgb)] + [255] for rgb in colours],
            # Pre-formatted strings for the hover tooltip.
            "time": df["Timestamp"].dt.strftime("%H:%M:%S"),
            "value": df[parameter].map(lambda v: f"{v:,.2f}"),
            "depth": df["Water Depth (m)"].map(lambda v: f"{v:.2f}"),
        }
    )


def track_3d_map(df: pd.DataFrame, parameter: str, dark: bool = False) -> pdk.Deck:
    """Tilted 3D street map with one column per reading."""
    columns = column_data(df, parameter, dark)
    ink, paper = ("#FFFFFF", "#0E1621") if dark else ("#000000", "#FFFFFF")

    # Start/End labels float above the tallest column on a solid background,
    # so they stay readable over any part of the map.
    label_z = MAX_HEIGHT_M + 6
    labels = pd.DataFrame(
        [
            {"text": "Start", "position": [df["Longitude"].iloc[0], df["Latitude"].iloc[0], label_z],
             "border": _hex_to_rgba(START_COLOR), "anchor": "end"},
            {"text": "End", "position": [df["Longitude"].iloc[-1], df["Latitude"].iloc[-1], label_z],
             "border": _hex_to_rgba(END_COLOR), "anchor": "start"},
        ]
    )

    layers = [
        pdk.Layer(
            "ColumnLayer",
            data=columns,
            id="readings",
            get_position=["lon", "lat"],
            get_elevation="height",
            elevation_scale=1,
            radius=COLUMN_RADIUS_M,
            get_fill_color="color",
            extruded=True,
            # More ambient light than deck.gl's default, so the sides of the
            # columns show their true colour instead of a darkened one.
            material={"ambient": 0.7, "diffuse": 0.4, "shininess": 16, "specularColor": [40, 40, 40]},
            pickable=True,
            auto_highlight=True,
        ),
        pdk.Layer(
            "TextLayer",
            data=labels,
            id="start-end-labels",
            get_position="position",
            get_text="text",
            get_size=16,
            get_color=_hex_to_rgba(ink),
            get_text_anchor="anchor",
            get_alignment_baseline="'bottom'",
            background=True,
            get_background_color=_hex_to_rgba(paper, 235),
            get_border_color="border",
            get_border_width=3,
            background_padding=[6, 3],
            font_weight=700,
        ),
    ]

    # Centre on the middle of the route's bounding box (the mean is pulled
    # towards wherever the vehicle lingered).
    view = pdk.ViewState(
        latitude=(df["Latitude"].min() + df["Latitude"].max()) / 2,
        longitude=(df["Longitude"].min() + df["Longitude"].max()) / 2,
        zoom=17.7,
        pitch=50,  # tilt so the column heights are visible
        bearing=60,  # look across the figure-eight loops rather than along them
    )
    tooltip = {
        "html": (
            "<b>{time}</b><br/>"
            f"{parameter}: <b>{{value}}</b><br/>"
            "Water depth: {depth} m"
        ),
        "style": {"backgroundColor": paper, "color": ink, "fontSize": "14px"},
    }
    return pdk.Deck(
        layers=layers,
        initial_view_state=view,
        map_style=pdk.map_styles.CARTO_DARK if dark else pdk.map_styles.CARTO_LIGHT,
        tooltip=tooltip,
    )


def legend_html(df: pd.DataFrame, parameter: str, dark: bool = False) -> str:
    """A colour-bar legend with text labels for the 3D map."""
    gradient = ", ".join(_scale(dark))
    low, high = df[parameter].min(), df[parameter].max()
    return f"""
    <div role="img" aria-label="Legend: column height and colour show {parameter}, from {low:,.2f}
         for the shortest columns to {high:,.2f} for the tallest.">
      <div style="font-weight:600; margin-bottom:4px;">{parameter}: column height and colour</div>
      <div style="display:flex; align-items:center; gap:10px; max-width:520px;">
        <span>Low<br><b>{low:,.2f}</b></span>
        <div style="flex:1; height:16px; border-radius:4px; border:1px solid currentColor;
                    background:linear-gradient(to right, {gradient});"></div>
        <span style="text-align:right;">High<br><b>{high:,.2f}</b></span>
      </div>
    </div>
    """
