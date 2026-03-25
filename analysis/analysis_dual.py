"""
Dual-Period Nearest-Neighbour Matching Analysis
================================================
Compares out-of-pocket health expenditure between medical scheme members
and non-members using NNM on Mahalanobis distance for both IES 2010/11
and IES 2022/23 datasets.

Outputs: analysis_dual_results.json
"""

import json
import sqlite3
import sys

import numpy as np
from scipy import stats
from scipy.spatial import KDTree

DB_2023 = "../ies2023.db"
DB_2011 = "../ies2011.db"

# CPI adjustment factor: March 2011 -> May 2023
# Source: Stats SA P0141 headline CPI (all items, metropolitan and other urban areas)
# March 2011 index (Dec 2016 = 100): 67.8
# May 2023 index (Dec 2016 = 100): 117.1
# Factor: 117.1 / 67.8 = 1.7271
CPI_FACTOR_2011_TO_2023 = 1.7271

PROVINCE_NAMES = {
    1: "Western Cape", 2: "Eastern Cape", 3: "Northern Cape",
    4: "Free State", 5: "KwaZulu-Natal", 6: "North West",
    7: "Gauteng", 8: "Mpumalanga", 9: "Limpopo",
}


def load_data_2023():
    """Load and prepare IES 2022/23 household data for matching."""
    conn = sqlite3.connect(DB_2023)
    query = """
    SELECT
        h.uqno,
        h.eoh_meds,
        CAST(h.expenditure AS REAL) AS expenditure,
        CAST(h.income AS REAL) AS income,
        CAST(h.hsize AS INTEGER) AS hsize,
        CAST(h.head_age AS INTEGER) AS head_age,
        h.head_sex,
        h.head_population,
        h.head_education,
        g.province,
        g.settlement_type,
        COALESCE(th.health_exp, 0) AS health_exp,
        CAST(h.hhold_wgt AS REAL) AS hhold_wgt
    FROM households h
    JOIN geography g ON h.uqno = g.uqno
    LEFT JOIN (
        SELECT uqno, SUM(valueannualized_adj) AS health_exp
        FROM total
        WHERE division = '06'
        GROUP BY uqno
    ) th ON h.uqno = th.uqno
    WHERE h.eoh_meds IN ('1', '2')
      AND CAST(h.expenditure AS REAL) > 0
      AND CAST(h.head_age AS INTEGER) > 0
      AND h.head_population IN ('1','2','3','4')
      AND h.head_education NOT IN ('98', '99')
    """
    rows = conn.execute(query).fetchall()
    conn.close()
    return _rows_to_data(rows)


def load_data_2011():
    """Load and prepare IES 2010/11 household data for matching."""
    conn = sqlite3.connect(DB_2011)
    query = """
    SELECT
        h.uqno,
        h.q31021medaid AS treatment_var,
        CAST(h.consumptions AS REAL) AS expenditure,
        CAST(h.income AS REAL) AS income,
        CAST(h.hsize AS INTEGER) AS hsize,
        CAST(p.q14age AS INTEGER) AS head_age,
        h.genderofhead AS head_sex,
        h.popgrpofhead AS head_population,
        p.q21highestlevel AS head_education,
        h.province,
        h.settlement_type,
        COALESCE(th.health_exp, 0) AS health_exp,
        CAST(h.full_calwgt AS REAL) AS hhold_wgt
    FROM households h
    LEFT JOIN (
        SELECT uqno, q14age, q21highestlevel
        FROM persons
        WHERE q15relationship = '1'
        GROUP BY uqno
        HAVING MIN(personno)
    ) p ON h.uqno = p.uqno
    LEFT JOIN (
        SELECT uqno, SUM(valueannualized) AS health_exp
        FROM total
        WHERE division = '06'
        GROUP BY uqno
    ) th ON h.uqno = th.uqno
    WHERE h.q31021medaid IN ('1', '2')
      AND CAST(h.consumptions AS REAL) > 0
      AND p.q14age IS NOT NULL
      AND CAST(p.q14age AS INTEGER) > 0
      AND h.popgrpofhead IN ('1','2','3','4')
      AND p.q21highestlevel NOT IN ('98', '99')
    """
    rows = conn.execute(query).fetchall()
    conn.close()
    return _rows_to_data(rows)


