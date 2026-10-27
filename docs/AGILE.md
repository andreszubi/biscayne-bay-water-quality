# Agile Project Management

This project followed a lightweight **Scrum** process adapted for a one-person team. The work was
broken into user stories, prioritized in a product backlog, and delivered in three short sprints.
Each sprint ended with a working, tested increment committed to Git, followed by a review and a
retrospective.

## Roles

| Scrum role | Who |
|---|---|
| Product Owner | Andres Zubizarreta (represents the end users and the course requirements) |
| Scrum Master | Andres Zubizarreta (keeps the process on track, removes blockers) |
| Development Team | Andres Zubizarreta |
| Stakeholder | CIS 3590 instructor (acceptance via the assignment rubric) |

## Product vision

> For students, researchers and community members who care about Biscayne Bay, the **Water Quality
> Explorer** is a web app that turns a raw 69-column sensor file into clear, interactive charts and
> plain-language findings, so anyone can understand bay conditions without writing code.

## User personas

- **Maria, environmental science student** – wants to see how oxygen and salinity change and export
  data for a lab report.
- **Dr. Lee, field researcher** – wants to check where along the route unusual readings occurred
  and whether the sensors behaved correctly.
- **Sam, community member** – has no data background and wants a quick, plain-English summary.

## Definition of Done

A user story is **done** when:

1. The feature works in the running app with no errors or warnings.
2. Code is modular (logic lives in `src/`, layout in `app.py`) and has docstrings/comments.
3. Automated tests for the feature are written and `python -m pytest` passes.
4. Any chart has a title, labelled axes and a legend, plus a text summary and data table.
5. Text and chart colours pass the WCAG 2.1 AA contrast tests in both the light and dark themes.
6. Text explains to the user what they are looking at.
7. The change is committed to Git with a descriptive message that names the sprint.

## Product backlog

Priority uses **MoSCoW** (Must / Should / Could / Won't this release). Estimates are in story points
(1 = trivial, 8 = large).

| ID | User story | Priority | Points | Sprint | Status |
|---|---|---|---|---|---|
| US-01 | As a user, I want the raw CSV cleaned with readable column names and units, so I can understand each value. | Must | 3 | 1 | ✅ Done |
| US-02 | As a user, I want each reading to have a proper timestamp, so I can see how conditions change over time. | Must | 2 | 1 | ✅ Done |
| US-03 | As a researcher, I want to filter by time window, mission waypoint and depth, so I can focus on part of the survey. | Must | 3 | 1 | ✅ Done |
| US-04 | As a user, I want to see the survey distance and duration, so I know how much area was covered. | Should | 2 | 1 | ✅ Done |
| US-05 | As a student, I want a line chart of any parameter over time with smoothing, so I can see trends through sensor noise. | Must | 3 | 2 | ✅ Done |
| US-06 | As a researcher, I want a scatter plot comparing two parameters with a trend line and r value, so I can spot relationships. | Must | 3 | 2 | ✅ Done |
| US-07 | As a student, I want to see the distribution of a parameter by depth zone, so I can find outliers. | Should | 3 | 2 | ✅ Done |
| US-08 | As a researcher, I want a map of the vehicle's track coloured by a parameter, so I can see where readings were taken. | Must | 5 | 2 | ✅ Done |
| US-09 | As a community member, I want plain-language insights that update with my filters, so I can understand the data without analyzing it myself. | Must | 5 | 3 | ✅ Done |
| US-10 | As a researcher, I want a correlation matrix, so I can see all relationships at once. | Should | 2 | 3 | ✅ Done |
| US-11 | As a user, I want the app organized into clear sections with instructions, so I always know where to go. | Must | 3 | 3 | ✅ Done |
| US-12 | As a student, I want to choose columns and download the filtered data as CSV, so I can use it in a report. | Should | 2 | 3 | ✅ Done |
| US-13 | As a researcher, I want uncalibrated optical sensors flagged and hidden by default, so I'm not misled by impossible values. | Should | 2 | 3 | ✅ Done |
| US-14 | As the instructor, I want a README, requirements.txt and a public URL, so I can run and grade the app. | Must | 3 | 3 | ✅ Done (URL added at deployment) |
| US-15 | As a developer, I want tests to run automatically on every push, so regressions are caught early. | Could | 2 | 3 | ✅ Done |
| US-19 | As a user, I want to choose a light or dark theme, so the app is comfortable in any lighting. | Should | 3 | 4 | ✅ Done |
| US-20 | As a user with low vision, I want all text and chart colours to have enough contrast in both themes, so I can read everything. | Must | 5 | 4 | ✅ Done |
| US-21 | As a colour-blind user, I want chart categories marked by shape, pattern or label as well as colour, so I can tell them apart. | Must | 3 | 4 | ✅ Done |
| US-22 | As a screen-reader user, I want a text summary and a data table for every chart, so I get the same information without seeing it. | Must | 3 | 4 | ✅ Done |
| US-23 | As a researcher, I want a 3D map of the survey, so I can see how a parameter such as water depth changes along the route at a glance. | Should | 5 | 5 | ✅ Done |
| US-16 | As a user, I want to upload my own water quality CSV and explore it the same way. | Could | 5 | – | 📋 Backlog (Project 2) |
| US-17 | As a user, I want to ask questions about the data in natural language (AI assistant). | Won't (this release) | 8 | – | 📋 Backlog (Project 2) |
| US-18 | As a researcher, I want to compare multiple survey days side by side. | Won't (this release) | 5 | – | 📋 Backlog |

**Total delivered:** 62 story points across 5 sprints.

## Sprint 1 – Data foundation

**Sprint goal:** Load, clean and filter the dataset reliably, with tests, so every later feature
builds on trustworthy data.

| Story | Tasks |
|---|---|
| US-01 | Inspect the 69 raw columns; choose 14 relevant ones; map to friendly names with units (`src/config.py`) |
| US-02 | Combine the sonde's date and time columns into a `Timestamp`; strip stray spaces in headers |
| US-03 | Write `filter_data()` for time, waypoint and depth zone; add depth-zone categories |
| US-04 | Haversine track distance and survey duration helpers |
| – | Unit tests in `tests/test_data_loader.py` |

**Review:** Data layer delivered and tested (5 tests passing). Velocity: 10 points.

**Retrospective**
- *What went well:* Profiling every column first revealed problems early.
- *What didn't:* The raw file has two different time columns (`Time` is a vehicle clock in mm:ss;
  `Time hh:mm:ss` is the sonde clock). Picking the wrong one would have broken the time axis.
