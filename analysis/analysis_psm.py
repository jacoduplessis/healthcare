"""
Propensity Score Matching and NNM Sensitivity Analysis
======================================================
Primary estimator: PSM (logistic regression → 1:1 nearest-neighbor
matching on logit propensity score with caliper).
Sensitivity: Mahalanobis NNM (from analysis_dual.py).

Both IES 2010/11 and IES 2022/23.  National + provincial.

Outputs: analysis_psm_results.json
"""

import json
import sqlite3
import sys
import warnings

import numpy as np
from scipy import stats
from scipy.spatial import KDTree

warnings.filterwarnings("ignore", category=RuntimeWarning)

DB_2023 = "../ies2023.db"
DB_2011 = "../ies2011.db"

CPI_FACTOR_2011_TO_2023 = 1.7271

PROVINCE_NAMES = {
    1: "Western Cape", 2: "Eastern Cape", 3: "Northern Cape",
    4: "Free State", 5: "KwaZulu-Natal", 6: "North West",
    7: "Gauteng", 8: "Mpumalanga", 9: "Limpopo",
}


# ── Data Loading (reused from analysis_dual) ──────────────────────


def load_data_2023():
    conn = sqlite3.connect(DB_2023)
    rows = conn.execute("""
        SELECT h.uqno, h.eoh_meds,
               CAST(h.expenditure AS REAL), CAST(h.income AS REAL),
               CAST(h.hsize AS INTEGER), CAST(h.head_age AS INTEGER),
               h.head_sex, h.head_population, h.head_education,
               g.province, g.settlement_type,
               COALESCE(th.health_exp, 0), CAST(h.hhold_wgt AS REAL)
        FROM households h
        JOIN geography g ON h.uqno = g.uqno
        LEFT JOIN (SELECT uqno, SUM(valueannualized_adj) AS health_exp
                   FROM total WHERE division = '06' GROUP BY uqno) th ON h.uqno = th.uqno
        WHERE h.eoh_meds IN ('1','2')
          AND CAST(h.expenditure AS REAL) > 0
          AND CAST(h.head_age AS INTEGER) > 0
          AND h.head_population IN ('1','2','3','4')
          AND h.head_education NOT IN ('98','99')
    """).fetchall()
    conn.close()
    return _rows_to_data(rows)


def load_data_2011():
    conn = sqlite3.connect(DB_2011)
    rows = conn.execute("""
        SELECT h.uqno, h.q31021medaid,
               CAST(h.consumptions AS REAL), CAST(h.income AS REAL),
               CAST(h.hsize AS INTEGER), CAST(p.q14age AS INTEGER),
               h.genderofhead, h.popgrpofhead, p.q21highestlevel,
               h.province, h.settlement_type,
               COALESCE(th.health_exp, 0), CAST(h.full_calwgt AS REAL)
        FROM households h
        LEFT JOIN (SELECT uqno, q14age, q21highestlevel
                   FROM persons WHERE q15relationship = '1'
                   GROUP BY uqno HAVING MIN(personno)) p ON h.uqno = p.uqno
        LEFT JOIN (SELECT uqno, SUM(valueannualized) AS health_exp
                   FROM total WHERE division = '06' GROUP BY uqno) th ON h.uqno = th.uqno
        WHERE h.q31021medaid IN ('1','2')
          AND CAST(h.consumptions AS REAL) > 0
          AND p.q14age IS NOT NULL AND CAST(p.q14age AS INTEGER) > 0
          AND h.popgrpofhead IN ('1','2','3','4')
          AND p.q21highestlevel NOT IN ('98','99')
    """).fetchall()
    conn.close()
    return _rows_to_data(rows)


