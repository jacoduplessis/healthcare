"""
SDG 3.8.2 and OOP Distribution Analysis
========================================
Computes:
1. OOP distribution characterisation for uninsured households (both periods)
2. Original SDG 3.8.2 (10% and 25% budget-share thresholds)
3. Revised SDG 3.8.2 (40% discretionary budget, SPL-anchored)
   - WHO SPL formula: max(IPL_local, $1.15_local + 0.5 * median(consumption_excl_oop))
   - Stats SA Food Poverty Line (FPL)
   - Stats SA Lower-Bound Poverty Line (LBPL)
   - Stats SA Upper-Bound Poverty Line (UBPL)

All amounts are per capita daily as per WHO methodology.
Disaggregated by medical scheme membership and survey period.

Outputs: analysis_sdg382_results.json
"""

import json
import sqlite3
import sys

import numpy as np
from scipy import stats as spstats

DB_2023 = "../ies2023.db"
DB_2011 = "../ies2011.db"

# ---------------------------------------------------------------------------
# PPP and CPI conversion parameters
# ---------------------------------------------------------------------------
# 2017 PPP conversion factor for South Africa (private consumption, LCU per intl $)
# Source: World Bank International Comparison Program
PPP_2017 = 6.14

# CPI indices (Stats SA P0141, Dec 2016 = 100 base)
CPI_2017_AVG = 105.2   # 2017 annual average
CPI_MAR_2011 = 67.8    # March 2011
CPI_MAY_2023 = 117.1   # May 2023

# International poverty line in 2017 PPP$
IPL_PPP = 2.15   # $/day
RELATIVE_BASE_PPP = 1.15  # $/day (for SPL formula)

# Convert PPP amounts to local currency at survey prices
def ppp_to_local(ppp_amount, cpi_survey):
    """Convert 2017 PPP$ daily amount to local currency at survey prices."""
    local_2017 = ppp_amount * PPP_2017
    return local_2017 * (cpi_survey / CPI_2017_AVG)

# IPL and relative base in local currency
IPL_2023 = ppp_to_local(IPL_PPP, CPI_MAY_2023)     # ~R14.69/day
IPL_2011 = ppp_to_local(IPL_PPP, CPI_MAR_2011)     # ~R8.51/day
REL_BASE_2023 = ppp_to_local(RELATIVE_BASE_PPP, CPI_MAY_2023)  # ~R7.86/day
REL_BASE_2011 = ppp_to_local(RELATIVE_BASE_PPP, CPI_MAR_2011)  # ~R4.55/day

# ---------------------------------------------------------------------------
# Stats SA National Poverty Lines (per person per month)
# Source: Stats SA Statistical Release P0310.1
# ---------------------------------------------------------------------------
# 2023 prices (April 2023, close to May 2023 survey reference)
FPL_2023_MONTHLY = 760     # Food Poverty Line
LBPL_2023_MONTHLY = 1058   # Lower-Bound Poverty Line
UBPL_2023_MONTHLY = 1558   # Upper-Bound Poverty Line

# 2011 prices (March 2011 reference)
FPL_2011_MONTHLY = 335
LBPL_2011_MONTHLY = 501
UBPL_2011_MONTHLY = 779

# Convert monthly per-capita to daily
DAYS_PER_MONTH = 365.25 / 12  # 30.4375

FPL_2023 = FPL_2023_MONTHLY / DAYS_PER_MONTH
LBPL_2023 = LBPL_2023_MONTHLY / DAYS_PER_MONTH
UBPL_2023 = UBPL_2023_MONTHLY / DAYS_PER_MONTH

FPL_2011 = FPL_2011_MONTHLY / DAYS_PER_MONTH
LBPL_2011 = LBPL_2011_MONTHLY / DAYS_PER_MONTH
UBPL_2011 = UBPL_2011_MONTHLY / DAYS_PER_MONTH

