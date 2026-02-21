"""Import IES 2022/23 CSV data into SQLite database."""
import csv
import sqlite3
import os

DB_PATH = "ies2023.db"
CSV_DIR = "csv_temp"

# Remove existing DB
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=NORMAL")
cur = conn.cursor()

# --- COICOP Lookup Table ---
print("Creating COICOP lookup table...")
cur.execute("""
CREATE TABLE coicop_lookup (
    code TEXT PRIMARY KEY,
    level TEXT,
    label TEXT
)
""")

coicop_data = [
    # Expenditure Divisions (level='division')
    ("01", "division", "Food and non-alcoholic beverages"),
    ("02", "division", "Alcoholic beverages, tobacco and narcotics"),
    ("03", "division", "Clothing and footwear"),
    ("04", "division", "Housing, water, electricity, gas and other fuels"),
    ("05", "division", "Furnishings, household equipment and routine maintenance"),
    ("06", "division", "Health"),
    ("07", "division", "Transport"),
    ("08", "division", "Information and communication"),
    ("09", "division", "Recreation, sport and culture"),
    ("10", "division", "Education services"),
    ("11", "division", "Restaurants and accommodation services"),
    ("12", "division", "Insurance and financial services"),
    ("13", "division", "Personal care, social protection and miscellaneous"),
    # Income Divisions
    ("50", "division", "Income: Salaries and wages"),
    ("51", "division", "Income: From business or profession"),
    ("52", "division", "Income: Other income"),
    ("53", "division", "Income: Grants and transfers"),
    ("66", "division", "Income: In-kind"),
    ("70", "division", "Income: Expenditure in kind (own production)"),
    ("71", "division", "Income: Expenditure in kind (received)"),
    ("80", "division", "Income: Imputed rent"),
    ("99", "division", "Income: Other/unclassified"),

    # Expenditure Groups (level='group')
    ("011", "group", "Food"),
    ("012", "group", "Non-alcoholic beverages"),
    ("013", "group", "Food not elsewhere classified"),
    ("021", "group", "Alcoholic beverages"),
    ("022", "group", "Tobacco"),
    ("023", "group", "Narcotics"),
    ("024", "group", "Alcoholic bev/tobacco NEC"),
    ("031", "group", "Clothing"),
    ("032", "group", "Footwear"),
    ("040", "group", "Actual and imputed rentals for housing"),
    ("041", "group", "Actual rentals for housing"),
    ("042", "group", "Imputed rentals for housing"),
    ("043", "group", "Maintenance and repair of dwelling"),
    ("044", "group", "Water supply and sanitation services"),
    ("045", "group", "Electricity, gas and other fuels"),
    ("051", "group", "Furniture, furnishings and carpets"),
    ("052", "group", "Household textiles"),
    ("053", "group", "Household appliances"),
    ("054", "group", "Glassware, tableware and household utensils"),
    ("055", "group", "Tools and equipment for house and garden"),
    ("056", "group", "Goods and services for routine household maintenance"),
    ("061", "group", "Medicines and health products"),
    ("062", "group", "Outpatient care services"),
    ("063", "group", "Inpatient care services"),
    ("064", "group", "Other health services"),
    ("071", "group", "Purchase of vehicles"),
    ("072", "group", "Operation of personal transport equipment"),
    ("073", "group", "Passenger transport services"),
    ("074", "group", "Transport services NEC"),
    ("081", "group", "Information and communication equipment"),
    ("082", "group", "Software, media and recordings"),
    ("083", "group", "Information and communication services"),
    ("091", "group", "Recreational durables"),
    ("092", "group", "Other recreational goods"),
    ("093", "group", "Garden products and pets"),
    ("094", "group", "Recreational services"),
    ("095", "group", "Cultural services"),
    ("096", "group", "Newspapers, books and stationery"),
    ("097", "group", "Package holidays"),
    ("098", "group", "Recreation NEC"),
    ("101", "group", "Pre-primary and primary education"),
    ("102", "group", "Secondary education"),
    ("103", "group", "Post-secondary non-tertiary education"),
    ("104", "group", "Tertiary education"),
    ("105", "group", "Education not definable by level"),
    ("111", "group", "Food and beverage serving services"),
    ("112", "group", "Accommodation services"),
    ("121", "group", "Insurance"),
    ("122", "group", "Financial services"),
    ("131", "group", "Personal care"),
    ("132", "group", "Personal effects NEC"),
    ("133", "group", "Social protection"),
    ("139", "group", "Other services NEC"),

    # Income Groups
    ("501", "group", "Income: Salaries/wages - regular"),
    ("502", "group", "Income: Salaries/wages - overtime"),
    ("503", "group", "Income: Salaries/wages - bonus"),
    ("504", "group", "Income: Salaries/wages - commission"),
    ("505", "group", "Income: Salaries/wages - allowances"),
    ("506", "group", "Income: Salaries/wages - other"),
    ("512", "group", "Income: Net profit - professional practice"),
    ("514", "group", "Income: Net profit - farming"),
    ("515", "group", "Income: Net profit - transport"),
    ("516", "group", "Income: Net profit - retail/trading"),
    ("517", "group", "Income: Net profit - manufacturing"),
    ("518", "group", "Income: Net profit - services"),
    ("519", "group", "Income: Net profit - other"),
    ("521", "group", "Income: Rental income"),
    ("522", "group", "Income: Royalties"),
    ("523", "group", "Income: Interest received"),
    ("524", "group", "Income: Dividends"),
    ("525", "group", "Income: Shareholders"),
    ("526", "group", "Income: Private pensions"),
    ("527", "group", "Income: Annuities"),
    ("531", "group", "Income: Social grants - old age"),
    ("532", "group", "Income: Social grants - disability"),
    ("533", "group", "Income: Social grants - child support"),
    ("534", "group", "Income: Social grants - other"),
    ("663", "group", "Income: In-kind benefits"),
    ("701", "group", "Income in kind: Own production - cereals"),
    ("702", "group", "Income in kind: Own production - vegetables"),
    ("703", "group", "Income in kind: Own production - fruit"),
    ("704", "group", "Income in kind: Own production - meat"),
    ("705", "group", "Income in kind: Own production - dairy"),
    ("706", "group", "Income in kind: Own production - other food"),
    ("707", "group", "Income in kind: Own production - beverages"),
    ("708", "group", "Income in kind: Own production - tobacco"),
    ("709", "group", "Income in kind: Own production - other"),
    ("711", "group", "Income in kind: Received - cereals"),
    ("712", "group", "Income in kind: Received - vegetables"),
    ("713", "group", "Income in kind: Received - fruit"),
    ("714", "group", "Income in kind: Received - meat"),
    ("715", "group", "Income in kind: Received - dairy"),
    ("716", "group", "Income in kind: Received - other food"),
    ("717", "group", "Income in kind: Received - beverages"),
    ("718", "group", "Income in kind: Received - tobacco"),
    ("719", "group", "Income in kind: Received - other"),
    ("801", "group", "Income: Imputed rent - owner occupied"),
    ("804", "group", "Income: Imputed rent - free/subsidised"),
    ("991", "group", "Income: Other unclassified"),
]

