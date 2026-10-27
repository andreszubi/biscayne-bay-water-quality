"""Tests for the pydeck 3D map."""
import pytest

from src.config import DATA_PATH
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


def test_legend_states_the_range_in_text(df):
    html = legend_html(df, PARAM)
    assert f"{df[PARAM].min():,.2f}" in html
    assert f"{df[PARAM].max():,.2f}" in html
    assert "aria-label" in html
