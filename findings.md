# IES 2022/23 Findings

## Part 1: Broad Exploration

### 1. Extreme Income Inequality

South Africa's inequality is starkly visible in the data:

- **Income ratio** (Decile 10 vs Decile 1): **54.4x** — the top 10% of households earn 54 times more than the bottom 10%
- **Expenditure ratio** (Decile 10 vs Decile 1): **23.4x** — the top 10% spend 23 times more

| Decile | Avg Expenditure (R) | Avg Income (R) |
|--------|-------------------:|---------------:|
| 1 (Poorest) | 22,428 | — |
| 5 (Median) | 73,481 | — |
| 10 (Wealthiest) | 525,043 | — |

The expenditure gap is smaller than the income gap, suggesting wealthier households save a larger share of their income while poorer households spend nearly everything they earn.

### 2. Racial Income Disparities

| Population Group | Households | Avg Income (R) | Avg Expenditure (R) |
|-----------------|----------:|---------------:|--------------------:|
| White | 1,035 | 636,745 | 387,400 |
| Indian/Asian | 276 | 376,280 | 265,246 |
| Coloured | 1,623 | 215,580 | 152,385 |
| Black African | 17,006 | 126,720 | 97,239 |

White-headed households earn **5x** more than Black African-headed households on average. The Indian/Asian to Black African ratio is 3x, and Coloured to Black African is 1.7x.

### 3. Gender Gap in Household Headship

| Head Gender | Households | Avg Income (R) | Avg Expenditure (R) | Avg HH Size |
|------------|----------:|---------------:|--------------------:|------------:|
| Male | 10,492 | 195,284 | 133,280 | 3.2 |
| Female | 9,448 | 129,006 | 103,384 | 3.9 |

Male-headed households earn 51% more but have fewer members (3.2 vs 3.9), meaning the per-capita gap is even wider. Nearly half (47.4%) of all households are female-headed.

### 4. Provincial Differences

| Province | Avg Income (R) | Avg Expenditure (R) |
|----------|---------------:|--------------------:|
| Western Cape | 300,933 | 196,722 |
| Gauteng | 191,283 | 134,227 |
| Northern Cape | 163,815 | 117,255 |
| KwaZulu-Natal | 149,398 | 111,491 |
| Free State | 142,730 | 105,443 |
| Mpumalanga | 134,625 | 104,261 |
| North West | 128,203 | 89,658 |
| Eastern Cape | 123,274 | 101,502 |
| Limpopo | 120,785 | 94,375 |

The Western Cape leads with an average household income of R300,933 — 2.5x that of Limpopo (R120,785).

### 5. Urban vs Rural Divide

| Settlement Type | Avg Income (R) | Avg Expenditure (R) |
|----------------|---------------:|--------------------:|
| Urban formal | 194,815 | 137,371 |
| Rural formal (farms) | 172,982 | 112,634 |
| Urban informal | 103,167 | 84,584 |

Urban formal households earn 89% more than urban informal households. Farm households earn more than urban informal ones, likely reflecting farm-owner wages.

### 6. Education and Income

| Education Level | Households | Avg Income (R) | Avg Expenditure (R) |
|----------------|----------:|---------------:|--------------------:|
| Primary school | 4,177 | 95,424 | 73,725 |
| Secondary school | 11,894 | 131,248 | 102,160 |
| Certificate/Diploma | 532 | 223,223 | 172,610 |
| Degree/Postgraduate | 2,339 | 474,334 | 295,289 |

A degree or postgraduate qualification is associated with **5x** the income of primary education only. The jump from secondary to degree level is 3.6x.

### 7. What Do Households Spend On?

**Poorest Quintile (Q1)** — spending is dominated by survival basics:

| Category | Total Spend (R) | Rank |
|----------|----------------:|:----:|
| Housing, water, electricity | 56,411,033 | 1 |
| Food and beverages | 38,995,850 | 2 |
| Clothing and footwear | 6,433,757 | 3 |
| Transport | 5,955,173 | 4 |

**Wealthiest Quintile (Q5)** — spending shifts to transport, insurance, and discretionary items:

| Category | Total Spend (R) | Rank |
|----------|----------------:|:----:|
| Housing, water, electricity | 311,448,893 | 1 |
| Transport | 237,636,346 | 2 |
| Insurance and financial services | 166,114,670 | 3 |
| Food and beverages | 126,267,865 | 4 |

For the poorest, food is the 2nd-largest expense. For the wealthiest, it drops to 4th while transport and insurance surge ahead.

### 8. Asset Ownership