def _rows_to_data(rows):
    """Convert query rows to numpy data dict."""
    cols = [
        "uqno", "treatment_var", "expenditure", "income", "hsize",
        "head_age", "head_sex", "head_population", "head_education",
        "province", "settlement_type", "health_exp", "hhold_wgt",
    ]
    data = {c: [] for c in cols}
    for row in rows:
        for c, v in zip(cols, row):
            data[c].append(v)

    n = len(data["uqno"])
    result = {}
    result["uqno"] = data["uqno"]
    result["treated"] = np.array([1 if str(x) == "1" else 0 for x in data["treatment_var"]])
    result["health_exp"] = np.array(data["health_exp"], dtype=float)
    result["hhold_wgt"] = np.array(data["hhold_wgt"], dtype=float)

    # Continuous covariates
    result["log_expenditure"] = np.log(np.array(data["expenditure"], dtype=float) + 1)
    result["log_income"] = np.log(np.array(data["income"], dtype=float) + 1)
    result["hsize"] = np.array(data["hsize"], dtype=float)
    result["head_age"] = np.array(data["head_age"], dtype=float)

    # Categorical covariates
    result["head_sex"] = np.array([int(x) for x in data["head_sex"]], dtype=float)
    result["head_population"] = np.array([int(x) for x in data["head_population"]], dtype=float)

    # Education grouped (same scheme for both years: 0-27 scale)
    def edu_group(e):
        try:
            e = int(e)
        except (ValueError, TypeError):
            return 0
        if e == 0:
            return 0
        if e <= 7:
            return 1  # primary
        if e <= 12:
            return 2  # secondary
        if e <= 20:
            return 3  # certificate/diploma
        if e <= 27:
            return 4  # degree/postgrad
        return 0

    result["education_group"] = np.array([edu_group(x) for x in data["head_education"]], dtype=float)
    result["province"] = np.array([int(x) for x in data["province"]], dtype=float)
    result["settlement_type"] = np.array([int(x) for x in data["settlement_type"]], dtype=float)

    print(f"  Loaded {n} households: {int(result['treated'].sum())} treated, "
          f"{n - int(result['treated'].sum())} control")
    return result


def build_covariate_matrix(data, indices=None):
    """Build covariate matrix for matching."""
    covariates = [
        "log_expenditure", "log_income", "hsize", "head_age",
        "head_sex", "head_population", "education_group", "settlement_type",
    ]
    if indices is None:
        indices = np.arange(len(data["treated"]))
    X = np.column_stack([data[c][indices] for c in covariates])
    return X, covariates


def standardize(X, mean=None, std=None):
    """Standardize columns to zero mean, unit variance."""
    if mean is None:
        mean = X.mean(axis=0)
    if std is None:
        std = X.std(axis=0)
    std[std == 0] = 1
    return (X - mean) / std, mean, std


