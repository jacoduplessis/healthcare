# IES 2022/23 Data Overview

## About the Dataset

The **Income and Expenditure Survey (IES) 2022/23** is a household-based sample survey conducted by Statistics South Africa (Stats SA) between November 2022 and November 2023. It collects information on acquisitions, consumption, spending, and income earned by households in South Africa.

The survey sample covers **19,939 households** representing an estimated **21.3 million households** and **61.2 million people** (when survey weights are applied).

---

## Database Structure

The SQLite database `ies2023.db` contains **5 data tables** and **3 lookup tables**:

| Table | Rows | Columns | Description |
|-------|------|---------|-------------|
| `geography` | 19,940 | 5 | Geographic location of each household (province, metro area, settlement type) |
| `households` | 19,940 | 345 | Household characteristics: dwelling, services, assets, crime, food security, finance, health, demographics of head, and aggregate income/expenditure |
| `persons` | 70,339 | 216 | Individual-level data: demographics, education, employment, health, migration, social grants, disability |
| `person_income` | 48,038 | 5 | Personal income by COICOP income category (annualised, adjusted values) |
| `total` | 1,128,279 | 10 | All expenditure and income line items classified by COICOP code (annualised, adjusted to May 2023 prices) |
| `coicop_lookup` | 121 | 3 | Maps COICOP division/group codes to human-readable labels |
| `province_lookup` | 9 | 2 | Maps province codes (1-9) to province names |
| `settlement_lookup` | 4 | 2 | Maps settlement type codes to descriptions |

### Key Relationships

- **`uqno`** (unique household number) links `geography`, `households`, `persons`, and `total`
- **`person_id`** links `persons` to `person_income`
- **`division`** and **`group`** in `total` link to `coicop_lookup`
- **`province`** in `geography` links to `province_lookup`

---

## Geographic Distribution

### Households by Province (sample)

| Province | Households | % of Sample |
|----------|-----------|-------------|
| Gauteng | 4,688 | 23.5% |
| KwaZulu-Natal | 3,216 | 16.1% |
| Eastern Cape | 2,752 | 13.8% |
| Limpopo | 2,237 | 11.2% |
| Western Cape | 1,830 | 9.2% |
| Mpumalanga | 1,580 | 7.9% |
| Free State | 1,369 | 6.9% |
| North West | 1,382 | 6.9% |
| Northern Cape | 886 | 4.4% |

### Households by Settlement Type

| Settlement Type | Households | % |
|----------------|-----------|---|
| Urban formal | 12,661 | 63.5% |
| Urban informal | 6,559 | 32.9% |
| Rural formal (farms) | 720 | 3.6% |

---

## Population Demographics

### Age Distribution (70,339 persons)

| Age Group | Count | % |
|-----------|-------|---|
| 0-17 (Children) | 25,236 | 35.9% |
| 18-34 (Young adults) | 18,689 | 26.6% |
| 35-49 (Middle age) | 12,916 | 18.4% |
| 50-64 (Older adults) | 8,578 | 12.2% |
| 65+ (Elderly) | 4,920 | 7.0% |

### Population Group

| Group | Count | % |
|-------|-------|---|
| Black African | 60,629 | 86.2% |
| Coloured | 6,300 | 9.0% |
| White | 2,589 | 3.7% |
| Indian/Asian | 821 | 1.2% |

### Household Size

- **Average**: 3.5 persons per household
- **Range**: 1 to 30 persons
- **Most common**: 1 person (23.3%), 2 persons (17.9%), 3 persons (15.7%)
- 23.3% of households are single-person households

---

## Income and Expenditure Summary

All monetary values are annualised and adjusted to **May 2023 prices** (in South African Rand).

### Household-Level Totals

| Metric | Min | Average | Max |
|--------|-----|---------|-----|
| Annual Expenditure (R) | 2,727 | 119,114 | 2,429,938 |
| Annual Income (R) | 150 | 163,880 | 6,854,725 |

### Average Income & Expenditure by Province

| Province | Avg Income (R) | Avg Expenditure (R) |
|----------|---------------|---------------------|
| Western Cape | 300,933 | 196,722 |
| Gauteng | 191,283 | 134,227 |
| Northern Cape | 163,815 | 117,255 |
| KwaZulu-Natal | 149,398 | 111,491 |
| Free State | 142,730 | 105,443 |
| Mpumalanga | 134,625 | 104,261 |
| North West | 128,203 | 89,658 |
| Eastern Cape | 123,274 | 101,502 |
| Limpopo | 120,785 | 94,375 |

### Expenditure Decile Distribution

