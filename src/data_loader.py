"""Loading, cleaning and filtering of the Biscayne Bay water quality data.

These functions are pure pandas (no Streamlit calls) so they can be unit
tested; app.py wraps `load_data` with Streamlit's cache.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import (
    COLUMN_MAP,
    DEPTH_BINS,
    DEPTH_LABELS,
    DEPTH_ZONE_COL,
    RAW_DATE_COL,
    RAW_TIME_COL,
)

EARTH_RADIUS_M = 6_371_000


def load_data(path: Path) -> pd.DataFrame:
    """Read the raw CSV and return a tidy DataFrame with friendly column names."""
    raw = pd.read_csv(path)
    # Some raw headers have trailing spaces (e.g. "Date m/d/y   ").
    raw.columns = raw.columns.str.strip()

    df = raw[list(COLUMN_MAP)].rename(columns=COLUMN_MAP)
    df.insert(
        0,
        "Timestamp",
        pd.to_datetime(
            raw[RAW_DATE_COL].str.strip() + " " + raw[RAW_TIME_COL].str.strip(),
            format="%m/%d/%y %H:%M:%S",
            errors="coerce",
        ),
    )
    df[DEPTH_ZONE_COL] = pd.cut(df["Water Depth (m)"], bins=DEPTH_BINS, labels=DEPTH_LABELS)

    df = df.dropna(subset=["Timestamp", "Latitude", "Longitude"])
    return df.sort_values("Timestamp", kind="stable").reset_index(drop=True)


def filter_data(
    df: pd.DataFrame,
    time_range: tuple,
    waypoint_range: tuple[int, int],
    depth_zones: list[str],
) -> pd.DataFrame:
    """Return only the rows inside the selected time window, waypoints and depth zones."""
    mask = (
        df["Timestamp"].between(*time_range)
        & df["Waypoint"].between(*waypoint_range)
        & df[DEPTH_ZONE_COL].isin(depth_zones)
    )
    return df.loc[mask].reset_index(drop=True)


def track_distance_m(df: pd.DataFrame) -> float:
    """Total distance travelled along the GPS track, using the haversine formula."""
    if len(df) < 2:
        return 0.0
    lat = np.radians(df["Latitude"].to_numpy())
    lon = np.radians(df["Longitude"].to_numpy())
    dlat, dlon = np.diff(lat), np.diff(lon)
    a = np.sin(dlat / 2) ** 2 + np.cos(lat[:-1]) * np.cos(lat[1:]) * np.sin(dlon / 2) ** 2
    return float((2 * EARTH_RADIUS_M * np.arcsin(np.sqrt(a))).sum())


def survey_duration_min(df: pd.DataFrame) -> float:
    """Minutes between the first and last reading."""
    if df.empty:
        return 0.0
    return (df["Timestamp"].max() - df["Timestamp"].min()).total_seconds() / 60
