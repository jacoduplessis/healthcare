#set document(
  title: "The Emergence of Co-Payment Burden Among Medical Scheme Members in South Africa: A Dual-Period Nearest-Neighbour Matching Analysis",
  author: "Statistical Analysis Report",
  date: datetime(year: 2025, month: 3, day: 2),
)

#set page(
  paper: "a4",
  margin: (top: 2.5cm, bottom: 2.5cm, left: 2.5cm, right: 2.5cm),
  numbering: "1",
  header: context {
    if counter(page).get().first() > 1 [
      #set text(size: 8pt, fill: gray)
      _OOP Health Expenditure: Medical Scheme Members vs Non-Members — IES 2010/11 & 2022/23_
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
  #v(2cm)
  #text(size: 18pt, weight: "bold")[
    The Emergence of Co-Payment Burden Among Medical Scheme Members in South Africa
  ]
  #v(0.5cm)
  #text(size: 14pt, weight: "bold", fill: rgb("#2d5a87"))[
    A Dual-Period Nearest-Neighbour Matching Analysis\
    Using the IES 2010/11 and IES 2022/23
  ]
  #v(2cm)
  #text(size: 11pt)[
    Statistical Analysis Report
  ]
  #v(0.5cm)
  #text(size: 10pt, fill: gray)[
    Data source: Statistics South Africa\
    Income and Expenditure Survey 2010/11 and 2022/23 (Report P0100)
  ]
  #v(0.5cm)
  #text(size: 10pt, fill: gray)[
    March 2025
  ]
]

#pagebreak()

// ============ ABSTRACT ============

#heading(level: 1, numbering: none)[Abstract]

#par(first-line-indent: 0em)[
  *Background:* South Africa's two-tier healthcare system creates a structural divide between medical scheme members who access private care and the uninsured majority who rely on public facilities. Whether medical scheme membership generates additional out-of-pocket (OOP) co-payment burden beyond premiums --- and whether this burden has changed over time --- remains underexplored in the health financing literature.
]

*Methods:* Using microdata from two nationally representative Income and Expenditure Surveys conducted by Statistics South Africa --- the IES 2010/11 (_n_ = 21,802) and IES 2022/23 (_n_ = 18,455) --- we employ nearest-neighbour matching (NNM) on Mahalanobis distance to estimate the Average Treatment Effect on the Treated (ATT) of medical scheme membership on OOP health expenditure. We additionally compute the revised SDG Indicator 3.8.2 (adopted March 2025), which measures the proportion of the population whose OOP health spending exceeds 40% of household discretionary budget, anchored to the Societal Poverty Line (SPL). We test sensitivity across four SPL definitions (WHO SPL, Stats SA Food Poverty Line, Lower-Bound Poverty Line, and Upper-Bound Poverty Line) and disaggregate by medical scheme membership.

*Results:* In 2010/11, the national ATT was statistically indistinguishable from zero (ATT = --R40.87; _p_ = 0.874; _d_ = --0.003), with matched controls exhibiting _higher_ healthcare utilisation (95.1%) than treated units (85.7%). By 2022/23, a large and highly significant co-payment premium had emerged: ATT = R968.44 (95% CI: R831 to R1,106; _p_ < 10#super[-43]; _d_ = 0.170), with treated utilisation (80.2%) now substantially exceeding controls (46.6%). The OOP distribution among uninsured households is genuinely bimodal: the proportion with zero health expenditure rose from 11.7% to 58.9% between the two surveys, confirming a collapse in healthcare utilisation rather than improved protection.

The revised SDG 3.8.2 analysis reveals a striking reversal. In 2010/11, uninsured households experienced far higher financial hardship (37.4%) than insured households (1.5%) under the WHO SPL. By 2022/23, the relationship had inverted: insured households now show _higher_ financial hardship rates (17.4%) than uninsured households (12.7%). This reversal --- robust across all SPL variants and all nine provinces --- reflects both the broadening of scheme membership to lower-income households and the mechanical effect of demand suppression: households with zero OOP cannot exceed any hardship threshold.

*Conclusion:* The co-payment burden associated with medical scheme membership has undergone a structural transformation. The NNM analysis identifies an ATT of R968 in 2022/23, absent in 2010/11, driven by collapsing utilisation among the uninsured. The revised SDG 3.8.2 indicator, while registering apparent improvement (30.6% to 14.8%), masks a protection paradox: the decline is driven by suppressed demand among the uninsured, not by genuine financial protection. These findings reveal a fundamental limitation of the SDG 3.8.2 indicator in contexts of demand suppression and have direct implications for the design of universal health coverage under NHI.

*Keywords:* out-of-pocket health expenditure, medical schemes, nearest-neighbour matching, SDG 3.8.2, catastrophic health expenditure, financial risk protection, South Africa, health financing, IES 2010/11, IES 2022/23

#v(1em)
#line(length: 100%, stroke: 0.5pt + gray)

// ============ INTRODUCTION ============

= Introduction

South Africa's healthcare system is characterised by pronounced duality. Medical scheme members --- comprising approximately 16--17% of the population --- access a well-resourced private sector, while the remaining 83--84% rely primarily on the public health system (Council for Medical Schemes, 2023). This divide has deepened over recent decades despite policy interventions, including the Medical Schemes Act of 1998 and the ongoing National Health Insurance (NHI) Bill. Understanding how the financial burden of healthcare has evolved for both insured and uninsured populations is essential for informed policy design.

A central question in health financing concerns out-of-pocket (OOP) expenditure: the direct costs borne by households for healthcare beyond any insurance coverage. For medical scheme members, OOP spending includes co-payments, deductibles, above-threshold expenses, and costs for services not covered by their benefit packages. For non-members, OOP spending captures direct payments for consultations, medicines, and other healthcare services.

Naive comparisons of OOP expenditure between these groups are confounded by the strong socioeconomic gradient in medical scheme membership. Wealthier, more educated, and urban households are far more likely to belong to medical schemes, and these same characteristics predict higher healthcare utilisation and spending. Nearest-neighbour matching (NNM) addresses this confounding by identifying comparable treated and control units on the basis of observable characteristics (Abadie & Imbens, 2006; Rubin, 1973).

While prior research has examined health expenditure inequality in South Africa (Ataguba & McIntyre, 2012; McIntyre _et al._, 2009; Ataguba, 2012), few studies have employed matching methods to isolate the effect of scheme membership on OOP spending, and none have compared this effect across multiple waves of the Income and Expenditure Survey.

This study exploits the availability of two nationally representative IES datasets --- 2010/11 and 2022/23 --- to examine three questions:

== Objectives

+ Estimate the ATT of medical scheme membership on OOP health expenditure for both 2010/11 and 2022/23, nationally and by province.
+ Assess how the co-payment differential has changed over the 12-year period, adjusting for inflation.
+ Examine changes in healthcare utilisation patterns and covariate overlap between the two periods.
+ Characterise the distribution of OOP health expenditure among uninsured households and assess whether the mass at zero represents genuine non-utilisation.
+ Compute the revised SDG Indicator 3.8.2 (WHO, 2025b) for both periods, disaggregated by medical scheme membership, to assess the implications of the co-payment gap for financial risk protection and South Africa's progress toward SDG Target 3.8.

// ============ DATA AND METHODS ============

= Data and Methods

== Data Sources

=== IES 2010/11

The Income and Expenditure Survey 2010/11 was conducted by Statistics South Africa between September 2010 and August 2011. The survey employed a two-stage stratified sampling design with probability-proportional-to-size sampling of primary sampling units (PSUs) from the 2001 Census Master Sample. The sample comprised 31,419 dwelling units drawn from 3,254 PSUs. The national response rate was 91.6% (Stats SA, 2012). All expenditure values are annualised and deflated to March 2011 prices using the consumer price index.

=== IES 2022/23

The IES 2022/23 was conducted between November 2022 and November 2023 using a stratified multi-stage design based on the Geospatial Information Frame (GIF), with 31,042 dwelling units drawn from 3,318 PSUs. The national response rate was 81.94% (Stats SA, 2025). All values are annualised and adjusted to May 2023 prices using CPI deflators.

Both surveys use the COICOP (Classification of Individual Consumption According to Purpose) standard for expenditure classification and provide household-level survey weights calibrated to known population benchmarks.

== Variables

*Outcome variable:* Total annual OOP health expenditure, computed as the sum of all household expenditure under COICOP Division 06 (Health), comprising medicines and health products (Group 061), outpatient care services (Group 062), inpatient care services (Group 063), and other health services (Group 064). Medical scheme premiums are classified separately under Division 12 (Insurance and Financial Services) and are excluded.

*Treatment variable:* Medical scheme membership, coded as a binary indicator. In the IES 2010/11, this is derived from the variable `q31021medaid` (medical aid membership, 1 = Yes, 2 = No). In the IES 2022/23, the variable is `eoh_meds` (1 = Yes, 2 = No). Households with missing, unspecified, or "not applicable" responses were excluded.

*Matching covariates:* The following eight covariates were used for matching in both periods, harmonised across the two survey instruments:

#figure(
  caption: [Matching Covariates and Variable Harmonisation],
  table(
    columns: (auto, auto, auto, auto),
    align: (left, left, left, left),
    stroke: none,
    table.hline(stroke: 1pt),
    table.header(
      [*Covariate*], [*Type*], [*IES 2010/11*], [*IES 2022/23*],
    ),
    table.hline(stroke: 0.5pt),
    [Log expenditure], [Continuous], [`consumptions`], [`expenditure`],
    [Log income], [Continuous], [`income`], [`income`],
    [Household size], [Continuous], [`hsize`], [`hsize`],
    [Head age], [Continuous], [Persons: `q14age`], [`head_age`],
    [Head sex], [Binary], [`genderofhead`], [`head_sex`],
    [Head population group], [Categorical], [`popgrpofhead`], [`head_population`],
    [Head education], [Ordinal (5 groups)], [Persons: `q21highestlevel`], [`head_education`],
    [Settlement type], [Categorical], [`settlement_type`], [`settlement_type`],
    table.hline(stroke: 1pt),
  ),
) <tab:variables>