def nearest_neighbour_match(data, caliper=0.5, province_filter=None):
    """1:1 NNM without replacement on standardized covariates."""
    if province_filter is not None:
        mask = data["province"] == province_filter
        indices = np.where(mask)[0]
    else:
        indices = np.arange(len(data["treated"]))

    treated_idx = indices[data["treated"][indices] == 1]
    control_idx = indices[data["treated"][indices] == 0]

    if len(treated_idx) < 5 or len(control_idx) < 5:
        return None

    X_all, cov_names = build_covariate_matrix(data, indices)
    X_treated, _ = build_covariate_matrix(data, treated_idx)
    X_control, _ = build_covariate_matrix(data, control_idx)

    mean_all = X_all.mean(axis=0)
    std_all = X_all.std(axis=0)

    X_treated_s, _, _ = standardize(X_treated, mean_all, std_all)
    X_control_s, _, _ = standardize(X_control, mean_all, std_all)

    tree = KDTree(X_control_s)

    matched_treated = []
    matched_control = []
    used_controls = set()

    distances, nearest_ids = tree.query(X_treated_s, k=min(10, len(control_idx)))

    rng = np.random.RandomState(42)
    order = rng.permutation(len(treated_idx))

    for i in order:
        if nearest_ids.ndim == 1:
            candidates = [nearest_ids[i]]
            dists = [distances[i]]
        else:
            candidates = nearest_ids[i]
            dists = distances[i]

        for ctrl_local, d in zip(candidates, dists):
            if ctrl_local not in used_controls and d <= caliper * X_treated_s.shape[1]:
                matched_treated.append(treated_idx[i])
                matched_control.append(control_idx[ctrl_local])
                used_controls.add(ctrl_local)
                break

    matched_treated = np.array(matched_treated)
    matched_control = np.array(matched_control)

    if len(matched_treated) < 5:
        return None

    y_treated = data["health_exp"][matched_treated]
    y_control = data["health_exp"][matched_control]

    diff = y_treated - y_control
    att = float(np.mean(diff))
    se = float(np.std(diff, ddof=1) / np.sqrt(len(diff)))

    t_stat, p_value_t = stats.ttest_rel(y_treated, y_control)
    try:
        w_stat, p_value_w = stats.wilcoxon(y_treated, y_control, alternative="two-sided")
    except ValueError:
        w_stat, p_value_w = np.nan, np.nan

    all_treated_idx = treated_idx
    all_control_idx = control_idx
    u_stat, p_value_mw = stats.mannwhitneyu(
        data["health_exp"][all_treated_idx],
        data["health_exp"][all_control_idx],
        alternative="two-sided",
    )

    # Balance diagnostics
    X_mt, _ = build_covariate_matrix(data, matched_treated)
    X_mc, _ = build_covariate_matrix(data, matched_control)
    X_ut, _ = build_covariate_matrix(data, all_treated_idx)
    X_uc, _ = build_covariate_matrix(data, all_control_idx)

    balance = []
    for j, name in enumerate(cov_names):
        pooled_std_before = np.sqrt((X_ut[:, j].var() + X_uc[:, j].var()) / 2)
        smd_before = (X_ut[:, j].mean() - X_uc[:, j].mean()) / pooled_std_before if pooled_std_before > 0 else 0
        pooled_std_after = np.sqrt((X_mt[:, j].var() + X_mc[:, j].var()) / 2)
        smd_after = (X_mt[:, j].mean() - X_mc[:, j].mean()) / pooled_std_after if pooled_std_after > 0 else 0
        balance.append({
            "covariate": name,
            "smd_before": round(smd_before, 4),
            "smd_after": round(smd_after, 4),
            "reduction_pct": round((1 - abs(smd_after) / max(abs(smd_before), 1e-10)) * 100, 1),
        })

    return {
        "n_treated_total": int(len(all_treated_idx)),
        "n_control_total": int(len(all_control_idx)),
        "n_matched": int(len(matched_treated)),
        "match_rate": round(len(matched_treated) / len(all_treated_idx) * 100, 1),
        "mean_treated_unmatched": round(float(data["health_exp"][all_treated_idx].mean()), 2),
        "mean_control_unmatched": round(float(data["health_exp"][all_control_idx].mean()), 2),
        "naive_diff": round(float(data["health_exp"][all_treated_idx].mean() - data["health_exp"][all_control_idx].mean()), 2),
        "p_value_mannwhitney": float(p_value_mw),
        "mean_treated_matched": round(float(y_treated.mean()), 2),
        "mean_control_matched": round(float(y_control.mean()), 2),
        "att": round(att, 2),
        "se": round(se, 2),
        "ci_lower": round(att - 1.96 * se, 2),
        "ci_upper": round(att + 1.96 * se, 2),
        "t_stat": round(float(t_stat), 4),
        "p_value_paired_t": float(p_value_t),
        "p_value_wilcoxon": float(p_value_w) if not np.isnan(p_value_w) else None,
        "median_treated_matched": round(float(np.median(y_treated)), 2),
        "median_control_matched": round(float(np.median(y_control)), 2),
        "median_diff": round(float(np.median(y_treated) - np.median(y_control)), 2),
        "pct_treated_any_spend": round(float((y_treated > 0).mean() * 100), 1),
        "pct_control_any_spend": round(float((y_control > 0).mean() * 100), 1),
        "cohens_d": round(float(att / (np.std(diff, ddof=1) if np.std(diff, ddof=1) > 0 else 1)), 4),
        "balance": balance,
    }


