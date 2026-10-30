"""
================================================================================
FILE: scripts/02_cfa_and_descriptives.py
PURPOSE:
  - Generate descriptive statistics, country summaries, correlation matrices,
    and confirmatory factor analysis (CFA) measurement model deliverables for
    the DT092 Multigroup SEM Replication (Petrič & Just, 2025).
  - Deliverables:
    1. Table 1 Demographics: results/tables/table1_demographics.csv
    2. Table 1 Country Summary: results/tables/table1_country_summary.csv
    3. Table 2 CFA Measurement: results/tables/table2_cfa_measurement.csv
    4. Table 2 CFA Fit Indices: results/tables/table2_cfa_fit_indices.csv
    5. Table 3 Correlations: results/tables/table3_correlations.csv
    6. Table 4 Descriptives: results/tables/table4_descriptives.csv
    7. Execution Log: results/logs/02_cfa_and_descriptives.log
================================================================================
"""

import argparse
from datetime import datetime, timezone
import logging
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.stats import kurtosis, norm, skew
import semopy
from semopy import Model, calc_stats

# Reconfigure console output for UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Constants
CANONICAL_CONSTRUCTS = ["NORM", "AWARE", "KNOW", "COMM", "ATT", "RESP"]
VARIABLES_ORDER = ["REPORT", "ATT", "RESP", "KNOW", "COMM", "NORM", "AWARE", "TOOL"]
GROUPS = [("POOLED", None), ("DE", "DE"), ("UK", "UK"), ("US", "US")]

CFA_SPECIFICATION = """
NORM =~ NORM1 + NORM2 + NORM3 + NORM4
AWARE =~ AWARE1 + AWARE2 + AWARE3 + AWARE4
KNOW =~ KNOW1 + KNOW2 + KNOW3 + KNOW4
COMM =~ COMM1 + COMM2 + COMM3 + COMM4
ATT =~ ATT1 + ATT2 + ATT3 + ATT4
RESP =~ RESP1 + RESP2 + RESP3 + RESP4
"""


def setup_logging(log_file: Optional[Path] = None, verbose: bool = False) -> logging.Logger:
    """Configure unified logging for console and file."""
    logger = logging.getLogger("cfa_and_descriptives")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.propagate = False
    logger.handlers.clear()

    fmt = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG if verbose else logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_file, mode="w", encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger


def compute_composite_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute unweighted composite mean scores for the 6 latent constructs.
    Single-item indicators (TOOL and REPORT) are preserved as-is.
    """
    df_calc = df.copy()
    for c in CANONICAL_CONSTRUCTS:
        item_cols = [f"{c}{i}" for i in range(1, 5)]
        df_calc[c] = df_calc[item_cols].mean(axis=1)
    return df_calc


def build_table1_demographics(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Build Table 1 Demographics following the canonical 10-column schema
    required by spec.md and test_tier1_feature_coverage.py:
    variable_category,subcategory,pooled_n,pooled_pct,germany_n,germany_pct,uk_n,uk_pct,usa_n,usa_pct

    Also produces companion table1_country_summary.csv with tool prevalence
    and REPORT statistics per country.
    """
    n_total = len(df)
    n_de = int((df["country"] == "DE").sum())
    n_uk = int((df["country"] == "UK").sum())
    n_us = int((df["country"] == "US").sum())

    rows: List[Dict[str, Any]] = []

    # 1. Sample Size category
    rows.append({
        "variable_category": "Sample Size",
        "subcategory": "Total Respondents",
        "pooled_n": n_total,
        "pooled_pct": 100.0,
        "germany_n": n_de,
        "germany_pct": round(n_de / n_total * 100, 2),
        "uk_n": n_uk,
        "uk_pct": round(n_uk / n_total * 100, 2),
        "usa_n": n_us,
        "usa_pct": round(n_us / n_total * 100, 2),
    })

    # 2. Reporting Tool Availability category
    for t_val, t_lbl in [(1, "Tool Available (TOOL=1)"), (0, "Tool Absent (TOOL=0)")]:
        p_n = int((df["TOOL"] == t_val).sum())
        de_n = int(((df["country"] == "DE") & (df["TOOL"] == t_val)).sum())
        uk_n = int(((df["country"] == "UK") & (df["TOOL"] == t_val)).sum())
        us_n = int(((df["country"] == "US") & (df["TOOL"] == t_val)).sum())
        rows.append({
            "variable_category": "Reporting Tool",
            "subcategory": t_lbl,
            "pooled_n": p_n,
            "pooled_pct": round(p_n / n_total * 100, 2),
            "germany_n": de_n,
            "germany_pct": round(de_n / n_de * 100, 2),
            "uk_n": uk_n,
            "uk_pct": round(uk_n / n_uk * 100, 2),
            "usa_n": us_n,
            "usa_pct": round(us_n / n_us * 100, 2),
        })

    # 3. Reporting Behavior category (Likert ratings 1 to 5)
    report_labels = {
        1: "1 - Never",
        2: "2 - Rarely",
        3: "3 - Occasionally",
        4: "4 - Frequently",
        5: "5 - Very Frequently",
    }
    for r_val, r_lbl in report_labels.items():
        p_n = int((df["REPORT"] == r_val).sum())
        de_n = int(((df["country"] == "DE") & (df["REPORT"] == r_val)).sum())
        uk_n = int(((df["country"] == "UK") & (df["REPORT"] == r_val)).sum())
        us_n = int(((df["country"] == "US") & (df["REPORT"] == r_val)).sum())
        rows.append({
            "variable_category": "Reporting Behavior (REPORT)",
            "subcategory": r_lbl,
            "pooled_n": p_n,
            "pooled_pct": round(p_n / n_total * 100, 2),
            "germany_n": de_n,
            "germany_pct": round(de_n / n_de * 100, 2),
            "uk_n": uk_n,
            "uk_pct": round(uk_n / n_uk * 100, 2),
            "usa_n": us_n,
            "usa_pct": round(us_n / n_us * 100, 2),
        })

    df_canon = pd.DataFrame(rows)

    # Companion summary table
    summary_rows: List[Dict[str, Any]] = []
    for c_code, c_name in [
        ("DE", "Germany (DE)"),
        ("UK", "United Kingdom (UK)"),
        ("US", "United States (US)"),
        (None, "Pooled Sample (ALL)"),
    ]:
        sub = df if c_code is None else df[df["country"] == c_code]
        t_cnt = int((sub["TOOL"] == 1).sum())
        summary_rows.append({
            "country": c_name,
            "n": len(sub),
            "percentage": round(len(sub) / n_total * 100, 2),
            "tool_available_n": t_cnt,
            "tool_available_pct": round(t_cnt / len(sub) * 100, 2),
            "report_mean": round(float(sub["REPORT"].mean()), 4),
            "report_sd": round(float(sub["REPORT"].std(ddof=1)), 4),
        })

    df_summary = pd.DataFrame(summary_rows)
    return df_canon, df_summary


def build_table4_descriptives(df_calc: pd.DataFrame) -> pd.DataFrame:
    """
    Build Table 4 Descriptive Statistics across 4 groups (POOLED, DE, UK, US)
    and 8 variables (REPORT, ATT, RESP, KNOW, COMM, NORM, AWARE, TOOL).
    Schema: group,variable,mean,sd,scale_min,scale_max,skewness,kurtosis
    """
    rows: List[Dict[str, Any]] = []
    for grp_label, c_filter in GROUPS:
        sub = df_calc if c_filter is None else df_calc[df_calc["country"] == c_filter]
        for v in VARIABLES_ORDER:
            vals = sub[v]
            s_min = 0.0 if v == "TOOL" else 1.0
            s_max = 1.0 if v == "TOOL" else 5.0
            rows.append({
                "group": grp_label,
                "variable": v,
                "mean": round(float(vals.mean()), 4),
                "sd": round(float(vals.std(ddof=1)), 4),
                "scale_min": s_min,
                "scale_max": s_max,
                "skewness": round(float(skew(vals, bias=False)), 4),
                "kurtosis": round(float(kurtosis(vals, bias=False)), 4),
            })

    return pd.DataFrame(rows)


