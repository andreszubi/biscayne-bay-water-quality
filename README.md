# 🌊 Biscayne Bay Water Quality Explorer

An interactive **Streamlit** web app for exploring water quality data collected by an autonomous
vehicle in northern Biscayne Bay, Miami, FL.

- **Live app:** _add your Streamlit Community Cloud URL here_
- **Repository:** https://github.com/andreszubi/biscayne-bay-water-quality
- **Course:** CIS 3590 – Internship-Ready Software Development
- **Author:** Andres Zubizarreta

---

## Purpose

Biscayne Bay is a shallow, subtropical lagoon whose seagrass, fisheries and coral habitat depend on
good water quality. Raw sensor files are hard to read — this one has 69 columns with names like
`ODOsat %` and `BGA-PC cells/mL`. The app turns that file into something anyone can explore:

- **See trends** in temperature, salinity, oxygen and pH over the course of the survey.
- **Compare parameters** to find relationships (for example, salinity vs. pH).
- **Locate readings** on a map of the vehicle's route.
- **Read plain-language insights** that update automatically as you filter the data.

## Dataset

| | |
|---|---|
| **File** | `data/biscayneBay_waterquality.csv` (CIS 3590 course dataset) |
| **Collected** | February 4, 2022, 16:18–16:34 local time |
| **Location** | Northern Biscayne Bay, Miami, FL (≈ 25.912° N, 80.137° W) |
| **Rows** | 942 readings, about one per second |
| **Source** | Autonomous vehicle with GPS, sonar and a multi-parameter water quality sonde |

The app keeps the 14 most useful of the 69 raw columns and renames them with plain names and units:

| Parameter | Unit | Meaning |
|---|---|---|
| Temperature | °C | Water temperature |
| Salinity | ppt | Dissolved salt content (open ocean ≈ 35 ppt) |
| Specific Conductance | mS/cm | Electrical conductivity, rises with salinity |
| pH | – | Acidity/alkalinity (healthy seawater ≈ 7.8–8.3) |
| Dissolved Oxygen | mg/L | Oxygen available to marine life (< 4 mg/L is stressful) |
| DO Saturation | % | Oxygen relative to the maximum the water can hold |
| Water Depth | m | Surface to bay floor, from the vehicle's sonar |
| Turbidity, Chlorophyll, Blue-Green Algae | NTU, µg/L, cells/mL | Optical sensors (see note below) |

Each reading is also assigned a **depth zone** (Shallow < 2.5 m, Moderate 2.5–3.5 m, Deep > 3.5 m),
which the charts use as their legend.

> **Data quality note:** the optical sensors (turbidity, chlorophyll, blue-green algae) report mostly
> negative values, which is physically impossible and points to a missing calibration offset. They
> are hidden by default and can be turned on from the sidebar for relative comparisons only.

## Features

| Section | What you can do |
|---|---|
| **📋 Overview** | Project summary, key metrics, how-to-use guide and a glossary of parameters |
| **🗂️ Data** | Pick columns, browse the filtered table, see summary statistics, download a CSV |
| **📈 Visualizations** | Time series with adjustable rolling average, scatter plot with trend line and correlation, histogram + box plot by depth zone |
| **🗺️ Map** | Vehicle track on a street map, coloured by any parameter, with start/end markers |
| **💡 Insights** | Auto-generated findings, correlation heatmap and depth-zone comparison chart |

**Interactive widgets:** time-window slider, waypoint range slider, depth-zone multiselect,
optical-sensor checkbox, parameter dropdowns, rolling-window slider, column picker and a download
button. All Plotly charts have a title, labelled axes and a legend, and support hover, zoom and pan.

## User instructions

1. Open the live app (link above), or run it locally (see below).
2. Use the **Filters** in the left sidebar to narrow the data by time, mission waypoints and depth
   zone. Every section updates immediately.
3. Click the tabs at the top to move between **Overview**, **Data**, **Visualizations**, **Map** and
   **Insights**.
4. In each chart, use the dropdowns to choose parameters. Hover for exact values, drag to zoom,
   and double-click to reset the view.
5. On the **Data** tab, choose columns and click **Download filtered data (CSV)** to save them.

## Run locally

Requires Python 3.10 or newer.

```bash
git clone https://github.com/andreszubi/biscayne-bay-water-quality.git
cd biscayne-bay-water-quality
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at <http://localhost:8501>.

### Run the tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

The tests check data loading and filtering, that every chart has a title, axis labels and a
legend, the generated insights, and that the full app runs without errors.

## Deploy to Streamlit Community Cloud

1. Push this repository to GitHub (public).
2. Go to <https://share.streamlit.io>, click **Create app**, and choose this repository.
3. Set **Branch** to `main` and **Main file path** to `app.py`, then click **Deploy**.
4. Paste the resulting `*.streamlit.app` URL into the **Live app** line at the top of this README.

## Project structure

```
├── app.py                  # Streamlit entry point: layout, sidebar and sections
├── src/
│   ├── config.py           # Paths, column names, parameter descriptions, thresholds
│   ├── data_loader.py      # Load, clean and filter the CSV; distance/duration helpers
│   ├── charts.py           # Plotly figure builders (one function per chart)
│   └── insights.py         # Plain-language findings generated from the data
├── tests/                  # pytest unit tests and headless app tests
├── data/biscayneBay_waterquality.csv
├── docs/AGILE.md           # Product backlog, sprints, reviews and retrospectives
├── .github/workflows/ci.yml  # Runs the tests on every push and pull request
├── .streamlit/config.toml  # Theme
├── requirements.txt        # Runtime dependencies
└── requirements-dev.txt    # Adds pytest for development
```

The code is split by responsibility: `data_loader`, `charts` and `insights` contain no Streamlit
calls, so they can be tested on their own, and `app.py` only arranges them on the page.

## Agile process

This project was managed with a lightweight **Scrum** process: a prioritized product backlog of user
stories, three short sprints, a Definition of Done, and a review and retrospective after each sprint.
Commits are labelled by sprint, and continuous integration runs the test suite on every push. See
[`docs/AGILE.md`](docs/AGILE.md) for the full backlog, sprint plans and retrospectives.

## Tech stack

Python · Streamlit · Plotly · pandas · NumPy · pytest · GitHub Actions · Streamlit Community Cloud
