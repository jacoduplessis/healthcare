#set document(
  title: "Out-of-Pocket Health Expenditure Among Medical Scheme Members and Non-Members in South Africa",
  author: "Statistical Analysis Report",
  date: datetime(year: 2025, month: 2, day: 20),
)

#set page(
  paper: "a4",
  margin: (top: 2.5cm, bottom: 2.5cm, left: 2.5cm, right: 2.5cm),
  numbering: "1",
  header: context {
    if counter(page).get().first() > 1 [
      #set text(size: 8pt, fill: gray)
      _OOP Health Expenditure: Medical Scheme Members vs Non-Members — IES 2022/23_
      #h(1fr)
      #counter(page).display()
    ]
  },
)

#set text(
  font: "New Computer Modern",
  size: 11pt,
  lang: "en",
)

#set par(
  justify: true,
  leading: 0.65em,
  first-line-indent: 1.25em,
)

#set heading(numbering: "1.1")

#show heading.where(level: 1): it => {
  set text(size: 14pt, weight: "bold")
  v(1.5em)
  it
  v(0.75em)
}

#show heading.where(level: 2): it => {
  set text(size: 12pt, weight: "bold")
  v(1em)
  it
  v(0.5em)
}

#show heading.where(level: 3): it => {
  set text(size: 11pt, weight: "bold", style: "italic")
  v(0.75em)
  it
  v(0.25em)
}

#show figure: it => {
  v(0.5em)
  it
  v(0.5em)
}

// ============ TITLE PAGE ============

#align(center)[
  #v(3cm)
  #text(size: 18pt, weight: "bold")[
    Out-of-Pocket Health Expenditure Among Medical Scheme Members and Non-Members in South Africa
  ]
  #v(0.75cm)
  #text(size: 14pt, weight: "bold", fill: rgb("#2d5a87"))[
    A Nearest-Neighbour Matching Analysis\ Using the IES 2022/23
  ]
  #v(2cm)
  #text(size: 11pt)[
    Statistical Analysis Report
  ]
  #v(0.5cm)
  #text(size: 10pt, fill: gray)[
    Data source: Statistics South Africa\ Income and Expenditure Survey 2022/23 (Report P0100)
  ]
  #v(0.5cm)
  #text(size: 10pt, fill: gray)[
    February 2025
  ]
]

#pagebreak()

// ============ ABSTRACT ============

#heading(level: 1, numbering: none)[Abstract]

#par(first-line-indent: 0em)[
  *Background:* South Africa operates a two-tier healthcare system in which medical scheme members access private healthcare while the uninsured rely primarily on public facilities. Whether medical scheme membership is associated with higher out-of-pocket (OOP) co-payments — beyond the premiums themselves — is a critical question for health financing policy.
]

*Methods:* Using microdata from the Income and Expenditure Survey (IES) 2022/23 conducted by Statistics South Africa (_n_ = 18,455 households), we employ nearest-neighbour matching (NNM) on Mahalanobis distance to estimate the Average Treatment Effect on the Treated (ATT) of medical scheme membership on OOP health expenditure. Matching covariates include log household expenditure, log household income, household size, age, sex, population group, and education level of the household head, and settlement type. We conduct national and provincial-level analyses with sensitivity checks.