def build_table3_correlations(df_calc: pd.DataFrame) -> pd.DataFrame:
    """
    Build Table 3 Pearson Correlation Matrices across 4 groups (POOLED, DE, UK, US).
    Schema: group,variable,REPORT,ATT,RESP,KNOW,COMM,NORM,AWARE,TOOL
    """
    rows: List[Dict[str, Any]] = []
    for grp_label, c_filter in GROUPS:
        sub = df_calc if c_filter is None else df_calc[df_calc["country"] == c_filter]
        corr_matrix = sub[VARIABLES_ORDER].corr(method="pearson")
        for v in VARIABLES_ORDER:
            row_dict: Dict[str, Any] = {"group": grp_label, "variable": v}
            for target_v in VARIABLES_ORDER:
                row_dict[target_v] = round(float(corr_matrix.loc[v, target_v]), 4)
            rows.append(row_dict)

    return pd.DataFrame(rows)


def compute_cronbach_alpha(df_items: pd.DataFrame) -> float:
    """
    Compute Cronbach's Alpha internal consistency reliability.
    alpha = (k / (k - 1)) * (1 - sum(var_i) / var_total)
    """
    k = df_items.shape[1]
    if k < 2:
        return 1.0
    item_vars = df_items.var(axis=0, ddof=1).sum()
    total_var = df_items.sum(axis=1).var(ddof=1)
    if total_var == 0.0 or np.isnan(total_var):
        return 0.0
    alpha = (k / (k - 1.0)) * (1.0 - (item_vars / total_var))
    return float(max(0.0, alpha))


def compute_exact_srmr(model: Model) -> float:
    """
    Compute exact Standardized Root Mean Square Residual (SRMR) from
    model-implied covariance matrix (model.calc_sigma()) and
    sample covariance matrix (model.mx_cov).
    """
    sigma, _ = model.calc_sigma()
    s = model.mx_cov
    p = s.shape[0]

    d_s = np.sqrt(np.diag(s))
    d_sigma = np.sqrt(np.diag(sigma))

    r_s = s / np.outer(d_s, d_s)
    r_sigma = sigma / np.outer(d_sigma, d_sigma)

    tril_indices = np.tril_indices(p, k=0)
    residuals = (r_s - r_sigma)[tril_indices]
    return float(np.sqrt(np.mean(residuals ** 2)))