| Asset | % of Households |
|-------|:--------------:|
| Cell phone | 93.3% |
| Electric stove | 91.3% |
| Fridge | 77.3% |
| TV | 76.5% |
| Satellite TV (DStv) | 59.1% |
| Washing machine | 37.6% |
| Motor vehicle | 23.1% |
| Computer/desktop | 23.1% |

Cell phone ownership is nearly universal (93.3%), while motor vehicle and computer ownership remain at around 23%.

### 9. Social Grants

Social grants are a critical safety net. By province, child support grant receipt ranges from 5.8% of the population (Western Cape) to 13.3% (KwaZulu-Natal). The Social Relief of Distress (SRD) grant — introduced during COVID-19 — reaches 4.1% in Western Cape and up to 13.0% in Limpopo.

### 10. Food Security Crisis

| Indicator | % of Households |
|-----------|:--------------:|
| Ran out of money for food | 39.9% |
| Skipped meals | 27.2% |
| Went hungry | 24.8% |

Nearly **40%** of households report running out of money for food, and **1 in 4** experienced actual hunger. This represents a significant food security challenge.

### 11. Poverty Rates by Province (Weighted)

Using the persons-level poverty indicators (where `poor1/2/3` = 1 means **above** the respective poverty line):

| Province | % Above Food Poverty Line | % Above Lower Bound | % Above Upper Bound |
|----------|:------------------------:|:-------------------:|:-------------------:|
| Western Cape | 92.2% | 78.6% | 49.2% |
| Gauteng | 89.3% | 73.5% | 46.4% |
| Free State | 86.5% | 65.6% | 34.1% |
| Mpumalanga | 85.7% | 61.6% | 28.5% |
| Northern Cape | 81.2% | 57.7% | 30.5% |
| Limpopo | 79.2% | 52.4% | 20.5% |
| Eastern Cape | 77.1% | 51.8% | 23.9% |
| KwaZulu-Natal | 72.7% | 50.4% | 22.8% |
| North West | 72.7% | 50.9% | 22.8% |

Inverted, this means KwaZulu-Natal and North West have the highest food poverty rates (~27.3%), while over half the population nationally falls below the upper-bound poverty line.

---

## Part 2: Out-of-Pocket Medical Expenses — Medical Aid vs Uninsured

### Overview: Who Has Medical Aid?

Only **40.5%** of surveyed households have medical aid coverage. Coverage is strongly correlated with income:

| Expenditure Decile | Medical Aid Coverage (%) |
|-------------------:|:-----------------------:|
| 1 (Poorest) | 19.0% |
| 2 | 26.0% |
| 3 | 30.8% |
| 4 | 34.4% |
| 5 | 37.9% |
| 6 | 43.4% |
| 7 | 47.9% |
| 8 | 54.7% |
| 9 | 58.3% |
| 10 (Wealthiest) | 66.7% |

Even among the wealthiest 10%, a third lack medical aid coverage.

### Medical Aid Coverage by Province

| Province | Medical Aid (%) |
|----------|:--------------:|
| Western Cape | 45.5% |
| Free State | 44.3% |
| KwaZulu-Natal | 43.8% |
| Eastern Cape | 42.6% |
| Mpumalanga | 41.5% |
| Limpopo | 39.3% |
| Gauteng | 39.1% |
| North West | 30.8% |
| Northern Cape | 30.2% |

### Total Health Expenditure: Medical Aid vs Uninsured

| Status | Households with Health Spending | Avg Health Spend per HH (R) | Health as % of Total Expenditure |
|--------|-------------------------------:|----------------------------:|:-------------------------------:|
| On medical aid | 6,524 | 2,685 | 1.7% |
| Not on medical aid | 4,662 | 1,260 | 1.4% |

Medical aid members spend **2.1x** more out-of-pocket on health, despite already paying for their medical aid premiums. This suggests medical aid facilitates greater healthcare utilisation rather than simply replacing out-of-pocket spending.

### What Are They Spending On?

| Health Category | Medical Aid (R/HH) | No Medical Aid (R/HH) | Ratio |
|-----------------|-------------------:|----------------------:|------:|
| Medicines and health products | 1,578 | 859 | 1.8x |
| Outpatient care services | 2,014 | 1,146 | 1.8x |
| Inpatient care services | 11,038 | 5,032 | 2.2x |
| Other health services | 1,617 | 1,131 | 1.4x |

Note: These are averages only among households that incurred costs in each category. Inpatient care is rare but extremely expensive — and medical aid members incur 2.7x more inpatient items (145 vs 54 in the sample).