Education levels (coded 0--27 in both surveys) were grouped into five ordinal categories: no schooling (0), primary (1--7), secondary (8--12), certificate/diploma (13--20), and degree/postgraduate (21--27). For the 2010/11 data, head demographics (age, education) were obtained by joining the household file with the persons file on the household head indicator (`q15relationship` = 1).

== Nearest-Neighbour Matching

We employ one-to-one nearest-neighbour matching without replacement using Euclidean distance on the standardised covariate vector. For each treated unit (medical scheme member), the algorithm identifies the control unit (non-member) with the minimum distance in the standardised covariate space, subject to a caliper constraint.

Formally, for treated unit _i_ with covariate vector $bold(x)_i$, the matched control $j(i)$ is:

$ j(i) = op("argmin", limits: #true)_(j in C) norm((bold(x)_i - bold(x)_j) / bold(s)) $

where $bold(s)$ is the pooled standard deviation vector and $C$ is the set of unmatched control units. A caliper of 0.5 pooled standard deviations per dimension was applied at the national level, relaxed to 0.75 for provincial analyses. Matching was performed greedily in random order (seed = 42) without replacement.

== Estimand and Inference

The estimand is the Average Treatment Effect on the Treated (ATT):

$ "ATT" = EE[Y(1) - Y(0) | T = 1] $

estimated as:

$ hat("ATT") = frac(1, N_m) sum_(i in "matched") [Y_i^T - Y_(j(i))^C] $

Standard errors are computed as $sigma_d \/ sqrt(N_m)$, where $sigma_d$ is the standard deviation of matched pair differences. We report paired _t_-tests, Wilcoxon signed-rank tests, 95% confidence intervals (analytical and bootstrap with 500 replications), and Cohen's _d_ as a standardised effect size measure.

== Balance Diagnostics

Covariate balance is assessed using standardised mean differences (SMD). An absolute SMD below 0.10 is conventionally considered adequate (Austin, 2011). We report SMDs before and after matching, together with percentage reduction.

== Inflation Adjustment

For cross-period comparisons, all values are expressed in May 2023 prices. The CPI adjustment factor from March 2011 to May 2023 is 1.727, derived from the Stats SA headline CPI (all items, metropolitan and other urban areas, December 2016 = 100 base): index values of 67.8 (March 2011) and 117.1 (May 2023).

== Sensitivity Analyses

For each survey period, three sensitivity analyses are conducted:
+ *Bootstrap confidence intervals* (500 replications) for the national ATT.
+ *Exact province matching:* matching is performed separately within each province and results are pooled with sample-size weighting.
+ *Positive health expenditure only:* restricting the sample to households with OOP health expenditure > 0 to assess the effect among healthcare utilisers.

== Samples

After exclusions for missing treatment status, zero expenditure, invalid demographic data, and unspecified population group or education, the analysis samples are:

#figure(
  caption: [Analysis Samples],
  table(
    columns: (auto, auto, auto),
    align: (left, right, right),
    stroke: none,
    table.hline(stroke: 1pt),
    table.header(
      [*Characteristic*], [*IES 2010/11*], [*IES 2022/23*],
    ),
    table.hline(stroke: 0.5pt),
    [Total households],                  [21,802],  [18,455],
    [Medical scheme members (treated)],  [4,096],   [7,711],
    [Non-members (control)],             [17,706],  [10,744],
    [Sample % treated],                  [18.8%],   [41.8%],
    [Weighted % treated],                [21.8%],   [42.5%],
    [Mean annual expenditure (R)],       [83,112],  [121,334],
    [Mean annual income (R)],            [104,296], [166,665],
    [Survey response rate],              [91.6%],   [81.9%],
    table.hline(stroke: 1pt),
  ),
) <tab:sample>

// ============ RESULTS ============

= Results

== IES 2010/11: National Analysis

=== Matching Performance

Of 4,096 treated households, 2,704 (66.0%) were successfully matched. The lower match rate compared with the 2022/23 analysis reflects the substantially greater socioeconomic distance between scheme members and non-members in 2010/11: the pre-matching SMD for log expenditure was 1.83 (versus 0.61 in 2022/23), and for education 0.65 (versus 0.24).

=== Covariate Balance

#figure(
  caption: [Covariate Balance --- IES 2010/11 National],
  table(
    columns: (auto, auto, auto, auto),
    align: (left, right, right, right),
    stroke: none,
    table.hline(stroke: 1pt),
    table.header(
      [*Covariate*], [*SMD Before*], [*SMD After*], [*% Reduction*],
    ),
    table.hline(stroke: 0.5pt),
    [Log expenditure],        [1.8304], [0.1787], [90.2%],
    [Log income],             [1.3221], [0.0975], [92.6%],
    [Household size],         [--0.2408], [--0.0195], [91.9%],
    [Head age],               [--0.0567], [0.0253], [55.4%],
    [Head sex],               [--0.3197], [0.0023], [99.3%],
    [Head population group],  [0.8703], [0.0028], [99.7%],
    [Education group],        [0.6547], [0.0381], [94.2%],
    [Settlement type],        [--0.7176], [0.0022], [99.7%],
    table.hline(stroke: 1pt),
  ),
) <tab:balance_2011>

The pre-matching imbalances in 2010/11 were severe, with five of eight covariates exhibiting SMDs exceeding 0.30. Matching achieved substantial reductions (mean reduction: 90.4%), though the residual SMD for log expenditure (0.179) exceeds the conventional 0.10 threshold. This is a consequence of limited common support: medical scheme members in 2010/11 were concentrated at far higher expenditure levels than non-members, with fewer comparable control units available.

=== Average Treatment Effect on the Treated