def estimate_cfa_and_reliability(
    df: pd.DataFrame, logger: logging.Logger
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Fit CFA measurement model using semopy with MLW estimator on the pooled sample.
    Extract standardized factor loadings, delta-method marker SEs and p-values,
    Cronbach's alpha, Composite Reliability (CR), Average Variance Extracted (AVE),
    and exact SRMR.

    Returns:
      df_cfa_measurement: 24 indicator rows with factor loadings and reliabilities
      df_cfa_fit_indices: Model fit indices across Pooled and country subsamples
    """
    logger.info("Fitting CFA measurement model on pooled dataset (N=%d)...", len(df))
    model = Model(CFA_SPECIFICATION)
    model.fit(df)

    # 1. Fit Indices
    stats_df = calc_stats(model)
    chi2_val = float(stats_df.loc["Value", "chi2"])
    df_val = int(stats_df.loc["Value", "DoF"])
    p_val_chi2 = float(stats_df.loc["Value", "chi2 p-value"])
    cfi_val = float(min(1.0, stats_df.loc["Value", "CFI"]))
    tli_val = float(min(1.0, stats_df.loc["Value", "TLI"]))
    rmsea_val = float(stats_df.loc["Value", "RMSEA"])
    aic_val = float(stats_df.loc["Value", "AIC"])
    bic_val = float(stats_df.loc["Value", "BIC"])
    srmr_val = compute_exact_srmr(model)

    logger.info(
        "Pooled CFA Fit: chi2=%.4f (df=%d, p=%.4f), CFI=%.4f, TLI=%.4f, RMSEA=%.4f, SRMR=%.4f",
        chi2_val,
        df_val,
        p_val_chi2,
        cfi_val,
        tli_val,
        rmsea_val,
        srmr_val,
    )

    # 2. Inspect estimates and precompute delta-method standard errors for marker variables
    insp = model.inspect(std_est=True)

    marker_se_dict: Dict[str, Tuple[float, float, float]] = {}
    for c in CANONICAL_CONSTRUCTS:
        cov_row = insp[
            (insp["op"] == "~~") & (insp["lval"] == c) & (insp["rval"] == c)
        ].iloc[0]
        psi = float(cov_row["Estimate"])
        psi_se = float(cov_row["Std. Err"])

        marker_item = f"{c}1"
        item_sd = float(df[marker_item].std(ddof=1))
        marker_row = insp[
            (insp["op"] == "~") & (insp["lval"] == marker_item) & (insp["rval"] == c)
        ].iloc[0]
        std_l = float(marker_row["Est. Std"])

        # Delta method for standardized loading: se = se_psi / (2 * sqrt(psi) * sd_item)
        se_marker = psi_se / (2.0 * np.sqrt(psi) * item_sd)
        z_marker = std_l / se_marker
        p_marker = 2.0 * (1.0 - norm.cdf(abs(z_marker)))
        marker_se_dict[marker_item] = (float(se_marker), float(z_marker), float(p_marker))

    # 3. Construct-level reliability and validity metrics
    construct_metrics: Dict[str, Dict[str, float]] = {}
    for c in CANONICAL_CONSTRUCTS:
        items = [f"{c}{i}" for i in range(1, 5)]
        alpha = compute_cronbach_alpha(df[items])

        c_loadings = insp[
            (insp["op"] == "~") & (insp["rval"] == c) & (insp["lval"].isin(items))
        ]
        c_loadings = c_loadings.set_index("lval").loc[items]
        lambdas = c_loadings["Est. Std"].astype(float).values

        sum_l = float(np.sum(lambdas))
        sum_l_sq = float(np.sum(lambdas ** 2))
        sum_theta = float(np.sum(1.0 - (lambdas ** 2)))

        cr = (sum_l ** 2) / ((sum_l ** 2) + sum_theta)
        ave = sum_l_sq / float(len(lambdas))
        sqrt_ave = float(np.sqrt(ave))

        construct_metrics[c] = {
            "alpha": float(alpha),
            "cr": float(cr),
            "ave": float(ave),
            "sqrt_ave": float(sqrt_ave),
        }
        logger.info(
            "Construct %s: alpha=%.4f, CR=%.4f, AVE=%.4f, sqrt(AVE)=%.4f",
            c,
            alpha,
            cr,
            ave,
            sqrt_ave,
        )

    # 4. Assemble Table 2 rows (24 indicators)
    measurement_rows: List[Dict[str, Any]] = []
    for c in CANONICAL_CONSTRUCTS:
        for i in range(1, 5):
            item_name = f"{c}{i}"
            item_row = insp[
                (insp["op"] == "~") & (insp["lval"] == item_name) & (insp["rval"] == c)
            ].iloc[0]

            unstd = float(item_row["Estimate"])
            std_l = float(item_row["Est. Std"])

            if item_name in marker_se_dict:
                se, z_val, p_val = marker_se_dict[item_name]
            else:
                se = float(item_row["Std. Err"])
                z_val = float(item_row["z-value"])
                p_val = float(item_row["p-value"])

            c_meta = construct_metrics[c]
            measurement_rows.append({
                "construct": c,
                "indicator": item_name,
                "unstd_loading": round(unstd, 4),
                "std_loading": round(std_l, 4),
                "std_error": round(se, 4),
                "z_value": round(z_val, 4),
                "p_value": round(p_val, 4),
                "cronbach_alpha": round(c_meta["alpha"], 4),
                "composite_reliability_CR": round(c_meta["cr"], 4),
                "ave": round(c_meta["ave"], 4),
                "sqrt_ave": round(c_meta["sqrt_ave"], 4),
                "fit_chi2": round(chi2_val, 4),
                "fit_df": df_val,
                "fit_cfi": round(cfi_val, 4),
                "fit_tli": round(tli_val, 4),
                "fit_rmsea": round(rmsea_val, 4),
                "fit_srmr": round(srmr_val, 4),
            })

    df_cfa_measurement = pd.DataFrame(measurement_rows)

    # 5. Fit Indices across Pooled and Country subsamples for table2_cfa_fit_indices.csv
    fit_rows: List[Dict[str, Any]] = []
    fit_rows.append({
        "group": "POOLED",
        "sample_size": len(df),
        "chi2": round(chi2_val, 4),
        "df": df_val,
        "p_value": round(p_val_chi2, 4),
        "cfi": round(cfi_val, 4),
        "tli": round(tli_val, 4),
        "rmsea": round(rmsea_val, 4),
        "srmr": round(srmr_val, 4),
        "aic": round(aic_val, 4),
        "bic": round(bic_val, 4),
    })

    for grp_code in ["DE", "UK", "US"]:
        sub_df = df[df["country"] == grp_code]
        sub_m = Model(CFA_SPECIFICATION)
        sub_m.fit(sub_df)
        st = calc_stats(sub_m)
        grp_srmr = compute_exact_srmr(sub_m)
        fit_rows.append({
            "group": grp_code,
            "sample_size": len(sub_df),
            "chi2": round(float(st.loc["Value", "chi2"]), 4),
            "df": int(st.loc["Value", "DoF"]),
            "p_value": round(float(st.loc["Value", "chi2 p-value"]), 4),
            "cfi": round(float(min(1.0, st.loc["Value", "CFI"])), 4),
            "tli": round(float(min(1.0, st.loc["Value", "TLI"])), 4),
            "rmsea": round(float(st.loc["Value", "RMSEA"]), 4),
            "srmr": round(grp_srmr, 4),
            "aic": round(float(st.loc["Value", "AIC"]), 4),
            "bic": round(float(st.loc["Value", "BIC"]), 4),
        })

    df_cfa_fit_indices = pd.DataFrame(fit_rows)

    return df_cfa_measurement, df_cfa_fit_indices


def run_self_checks(
    df: pd.DataFrame,
    df_t1: pd.DataFrame,
    df_t2: pd.DataFrame,
    df_t3: pd.DataFrame,
    df_t4: pd.DataFrame,
    logger: logging.Logger,
) -> bool:
    """Execute thorough runtime assertions to ensure full contract compliance."""
    logger.info("Running post-execution self-verification checks...")

    # Table 1 checks
    for idx, r in df_t1.iterrows():
        p_n = float(r["pooled_n"])
        de_n = float(r["germany_n"])
        uk_n = float(r["uk_n"])
        us_n = float(r["usa_n"])
        if abs((de_n + uk_n + us_n) - p_n) > 0.5:
            raise AssertionError(f"Table 1 row {idx} count sum violation: {de_n}+{uk_n}+{us_n} != {p_n}")
    logger.info("  [PASS] Table 1 country counts sum to pooled counts for all rows.")

    # Table 2 checks
    assert len(df_t2) == 24, f"Table 2 must have 24 indicator rows, got {len(df_t2)}"
    for idx, r in df_t2.iterrows():
        std_l = float(r["std_loading"])
        p_val = float(r["p_value"])
        assert std_l > 0.40, f"Table 2 factor loading too low: {r['indicator']} ({std_l})"
        assert p_val < 0.05, f"Table 2 non-significant p-value: {r['indicator']} ({p_val})"
    for c in CANONICAL_CONSTRUCTS:
        sub = df_t2[df_t2["construct"] == c]
        alpha = float(sub.iloc[0]["cronbach_alpha"])
        cr = float(sub.iloc[0]["composite_reliability_CR"])
        ave = float(sub.iloc[0]["ave"])
        assert alpha >= 0.70, f"Alpha < 0.70 for {c}: {alpha}"
        assert cr >= 0.70, f"CR < 0.70 for {c}: {cr}"
        assert ave >= 0.40, f"AVE < 0.40 for {c}: {ave}"
    logger.info("  [PASS] Table 2 factor loadings, p-values, Alpha, CR, and AVE meet all thresholds.")

    # Table 3 checks
    assert len(df_t3) == 32, f"Table 3 must have 32 rows, got {len(df_t3)}"
    for g in ["POOLED", "DE", "UK", "US"]:
        sub_t3 = df_t3[df_t3["group"] == g].set_index("variable")
        for v in VARIABLES_ORDER:
            diag_val = float(sub_t3.loc[v, v])
            assert abs(diag_val - 1.0) < 1e-4, f"Diagonal for {v} in {g} != 1.0"
            for v2 in VARIABLES_ORDER:
                r12 = float(sub_t3.loc[v, v2])
                r21 = float(sub_t3.loc[v2, v])
                assert abs(r12 - r21) < 1e-3, f"Asymmetry between {v} and {v2} in {g}"
                assert -1.0 <= r12 <= 1.0, f"Correlation {r12} out of bounds"
        # Positive semi-definiteness check
        mat = sub_t3[VARIABLES_ORDER].values.astype(float)
        min_eig = np.min(np.linalg.eigvals(mat))
        assert min_eig > 0.0, f"Correlation matrix in {g} not positive definite: min_eig={min_eig}"
    logger.info("  [PASS] Table 3 correlations symmetric, bounded, diagonal 1.0, and positive definite.")

    # Table 4 checks
    assert len(df_t4) == 32, f"Table 4 must have 32 rows, got {len(df_t4)}"
    for idx, r in df_t4.iterrows():
        sd = float(r["sd"])
        m = float(r["mean"])
        skew_v = float(r["skewness"])
        kurt_v = float(r["kurtosis"])
        assert sd > 0.0, f"SD not positive for {r['variable']} in {r['group']}"
        assert not (np.isnan(skew_v) or np.isinf(skew_v)), f"Invalid skewness for {r['variable']}"
        assert not (np.isnan(kurt_v) or np.isinf(kurt_v)), f"Invalid kurtosis for {r['variable']}"
        if r["variable"] == "TOOL":
            assert 0.0 <= m <= 1.0, f"Tool mean out of bounds: {m}"
        else:
            assert 1.0 <= m <= 5.0, f"Likert mean out of bounds: {m}"
    logger.info("  [PASS] Table 4 descriptives valid, means within range, SDs positive, skew/kurtosis finite.")

    # Fornell-Larcker discriminant validity test
    sqrt_aves = {
        c: float(df_t2[df_t2["construct"] == c].iloc[0]["sqrt_ave"])
        for c in CANONICAL_CONSTRUCTS
    }
    pooled_corr = df_t3[df_t3["group"] == "POOLED"].set_index("variable")
    for c1, sq_ave in sqrt_aves.items():
        for c2 in CANONICAL_CONSTRUCTS:
            if c1 != c2:
                r_val = abs(float(pooled_corr.loc[c1, c2]))
                assert sq_ave > r_val, f"Fornell-Larcker violation: sqrt(AVE) of {c1} ({sq_ave}) <= r({c1}, {c2}) ({r_val})"
    logger.info("  [PASS] Fornell-Larcker discriminant validity 100% satisfied across all pairs.")

    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate CFA measurement model and descriptive statistics tables."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root directory (auto-detected if omitted)",
    )
    parser.add_argument(
        "--data-path",
        type=Path,
        default=None,
        help="Path to synthetic multigroup CSV dataset",
    )
    parser.add_argument(
        "--tables-dir",
        type=Path,
        default=None,
        help="Target directory for output CSV tables",
    )
    parser.add_argument(
        "--logs-dir",
        type=Path,
        default=None,
        help="Target directory for execution log files",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Target log file path",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed debug logging",
    )

    args = parser.parse_args()

    # Resolve paths
    repo_root = args.repo_root or Path(__file__).resolve().parent.parent
    data_path = args.data_path or (repo_root / "data" / "synthetic_multigroup.csv")
    tables_dir = args.tables_dir or (repo_root / "results" / "tables")
    logs_dir = args.logs_dir or (repo_root / "results" / "logs")
    log_file = args.log_file or (logs_dir / "02_cfa_and_descriptives.log")

    tables_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    logger = setup_logging(log_file=log_file, verbose=args.verbose)

    logger.info("=" * 80)
    logger.info("START: CFA Measurement Model and Descriptive Statistics (Milestone M2)")
    logger.info("Repository Root : %s", repo_root)
    logger.info("Input Dataset   : %s", data_path)
    logger.info("Output Tables   : %s", tables_dir)
    logger.info("Log File        : %s", log_file)
    logger.info("Execution Time  : %s", datetime.now(timezone.utc).isoformat())
    logger.info("=" * 80)

    try:
        # Load and validate input dataset
        if not data_path.exists():
            raise FileNotFoundError(f"Input dataset not found at {data_path}")

        df = pd.read_csv(data_path)
        logger.info("Loaded dataset successfully: %d rows, %d columns", len(df), len(df.columns))
        country_counts = df["country"].value_counts().to_dict()
        logger.info("Country subsample counts: %s", country_counts)

        # 1. Table 1 Demographics
        logger.info("Generating Table 1 Demographics and Country Summary...")
        df_t1_canon, df_t1_summary = build_table1_demographics(df)

        path_t1_canon = tables_dir / "table1_demographics.csv"
        df_t1_canon.to_csv(path_t1_canon, index=False, encoding="utf-8")
        logger.info("Wrote Table 1 Demographics: %s (%d rows)", path_t1_canon, len(df_t1_canon))

        path_t1_summary = tables_dir / "table1_country_summary.csv"
        df_t1_summary.to_csv(path_t1_summary, index=False, encoding="utf-8")
        logger.info("Wrote Table 1 Country Summary: %s (%d rows)", path_t1_summary, len(df_t1_summary))

        # 2. Compute composite scores for construct descriptives & correlations
        logger.info("Computing composite scale scores for latent constructs...")
        df_calc = compute_composite_scores(df)

        # 3. Table 4 Descriptives
        logger.info("Generating Table 4 Descriptive Statistics...")
        df_t4 = build_table4_descriptives(df_calc)

        path_t4 = tables_dir / "table4_descriptives.csv"
        df_t4.to_csv(path_t4, index=False, encoding="utf-8")
        logger.info("Wrote Table 4 Descriptives: %s (%d rows)", path_t4, len(df_t4))

        # 4. Table 3 Correlations
        logger.info("Generating Table 3 Pearson Correlation Matrices...")
        df_t3 = build_table3_correlations(df_calc)

        path_t3 = tables_dir / "table3_correlations.csv"
        df_t3.to_csv(path_t3, index=False, encoding="utf-8")
        logger.info("Wrote Table 3 Correlations: %s (%d rows)", path_t3, len(df_t3))

        # 5. Table 2 CFA Measurement Model and Fit Indices
        logger.info("Estimating CFA Measurement Model via semopy (MLW)...")
        df_t2, df_t2_fit = estimate_cfa_and_reliability(df, logger)

        path_t2 = tables_dir / "table2_cfa_measurement.csv"
        df_t2.to_csv(path_t2, index=False, encoding="utf-8")
        logger.info("Wrote Table 2 CFA Measurement: %s (%d rows)", path_t2, len(df_t2))

        path_t2_fit = tables_dir / "table2_cfa_fit_indices.csv"
        df_t2_fit.to_csv(path_t2_fit, index=False, encoding="utf-8")
        logger.info("Wrote Table 2 CFA Fit Indices: %s (%d rows)", path_t2_fit, len(df_t2_fit))

        # 6. Run post-execution self-checks
        run_self_checks(df, df_t1_canon, df_t2, df_t3, df_t4, logger)

        logger.info("=" * 80)
        logger.info("[SUCCESS] Milestone M2 CFA and Descriptives pipeline completed successfully.")
        logger.info("Generated tables in %s:", tables_dir)
        logger.info("  1. table1_demographics.csv (%d rows)", len(df_t1_canon))
        logger.info("  2. table1_country_summary.csv (%d rows)", len(df_t1_summary))
        logger.info("  3. table2_cfa_measurement.csv (%d rows)", len(df_t2))
        logger.info("  4. table2_cfa_fit_indices.csv (%d rows)", len(df_t2_fit))
        logger.info("  5. table3_correlations.csv (%d rows)", len(df_t3))
        logger.info("  6. table4_descriptives.csv (%d rows)", len(df_t4))
        logger.info("=" * 80)
        return 0

    except Exception as e:
        logger.exception("[FATAL ERROR] Pipeline execution failed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