### Out-of-Pocket Health Spending by Income Level

| Decile | Medical Aid (R/HH) | No Medical Aid (R/HH) | Gap |
|-------:|-------------------:|----------------------:|----:|
| 1 | 399 | 361 | 1.1x |
| 2 | 568 | 445 | 1.3x |
| 3 | 761 | 505 | 1.5x |
| 4 | 893 | 709 | 1.3x |
| 5 | 967 | 784 | 1.2x |
| 6 | 1,239 | 1,199 | 1.0x |
| 7 | 1,511 | 1,040 | 1.5x |
| 8 | 2,018 | 1,454 | 1.4x |
| 9 | 3,804 | 2,334 | 1.6x |
| 10 | 10,651 | 5,788 | 1.8x |

**Key trend**: At low income levels, the gap between medical aid and uninsured is small (deciles 1-6, gap of 1.0-1.5x). The gap **widens dramatically at the top**: in decile 10, medical aid members spend R10,651 vs R5,788 for the uninsured. This suggests wealthy medical aid members top up their coverage with significant private spending (specialists, private hospital co-payments, cosmetic/elective procedures).

### The Racial Dimension

| Population Group | Status | Avg Health Expenditure (R) |
|-----------------|--------|---------------------------:|
| White | Medical aid | 9,319 |
| White | No medical aid | 2,695 |
| Indian/Asian | Medical aid | 4,011 |
| Indian/Asian | No medical aid | 1,059 |
| Coloured | Medical aid | 2,046 |
| Coloured | No medical aid | 451 |
| Black African | Medical aid | 1,465 |
| Black African | No medical aid | 439 |

The disparity is staggering: White households on medical aid spend **21x** more on health than Black African households without medical aid. Even within the same medical aid status, White households spend 6x more than Black African households.

### The Full Cost of Healthcare: Premiums + Out-of-Pocket

When including insurance/financial services (division 12, which contains medical aid premiums):

| Status | Avg Insurance Spend (R) | Avg Health Out-of-Pocket (R) | Estimated Total (R) |
|--------|------------------------:|-----------------------------:|--------------------:|
| On medical aid | 20,076 | 2,685 | ~22,761 |
| Not on medical aid | 9,749 | 1,260 | ~11,009 |

The ~R10,327 difference in insurance spend largely reflects medical aid premiums. Medical aid members therefore spend approximately **R22,761** annually on healthcare (premiums + out-of-pocket), while the uninsured spend **R1,260** out-of-pocket only (plus a small portion of their R9,749 insurance spend may cover funeral/life policies with health components).

### Healthcare Spending vs Inflation Context

All IES 2022/23 values are benchmarked to **May 2023 prices**. South Africa's headline CPI inflation averaged approximately 6.9% in 2022 and 6.0% in 2023. However, medical inflation has historically run well above general CPI in South Africa:

- The medical CPI sub-index has consistently risen 1.5-2x faster than headline CPI
- Medical aid premiums have increased at 8-12% annually over the past decade
- This means the real burden of healthcare costs grows faster than wages for most households

Since this is a single cross-sectional survey, we cannot directly measure inflation trends within this data. However, the pattern across income deciles reveals that healthcare spending is **income elastic** — as household income rises, health spending rises even faster (from R361-399 in decile 1 to R5,788-10,651 in decile 10). This suggests that:

1. **Lower-income households suppress healthcare spending** — likely forgoing or delaying care due to cost
2. **Medical inflation disproportionately burdens middle-income households** — those in deciles 5-7 who may have medical aid but face rising premiums and co-payments
3. **The uninsured face a double bind**: no coverage AND lower out-of-pocket spending, suggesting they simply access less care rather than paying for it differently

### Summary of Key Medical Findings

1. Only 40.5% of households have medical aid — coverage ranges from 19% (poorest) to 67% (wealthiest)
2. Medical aid members spend 2.1x more out-of-pocket on health than uninsured households
3. The spending gap widens with income: 1.0x in the middle deciles, 1.8x at the top
4. Inpatient care is the biggest cost driver (R11,038 per episode for medical aid, R5,032 without)
5. White medical aid members spend 21x more than Black African uninsured households
6. Including premiums, medical aid members pay ~R22,761/year for healthcare vs ~R1,260 for the uninsured
7. Low out-of-pocket spending by uninsured households likely reflects suppressed demand, not lower need

---

*Source: Statistics South Africa, Income and Expenditure Survey 2022/23 (Report P0100). All monetary values in South African Rand, annualised and adjusted to May 2023 prices.*