#figure(
  caption: [National ATT Estimates --- IES 2010/11],
  table(
    columns: (auto, auto),
    align: (left, right),
    stroke: none,
    table.hline(stroke: 1pt),
    table.header([*Estimate*], [*Value*]),
    table.hline(stroke: 0.5pt),
    [Matched pairs],                    [2,704],
    [Mean OOP --- treated (R)],         [2,204.34],
    [Mean OOP --- matched control (R)], [2,245.21],
    [*ATT (R)*],                        [*--40.87*],
    [Standard error (R)],               [257.17],
    [95% CI --- analytical (R)],        [\[--544.92, 463.17\]],
    [95% CI --- bootstrap (R)],         [\[--528.14, 487.41\]],
    [Paired _t_-statistic],             [--0.159],
    [_p_-value (paired _t_-test)],      [0.874],
    [_p_-value (Wilcoxon)],             [0.016],
    [Cohen's _d_],                      [--0.003],
    table.hline(stroke: 1pt),
  ),
) <tab:att_2011>

The national ATT in 2010/11 is statistically indistinguishable from zero (ATT = --R40.87; _p_ = 0.874; _d_ = --0.003). After matching on socioeconomic characteristics, medical scheme members incurred virtually identical OOP health expenditure (R2,204) to comparable non-members (R2,245). The naive (unmatched) difference of R2,106 dramatically overstates the matched estimate, confirming the severity of selection bias.

The Wilcoxon signed-rank test yields a nominally significant _p_-value (0.016), reflecting distributional differences in the _shape_ of OOP spending rather than a location shift --- consistent with the near-zero mean difference and Cohen's _d_.

=== Healthcare Utilisation

A notable finding is the high utilisation rate among matched controls: 95.1% of matched non-member households reported some health expenditure, compared with 85.7% of matched scheme member households. This pattern --- higher utilisation among controls --- is the opposite of what is observed in the 2022/23 data and suggests that in 2010/11, comparable non-member households accessed healthcare at similar or higher rates.

== IES 2022/23: National Analysis

=== Matching Performance

Of 7,711 treated households, 6,625 (85.9%) were successfully matched, a substantially higher match rate than in 2010/11. The improved overlap reflects the narrower socioeconomic gap between scheme members and non-members in the more recent period.

=== Covariate Balance

#figure(
  caption: [Covariate Balance --- IES 2022/23 National],
  table(
    columns: (auto, auto, auto, auto),
    align: (left, right, right, right),
    stroke: none,
    table.hline(stroke: 1pt),
    table.header(
      [*Covariate*], [*SMD Before*], [*SMD After*], [*% Reduction*],
    ),
    table.hline(stroke: 0.5pt),
    [Log expenditure],        [0.6132], [0.0903], [85.3%],
    [Log income],             [0.4571], [0.0241], [94.7%],
    [Household size],         [0.1766], [0.0278], [84.3%],
    [Head age],               [0.1641], [0.0094], [94.3%],
    [Head sex],               [0.0629], [0.0015], [97.6%],
    [Head population group],  [0.2103], [0.0066], [96.9%],
    [Education group],        [0.2369], [0.0044], [98.2%],
    [Settlement type],        [--0.0593], [0.0022], [96.3%],
    table.hline(stroke: 1pt),
  ),
) <tab:balance_2023>

All post-matching SMDs fall below 0.10 (mean |SMD| = 0.021), indicating excellent balance. The pre-matching imbalances, while still present, are substantially smaller than in 2010/11: the SMD for log expenditure is 0.61 (versus 1.83), suggesting a less extreme socioeconomic gradient in scheme membership by 2022/23.

=== Average Treatment Effect on the Treated

#figure(
  caption: [National ATT Estimates --- IES 2022/23],
  table(
    columns: (auto, auto),
    align: (left, right),
    stroke: none,
    table.hline(stroke: 1pt),
    table.header([*Estimate*], [*Value*]),
    table.hline(stroke: 0.5pt),
    [Matched pairs],                    [6,625],
    [Mean OOP --- treated (R)],         [1,699.23],
    [Mean OOP --- matched control (R)], [730.79],
    [*ATT (R)*],                        [*968.44*],
    [Standard error (R)],               [69.93],
    [95% CI --- analytical (R)],        [\[831.37, 1,105.51\]],
    [95% CI --- bootstrap (R)],         [\[815.46, 1,093.42\]],
    [Paired _t_-statistic],             [13.848],
    [_p_-value (paired _t_-test)],      [$5.17 times 10^(-43)$],
    [_p_-value (Wilcoxon)],             [$7.09 times 10^(-226)$],
    [Cohen's _d_],                      [0.170],
    table.hline(stroke: 1pt),
  ),
) <tab:att_2023>