def _rows_to_data(rows):
    cols = ["uqno", "treatment_var", "expenditure", "income", "hsize",
            "head_age", "head_sex", "head_population", "head_education",
            "province", "settlement_type", "health_exp", "hhold_wgt"]
    data = {c: [] for c in cols}
    for row in rows:
        for c, v in zip(cols, row):
            data[c].append(v)

    n = len(data["uqno"])
    r = {}
    r["uqno"] = data["uqno"]
    r["treated"] = np.array([1 if str(x) == "1" else 0 for x in data["treatment_var"]])
    r["health_exp"] = np.array(data["health_exp"], dtype=float)
    r["hhold_wgt"] = np.array(data["hhold_wgt"], dtype=float)
    r["log_expenditure"] = np.log(np.array(data["expenditure"], dtype=float) + 1)
    r["log_income"] = np.log(np.array(data["income"], dtype=float) + 1)
    r["hsize"] = np.array(data["hsize"], dtype=float)
    r["head_age"] = np.array(data["head_age"], dtype=float)
    r["head_sex"] = np.array([int(x) for x in data["head_sex"]], dtype=float)
    r["head_population"] = np.array([int(x) for x in data["head_population"]], dtype=float)

    def edu_group(e):
        try:
            e = int(e)
        except (ValueError, TypeError):
            return 0
        if e == 0: return 0
        if e <= 7: return 1
        if e <= 12: return 2
        if e <= 20: return 3
        if e <= 27: return 4
        return 0

    r["education_group"] = np.array([edu_group(x) for x in data["head_education"]], dtype=float)
    r["province"] = np.array([int(x) for x in data["province"]], dtype=float)
    r["settlement_type"] = np.array([int(x) for x in data["settlement_type"]], dtype=float)

    print(f"  Loaded {n} households: {int(r['treated'].sum())} treated, "
          f"{n - int(r['treated'].sum())} control")
    return r


COV_NAMES = ["log_expenditure", "log_income", "hsize", "head_age",
             "head_sex", "head_population", "education_group", "settlement_type"]


def build_X(data, indices=None):
    if indices is None:
        indices = np.arange(len(data["treated"]))
    return np.column_stack([data[c][indices] for c in COV_NAMES])


# ── Logistic Regression (pure NumPy — no sklearn dependency) ──────


def _sigmoid(z):
    z = np.clip(z, -500, 500)
    return 1.0 / (1.0 + np.exp(-z))


def logistic_regression(X, y, max_iter=200, lr=0.05, tol=1e-8):
    """
    Fit logistic regression via IRLS (iteratively reweighted least squares).
    Returns coefficient vector (intercept last).
    """
    n, p = X.shape
    # Add intercept
    Xa = np.column_stack([X, np.ones(n)])
    beta = np.zeros(Xa.shape[1])

    for it in range(max_iter):
        mu = _sigmoid(Xa @ beta)
        # Clamp to avoid 0/1
        mu = np.clip(mu, 1e-10, 1 - 1e-10)
        W = mu * (1 - mu)
        # IRLS step: beta_new = beta + (X'WX)^-1 X'(y - mu)
        r = y - mu
        XtW = Xa.T * W
        H = XtW @ Xa
        # Regularise for stability
        H += 1e-6 * np.eye(H.shape[0])
        try:
            delta = np.linalg.solve(H, Xa.T @ r)
        except np.linalg.LinAlgError:
            delta = np.linalg.lstsq(H, Xa.T @ r, rcond=None)[0]
        beta += delta
        if np.max(np.abs(delta)) < tol:
            break

    return beta


def predict_propensity(data, indices=None):
    """Estimate propensity scores via logistic regression."""
    if indices is None:
        indices = np.arange(len(data["treated"]))
    X = build_X(data, indices)
    y = data["treated"][indices]

    # Standardise covariates for numerical stability
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd[sd == 0] = 1
    Xs = (X - mu) / sd

    beta = logistic_regression(Xs, y)
    Xa = np.column_stack([Xs, np.ones(len(indices))])
    ps = _sigmoid(Xa @ beta)
    logit_ps = np.log(ps / (1 - ps + 1e-15) + 1e-15)

    return ps, logit_ps, beta


# ── PSM Matching ──────────────────────────────────────────────────


