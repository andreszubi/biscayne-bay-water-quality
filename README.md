# 🌊 Biscayne Bay Water Quality Explorer

An interactive **Streamlit** web app for exploring water quality data collected by an autonomous
vehicle in northern Biscayne Bay, Miami, FL.

- **Live app:** https://biscayne-bay-water-quality-andres-zubizarreta.streamlit.app/
- **Repository:** https://github.com/andreszubi/biscayne-bay-water-quality
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
optical-sensor checkbox, map-background selector, parameter dropdowns, rolling-window slider,
column picker and a download button. All Plotly charts have a title, labelled axes and a legend,
and support hover, zoom and pan.

## Light and dark themes

The app has a custom **light theme** and **dark theme**. It follows the viewer's device setting by
default. To switch, open the **⋮ menu** at the top right of the app and choose **System**,
**Light** or **Dark**. The charts and map are designed to stay readable in both themes. The map
background can also be set separately from the sidebar (**Appearance → Map background**).

## Accessibility

The app is designed to meet **WCAG 2.1 level AA**:

| Guideline | How the app meets it |
|---|---|
| **1.4.3 Text contrast (4.5:1)** | Theme text, link and tag colours were chosen and tested for at least 4.5:1 in both themes. Streamlit's faded caption style (about 4.2:1) is not used, and slider labels and selected-filter tags get small CSS fixes. |
| **1.4.11 Non-text contrast (3:1)** | Every chart colour (lines, points, bars, markers) reaches 3:1 against **both** the light and the dark background. Widget borders are turned on. |
| **1.4.1 Use of colour** | Nothing is shown by colour alone: depth zones use colour **and** marker shape (scatter) or fill pattern (histogram), the trend line is dashed, map markers carry "Start"/"End" text, links are underlined, and correlation values are printed in each heatmap cell. |
| **Colour-blind safety** | The three depth-zone colours were checked with a colour-vision-deficiency simulator: they stay clearly distinct for red-green colour blindness (the most common types). For the rarer blue-yellow type they are closer, which is one reason every chart also uses shapes, patterns or labels. The map uses the colour-blind-safe Viridis scale. |
| **1.1.1 Non-text content** | Every chart is followed by a written **Chart summary** and a **View the data behind this chart** table, so screen-reader users get the same information. |
| **1.3.1 Info and relationships / 2.4.6 Headings** | Headings follow a proper order (page title → section → subsection) with no skipped levels. |
| **2.1.1 Keyboard** | All controls are standard Streamlit widgets that work with the keyboard. |

These rules are enforced by `tests/test_accessibility.py`, which computes the WCAG contrast ratio
of every theme colour pair and chart colour, so a future colour change cannot quietly break them.

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

Requires Python 3.11 or newer.

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
legend, the generated insights, colour contrast in both themes, and that the full app runs
without errors.

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
│   ├── colors.py           # WCAG contrast-ratio helpers
│   └── insights.py         # Plain-language findings generated from the data
├── tests/                  # pytest unit tests and headless app tests
├── data/biscayneBay_waterquality.csv
├── docs/AGILE.md           # Product backlog, sprints, reviews and retrospectives
├── .github/workflows/ci.yml  # Runs the tests on every push and pull request
├── .streamlit/config.toml  # Light and dark themes
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