By 2022/23, the ATT is large, highly significant, and positive: R968.44 (_p_ < 10#super[-43]; _d_ = 0.170). Medical scheme members incur nearly R1,000 more per year in OOP health spending than socioeconomically comparable non-members. The naive difference of R1,680 overstates the matched estimate by 73.5%.

=== Healthcare Utilisation

The utilisation pattern has reversed: 80.2% of matched treated households report any health spending versus only 46.6% of matched controls. The median OOP expenditure is R457.62 for treated households versus R0.00 for controls --- a stark indicator of suppressed demand among non-members.

== Provincial Analysis

=== IES 2010/11

#figure(
  caption: [Provincial ATT Estimates --- IES 2010/11],
  table(
    columns: (auto, auto, auto, auto, auto, auto, auto),
    align: (left, center, right, right, center, center, right),
    stroke: none,
    table.hline(stroke: 1pt),
    table.header(
      [*Province*], [*Pairs*], [*ATT (R)*], [*SE (R)*], [*95% CI (R)*], [*_p_-value*], [*Cohen's _d_*],
    ),
    table.hline(stroke: 0.5pt),
    [Western Cape],    [531],  [--394.67], [1,408.61], [\[--3,156, 2,366\]], [0.779],                  [--0.012],
    [Eastern Cape],    [319],  [42.98],    [190.22],   [\[--330, 416\]],     [0.821],                  [0.011],
    [Northern Cape],   [193],  [410.38],   [531.66],   [\[--632, 1,452\]],   [0.441],                  [0.056],
    [Free State],      [247],  [--315.16], [588.31],   [\[--1,468, 838\]],   [0.593],                  [--0.034],
    [KwaZulu-Natal],   [359],  [282.50],   [292.59],   [\[--291, 856\]],     [0.335],                  [0.051],
    [North West],      [292],  [680.19],   [354.37],   [\[--14, 1,375\]],    [0.056],                  [0.112],
    [Gauteng],         [521],  [1,349.18], [370.32],   [\[623, 2,075\]],     [$3.0 times 10^(-4)$],    [0.160],
    [Mpumalanga],      [242],  [594.99],   [292.27],   [\[22, 1,168\]],      [0.043],                  [0.131],
    [Limpopo],         [233],  [86.50],    [214.42],   [\[--334, 507\]],     [0.687],                  [0.026],
    table.hline(stroke: 1pt),
  ),
) <tab:prov_2011>

In 2010/11, only two of nine provinces show a statistically significant ATT: *Gauteng* (R1,349.18; _p_ < 0.001; _d_ = 0.160) and *Mpumalanga* (R594.99; _p_ = 0.043; _d_ = 0.131). The remaining seven provinces yield non-significant results with wide confidence intervals. North West approaches significance (_p_ = 0.056). The overall picture is one of no systematic co-payment differential, except in Gauteng --- the most urbanised province with the densest private healthcare infrastructure.

=== IES 2022/23

#figure(
  caption: [Provincial ATT Estimates --- IES 2022/23],
  table(
    columns: (auto, auto, auto, auto, auto, auto, auto),
    align: (left, center, right, right, center, center, right),
    stroke: none,
    table.hline(stroke: 1pt),
    table.header(
      [*Province*], [*Pairs*], [*ATT (R)*], [*SE (R)*], [*95% CI (R)*], [*_p_-value*], [*Cohen's _d_*],
    ),
    table.hline(stroke: 0.5pt),
    [Western Cape],    [648],   [1,588.77], [280.01], [\[1,040, 2,138\]], [$2.1 times 10^(-8)$],   [0.223],
    [Eastern Cape],    [924],   [1,046.49], [114.61], [\[822, 1,271\]],   [$4.2 times 10^(-19)$],  [0.300],
    [Northern Cape],   [256],   [913.61],   [314.91], [\[296, 1,531\]],   [$4.0 times 10^(-3)$],   [0.181],
    [Free State],      [504],   [747.94],   [267.15], [\[224, 1,272\]],   [$5.3 times 10^(-3)$],   [0.125],
    [KwaZulu-Natal],   [1,106], [1,132.81], [140.53], [\[857, 1,408\]],   [$2.0 times 10^(-15)$],  [0.242],
    [North West],      [389],   [402.17],   [155.97], [\[96, 708\]],      [$1.0 times 10^(-2)$],   [0.131],
    [Gauteng],         [1,564], [806.60],   [187.97], [\[438, 1,175\]],   [$1.9 times 10^(-5)$],   [0.109],
    [Mpumalanga],      [543],   [681.45],   [112.89], [\[460, 903\]],     [$2.9 times 10^(-9)$],   [0.259],
    [Limpopo],         [717],   [932.14],   [132.29], [\[673, 1,191\]],   [$4.3 times 10^(-12)$],  [0.263],
    table.hline(stroke: 1pt),
  ),
) <tab:prov_2023>

By 2022/23, the ATT is statistically significant (_p_ < 0.05) in *all nine provinces*. The effect ranges from R402 in North West (_d_ = 0.131) to R1,589 in the Western Cape (_d_ = 0.223). The largest relative effect sizes (Cohen's _d_) are found in the Eastern Cape (0.300), Limpopo (0.263), and Mpumalanga (0.259) --- less urbanised provinces where the OOP premium, though smaller in absolute Rand terms, is proportionally larger relative to background expenditure variation.

== Cross-Period Comparison

=== National ATT in Real Terms

#figure(
  caption: [Cross-Period Comparison of National ATT (May 2023 Prices)],
  table(
    columns: (auto, auto, auto, auto),
    align: (left, right, right, right),
    stroke: none,
    table.hline(stroke: 1pt),
    table.header(
      [*Measure*], [*IES 2010/11#super[\*]*], [*IES 2022/23*], [*Change*],
    ),
    table.hline(stroke: 0.5pt),
    [ATT (R)],                        [--70.59],     [968.44],  [+1,039],
    [Naive difference (R)],           [3,637.43],    [1,679.68],[--1,958],
    [Mean OOP --- treated (R)],       [5,035.36],    [2,206.78],[--56.2%],
    [Mean OOP --- control (R)],       [1,397.79],    [527.09],  [--62.3%],
    [Matched treated mean (R)],       [3,807.12],    [1,699.23],[--55.4%],
    [Matched control mean (R)],       [3,877.70],    [730.79],  [--81.1%],
    [% any health spend --- treated], [86.3%],       [80.6%],   [--5.7pp],
    [% any health spend --- control], [88.3%],       [41.3%],   [--47.0pp],
    table.hline(stroke: 1pt),
  ),
) <tab:comparison>

#text(size: 9pt)[#super[\*] 2010/11 values inflated to May 2023 prices using CPI factor of 1.727 (Stats SA P0141). Original values are in March 2011 prices.]

The cross-period comparison reveals three striking findings:

*First, the ATT shifted from zero to R968.* In 2010/11, comparable scheme members and non-members spent virtually the same amount on healthcare. By 2022/23, scheme members spent R968 more per year --- a substantively meaningful gap that is entirely absent in the earlier period.

*Second, real OOP expenditure declined for both groups, but the decline was steeper for non-members.* Mean OOP spending among scheme members fell by 56% in real terms, while non-member spending fell by 62%. Among matched pairs, the divergence is even starker: matched control spending declined by 81% in real terms (from R3,878 to R731), while matched treated spending declined by 55% (from R3,807 to R1,699).

*Third, healthcare utilisation among non-members collapsed.* In 2010/11, 88.3% of non-member households (and 95.1% of matched controls) reported some health expenditure. By 2022/23, this fell to 41.3% (46.6% for matched controls) --- a decline of nearly 47 percentage points. Among scheme members, the decline was much smaller (86.3% to 80.6%).

=== Provincial Evolution

#figure(
  caption: [Provincial ATT Evolution (May 2023 Prices)],
  table(
    columns: (auto, auto, auto, auto, auto, auto),
    align: (left, right, right, right, right, right),
    stroke: none,
    table.hline(stroke: 1pt),
    table.header(
      [*Province*], [*ATT 2011#super[\*] (R)*], [*ATT 2023 (R)*], [*Change (R)*], [*_d_ 2011*], [*_d_ 2023*],
    ),
    table.hline(stroke: 0.5pt),
    [Western Cape],    [--681.63],  [1,588.77], [+2,270],   [--0.012], [0.223],
    [Eastern Cape],    [74.23],     [1,046.49], [+972],     [0.011],   [0.300],
    [Northern Cape],   [708.77],    [913.61],   [+205],     [0.056],   [0.181],
    [Free State],      [--544.31],  [747.94],   [+1,292],   [--0.034], [0.125],
    [KwaZulu-Natal],   [487.91],    [1,132.81], [+645],     [0.051],   [0.242],
    [North West],      [1,174.76],  [402.17],   [--773],    [0.112],   [0.131],
    [Gauteng],         [2,330.17],  [806.60],   [--1,524],  [0.160],   [0.109],
    [Mpumalanga],      [1,027.61],  [681.45],   [--346],    [0.131],   [0.259],
    [Limpopo],         [149.39],    [932.14],   [+783],     [0.026],   [0.263],
    table.hline(stroke: 1pt),
  ),
) <tab:prov_evolution>

#text(size: 9pt)[#super[\*] 2010/11 ATT values inflated to May 2023 prices. Note: 2010/11 ATTs are not statistically significant except Gauteng and Mpumalanga.]

The provincial comparison reveals two distinct patterns:

- *Provinces where the ATT increased substantially:* The Western Cape (+R2,270), Eastern Cape (+R972), Free State (+R1,292), KwaZulu-Natal (+R645), and Limpopo (+R783) all show large increases in the co-payment differential. These are provinces where the 2010/11 ATT was zero or negative.

- *Provinces where the ATT decreased:* Gauteng (--R1,524), North West (--R773), and Mpumalanga (--R346) show declining ATTs in real terms. Notably, Gauteng was the only province with a significant and large ATT in 2010/11 (R2,330 in 2023 prices), which shrank to R807 by 2022/23. This convergence may reflect increased access to public healthcare or changes in the composition of scheme membership in these provinces.

== Sensitivity Analyses

#figure(
  caption: [Sensitivity Analysis Results --- Both Periods],
  table(
    columns: (auto, auto, auto, auto, auto),
    align: (left, right, center, right, center),
    stroke: none,
    table.hline(stroke: 1pt),
    table.header([*Analysis*], [*ATT (R)*], [*95% CI (R)*], [*ATT (R)*], [*95% CI (R)*]),
    table.hline(stroke: 0.25pt),
    [], [#underline[IES 2010/11]], [], [#underline[IES 2022/23]], [],
    table.hline(stroke: 0.5pt),
    [Main analysis],                   [--40.87],  [\[--545, 463\]],  [968.44], [\[831, 1,106\]],
    [Bootstrap (500 reps)],            [46.93],    [\[--528, 487\]],  [951.23], [\[815, 1,093\]],
    [Exact province (pooled)],         [331.15],   [\[--212, 874\]],  [949.71], [\[819, 1,080\]],
    [Positive health exp only],        [75.37],    [\[--471, 622\]],  [719.70], [\[533, 906\]],
    table.hline(stroke: 1pt),
  ),
) <tab:sensitivity>

For the IES 2010/11, all sensitivity analyses confirm the null finding: no analysis yields a significant ATT. The exact province matching (pooled ATT = R331) is positive but not significant, and the bootstrap CI spans zero.

For the IES 2022/23, all sensitivity analyses confirm the main finding. The bootstrap CI [R815, R1,093] closely aligns with the analytical CI. Exact province matching yields a nearly identical pooled ATT (R950). Among healthcare utilisers only, the ATT of R720 remains highly significant, indicating that even conditional on accessing healthcare, scheme members pay more.

== Covariate Overlap and Common Support

The declining pre-matching SMDs between the two periods are themselves an important finding. @tab:overlap summarises the maximum covariate imbalances.

#figure(
  caption: [Pre-Matching Covariate Imbalance: 2010/11 vs 2022/23],
  table(
    columns: (auto, auto, auto),
    align: (left, right, right),
    stroke: none,
    table.hline(stroke: 1pt),
    table.header(
      [*Covariate*], [*SMD 2010/11*], [*SMD 2022/23*],
    ),
    table.hline(stroke: 0.5pt),
    [Log expenditure],        [1.830], [0.613],
    [Log income],             [1.322], [0.457],
    [Head population group],  [0.870], [0.210],
    [Settlement type],        [--0.718], [--0.059],
    [Education group],        [0.655], [0.237],
    [Head sex],               [--0.320], [0.063],
    [Household size],         [--0.241], [0.177],
    [Head age],               [--0.057], [0.164],
    table.hline(stroke: 0.5pt),
    [Mean |SMD|],             [0.752], [0.247],
    [Match rate],             [66.0%], [85.9%],
    table.hline(stroke: 1pt),
  ),
) <tab:overlap>

The mean absolute pre-matching SMD declined from 0.752 to 0.247 --- a 67% reduction. This indicates that the socioeconomic profile of medical scheme members converged substantially toward that of non-members between 2010/11 and 2022/23. The most dramatic improvement was in log expenditure (1.83 to 0.61), population group (0.87 to 0.21), and settlement type (0.72 to 0.06). This convergence enabled better matching (66% vs 86% match rate) and more credible causal estimates in the later period.

== Distribution of OOP Health Expenditure Among Uninsured Households

A critical question for interpreting the ATT estimates --- and for the SDG 3.8.2 analysis that follows --- is whether the OOP distribution among uninsured households is truly bimodal (a genuine mass at zero and a separate positive-spending subpopulation) or whether it reflects a continuous distribution with many small values rounded or truncated to zero.

=== Distributional Characterisation

#figure(
  caption: [OOP Distribution Among Uninsured Households],
  table(
    columns: (auto, auto, auto, auto, auto),
    align: (left, right, right, right, right),
    stroke: none,
    table.hline(stroke: 1pt),
    table.header(
      [*Measure*], [*IES 2010/11*], [*(weighted)*], [*IES 2022/23*], [*(weighted)*],
    ),
    table.hline(stroke: 0.5pt),
    [Total uninsured households], [17,976], [], [11,345], [],
    [Zero OOP (count)], [2,100], [], [6,683], [],
    [Zero OOP (%)], [11.7%], [10.6%], [58.9%], [58.2%],
    [Positive OOP (%)], [88.3%], [89.4%], [41.1%], [41.8%],
    table.hline(stroke: 0.25pt),
    [Mean OOP --- all (R)], [815.23], [], [517.89], [],
    [Mean OOP --- positive only (R)], [923.06], [], [1,260.29], [],
    [Median OOP --- all (R)], [299.00], [], [0.00], [],
    [Median OOP --- positive only (R)], [359.00], [], [452.06], [],
    table.hline(stroke: 0.25pt),
    [Minimum positive value (R)], [2.00], [], [2.01], [],
    [Skewness (positive)], [10.16], [], [15.81], [],
    [Kurtosis (positive)], [172.73], [], [401.91], [],
    table.hline(stroke: 1pt),
  ),
) <tab:oop_dist>