def bootstrap_ci(data, province_filter=None, n_boot=500, caliper=0.5):
    """Bootstrap confidence interval for ATT."""
    rng = np.random.RandomState(123)
    if province_filter is not None:
        mask = data["province"] == province_filter
        indices = np.where(mask)[0]
    else:
        indices = np.arange(len(data["treated"]))

    n = len(indices)
    atts = []
    for b in range(n_boot):
        boot_idx = rng.choice(indices, size=n, replace=True)
        boot_data = {}
        for key in data:
            if isinstance(data[key], np.ndarray):
                boot_data[key] = data[key][boot_idx]
            else:
                boot_data[key] = [data[key][i] for i in boot_idx]
        res = nearest_neighbour_match(boot_data, caliper=caliper, province_filter=None)
        if res is not None:
            atts.append(res["att"])

    if len(atts) < 50:
        return None, None, None

    atts = np.array(atts)
    lo = np.percentile(atts, 2.5)
    hi = np.percentile(atts, 97.5)
    return round(float(np.mean(atts)), 2), round(float(lo), 2), round(float(hi), 2)


def run_full_analysis(data, year_label, caliper_national=0.5, caliper_provincial=0.75):
    """Run complete analysis for one dataset year."""
    results = {"year": year_label}

    # ---- National Analysis ----
    print(f"\n{'='*60}")
    print(f"  NATIONAL ANALYSIS — {year_label}")
    print(f"{'='*60}")

    nat = nearest_neighbour_match(data, caliper=caliper_national)
    results["national"] = nat

    print(f"  Treated: {nat['n_treated_total']}, Control: {nat['n_control_total']}")
    print(f"  Matched: {nat['n_matched']} ({nat['match_rate']}%)")
    print(f"  ATT: R{nat['att']:,.2f} (SE: R{nat['se']:,.2f})")
    print(f"  95% CI: [R{nat['ci_lower']:,.2f}, R{nat['ci_upper']:,.2f}]")
    print(f"  p-value: {nat['p_value_paired_t']:.2e}")
    print(f"  Cohen's d: {nat['cohens_d']:.4f}")
    print(f"  % any spend — treated: {nat['pct_treated_any_spend']}%, "
          f"control: {nat['pct_control_any_spend']}%")

    print("\n  Balance diagnostics:")
    print(f"    {'Covariate':<20} {'Before':>10} {'After':>10} {'% Reduction':>12}")
    for b in nat["balance"]:
        print(f"    {b['covariate']:<20} {b['smd_before']:>10.4f} {b['smd_after']:>10.4f} {b['reduction_pct']:>11.1f}%")

    # Bootstrap CI
    print(f"\n  Computing bootstrap CI (500 replications)...")
    boot_att, boot_lo, boot_hi = bootstrap_ci(data, n_boot=500, caliper=caliper_national)
    if boot_att is not None:
        results["national"]["boot_att"] = boot_att
        results["national"]["boot_ci_lower"] = boot_lo
        results["national"]["boot_ci_upper"] = boot_hi
        print(f"  Bootstrap ATT: R{boot_att:,.2f} [{boot_lo:,.2f}, {boot_hi:,.2f}]")

    # ---- Provincial Analysis ----
    results["provincial"] = {}
    print(f"\n{'='*60}")
    print(f"  PROVINCIAL ANALYSIS — {year_label}")
    print(f"{'='*60}")

    for pcode, pname in sorted(PROVINCE_NAMES.items()):
        prov_result = nearest_neighbour_match(data, caliper=caliper_provincial, province_filter=float(pcode))
        if prov_result is None:
            print(f"  {pname}: Insufficient data")
            results["provincial"][pname] = None
            continue

        results["provincial"][pname] = prov_result
        r = prov_result
        sig = "***" if r["p_value_paired_t"] < 0.001 else ("**" if r["p_value_paired_t"] < 0.01 else ("*" if r["p_value_paired_t"] < 0.05 else ""))
        print(f"  {pname:<16} Matched: {r['n_matched']:>5}/{r['n_treated_total']:<5} "
              f"ATT: R{r['att']:>10,.2f} (d={r['cohens_d']:.3f}) {sig}")

    # ---- Sensitivity: positive health expenditure only ----
    print(f"\n  Sensitivity: positive health expenditure only...")
    mask_nz = data["health_exp"] > 0
    idx_nz = np.where(mask_nz)[0]
    data_nz = {}
    for key in data:
        if isinstance(data[key], np.ndarray):
            data_nz[key] = data[key][idx_nz]
        else:
            data_nz[key] = [data[key][i] for i in idx_nz]

    sens_nz = nearest_neighbour_match(data_nz, caliper=caliper_national)
    results["sensitivity_nonzero"] = sens_nz
    if sens_nz:
        print(f"  ATT (OOP>0): R{sens_nz['att']:,.2f} (p={sens_nz['p_value_paired_t']:.2e})")

    # ---- Sensitivity: exact province matching ----
    print(f"  Sensitivity: exact province matching...")
    pooled_atts = []
    pooled_ns = []
    pooled_ses = []
    for pcode in range(1, 10):
        r = nearest_neighbour_match(data, caliper=caliper_provincial, province_filter=float(pcode))
        if r:
            pooled_atts.append(r["att"])
            pooled_ns.append(r["n_matched"])
            pooled_ses.append(r["se"])

    pooled_atts = np.array(pooled_atts)
    pooled_ns = np.array(pooled_ns)
    pooled_ses = np.array(pooled_ses)
    pooled_att = float(np.average(pooled_atts, weights=pooled_ns))
    pooled_se = float(np.sqrt(np.sum((pooled_ns / pooled_ns.sum()) ** 2 * pooled_ses ** 2)))

    results["sensitivity_exact_province"] = {
        "pooled_att": round(pooled_att, 2),
        "pooled_se": round(pooled_se, 2),
        "total_matched": int(pooled_ns.sum()),
        "ci_lower": round(pooled_att - 1.96 * pooled_se, 2),
        "ci_upper": round(pooled_att + 1.96 * pooled_se, 2),
    }
    print(f"  Pooled ATT (exact province): R{pooled_att:,.2f} [{pooled_att - 1.96 * pooled_se:,.2f}, {pooled_att + 1.96 * pooled_se:,.2f}]")

    # ---- Descriptive statistics ----
    results["descriptives"] = {
        "n_total": int(len(data["treated"])),
        "n_treated": int(data["treated"].sum()),
        "n_control": int(len(data["treated"]) - data["treated"].sum()),
        "mean_expenditure_all": round(float(np.exp(data["log_expenditure"]).mean()), 2),
        "mean_income_all": round(float(np.exp(data["log_income"]).mean()), 2),
        "mean_health_exp_all": round(float(data["health_exp"].mean()), 2),
        "mean_health_exp_treated": round(float(data["health_exp"][data["treated"] == 1].mean()), 2),
        "mean_health_exp_control": round(float(data["health_exp"][data["treated"] == 0].mean()), 2),
        "median_health_exp_treated": round(float(np.median(data["health_exp"][data["treated"] == 1])), 2),
        "median_health_exp_control": round(float(np.median(data["health_exp"][data["treated"] == 0])), 2),
        "pct_any_health_treated": round(float((data["health_exp"][data["treated"] == 1] > 0).mean() * 100), 1),
        "pct_any_health_control": round(float((data["health_exp"][data["treated"] == 0] > 0).mean() * 100), 1),
        "pct_treated": round(float(data["treated"].mean() * 100), 1),
        "weighted_pct_treated": round(
            float(np.sum(data["hhold_wgt"][data["treated"] == 1]) / np.sum(data["hhold_wgt"]) * 100), 1
        ),
    }

    return results


