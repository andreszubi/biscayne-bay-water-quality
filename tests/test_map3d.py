"""Tests for the pydeck 3D map."""
import pytest

from src import charts
from src.colors import shade_bands
from src.config import DATA_PATH, MAP_SCALE_LIGHT
from src.data_loader import load_data
from src.map3d import MAX_HEIGHT_M, MIN_HEIGHT_M, column_data, legend_html, track_3d_map

PARAM = "Water Depth (m)"


@pytest.fixture(scope="module")
def df():
    return load_data(DATA_PATH)


def test_one_column_per_reading(df):
    assert len(column_data(df, PARAM)) == len(df)


def test_height_follows_the_value(df):
    cols = column_data(df, PARAM)
    assert cols["height"].min() == pytest.approx(MIN_HEIGHT_M)
    assert cols["height"].max() == pytest.approx(MAX_HEIGHT_M)
    # The deepest reading gets the tallest column.
    assert cols["height"].idxmax() == df[PARAM].idxmax()


def test_constant_values_do_not_break_scaling(df):
    flat = df.assign(**{PARAM: 2.0})
    assert column_data(flat, PARAM)["height"].nunique() == 1


@pytest.mark.parametrize("dark", [False, True])
def test_deck_has_columns_labels_and_matching_basemap(df, dark):
    deck = track_3d_map(df, PARAM, dark=dark)
    layer_types = [layer.type for layer in deck.layers]
    assert layer_types == ["ColumnLayer", "TextLayer"]
    assert ("dark-matter" in deck.map_style) == dark
    assert deck.initial_view_state.pitch > 0  # tilted, so heights are visible


def test_every_shade_is_used_and_low_values_are_darkest(df):
    cols = column_data(df, PARAM)
    used = {tuple(c) for c in cols["color"]}
    assert len(used) == len(MAP_SCALE_LIGHT)
    shallowest, deepest = df[PARAM].idxmin(), df[PARAM].idxmax()
    darkest = [int(MAP_SCALE_LIGHT[0][i : i + 2], 16) for i in (1, 3, 5)] + [255]
    brightest = [int(MAP_SCALE_LIGHT[-1][i : i + 2], 16) for i in (1, 3, 5)] + [255]
    assert cols.loc[shallowest, "color"] == darkest
    assert cols.loc[deepest, "color"] == brightest


def test_shade_bands_hold_about_equal_counts(df):
    bands, edges, shades = shade_bands(df[PARAM], MAP_SCALE_LIGHT)
    counts = bands.value_counts()
    assert len(shades) == len(edges) - 1 == len(MAP_SCALE_LIGHT)
    assert counts.max() - counts.min() < 0.1 * len(df)


def test_shade_bands_with_few_or_one_distinct_values(df):
    bands, edges, shades = shade_bands(df["pH"], MAP_SCALE_LIGHT)
    assert 1 < len(shades) < len(MAP_SCALE_LIGHT)
    # Still spread from the darkest to the brightest shade.
    assert shades[0] == MAP_SCALE_LIGHT[0] and shades[-1] == MAP_SCALE_LIGHT[-1]

    bands, edges, shades = shade_bands(df[PARAM] * 0 + 2.0, MAP_SCALE_LIGHT)
    assert len(shades) == 1 and (bands == 0).all()


def test_legend_lists_every_band_range_in_text(df):
    html = legend_html(df, PARAM)
    _, edges, _ = shade_bands(df[PARAM], MAP_SCALE_LIGHT)
    for low, high in zip(edges[:-1], edges[1:]):
        assert f"{low:,.2f} – {high:,.2f}" in html


def test_2d_map_uses_the_same_bands(df):
    fig = charts.track_map(df, PARAM)
    _, edges, _ = shade_bands(df[PARAM], MAP_SCALE_LIGHT)
    assert list(fig.layout.coloraxis.colorbar.tickvals) == pytest.approx(edges)