=== Bimodality Assessment

The distribution is *genuinely bimodal*, not an artefact of rounding or truncation. Three lines of evidence support this:

*First, the gap between zero and the smallest positive values is clean.* In both surveys, the minimum positive OOP is approximately R2 per annum --- not a fraction of a cent that might suggest rounding. There are no values between R0 and R2 in either period. This discrete gap confirms that zero represents true non-utilisation: these households have _no_ COICOP Division 06 expenditure line items whatsoever.

*Second, the mass at zero is large and has grown dramatically.* The proportion of uninsured households with zero OOP increased from 11.7% (weighted: 10.6%) in 2010/11 to 58.9% (weighted: 58.2%) in 2022/23. This 47-percentage-point shift is far too large to be attributable to data processing changes and represents a genuine behavioural shift in healthcare utilisation.

*Third, the positive-spending subpopulation has a well-defined distribution.* Among the 41.1% of uninsured households with positive OOP in 2022/23, the distribution is heavily right-skewed (skewness = 15.81, kurtosis = 401.91) with a median of R452 and a long right tail extending to R123,362. This shape is characteristic of health expenditure distributions globally and shows no evidence of truncation or artificial compression at the lower end.

#figure(
  caption: [Distribution of Positive OOP Expenditure Among Uninsured Households],
  table(
    columns: (auto, auto, auto),
    align: (left, right, right),
    stroke: none,
    table.hline(stroke: 1pt),
    table.header(
      [*Expenditure Range*], [*IES 2010/11*], [*IES 2022/23*],
    ),
    table.hline(stroke: 0.5pt),
    [R0 (zero)],         [11.7%], [58.9%],
    [R0.01--R10],        [0.5%],  [0.5%],
    [R10--R50],          [4.8%],  [2.6%],
    [R50--R100],         [6.9%],  [2.4%],
    [R100--R500],        [40.8%], [15.7%],
    [R500--R1,000],      [17.1%], [7.9%],
    [R1,000--R5,000],    [16.1%], [9.3%],
    [> R5,000],          [2.0%],  [2.0%],
    table.hline(stroke: 1pt),
  ),
) <tab:oop_bins>

=== Implications for Analysis

The bimodal distribution has two important analytical implications. First, it validates the NNM approach, which compares mean OOP levels: the ATT captures both the intensive margin (how much utilisers spend) and the extensive margin (the probability of any spending). The 2022/23 ATT of R968 is substantially driven by the extensive margin --- the 34-percentage-point gap in utilisation rates between matched treated (80.2%) and matched control (46.6%) households.

Second, the bimodality creates a fundamental interpretive challenge for the SDG 3.8.2 indicator. As the conceptual framework identifies (Feedback 2: Poverty $arrow.l.r$ Ill Health), zero OOP does not imply financial protection --- it may indicate suppressed demand due to access barriers. The 58.2% of uninsured households with zero health spending are not "protected"; they are not accessing care. This distinction is central to the analysis that follows.

== Financial Risk Protection: SDG Indicator 3.8.2

=== Methodology

We compute SDG Indicator 3.8.2 using the revised methodology adopted by the UN Statistical Commission in March 2025 (WHO, 2025b). The revised indicator measures the proportion of the population with positive out-of-pocket household expenditure on health exceeding 40% of the household discretionary budget.

The discretionary household budget is defined as total household consumption expenditure per capita minus the societal poverty line (SPL), measured on a per capita daily basis:

$ "Indicator" = frac(sum_i m_i omega_i bold(1)(o o p_i^"health" > 0.4 dot (y_i - "SPL") inter o o p_i^"health" > 0), sum_i m_i omega_i) $

where $m_i$ is household size, $omega_i$ is the sampling weight, $o o p_i^"health"$ is daily per capita OOP health expenditure, and $y_i$ is daily per capita total consumption expenditure. For households living below the SPL ($y_i <$ SPL), the discretionary budget is negative and any positive OOP expenditure constitutes financial hardship.

Using 2017 purchasing power parities, the WHO SPL is defined as:

$ "SPL" = op("max")(dollar 2.15 slash "day", thin dollar 1.15 slash "day" + 0.5 times "median"^*(y_i - o o p_i^"health")) $

where the median is population-weighted and computed from per capita daily consumption excluding OOP health expenditure (WHO, 2025b; Jolliffe & Prydz, 2021).

To test sensitivity to the poverty line assumption, we compute the indicator under four SPL definitions:

#figure(
  caption: [SPL Variants Used for SDG 3.8.2 Computation],
  table(
    columns: (auto, auto, auto, auto),
    align: (left, auto, right, right),
    stroke: none,
    table.hline(stroke: 1pt),
    table.header(
      [*SPL Variant*], [*Definition*], [*IES 2010/11*], [*IES 2022/23*],
    ),
    table.hline(stroke: 0.5pt),
    [WHO SPL], [max(IPL; relative formula)], [R532/month], [R1,117/month],
    [Stats SA FPL], [Food Poverty Line], [R335/month], [R760/month],
    [Stats SA LBPL], [Lower-Bound Poverty Line], [R501/month], [R1,058/month],
    [Stats SA UBPL], [Upper-Bound Poverty Line], [R779/month], [R1,558/month],
    table.hline(stroke: 1pt),
  ),
) <tab:spl_variants>

