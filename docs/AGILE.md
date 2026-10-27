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
4. Any chart has a title, labelled axes and a legend.
5. Text explains to the user what they are looking at.
6. The change is committed to Git with a descriptive message that names the sprint.

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
| US-16 | As a user, I want to upload my own water quality CSV and explore it the same way. | Could | 5 | – | 📋 Backlog (Project 2) |
| US-17 | As a user, I want to ask questions about the data in natural language (AI assistant). | Won't (this release) | 8 | – | 📋 Backlog (Project 2) |
| US-18 | As a researcher, I want to compare multiple survey days side by side. | Won't (this release) | 5 | – | 📋 Backlog |

**Total delivered:** 43 story points across 3 sprints.

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

## Burndown summary

| | Sprint 1 | Sprint 2 | Sprint 3 |
|---|---|---|---|
| Points committed | 10 | 14 | 19 |
| Points completed | 10 | 14 | 19 |
| Points remaining in release | 33 | 19 | 0 |

## Kanban board (end of release)

| 📋 Backlog | 🔄 In progress | ✅ Done |
|---|---|---|
| US-16 Upload own CSV | – | US-01 … US-15 |
| US-17 AI assistant | | |
| US-18 Multi-day comparison | | |

## Next release (Project 2)

The remaining backlog items set up the AI-integrated dashboard in Project 2: CSV upload (US-16) and
a natural-language assistant (US-17), building on the modular `src/` package and the existing tests.
