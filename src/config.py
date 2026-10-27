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
DEPTH_COLORS = dict(zip(DEPTH_LABELS, ["#7FB8E0", "#2E7EC1", "#0B3C73"]))

# Reference thresholds used by the Insights section.
DO_STRESS_MG_L = 4.0
OCEAN_SALINITY_PPT = 35.0
HEALTHY_PH_RANGE = (7.8, 8.3)

MAP_CENTER = {"lat": 25.9121, "lon": -80.1371}