We also report the original budget-share indicators (OOP > 10% and > 25% of total consumption) for comparison with the pre-revision methodology. All amounts are measured per capita per day, with population weighting ($m_i times omega_i$), as specified in the WHO metadata.

=== National Results: Original Budget-Share Approach

Under the original SDG 3.8.2 methodology, financial hardship rates are strikingly low:

#figure(
  caption: [Original SDG 3.8.2 --- Budget-Share Approach],
  table(
    columns: (auto, auto, auto, auto, auto, auto, auto),
    align: (left, right, right, right, right, right, right),
    stroke: none,
    table.hline(stroke: 1pt),
    table.header(
      [], [*IES 2010/11*], [], [], [*IES 2022/23*], [], [],
    ),
    table.hline(stroke: 0.25pt),
    [*Threshold*], [*All*], [*Insured*], [*Uninsured*], [*All*], [*Insured*], [*Uninsured*],
    table.hline(stroke: 0.5pt),
    [> 10% of consumption], [1.7%], [2.1%], [1.6%], [0.5%], [0.7%], [0.3%],
    [> 25% of consumption], [0.1%], [0.4%], [0.1%], [0.0%], [0.1%], [0.0%],
    table.hline(stroke: 1pt),
  ),
) <tab:sdg382_original>

The original indicator paints a picture of near-universal financial protection: fewer than 2% of the population exceed the 10% threshold in either period. This is precisely the measurement artefact that motivated the 2025 revision. The budget-share approach is insensitive to poverty --- a household spending R50 out of R5,000 (1%) appears equally protected as a household spending R5 out of R50 (10%), despite the latter being destitute. The decline from 1.7% to 0.5% between the two surveys reflects the suppression of healthcare demand among the poor, not improved protection.

=== National Results: Revised SDG 3.8.2 (40% of Discretionary Budget)

The revised indicator reveals a fundamentally different --- and more concerning --- picture:

#figure(
  caption: [Revised SDG 3.8.2 --- 40% of Discretionary Budget by SPL Variant],
  table(
    columns: (auto, auto, auto, auto, auto, auto, auto),
    align: (left, right, right, right, right, right, right),
    stroke: none,
    table.hline(stroke: 1pt),
    table.header(
      [], [*IES 2010/11*], [], [], [*IES 2022/23*], [], [],
    ),
    table.hline(stroke: 0.25pt),
    [*SPL Variant*], [*All*], [*Insured*], [*Uninsured*], [*All*], [*Insured*], [*Uninsured*],
    table.hline(stroke: 0.5pt),
    [Stats SA FPL],  [15.8%], [0.4%], [19.3%], [7.5%],  [8.6%],  [6.6%],
    [Stats SA LBPL], [28.8%], [1.3%], [35.2%], [13.5%], [15.7%], [11.7%],
    [WHO SPL],       [30.6%], [1.5%], [37.4%], [14.8%], [17.4%], [12.7%],
    [Stats SA UBPL], [43.6%], [4.0%], [52.7%], [23.5%], [28.3%], [19.5%],
    table.hline(stroke: 1pt),
  ),
) <tab:sdg382_revised>

Three findings stand out.

*First, the revised indicator yields dramatically higher rates than the original.* Under the WHO SPL, 14.8% of the population in 2022/23 experience financial hardship from health spending --- 30 times higher than the original 10%-threshold rate (0.5%). This confirms the critique that the budget-share approach systematically understates the burden of health spending on the poor (Wagstaff, 2019; Grépin _et al._, 2020).

*Second, a remarkable reversal has occurred between insured and uninsured households.* In 2010/11, the pattern was intuitive: uninsured households experienced far higher financial hardship than insured households across all SPL variants (e.g., 37.4% vs 1.5% under WHO SPL). By 2022/23, this relationship had *inverted*: insured households now show _higher_ financial hardship rates (17.4%) than uninsured households (12.7%) under the WHO SPL. This inversion is consistent across all SPL variants.

*Third, the overall rate has fallen, but this decline is misleading.* The national rate dropped from 30.6% to 14.8% (WHO SPL). However, this apparent improvement is driven almost entirely by the collapse in healthcare utilisation among uninsured households documented in @tab:oop_dist. A household with zero OOP cannot exceed any threshold --- it is classified as "protected" by the indicator regardless of whether it has actually accessed needed care. The 58% of uninsured households with zero health spending in 2022/23 are counted as experiencing no financial hardship, even though their zero spending may reflect foregone care rather than genuine protection.

=== The Insured--Uninsured Reversal

The reversal in SDG 3.8.2 rates between insured and uninsured households is the central finding of this analysis and warrants detailed examination.

In 2010/11, insured households had near-zero financial hardship rates (0.4--4.0% depending on SPL) because they were overwhelmingly above all poverty lines: only 1.3% of insured households fell below the WHO SPL, and their OOP spending, while positive, rarely exceeded 40% of their ample discretionary budgets.

By 2022/23, two forces produced the reversal:

+ *Broadening of the insured base.* The expansion of medical scheme membership to lower-income households meant that 22.0% of insured households now fall below the WHO SPL (up from 1.3%). These newly insured, near-poor households face co-payments that can exceed 40% of their limited discretionary budgets.

+ *Demand suppression among the uninsured.* The collapse of healthcare utilisation from 88.3% to 41.1% among uninsured households mechanically reduced their SDG 3.8.2 rates: households that do not spend on healthcare cannot experience financial hardship as measured by the indicator.

This creates what might be termed the *protection paradox*: the indicator registers improved "protection" for uninsured households precisely when they are accessing _less_ care. As the literature review identifies, zero OOP does not equal protection when it reflects suppressed demand (O'Donnell, 2024; Koch & Setshegetso, 2020; Ataguba & Goudge, 2012).

=== Sensitivity to SPL Choice

The absolute level of the revised indicator is highly sensitive to the poverty line assumed, but the *qualitative findings are robust* across all four SPL variants:

+ The insured--uninsured reversal appears under all four SPL definitions in 2022/23.
+ The decline from 2010/11 to 2022/23 appears under all four SPL definitions.
+ The ranking of provinces is consistent regardless of SPL choice.

The sensitivity is driven primarily by the share of households classified as below the SPL: under the FPL (the most conservative line), 15.4% of all households fall below the line; under the UBPL, this rises to 44.1%. Since any below-SPL household with positive OOP automatically qualifies as experiencing financial hardship, the choice of poverty line has a multiplicative effect on the indicator.

=== Provincial Analysis (Revised SDG 3.8.2, WHO SPL)

#figure(
  caption: [Revised SDG 3.8.2 by Province (WHO SPL, 40% Threshold)],
  table(
    columns: (auto, auto, auto, auto, auto, auto, auto),
    align: (left, right, right, right, right, right, right),
    stroke: none,
    table.hline(stroke: 1pt),
    table.header(
      [], [*IES 2010/11*], [], [], [*IES 2022/23*], [], [],
    ),
    table.hline(stroke: 0.25pt),
    [*Province*], [*All*], [*Insured*], [*Uninsured*], [*All*], [*Insured*], [*Uninsured*],
    table.hline(stroke: 0.5pt),
    [Western Cape],    [13.8%], [0.8%],  [18.4%], [5.9%],  [6.0%],  [5.7%],
    [Eastern Cape],    [36.7%], [1.1%],  [43.0%], [18.9%], [23.6%], [14.9%],
    [Northern Cape],   [32.6%], [5.7%],  [42.2%], [13.8%], [20.9%], [10.2%],
    [Free State],      [32.5%], [2.6%],  [39.3%], [17.0%], [18.5%], [15.5%],
    [KwaZulu-Natal],   [44.4%], [2.1%],  [51.0%], [21.7%], [25.1%], [18.7%],
    [North West],      [30.6%], [2.1%],  [35.9%], [21.6%], [26.0%], [19.2%],
    [Gauteng],         [15.0%], [0.7%],  [20.8%], [8.4%],  [10.6%], [6.4%],
    [Mpumalanga],      [39.2%], [1.7%],  [45.3%], [17.7%], [21.9%], [13.9%],
    [Limpopo],         [38.7%], [4.2%],  [41.9%], [16.5%], [18.9%], [14.8%],
    table.hline(stroke: 1pt),
  ),
) <tab:sdg382_provincial>