cur.executemany("INSERT INTO coicop_lookup VALUES (?, ?, ?)", coicop_data)

# --- Province Lookup ---
print("Creating province lookup table...")
cur.execute("""
CREATE TABLE province_lookup (
    code TEXT PRIMARY KEY,
    name TEXT
)
""")
provinces = [
    ("1", "Western Cape"), ("2", "Eastern Cape"), ("3", "Northern Cape"),
    ("4", "Free State"), ("5", "KwaZulu-Natal"), ("6", "North West"),
    ("7", "Gauteng"), ("8", "Mpumalanga"), ("9", "Limpopo"),
]
cur.executemany("INSERT INTO province_lookup VALUES (?, ?)", provinces)

# --- Settlement Type Lookup ---
print("Creating settlement type lookup table...")
cur.execute("""
CREATE TABLE settlement_lookup (
    code TEXT PRIMARY KEY,
    name TEXT
)
""")
settlements = [
    ("1", "Urban formal"), ("2", "Urban informal"),
    ("3", "Rural formal (farms)"), ("4", "Rural informal (tribal)"),
]
cur.executemany("INSERT INTO settlement_lookup VALUES (?, ?)", settlements)

conn.commit()

# --- Import CSV files ---
CSV_TABLE_MAP = {
    "Fact_IES2023_Geography.csv": "geography",
    "Fact_IES2023_Households.csv": "households",
    "Fact_IES2023_PersonIncome.csv": "person_income",
    "Fact_IES2023_Persons.csv": "persons",
    "Fact_IES2023_Total.csv": "total",
}

