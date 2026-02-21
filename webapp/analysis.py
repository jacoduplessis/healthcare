"""
Nearest-Neighbour Matching Analysis: Medical Scheme Co-payments
Compares out-of-pocket health expenditure between medical scheme members
and non-members using Mahalanobis distance nearest-neighbour matching.
"""
import json
import sqlite3
import sys

import numpy as np
from scipy import stats
from scipy.spatial import KDTree

DB_PATH = "../ies2023.db"


def load_data():
    """Load and prepare household-level data for matching."""
    conn = sqlite3.connect(DB_PATH)

    # Get household data with covariates and health expenditure
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
      AND h.head_education != '98'
    """

    rows = conn.execute(query).fetchall()
    cols = [
        "uqno", "eoh_meds", "expenditure", "income", "hsize",
        "head_age", "head_sex", "head_population", "head_education",
        "province", "settlement_type", "health_exp", "hhold_wgt",
    ]
    conn.close()

    data = {c: [] for c in cols}
    for row in rows:
        for c, v in zip(cols, row):
            data[c].append(v)

    # Convert to numpy arrays
    n = len(data["uqno"])
    result = {}
    result["uqno"] = data["uqno"]
    result["treated"] = np.array([1 if x == "1" else 0 for x in data["eoh_meds"]])
    result["health_exp"] = np.array(data["health_exp"], dtype=float)
    result["hhold_wgt"] = np.array(data["hhold_wgt"], dtype=float)

    # Continuous covariates
    result["log_expenditure"] = np.log(np.array(data["expenditure"], dtype=float) + 1)
    result["log_income"] = np.log(np.array(data["income"], dtype=float) + 1)
    result["hsize"] = np.array(data["hsize"], dtype=float)
    result["head_age"] = np.array(data["head_age"], dtype=float)

    # Categorical covariates (encode as numeric)
    result["head_sex"] = np.array([int(x) for x in data["head_sex"]], dtype=float)
    result["head_population"] = np.array([int(x) for x in data["head_population"]], dtype=float)

    # Education grouped
    def edu_group(e):
        try:
            e = int(e)
        except (ValueError, TypeError):
            return 0
        if e == 0:
            return 0
        if e <= 7:
            return 1
        if e <= 12:
            return 2
        if e <= 20:
            return 3
        if e <= 27:
            return 4
        return 0

    result["education_group"] = np.array([edu_group(x) for x in data["head_education"]], dtype=float)
    result["province"] = np.array([int(x) for x in data["province"]], dtype=float)
    result["settlement_type"] = np.array([int(x) for x in data["settlement_type"]], dtype=float)

    print(f"Loaded {n} households: {result['treated'].sum()} treated, {n - result['treated'].sum()} control")
    return result


def build_covariate_matrix(data, indices=None):
    """Build standardised covariate matrix for matching."""
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
    std[std == 0] = 1  # prevent division by zero
    return (X - mean) / std, mean, std


def nearest_neighbour_match(data, caliper=0.25, n_neighbours=1, province_filter=None):
    """
    Perform 1:1 nearest-neighbour matching using Mahalanobis distance
    on standardised covariates. Matching without replacement.

    Returns dict with match results.
    """
    if province_filter is not None:
        mask = data["province"] == province_filter
        indices = np.where(mask)[0]
    else:
        indices = np.arange(len(data["treated"]))

    treated_idx = indices[data["treated"][indices] == 1]
    control_idx = indices[data["treated"][indices] == 0]

    if len(treated_idx) < 5 or len(control_idx) < 5:
        return None

    # Build covariate matrices
    X_all, cov_names = build_covariate_matrix(data, indices)
    X_treated, cov_names = build_covariate_matrix(data, treated_idx)
    X_control, cov_names = build_covariate_matrix(data, control_idx)

    # Standardize using pooled mean/std
    mean_all = X_all.mean(axis=0)
    std_all = X_all.std(axis=0)

    X_treated_s, _, _ = standardize(X_treated, mean_all, std_all)
    X_control_s, _, _ = standardize(X_control, mean_all, std_all)

    # Build KD-tree on control units
    tree = KDTree(X_control_s)

    # Match each treated unit to nearest control
    matched_treated = []
    matched_control = []
    used_controls = set()

    # Query all at once, then assign greedily
    distances, nearest_ids = tree.query(X_treated_s, k=min(10, len(control_idx)))

    # Sort treated by distance to best match (match hardest first would be better,
    # but random order is standard)
    rng = np.random.RandomState(42)
    order = rng.permutation(len(treated_idx))

    for i in order:
        if nearest_ids.ndim == 1:
            candidates = [nearest_ids[i]]
            dists = [distances[i]]
        else:
            candidates = nearest_ids[i]
            dists = distances[i]

        for j, (ctrl_local, d) in enumerate(zip(candidates, dists)):
            if ctrl_local not in used_controls and d <= caliper * X_treated_s.shape[1]:
                matched_treated.append(treated_idx[i])
                matched_control.append(control_idx[ctrl_local])
                used_controls.add(ctrl_local)
                break

    matched_treated = np.array(matched_treated)
    matched_control = np.array(matched_control)

    if len(matched_treated) < 5:
        return None

    # Compute outcomes
    y_treated = data["health_exp"][matched_treated]
    y_control = data["health_exp"][matched_control]
    w_treated = data["hhold_wgt"][matched_treated]
    w_control = data["hhold_wgt"][matched_control]

    # ATT (Average Treatment Effect on the Treated)
    diff = y_treated - y_control
    att = np.mean(diff)
    att_weighted = np.average(diff, weights=w_treated)

    # Standard error (Abadie-Imbens)
    se = np.std(diff, ddof=1) / np.sqrt(len(diff))

    # t-test on matched differences
    t_stat, p_value_t = stats.ttest_rel(y_treated, y_control)

    # Wilcoxon signed-rank test (non-parametric)
    try:
        w_stat, p_value_w = stats.wilcoxon(y_treated, y_control, alternative="two-sided")
    except ValueError:
        w_stat, p_value_w = np.nan, np.nan

    # Mann-Whitney U on unmatched (for comparison)
    all_treated_idx = treated_idx
    all_control_idx = control_idx
    u_stat, p_value_mw = stats.mannwhitneyu(
        data["health_exp"][all_treated_idx],
        data["health_exp"][all_control_idx],
        alternative="two-sided",
    )

    # Balance diagnostics (standardized mean differences)
    X_mt, _ = build_covariate_matrix(data, matched_treated)
    X_mc, _ = build_covariate_matrix(data, matched_control)
    X_ut, _ = build_covariate_matrix(data, all_treated_idx)
    X_uc, _ = build_covariate_matrix(data, all_control_idx)

    balance = []
    for j, name in enumerate(cov_names):
        # Before matching
        pooled_std_before = np.sqrt((X_ut[:, j].var() + X_uc[:, j].var()) / 2)
        if pooled_std_before > 0:
            smd_before = (X_ut[:, j].mean() - X_uc[:, j].mean()) / pooled_std_before
        else:
            smd_before = 0

        # After matching
        pooled_std_after = np.sqrt((X_mt[:, j].var() + X_mc[:, j].var()) / 2)
        if pooled_std_after > 0:
            smd_after = (X_mt[:, j].mean() - X_mc[:, j].mean()) / pooled_std_after
        else:
            smd_after = 0

        balance.append({
            "covariate": name,
            "smd_before": round(smd_before, 4),
            "smd_after": round(smd_after, 4),
            "reduction_pct": round((1 - abs(smd_after) / max(abs(smd_before), 1e-10)) * 100, 1),
        })

    # Additional descriptives
    result = {
        "n_treated_total": int(len(all_treated_idx)),
        "n_control_total": int(len(all_control_idx)),
        "n_matched": int(len(matched_treated)),
        "match_rate": round(len(matched_treated) / len(all_treated_idx) * 100, 1),

        # Unmatched comparison
        "mean_treated_unmatched": round(float(data["health_exp"][all_treated_idx].mean()), 2),
        "mean_control_unmatched": round(float(data["health_exp"][all_control_idx].mean()), 2),
        "naive_diff": round(float(data["health_exp"][all_treated_idx].mean() - data["health_exp"][all_control_idx].mean()), 2),
        "p_value_mannwhitney": float(p_value_mw),

        # Matched comparison
        "mean_treated_matched": round(float(y_treated.mean()), 2),
        "mean_control_matched": round(float(y_control.mean()), 2),
        "att": round(float(att), 2),
        "att_weighted": round(float(att_weighted), 2),
        "se": round(float(se), 2),
        "ci_lower": round(float(att - 1.96 * se), 2),
        "ci_upper": round(float(att + 1.96 * se), 2),
        "t_stat": round(float(t_stat), 4),
        "p_value_paired_t": float(p_value_t),
        "p_value_wilcoxon": float(p_value_w) if not np.isnan(p_value_w) else None,

        # Medians
        "median_treated_matched": round(float(np.median(y_treated)), 2),
        "median_control_matched": round(float(np.median(y_control)), 2),
        "median_diff": round(float(np.median(y_treated) - np.median(y_control)), 2),

        # Proportion with any health spending
        "pct_treated_any_spend": round(float((y_treated > 0).mean() * 100), 1),
        "pct_control_any_spend": round(float((y_control > 0).mean() * 100), 1),

        # Cohen's d
        "cohens_d": round(float(att / (np.std(diff, ddof=1) if np.std(diff, ddof=1) > 0 else 1)), 4),

        "balance": balance,
    }

    return result


def bootstrap_ci(data, province_filter=None, n_boot=500, alpha=0.05):
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
        # Create a subset data dict
        boot_data = {}
        for key in data:
            if isinstance(data[key], np.ndarray):
                boot_data[key] = data[key][boot_idx]
            else:
                boot_data[key] = [data[key][i] for i in boot_idx]

        # Reset province to avoid filter issues
        res = nearest_neighbour_match(boot_data, caliper=0.5, province_filter=None)
        if res is not None:
            atts.append(res["att"])

    if len(atts) < 50:
        return None, None, None

    atts = np.array(atts)
    lo = np.percentile(atts, 100 * alpha / 2)
    hi = np.percentile(atts, 100 * (1 - alpha / 2))
    return round(float(np.mean(atts)), 2), round(float(lo), 2), round(float(hi), 2)


def main():
    print("=" * 70)
    print("NEAREST-NEIGHBOUR MATCHING ANALYSIS")
    print("Medical Scheme Co-payments: Members vs Non-Members")
    print("=" * 70)
    print()

    data = load_data()

    province_names = {
        1: "Western Cape", 2: "Eastern Cape", 3: "Northern Cape",
        4: "Free State", 5: "KwaZulu-Natal", 6: "North West",
        7: "Gauteng", 8: "Mpumalanga", 9: "Limpopo",
    }

    results = {}

    # ---- National Analysis ----
    print("\n" + "=" * 50)
    print("NATIONAL ANALYSIS")
    print("=" * 50)

    nat = nearest_neighbour_match(data, caliper=0.5)
    results["national"] = nat

    print(f"  Treated (medical aid): {nat['n_treated_total']}")
    print(f"  Control (no medical aid): {nat['n_control_total']}")
    print(f"  Matched pairs: {nat['n_matched']} ({nat['match_rate']}%)")
    print()
    print("  UNMATCHED comparison:")
    print(f"    Mean health exp (treated): R{nat['mean_treated_unmatched']:,.2f}")
    print(f"    Mean health exp (control): R{nat['mean_control_unmatched']:,.2f}")
    print(f"    Naive difference: R{nat['naive_diff']:,.2f}")
    print(f"    Mann-Whitney U p-value: {nat['p_value_mannwhitney']:.2e}")
    print()
    print("  MATCHED comparison (ATT):")
    print(f"    Mean health exp (treated): R{nat['mean_treated_matched']:,.2f}")
    print(f"    Mean health exp (control): R{nat['mean_control_matched']:,.2f}")
    print(f"    ATT: R{nat['att']:,.2f}")
    print(f"    SE: R{nat['se']:,.2f}")
    print(f"    95% CI: [R{nat['ci_lower']:,.2f}, R{nat['ci_upper']:,.2f}]")
    print(f"    Paired t-test: t={nat['t_stat']:.4f}, p={nat['p_value_paired_t']:.2e}")
    if nat['p_value_wilcoxon']:
        print(f"    Wilcoxon signed-rank p-value: {nat['p_value_wilcoxon']:.2e}")
    print(f"    Cohen's d: {nat['cohens_d']:.4f}")
    print()
    print(f"    Median treated: R{nat['median_treated_matched']:,.2f}")
    print(f"    Median control: R{nat['median_control_matched']:,.2f}")
    print(f"    % with any health spend (treated): {nat['pct_treated_any_spend']}%")
    print(f"    % with any health spend (control): {nat['pct_control_any_spend']}%")
    print()
    print("  BALANCE DIAGNOSTICS (Standardised Mean Differences):")
    print(f"    {'Covariate':<20} {'Before':>10} {'After':>10} {'% Reduction':>12}")
    for b in nat["balance"]:
        print(f"    {b['covariate']:<20} {b['smd_before']:>10.4f} {b['smd_after']:>10.4f} {b['reduction_pct']:>11.1f}%")

    # Bootstrap CI for national
    print("\n  Computing bootstrap 95% CI (500 replications)...")
    boot_att, boot_lo, boot_hi = bootstrap_ci(data, province_filter=None, n_boot=500)
    if boot_att is not None:
        results["national"]["boot_att"] = boot_att
        results["national"]["boot_ci_lower"] = boot_lo
        results["national"]["boot_ci_upper"] = boot_hi
        print(f"    Bootstrap ATT: R{boot_att:,.2f}")
        print(f"    Bootstrap 95% CI: [R{boot_lo:,.2f}, R{boot_hi:,.2f}]")

    # ---- Provincial Analysis ----
    results["provincial"] = {}
    print("\n" + "=" * 50)
    print("PROVINCIAL ANALYSIS")
    print("=" * 50)

    for pcode, pname in sorted(province_names.items()):
        print(f"\n  --- {pname} (Province {pcode}) ---")
        prov_result = nearest_neighbour_match(data, caliper=0.75, province_filter=float(pcode))
        if prov_result is None:
            print("    Insufficient data for matching")
            results["provincial"][pname] = None
            continue

        results["provincial"][pname] = prov_result
        r = prov_result
        sig = "***" if r["p_value_paired_t"] < 0.001 else ("**" if r["p_value_paired_t"] < 0.01 else ("*" if r["p_value_paired_t"] < 0.05 else ""))
        print(f"    Matched: {r['n_matched']}/{r['n_treated_total']} treated ({r['match_rate']}%)")
        print(f"    ATT: R{r['att']:,.2f} (SE: R{r['se']:,.2f}) {sig}")
        print(f"    95% CI: [R{r['ci_lower']:,.2f}, R{r['ci_upper']:,.2f}]")
        print(f"    Paired t p-value: {r['p_value_paired_t']:.4e}")
        print(f"    Cohen's d: {r['cohens_d']:.4f}")
        print(f"    Mean treated: R{r['mean_treated_matched']:,.2f} | Mean control: R{r['mean_control_matched']:,.2f}")

    # ---- Sensitivity: matching only among those with non-zero health expenditure ----
    print("\n" + "=" * 50)
    print("SENSITIVITY ANALYSIS: Only HH with health expenditure > 0")
    print("=" * 50)

    mask_nonzero = data["health_exp"] > 0
    data_nz = {}
    idx_nz = np.where(mask_nonzero)[0]
    for key in data:
        if isinstance(data[key], np.ndarray):
            data_nz[key] = data[key][idx_nz]
        else:
            data_nz[key] = [data[key][i] for i in idx_nz]

    sens_result = nearest_neighbour_match(data_nz, caliper=0.5)
    results["sensitivity_nonzero"] = sens_result

    if sens_result:
        r = sens_result
        print(f"  N with health exp > 0: {len(idx_nz)} (treated: {r['n_treated_total']}, control: {r['n_control_total']})")
        print(f"  Matched pairs: {r['n_matched']}")
        print(f"  ATT: R{r['att']:,.2f} (SE: R{r['se']:,.2f})")
        print(f"  95% CI: [R{r['ci_lower']:,.2f}, R{r['ci_upper']:,.2f}]")
        print(f"  Paired t p-value: {r['p_value_paired_t']:.4e}")
        print(f"  Cohen's d: {r['cohens_d']:.4f}")
        print(f"  Mean treated: R{r['mean_treated_matched']:,.2f} | Mean control: R{r['mean_control_matched']:,.2f}")

    # ---- Sensitivity: with exact province matching ----
    print("\n" + "=" * 50)
    print("SENSITIVITY ANALYSIS: Exact province matching (national)")
    print("=" * 50)

    # Match within each province, then pool
    pooled_atts = []
    pooled_ns = []
    for pcode in range(1, 10):
        r = nearest_neighbour_match(data, caliper=0.75, province_filter=float(pcode))
        if r:
            pooled_atts.append(r["att"])
            pooled_ns.append(r["n_matched"])

    pooled_atts = np.array(pooled_atts)
    pooled_ns = np.array(pooled_ns)
    pooled_att = np.average(pooled_atts, weights=pooled_ns)
    pooled_se = np.sqrt(np.sum((pooled_ns / pooled_ns.sum()) ** 2 * np.array([
        nearest_neighbour_match(data, caliper=0.75, province_filter=float(p))["se"] ** 2
        for p in range(1, 10)
        if nearest_neighbour_match(data, caliper=0.75, province_filter=float(p)) is not None
    ])))

    results["sensitivity_exact_province"] = {
        "pooled_att": round(float(pooled_att), 2),
        "pooled_se": round(float(pooled_se), 2),
        "total_matched": int(pooled_ns.sum()),
        "ci_lower": round(float(pooled_att - 1.96 * pooled_se), 2),
        "ci_upper": round(float(pooled_att + 1.96 * pooled_se), 2),
    }

    print(f"  Pooled ATT (province-exact): R{pooled_att:,.2f}")
    print(f"  Pooled SE: R{pooled_se:,.2f}")
    print(f"  95% CI: [R{pooled_att - 1.96 * pooled_se:,.2f}, R{pooled_att + 1.96 * pooled_se:,.2f}]")
    print(f"  Total matched pairs: {int(pooled_ns.sum())}")

    # Save results
    # Convert numpy types for JSON serialization
    def convert(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    with open("analysis_results.json", "w") as f:
        json.dump(results, f, indent=2, default=convert)

    print(f"\nResults saved to analysis_results.json")
    return results


if __name__ == "__main__":
    main()
