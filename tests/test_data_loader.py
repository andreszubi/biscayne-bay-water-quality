"""Unit tests for the data layer (run with: python -m pytest)."""
import pandas as pd
import pytest

from src.config import ALL_PARAMETERS, DATA_PATH, DEPTH_LABELS
from src.data_loader import filter_data, load_data, survey_duration_min, track_distance_m


@pytest.fixture(scope="module")
def df():
    return load_data(DATA_PATH)


def test_load_returns_expected_columns(df):
    for col in ["Timestamp", "Latitude", "Longitude", "Waypoint", "Depth Zone", *ALL_PARAMETERS]:
        assert col in df.columns


def test_timestamps_parsed_and_sorted(df):
    assert pd.api.types.is_datetime64_any_dtype(df["Timestamp"])
    assert df["Timestamp"].is_monotonic_increasing
    assert df["Timestamp"].notna().all()


def test_every_row_has_a_depth_zone(df):
    assert df["Depth Zone"].notna().all()


def test_filter_narrows_rows(df):
    start, end = df["Timestamp"].min(), df["Timestamp"].max()
    full = filter_data(df, (start, end), (df["Waypoint"].min(), df["Waypoint"].max()), DEPTH_LABELS)
    assert len(full) == len(df)

    partial = filter_data(df, (start, end), (0, 5), DEPTH_LABELS[:1])
    assert 0 < len(partial) < len(df)
    assert partial["Waypoint"].between(0, 5).all()
    assert (partial["Depth Zone"] == DEPTH_LABELS[0]).all()


def test_track_metrics_are_sensible(df):
    # The survey covers a few hundred metres over roughly a quarter hour.
    assert 100 < track_distance_m(df) < 5_000
    assert 5 < survey_duration_min(df) < 60
    assert track_distance_m(df.head(1)) == 0.0
