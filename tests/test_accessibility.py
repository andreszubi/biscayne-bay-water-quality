"""Accessibility checks (WCAG 2.1 AA) for both the light and dark themes."""
import tomllib

import pytest
from plotly.colors import sample_colorscale

from src import charts
from src.colors import NON_TEXT_CONTRAST, TEXT_CONTRAST, contrast_ratio, readable_text_on
from src.config import (
    ACCENT_COLOR,
    CONTEXT_COLOR,
    CORE_PARAMETERS,
    DARK_BACKGROUND,
    DATA_PATH,
    DEPTH_COLORS,
    DEPTH_LABELS,
    DEPTH_PATTERNS,
    DEPTH_SYMBOLS,
    DIVERGING_SCALE,
    END_COLOR,
    FIT_LINE_COLOR,
    LIGHT_BACKGROUND,
    ROOT_DIR,
    START_COLOR,
    TAG_BACKGROUND,
    TAG_TEXT,
)
from src.data_loader import load_data

THEME_FILE = ROOT_DIR / ".streamlit" / "config.toml"
MODES = ["light", "dark"]
CHART_MARK_COLORS = [*DEPTH_COLORS.values(), ACCENT_COLOR, CONTEXT_COLOR, FIT_LINE_COLOR, START_COLOR, END_COLOR]


@pytest.fixture(scope="module")
def theme():
    with open(THEME_FILE, "rb") as f:
        return tomllib.load(f)["theme"]


@pytest.fixture(scope="module")
def df():
    return load_data(DATA_PATH)


def test_contrast_helper_matches_known_values():
    assert contrast_ratio("#000000", "#FFFFFF") == pytest.approx(21)
    assert contrast_ratio("#777777", "#FFFFFF") == pytest.approx(4.48, abs=0.01)


def test_both_themes_are_defined(theme):
    for mode in MODES:
        assert "backgroundColor" in theme[mode]
    # Chart colours are checked against these, so they must match the theme file.
    assert theme["light"]["backgroundColor"].upper() == LIGHT_BACKGROUND
    assert theme["dark"]["backgroundColor"].upper() == DARK_BACKGROUND


@pytest.mark.parametrize("mode", MODES)
def test_text_is_readable(theme, mode):
    t = theme[mode]
    assert contrast_ratio(t["textColor"], t["backgroundColor"]) >= TEXT_CONTRAST
    assert contrast_ratio(t["textColor"], t["secondaryBackgroundColor"]) >= TEXT_CONTRAST
    assert contrast_ratio(t["linkColor"], t["backgroundColor"]) >= TEXT_CONTRAST


@pytest.mark.parametrize("mode", MODES)
def test_controls_are_visible(theme, mode):
    t = theme[mode]
    # Slider tracks, checkboxes and focus rings use the primary colour.
    assert contrast_ratio(t["primaryColor"], t["backgroundColor"]) >= NON_TEXT_CONTRAST
    assert contrast_ratio(t["primaryColor"], t["secondaryBackgroundColor"]) >= NON_TEXT_CONTRAST
    assert contrast_ratio(t["borderColor"], t["backgroundColor"]) >= NON_TEXT_CONTRAST


def test_selected_tags_are_readable():
    # Applied with CSS in app.py, identically in both themes.
    assert contrast_ratio(TAG_TEXT, TAG_BACKGROUND) >= TEXT_CONTRAST


def test_widget_borders_and_link_underlines_are_on(theme):
    assert theme["showWidgetBorder"] is True
    assert theme["linkUnderline"] is True


@pytest.mark.parametrize("background", [LIGHT_BACKGROUND, DARK_BACKGROUND])
@pytest.mark.parametrize("color", CHART_MARK_COLORS)
def test_chart_marks_stand_out_in_both_themes(color, background):
    assert contrast_ratio(color, background) >= NON_TEXT_CONTRAST


def test_depth_zones_are_not_identified_by_colour_alone():
    assert len(set(DEPTH_SYMBOLS[z] for z in DEPTH_LABELS)) == len(DEPTH_LABELS)
    assert len(set(DEPTH_PATTERNS[z] for z in DEPTH_LABELS)) == len(DEPTH_LABELS)


def test_bar_value_labels_are_readable(df):
    fig = charts.zone_comparison(df, "pH")
    for trace in fig.data:
        assert contrast_ratio(trace.textfont.color, trace.marker.color) >= TEXT_CONTRAST


def test_heatmap_cell_labels_are_readable(df):
    fig = charts.correlation_heatmap(df, list(CORE_PARAMETERS))
    assert fig.layout.annotations, "every cell should carry a printed value"
    for note in fig.layout.annotations:
        fill = sample_colorscale(DIVERGING_SCALE, (float(note.text) + 1) / 2)[0]
        assert contrast_ratio(note.font.color, fill) >= TEXT_CONTRAST


@pytest.mark.parametrize("fill", ["#FFFFFF", "#000000", "#2A78D6", "#E2E1DD", "rgb(28, 92, 171)"])
def test_readable_text_on_any_fill(fill):
    assert contrast_ratio(readable_text_on(fill), fill) >= TEXT_CONTRAST


@pytest.mark.parametrize("dark", [False, True])
def test_map_matches_requested_background(df, dark):
    fig = charts.track_map(df, "Salinity (ppt)", dark=dark)
    assert fig.layout.map.style == ("carto-darkmatter" if dark else "carto-positron")
    labels = [t for t in fig.data if t.mode == "markers+text"]
    assert [t.text[0] for t in labels] == ["Start", "End"]