for csv_file, table_name in CSV_TABLE_MAP.items():
    path = os.path.join(CSV_DIR, csv_file)
    print(f"Importing {csv_file} -> {table_name}...")

    with open(path, "r") as f:
        reader = csv.reader(f)
        headers = [h.strip().lower() for h in next(reader)]

        # Create table - detect types from first few rows
        sample_rows = []
        for i, row in enumerate(reader):
            sample_rows.append(row)
            if i >= 100:
                break

        col_types = []
        for col_idx, header in enumerate(headers):
            is_numeric = True
            is_float = False
            for row in sample_rows:
                val = row[col_idx].strip().strip('"')
                if val == "" or val == "88" or val == "888" or val == "8888":
                    continue
                try:
                    int(val)
                except ValueError:
                    try:
                        float(val)
                        is_float = True
                    except ValueError:
                        is_numeric = False
                        break

            if is_numeric and is_float:
                col_types.append("REAL")
            elif is_numeric and header in (
                "valueannualized_adj", "valueannualized_adj_wgt",
                "hhold_wgt", "persns_wgt", "expenditure", "income",
                "expenditure_inkind", "income_inkind",
                "expenditure_weighted", "income_weighted",
                "expenditure_inkind_weighted", "income_inkind_weighted",
                "expenditure_pcp", "income_pcp",
            ):
                col_types.append("REAL")
            elif is_numeric and header in ("age", "hsize", "head_age", "personno"):
                col_types.append("INTEGER")
            else:
                col_types.append("TEXT")

        cols_def = ", ".join(f'"{h}" {t}' for h, t in zip(headers, col_types))
        cur.execute(f"CREATE TABLE {table_name} ({cols_def})")

        # Insert sample rows first
        placeholders = ", ".join(["?"] * len(headers))
        cur.executemany(
            f"INSERT INTO {table_name} VALUES ({placeholders})",
            sample_rows,
        )

        # Insert remaining rows in batches
        batch = []
        batch_size = 10000
        for row in reader:
            batch.append(row)
            if len(batch) >= batch_size:
                cur.executemany(
                    f"INSERT INTO {table_name} VALUES ({placeholders})",
                    batch,
                )
                batch = []
        if batch:
            cur.executemany(
                f"INSERT INTO {table_name} VALUES ({placeholders})",
                batch,
            )

    conn.commit()
    count = cur.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"  -> {count:,} rows imported")

# --- Create indexes ---
print("Creating indexes...")
cur.execute("CREATE INDEX idx_geography_uqno ON geography(uqno)")
cur.execute("CREATE INDEX idx_households_uqno ON households(uqno)")
cur.execute("CREATE INDEX idx_persons_uqno ON persons(uqno)")
cur.execute("CREATE INDEX idx_persons_person_id ON persons(person_id)")
cur.execute("CREATE INDEX idx_total_uqno ON total(uqno)")
cur.execute("CREATE INDEX idx_total_division ON total(division)")
cur.execute("CREATE INDEX idx_total_coicop ON total(coicop)")
cur.execute("CREATE INDEX idx_person_income_person_id ON person_income(person_id)")
cur.execute("CREATE INDEX idx_geography_province ON geography(province)")
cur.execute("CREATE INDEX idx_geography_settlement ON geography(settlement_type)")
conn.commit()

print("Creating views...")
# Useful view: households joined with geography
cur.execute("""
CREATE VIEW household_geo AS
SELECT h.*, g.metro_code, g.province, g.settlement_type, g.surveydate,
       p.name AS province_name, s.name AS settlement_name
FROM households h
JOIN geography g ON h.uqno = g.uqno
LEFT JOIN province_lookup p ON g.province = p.code
LEFT JOIN settlement_lookup s ON g.settlement_type = s.code
""")

# Useful view: total expenditure with COICOP labels
cur.execute("""
CREATE VIEW total_labelled AS
SELECT t.*,
       cd.label AS division_label,
       cg.label AS group_label
FROM total t
LEFT JOIN coicop_lookup cd ON t.division = cd.code AND cd.level = 'division'
LEFT JOIN coicop_lookup cg ON t."group" = cg.code AND cg.level = 'group'
""")

conn.commit()
conn.close()
print("Done! Database created: ies2023.db")
