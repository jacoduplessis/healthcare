"""IES Data Explorer - Flask Web Application.

Supports multiple survey datasets (IES 2022/23, IES 2010/11) with
a toggle to switch between them.
"""
import os
import re

from flask import Flask, jsonify, render_template, request
from sqlalchemy import create_engine, text

app = Flask(__name__)

# --- Database engines keyed by dataset id ---
_app_dir = os.path.dirname(os.path.abspath(__file__))


def _find_db(name: str) -> str | None:
    """Locate a database file, checking the webapp dir first, then parent."""
    for d in (_app_dir, os.path.join(_app_dir, "..")):
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return None


DATASETS: dict[str, dict] = {}

_db2023 = _find_db("ies2023.db")
if _db2023:
    DATASETS["ies2023"] = {
        "label": "IES 2022/23",
        "engine": create_engine(f"sqlite:///{_db2023}", echo=False),
    }

_db2011 = _find_db("ies2011.db")
if _db2011:
    DATASETS["ies2011"] = {
        "label": "IES 2010/11",
        "engine": create_engine(f"sqlite:///{_db2011}", echo=False),
    }

DEFAULT_DATASET = "ies2023" if "ies2023" in DATASETS else next(iter(DATASETS), None)


def _get_engine(dataset: str | None = None):
    ds = dataset or DEFAULT_DATASET
    entry = DATASETS.get(ds)
    if not entry:
        return None, ds
    return entry["engine"], ds