PROVINCE_NAMES = {
    1: "Western Cape", 2: "Eastern Cape", 3: "Northern Cape",
    4: "Free State", 5: "KwaZulu-Natal", 6: "North West",
    7: "Gauteng", 8: "Mpumalanga", 9: "Limpopo",
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_data_2023():
    """Load IES 2022/23 household data with per-capita daily values."""
    conn = sqlite3.connect(DB_2023)
    rows = conn.execute("""
        SELECT
            h.uqno,
            h.eoh_meds,
            CAST(h.expenditure AS REAL) AS expenditure,
            CAST(h.hsize AS INTEGER) AS hsize,
            COALESCE(th.health_exp, 0) AS health_exp,
            CAST(h.hhold_wgt AS REAL) AS hhold_wgt,
            g.province
        FROM households h
        JOIN geography g ON h.uqno = g.uqno
        LEFT JOIN (
            SELECT uqno, SUM(valueannualized_adj) AS health_exp
            FROM total WHERE division = '06'
            GROUP BY uqno
        ) th ON h.uqno = th.uqno
        WHERE h.eoh_meds IN ('1', '2')
          AND CAST(h.expenditure AS REAL) > 0
          AND CAST(h.hsize AS INTEGER) > 0
    """).fetchall()
    conn.close()
    return _build_arrays(rows, is_2023=True)


def load_data_2011():
    """Load IES 2010/11 household data with per-capita daily values."""
    conn = sqlite3.connect(DB_2011)
    rows = conn.execute("""
        SELECT
            h.uqno,
            h.q31021medaid,
            CAST(h.consumptions AS REAL) AS expenditure,
            CAST(h.hsize AS INTEGER) AS hsize,
            COALESCE(th.health_exp, 0) AS health_exp,
            CAST(h.full_calwgt AS REAL) AS hhold_wgt,
            h.province
        FROM households h
        LEFT JOIN (
            SELECT uqno, SUM(valueannualized) AS health_exp
            FROM total WHERE division = '06'
            GROUP BY uqno
        ) th ON h.uqno = th.uqno
        WHERE h.q31021medaid IN ('1', '2')
          AND CAST(h.consumptions AS REAL) > 0
          AND CAST(h.hsize AS INTEGER) > 0
    """).fetchall()
    conn.close()
    return _build_arrays(rows, is_2023=False)


def _build_arrays(rows, is_2023):
    """Convert rows to numpy arrays with per-capita daily values."""
    n = len(rows)
    treated = np.zeros(n, dtype=int)
    expenditure_annual = np.zeros(n)
    hsize = np.zeros(n, dtype=int)
    health_exp_annual = np.zeros(n)
    weight = np.zeros(n)
    province = np.zeros(n, dtype=int)

    for i, row in enumerate(rows):
        treated[i] = 1 if str(row[1]) == "1" else 0
        expenditure_annual[i] = float(row[2])
        hsize[i] = int(row[3])
        health_exp_annual[i] = float(row[4])
        weight[i] = float(row[5])
        province[i] = int(row[6])

    # Per capita daily values (as per SDG 3.8.2 methodology)
    pc_consumption_daily = expenditure_annual / hsize / 365.0
    pc_oop_daily = health_exp_annual / hsize / 365.0
    pc_consumption_excl_oop_daily = pc_consumption_daily - pc_oop_daily

    # Population weight = household weight * household size
    pop_weight = weight * hsize

    return {
        "treated": treated,
        "hsize": hsize,
        "expenditure_annual": expenditure_annual,
        "health_exp_annual": health_exp_annual,
        "weight": weight,
        "pop_weight": pop_weight,
        "province": province,
        "pc_consumption_daily": pc_consumption_daily,
        "pc_oop_daily": pc_oop_daily,
        "pc_consumption_excl_oop_daily": pc_consumption_excl_oop_daily,
        "n": n,
    }


# ---------------------------------------------------------------------------
# WHO SPL computation
# ---------------------------------------------------------------------------
def compute_who_spl(data, ipl_local, rel_base_local):
    """
    Compute WHO Societal Poverty Line from data.
    SPL = max(IPL_local, rel_base_local + 0.5 * median*(consumption_excl_oop))
    The median is weighted.
    """
    # Weighted median of per capita daily consumption excluding OOP
    values = data["pc_consumption_excl_oop_daily"]
    weights = data["pop_weight"]

    # Sort by value
    sorted_idx = np.argsort(values)
    sorted_vals = values[sorted_idx]
    sorted_wts = weights[sorted_idx]

    # Cumulative weight
    cum_wt = np.cumsum(sorted_wts)
    total_wt = cum_wt[-1]
    median_idx = np.searchsorted(cum_wt, total_wt / 2)
    weighted_median = sorted_vals[min(median_idx, len(sorted_vals) - 1)]

    spl = max(ipl_local, rel_base_local + 0.5 * weighted_median)
    return spl, weighted_median


# ---------------------------------------------------------------------------
# OOP Distribution Analysis
# ---------------------------------------------------------------------------
def analyze_oop_distribution(data, label):
    """Characterize OOP distribution for uninsured households."""
    mask = data["treated"] == 0
    oop = data["health_exp_annual"][mask]
    wt = data["weight"][mask]

    n_total = int(mask.sum())
    n_zero = int((oop == 0).sum())
    n_positive = n_total - n_zero

    # Weighted proportions
    wt_total = wt.sum()
    wt_zero = wt[oop == 0].sum()
    wt_positive = wt[oop > 0].sum()

    pos = oop[oop > 0]
    pos_wt = wt[oop > 0]

    # Weighted mean and percentiles for positive values
    wt_mean_all = float(np.average(oop, weights=wt))
    wt_mean_pos = float(np.average(pos, weights=pos_wt)) if len(pos) > 0 else 0

    # Unweighted descriptives
    mean_all = float(oop.mean())
    mean_pos = float(pos.mean()) if len(pos) > 0 else 0
    median_all = float(np.median(oop))
    median_pos = float(np.median(pos)) if len(pos) > 0 else 0

    # Distribution bins
    bins = [
        (0, 0, "Zero"),
        (0.01, 10, "R0.01–R10"),
        (10.01, 50, "R10–R50"),
        (50.01, 100, "R50–R100"),
        (100.01, 500, "R100–R500"),
        (500.01, 1000, "R500–R1,000"),
        (1000.01, 5000, "R1,000–R5,000"),
        (5000.01, float("inf"), ">R5,000"),
    ]
    distribution = []
    for lo, hi, lbl in bins:
        if lbl == "Zero":
            m = oop == 0
        else:
            m = (oop > lo - 0.01) & (oop <= hi)
        distribution.append({
            "bin": lbl,
            "count": int(m.sum()),
            "pct": round(100 * m.sum() / n_total, 1),
            "weighted_pct": round(100 * wt[m].sum() / wt_total, 1),
        })

    # Percentiles of positive values
    percentiles = {}
    if len(pos) > 0:
        for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]:
            percentiles[f"p{p}"] = round(float(np.percentile(pos, p)), 2)

    # Skewness and kurtosis of positive values
    skew_pos = float(spstats.skew(pos)) if len(pos) > 10 else None
    kurt_pos = float(spstats.kurtosis(pos)) if len(pos) > 10 else None

    # Min positive value (to check for rounding)
    min_positive = round(float(pos.min()), 4) if len(pos) > 0 else None

    # Also compute for insured
    mask_ins = data["treated"] == 1
    oop_ins = data["health_exp_annual"][mask_ins]
    wt_ins = data["weight"][mask_ins]
    n_ins = int(mask_ins.sum())
    n_zero_ins = int((oop_ins == 0).sum())

    return {
        "label": label,
        "uninsured": {
            "n_total": n_total,
            "n_zero": n_zero,
            "n_positive": n_positive,
            "pct_zero": round(100 * n_zero / n_total, 1),
            "pct_positive": round(100 * n_positive / n_total, 1),
            "weighted_pct_zero": round(100 * wt_zero / wt_total, 1),
            "weighted_pct_positive": round(100 * wt_positive / wt_total, 1),
            "mean_all": round(mean_all, 2),
            "mean_positive": round(mean_pos, 2),
            "weighted_mean_all": round(wt_mean_all, 2),
            "weighted_mean_positive": round(wt_mean_pos, 2),
            "median_all": round(median_all, 2),
            "median_positive": round(median_pos, 2),
            "min_positive": min_positive,
            "skewness_positive": round(skew_pos, 2) if skew_pos else None,
            "kurtosis_positive": round(kurt_pos, 2) if kurt_pos else None,
            "distribution": distribution,
            "percentiles": percentiles,
        },
        "insured": {
            "n_total": n_ins,
            "n_zero": n_zero_ins,
            "pct_zero": round(100 * n_zero_ins / n_ins, 1) if n_ins > 0 else None,
            "pct_positive": round(100 * (n_ins - n_zero_ins) / n_ins, 1) if n_ins > 0 else None,
            "mean_all": round(float(oop_ins.mean()), 2) if n_ins > 0 else None,
            "mean_positive": round(float(oop_ins[oop_ins > 0].mean()), 2) if (oop_ins > 0).sum() > 0 else None,
        },
    }