| Decile | Households | Min (R) | Avg (R) | Max (R) |
|--------|-----------|---------|---------|---------|
| 1 (Poorest) | 2,044 | 2,727 | 22,428 | 30,820 |
| 2 | 2,126 | 30,821 | 36,958 | 42,652 |
| 3 | 2,158 | 42,653 | 48,111 | 53,726 |
| 4 | 2,135 | 53,726 | 59,910 | 66,240 |
| 5 | 2,181 | 66,243 | 73,481 | 81,551 |
| 6 | 2,152 | 81,558 | 90,738 | 101,100 |
| 7 | 2,148 | 101,106 | 115,567 | 133,192 |
| 8 | 1,948 | 133,205 | 158,208 | 188,478 |
| 9 | 1,705 | 188,491 | 235,723 | 306,043 |
| 10 (Wealthiest) | 1,343 | 306,318 | 525,043 | 2,429,938 |

The wealthiest 10% of households spend on average **23x** more than the poorest 10%.

---

## What Households Spend On (COICOP Expenditure Divisions)

| Category | Items in Data | Total Spend (R, sample) | Avg per Item (R) |
|----------|--------------|------------------------|-------------------|
| Housing, water, electricity, gas | 72,940 | 780,503,766 | 10,701 |
| Food and non-alcoholic beverages | 419,328 | 465,781,643 | 1,111 |
| Transport | 52,569 | 347,283,715 | 6,606 |
| Insurance and financial services | 38,855 | 244,216,385 | 6,285 |
| Clothing and footwear | 81,608 | 135,825,710 | 1,664 |
| Information and communication | 51,653 | 110,105,998 | 2,132 |
| Furnishings and household equipment | 86,103 | 98,150,250 | 1,140 |
| Personal care and miscellaneous | 65,115 | 76,808,715 | 1,180 |
| Restaurants and accommodation | 27,394 | 59,391,002 | 2,168 |
| Education | 4,832 | 52,052,279 | 10,772 |
| Alcohol, tobacco and narcotics | 23,114 | 36,434,069 | 1,576 |
| Recreation, sport and culture | 21,866 | 29,955,777 | 1,370 |
| Health | 21,982 | 23,403,778 | 1,065 |

**Housing** is the single largest spending category, followed by **food** (which has the most individual line items).

---

## Health and Medical Aid Coverage

| Medical Aid Status | Households | % |
|-------------------|-----------|---|
| Yes (on medical aid) | 8,085 | 40.5% |
| No (not on medical aid) | 11,345 | 56.9% |
| Don't know | 19 | 0.1% |
| Unspecified | 491 | 2.5% |

---

## Food Security Indicators

| Indicator | Households | % |
|-----------|-----------|---|
| Ran out of money for food | 7,962 | 39.9% |
| Skipped meals | 5,432 | 27.2% |
| Went hungry | 4,947 | 24.8% |

Nearly **40%** of surveyed households reported running out of money to buy food, and about **1 in 4** households experienced hunger.

---

## Key Columns in the Households Table (345 columns)

The households table is extensive. Key column groups include:

| Prefix | Domain | Examples |
|--------|--------|----------|
| `IRD_` | Dwelling characteristics | Walls, roof, floor material and condition |
| `WAT_` | Water supply | Drinking water source, distance, payment |
| `SAN_` | Sanitation | Toilet type, sewerage, location |
| `ENG_` | Energy | Electricity access, cooking/heating fuel |
| `SWR_` | Solid waste removal | Refuse collection, separation, recycling |
| `ATS_` | Access to services | Distance to clinic, hospital |
| `HOU_` | Housing | Ownership, rooms, value, repairs |
| `HAS_` | Household assets | Radio, TV, fridge, vehicle, cell phone, etc. |
| `CRIME_` | Crime experience | Assault, robbery, burglary, fraud, etc. |
| `SPG_` | Swimming pool/garden | |
| `TRA_` | Transport | Vehicle acquisition, driving licence |
| `DWS_` | Domestic workers | |
| `ICH_` | Own production | |
| `CFW_` | Clothing/footwear | |
| `EDU_` | Education expenditure | Public/private attendance at various levels |
| `SUB_` | Subsistence farming | Land ownership, crops, livestock |
| `LCF_` | Living conditions & food security | Food security scale indicators |
| `FAB_` | Finance and banking | Mortgages, loans, credit cards, stokvels |
| `EOH_` | Expenditure on health | Medical aid, prescriptions |
| `HEAD_` | Head of household | Sex, age, population group, education, marital status |
| `EXPENDITURE*` | Aggregate expenditure | Total, per capita, decile, quintile |
| `INCOME*` | Aggregate income | Total, per capita, decile, quintile |

---

## Code Reference

| Variable | Code | Meaning |
|----------|------|---------|
| Province | 1-9 | WC, EC, NC, FS, KZN, NW, GP, MP, LP |
| Settlement Type | 1-3 | Urban formal, Urban informal, Rural formal |
| Sex | 1=Male | 2=Female |
| Population Group | 1=Black African | 2=Coloured, 3=Indian/Asian, 4=White |
| Medical Aid (eoh_meds) | 1=Yes, 2=No | 3=Don't know, 9=Unspecified |
| Yes/No fields | 1=Yes, 2=No | 8=N/A, 88=N/A, 9=Unspecified |

---

*Source: Statistics South Africa, Income and Expenditure Survey 2022/23 (Report P0100)*