def cross_period_comparison(results_2011, results_2023):
    """Compare OOP spending trends between periods, adjusted for inflation."""
    comparison = {
        "cpi_factor": CPI_FACTOR_2011_TO_2023,
        "reference_prices": {
            "2011": "March 2011 Rand",
            "2023": "May 2023 Rand",
        },
    }

    # National ATT comparison
    att_2011_nominal = results_2011["national"]["att"]
    att_2011_real = round(att_2011_nominal * CPI_FACTOR_2011_TO_2023, 2)
    att_2023 = results_2023["national"]["att"]
    real_change = round(att_2023 - att_2011_real, 2)
    real_change_pct = round((att_2023 / att_2011_real - 1) * 100, 1) if att_2011_real != 0 else None

    comparison["national_att"] = {
        "att_2011_nominal": att_2011_nominal,
        "att_2011_real_2023_prices": att_2011_real,
        "att_2023": att_2023,
        "real_change": real_change,
        "real_change_pct": real_change_pct,
        "nominal_change_pct": round((att_2023 / att_2011_nominal - 1) * 100, 1) if att_2011_nominal != 0 else None,
    }

    # Mean OOP comparison (all households)
    mean_2011_t = results_2011["descriptives"]["mean_health_exp_treated"]
    mean_2011_c = results_2011["descriptives"]["mean_health_exp_control"]
    mean_2023_t = results_2023["descriptives"]["mean_health_exp_treated"]
    mean_2023_c = results_2023["descriptives"]["mean_health_exp_control"]

    comparison["mean_oop"] = {
        "treated_2011_nominal": mean_2011_t,
        "treated_2011_real": round(mean_2011_t * CPI_FACTOR_2011_TO_2023, 2),
        "treated_2023": mean_2023_t,
        "treated_real_change_pct": round((mean_2023_t / (mean_2011_t * CPI_FACTOR_2011_TO_2023) - 1) * 100, 1) if mean_2011_t > 0 else None,
        "control_2011_nominal": mean_2011_c,
        "control_2011_real": round(mean_2011_c * CPI_FACTOR_2011_TO_2023, 2),
        "control_2023": mean_2023_c,
        "control_real_change_pct": round((mean_2023_c / (mean_2011_c * CPI_FACTOR_2011_TO_2023) - 1) * 100, 1) if mean_2011_c > 0 else None,
    }

    # Healthcare utilisation comparison
    comparison["utilisation"] = {
        "pct_treated_any_2011": results_2011["descriptives"]["pct_any_health_treated"],
        "pct_treated_any_2023": results_2023["descriptives"]["pct_any_health_treated"],
        "pct_control_any_2011": results_2011["descriptives"]["pct_any_health_control"],
        "pct_control_any_2023": results_2023["descriptives"]["pct_any_health_control"],
    }

    # Medical scheme coverage comparison
    comparison["coverage"] = {
        "pct_treated_2011_sample": results_2011["descriptives"]["pct_treated"],
        "pct_treated_2023_sample": results_2023["descriptives"]["pct_treated"],
        "pct_treated_2011_weighted": results_2011["descriptives"]["weighted_pct_treated"],
        "pct_treated_2023_weighted": results_2023["descriptives"]["weighted_pct_treated"],
    }

    # Provincial ATT comparison
    provincial = {}
    for pname in PROVINCE_NAMES.values():
        r2011 = results_2011["provincial"].get(pname)
        r2023 = results_2023["provincial"].get(pname)
        if r2011 and r2023:
            att_2011_r = round(r2011["att"] * CPI_FACTOR_2011_TO_2023, 2)
            provincial[pname] = {
                "att_2011_nominal": r2011["att"],
                "att_2011_real": att_2011_r,
                "att_2023": r2023["att"],
                "real_change": round(r2023["att"] - att_2011_r, 2),
                "real_change_pct": round((r2023["att"] / att_2011_r - 1) * 100, 1) if att_2011_r != 0 else None,
                "cohens_d_2011": r2011["cohens_d"],
                "cohens_d_2023": r2023["cohens_d"],
            }

    comparison["provincial_att"] = provincial

    # Mean health expenditure by COICOP group (for more granular analysis)
    comparison["matched_comparison"] = {
        "mean_treated_matched_2011_nominal": results_2011["national"]["mean_treated_matched"],
        "mean_treated_matched_2011_real": round(results_2011["national"]["mean_treated_matched"] * CPI_FACTOR_2011_TO_2023, 2),
        "mean_treated_matched_2023": results_2023["national"]["mean_treated_matched"],
        "mean_control_matched_2011_nominal": results_2011["national"]["mean_control_matched"],
        "mean_control_matched_2011_real": round(results_2011["national"]["mean_control_matched"] * CPI_FACTOR_2011_TO_2023, 2),
        "mean_control_matched_2023": results_2023["national"]["mean_control_matched"],
    }

    return comparison