*Results:* After matching 6,625 treated-control pairs (85.9% match rate) with excellent covariate balance (all post-matching standardised mean differences < 0.10), medical scheme members incur significantly higher OOP health expenditure than comparable non-members: ATT = R968.44 (95% CI: R831.37 to R1,105.51; _p_ < 0.001; Cohen's _d_ = 0.170). The naive (unmatched) difference of R1,679.68 overstates the effect by 73%, confirming the importance of controlling for confounders. The effect is significant in all nine provinces (_p_ < 0.05), ranging from R402 in North West to R1,589 in the Western Cape. Medical scheme members are substantially more likely to incur any health spending (80.2% vs 46.6%).

*Conclusion:* Medical scheme membership is associated with significantly higher OOP health expenditure of approximately R968 per annum. This suggests that medical scheme coverage complements rather than substitutes for private health spending.

*Keywords:* out-of-pocket health expenditure, medical schemes, nearest-neighbour matching, South Africa, health financing, co-payments, IES 2022/23

#v(1em)
#line(length: 100%, stroke: 0.5pt + gray)

// ============ INTRODUCTION ============

= Introduction

South Africa's healthcare system is characterised by stark duality. Approximately 16% of the population — predominantly higher-income earners — belong to medical schemes and access a well-resourced private sector, while the remaining 84% rely on the public health system (Council for Medical Schemes, 2023). This structural divide has motivated ongoing policy reform, including the proposed National Health Insurance (NHI) Bill.

A key but underexplored dimension of this duality concerns out-of-pocket (OOP) health expenditure. While medical schemes provide coverage for hospitalisation, consultations, and medicines, members frequently face co-payments, deductibles, and above-threshold expenses that are not fully reimbursed. Whether these co-payments are systematically larger than the OOP spending of non-members — who may simply forego or delay care — has important implications for understanding health access and financial protection.

Naive comparisons of OOP expenditure between scheme members and non-members conflate the effect of scheme membership with underlying differences in socioeconomic status, since wealthier households are far more likely to hold medical scheme coverage. This study addresses this confounding by employing nearest-neighbour matching (NNM), a well-established method in the programme evaluation literature (Abadie & Imbens, 2006; Rubin, 1973), to construct comparable treatment and control groups.

We use microdata from the Income and Expenditure Survey (IES) 2022/23, the most recent national household expenditure survey conducted by Statistics South Africa, which provides detailed line-item expenditure data classified by the international COICOP standard.

== Objectives

+ Estimate the causal effect of medical scheme membership on out-of-pocket health expenditure at the national level, controlling for observable socioeconomic confounders.
+ Conduct province-level analyses to assess geographic heterogeneity.
+ Evaluate the robustness of findings through sensitivity analyses.

// ============ DATA AND METHODS ============

= Data and Methods

== Data Source

The IES 2022/23 was conducted by Statistics South Africa between 7 November 2022 and 19 November 2023 over 26 survey periods. The survey employed a stratified multi-stage sampling design using the Geospatial Information Frame (GIF), with primary sampling units drawn from 3,318 PSUs and a systematic sample of 31,042 dwelling units. The overall response rate was 81.94%. The final dataset comprises 19,939 responding households.

All expenditure values are annualised and price-adjusted to May 2023 Rand using CPI deflators, as documented in the IES methodology (Stats SA, 2025).

== Variables

*Outcome variable:* Total annual out-of-pocket health expenditure, computed as the sum of all household expenditure items classified under COICOP Division 06 (Health), comprising medicines and health products (Group 061), outpatient care services (Group 062), inpatient care services (Group 063), and other health services (Group 064). This measure excludes medical scheme premiums (classified under Division 12).

*Treatment variable:* Medical scheme membership, coded as a binary indicator. Households with missing or unspecified values (_n_ = 510) were excluded.

*Matching covariates:* Log annual household expenditure, log annual household income, household size, age of household head, sex of household head, population group of household head, education level of household head (grouped into five ordinal categories), and settlement type.

== Nearest-Neighbour Matching

We employ one-to-one nearest-neighbour matching without replacement using Mahalanobis distance on the standardised covariate vector. For each treated unit (medical scheme member), the algorithm identifies the control unit (non-member) with the minimum Euclidean distance in the standardised covariate space, subject to a caliper constraint of 0.5 pooled standard deviations per dimension at the national level (relaxed to 0.75 for provincial analyses).

Formally, for treated unit _i_ with covariate vector $bold(x)_i$, the matched control $j(i)$ is:

$ j(i) = op("argmin", limits: #true)_(j in C) norm((bold(x)_i - bold(x)_j) / bold(s)) $

where $bold(s)$ is the pooled standard deviation vector and _C_ is the set of unmatched control units.

== Estimand and Inference

The estimand is the Average Treatment Effect on the Treated (ATT):

$ "ATT" = EE[Y(1) - Y(0) | T = 1] $

estimated as:

$ hat("ATT") = frac(1, N_m) sum_(i in "matched") [Y_i^T - Y_(j(i))^C] $

Standard errors are computed as $sigma_d \/ sqrt(N_m)$. We report paired _t_-tests, Wilcoxon signed-rank tests, analytical and bootstrap (500 replications) 95% confidence intervals, and Cohen's _d_.

== Balance Diagnostics

Covariate balance is assessed using standardised mean differences (SMD). An SMD below 0.10 in absolute value is considered adequate (Austin, 2011).

== Sensitivity Analyses

Three sensitivity analyses are conducted: (1) bootstrap confidence intervals for the national ATT; (2) exact province matching with pooled estimates; (3) restriction to households with positive health expenditure.

== Sample

After exclusions, the analysis sample comprises 18,455 households: 7,711 medical scheme members (treated) and 10,744 non-members (control).

// ============ RESULTS ============

= Results

== National Analysis

=== Matching Performance

Of 7,711 treated households, 6,625 (85.9%) were successfully matched to unique control households, indicating adequate overlap in covariate distributions.

=== Covariate Balance

#figure(
  caption: [Covariate Balance — Standardised Mean Differences],
  table(
    columns: (auto, auto, auto, auto),
    align: (left, right, right, right),
    stroke: none,
    table.hline(stroke: 1pt),
    table.header(
      [*Covariate*], [*SMD Before*], [*SMD After*], [*% Reduction*],
    ),
    table.hline(stroke: 0.5pt),
    [Log expenditure],    [0.6132], [0.0903], [85.3%],
    [Log income],         [0.4571], [0.0241], [94.7%],
    [Household size],     [0.1766], [0.0278], [84.3%],
    [Head age],           [0.1641], [0.0094], [94.3%],
    [Head sex],           [0.0629], [0.0015], [97.6%],
    [Head population group], [0.2103], [0.0066], [96.9%],
    [Education group],    [0.2369], [0.0044], [98.2%],
    [Settlement type],    [−0.0593], [0.0022], [96.3%],
    table.hline(stroke: 1pt),
  ),
) <tab:balance>

Before matching, substantial imbalances exist, particularly in log expenditure (SMD = 0.613) and education (SMD = 0.237). After matching, all SMDs fall below 0.10 (mean |SMD| = 0.017), with balance improvement ranging from 84.3% to 98.2%.

=== Average Treatment Effect on the Treated

#figure(
  caption: [National ATT Estimates],
  table(
    columns: (auto, auto),
    align: (left, right),
    stroke: none,
    table.hline(stroke: 1pt),
    table.header([*Estimate*], [*Value*]),
    table.hline(stroke: 0.5pt),
    [Matched pairs],                    [6,625],
    [Mean OOP — treated (R)],          [1,699.23],
    [Mean OOP — matched control (R)],  [730.79],
    [*ATT (R)*],                       [*968.44*],
    [Standard error (R)],              [69.93],
    [95% CI — analytical (R)],         [\[831.37, 1,105.51\]],
    [95% CI — bootstrap (R)],          [\[815.46, 1,093.42\]],
    [Paired _t_-statistic],            [13.848],
    [_p_-value (paired _t_-test)],     [$5.17 times 10^(-43)$],
    [_p_-value (Wilcoxon)],            [$7.09 times 10^(-226)$],
    [Cohen's _d_],                     [0.170],
    table.hline(stroke: 1pt),
  ),
) <tab:att>

The ATT of R968.44 is highly statistically significant ($p < 10^(-42)$) and indicates that medical scheme members incur nearly R1,000 per year more in OOP health expenditure than socioeconomically comparable non-members. The naive (unmatched) difference of R1,679.68 overstates the matched ATT by 73.5%.

Cohen's _d_ of 0.170 indicates a small-to-medium effect size, typical for population-level observational studies.

=== Healthcare Utilisation

A striking finding is the differential in healthcare utilisation: 80.2% of matched treated households report any health expenditure, compared with only 46.6% of matched controls. The median OOP expenditure among treated households is R457.62, versus R0.00 for controls.

== Provincial Analysis

#figure(
  caption: [Provincial ATT Estimates],
  table(
    columns: (auto, auto, auto, auto, auto, auto, auto),
    align: (left, center, right, right, center, center, right),
    stroke: none,
    table.hline(stroke: 1pt),
    table.header(
      [*Province*], [*Pairs*], [*ATT (R)*], [*SE (R)*], [*95% CI (R)*], [*_p_-value*], [*Cohen's _d_*],
    ),
    table.hline(stroke: 0.5pt),
    [Western Cape],   [648],   [1,588.77], [280.01], [\[1,040, 2,138\]], [$2.1 times 10^(-8)$],  [0.223],
    [Eastern Cape],   [924],   [1,046.49], [114.61], [\[822, 1,271\]],   [$4.2 times 10^(-19)$], [0.300],
    [Northern Cape],  [256],   [913.61],   [314.91], [\[296, 1,531\]],   [$4.0 times 10^(-3)$],  [0.181],
    [Free State],     [504],   [747.94],   [267.15], [\[224, 1,272\]],   [$5.3 times 10^(-3)$],  [0.125],
    [KwaZulu-Natal],  [1,106], [1,132.81], [140.53], [\[857, 1,408\]],   [$2.0 times 10^(-15)$], [0.242],
    [North West],     [389],   [402.17],   [155.97], [\[96, 708\]],      [$1.0 times 10^(-2)$],  [0.131],
    [Gauteng],        [1,564], [806.60],   [187.97], [\[438, 1,175\]],   [$1.9 times 10^(-5)$],  [0.109],
    [Mpumalanga],     [543],   [681.45],   [112.89], [\[460, 903\]],     [$2.9 times 10^(-9)$],  [0.259],
    [Limpopo],        [717],   [932.14],   [132.29], [\[673, 1,191\]],   [$4.3 times 10^(-12)$], [0.263],
    table.hline(stroke: 1pt),
  ),
) <tab:provincial>

The ATT is statistically significant (_p_ < 0.05) in all nine provinces. The effect exhibits notable geographic heterogeneity:

- *Largest absolute effect:* Western Cape (R1,588.77), where the concentration of private healthcare providers and higher-benefit medical scheme options likely drives higher co-payments.
- *Smallest absolute effect:* North West (R402.17), a predominantly rural province with less private healthcare infrastructure.
- *Largest relative effect sizes:* Eastern Cape (_d_ = 0.300), Limpopo (_d_ = 0.263), and Mpumalanga (_d_ = 0.259), suggesting that the OOP premium is most pronounced relative to background variation in less urbanised provinces.
- *Smallest relative effect size:* Gauteng (_d_ = 0.109), where both groups have higher absolute spending levels.

== Sensitivity Analyses

#figure(
  caption: [Sensitivity Analysis Results],
  table(
    columns: (auto, auto, auto, auto),
    align: (left, right, center, center),
    stroke: none,
    table.hline(stroke: 1pt),
    table.header([*Analysis*], [*ATT (R)*], [*95% CI (R)*], [*_p_-value*]),
    table.hline(stroke: 0.5pt),
    [*Main analysis* (national NNM)],       [*968.44*], [*\[831, 1,106\]*], [*$5.2 times 10^(-43)$*],
    [Bootstrap (500 replications)],          [951.23],   [\[815, 1,093\]],   [—],
    [Exact province matching (pooled)],      [949.71],   [\[819, 1,080\]],   [—],
    [Positive health expenditure only],      [719.70],   [\[533, 906\]],     [$4.8 times 10^(-14)$],
    table.hline(stroke: 1pt),
  ),
) <tab:sensitivity>

