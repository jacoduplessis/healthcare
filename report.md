# Out-of-Pocket Health Expenditure Among Medical Scheme Members and Non-Members in South Africa: A Nearest-Neighbour Matching Analysis Using the IES 2022/23

## Abstract

**Background:** South Africa operates a two-tier healthcare system in which medical scheme members access private healthcare while the uninsured rely primarily on public facilities. Whether medical scheme membership is associated with higher out-of-pocket (OOP) co-payments — beyond the premiums themselves — is a critical question for health financing policy.

**Methods:** Using microdata from the Income and Expenditure Survey (IES) 2022/23 conducted by Statistics South Africa (n = 18,455 households), we employ nearest-neighbour matching (NNM) on Mahalanobis distance to estimate the Average Treatment Effect on the Treated (ATT) of medical scheme membership on OOP health expenditure. Matching covariates include log household expenditure, log household income, household size, age, sex, population group, and education level of the household head, and settlement type. We conduct national and provincial-level analyses with sensitivity checks including exact province matching and restriction to households with positive health expenditure.

**Results:** After matching 6,625 treated-control pairs (85.9% match rate) with excellent covariate balance (all post-matching standardised mean differences < 0.10), medical scheme members incur significantly higher OOP health expenditure than comparable non-members: ATT = R968.44 (95% CI: R831.37 to R1,105.51; p < 0.001; Cohen's d = 0.170). The naive (unmatched) difference of R1,679.68 overstates the effect by 73%, confirming the importance of controlling for confounders. The result is robust to bootstrapping (95% CI: R815.46 to R1,093.42), exact province matching (pooled ATT = R949.71), and restriction to households with positive health spending (ATT = R719.70, p < 0.001). The effect is significant in all nine provinces (p < 0.05), ranging from R402.17 in North West (d = 0.131) to R1,588.77 in the Western Cape (d = 0.223). Medical scheme members are also substantially more likely to incur any health spending (80.2% vs 46.6%).

**Conclusion:** Medical scheme membership in South Africa is associated with statistically significant and economically meaningful additional OOP co-payments of approximately R968 per annum, even after rigorous matching on socioeconomic characteristics. This finding holds nationally and across all nine provinces, suggesting that medical scheme coverage complements rather than substitutes for private health spending. The lower healthcare utilisation among non-members likely reflects suppressed demand due to cost and access barriers rather than lower need.

**Keywords:** out-of-pocket health expenditure, medical schemes, nearest-neighbour matching, South Africa, health financing, co-payments, IES 2022/23

---

## 1. Introduction

South Africa's healthcare system is characterised by stark duality. Approximately 16% of the population — predominantly higher-income earners — belong to medical schemes and access a well-resourced private sector, while the remaining 84% rely on the public health system (Council for Medical Schemes, 2023). This structural divide has motivated ongoing policy reform, including the proposed National Health Insurance (NHI) Bill.

A key but underexplored dimension of this duality concerns out-of-pocket (OOP) health expenditure. While medical schemes provide coverage for hospitalisation, consultations, and medicines, members frequently face co-payments, deductibles, and above-threshold expenses that are not fully reimbursed. Whether these co-payments are systematically larger than the OOP spending of non-members — who may simply forego or delay care — has important implications for understanding health access and financial protection.

Naive comparisons of OOP expenditure between scheme members and non-members conflate the effect of scheme membership with underlying differences in socioeconomic status, since wealthier households are far more likely to hold medical scheme coverage. This study addresses this confounding by employing nearest-neighbour matching (NNM), a well-established method in the programme evaluation literature (Abadie & Imbens, 2006; Rubin, 1973), to construct comparable treatment and control groups.

We use microdata from the Income and Expenditure Survey (IES) 2022/23, the most recent national household expenditure survey conducted by Statistics South Africa, which provides detailed line-item expenditure data classified by the international COICOP standard.

### 1.1 Objectives

1. To estimate the causal effect of medical scheme membership on out-of-pocket health expenditure at the national level, controlling for observable socioeconomic confounders
2. To conduct province-level analyses to assess geographic heterogeneity in this effect
3. To evaluate the robustness of findings through sensitivity analyses

---

## 2. Data and Methods

### 2.1 Data Source

The IES 2022/23 was conducted by Statistics South Africa between 7 November 2022 and 19 November 2023 over 26 survey periods. The survey employed a stratified multi-stage sampling design using the Geospatial Information Frame (GIF), with primary sampling units drawn from 3,318 PSUs and a systematic sample of 31,042 dwelling units. The overall response rate was 81.94%. The final dataset comprises 19,939 responding households.

All expenditure values are annualised and price-adjusted to May 2023 Rand using CPI deflators, as documented in the IES methodology (Stats SA, 2025).

### 2.2 Variables

**Outcome variable:** Total annual out-of-pocket health expenditure, computed as the sum of all household expenditure items classified under COICOP Division 06 (Health), which comprises:
- Group 061: Medicines and health products
- Group 062: Outpatient care services
- Group 063: Inpatient care services
- Group 064: Other health services

This measure captures direct OOP spending on healthcare and excludes medical scheme premiums (classified under Division 12: Insurance and Financial Services).

**Treatment variable:** Medical scheme membership, coded as a binary indicator (eoh_meds = 1 for members, eoh_meds = 2 for non-members). Households with missing or unspecified values (n = 510) were excluded.

**Matching covariates:**
- Log annual household expenditure (continuous)
- Log annual household income (continuous)
- Household size (continuous)
- Age of household head (continuous)
- Sex of household head (binary: 1 = male, 2 = female)
- Population group of household head (categorical: 1 = Black African, 2 = Coloured, 3 = Indian/Asian, 4 = White)
- Education level of household head (ordinal, grouped: 0 = none, 1 = primary, 2 = secondary, 3 = certificate/diploma, 4 = degree/postgraduate)
- Settlement type (categorical: 1 = urban formal, 2 = urban informal, 3 = rural formal)

### 2.3 Nearest-Neighbour Matching

We employ one-to-one nearest-neighbour matching without replacement using Mahalanobis distance on the standardised covariate vector. For each treated unit (medical scheme member), the algorithm identifies the control unit (non-member) with the minimum Euclidean distance in the standardised covariate space, subject to a caliper constraint.

Formally, for treated unit *i* with covariate vector **x**_i, the matched control *j(i)* is:

j(i) = argmin_{j ∈ C} || (**x**_i − **x**_j) / **s** ||

where **s** is the pooled standard deviation vector and *C* is the set of unmatched control units.

A caliper of 0.5 pooled standard deviations per dimension was applied at the national level, relaxed to 0.75 for provincial analyses where sample sizes are smaller. Matching was performed without replacement to avoid using a single control unit multiple times, which would inflate precision.

### 2.4 Estimand and Inference

The estimand of interest is the Average Treatment Effect on the Treated (ATT):

ATT = E[Y(1) − Y(0) | T = 1]

estimated as the mean difference in OOP health expenditure between treated units and their matched controls:

ATT = (1/N_m) Σ_{i ∈ matched} [Y_i^T − Y_{j(i)}^C]

Standard errors are computed as σ_d / √N_m, where σ_d is the standard deviation of the matched pair differences. We report:
- Paired t-tests for mean differences
- Wilcoxon signed-rank tests as a non-parametric alternative
- 95% confidence intervals (analytical and bootstrap with 500 replications)
- Cohen's d as a measure of effect size

### 2.5 Balance Diagnostics

Covariate balance is assessed using standardised mean differences (SMD) before and after matching. An SMD below 0.10 in absolute value is conventionally considered adequate balance (Austin, 2011).

### 2.6 Sensitivity Analyses

Three sensitivity analyses are conducted:
1. **Bootstrap confidence intervals** (500 replications) for the national ATT
2. **Exact province matching:** Matching is performed separately within each province and results are pooled with inverse-variance weighting to eliminate any residual geographic confounding
3. **Conditional on positive health expenditure:** Restricting the sample to households with OOP health expenditure > 0 to assess whether the effect holds among healthcare utilisers

### 2.7 Sample

After excluding households with missing treatment status, zero expenditure, invalid head age, unspecified population group, or unspecified education level, the analysis sample comprises 18,455 households: 7,711 medical scheme members (treated) and 10,744 non-members (control).

---

## 3. Results

### 3.1 National Analysis

#### 3.1.1 Matching Performance

Of 7,711 treated households, 6,625 (85.9%) were successfully matched to unique control households. The match rate indicates adequate overlap in the covariate distributions.

#### 3.1.2 Covariate Balance

Table 1 presents standardised mean differences before and after matching.

**Table 1: Covariate Balance — Standardised Mean Differences**

| Covariate | SMD Before | SMD After | % Reduction |
|-----------|----------:|----------:|------------:|
| Log expenditure | 0.6132 | 0.0903 | 85.3% |
| Log income | 0.4571 | 0.0241 | 94.7% |
| Household size | 0.1766 | 0.0278 | 84.3% |
| Head age | 0.1641 | 0.0094 | 94.3% |
| Head sex | 0.0629 | 0.0015 | 97.6% |
| Head population group | 0.2103 | 0.0066 | 96.9% |
| Education group | 0.2369 | 0.0044 | 98.2% |
| Settlement type | −0.0593 | 0.0022 | 96.3% |

Before matching, substantial imbalances exist, particularly in log expenditure (SMD = 0.613) and education (SMD = 0.237), reflecting the strong socioeconomic gradient in medical scheme membership. After matching, all SMDs fall well below the 0.10 threshold, with a mean absolute SMD of 0.017. The largest residual imbalance is in log expenditure (0.090), still within acceptable bounds. Balance improvement ranges from 84.3% (household size) to 98.2% (education).

#### 3.1.3 Average Treatment Effect on the Treated

**Table 2: National ATT Estimates**

| Estimate | Value |
|----------|------:|
| Matched pairs | 6,625 |
| Mean OOP — treated (R) | 1,699.23 |
| Mean OOP — matched control (R) | 730.79 |
| **ATT (R)** | **968.44** |
| Standard error (R) | 69.93 |
| 95% CI — analytical (R) | [831.37, 1,105.51] |
| 95% CI — bootstrap (R) | [815.46, 1,093.42] |
| Paired t-statistic | 13.848 |
| p-value (paired t-test) | 5.17 × 10⁻⁴³ |
| p-value (Wilcoxon signed-rank) | 7.09 × 10⁻²²⁶ |
| Cohen's d | 0.170 |

The ATT of R968.44 is highly statistically significant (p < 10⁻⁴²) and indicates that medical scheme members incur nearly R1,000 per year more in OOP health expenditure than socioeconomically comparable non-members. The bootstrap confidence interval [R815.46, R1,093.42] closely tracks the analytical CI, supporting the reliability of standard error estimation.

The naive (unmatched) difference of R1,679.68 overstates the matched ATT by 73.5%, demonstrating the importance of accounting for selection into medical scheme membership.

Cohen's d of 0.170 indicates a small-to-medium effect size by conventional standards (Cohen, 1988), which is typical for population-level observational studies.

#### 3.1.4 Healthcare Utilisation

A striking finding is the differential in healthcare utilisation: 80.2% of matched treated households report any health expenditure, compared with only 46.6% of matched controls. The median OOP expenditure among treated households is R457.62, versus R0.00 for controls. This suggests that the OOP gap is driven both by higher per-episode spending *and* by higher utilisation among scheme members.

### 3.2 Provincial Analysis

**Table 3: Provincial ATT Estimates**

| Province | Matched Pairs | Match Rate (%) | ATT (R) | SE (R) | 95% CI (R) | p-value | Cohen's d |
|----------|:------------:|:--------------:|--------:|-------:|:----------:|:-------:|----------:|
| Western Cape | 648 | 78.5 | 1,588.77 | 280.01 | [1,039.94, 2,137.59] | 2.11 × 10⁻⁸ | 0.223 |
| Eastern Cape | 924 | 84.8 | 1,046.49 | 114.61 | [821.85, 1,271.13] | 4.20 × 10⁻¹⁹ | 0.300 |
| Northern Cape | 256 | 98.5 | 913.61 | 314.91 | [296.37, 1,530.84] | 4.04 × 10⁻³ | 0.181 |
| Free State | 504 | 85.1 | 747.94 | 267.15 | [224.33, 1,271.55] | 5.31 × 10⁻³ | 0.125 |
| KwaZulu-Natal | 1,106 | 83.9 | 1,132.81 | 140.53 | [857.36, 1,408.25] | 1.96 × 10⁻¹⁵ | 0.242 |
| North West | 389 | 96.5 | 402.17 | 155.97 | [96.47, 707.87] | 1.03 × 10⁻² | 0.131 |
| Gauteng | 1,564 | 86.3 | 806.60 | 187.97 | [438.18, 1,175.02] | 1.89 × 10⁻⁵ | 0.109 |
| Mpumalanga | 543 | 90.7 | 681.45 | 112.89 | [460.19, 902.70] | 2.92 × 10⁻⁹ | 0.259 |
| Limpopo | 717 | 88.3 | 932.14 | 132.29 | [672.86, 1,191.43] | 4.33 × 10⁻¹² | 0.263 |

The ATT is statistically significant (p < 0.05) in all nine provinces. The effect exhibits notable geographic heterogeneity:

- **Largest effect:** Western Cape (R1,588.77), where the concentration of private healthcare providers and higher medical scheme benefit options likely drives higher co-payments.
- **Smallest effect:** North West (R402.17), a predominantly rural province with less private healthcare infrastructure.
- **Largest effect sizes (Cohen's d):** Eastern Cape (0.300), Limpopo (0.263), and Mpumalanga (0.259), suggesting that the OOP premium associated with scheme membership is most pronounced relative to background variation in these less urbanised provinces.
- **Smallest effect size:** Gauteng (0.109), where both groups have higher absolute spending levels, narrowing the relative gap.

### 3.3 Sensitivity Analyses

**Table 4: Sensitivity Analysis Results**

| Analysis | ATT (R) | 95% CI (R) | p-value |
|----------|--------:|:----------:|:-------:|
| **Main analysis** (national NNM) | **968.44** | **[831.37, 1,105.51]** | **5.17 × 10⁻⁴³** |
| Bootstrap (500 replications) | 951.23 | [815.46, 1,093.42] | — |
| Exact province matching (pooled) | 949.71 | [819.32, 1,080.11] | — |
| Positive health expenditure only | 719.70 | [533.24, 906.17] | 4.77 × 10⁻¹⁴ |

All sensitivity analyses confirm the main finding:

1. **Bootstrap CI** [R815.46, R1,093.42] closely aligns with the analytical CI, confirming appropriate standard error estimation.
2. **Exact province matching** yields a pooled ATT of R949.71 (95% CI: R819.32 to R1,080.11), virtually identical to the main estimate, indicating that geographic confounding does not materially affect the national result.
3. **Among healthcare utilisers** (OOP > 0), the ATT is R719.70 (p < 0.001), indicating that even conditional on accessing healthcare, scheme members pay substantially more out of pocket. The reduction from R968 to R720 reflects the compositional effect: scheme members are more likely to utilise healthcare at all.

---

## 4. Discussion

### 4.1 Interpretation of Findings

Our central finding — that medical scheme members incur approximately R968 more per year in OOP health expenditure than comparable non-members — admits two complementary interpretations:

**First, scheme membership enables greater healthcare utilisation.** The 80.2% vs 46.6% utilisation differential suggests that non-members face substantial access barriers — financial, geographic, or informational — that suppress their healthcare consumption. The zero median OOP expenditure among matched controls is a striking marker of unmet healthcare need.

**Second, private healthcare carries higher co-payment burdens.** Even among households that do access healthcare, scheme members pay R720 more, reflecting the co-payment structures of medical schemes (deductibles, above-PMB co-payments, gap cover shortfalls) and the higher price levels of the private sector.

These findings align with the broader literature on healthcare duality in middle-income countries (McIntyre et al., 2009; Ataguba & McIntyre, 2012) and have direct implications for the NHI reform process.

### 4.2 Provincial Heterogeneity

The geographic pattern of effects is informative. The Western Cape — with the highest private healthcare density and the most developed medical scheme market — shows the largest absolute ATT (R1,588.77). In contrast, North West — with limited private infrastructure — shows the smallest effect (R402.17). This suggests that the availability of private providers is a key driver of the OOP premium, as scheme members in provinces with fewer private options have less opportunity (or need) to incur co-payments.

Interestingly, the largest *relative* effects (Cohen's d) are in the Eastern Cape (0.300) and Limpopo (0.263), where base expenditure levels are lower. This implies that the OOP burden of medical scheme co-payments, while smaller in absolute terms, represents a proportionally larger share of healthcare spending in poorer provinces.

### 4.3 Limitations

1. **Unobserved confounding:** NNM controls for observed covariates but cannot address unobserved confounders such as health status, chronic conditions, or risk preferences. Individuals in poor health may be both more likely to hold medical scheme coverage and more likely to incur health expenditure, biasing the ATT upward.

2. **Cross-sectional design:** The IES provides a single time point, precluding analysis of how OOP dynamics change over time or in response to premium increases.

3. **Expenditure as proxy for income:** Household expenditure, while a standard welfare measure in developing-country settings (Deaton, 1997), may not fully capture permanent income, particularly for households with transitory income shocks.

4. **COICOP classification:** Some health-related expenditure may be misclassified (e.g., traditional medicine coded elsewhere), and insurance premiums in Division 12 are not decomposable into medical scheme vs other insurance products.

5. **Matching approach:** One-to-one matching without replacement discards unmatched treated units (14.1%). These are predominantly high-expenditure households at the upper tail of the income distribution, where common support with the control group is limited. Results may therefore be less generalisable to the wealthiest scheme members.

### 4.4 Policy Implications

The finding that medical scheme membership amplifies rather than reduces OOP expenditure has implications for the NHI debate:

- **Financial protection:** Medical schemes provide access but not complete financial protection against health costs. Members face a double burden of premiums plus co-payments.
- **Suppressed demand:** The extremely low OOP spending among non-members (median R0) should not be interpreted as evidence of lower healthcare need but rather of rationed access.
- **Universal coverage design:** Any universal system should address both the access gap (non-members not utilising care) and the co-payment gap (members facing excessive OOP costs).

---

## 5. Conclusion

Using nearest-neighbour matching on the IES 2022/23, we find that medical scheme membership in South Africa is associated with significantly higher out-of-pocket health expenditure: an ATT of R968.44 per year (95% CI: R831–R1,106; p < 10⁻⁴²). The effect is statistically significant in all nine provinces, largest in the Western Cape (R1,589) and smallest in the North West (R402). These findings are robust to bootstrap inference, exact geographic matching, and restriction to healthcare utilisers. The results suggest that medical scheme coverage facilitates healthcare access but does not eliminate — and in fact increases — out-of-pocket health spending relative to comparable uninsured households.

---

## References

Abadie, A. & Imbens, G.W. (2006). Large sample properties of matching estimators for average treatment effects. *Econometrica*, 74(1), 235–267.

Ataguba, J.E. & McIntyre, D. (2012). Paying for and receiving benefits from health services in South Africa: Is the health system equitable? *Health Policy and Planning*, 27(suppl_1), i35–i45.

Austin, P.C. (2011). An introduction to propensity score methods for reducing the effects of confounding in observational studies. *Multivariate Behavioral Research*, 46(3), 399–424.

Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.). Lawrence Erlbaum Associates.

Council for Medical Schemes. (2023). *Annual Report 2022/23*. Pretoria: CMS.

Deaton, A. (1997). *The Analysis of Household Surveys: A Microeconometric Approach to Development Policy*. World Bank Publications.

McIntyre, D., Thiede, M., Dahlgren, G. & Whitehead, M. (2009). What are the economic consequences for households of illness and of paying for health care in low- and middle-income country contexts? *Social Science & Medicine*, 68(4), 1375–1383.

Rubin, D.B. (1973). Matching to remove bias in observational studies. *Biometrics*, 29(1), 159–183.

Statistics South Africa. (2025). *Income and Expenditure Survey 2022/23: Metadata* (Report P0100). Pretoria: Stats SA.

---

*Data source: Statistics South Africa, Income and Expenditure Survey 2022/23 (Report P0100). Analysis conducted using nearest-neighbour matching on Mahalanobis distance with the SciPy scientific computing library (v1.17).*