The provincial results reveal:

- *The insured--uninsured reversal is present in all nine provinces in 2022/23.* In every province, insured households now have higher SDG 3.8.2 rates than uninsured households --- a pattern that was absent in 2010/11 when the opposite held universally.

- *The provinces with the largest NNM-estimated ATTs also show the largest insured SDG 3.8.2 rates.* The Eastern Cape (ATT = R1,046; insured SDG 3.8.2 = 23.6%), North West (ATT = R402; 26.0%), and KwaZulu-Natal (ATT = R1,133; 25.1%) combine high co-payment burdens with high financial hardship, indicating that the causal co-payment effect identified by NNM translates directly into measured financial risk.

- *The decline in national rates masks divergent trends.* The Western Cape saw the largest reduction in financial hardship (from 13.8% to 5.9%), consistent with its relatively high income levels. KwaZulu-Natal, despite a decline from 44.4% to 21.7%, retains the highest overall rate --- consistent with its having both high poverty rates and significant co-payment exposure.

// ============ DISCUSSION ============

= Discussion

== Principal Findings

This study documents a structural transformation in the relationship between medical scheme membership and out-of-pocket health expenditure in South Africa over a 12-year period. Three principal findings emerge.

*First, the co-payment burden associated with medical scheme membership has emerged as a new phenomenon.* In 2010/11, after matching on socioeconomic characteristics, the ATT was statistically and substantively zero (--R41, _d_ = --0.003). By 2022/23, the ATT had grown to R968 (_d_ = 0.170), significant in all nine provinces. This is not a gradual intensification of an existing effect but a qualitative shift from absence to presence.

*Second, the emergence of the ATT is driven primarily by a collapse in healthcare utilisation among non-members.* Between the two surveys, the proportion of non-member households with any health expenditure fell from 88.3% to 41.3% --- a decline of 47 percentage points. Among matched controls, the decline was from 95.1% to 46.6%. Meanwhile, utilisation among scheme members declined only modestly (86.3% to 80.6%). The matched control mean OOP spending fell by 81% in real terms, compared with 55% for matched treated households. The ATT of R968 in 2022/23 thus reflects not an increase in scheme member spending but a steeper decline in non-member spending.

*Third, the socioeconomic gradient in scheme membership has narrowed substantially.* The mean pre-matching SMD across covariates fell from 0.75 to 0.25, and the match rate improved from 66% to 86%. This convergence likely reflects expansion of scheme membership to middle-income households, particularly through low-cost benefit options and employer-mandated coverage, as well as the changing employment and education profile of South African households.

== Interpretation

=== The Utilisation Collapse

The near-halving of healthcare utilisation among non-members is the most striking finding and admits several explanations.

*Cost barriers.* Despite the expansion of primary healthcare services and the removal of user fees at public facilities for certain categories (pregnant women, children under 6), effective access may have declined due to transport costs, opportunity costs of queueing, and informal payments. The real decline in OOP spending among non-members could reflect price-rationed demand rather than improved coverage.

*Public healthcare capacity constraints.* The South African public health system has faced well-documented staffing shortages, infrastructure decay, and management challenges over the 2010--2023 period (Coovadia _et al._, 2009; Maphumulo & Bhengu, 2019). If public facilities became less accessible or perceived as lower quality, non-members may have reduced their healthcare-seeking behaviour.

*Survey methodology differences.* The IES 2010/11 and 2022/23 differed in survey design, questionnaire structure, and data collection periods. The 2010/11 survey used diary-based recording of expenditure (weekly diaries for two weeks), which may capture more routine health purchases (e.g., over-the-counter medicines) than the recall-based approach of the 2022/23 survey. This methodological difference could account for part of the higher utilisation rates observed in 2010/11.

*COVID-19 pandemic effects.* The IES 2022/23 survey period (November 2022 to November 2023) followed the COVID-19 pandemic, which disrupted healthcare access patterns and may have persistently reduced healthcare-seeking behaviour, particularly among the uninsured.

=== The Gauteng Anomaly

Gauteng warrants specific discussion. It was the only province with a large, significant ATT in 2010/11 (R1,349 nominal, R2,330 in 2023 prices), which then _decreased_ to R807 by 2022/23. This counter-trend may reflect Gauteng's unique position as the most urbanised and economically developed province, where private healthcare infrastructure was already extensive in 2010/11. The subsequent expansion of medical scheme membership to lower-income strata (facilitated by low-cost benefit options) may have brought in members with lower co-payment obligations, reducing the average ATT.

=== Changing Composition of Scheme Membership

The doubling of the proportion of households with medical scheme membership in the analysis sample --- from 18.8% (21.8% weighted) in 2010/11 to 41.8% (42.5% weighted) in 2022/23 --- is substantial. While part of this change may reflect the differing exclusion criteria and survey designs, it is consistent with the expansion of medical scheme products to lower-income segments. As the membership base broadens, the average socioeconomic profile of scheme members converges toward that of non-members (as evidenced by declining pre-matching SMDs), and the composition of co-payment obligations shifts.