All sensitivity analyses confirm the main finding. The bootstrap CI closely aligns with the analytical CI. Exact province matching yields a virtually identical pooled ATT (R949.71). Among healthcare utilisers (OOP > 0), the ATT of R719.70 remains highly significant.

// ============ DISCUSSION ============

= Discussion

== Interpretation of Findings

Our central finding — that medical scheme members incur approximately R968 more per year in OOP health expenditure than comparable non-members — admits two complementary interpretations.

*First, scheme membership enables greater healthcare utilisation.* The 80.2% vs 46.6% utilisation differential suggests that non-members face substantial access barriers — financial, geographic, or informational — that suppress their healthcare consumption. The zero median OOP expenditure among matched controls is a striking marker of unmet healthcare need.

*Second, private healthcare carries higher co-payment burdens.* Even among households that do access healthcare, scheme members pay R720 more, reflecting the co-payment structures of medical schemes and the higher price levels of the private sector.

These findings align with the broader literature on healthcare duality in middle-income countries (McIntyre _et al._, 2009; Ataguba & McIntyre, 2012) and have direct implications for the NHI reform process.

== Provincial Heterogeneity

The geographic pattern is informative. The Western Cape — with the highest private healthcare density — shows the largest absolute ATT (R1,589). The largest _relative_ effects (Cohen's _d_) are in the Eastern Cape (0.300) and Limpopo (0.263), implying that the OOP burden of scheme co-payments is proportionally larger in poorer provinces.

== Limitations

+ *Unobserved confounding:* NNM controls for observed covariates but cannot address unobserved confounders such as health status, chronic conditions, or risk preferences.
+ *Cross-sectional design:* The IES provides a single time point, precluding longitudinal analysis.
+ *Expenditure as proxy for income:* While standard in developing-country settings (Deaton, 1997), household expenditure may not fully capture permanent income.
+ *COICOP classification:* Some health-related expenditure may be misclassified, and insurance premiums in Division 12 are not decomposable.
+ *Common support:* 14.1% of treated units remain unmatched, predominantly high-expenditure households, limiting generalisability to the wealthiest scheme members.

== Policy Implications

The finding that scheme membership amplifies rather than reduces OOP expenditure has implications for the NHI debate:

- *Financial protection:* Medical schemes provide access but not complete financial protection. Members face a double burden of premiums plus co-payments.
- *Suppressed demand:* The low OOP spending among non-members reflects rationed access, not lower need.
- *Universal coverage design:* Any universal system should address both the access gap and the co-payment gap.

// ============ CONCLUSION ============

= Conclusion

Using nearest-neighbour matching on the IES 2022/23, we find that medical scheme membership in South Africa is associated with significantly higher out-of-pocket health expenditure: an ATT of R968.44 per year (95% CI: R831–R1,106; $p < 10^(-42)$). The effect is statistically significant in all nine provinces, largest in the Western Cape (R1,589) and smallest in the North West (R402). These findings are robust to bootstrap inference, exact geographic matching, and restriction to healthcare utilisers. Medical scheme coverage facilitates healthcare access but does not eliminate — and in fact increases — out-of-pocket health spending relative to comparable uninsured households.

// ============ REFERENCES ============

#heading(level: 1, numbering: none)[References]

#set par(first-line-indent: 0em, hanging-indent: 1.5em)
#set text(size: 10pt)

Abadie, A. & Imbens, G.W. (2006). Large sample properties of matching estimators for average treatment effects. _Econometrica_, 74(1), 235–267.

Ataguba, J.E. & McIntyre, D. (2012). Paying for and receiving benefits from health services in South Africa: Is the health system equitable? _Health Policy and Planning_, 27(suppl_1), i35–i45.

Austin, P.C. (2011). An introduction to propensity score methods for reducing the effects of confounding in observational studies. _Multivariate Behavioral Research_, 46(3), 399–424.

Cohen, J. (1988). _Statistical Power Analysis for the Behavioral Sciences_ (2nd ed.). Lawrence Erlbaum Associates.

Council for Medical Schemes. (2023). _Annual Report 2022/23_. Pretoria: CMS.

Deaton, A. (1997). _The Analysis of Household Surveys: A Microeconometric Approach to Development Policy_. World Bank Publications.

McIntyre, D., Thiede, M., Dahlgren, G. & Whitehead, M. (2009). What are the economic consequences for households of illness and of paying for health care in low- and middle-income country contexts? _Social Science & Medicine_, 68(4), 1375–1383.

Rubin, D.B. (1973). Matching to remove bias in observational studies. _Biometrics_, 29(1), 159–183.

Statistics South Africa. (2025). _Income and Expenditure Survey 2022/23: Metadata_ (Report P0100). Pretoria: Stats SA.

#v(2em)
#line(length: 100%, stroke: 0.5pt + gray)
#set text(size: 8pt, fill: gray)
#set par(first-line-indent: 0em)
_Data source: Statistics South Africa, Income and Expenditure Survey 2022/23 (Report P0100). Analysis conducted using nearest-neighbour matching on Mahalanobis distance with the SciPy scientific computing library (v1.17)._