- *Discovery:* Turbidity is negative in 100% of readings and chlorophyll in ~79%, so the optical
  sensors were not calibrated. → Added **US-13** to the backlog.
- *Action item:* Keep all column names and thresholds in `config.py` so they are never hard-coded.

## Sprint 2 – Visualizations

**Sprint goal:** Deliver accurate, fully labelled Plotly charts for trends, relationships,
distributions and location.

| Story | Tasks |
|---|---|
| US-05 | `time_series()` with raw + rolling-average traces |
| US-06 | `relationship()` scatter coloured by depth zone, numpy least-squares fit, r in legend |
| US-07 | `distribution()` overlaid histograms with marginal box plots |
| US-08 | `track_map()` using `scatter_map` (no API token needed) with start/end markers |
| – | Shared `_finish()` helper so every chart has a title, axis labels and legend |
| – | Tests asserting title, legend and axis labels for every chart |

**Review:** All charts built and tested (12 tests passing). Velocity: 14 points.

**Retrospective**
- *What went well:* A shared styling helper made the rubric requirements (title, axis labels,
  legend) automatic instead of something to remember per chart.
- *What didn't:* Single-series charts have no legend by default in Plotly; solved by naming traces
  (raw vs. rolling average, linear fit) and using depth zone as a categorical colour.
- *Action item:* Avoid extra dependencies (the trend line uses numpy instead of statsmodels) to
  keep deployment simple.

## Sprint 3 – Insights, UI and delivery

**Sprint goal:** Assemble a polished, intuitive app with explanatory text and auto-generated
insights, and prepare it for deployment.

| Story | Tasks |
|---|---|
| US-09 | `generate_insights()` – temperature, salinity, oxygen, pH, depth and strongest-correlation findings |
| US-10 | Correlation heatmap |
| US-11 | Five tabs (Overview, Data, Visualizations, Map, Insights), sidebar filters, how-to guide, glossary |
| US-12 | Column multiselect, summary statistics, download button |
| US-13 | Sidebar checkbox to include optical sensors (off by default) plus a data-quality insight |
| US-14 | README, requirements.txt, Streamlit theme, deployment steps |
| US-15 | GitHub Actions workflow running pytest |
| – | Headless `AppTest` smoke tests, including an empty-filter edge case |

**Review:** App complete, 18 tests passing, verified manually in the browser. Velocity: 19 points.

**Retrospective**
- *What went well:* Because the logic was already modular and tested, building the UI was mostly
  arranging existing pieces.