def health_spending_by_group(db_path, year_label):
    """Get detailed health spending breakdown by COICOP group."""
    conn = sqlite3.connect(db_path)

    if year_label == "IES 2022/23":
        medaid_col = "eoh_meds"
        exp_col = "valueannualized_adj"
        join_clause = "JOIN geography g ON h.uqno = g.uqno"
        where_extra = ""
    else:
        medaid_col = "q31021medaid"
        exp_col = "valueannualized"
        join_clause = ""
        where_extra = ""

    # Health spending by group (061-064)
    if year_label == "IES 2022/23":
        query = f"""
        SELECT
            t."group",
            cg.label AS group_label,
            h.{medaid_col} AS scheme,
            SUM(t.{exp_col}) / COUNT(DISTINCT h.uqno) AS mean_per_hh
        FROM total t
        JOIN households h ON t.uqno = h.uqno
        LEFT JOIN coicop_lookup cg ON t."group" = cg.code AND cg.level = 'group'
        WHERE t.division = '06'
          AND h.{medaid_col} IN ('1', '2')
        GROUP BY t."group", cg.label, h.{medaid_col}
        ORDER BY t."group", h.{medaid_col}
        """
    else:
        query = f"""
        SELECT
            t."group",
            cg.label AS group_label,
            h.{medaid_col} AS scheme,
            SUM(t.{exp_col}) / COUNT(DISTINCT h.uqno) AS mean_per_hh
        FROM total t
        JOIN households h ON t.uqno = h.uqno
        LEFT JOIN coicop_lookup cg ON t."group" = cg.code AND cg.level = 'group'
        WHERE t.division = '06'
          AND h.{medaid_col} IN ('1', '2')
        GROUP BY t."group", cg.label, h.{medaid_col}
        ORDER BY t."group", h.{medaid_col}
        """

    rows = conn.execute(query).fetchall()
    conn.close()

    breakdown = {}
    for group_code, group_label, scheme, mean_val in rows:
        if group_code not in breakdown:
            breakdown[group_code] = {"label": group_label, "treated": 0, "control": 0}
        if scheme == "1":
            breakdown[group_code]["treated"] = round(float(mean_val), 2)
        else:
            breakdown[group_code]["control"] = round(float(mean_val), 2)

    return breakdown