# --- Example queries per dataset ---
EXAMPLE_QUERIES_2023 = [
    {
        "id": "income_by_province",
        "title": "Average Income & Expenditure by Province",
        "description": "Compare average household income and expenditure across South Africa's 9 provinces.",
        "sql": """SELECT p.name AS province,
       ROUND(AVG(CAST(h.income AS REAL)), 0) AS avg_income,
       ROUND(AVG(CAST(h.expenditure AS REAL)), 0) AS avg_expenditure
FROM households h
JOIN geography g ON h.uqno = g.uqno
JOIN province_lookup p ON g.province = p.code
GROUP BY g.province
ORDER BY avg_income DESC""",
        "chart": {
            "mark": "bar",
            "encoding": {
                "y": {"field": "province", "type": "nominal", "sort": "-x", "title": "Province"},
                "x": {"field": "avg_income", "type": "quantitative", "title": "Average Annual Income (R)"},
                "color": {"value": "#4e79a7"},
                "tooltip": [
                    {"field": "province", "type": "nominal"},
                    {"field": "avg_income", "type": "quantitative", "title": "Avg Income", "format": ",.0f"},
                    {"field": "avg_expenditure", "type": "quantitative", "title": "Avg Expenditure", "format": ",.0f"},
                ],
            },
        },
    },
    {
        "id": "spending_categories",
        "title": "What Households Spend On (COICOP Divisions)",
        "description": "Total household expenditure broken down by major spending category.",
        "sql": """SELECT cd.label AS category,
       ROUND(SUM(t.valueannualized_adj), 0) AS total_spend,
       COUNT(*) AS items
FROM total t
JOIN coicop_lookup cd ON t.division = cd.code AND cd.level = 'division'
WHERE CAST(t.division AS INTEGER) <= 13
GROUP BY t.division
ORDER BY total_spend DESC""",
        "chart": {
            "mark": "bar",
            "encoding": {
                "y": {"field": "category", "type": "nominal", "sort": "-x", "title": "Category"},
                "x": {"field": "total_spend", "type": "quantitative", "title": "Total Spend (R)"},
                "color": {"value": "#e15759"},
                "tooltip": [
                    {"field": "category", "type": "nominal"},
                    {"field": "total_spend", "type": "quantitative", "title": "Total Spend", "format": ",.0f"},
                    {"field": "items", "type": "quantitative", "title": "# Items"},
                ],
            },
        },
    },
    {
        "id": "income_by_population",
        "title": "Income by Population Group",
        "description": "Average household income by population group of the head of household.",
        "sql": """SELECT
  CASE head_population
    WHEN '1' THEN 'Black African'
    WHEN '2' THEN 'Coloured'
    WHEN '3' THEN 'Indian/Asian'
    WHEN '4' THEN 'White'
  END AS population_group,
  COUNT(*) AS households,
  ROUND(AVG(CAST(income AS REAL)), 0) AS avg_income,
  ROUND(AVG(CAST(expenditure AS REAL)), 0) AS avg_expenditure
FROM households
WHERE head_population IN ('1','2','3','4')
GROUP BY head_population
ORDER BY avg_income DESC""",
        "chart": {
            "mark": "bar",
            "encoding": {
                "y": {
                    "field": "population_group",
                    "type": "nominal",
                    "sort": "-x",
                    "title": "Population Group",
                },
                "x": {"field": "avg_income", "type": "quantitative", "title": "Average Income (R)"},
                "color": {"field": "population_group", "type": "nominal", "legend": None},
                "tooltip": [
                    {"field": "population_group", "type": "nominal"},
                    {"field": "avg_income", "type": "quantitative", "title": "Avg Income", "format": ",.0f"},
                    {"field": "avg_expenditure", "type": "quantitative", "title": "Avg Expenditure", "format": ",.0f"},
                    {"field": "households", "type": "quantitative", "title": "Households"},
                ],
            },
        },
    },
    {
        "id": "expenditure_deciles",
        "title": "Expenditure by Decile (Inequality)",
        "description": "Average household expenditure across 10 income groups — decile 1 is the poorest 10%, decile 10 is the wealthiest 10%.",
        "sql": """SELECT
  CAST(expenditure_decile AS INTEGER) AS decile,
  COUNT(*) AS households,
  ROUND(AVG(CAST(expenditure AS REAL)), 0) AS avg_expenditure,
  ROUND(AVG(CAST(income AS REAL)), 0) AS avg_income
FROM households
GROUP BY expenditure_decile
ORDER BY CAST(expenditure_decile AS INTEGER)""",
        "chart": {
            "mark": "bar",
            "encoding": {
                "x": {"field": "decile", "type": "ordinal", "title": "Expenditure Decile (1=Poorest, 10=Wealthiest)"},
                "y": {"field": "avg_expenditure", "type": "quantitative", "title": "Average Expenditure (R)"},
                "color": {
                    "field": "decile",
                    "type": "ordinal",
                    "scale": {"scheme": "redyellowgreen"},
                    "legend": None,
                },
                "tooltip": [
                    {"field": "decile", "type": "ordinal", "title": "Decile"},
                    {"field": "avg_expenditure", "type": "quantitative", "title": "Avg Expenditure", "format": ",.0f"},
                    {"field": "avg_income", "type": "quantitative", "title": "Avg Income", "format": ",.0f"},
                    {"field": "households", "type": "quantitative", "title": "Households"},
                ],
            },
        },
    },
    {
        "id": "medical_aid_health",
        "title": "Health Spending: Medical Aid vs Uninsured",
        "description": "Average out-of-pocket health expenditure per household, comparing those with and without medical aid.",
        "sql": """SELECT
  CASE h.eoh_meds WHEN '1' THEN 'On Medical Aid' WHEN '2' THEN 'Not on Medical Aid' END AS status,
  COUNT(DISTINCT h.uqno) AS households,
  ROUND(SUM(t.valueannualized_adj) / COUNT(DISTINCT h.uqno), 0) AS avg_health_per_hh,
  ROUND(SUM(t.valueannualized_adj), 0) AS total_health_spend
FROM total t
JOIN households h ON t.uqno = h.uqno
WHERE t.division = '06' AND h.eoh_meds IN ('1', '2')
GROUP BY h.eoh_meds""",
        "chart": {
            "mark": "bar",
            "encoding": {
                "x": {"field": "status", "type": "nominal", "title": "Medical Aid Status"},
                "y": {"field": "avg_health_per_hh", "type": "quantitative", "title": "Avg Health Spend per HH (R)"},
                "color": {"field": "status", "type": "nominal", "legend": None},
                "tooltip": [
                    {"field": "status", "type": "nominal"},
                    {"field": "avg_health_per_hh", "type": "quantitative", "title": "Avg Health/HH", "format": ",.0f"},
                    {"field": "households", "type": "quantitative", "title": "Households"},
                    {"field": "total_health_spend", "type": "quantitative", "title": "Total Health Spend", "format": ",.0f"},
                ],
            },
        },
    },
    {
        "id": "health_by_decile",
        "title": "Health Spending by Income Level & Medical Aid Status",
        "description": "How out-of-pocket health spending changes across income deciles for medical aid vs uninsured households.",
        "sql": """SELECT
  CAST(h.expenditure_decile AS INTEGER) AS decile,
  CASE h.eoh_meds WHEN '1' THEN 'Medical Aid' WHEN '2' THEN 'No Medical Aid' END AS status,
  COUNT(DISTINCT h.uqno) AS households,
  ROUND(SUM(t.valueannualized_adj) / COUNT(DISTINCT h.uqno), 0) AS avg_health_per_hh
FROM total t
JOIN households h ON t.uqno = h.uqno
WHERE t.division = '06' AND h.eoh_meds IN ('1', '2')
GROUP BY h.expenditure_decile, h.eoh_meds
ORDER BY CAST(h.expenditure_decile AS INTEGER), status""",
        "chart": {
            "mark": {"type": "line", "point": True},
            "encoding": {
                "x": {"field": "decile", "type": "ordinal", "title": "Expenditure Decile"},
                "y": {"field": "avg_health_per_hh", "type": "quantitative", "title": "Avg Health Spend per HH (R)"},
                "color": {"field": "status", "type": "nominal", "title": "Status"},
                "tooltip": [
                    {"field": "decile", "type": "ordinal"},
                    {"field": "status", "type": "nominal"},
                    {"field": "avg_health_per_hh", "type": "quantitative", "title": "Avg Health/HH", "format": ",.0f"},
                    {"field": "households", "type": "quantitative"},
                ],
            },
        },
    },
    {
        "id": "asset_ownership",
        "title": "Household Asset Ownership",
        "description": "Percentage of households that own various assets.",
        "sql": """SELECT
  'Cell phone' AS asset, ROUND(SUM(CASE WHEN has_cell='1' THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) AS ownership_pct FROM households
UNION ALL SELECT 'Electric stove', ROUND(SUM(CASE WHEN has_stove='1' THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) FROM households
UNION ALL SELECT 'Fridge', ROUND(SUM(CASE WHEN has_fridge='1' THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) FROM households
UNION ALL SELECT 'TV', ROUND(SUM(CASE WHEN has_tv='1' THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) FROM households
UNION ALL SELECT 'Satellite TV', ROUND(SUM(CASE WHEN has_satellite='1' THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) FROM households
UNION ALL SELECT 'Washing machine', ROUND(SUM(CASE WHEN has_washin='1' THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) FROM households
UNION ALL SELECT 'Motor vehicle', ROUND(SUM(CASE WHEN has_vehicle='1' THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) FROM households
UNION ALL SELECT 'Computer', ROUND(SUM(CASE WHEN has_desktop='1' THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) FROM households""",
        "chart": {
            "mark": "bar",
            "encoding": {
                "y": {"field": "asset", "type": "nominal", "sort": "-x", "title": "Asset"},
                "x": {"field": "ownership_pct", "type": "quantitative", "title": "% of Households"},
                "color": {"value": "#59a14f"},
                "tooltip": [
                    {"field": "asset", "type": "nominal"},
                    {"field": "ownership_pct", "type": "quantitative", "title": "Ownership %", "format": ".1f"},
                ],
            },
        },
    },
    {
        "id": "food_security",
        "title": "Food Security by Province",
        "description": "Percentage of households that report running out of money for food, by province.",
        "sql": """SELECT p.name AS province,
  ROUND(SUM(CASE WHEN h.lcf_anomoney = '1' THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) AS ran_out_of_money_pct,
  ROUND(SUM(CASE WHEN h.lcf_askip = '1' THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) AS skipped_meals_pct,
  ROUND(SUM(CASE WHEN h.lcf_alack = '1' THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) AS went_hungry_pct
FROM households h
JOIN geography g ON h.uqno = g.uqno
JOIN province_lookup p ON g.province = p.code
GROUP BY g.province
ORDER BY ran_out_of_money_pct DESC""",
        "chart": {
            "mark": "bar",
            "encoding": {
                "y": {"field": "province", "type": "nominal", "sort": "-x", "title": "Province"},
                "x": {"field": "ran_out_of_money_pct", "type": "quantitative", "title": "% Ran Out of Money for Food"},
                "color": {"value": "#e15759"},
                "tooltip": [
                    {"field": "province", "type": "nominal"},
                    {"field": "ran_out_of_money_pct", "type": "quantitative", "title": "Ran out of money %"},
                    {"field": "skipped_meals_pct", "type": "quantitative", "title": "Skipped meals %"},
                    {"field": "went_hungry_pct", "type": "quantitative", "title": "Went hungry %"},
                ],
            },
        },
    },
]