def psm_match(data, caliper_sd=0.2, province_filter=None):
    """
    1:1 propensity-score matching without replacement.
    Caliper = caliper_sd × SD(logit PS)  (Austin, 2011).
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

    # Estimate propensity scores on the analysis sample
    ps, logit_ps, beta = predict_propensity(data, indices)

    # Map indices back to local positions
    local_treated = np.array([np.searchsorted(indices, t) for t in treated_idx])
    local_control = np.array([np.searchsorted(indices, c) for c in control_idx])

    logit_treated = logit_ps[local_treated]
    logit_control = logit_ps[local_control]
    ps_treated = ps[local_treated]
    ps_control = ps[local_control]

    # Caliper on logit scale
    caliper = caliper_sd * np.std(logit_ps)

    # Common support
    ps_min = max(ps_treated.min(), ps_control.min())
    ps_max = min(ps_treated.max(), ps_control.max())
    in_support_t = (ps_treated >= ps_min) & (ps_treated <= ps_max)
    in_support_c = (ps_control >= ps_min) & (ps_control <= ps_max)

    # Build KDTree on control logit PS (1-D)
    tree = KDTree(logit_control.reshape(-1, 1))

    matched_t = []
    matched_c = []
    used = set()

    rng = np.random.RandomState(42)
    order = rng.permutation(len(treated_idx))

    for i in order:
        if not in_support_t[i]:
            continue
        dists, nns = tree.query(logit_treated[i:i+1].reshape(1, 1),
                                k=min(20, len(control_idx)))
        dists = dists.ravel()
        nns = nns.ravel()
        for nn, d in zip(nns, dists):
            if nn not in used and d <= caliper and in_support_c[nn]:
                matched_t.append(treated_idx[i])
                matched_c.append(control_idx[nn])
                used.add(nn)
                break

    matched_t = np.array(matched_t)
    matched_c = np.array(matched_c)

    if len(matched_t) < 5:
        return None

    # ── Outcomes ──
    y_t = data["health_exp"][matched_t]
    y_c = data["health_exp"][matched_c]
    diff = y_t - y_c
    att = float(np.mean(diff))
    se = float(np.std(diff, ddof=1) / np.sqrt(len(diff)))

    t_stat, p_t = stats.ttest_rel(y_t, y_c)
    try:
        _, p_w = stats.wilcoxon(y_t, y_c, alternative="two-sided")
    except ValueError:
        p_w = np.nan

    # ── Balance ──
    X_mt = build_X(data, matched_t)
    X_mc = build_X(data, matched_c)
    X_ut = build_X(data, treated_idx)
    X_uc = build_X(data, control_idx)

    balance = []
    for j, name in enumerate(COV_NAMES):
        ps_before = np.sqrt((X_ut[:, j].var() + X_uc[:, j].var()) / 2)
        smd_b = (X_ut[:, j].mean() - X_uc[:, j].mean()) / ps_before if ps_before > 0 else 0
        ps_after = np.sqrt((X_mt[:, j].var() + X_mc[:, j].var()) / 2)
        smd_a = (X_mt[:, j].mean() - X_mc[:, j].mean()) / ps_after if ps_after > 0 else 0
        balance.append({
            "covariate": name,
            "smd_before": round(smd_b, 4),
            "smd_after": round(smd_a, 4),
            "reduction_pct": round((1 - abs(smd_a) / max(abs(smd_b), 1e-10)) * 100, 1),
        })

    # ── PS diagnostics ──
    ps_diag = {
        "ps_mean_treated": round(float(ps_treated.mean()), 4),
        "ps_mean_control": round(float(ps_control.mean()), 4),
        "ps_sd_overall": round(float(np.std(logit_ps)), 4),
        "caliper_logit": round(float(caliper), 4),
        "common_support_min": round(float(ps_min), 4),
        "common_support_max": round(float(ps_max), 4),
        "n_treated_in_support": int(in_support_t.sum()),
        "n_treated_outside_support": int((~in_support_t).sum()),
    }

    return {
        "method": "PSM",
        "n_treated_total": int(len(treated_idx)),
        "n_control_total": int(len(control_idx)),
        "n_matched": int(len(matched_t)),
        "match_rate": round(len(matched_t) / len(treated_idx) * 100, 1),
        "mean_treated_unmatched": round(float(data["health_exp"][treated_idx].mean()), 2),
        "mean_control_unmatched": round(float(data["health_exp"][control_idx].mean()), 2),
        "naive_diff": round(float(data["health_exp"][treated_idx].mean() -
                                   data["health_exp"][control_idx].mean()), 2),
        "mean_treated_matched": round(float(y_t.mean()), 2),
        "mean_control_matched": round(float(y_c.mean()), 2),
        "att": round(att, 2),
        "se": round(se, 2),
        "ci_lower": round(att - 1.96 * se, 2),
        "ci_upper": round(att + 1.96 * se, 2),
        "t_stat": round(float(t_stat), 4),
        "p_value_paired_t": float(p_t),
        "p_value_wilcoxon": float(p_w) if not np.isnan(p_w) else None,
        "median_treated_matched": round(float(np.median(y_t)), 2),
        "median_control_matched": round(float(np.median(y_c)), 2),
        "pct_treated_any_spend": round(float((y_t > 0).mean() * 100), 1),
        "pct_control_any_spend": round(float((y_c > 0).mean() * 100), 1),
        "cohens_d": round(float(att / (np.std(diff, ddof=1) if np.std(diff, ddof=1) > 0 else 1)), 4),
        "balance": balance,
        "ps_diagnostics": ps_diag,
    }


# ── Mahalanobis NNM (sensitivity) ─────────────────────────────────


def nnm_match(data, caliper=0.5, province_filter=None):
    """1:1 NNM without replacement on standardised covariates."""
    if province_filter is not None:
        mask = data["province"] == province_filter
        indices = np.where(mask)[0]
    else:
        indices = np.arange(len(data["treated"]))

    treated_idx = indices[data["treated"][indices] == 1]
    control_idx = indices[data["treated"][indices] == 0]
    if len(treated_idx) < 5 or len(control_idx) < 5:
        return None

    X_all = build_X(data, indices)
    X_t = build_X(data, treated_idx)
    X_c = build_X(data, control_idx)

    mu = X_all.mean(axis=0)
    sd = X_all.std(axis=0); sd[sd == 0] = 1
    X_ts = (X_t - mu) / sd
    X_cs = (X_c - mu) / sd

    tree = KDTree(X_cs)
    dists, nns = tree.query(X_ts, k=min(10, len(control_idx)))

    matched_t, matched_c, used = [], [], set()
    rng = np.random.RandomState(42)
    for i in rng.permutation(len(treated_idx)):
        cands = nns[i] if nns.ndim > 1 else [nns[i]]
        ds = dists[i] if dists.ndim > 1 else [dists[i]]
        for c, d in zip(cands, ds):
            if c not in used and d <= caliper * X_ts.shape[1]:
                matched_t.append(treated_idx[i])
                matched_c.append(control_idx[c])
                used.add(c)
                break

    matched_t = np.array(matched_t)
    matched_c = np.array(matched_c)
    if len(matched_t) < 5:
        return None

    y_t = data["health_exp"][matched_t]
    y_c = data["health_exp"][matched_c]
    diff = y_t - y_c
    att = float(np.mean(diff))
    se = float(np.std(diff, ddof=1) / np.sqrt(len(diff)))
    t_stat, p_t = stats.ttest_rel(y_t, y_c)
    try:
        _, p_w = stats.wilcoxon(y_t, y_c, alternative="two-sided")
    except ValueError:
        p_w = np.nan

    # Balance
    X_mt = build_X(data, matched_t)
    X_mc = build_X(data, matched_c)
    X_ut = build_X(data, treated_idx)
    X_uc = build_X(data, control_idx)
    balance = []
    for j, name in enumerate(COV_NAMES):
        ps_b = np.sqrt((X_ut[:, j].var() + X_uc[:, j].var()) / 2)
        smd_b = (X_ut[:, j].mean() - X_uc[:, j].mean()) / ps_b if ps_b > 0 else 0
        ps_a = np.sqrt((X_mt[:, j].var() + X_mc[:, j].var()) / 2)
        smd_a = (X_mt[:, j].mean() - X_mc[:, j].mean()) / ps_a if ps_a > 0 else 0
        balance.append({
            "covariate": name,
            "smd_before": round(smd_b, 4),
            "smd_after": round(smd_a, 4),
            "reduction_pct": round((1 - abs(smd_a) / max(abs(smd_b), 1e-10)) * 100, 1),
        })

    return {
        "method": "NNM",
        "n_treated_total": int(len(treated_idx)),
        "n_control_total": int(len(control_idx)),
        "n_matched": int(len(matched_t)),
        "match_rate": round(len(matched_t) / len(treated_idx) * 100, 1),
        "mean_treated_matched": round(float(y_t.mean()), 2),
        "mean_control_matched": round(float(y_c.mean()), 2),
        "att": round(att, 2),
        "se": round(se, 2),
        "ci_lower": round(att - 1.96 * se, 2),
        "ci_upper": round(att + 1.96 * se, 2),
        "t_stat": round(float(t_stat), 4),
        "p_value_paired_t": float(p_t),
        "p_value_wilcoxon": float(p_w) if not np.isnan(p_w) else None,
        "pct_treated_any_spend": round(float((y_t > 0).mean() * 100), 1),
        "pct_control_any_spend": round(float((y_c > 0).mean() * 100), 1),
        "cohens_d": round(float(att / (np.std(diff, ddof=1) if np.std(diff, ddof=1) > 0 else 1)), 4),
        "balance": balance,
    }


# ── Bootstrap ─────────────────────────────────────────────────────


def bootstrap_ci(match_fn, data, n_boot=500, **kwargs):
    """Bootstrap CI for any matching function."""
    rng = np.random.RandomState(123)
    pf = kwargs.get("province_filter")
    if pf is not None:
        indices = np.where(data["province"] == pf)[0]
    else:
        indices = np.arange(len(data["treated"]))

    n = len(indices)
    atts = []
    for _ in range(n_boot):
        bi = rng.choice(indices, size=n, replace=True)
        bd = {}
        for k in data:
            if isinstance(data[k], np.ndarray):
                bd[k] = data[k][bi]
            else:
                bd[k] = [data[k][i] for i in bi]
        kw = {k: v for k, v in kwargs.items() if k != "province_filter"}
        res = match_fn(bd, **kw)
        if res is not None:
            atts.append(res["att"])

    if len(atts) < 50:
        return None, None, None
    atts = np.array(atts)
    return (round(float(np.mean(atts)), 2),
            round(float(np.percentile(atts, 2.5)), 2),
            round(float(np.percentile(atts, 97.5)), 2))


# ── Full analysis driver ──────────────────────────────────────────


def run_analysis(data, year_label):
    results = {"year": year_label}

    # ═══ NATIONAL: PSM (primary) ═══
    print(f"\n{'='*65}")
    print(f"  PSM NATIONAL — {year_label}")
    print(f"{'='*65}")

    psm = psm_match(data, caliper_sd=0.2)
    results["national_psm"] = psm

    if psm:
        print(f"  Sample: {psm['n_treated_total']} treated, {psm['n_control_total']} control")
        print(f"  PS diagnostics:")
        pd = psm["ps_diagnostics"]
        print(f"    Mean PS — treated: {pd['ps_mean_treated']:.4f}, control: {pd['ps_mean_control']:.4f}")
        print(f"    Caliper (0.2×SD logit): {pd['caliper_logit']:.4f}")
        print(f"    Common support: [{pd['common_support_min']:.4f}, {pd['common_support_max']:.4f}]")
        print(f"    Treated outside support: {pd['n_treated_outside_support']}")
        print(f"  Matched: {psm['n_matched']} ({psm['match_rate']}%)")
        print(f"  ATT: R{psm['att']:,.2f} (SE: R{psm['se']:,.2f})")
        print(f"  95% CI: [R{psm['ci_lower']:,.2f}, R{psm['ci_upper']:,.2f}]")
        print(f"  p-value: {psm['p_value_paired_t']:.2e}")
        print(f"  Cohen's d: {psm['cohens_d']:.4f}")
        print(f"  Utilisation — treated: {psm['pct_treated_any_spend']}%, "
              f"control: {psm['pct_control_any_spend']}%")
        print(f"\n  Balance:")
        print(f"    {'Covariate':<20} {'Before':>10} {'After':>10} {'% Red':>8}")
        for b in psm["balance"]:
            print(f"    {b['covariate']:<20} {b['smd_before']:>10.4f} "
                  f"{b['smd_after']:>10.4f} {b['reduction_pct']:>7.1f}%")

        # Bootstrap
        print(f"\n  Bootstrap CI (500 reps)...")
        ba, bl, bh = bootstrap_ci(psm_match, data, n_boot=500, caliper_sd=0.2)
        if ba is not None:
            psm["boot_att"] = ba; psm["boot_ci_lower"] = bl; psm["boot_ci_upper"] = bh
            print(f"  Bootstrap ATT: R{ba:,.2f} [{bl:,.2f}, {bh:,.2f}]")

    # ═══ NATIONAL: NNM (sensitivity) ═══
    print(f"\n{'='*65}")
    print(f"  NNM SENSITIVITY — {year_label}")
    print(f"{'='*65}")

    nnm = nnm_match(data, caliper=0.5)
    results["national_nnm"] = nnm

    if nnm:
        print(f"  Matched: {nnm['n_matched']} ({nnm['match_rate']}%)")
        print(f"  ATT: R{nnm['att']:,.2f} (SE: R{nnm['se']:,.2f})")
        print(f"  95% CI: [R{nnm['ci_lower']:,.2f}, R{nnm['ci_upper']:,.2f}]")
        print(f"  p-value: {nnm['p_value_paired_t']:.2e}")
        print(f"  Cohen's d: {nnm['cohens_d']:.4f}")
        ba, bl, bh = bootstrap_ci(nnm_match, data, n_boot=500, caliper=0.5)
        if ba is not None:
            nnm["boot_att"] = ba; nnm["boot_ci_lower"] = bl; nnm["boot_ci_upper"] = bh
            print(f"  Bootstrap ATT: R{ba:,.2f} [{bl:,.2f}, {bh:,.2f}]")

    # ═══ SENSITIVITY: positive OOP only (PSM) ═══
    print(f"\n  Sensitivity: PSM on positive-OOP subsample...")
    mask_nz = data["health_exp"] > 0
    idx_nz = np.where(mask_nz)[0]
    data_nz = {k: (data[k][idx_nz] if isinstance(data[k], np.ndarray)
                    else [data[k][i] for i in idx_nz]) for k in data}
    sens_nz = psm_match(data_nz, caliper_sd=0.2)
    results["sensitivity_nonzero_psm"] = sens_nz
    if sens_nz:
        print(f"  ATT (OOP>0): R{sens_nz['att']:,.2f} (p={sens_nz['p_value_paired_t']:.2e})")

    # ═══ SENSITIVITY: exact province matching (PSM) ═══
    print(f"  Sensitivity: PSM with exact province matching...")
    pooled_atts, pooled_ns, pooled_ses = [], [], []
    for pc in range(1, 10):
        r = psm_match(data, caliper_sd=0.2, province_filter=float(pc))
        if r:
            pooled_atts.append(r["att"])
            pooled_ns.append(r["n_matched"])
            pooled_ses.append(r["se"])
    if pooled_atts:
        pa = np.array(pooled_atts); pn = np.array(pooled_ns); pe = np.array(pooled_ses)
        p_att = float(np.average(pa, weights=pn))
        p_se = float(np.sqrt(np.sum((pn / pn.sum())**2 * pe**2)))
        results["sensitivity_exact_province_psm"] = {
            "pooled_att": round(p_att, 2), "pooled_se": round(p_se, 2),
            "total_matched": int(pn.sum()),
            "ci_lower": round(p_att - 1.96 * p_se, 2),
            "ci_upper": round(p_att + 1.96 * p_se, 2),
        }
        print(f"  Pooled ATT: R{p_att:,.2f} [{p_att-1.96*p_se:,.2f}, {p_att+1.96*p_se:,.2f}]")

    # ═══ PROVINCIAL: PSM ═══
    results["provincial_psm"] = {}
    print(f"\n{'='*65}")
    print(f"  PROVINCIAL PSM — {year_label}")
    print(f"{'='*65}")
    print(f"  {'Province':<16} {'Matched':>8} {'ATT (R)':>10} {'SE':>8} {'p':>12} {'d':>8}")

    for pc, pn in sorted(PROVINCE_NAMES.items()):
        r = psm_match(data, caliper_sd=0.25, province_filter=float(pc))
        if r is None:
            print(f"  {pn:<16} Insufficient data")
            results["provincial_psm"][pn] = None
            continue
        results["provincial_psm"][pn] = r
        sig = "***" if r["p_value_paired_t"] < 0.001 else (
              "**"  if r["p_value_paired_t"] < 0.01 else (
              "*"   if r["p_value_paired_t"] < 0.05 else ""))
        print(f"  {pn:<16} {r['n_matched']:>5}/{r['n_treated_total']:<5} "
              f"R{r['att']:>9,.2f} {r['se']:>7,.2f} "
              f"{r['p_value_paired_t']:>11.2e} {r['cohens_d']:>7.3f} {sig}")

    # ═══ PROVINCIAL: NNM (sensitivity) ═══
    results["provincial_nnm"] = {}
    print(f"\n  Provincial NNM (sensitivity):")
    for pc, pn in sorted(PROVINCE_NAMES.items()):
        r = nnm_match(data, caliper=0.75, province_filter=float(pc))
        results["provincial_nnm"][pn] = r
        if r:
            sig = "***" if r["p_value_paired_t"] < 0.001 else (
                  "**"  if r["p_value_paired_t"] < 0.01 else (
                  "*"   if r["p_value_paired_t"] < 0.05 else ""))
            print(f"  {pn:<16} ATT: R{r['att']:>9,.2f} (d={r['cohens_d']:.3f}) {sig}")

    # ═══ Descriptives ═══
    t_mask = data["treated"] == 1
    c_mask = data["treated"] == 0
    results["descriptives"] = {
        "n_treated": int(t_mask.sum()),
        "n_control": int(c_mask.sum()),
        "mean_oop_treated": round(float(data["health_exp"][t_mask].mean()), 2),
        "mean_oop_control": round(float(data["health_exp"][c_mask].mean()), 2),
        "median_oop_treated": round(float(np.median(data["health_exp"][t_mask])), 2),
        "median_oop_control": round(float(np.median(data["health_exp"][c_mask])), 2),
        "pct_any_spend_treated": round(float((data["health_exp"][t_mask] > 0).mean() * 100), 1),
        "pct_any_spend_control": round(float((data["health_exp"][c_mask] > 0).mean() * 100), 1),
    }

    return results


# ── Main ──────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("  PSM + NNM DUAL-PERIOD ANALYSIS")
    print("=" * 65)

    print("\nLoading IES 2022/23...")
    d23 = load_data_2023()
    print("\nLoading IES 2010/11...")
    d11 = load_data_2011()

    r23 = run_analysis(d23, "IES 2022/23")
    r11 = run_analysis(d11, "IES 2010/11")

    # ═══ CROSS-PERIOD COMPARISON ═══
    print(f"\n{'='*65}")
    print(f"  CROSS-PERIOD COMPARISON (PSM)")
    print(f"{'='*65}")

    for lbl, key in [("National", "national_psm")]:
        a = r11.get(key, {})
        b = r23.get(key, {})
        if a and b:
            print(f"\n  {lbl}:")
            print(f"    {'':25} {'IES 2010/11':>15} {'IES 2022/23':>15}")
            print(f"    {'ATT (R)':25} {a['att']:>15,.2f} {b['att']:>15,.2f}")
            print(f"    {'SE':25} {a['se']:>15,.2f} {b['se']:>15,.2f}")
            print(f"    {'p-value':25} {a['p_value_paired_t']:>15.2e} {b['p_value_paired_t']:>15.2e}")
            print(f"    {'Cohen d':25} {a['cohens_d']:>15.4f} {b['cohens_d']:>15.4f}")
            print(f"    {'Matched pairs':25} {a['n_matched']:>15,} {b['n_matched']:>15,}")
            print(f"    {'Match rate':25} {a['match_rate']:>14.1f}% {b['match_rate']:>14.1f}%")
            print(f"    {'Util treated':25} {a['pct_treated_any_spend']:>14.1f}% {b['pct_treated_any_spend']:>14.1f}%")
            print(f"    {'Util control':25} {a['pct_control_any_spend']:>14.1f}% {b['pct_control_any_spend']:>14.1f}%")

    # Cross-period comparison for NNM
    print(f"\n  NNM Sensitivity:")
    a = r11.get("national_nnm", {})
    b = r23.get("national_nnm", {})
    if a and b:
        print(f"    {'ATT (R)':25} {a['att']:>15,.2f} {b['att']:>15,.2f}")
        print(f"    {'p-value':25} {a['p_value_paired_t']:>15.2e} {b['p_value_paired_t']:>15.2e}")

    all_results = {"ies_2023": r23, "ies_2011": r11}
    with open("analysis_psm_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nResults saved to analysis_psm_results.json")


if __name__ == "__main__":
    main()