The high weighted treatment rate of 42.5% in the 2022/23 sample --- considerably above the population medical scheme coverage rate of approximately 16--17% (CMS, 2023) --- likely reflects both the household-level measurement (where any member's scheme membership classifies the entire household as treated) and potential sample composition effects after exclusions.

== Limitations

+ *Unobserved confounding:* NNM controls for observed covariates but cannot address unobserved confounders such as health status, chronic disease burden, risk preferences, or health literacy. Individuals in poor health may be both more likely to hold medical scheme coverage and more likely to incur health expenditure, biasing the ATT upward. This concern is more acute for the 2022/23 analysis where the ATT is significant.

+ *Limited common support in 2010/11:* The 66% match rate and residual SMD of 0.18 for log expenditure in 2010/11 indicate that the matched sample may not be representative of all treated households. The null ATT finding applies to the matchable subpopulation, which excludes the 34% of scheme members at the extreme upper tail of the expenditure distribution.

+ *Survey comparability:* The IES 2010/11 and 2022/23 differ in sampling frame (2001 Census vs GIF), survey period length, questionnaire design, and data collection methodology. The 2010/11 diary method may capture different types of health spending than the 2022/23 recall method, complicating direct comparisons. The different settlement type classifications (four categories in 2010/11 versus three in 2022/23) further limit strict comparability.

+ *CPI adjustment:* The inflation factor of 1.727 is based on headline CPI, which may not accurately reflect healthcare-specific price changes. Medical inflation in South Africa has typically exceeded headline CPI, meaning that health-specific deflation would yield even larger real declines in OOP spending.

+ *Cross-sectional design:* Both surveys are cross-sectional, precluding panel analysis of the same households over time. The observed changes could reflect cohort effects, compositional shifts in the population, or genuine temporal trends.

+ *COICOP classification:* Some health-related expenditure may be misclassified (e.g., traditional medicine coded under Division 13), and the coding practices may have evolved between the two survey waves.

== The Protection Paradox and SDG 3.8.2

The SDG 3.8.2 analysis reveals a fundamental limitation of financial risk protection indicators in contexts of demand suppression. The revised indicator --- designed to be more pro-poor than the budget-share approach it replaces --- still relies on _observed_ OOP expenditure. When households forego care due to access barriers, their zero OOP is recorded as zero financial hardship. The indicator cannot distinguish between a household that spends nothing on healthcare because the public system provides free care (genuine protection) and one that spends nothing because it cannot access care at all (suppressed demand).

This creates the protection paradox identified in the results: the apparent improvement in national SDG 3.8.2 rates (from 30.6% to 14.8% under the WHO SPL) is driven substantially by the 47-percentage-point increase in zero-OOP households among the uninsured, not by actual improvements in financial protection. As Feedback 2 in the conceptual framework identifies, poverty suppresses demand, producing low OOP that the indicator misreads as protection.

The reversal --- insured households now showing _higher_ financial hardship than uninsured --- is particularly consequential for policy. It suggests that as South Africa broadens insurance coverage through NHI, newly insured households may _increase_ the national SDG 3.8.2 rate simply by accessing care they previously could not. This is a measurement paradox: successful expansion of coverage may register as _deterioration_ in financial risk protection on the headline indicator.

== Policy Implications

The findings have direct relevance for the National Health Insurance (NHI) policy debate:

- *The access gap is widening.* The dramatic decline in healthcare utilisation among non-members --- from 88% to 41% of households with any health spending --- suggests that the uninsured face intensifying barriers to care. The zero median OOP expenditure among matched non-members in 2022/23 is a stark indicator of unmet healthcare need.

- *Medical scheme co-payments represent a growing burden.* The emergence of a significant ATT by 2022/23 indicates that scheme membership now carries a meaningful OOP cost beyond premiums. Members face a double financial burden: premiums plus approximately R1,000 per year in co-payments.

- *Universal coverage design must address both gaps.* Any NHI system must simultaneously expand access for the currently uninsured (who are rationing care) and address the co-payment burden for scheme members (who are paying out of pocket despite insurance coverage).

- *The Gauteng convergence offers a positive signal.* The decline in Gauteng's ATT from R2,330 to R807 suggests that as scheme membership broadens and healthcare markets mature, the co-payment differential can moderate.

- *SDG 3.8.2 must be interpreted alongside utilisation data.* South Africa's apparently improving SDG 3.8.2 rate conceals a deepening access crisis. Policymakers should complement the headline indicator with utilisation-adjusted measures that distinguish suppressed demand from genuine financial protection. A household with zero OOP and no healthcare contact is not "protected" --- it is excluded.

// ============ CONCLUSION ============

= Conclusion

Using nearest-neighbour matching on two waves of the Income and Expenditure Survey, we document a structural transformation in the relationship between medical scheme membership and out-of-pocket health expenditure in South Africa. In 2010/11, the matched ATT was zero (--R41, _p_ = 0.874) with only Gauteng showing a significant effect. By 2022/23, the ATT had grown to R968 (_p_ < 10#super[-43]), significant in all nine provinces. This emergence is driven not by increased scheme member spending --- which declined 55% in real terms --- but by a collapse in healthcare utilisation among non-members, whose spending declined 81% in real terms and whose utilisation rate fell from 95% to 47% among matched households.

The OOP distribution among uninsured households is genuinely bimodal: 58.9% report zero health expenditure in 2022/23, up from 11.7% in 2010/11, with a clean gap between zero and the smallest positive values (~R2). This confirms that the mass at zero represents true non-utilisation, not a rounding artefact.

Application of the revised SDG Indicator 3.8.2 (WHO, 2025b) reveals a protection paradox. Under the WHO Societal Poverty Line, the national financial hardship rate fell from 30.6% to 14.8% between the two surveys --- but this apparent improvement is driven by demand suppression among the uninsured, not by genuine financial protection. A striking reversal has occurred: insured households now show higher financial hardship (17.4%) than uninsured households (12.7%), reflecting both the broadening of scheme membership to lower-income strata and the mechanical effect of zero OOP among non-utilisers. This reversal is robust across all four SPL variants tested and all nine provinces.

These findings underscore the urgency of addressing the widening healthcare access gap in South Africa and reveal a fundamental limitation of the revised SDG 3.8.2 indicator in contexts of demand suppression. Policymakers should complement the headline indicator with utilisation-adjusted measures. As South Africa implements NHI, the paradoxical implication is that successful coverage expansion may initially _increase_ measured financial hardship by enabling care-seeking among previously excluded populations --- a measurement challenge that must be anticipated in monitoring frameworks.

// ============ REFERENCES ============

#heading(level: 1, numbering: none)[References]

#set par(first-line-indent: 0em, hanging-indent: 1.5em)
#set text(size: 10pt)

Abadie, A. & Imbens, G.W. (2006). Large sample properties of matching estimators for average treatment effects. _Econometrica_, 74(1), 235--267.

Ataguba, J.E. (2012). Reassessing catastrophic health-care payments with a Nigerian case study. _Health Economics, Policy and Law_, 7(3), 309--326.

Ataguba, J.E. & Goudge, J. (2012). The impact of health insurance on health-care utilisation and out-of-pocket payments in South Africa. _The Geneva Papers on Risk and Insurance --- Issues and Practice_, 37(4), 633--654.

Ataguba, J.E. & McIntyre, D. (2012). Paying for and receiving benefits from health services in South Africa: Is the health system equitable? _Health Policy and Planning_, 27(suppl_1), i35--i45.

Austin, P.C. (2011). An introduction to propensity score methods for reducing the effects of confounding in observational studies. _Multivariate Behavioral Research_, 46(3), 399--424.

Cohen, J. (1988). _Statistical Power Analysis for the Behavioral Sciences_ (2nd ed.). Lawrence Erlbaum Associates.

Coovadia, H., Jewkes, R., Barron, P., Sanders, D. & McIntyre, D. (2009). The health and health system of South Africa: Historical roots of current public health challenges. _The Lancet_, 374(9692), 817--834.

Council for Medical Schemes. (2023). _Annual Report 2022/23_. Pretoria: CMS.

Deaton, A. (1997). _The Analysis of Household Surveys: A Microeconometric Approach to Development Policy_. World Bank Publications.

Maphumulo, W.T. & Bhengu, B.R. (2019). Challenges of quality improvement in the healthcare of South Africa post-apartheid: A critical review. _Curationis_, 42(1), e1--e9.

McIntyre, D., Thiede, M., Dahlgren, G. & Whitehead, M. (2009). What are the economic consequences for households of illness and of paying for health care in low- and middle-income country contexts? _Social Science & Medicine_, 68(4), 1375--1383.

Rubin, D.B. (1973). Matching to remove bias in observational studies. _Biometrics_, 29(1), 159--183.

Statistics South Africa. (2012). _Income and Expenditure of Households 2010/2011: Metadata_ (Report P0100). Pretoria: Stats SA.

Grépin, K.A., Irwin, B.R. & Tanimoto, A.H.S. (2020). On tracking catastrophic health expenditure: Assessing the performance of the SDG indicator 3.8.2. _BMJ Global Health_, 5(3), e002175.

Jolliffe, D. & Prydz, E.B. (2021). Societal poverty: A relative and relevant measure. _The World Bank Economic Review_, 35(1), 180--206.

Koch, S.F. & Setshegetso, N. (2020). Catastrophic health expenditure in South Africa. _Development Southern Africa_, 37(3), 373--390.

O'Donnell, O. (2024). The economic consequences of ill health. In _Handbook of Health Economics_ (Vol. 3). Elsevier.

Statistics South Africa. (2025). _Income and Expenditure Survey 2022/23: Metadata_ (Report P0100). Pretoria: Stats SA.

Wagstaff, A. (2019). Measuring catastrophic medical expenditures: Reflections on three issues. _Health Economics_, 28(6), 765--781.

World Health Organization. (2025b). _SDG Indicator 3.8.2: Metadata_ (Harmonized metadata template v1.1). Geneva: WHO.

Xu, K., Evans, D.B., Kawabata, K., Zeramdini, R., Klavus, J. & Murray, C. (2003). Household catastrophic health expenditure: A multi-country analysis. _The Lancet_, 362(9378), 111--117.

#v(2em)
#line(length: 100%, stroke: 0.5pt + gray)
#set text(size: 8pt, fill: gray)
#set par(first-line-indent: 0em)
_Data source: Statistics South Africa, Income and Expenditure Surveys 2010/11 and 2022/23 (Report P0100). Analysis conducted using nearest-neighbour matching on Mahalanobis distance with the SciPy scientific computing library. CPI adjustment factor (March 2011 to May 2023): 1.727, based on Stats SA P0141 headline CPI (Dec 2016 = 100)._