EXAMPLE_QUERIES_2011 = [
    {
        "id": "income_by_province",
        "title": "Average Income & Consumption by Province",
        "description": "Compare average household income and consumption expenditure across South Africa's 9 provinces.",
        "sql": """SELECT p.name AS province,
       ROUND(AVG(CAST(h.income AS REAL)), 0) AS avg_income,
       ROUND(AVG(CAST(h.consumptions AS REAL)), 0) AS avg_consumption
FROM households h
JOIN province_lookup p ON h.province = p.code
GROUP BY h.province
ORDER BY avg_income DESC""",
        "chart": {
            "mark": "bar",
            "encoding": {
                "y": {"field": "province", "type": "nominal", "sort": "-x", "title": "Province"},
                "x": {"field": "avg_income", "type": "quantitative", "title": "Average Annual Income (R)"},
                "color": {"value": "#4e79a7"},
                "tooltip": [
                    {"field": "province", "type": "nominal"},
                    {"field": "avg_income", "type": "quantitative", "title": "Avg Income", "format": ",.0f"},
                    {"field": "avg_consumption", "type": "quantitative", "title": "Avg Consumption", "format": ",.0f"},
                ],
            },
        },
    },
    {
        "id": "spending_categories",
        "title": "What Households Spend On (COICOP Divisions)",
        "description": "Total household expenditure broken down by major spending category.",
        "sql": """SELECT cd.label AS category,
       ROUND(SUM(t.valueannualized), 0) AS total_spend,
       COUNT(*) AS items
FROM total t
JOIN coicop_lookup cd ON t.division = cd.code AND cd.level = 'division'
WHERE CAST(t.division AS INTEGER) <= 13
GROUP BY t.division
ORDER BY total_spend DESC""",
        "chart": {
            "mark": "bar",
            "encoding": {
                "y": {"field": "category", "type": "nominal", "sort": "-x", "title": "Category"},
                "x": {"field": "total_spend", "type": "quantitative", "title": "Total Spend (R)"},
                "color": {"value": "#e15759"},
                "tooltip": [
                    {"field": "category", "type": "nominal"},
                    {"field": "total_spend", "type": "quantitative", "title": "Total Spend", "format": ",.0f"},
                    {"field": "items", "type": "quantitative", "title": "# Items"},
                ],
            },
        },
    },
    {
        "id": "income_by_population",
        "title": "Income by Population Group",
        "description": "Average household income by population group of the head of household.",
        "sql": """SELECT
  CASE popgrpofhead
    WHEN '1' THEN 'Black African'
    WHEN '2' THEN 'Coloured'
    WHEN '3' THEN 'Indian/Asian'
    WHEN '4' THEN 'White'
  END AS population_group,
  COUNT(*) AS households,
  ROUND(AVG(CAST(income AS REAL)), 0) AS avg_income,
  ROUND(AVG(CAST(consumptions AS REAL)), 0) AS avg_consumption
FROM households
WHERE popgrpofhead IN ('1','2','3','4')
GROUP BY popgrpofhead
ORDER BY avg_income DESC""",
        "chart": {
            "mark": "bar",
            "encoding": {
                "y": {
                    "field": "population_group",
                    "type": "nominal",
                    "sort": "-x",
                    "title": "Population Group",
                },
                "x": {"field": "avg_income", "type": "quantitative", "title": "Average Income (R)"},
                "color": {"field": "population_group", "type": "nominal", "legend": None},
                "tooltip": [
                    {"field": "population_group", "type": "nominal"},
                    {"field": "avg_income", "type": "quantitative", "title": "Avg Income", "format": ",.0f"},
                    {"field": "avg_consumption", "type": "quantitative", "title": "Avg Consumption", "format": ",.0f"},
                    {"field": "households", "type": "quantitative", "title": "Households"},
                ],
            },
        },
    },
    {
        "id": "expenditure_deciles",
        "title": "Consumption by Decile (Inequality)",
        "description": "Average household consumption across 10 income groups — decile 1 is the poorest 10%, decile 10 is the wealthiest 10%.",
        "sql": """SELECT
  CAST(consumptiondecile AS INTEGER) AS decile,
  COUNT(*) AS households,
  ROUND(AVG(CAST(consumptions AS REAL)), 0) AS avg_consumption,
  ROUND(AVG(CAST(income AS REAL)), 0) AS avg_income
FROM households
GROUP BY consumptiondecile
ORDER BY CAST(consumptiondecile AS INTEGER)""",
        "chart": {
            "mark": "bar",
            "encoding": {
                "x": {"field": "decile", "type": "ordinal", "title": "Consumption Decile (1=Poorest, 10=Wealthiest)"},
                "y": {"field": "avg_consumption", "type": "quantitative", "title": "Average Consumption (R)"},
                "color": {
                    "field": "decile",
                    "type": "ordinal",
                    "scale": {"scheme": "redyellowgreen"},
                    "legend": None,
                },
                "tooltip": [
                    {"field": "decile", "type": "ordinal", "title": "Decile"},
                    {"field": "avg_consumption", "type": "quantitative", "title": "Avg Consumption", "format": ",.0f"},
                    {"field": "avg_income", "type": "quantitative", "title": "Avg Income", "format": ",.0f"},
                    {"field": "households", "type": "quantitative", "title": "Households"},
                ],
            },
        },
    },
    {
        "id": "health_spending",
        "title": "Health Spending (COICOP Division 06)",
        "description": "Average out-of-pocket health expenditure per household, by province.",
        "sql": """SELECT p.name AS province,
  COUNT(DISTINCT t.uqno) AS households,
  ROUND(SUM(t.valueannualized) / COUNT(DISTINCT t.uqno), 0) AS avg_health_per_hh
FROM total t
JOIN geography g ON t.uqno = g.uqno
JOIN province_lookup p ON g.province = p.code
WHERE t.division = '06'
GROUP BY g.province
ORDER BY avg_health_per_hh DESC""",
        "chart": {
            "mark": "bar",
            "encoding": {
                "y": {"field": "province", "type": "nominal", "sort": "-x", "title": "Province"},
                "x": {"field": "avg_health_per_hh", "type": "quantitative", "title": "Avg Health Spend per HH (R)"},
                "color": {"value": "#76b7b2"},
                "tooltip": [
                    {"field": "province", "type": "nominal"},
                    {"field": "avg_health_per_hh", "type": "quantitative", "title": "Avg Health/HH", "format": ",.0f"},
                    {"field": "households", "type": "quantitative", "title": "Households"},
                ],
            },
        },
    },
    {
        "id": "asset_ownership",
        "title": "Household Asset Ownership",
        "description": "Percentage of households that own various assets (Q5.10.1 items, code 1=Yes).",
        "sql": """SELECT
  'Cell phone' AS asset, ROUND(SUM(CASE WHEN q5101a14cellularphone='1' THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) AS ownership_pct FROM households
UNION ALL SELECT 'Electric stove', ROUND(SUM(CASE WHEN q5101a06stove='1' THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) FROM households
UNION ALL SELECT 'Fridge', ROUND(SUM(CASE WHEN q5101a05refrigerator='1' THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) FROM households
UNION ALL SELECT 'TV', ROUND(SUM(CASE WHEN q5101a03television='1' THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) FROM households
UNION ALL SELECT 'Satellite TV (DSTV)', ROUND(SUM(CASE WHEN q5101a16dstv='1' THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) FROM households
UNION ALL SELECT 'Washing machine', ROUND(SUM(CASE WHEN q5101a08washingmachine='1' THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) FROM households
UNION ALL SELECT 'Motor vehicle', ROUND(SUM(CASE WHEN q5101a09motorvehicle='1' THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) FROM households
UNION ALL SELECT 'Computer', ROUND(SUM(CASE WHEN q5101a11computer='1' THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) FROM households""",
        "chart": {
            "mark": "bar",
            "encoding": {
                "y": {"field": "asset", "type": "nominal", "sort": "-x", "title": "Asset"},
                "x": {"field": "ownership_pct", "type": "quantitative", "title": "% of Households"},
                "color": {"value": "#59a14f"},
                "tooltip": [
                    {"field": "asset", "type": "nominal"},
                    {"field": "ownership_pct", "type": "quantitative", "title": "Ownership %", "format": ".1f"},
                ],
            },
        },
    },
]

