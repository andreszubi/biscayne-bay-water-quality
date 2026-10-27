"""Static configuration: file paths, column mappings and parameter metadata.

Keeping these values in one place means the rest of the app never has to
know the raw (and messy) column names that come out of the sensors.
"""
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT_DIR / "data" / "biscayneBay_waterquality.csv"

# Raw sensor columns that hold the date and time of each sonde reading.
RAW_DATE_COL = "Date m/d/y"
RAW_TIME_COL = "Time hh:mm:ss"

# Raw CSV column -> friendly name (with units) used everywhere in the app.
COLUMN_MAP = {
    "Latitude": "Latitude",
    "Longitude": "Longitude",
    "Current Step": "Waypoint",
    "Vehicle Speed (kn)": "Vehicle Speed (kn)",
    "Total Water Column (m)": "Water Depth (m)",
    "Temp C": "Temperature (°C)",
    "Sal ppt": "Salinity (ppt)",
    "SpCond mS/cm": "Specific Conductance (mS/cm)",
    "pH": "pH",
    "ODO mg/L": "Dissolved Oxygen (mg/L)",
    "ODOsat %": "DO Saturation (%)",
    "Turbid+ NTU": "Turbidity (NTU)",
    "Chl ug/L": "Chlorophyll (µg/L)",
    "BGA-PC cells/mL": "Blue-Green Algae (cells/mL)",
}

# Water-quality parameters the user can explore, with a plain-language description.
CORE_PARAMETERS = {
    "Temperature (°C)": "Water temperature. Controls how much oxygen water can hold and how fast organisms grow.",
    "Salinity (ppt)": "Dissolved salt content in parts per thousand. Open ocean water is about 35 ppt.",
    "Specific Conductance (mS/cm)": "How well the water conducts electricity, corrected to 25 °C. Rises with salinity.",
    "pH": "Acidity/alkalinity on a 0–14 scale. Healthy seawater is usually between 7.8 and 8.3.",
    "Dissolved Oxygen (mg/L)": "Oxygen available to fish and seagrass. Below 4 mg/L marine life becomes stressed.",
    "DO Saturation (%)": "Dissolved oxygen as a percentage of the maximum the water can hold at its temperature.",
    "Water Depth (m)": "Total water column from the surface to the bay floor, measured by the vehicle's sonar.",
}

# Optical sensors in this file report mostly negative values, which means they
# were not calibrated (a zero offset). They are hidden unless the user opts in.
OPTICAL_PARAMETERS = {
    "Turbidity (NTU)": "Water cloudiness caused by suspended particles. (Uncalibrated: values are offset below zero.)",
    "Chlorophyll (µg/L)": "Proxy for phytoplankton biomass. (Uncalibrated: values are offset below zero.)",
    "Blue-Green Algae (cells/mL)": "Phycocyanin-based cyanobacteria estimate. (Uncalibrated: values are offset below zero.)",
}

ALL_PARAMETERS = {**CORE_PARAMETERS, **OPTICAL_PARAMETERS}

# Depth zones give charts a categorical legend that is meaningful to the user.
DEPTH_ZONE_COL = "Depth Zone"
DEPTH_BINS = [0, 2.5, 3.5, float("inf")]
DEPTH_LABELS = ["Shallow (< 2.5 m)", "Moderate (2.5–3.5 m)", "Deep (> 3.5 m)"]

# ---------------------------------------------------------------------------
# Accessible colours (WCAG 2.1 AA)
# ---------------------------------------------------------------------------
# Chart colours are fixed in Python, but viewers can switch between the light
# and dark themes in the browser, so every mark colour must reach 3:1 contrast
# against BOTH page backgrounds (WCAG 1.4.11). The three depth-zone colours
# also stay distinguishable for colour-blind viewers, and every chart pairs
# colour with a second cue (marker shape, fill pattern or a text label).
LIGHT_BACKGROUND = "#FFFFFF"
DARK_BACKGROUND = "#0E1621"

DEPTH_COLORS = dict(zip(DEPTH_LABELS, ["#2A78D6", "#D95926", "#199E70"]))
DEPTH_SYMBOLS = dict(zip(DEPTH_LABELS, ["circle", "diamond", "square"]))
DEPTH_PATTERNS = dict(zip(DEPTH_LABELS, ["", "/", "x"]))

ACCENT_COLOR = "#2A78D6"  # main data line
CONTEXT_COLOR = "#7F8C9A"  # raw readings, error bars and other secondary marks
FIT_LINE_COLOR = "#7A6BE0"  # trend line (also dashed, so it is not colour-only)
START_COLOR = "#008300"
END_COLOR = "#D63C3B"

# Map colour scales: the Viridis steps that keep at least 3:1 contrast on a
# light basemap (dark purple -> teal) and on a dark one (blue -> yellow).
_VIRIDIS = ["#440154", "#482878", "#3E4989", "#31688E", "#26828E",
            "#1F9E89", "#35B779", "#6ECE58", "#B5DE2B", "#FDE725"]
MAP_SCALE_LIGHT = _VIRIDIS[:6]
MAP_SCALE_DARK = _VIRIDIS[3:]

# Selected-option tags in multiselects. Streamlit draws them in the theme's
# primary colour with white text, which is too light in the dark theme, so the
# app gives them this darker blue (white text reaches 6.4:1) in both themes.
TAG_BACKGROUND = "#1F5FA8"
TAG_TEXT = "#FFFFFF"

# Diverging blue <-> red scale with a neutral grey midpoint for correlations.
DIVERGING_SCALE = [[0.0, "#1C5CAB"], [0.5, "#E2E1DD"], [1.0, "#C23333"]]

# Reference thresholds used by the Insights section.
DO_STRESS_MG_L = 4.0
OCEAN_SALINITY_PPT = 35.0
HEALTHY_PH_RANGE = (7.8, 8.3)
