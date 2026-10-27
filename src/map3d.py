"""3D map of the survey built with pydeck (deck.gl), which ships with Streamlit.

Each reading is drawn as a column standing on a tilted street map. A column's
height AND colour both show the selected parameter, so the value is never
carried by colour alone. deck.gl has no built-in legend, so `legend_html`
returns one to place next to the map.
"""
import pandas as pd
import pydeck as pdk
from src.colors import shade_bands
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
    """One row per reading with the position, height, colour and tooltip text deck.gl needs.

    Height follows the value smoothly; colour shows which equal-count band
    (shade) the value falls in.
    """
    t = _normalise(df[parameter])
    bands, _, shades = shade_bands(df[parameter], _scale(dark))
    return pd.DataFrame(
        {
            "lon": df["Longitude"],
            "lat": df["Latitude"],
            "height": MIN_HEIGHT_M + t * (MAX_HEIGHT_M - MIN_HEIGHT_M),
            "color": [_hex_to_rgba(shades[b]) for b in bands],
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
    """A legend for the 3D map: one swatch per shade with its value range as text."""
    _, edges, shades = shade_bands(df[parameter], _scale(dark))
    items = "".join(
        f"""<span style="display:inline-flex; align-items:center; gap:6px; margin:0 14px 6px 0;">
              <span aria-hidden="true" style="width:22px; height:16px; border-radius:3px;
                    border:1px solid currentColor; background:{shade};"></span>
              {low:,.2f} – {high:,.2f}
            </span>"""
        for shade, low, high in zip(shades, edges[:-1], edges[1:])
    )
    return f"""
    <div>
      <div style="font-weight:600; margin-bottom:6px;">
        {parameter}: shortest, darkest columns are lowest; tallest, brightest are highest.
        Each shade covers about the same number of readings.
      </div>
      <div style="display:flex; flex-wrap:wrap;">{items}</div>
    </div>
    """