# ---------------------------------------------------------------------------
# SDG 3.8.2 computation
# ---------------------------------------------------------------------------
def compute_sdg382(data, spl_value, spl_label, mask=None):
    """
    Compute SDG 3.8.2 indicator.

    Revised (40% discretionary budget):
      Indicator = Σ m_i ω_i 1(oop > 0.4*(y - SPL) AND oop > 0) / Σ m_i ω_i
      where y = per capita daily consumption, SPL = poverty line per capita daily

    For households below SPL (y < SPL), discretionary budget is negative,
    so any positive OOP exceeds 40% of it → counts as financial hardship.

    Original (budget share):
      10%: oop / consumption > 0.10
      25%: oop / consumption > 0.25
    """
    if mask is None:
        mask = np.ones(data["n"], dtype=bool)

    oop = data["pc_oop_daily"][mask]
    y = data["pc_consumption_daily"][mask]
    pop_wt = data["pop_weight"][mask]

    total_pop = pop_wt.sum()

    # Revised SDG 3.8.2: 40% of discretionary budget
    discretionary = y - spl_value
    # Financial hardship: OOP > 0 AND OOP > 0.4 * discretionary budget
    # When discretionary < 0, 0.4 * discretionary < 0, so any OOP > 0 qualifies
    hardship_40 = (oop > 0) & (oop > 0.4 * discretionary)
    rate_40 = float((pop_wt[hardship_40]).sum() / total_pop * 100)

    # Count households below SPL
    below_spl = y < spl_value
    n_below = int(below_spl.sum())
    pct_below = float(pop_wt[below_spl].sum() / total_pop * 100)

    # Among below-SPL, how many have positive OOP?
    below_spl_pos_oop = below_spl & (oop > 0)
    n_below_pos = int(below_spl_pos_oop.sum())

    # Among above-SPL, how many exceed 40% threshold?
    above_spl = ~below_spl
    above_spl_hardship = above_spl & (oop > 0) & (oop > 0.4 * discretionary)
    n_above_hardship = int(above_spl_hardship.sum())

    # Original budget-share thresholds
    budget_share = np.where(y > 0, oop / y, 0)
    hardship_10 = (oop > 0) & (budget_share > 0.10)
    hardship_25 = (oop > 0) & (budget_share > 0.25)
    rate_10 = float((pop_wt[hardship_10]).sum() / total_pop * 100)
    rate_25 = float((pop_wt[hardship_25]).sum() / total_pop * 100)

    return {
        "spl_label": spl_label,
        "spl_value_daily": round(spl_value, 4),
        "spl_value_monthly": round(spl_value * DAYS_PER_MONTH, 2),
        "n_households": int(mask.sum()),
        "population_weighted": round(total_pop, 0),
        "revised_40pct": round(rate_40, 2),
        "original_10pct": round(rate_10, 2),
        "original_25pct": round(rate_25, 2),
        "pct_below_spl": round(pct_below, 2),
        "n_below_spl": n_below,
        "n_below_spl_with_oop": n_below_pos,
        "n_above_spl_exceeding_40pct": n_above_hardship,
    }


