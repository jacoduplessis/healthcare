# IES Data Explorer

A web application for exploring South Africa's Income and Expenditure Survey (IES) microdata, published by Statistics South Africa. Currently includes the **IES 2022/23** and **IES 2010/11** datasets.

## Overview

This project imports IES microdata into SQLite databases and provides a Flask-based web interface for querying and visualising the data. It includes pre-built example queries covering income inequality, household spending, asset ownership, and health expenditure. A toggle in the header lets you switch between survey years.

A separate statistical analysis uses nearest-neighbour matching to estimate the causal effect of medical scheme membership on out-of-pocket healthcare spending (2022/23 data).

## Project Structure

```
.
├── IES2023.zip              # Source CSV data – IES 2022/23 (5 files)
├── IES2023Metadata.pdf      # Stats SA survey documentation (2022/23)
├── IES2011.zip              # Source CSV data – IES 2010/11 (4 files)
├── IES2011 metadata.pdf     # Stats SA survey documentation (2010/11)
├── import_data.py           # Builds ies2023.db from CSVs
├── import_data_2011.py      # Builds ies2011.db from CSVs
├── Dockerfile               # Multi-stage build (both DBs + webapp)
├── data.md / data.html      # Database structure & data overview
├── findings.md / findings.html  # Exploratory analysis findings
├── report.md / report.typ / report.pdf  # NNM analysis paper
├── study.md                 # Analysis brief
└── webapp/
    ├── app.py               # Flask application (multi-dataset)
    ├── main.py              # Dev entry point
    ├── templates/
    │   └── index.html       # Single-page UI (Bootstrap + Vega-Lite)
    ├── analysis.py          # Nearest-neighbour matching analysis
    ├── pyproject.toml       # Python dependencies (managed by uv)
    └── uv.lock
```

## Databases

Both databases share the same schema: 5 data tables, 3 lookup tables, and 2 views.

| Table | Description | IES 2022/23 | IES 2010/11 |
|-------|-------------|-------------|-------------|
| `geography` | Province, settlement type per household | 19,940 | 25,328 |
| `households` | Demographics, income, expenditure, assets | 19,940 | 25,328 |
| `persons` | Individual-level demographics | 70,339 | 95,042 |
| `person_income` | Individual income sources | 48,038 | 55,800 |
| `total` | Line-item expenditure/income (COICOP-coded) | 1,128,279 | 1,298,446 |
| `coicop_lookup` | COICOP division/group labels | 121 | 121 |
| `province_lookup` | Province code → name | 9 | 9 |
| `settlement_lookup` | Settlement type code → name | 4 | 4 |

Views: `household_geo` (households with province/settlement labels), `total_labelled` (expenditure with COICOP labels).

Column names differ between survey years (reflecting the different questionnaire instruments) but the table structure, lookup tables, views, and indexes are consistent across both.

## Getting Started

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Python 3.14+

### Build the Databases

```bash
# IES 2022/23
unzip IES2023.zip -d csv_temp
python import_data.py
rm -rf csv_temp

# IES 2010/11
unzip IES2011.zip -d csv_temp
python import_data_2011.py
rm -rf csv_temp
```

Both import scripts accept `CSV_DIR` and `DB_PATH` environment variables to override defaults.

### Run the Web App

```bash
cd webapp
uv sync
uv run python main.py
```

Open http://localhost:5001. Use the dataset toggle in the header to switch between IES 2022/23 and IES 2010/11. The app provides a SQL query editor, schema browser, clickable example queries, and automatic Vega-Lite chart rendering.

## Docker

The Dockerfile uses a multi-stage build: stage 1 extracts both zip files and builds both SQLite databases, stage 2 runs the Flask app with gunicorn.

```bash
docker build -t ies-explorer .
docker run -p 8000:8000 ies-explorer
```

## CI/CD

GitHub Actions (`.github/workflows/docker.yml`) builds and pushes the Docker image to GitHub Container Registry on pushes to `main`.

## Web App Features

- Dataset toggle to switch between IES 2022/23 and IES 2010/11
- SQL query editor with syntax validation (read-only, SELECT queries only)
- Schema browser showing all tables and columns for the active dataset
- Pre-built example queries tailored to each dataset
- Automatic Vega-Lite chart generation (bar, line, scatter, area, pie)
- Results displayed in a sortable table
- Bootstrap 5 responsive UI

## Analysis

`webapp/analysis.py` implements a nearest-neighbour matching estimator (Mahalanobis distance) to compare out-of-pocket healthcare spending between medical scheme members and non-members, controlling for income, household size, age, sex, and settlement type. Results are in `report.pdf`.

## Data Source

Statistics South Africa, Income and Expenditure of Households (Report P0100). The microdata is Crown copyright and subject to Stats SA's terms of use.
