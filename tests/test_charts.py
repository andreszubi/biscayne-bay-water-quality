"""Every chart must render with a title, axis labels and a legend (rubric requirement)."""
import pytest

from src import charts
from src.config import CORE_PARAMETERS, DATA_PATH
from src.data_loader import load_data

PARAMS = list(CORE_PARAMETERS)


@pytest.fixture(scope="module")
def df():
    return load_data(DATA_PATH)


@pytest.mark.parametrize(
    "build",
    [
        lambda d: charts.time_series(d, "Temperature (°C)", window=10),
        lambda d: charts.relationship(d, "Temperature (°C)", "Salinity (ppt)"),
        lambda d: charts.distribution(d, "pH"),
        lambda d: charts.zone_comparison(d, "Dissolved Oxygen (mg/L)"),
        lambda d: charts.track_map(d, "Salinity (ppt)"),
    ],
)
def test_chart_has_title_and_legend(df, build):
    fig = build(df)
    assert fig.layout.title.text
    assert fig.layout.showlegend is True
    assert len(fig.data) >= 1


def test_axes_are_labelled(df):
    fig = charts.relationship(df, "Temperature (°C)", "Salinity (ppt)")
    assert fig.layout.xaxis.title.text == "Temperature (°C)"
    assert fig.layout.yaxis.title.text == "Salinity (ppt)"


def test_heatmap_is_square(df):
    fig = charts.correlation_heatmap(df, PARAMS)
    assert fig.data[0].z.shape == (len(PARAMS), len(PARAMS))
