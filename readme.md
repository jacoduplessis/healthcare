# IES 2022/23 Data Explorer

A web application for exploring South Africa's Income and Expenditure Survey (IES) 2022/23 data, published by Statistics South Africa.

## Overview

This project imports the IES 2022/23 microdata into a SQLite database and provides a Flask-based web interface for querying and visualising the data. It includes pre-built example queries covering income inequality, household spending, food security, asset ownership, and health expenditure.

A separate statistical analysis uses nearest-neighbour matching to estimate the causal effect of medical scheme membership on out-of-pocket healthcare spending.

## Project Structure

```
.
├── IES2023.zip              # Source CSV data (5 files)
├── IES2023Metadata.pdf      # Stats SA survey documentation
├── import_data.py           # Builds SQLite DB from CSVs
├── Dockerfile               # Multi-stage build (DB + webapp)
├── data.md / data.html      # Database structure & data overview
├── findings.md / findings.html  # Exploratory analysis findings
├── report.md / report.typ / report.pdf  # NNM analysis paper
├── study.md                 # Analysis brief
└── webapp/
    ├── app.py               # Flask application
    ├── main.py              # Dev entry point
    ├── templates/
    │   └── index.html       # Single-page UI (Bootstrap + Vega-Lite)
    ├── static/              # Static assets
    ├── analysis.py          # Nearest-neighbour matching analysis
    ├── pyproject.toml       # Python dependencies (managed by uv)
    └── uv.lock
```

## Database

The SQLite database contains 5 data tables, 3 lookup tables, and 2 views:

| Table | Description | Rows |
|-------|-------------|------|
| `geography` | Province, metro, settlement type per household | ~23k |
| `households` | Demographics, income, expenditure, assets, food security | ~23k |
| `persons` | Individual-level demographics | ~70k |
| `person_income` | Individual income sources | ~54k |
| `total` | Line-item expenditure/income (COICOP-coded) | ~1.3M |
| `coicop_lookup` | COICOP division/group labels | 121 |
| `province_lookup` | Province code → name | 9 |
| `settlement_lookup` | Settlement type code → name | 4 |

Views: `household_geo` (households joined with geography + labels), `total_labelled` (expenditure with COICOP labels).

## Getting Started

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Python 3.14+

### Build the Database

```bash
unzip IES2023.zip -d csv_temp
python import_data.py
rm -rf csv_temp
```

### Run the Web App

```bash
cd webapp
uv sync
uv run python main.py
```

Open http://localhost:5001. The app provides a SQL query editor, schema browser, clickable example queries, and automatic Vega-Lite chart rendering.

## Docker

The Dockerfile uses a multi-stage build: stage 1 extracts the zip and builds the SQLite database, stage 2 runs the Flask app with gunicorn.

```bash
docker build -t ies-explorer .
docker run -p 8000:8000 ies-explorer
```

## CI/CD

GitHub Actions (`.github/workflows/docker.yml`) builds and pushes the Docker image to GitHub Container Registry on pushes to `main`.

## Web App Features

- SQL query editor with syntax validation (read-only, SELECT queries only)
- Schema browser showing all tables and columns
- 8 pre-built example queries with one-click execution
- Automatic Vega-Lite chart generation (bar, line, scatter, area, pie)
- Results displayed in a sortable table
- Bootstrap 5 responsive UI

## Analysis

`webapp/analysis.py` implements a nearest-neighbour matching estimator (Mahalanobis distance) to compare out-of-pocket healthcare spending between medical scheme members and non-members, controlling for income, household size, age, sex, and settlement type. Results are in `report.pdf`.

## Data Source

Statistics South Africa, Income and Expenditure Survey 2022/23. The microdata is Crown copyright and subject to Stats SA's terms of use.
