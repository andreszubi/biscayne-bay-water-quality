"""End-to-end smoke tests that run the Streamlit script headlessly."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = 60


def test_app_runs_without_errors():
    at = AppTest.from_file(APP_PATH, default_timeout=TIMEOUT).run()
    assert not at.exception
    assert len(at.tabs) == 5


def test_optical_toggle_and_depth_filter_work():
    at = AppTest.from_file(APP_PATH, default_timeout=TIMEOUT).run()
    at.sidebar.checkbox[0].check().run()
    at.sidebar.multiselect[0].set_value(["Deep (> 3.5 m)"]).run()
    assert not at.exception


def test_empty_selection_shows_warning():
    at = AppTest.from_file(APP_PATH, default_timeout=TIMEOUT).run()
    at.sidebar.multiselect[0].set_value([]).run()
    assert not at.exception
    assert at.warning
