"""Tests for the auto-generated insight text."""
import pytest

from src.config import CORE_PARAMETERS, DATA_PATH
from src.data_loader import load_data
from src.insights import generate_insights, strongest_correlation


@pytest.fixture(scope="module")
def df():
    return load_data(DATA_PATH)


def test_insights_are_generated(df):
    insights = generate_insights(df)
    assert len(insights) >= 5
    assert all(isinstance(text, str) and text for text in insights)


def test_empty_data_gives_no_insights(df):
    assert generate_insights(df.iloc[0:0]) == []


def test_strongest_correlation_skips_redundant_pairs(df):
    a, b, r = strongest_correlation(df, list(CORE_PARAMETERS))
    assert {a, b} != {"Salinity (ppt)", "Specific Conductance (mS/cm)"}
    assert {a, b} != {"Dissolved Oxygen (mg/L)", "DO Saturation (%)"}
    assert -1 <= r <= 1