EXAMPLES_BY_DATASET = {
    "ies2023": EXAMPLE_QUERIES_2023,
    "ies2011": EXAMPLE_QUERIES_2011,
}


SAFE_SQL_PATTERN = re.compile(
    r"^\s*SELECT\b", re.IGNORECASE | re.DOTALL
)
BLOCKED_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|ATTACH|DETACH|PRAGMA|VACUUM)\b",
    re.IGNORECASE,
)


def validate_sql(sql: str) -> str | None:
    """Return an error message if the SQL is not a safe read-only query."""
    sql = sql.strip().rstrip(";")
    if not SAFE_SQL_PATTERN.match(sql):
        return "Only SELECT queries are allowed."
    if BLOCKED_KEYWORDS.search(sql):
        return "Query contains forbidden keywords."
    return None


@app.route("/")
def index():
    dataset = request.args.get("dataset", DEFAULT_DATASET)
    examples = EXAMPLES_BY_DATASET.get(dataset, [])
    return render_template(
        "index.html",
        examples=examples,
        datasets=DATASETS,
        current_dataset=dataset,
    )


@app.route("/api/query", methods=["POST"])
def run_query():
    data = request.get_json()
    sql = data.get("sql", "").strip()
    dataset = data.get("dataset", DEFAULT_DATASET)
    if not sql:
        return jsonify({"error": "No SQL query provided."}), 400

    error = validate_sql(sql)
    if error:
        return jsonify({"error": error}), 400

    engine, _ = _get_engine(dataset)
    if not engine:
        return jsonify({"error": f"Unknown dataset: {dataset}"}), 400

    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
        return jsonify({"columns": columns, "rows": rows, "count": len(rows)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/tables")
def list_tables():
    dataset = request.args.get("dataset", DEFAULT_DATASET)
    engine, _ = _get_engine(dataset)
    if not engine:
        return jsonify({"error": f"Unknown dataset: {dataset}"}), 400

    with engine.connect() as conn:
        tables = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        ).fetchall()
        result = {}
        for (table_name,) in tables:
            cols = conn.execute(text(f"PRAGMA table_info('{table_name}')")).fetchall()
            result[table_name] = [{"name": c[1], "type": c[2]} for c in cols]
    return jsonify(result)


@app.route("/api/examples")
def get_examples():
    dataset = request.args.get("dataset", DEFAULT_DATASET)
    return jsonify(EXAMPLES_BY_DATASET.get(dataset, []))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