- *What didn't:* A visual review found layout bugs that tests could not catch: chart titles
  overlapping legends, a cramped heatmap, a truncated glossary table, and the map zoomed out too far.
  All were fixed before the sprint closed.
- *Action item:* Include a manual browser check of every tab in the Definition of Done for future
  UI work.

## Sprint 4 – Themes and accessibility

**Sprint goal:** Offer light and dark themes and bring the whole app up to WCAG 2.1 AA, so it is
readable and usable for everyone.

| Story | Tasks |
|---|---|
| US-19 | Custom `[theme.light]` and `[theme.dark]` palettes in `.streamlit/config.toml`; theme switcher in the ⋮ menu; sidebar instructions; map background that follows the theme or can be chosen |
| US-20 | Chart colours chosen to reach 3:1 on both backgrounds; per-cell black/white heatmap labels; replaced faded captions; CSS fixes for multiselect tags and slider labels; `tests/test_accessibility.py` |
| US-21 | Marker shapes in the scatter plot, fill patterns in the histogram, dashed trend line, labelled Start/End map markers; palette checked with a colour-blindness simulator |
| US-22 | `show_chart()` helper adds a written summary and a data-table expander under every chart; fixed heading order |

**Review:** Both themes audited in the browser on all five tabs with an automated contrast scan
(zero text below 4.5:1); 52 tests passing. Velocity: 14 points.

**Retrospective**
- *What went well:* Writing the contrast rules as tests means they are checked on every push, not
  just once.
- *What didn't:* Some problems only appeared in the running app, not in the config: Streamlit's
  caption style, slider min/max labels and multiselect tags all fell below 4.5:1. A browser scan of
  the real page found them.
- *Discovery:* One theme colour cannot serve as both text on a dark background and a background
  behind white text, so the multiselect tags needed their own colour.
- *Action item:* Run the browser contrast scan in both themes as part of the Definition of Done for
  any UI change.

## Sprint 5 – 3D map

**Sprint goal:** Add a 3D view of the survey to the Map tab that is as readable and accessible as
the rest of the app.

| Story | Tasks |
|---|---|
| US-23 | `src/map3d.py`: pydeck ColumnLayer on a tilted Carto basemap, column height and colour both encode the chosen parameter, Start/End text labels, hover tooltip, text legend; alt text, summary and data table; keyboard instructions; colour scales limited to steps that keep 3:1 contrast against the basemap's land and water (also applied to the 2D map); `tests/test_map3d.py` |

**Review:** 3D map delivered and checked in both themes; the browser contrast scan found no text
below 4.5:1 on any tab; 60 tests passing. Velocity: 5 points.

**Retrospective**
- *What went well:* Reusing the theme-aware map background and the summary/table helper made the
  3D map accessible from the start.
- *What didn't:* The first version's columns were too tall and wide: readings are only ~0.5 m
  apart, so they merged into one wall. Thinner, shorter columns form a readable "curtain" instead.
  The map credit text in the 3D map was also unreadable in the dark theme and needed a CSS fix.
- *Discovery:* The light 2D map's colour scale included two green steps below 3:1 contrast; both
  maps now use only the passing steps.
- *User feedback:* The product owner found the 3D map hard to read in the light theme. The cause:
  colours had been checked against the white page, but the columns stand over the basemap's
  grey-blue water, where the highest values (teal) reached only 2.36:1 and also matched the water's
  hue. The light scale was changed to Plasma (navy → magenta, at least 3.67:1 on the water), the
  dark scale dropped two steps that failed on the dark water, the columns were made fully opaque
  with brighter lighting, and the tests now check against the real basemap colours.
- *Action item:* Try new visualizations at the real data density early, before tuning the styling,
  and test colours against what is actually behind them.

## Burndown summary

| | Sprint 1 | Sprint 2 | Sprint 3 | Sprint 4 | Sprint 5 |
|---|---|---|---|---|---|
| Points committed | 10 | 14 | 19 | 14 | 5 |
| Points completed | 10 | 14 | 19 | 14 | 5 |
| Points remaining in release | 52 | 38 | 19 | 5 | 0 |

## Kanban board (end of release)

| 📋 Backlog | 🔄 In progress | ✅ Done |
|---|---|---|
| US-16 Upload own CSV | – | US-01 … US-15, US-19 … US-23 |
| US-17 AI assistant | | |
| US-18 Multi-day comparison | | |

## Next release (Project 2)

The remaining backlog items set up the AI-integrated dashboard in Project 2: CSV upload (US-16) and
a natural-language assistant (US-17), building on the modular `src/` package and the existing tests.