def run_sdg382_analysis(data, year_label, ipl_local, rel_base_local,
                        fpl_daily, lbpl_daily, ubpl_daily):
    """Run full SDG 3.8.2 analysis with all SPL variants."""

    # Compute WHO SPL from data
    who_spl, median_cons = compute_who_spl(data, ipl_local, rel_base_local)
    print(f"\n  WHO SPL computation:")
    print(f"    IPL (local): R{ipl_local:.4f}/day")
    print(f"    $1.15 base (local): R{rel_base_local:.4f}/day")
    print(f"    Weighted median consumption excl OOP: R{median_cons:.4f}/day")
    print(f"    Relative component: R{rel_base_local:.4f} + 0.5 × R{median_cons:.4f} = R{rel_base_local + 0.5 * median_cons:.4f}/day")
    print(f"    WHO SPL = max(R{ipl_local:.4f}, R{rel_base_local + 0.5 * median_cons:.4f}) = R{who_spl:.4f}/day")
    print(f"    WHO SPL monthly: R{who_spl * DAYS_PER_MONTH:.2f}")

    spl_variants = [
        (who_spl, "WHO SPL"),
        (fpl_daily, "Stats SA FPL"),
        (lbpl_daily, "Stats SA LBPL"),
        (ubpl_daily, "Stats SA UBPL"),
    ]

    results = {
        "year": year_label,
        "who_spl_daily": round(who_spl, 4),
        "who_spl_monthly": round(who_spl * DAYS_PER_MONTH, 2),
        "median_consumption_excl_oop_daily": round(median_cons, 4),
    }

    # National results by SPL variant
    for spl_val, spl_lbl in spl_variants:
        print(f"\n  --- {spl_lbl}: R{spl_val:.4f}/day (R{spl_val * DAYS_PER_MONTH:.2f}/month) ---")

        # All households
        key = spl_lbl.replace(" ", "_").lower()
        res_all = compute_sdg382(data, spl_val, spl_lbl)
        results[f"national_{key}_all"] = res_all
        print(f"    All:       Revised 40%={res_all['revised_40pct']:.1f}%  "
              f"Original 10%={res_all['original_10pct']:.1f}%  25%={res_all['original_25pct']:.1f}%  "
              f"Below SPL={res_all['pct_below_spl']:.1f}%")

        # By scheme membership
        mask_insured = data["treated"] == 1
        mask_uninsured = data["treated"] == 0
        res_ins = compute_sdg382(data, spl_val, spl_lbl, mask=mask_insured)
        res_unins = compute_sdg382(data, spl_val, spl_lbl, mask=mask_uninsured)
        results[f"national_{key}_insured"] = res_ins
        results[f"national_{key}_uninsured"] = res_unins
        print(f"    Insured:   Revised 40%={res_ins['revised_40pct']:.1f}%  "
              f"Original 10%={res_ins['original_10pct']:.1f}%  25%={res_ins['original_25pct']:.1f}%  "
              f"Below SPL={res_ins['pct_below_spl']:.1f}%")
        print(f"    Uninsured: Revised 40%={res_unins['revised_40pct']:.1f}%  "
              f"Original 10%={res_unins['original_10pct']:.1f}%  25%={res_unins['original_25pct']:.1f}%  "
              f"Below SPL={res_unins['pct_below_spl']:.1f}%")

    # Provincial analysis (WHO SPL only, to keep output manageable)
    results["provincial_who_spl"] = {}
    print(f"\n  --- Provincial Analysis (WHO SPL) ---")
    for pcode, pname in sorted(PROVINCE_NAMES.items()):
        mask_prov = data["province"] == pcode
        if mask_prov.sum() < 10:
            continue
        res_prov_all = compute_sdg382(data, who_spl, "WHO SPL", mask=mask_prov)
        mask_prov_ins = mask_prov & (data["treated"] == 1)
        mask_prov_unins = mask_prov & (data["treated"] == 0)
        res_prov_ins = compute_sdg382(data, who_spl, "WHO SPL", mask=mask_prov_ins)
        res_prov_unins = compute_sdg382(data, who_spl, "WHO SPL", mask=mask_prov_unins)
        results["provincial_who_spl"][pname] = {
            "all": res_prov_all,
            "insured": res_prov_ins,
            "uninsured": res_prov_unins,
        }
        print(f"    {pname:20s}  All: {res_prov_all['revised_40pct']:5.1f}%  "
              f"Ins: {res_prov_ins['revised_40pct']:5.1f}%  "
              f"Unins: {res_prov_unins['revised_40pct']:5.1f}%")

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("  SDG 3.8.2 AND OOP DISTRIBUTION ANALYSIS")
    print("=" * 70)

    # Load data
    print("\nLoading IES 2022/23...")
    data_2023 = load_data_2023()
    print(f"  Loaded {data_2023['n']} households: "
          f"{data_2023['treated'].sum()} insured, "
          f"{data_2023['n'] - data_2023['treated'].sum()} uninsured")

    print("\nLoading IES 2010/11...")
    data_2011 = load_data_2011()
    print(f"  Loaded {data_2011['n']} households: "
          f"{data_2011['treated'].sum()} insured, "
          f"{data_2011['n'] - data_2011['treated'].sum()} uninsured")

    all_results = {}

    # --- OOP Distribution ---
    print("\n" + "=" * 70)
    print("  OOP DISTRIBUTION ANALYSIS")
    print("=" * 70)

    dist_2023 = analyze_oop_distribution(data_2023, "IES 2022/23")
    dist_2011 = analyze_oop_distribution(data_2011, "IES 2010/11")
    all_results["oop_distribution"] = {"ies_2023": dist_2023, "ies_2011": dist_2011}

    print(f"\n  IES 2010/11 Uninsured: {dist_2011['uninsured']['pct_zero']}% zero OOP, "
          f"{dist_2011['uninsured']['pct_positive']}% positive "
          f"(weighted: {dist_2011['uninsured']['weighted_pct_zero']}% zero)")
    print(f"  IES 2022/23 Uninsured: {dist_2023['uninsured']['pct_zero']}% zero OOP, "
          f"{dist_2023['uninsured']['pct_positive']}% positive "
          f"(weighted: {dist_2023['uninsured']['weighted_pct_zero']}% zero)")
    print(f"  IES 2010/11 Insured:   {dist_2011['insured']['pct_zero']}% zero OOP")
    print(f"  IES 2022/23 Insured:   {dist_2023['insured']['pct_zero']}% zero OOP")

    # --- SDG 3.8.2 ---
    print("\n" + "=" * 70)
    print("  SDG 3.8.2 ANALYSIS — IES 2022/23")
    print("=" * 70)

    sdg_2023 = run_sdg382_analysis(
        data_2023, "IES 2022/23",
        IPL_2023, REL_BASE_2023,
        FPL_2023, LBPL_2023, UBPL_2023,
    )
    all_results["sdg382_2023"] = sdg_2023

    print("\n" + "=" * 70)
    print("  SDG 3.8.2 ANALYSIS — IES 2010/11")
    print("=" * 70)

    sdg_2011 = run_sdg382_analysis(
        data_2011, "IES 2010/11",
        IPL_2011, REL_BASE_2011,
        FPL_2011, LBPL_2011, UBPL_2011,
    )
    all_results["sdg382_2011"] = sdg_2011

    # --- Summary table for report ---
    print("\n" + "=" * 70)
    print("  SUMMARY: SENSITIVITY TO SPL CHOICE")
    print("=" * 70)
    for period, sdg in [("IES 2010/11", sdg_2011), ("IES 2022/23", sdg_2023)]:
        print(f"\n  {period}:")
        print(f"  {'SPL':20s} {'Monthly':>10s} {'All':>8s} {'Insured':>8s} {'Uninsured':>10s}")
        for key_base, lbl in [("who_spl", "WHO SPL"), ("stats_sa_fpl", "Stats SA FPL"),
                               ("stats_sa_lbpl", "Stats SA LBPL"), ("stats_sa_ubpl", "Stats SA UBPL")]:
            r_all = sdg[f"national_{key_base}_all"]
            r_ins = sdg[f"national_{key_base}_insured"]
            r_un = sdg[f"national_{key_base}_uninsured"]
            print(f"  {lbl:20s} R{r_all['spl_value_monthly']:>8.2f} "
                  f"{r_all['revised_40pct']:>7.1f}% {r_ins['revised_40pct']:>7.1f}% "
                  f"{r_un['revised_40pct']:>9.1f}%")

    # Save results
    output_file = "analysis_sdg382_results.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()