def main():
    print("=" * 70)
    print("DUAL-PERIOD NEAREST-NEIGHBOUR MATCHING ANALYSIS")
    print("Medical Scheme Co-payments: IES 2010/11 vs IES 2022/23")
    print("=" * 70)

    # ---- Load Data ----
    print("\nLoading IES 2010/11 data...")
    data_2011 = load_data_2011()
    print("\nLoading IES 2022/23 data...")
    data_2023 = load_data_2023()

    # ---- Run Analyses ----
    results_2011 = run_full_analysis(data_2011, "IES 2010/11")
    results_2023 = run_full_analysis(data_2023, "IES 2022/23")

    # ---- Cross-Period Comparison ----
    print(f"\n{'='*60}")
    print("  CROSS-PERIOD COMPARISON")
    print(f"{'='*60}")

    comparison = cross_period_comparison(results_2011, results_2023)

    c = comparison["national_att"]
    print(f"\n  National ATT:")
    print(f"    2011 (nominal):  R{c['att_2011_nominal']:,.2f}")
    print(f"    2011 (real, 2023 prices): R{c['att_2011_real_2023_prices']:,.2f}")
    print(f"    2023:            R{c['att_2023']:,.2f}")
    print(f"    Real change:     R{c['real_change']:,.2f} ({c['real_change_pct']:+.1f}%)")

    m = comparison["mean_oop"]
    print(f"\n  Mean OOP (treated, unmatched):")
    print(f"    2011 (nominal):  R{m['treated_2011_nominal']:,.2f}")
    print(f"    2011 (real):     R{m['treated_2011_real']:,.2f}")
    print(f"    2023:            R{m['treated_2023']:,.2f}")
    print(f"    Real change:     {m['treated_real_change_pct']:+.1f}%")

    print(f"\n  Mean OOP (control, unmatched):")
    print(f"    2011 (nominal):  R{m['control_2011_nominal']:,.2f}")
    print(f"    2011 (real):     R{m['control_2011_real']:,.2f}")
    print(f"    2023:            R{m['control_2023']:,.2f}")
    print(f"    Real change:     {m['control_real_change_pct']:+.1f}%")

    print(f"\n  Provincial comparison (real 2023 prices):")
    for pname, pdata in comparison["provincial_att"].items():
        print(f"    {pname:<16} 2011: R{pdata['att_2011_real']:>8,.2f}  "
              f"2023: R{pdata['att_2023']:>8,.2f}  "
              f"Change: {pdata['real_change_pct']:>+6.1f}%")

    # ---- Health Spending Breakdown ----
    print(f"\n  Health spending breakdown by COICOP group...")
    breakdown_2011 = health_spending_by_group(DB_2011, "IES 2010/11")
    breakdown_2023 = health_spending_by_group(DB_2023, "IES 2022/23")

    # ---- Compile and Save ----
    all_results = {
        "ies_2011": results_2011,
        "ies_2023": results_2023,
        "comparison": comparison,
        "health_breakdown_2011": breakdown_2011,
        "health_breakdown_2023": breakdown_2023,
        "metadata": {
            "cpi_factor": CPI_FACTOR_2011_TO_2023,
            "cpi_source": "Stats SA P0141, headline CPI (all items), Dec 2016 = 100",
            "reference_2011": "March 2011 prices",
            "reference_2023": "May 2023 prices",
            "survey_2011": "IES 2010/11 (Sep 2010 - Aug 2011, n=25,328)",
            "survey_2023": "IES 2022/23 (Nov 2022 - Nov 2023, n=19,939)",
            "response_rate_2011": 91.6,
            "response_rate_2023": 81.94,
        },
    }

    def convert(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    with open("analysis_dual_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=convert)

    print(f"\nResults saved to analysis_dual_results.json")
    return all_results


if __name__ == "__main__":
    main()
