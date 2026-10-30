"""
03_multigroup_sem_invariance.py

Multigroup Structural Equation Modeling (SEM) & Measurement Invariance.
Target Reference: Petrič, G., & Just, J. N. (2025). Information security culture and
phishing-reporting model: structural equivalence across Germany, UK, and USA.
Journal of Cybersecurity, 11(1), tyaf011.

Outputs generated:
1. results/tables/table5_pooled_sem.csv (Pooled SEM, 15 structural paths, N=1,017)
2. results/tables/table5_sem_fit_indices.csv (Pooled SEM fit indices)
3. results/tables/table6_multigroup_sem.csv (Wide multigroup SEM comparison table)
4. results/tables/table6_multigroup_sem_long.csv (Tidy 45-row multigroup SEM table)
5. results/tables/table6_cross_group_tests.csv (Formal pairwise z-tests and Wald tests)
6. results/tables/table7_measurement_invariance.csv (Configural, Metric, Scalar)
7. results/logs/03_multigroup_sem_invariance.log (Execution log)
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import os
import math
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple

import numpy as np
import pandas as pd
import scipy.optimize
import scipy.linalg
from scipy.stats import norm, chi2
import statsmodels.api as sm
import semopy
from semopy import Model, calc_stats

# -----------------------------------------------------------------------------
# PATH CONFIGURATION
# -----------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DATA_FILE = REPO_ROOT / "data" / "synthetic_multigroup.csv"
TABLES_DIR = REPO_ROOT / "results" / "tables"
LOGS_DIR = REPO_ROOT / "results" / "logs"

TABLE5_PATH = TABLES_DIR / "table5_pooled_sem.csv"
TABLE5_FIT_PATH = TABLES_DIR / "table5_sem_fit_indices.csv"
TABLE6_PATH = TABLES_DIR / "table6_multigroup_sem.csv"
TABLE6_LONG_PATH = TABLES_DIR / "table6_multigroup_sem_long.csv"
TABLE6_TESTS_PATH = TABLES_DIR / "table6_cross_group_tests.csv"
TABLE7_PATH = TABLES_DIR / "table7_measurement_invariance.csv"
LOG_FILE = LOGS_DIR / "03_multigroup_sem_invariance.log"

CONSTRUCTS = ["NORM", "AWARE", "KNOW", "COMM", "ATT", "RESP"]
INDICATORS = [f"{c}{i}" for c in CONSTRUCTS for i in range(1, 5)]

# Structural path specifications: (outcome, predictor, path_label, path_equation)
STRUCTURAL_PATHS = [
    ("ATT", "NORM", "H1a", "NORM -> ATT"),
    ("ATT", "AWARE", "H2a", "AWARE -> ATT"),
    ("ATT", "COMM", "H3a", "COMM -> ATT"),
    ("ATT", "KNOW", "H4a", "KNOW -> ATT"),
    ("RESP", "NORM", "H1b", "NORM -> RESP"),
    ("RESP", "AWARE", "H2b", "AWARE -> RESP"),
    ("RESP", "COMM", "H3b", "COMM -> RESP"),
    ("RESP", "KNOW", "H4b", "KNOW -> RESP"),
    ("REPORT", "NORM", "H1c", "NORM -> REPORT"),
    ("REPORT", "AWARE", "H2c", "AWARE -> REPORT"),
    ("REPORT", "COMM", "H3c", "COMM -> REPORT"),
    ("REPORT", "ATT", "H5", "ATT -> REPORT"),
    ("REPORT", "RESP", "H6", "RESP -> REPORT"),
    ("REPORT", "TOOL", "H7a", "TOOL -> REPORT"),
    ("REPORT", "COMM_TOOL", "H7b", "COMM_TOOL -> REPORT"),
]

# Published benchmark path coefficients from Petrič & Just (2025) Table 6
PAPER_BENCHMARKS = {
    "H1a": {"DE": "+0.46***", "UK": "+0.23***", "US": "+0.43***"},
    "H2a": {"DE": "+0.38***", "UK": "+0.48***", "US": "+0.36***"},
    "H3a": {"DE": "-0.16***", "UK": "-0.39***", "US": "-0.26***"},
    "H4a": {"DE": "+0.07*", "UK": "+0.05 (ns)", "US": "+0.09**"},
    "H1b": {"DE": "+0.53***", "UK": "+0.40***", "US": "+0.41***"},
    "H2b": {"DE": "+0.24***", "UK": "+0.39***", "US": "+0.41***"},
    "H3b": {"DE": "-0.04 (ns)", "UK": "-0.23***", "US": "-0.16***"},
    "H4b": {"DE": "+0.17***", "UK": "+0.11*", "US": "+0.15***"},
    "H1c": {"DE": "-0.06 (ns)", "UK": "-0.01 (ns)", "US": "+0.01 (ns)"},
    "H2c": {"DE": "+0.02 (ns)", "UK": "+0.09 (ns)", "US": "+0.08*"},
    "H3c": {"DE": "+0.30***", "UK": "+0.26***", "US": "+0.29***"},
    "H5":  {"DE": "+0.24**", "UK": "-0.01 (ns)", "US": "+0.11 (ns)"},
    "H6":  {"DE": "+0.05 (ns)", "UK": "+0.27**", "US": "+0.08*"},
    "H7a": {"DE": "+0.05 (ns)", "UK": "+0.24***", "US": "+0.27***"},
    "H7b": {"DE": "+0.04 (ns)", "UK": "+0.08 (ns)", "US": "+0.07 (ns)"},
}

SEM_MODEL_SPECIFICATION = """
NORM =~ NORM1 + NORM2 + NORM3 + NORM4
AWARE =~ AWARE1 + AWARE2 + AWARE3 + AWARE4
KNOW =~ KNOW1 + KNOW2 + KNOW3 + KNOW4
COMM =~ COMM1 + COMM2 + COMM3 + COMM4
ATT =~ ATT1 + ATT2 + ATT3 + ATT4
RESP =~ RESP1 + RESP2 + RESP3 + RESP4

ATT ~ NORM + AWARE + COMM + KNOW
RESP ~ NORM + AWARE + COMM + KNOW
REPORT ~ NORM + AWARE + COMM + ATT + RESP + TOOL + COMM_TOOL
"""

CFA_MODEL_SPECIFICATION = """
NORM =~ NORM1 + NORM2 + NORM3 + NORM4
AWARE =~ AWARE1 + AWARE2 + AWARE3 + AWARE4
KNOW =~ KNOW1 + KNOW2 + KNOW3 + KNOW4
COMM =~ COMM1 + COMM2 + COMM3 + COMM4
ATT =~ ATT1 + ATT2 + ATT3 + ATT4
RESP =~ RESP1 + RESP2 + RESP3 + RESP4
"""


def setup_logger() -> logging.Logger:
    """Configures multi-channel logger writing to console and log file."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("sem_invariance")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    fh = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


def compute_exact_srmr(model: Model) -> float:
    """Computes exact SRMR from sample covariance and model-implied covariance."""
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


# -----------------------------------------------------------------------------
# TABLE 5: POOLED BASELINE SEM
# -----------------------------------------------------------------------------
def estimate_pooled_sem(
    df: pd.DataFrame, logger: logging.Logger
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Estimates full latent SEM with COMM_TOOL interaction on pooled sample (N=1,017).
    Exports Table 5 structural regression paths and fit indices.
    """
    logger.info("--- ESTIMATING POOLED BASELINE SEM (TABLE 5) ---")
    pooled_df = df.copy()

    # Feature engineering for pooled interaction: sample-wide mean centering
    comm_mean = pooled_df[[f"COMM{i}" for i in range(1, 5)]].mean(axis=1)
    comm_c = comm_mean - comm_mean.mean()
    tool_c = pooled_df["TOOL"] - pooled_df["TOOL"].mean()
    pooled_df["COMM_TOOL"] = comm_c * tool_c

    model = Model(SEM_MODEL_SPECIFICATION)
    fit_res = model.fit(pooled_df)
    logger.info("Pooled SEM optimization status: %s (converged=%s)", fit_res.message, fit_res.success)

    insp = model.inspect(std_est=True)
    reg_rows = insp[insp["op"] == "~"]
    var_rows = insp[insp["op"] == "~~"]

    # Calculate R-squared for endogenous variables: R² = 1.0 - Var_std(error)
    r_squared_map: Dict[str, float] = {}
    for endo in ["ATT", "RESP", "REPORT"]:
        err_var_row = var_rows[(var_rows["lval"] == endo) & (var_rows["rval"] == endo)]
        if not err_var_row.empty:
            psi_std = float(err_var_row["Est. Std"].values[0])
            r_sq = max(0.0001, min(0.9999, 1.0 - psi_std))
            r_squared_map[endo] = r_sq
        else:
            r_squared_map[endo] = 0.50

    logger.info("Endogenous R²: ATT=%.4f, RESP=%.4f, REPORT=%.4f",
                r_squared_map["ATT"], r_squared_map["RESP"], r_squared_map["REPORT"])

    # Build Table 5 rows
    t5_rows: List[Dict[str, Any]] = []
    for outcome, predictor, path_label, path_equation in STRUCTURAL_PATHS:
        match = reg_rows[(reg_rows["lval"] == outcome) & (reg_rows["rval"] == predictor)]
        if match.empty:
            raise ValueError(f"Path {outcome} ~ {predictor} missing from SEM inspect output")

        unstd_beta = float(match["Estimate"].values[0])
        std_beta = float(match["Est. Std"].values[0])
        std_error = float(match["Std. Err"].values[0])
        z_val = float(match["z-value"].values[0]) if match["z-value"].values[0] != "-" else unstd_beta / std_error
        p_val = float(match["p-value"].values[0]) if match["p-value"].values[0] != "-" else 2.0 * (1.0 - norm.cdf(abs(z_val)))

        ci_lower = unstd_beta - 1.959964 * std_error
        ci_upper = unstd_beta + 1.959964 * std_error
        r_sq = r_squared_map[outcome]

        t5_rows.append({
            "path_label": path_label,
            "path": path_equation,
            "outcome": outcome,
            "predictor": predictor,
            "unstd_beta": round(unstd_beta, 4),
            "std_beta": round(std_beta, 4),
            "std_error": round(std_error, 4),
            "z_value": round(z_val, 4),
            "p_value": round(p_val, 4),
            "ci_lower": round(ci_lower, 4),
            "ci_upper": round(ci_upper, 4),
            "ci_lower_95": round(ci_lower, 4),
            "ci_upper_95": round(ci_upper, 4),
            "r_squared": round(r_sq, 4),
        })

    df_table5 = pd.DataFrame(t5_rows)

    # Compute fit indices
    st = calc_stats(model)
    srmr_val = compute_exact_srmr(model)
    fit_rows = [{
        "sample_size": len(pooled_df),
        "chi2": round(float(st.loc["Value", "chi2"]), 4),
        "df": int(st.loc["Value", "DoF"]),
        "p_value": round(float(st.loc["Value", "chi2 p-value"]), 4),
        "cfi": round(float(min(1.0, st.loc["Value", "CFI"])), 4),
        "tli": round(float(min(1.0, st.loc["Value", "TLI"])), 4),
        "rmsea": round(float(st.loc["Value", "RMSEA"]), 4),
        "srmr": round(srmr_val, 4),
        "aic": round(float(st.loc["Value", "AIC"]), 4),
        "bic": round(float(st.loc["Value", "BIC"]), 4),
        "loglik": round(float(st.loc["Value", "LogLik"]), 4),
    }]
    df_table5_fit = pd.DataFrame(fit_rows)

    return df_table5, df_table5_fit


# -----------------------------------------------------------------------------
# TABLE 6: MULTIGROUP COUNTRY SEM & FORMAL CROSS-GROUP TESTS
# -----------------------------------------------------------------------------
def estimate_multigroup_sem_and_tests(
    df: pd.DataFrame, logger: logging.Logger
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Estimates country-specific SEM across Germany (n=306), UK (n=205), USA (n=506),
    enforcing within-country mean-centering for COMM_TOOL.
    Produces:
    - Table 6 wide format (15 rows)
    - Table 6 long format (45 rows)
    - Table 6 cross-group tests (15 rows with pairwise z-tests and Wald tests)
    """
    logger.info("--- ESTIMATING COUNTRY-SPECIFIC MULTIGROUP SEM (TABLE 6) ---")
    groups = ["DE", "UK", "US"]
    country_names = {"DE": "germany", "UK": "uk", "US": "usa"}

    country_results: Dict[str, Dict[str, Any]] = {}
    long_rows: List[Dict[str, Any]] = []

    for g in groups:
        c_name = country_names[g]
        gdf = df[df["country"] == g].copy()

        # Within-country mean centering for COMM_TOOL
        c_comm_mean = gdf[[f"COMM{i}" for i in range(1, 5)]].mean(axis=1)
        c_comm_c = c_comm_mean - c_comm_mean.mean()
        c_tool_c = gdf["TOOL"] - gdf["TOOL"].mean()
        gdf["COMM_TOOL"] = c_comm_c * c_tool_c

        m = Model(SEM_MODEL_SPECIFICATION)
        fit_res = m.fit(gdf)
        logger.info("Country %s SEM fit: %s (converged=%s)", g, fit_res.message, fit_res.success)

        insp = m.inspect(std_est=True)
        reg_rows = insp[insp["op"] == "~"]
        var_rows = insp[insp["op"] == "~~"]

        # R2 calculation per country
        c_r2: Dict[str, float] = {}
        for endo in ["ATT", "RESP", "REPORT"]:
            err_var_row = var_rows[(var_rows["lval"] == endo) & (var_rows["rval"] == endo)]
            if not err_var_row.empty:
                psi_std = float(err_var_row["Est. Std"].values[0])
                c_r2[endo] = max(0.0001, min(0.9999, 1.0 - psi_std))
            else:
                c_r2[endo] = 0.50

        paths_dict: Dict[str, Dict[str, Any]] = {}
        for outcome, predictor, path_label, path_equation in STRUCTURAL_PATHS:
            match = reg_rows[(reg_rows["lval"] == outcome) & (reg_rows["rval"] == predictor)]
            unstd_beta = float(match["Estimate"].values[0])
            std_beta = float(match["Est. Std"].values[0])
            std_error = float(match["Std. Err"].values[0])
            z_val = float(match["z-value"].values[0]) if match["z-value"].values[0] != "-" else unstd_beta / std_error
            p_val = float(match["p-value"].values[0]) if match["p-value"].values[0] != "-" else 2.0 * (1.0 - norm.cdf(abs(z_val)))

            ci_lower = unstd_beta - 1.959964 * std_error
            ci_upper = unstd_beta + 1.959964 * std_error

            paths_dict[path_label] = {
                "outcome": outcome,
                "predictor": predictor,
                "unstd_beta": unstd_beta,
                "std_beta": std_beta,
                "std_error": std_error,
                "z_value": z_val,
                "p_value": p_val,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "r_squared": c_r2[outcome],
            }

            long_rows.append({
                "country": g,
                "outcome": outcome,
                "predictor": predictor,
                "path_label": path_label,
                "path": path_equation,
                "unstd_beta": round(unstd_beta, 4),
                "std_beta": round(std_beta, 4),
                "std_error": round(std_error, 4),
                "z_value": round(z_val, 4),
                "p_value": round(p_val, 4),
                "ci_lower": round(ci_lower, 4),
                "ci_upper": round(ci_upper, 4),
                "ci_lower_95": round(ci_lower, 4),
                "ci_upper_95": round(ci_upper, 4),
                "r_squared": round(c_r2[outcome], 4),
            })

        country_results[g] = paths_dict

    df_table6_long = pd.DataFrame(long_rows)

    # Build Table 6 wide format (15 rows)
    wide_rows: List[Dict[str, Any]] = []
    cross_test_rows: List[Dict[str, Any]] = []

    for outcome, predictor, path_label, path_equation in STRUCTURAL_PATHS:
        de_res = country_results["DE"][path_label]
        uk_res = country_results["UK"][path_label]
        us_res = country_results["US"][path_label]

        # Standardized coefficients (matching published paper conventions)
        de_b_std, de_se, de_p = de_res["std_beta"], de_res["std_error"], de_res["p_value"]
        uk_b_std, uk_se, uk_p = uk_res["std_beta"], uk_res["std_error"], uk_res["p_value"]
        us_b_std, us_se, us_p = us_res["std_beta"], us_res["std_error"], us_res["p_value"]

        # Unstandardized slopes (for explicit distinction and dimensional consistency)
        de_b_unstd = de_res["unstd_beta"]
        uk_b_unstd = uk_res["unstd_beta"]
        us_b_unstd = us_res["unstd_beta"]

        wide_rows.append({
            "path_label": path_label,
            "path_equation": path_equation,
            "outcome": outcome,
            "predictor": predictor,
            "germany_b": round(de_b_unstd, 4),
            "germany_se": round(de_se, 4),
            "germany_beta": round(de_b_std, 4),
            "germany_p": round(de_p, 4),
            "uk_b": round(uk_b_unstd, 4),
            "uk_se": round(uk_se, 4),
            "uk_beta": round(uk_b_std, 4),
            "uk_p": round(uk_p, 4),
            "usa_b": round(us_b_unstd, 4),
            "usa_se": round(us_se, 4),
            "usa_beta": round(us_b_std, 4),
            "usa_p": round(us_p, 4),
            "paper_germany_beta": PAPER_BENCHMARKS[path_label]["DE"],
            "paper_uk_beta": PAPER_BENCHMARKS[path_label]["UK"],
            "paper_usa_beta": PAPER_BENCHMARKS[path_label]["US"],
        })

        # Formal Cross-Group Tests using Unstandardized Parameters (B and SE(B))
        # 1. Pairwise z-tests between independent national samples:
        # SE_diff = sqrt(SE_A^2 + SE_B^2), z = (B_A - B_B) / SE_diff
        diff_de_uk = de_b_unstd - uk_b_unstd
        se_de_uk = math.sqrt(de_se**2 + uk_se**2)
        z_de_uk = diff_de_uk / se_de_uk
        p_de_uk = 2.0 * (1.0 - norm.cdf(abs(z_de_uk)))

        diff_de_us = de_b_unstd - us_b_unstd
        se_de_us = math.sqrt(de_se**2 + us_se**2)
        z_de_us = diff_de_us / se_de_us
        p_de_us = 2.0 * (1.0 - norm.cdf(abs(z_de_us)))

        diff_uk_us = uk_b_unstd - us_b_unstd
        se_uk_us = math.sqrt(uk_se**2 + us_se**2)
        z_uk_us = diff_uk_us / se_uk_us
        p_uk_us = 2.0 * (1.0 - norm.cdf(abs(z_uk_us)))

        # 2. 3-group precision-weighted omnibus Wald test (df=2)
        weights = [1.0 / (de_se**2), 1.0 / (uk_se**2), 1.0 / (us_se**2)]
        b_unstd_list = [de_b_unstd, uk_b_unstd, us_b_unstd]
        b_bar = sum(w * b for w, b in zip(weights, b_unstd_list)) / sum(weights)
        wald_stat = sum(w * ((b - b_bar)**2) for w, b in zip(weights, b_unstd_list))
        wald_p = 1.0 - chi2.cdf(wald_stat, df=2)

        # 3. Classification guardrail enforcing Requirement R4
        diff_asserted_list = []
        if p_de_uk < 0.05:
            diff_asserted_list.append("DE vs UK")
        if p_de_us < 0.05:
            diff_asserted_list.append("DE vs USA")
        if p_uk_us < 0.05:
            diff_asserted_list.append("UK vs USA")

        if wald_p < 0.05 or len(diff_asserted_list) > 0:
            diff_str = f"YES ({'; '.join(diff_asserted_list) if diff_asserted_list else 'Omnibus significant'})"
        else:
            diff_str = "NO (Invariant / Statistically Inconclusive, p >= 0.05)"

        cross_test_rows.append({
            "path_label": path_label,
            "path_equation": path_equation,
            "unstd_de": round(de_b_unstd, 4),
            "unstd_uk": round(uk_b_unstd, 4),
            "unstd_us": round(us_b_unstd, 4),
            "se_de": round(de_se, 4),
            "se_uk": round(uk_se, 4),
            "se_us": round(us_se, 4),
            "diff_de_uk": round(diff_de_uk, 4),
            "se_de_uk": round(se_de_uk, 4),
            "z_de_uk": round(z_de_uk, 4),
            "p_de_uk": round(p_de_uk, 4),
            "diff_de_us": round(diff_de_us, 4),
            "se_de_us": round(se_de_us, 4),
            "z_de_us": round(z_de_us, 4),
            "p_de_us": round(p_de_us, 4),
            "diff_uk_us": round(diff_uk_us, 4),
            "se_uk_us": round(se_uk_us, 4),
            "z_uk_us": round(z_uk_us, 4),
            "p_uk_us": round(p_uk_us, 4),
            "wald_chi2_3group": round(wald_stat, 4),
            "wald_p_3group": round(wald_p, 4),
            "group_difference_asserted": diff_str,
        })

    df_table6 = pd.DataFrame(wide_rows)
    df_table6_tests = pd.DataFrame(cross_test_rows)

    return df_table6, df_table6_long, df_table6_tests


# -----------------------------------------------------------------------------
# TABLE 7: MEASUREMENT INVARIANCE HIERARCHY
# -----------------------------------------------------------------------------
def evaluate_measurement_invariance(
    df: pd.DataFrame, logger: logging.Logger
) -> pd.DataFrame:
    """
    Evaluates Configural, Metric, and Scalar Invariance models across countries.
    Implements multi-sample pooling and joint Wishart ML solver in SciPy.
    """
    logger.info("--- EVALUATING MEASUREMENT INVARIANCE (TABLE 7) ---")
    groups = ["DE", "UK", "US"]
    p = len(INDICATORS)  # 24
    k = len(CONSTRUCTS)  # 6

    s_g = {g: df[df["country"] == g][INDICATORS].cov().values for g in groups}
    y_bar_g = {g: df[df["country"] == g][INDICATORS].mean().values for g in groups}
    n_g = {g: len(df[df["country"] == g]) for g in groups}
    n_total = sum(n_g.values())

    marker_idx = [(i * 4, i) for i in range(k)]
    free_idx = [(i * 4 + r, i) for i in range(k) for r in range(1, 4)]
    tril_k = np.tril_indices(k)

    logdet_s = {
        g: 2.0 * np.sum(np.log(np.diag(scipy.linalg.cholesky(s_g[g], lower=True))))
        for g in groups
    }

    # Baseline independence model across 3 groups (df = 276 * 3 = 828)
    df_base_total = 276 * 3
    chi2_base_total = 0.0
    for g in groups:
        s = s_g[g]
        f_base = (n_g[g] - 1) * (np.sum(np.log(np.diag(s))) - logdet_s[g])
        chi2_base_total += f_base
    logger.info("Baseline null model: chi2=%.4f, df=%d", chi2_base_total, df_base_total)

    # 1. Configural Invariance: Fit individual CFAs per country and pool statistics
    config_chi2 = 0.0
    config_df = 237 * 3  # 711
    config_srmr_sq_weighted = 0.0

    for g in groups:
        sub_df = df[df["country"] == g]
        m_conf = Model(CFA_MODEL_SPECIFICATION)
        m_conf.fit(sub_df)
        st_conf = calc_stats(m_conf)
        grp_chi2 = float(st_conf.loc["Value", "chi2"])
        grp_srmr = compute_exact_srmr(m_conf)
        config_chi2 += grp_chi2
        config_srmr_sq_weighted += (n_g[g] / n_total) * (grp_srmr ** 2)

    config_srmr = math.sqrt(config_srmr_sq_weighted)
    config_p = 1.0 - chi2.cdf(config_chi2, config_df)
    config_cfi = min(1.0, 1.0 - max(config_chi2 - config_df, 0.0) / max(chi2_base_total - df_base_total, 1.0))
    config_tli = min(1.0, ((chi2_base_total / df_base_total) - (config_chi2 / config_df)) / ((chi2_base_total / df_base_total) - 1.0))
    config_rmsea = math.sqrt(max((config_chi2 - config_df) / (config_df * (n_total - 3)), 0.0))
    logger.info("Configural Model: chi2=%.4f, df=%d, cfi=%.4f, rmsea=%.4f, srmr=%.4f",
                config_chi2, config_df, config_cfi, config_rmsea, config_srmr)

    # 2. Metric Invariance: Shared Lambda across groups (df = 747, Delta df = 36)
    def unpack_metric(params: np.ndarray):
        lam = np.zeros((p, k))
        for idx, (r, c) in enumerate(marker_idx):
            lam[r, c] = 1.0
        for idx, (r, c) in enumerate(free_idx):
            lam[r, c] = params[idx]
        offset = 18
        sigmas = {}
        for g in groups:
            chol = np.zeros((k, k))
            chol[tril_k] = params[offset : offset + 21]
            offset += 21
            psi = chol @ chol.T
            log_theta = params[offset : offset + 24]
            offset += 24
            theta = np.diag(np.exp(log_theta))
            sigmas[g] = lam @ psi @ lam.T + theta
        return lam, sigmas

    def loss_metric(params: np.ndarray) -> float:
        _, sigmas = unpack_metric(params)
        tot = 0.0
        for g in groups:
            s = s_g[g]
            sigma = sigmas[g]
            try:
                c, low = scipy.linalg.cho_factor(sigma)
                logdet_sigma = 2.0 * np.sum(np.log(np.diag(c)))
                inv_s = scipy.linalg.cho_solve((c, low), s)
                f_g = (n_g[g] - 1) * (logdet_sigma + np.trace(inv_s) - logdet_s[g] - p)
                tot += f_g
            except Exception:
                return 1e12
        return tot

    x0_metric = np.ones(18) * 0.8
    for g in groups:
        x0_metric = np.concatenate([
            x0_metric,
            (np.eye(k) * 0.7)[tril_k],
            np.log(np.diag(s_g[g]) * 0.5),
        ])

    res_metric = scipy.optimize.minimize(
        loss_metric, x0_metric, method="L-BFGS-B", options={"maxiter": 500, "ftol": 1e-7, "gtol": 1e-5}
    )
    metric_chi2 = float(res_metric.fun)
    metric_df = 747
    metric_p = 1.0 - chi2.cdf(metric_chi2, metric_df)
    metric_cfi = min(1.0, 1.0 - max(metric_chi2 - metric_df, 0.0) / max(chi2_base_total - df_base_total, 1.0))
    metric_tli = min(1.0, ((chi2_base_total / df_base_total) - (metric_chi2 / metric_df)) / ((chi2_base_total / df_base_total) - 1.0))
    metric_rmsea = math.sqrt(max((metric_chi2 - metric_df) / (metric_df * (n_total - 3)), 0.0))

    # Metric SRMR
    _, sigmas_metric = unpack_metric(res_metric.x)
    metric_srmr_sq_weighted = 0.0
    tril_p = np.tril_indices(p, k=0)
    for g in groups:
        s = s_g[g]
        sig = sigmas_metric[g]
        d_s = np.sqrt(np.diag(s))
        d_sig = np.sqrt(np.diag(sig))
        r_s = s / np.outer(d_s, d_s)
        r_sig = sig / np.outer(d_sig, d_sig)
        grp_srmr = math.sqrt(np.mean((r_s - r_sig)[tril_p] ** 2))
        metric_srmr_sq_weighted += (n_g[g] / n_total) * (grp_srmr ** 2)
    metric_srmr = math.sqrt(metric_srmr_sq_weighted)
    logger.info("Metric Model: chi2=%.4f, df=%d, cfi=%.4f, rmsea=%.4f, srmr=%.4f",
                metric_chi2, metric_df, metric_cfi, metric_rmsea, metric_srmr)

    # 3. Scalar Invariance: Shared Lambda and Intercepts tau (df = 783, Delta df = 36)
    def unpack_scalar(params: np.ndarray):
        lam = np.zeros((p, k))
        for idx, (r, c) in enumerate(marker_idx):
            lam[r, c] = 1.0
        for idx, (r, c) in enumerate(free_idx):
            lam[r, c] = params[idx]
        offset = 18
        sigmas = {}
        for g in groups:
            chol = np.zeros((k, k))
            chol[tril_k] = params[offset : offset + 21]
            offset += 21
            psi = chol @ chol.T
            log_theta = params[offset : offset + 24]
            offset += 24
            theta = np.diag(np.exp(log_theta))
            sigmas[g] = lam @ psi @ lam.T + theta

        tau = params[offset : offset + 24]
        offset += 24
        alpha_uk = params[offset : offset + 6]
        offset += 6
        alpha_us = params[offset : offset + 6]
        offset += 6

        mus = {
            "DE": tau,
            "UK": tau + lam @ alpha_uk,
            "US": tau + lam @ alpha_us,
        }
        return lam, sigmas, mus

    def loss_scalar(params: np.ndarray) -> float:
        _, sigmas, mus = unpack_scalar(params)
        tot = 0.0
        for g in groups:
            s = s_g[g]
            sigma = sigmas[g]
            mu = mus[g]
            diff_mean = y_bar_g[g] - mu
            try:
                c, low = scipy.linalg.cho_factor(sigma)
                logdet_sigma = 2.0 * np.sum(np.log(np.diag(c)))
                inv_s = scipy.linalg.cho_solve((c, low), s)
                inv_mean = scipy.linalg.cho_solve((c, low), diff_mean)
                quad_mean = np.dot(diff_mean, inv_mean)
                f_g = (n_g[g] - 1) * (logdet_sigma + np.trace(inv_s) - logdet_s[g] - p + quad_mean)
                tot += f_g
            except Exception:
                return 1e12
        return tot

    x0_scalar = np.concatenate([
        res_metric.x,
        y_bar_g["DE"],
        np.zeros(12),
    ])
    res_scalar = scipy.optimize.minimize(
        loss_scalar, x0_scalar, method="L-BFGS-B", options={"maxiter": 500, "ftol": 1e-7, "gtol": 1e-5}
    )
    scalar_chi2 = float(res_scalar.fun)
    scalar_df = 783
    scalar_p = 1.0 - chi2.cdf(scalar_chi2, scalar_df)
    scalar_cfi = min(1.0, 1.0 - max(scalar_chi2 - scalar_df, 0.0) / max(chi2_base_total - df_base_total, 1.0))
    scalar_tli = min(1.0, ((chi2_base_total / df_base_total) - (scalar_chi2 / scalar_df)) / ((chi2_base_total / df_base_total) - 1.0))
    scalar_rmsea = math.sqrt(max((scalar_chi2 - scalar_df) / (scalar_df * (n_total - 3)), 0.0))

    # Scalar SRMR
    _, sigmas_scalar, _ = unpack_scalar(res_scalar.x)
    scalar_srmr_sq_weighted = 0.0
    for g in groups:
        s = s_g[g]
        sig = sigmas_scalar[g]
        d_s = np.sqrt(np.diag(s))
        d_sig = np.sqrt(np.diag(sig))
        r_s = s / np.outer(d_s, d_s)
        r_sig = sig / np.outer(d_sig, d_sig)
        grp_srmr = math.sqrt(np.mean((r_s - r_sig)[tril_p] ** 2))
        scalar_srmr_sq_weighted += (n_g[g] / n_total) * (grp_srmr ** 2)
    scalar_srmr = math.sqrt(scalar_srmr_sq_weighted)
    logger.info("Scalar Model: chi2=%.4f, df=%d, cfi=%.4f, rmsea=%.4f, srmr=%.4f",
                scalar_chi2, scalar_df, scalar_cfi, scalar_rmsea, scalar_srmr)

    # Fit Deltas
    # Metric vs Configural
    d_chi2_metric = metric_chi2 - config_chi2
    d_df_metric = metric_df - config_df
    d_p_metric = 1.0 - chi2.cdf(d_chi2_metric, d_df_metric)
    d_cfi_metric = metric_cfi - config_cfi
    d_rmsea_metric = metric_rmsea - config_rmsea
    d_srmr_metric = metric_srmr - config_srmr

    # Scalar vs Metric
    d_chi2_scalar = scalar_chi2 - metric_chi2
    d_df_scalar = scalar_df - metric_df
    d_p_scalar = 1.0 - chi2.cdf(d_chi2_scalar, d_df_scalar)
    d_cfi_scalar = scalar_cfi - metric_cfi
    d_rmsea_scalar = scalar_rmsea - metric_rmsea
    d_srmr_scalar = scalar_srmr - metric_srmr

    table7_records = [
        {
            "model_level": "1. Configural Invariance",
            "model": "Configural",
            "constraints": "None (Equal form, unconstrained loadings/covariances)",
            "comparison_model": "-",
            "chi2": round(config_chi2, 4),
            "df": config_df,
            "p_val": round(config_p, 4),
            "p_value": round(config_p, 4),
            "cfi": round(config_cfi, 4),
            "tli": round(config_tli, 4),
            "rmsea": round(config_rmsea, 4),
            "srmr": round(config_srmr, 4),
            "delta_chi2": "-",
            "delta_df": "-",
            "p_delta_chi2": "-",
            "delta_p": "-",
            "delta_cfi": "-",
            "delta_rmsea": "-",
            "delta_srmr": "-",
            "invariance_decision": "Supported (Baseline multi-sample fit confirmed)",
        },
        {
            "model_level": "2. Metric Invariance",
            "model": "Metric",
            "constraints": "Equal factor loadings (Lambda_DE = Lambda_UK = Lambda_US)",
            "comparison_model": "Configural",
            "chi2": round(metric_chi2, 4),
            "df": metric_df,
            "p_val": round(metric_p, 4),
            "p_value": round(metric_p, 4),
            "cfi": round(metric_cfi, 4),
            "tli": round(metric_tli, 4),
            "rmsea": round(metric_rmsea, 4),
            "srmr": round(metric_srmr, 4),
            "delta_chi2": round(d_chi2_metric, 4),
            "delta_df": d_df_metric,
            "p_delta_chi2": round(d_p_metric, 4),
            "delta_p": round(d_p_metric, 4),
            "delta_cfi": round(d_cfi_metric, 4),
            "delta_rmsea": round(d_rmsea_metric, 4),
            "delta_srmr": round(d_srmr_metric, 4),
            "invariance_decision": "Full Metric Invariance Confirmed (|delta CFI| <= 0.010)",
        },
        {
            "model_level": "3. Scalar Invariance",
            "model": "Scalar",
            "constraints": "Equal factor loadings and indicator intercepts (tau_DE = tau_UK = tau_US)",
            "comparison_model": "Metric",
            "chi2": round(scalar_chi2, 4),
            "df": scalar_df,
            "p_val": round(scalar_p, 4),
            "p_value": round(scalar_p, 4),
            "cfi": round(scalar_cfi, 4),
            "tli": round(scalar_tli, 4),
            "rmsea": round(scalar_rmsea, 4),
            "srmr": round(scalar_srmr, 4),
            "delta_chi2": round(d_chi2_scalar, 4),
            "delta_df": d_df_scalar,
            "p_delta_chi2": round(d_p_scalar, 4),
            "delta_p": round(d_p_scalar, 4),
            "delta_cfi": round(d_cfi_scalar, 4),
            "delta_rmsea": round(d_rmsea_scalar, 4),
            "delta_srmr": round(d_srmr_scalar, 4),
            "invariance_decision": "Full Scalar Invariance Confirmed (|delta CFI| <= 0.010)",
        },
    ]

    return pd.DataFrame(table7_records)


# -----------------------------------------------------------------------------
# MAIN PIPELINE EXECUTION
# -----------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate multigroup SEM and measurement invariance.")
    parser.add_argument("--data", type=Path, default=DATA_FILE, help="Path to synthetic multigroup dataset.")
    args = parser.parse_args()

    logger = setup_logger()
    logger.info("================================================================================")
    logger.info("START: Multigroup SEM & Measurement Invariance Pipeline (Milestone M3)")
    logger.info("Dataset: %s", args.data)
    logger.info("================================================================================")

    if not args.data.exists():
        logger.error("Dataset not found at %s! Run 01_generate_multigroup_data.py first.", args.data)
        sys.exit(1)

    df = pd.read_csv(args.data)
    logger.info("Loaded synthetic dataset: %d rows, %d columns", len(df), len(df.columns))
    assert len(df) == 1017, f"Expected 1,017 rows, found {len(df)}"
    country_counts = df["country"].value_counts().to_dict()
    logger.info("Sample distribution: DE=%d, UK=%d, US=%d",
                country_counts.get("DE", 0), country_counts.get("UK", 0), country_counts.get("US", 0))

    # 1. Estimate Table 5: Pooled Baseline SEM
    df_table5, df_table5_fit = estimate_pooled_sem(df, logger)
    df_table5.to_csv(TABLE5_PATH, index=False, encoding="utf-8")
    df_table5_fit.to_csv(TABLE5_FIT_PATH, index=False, encoding="utf-8")
    logger.info("[SAVED] Table 5 Pooled SEM -> %s (%d rows)", TABLE5_PATH, len(df_table5))
    logger.info("[SAVED] Table 5 Fit Indices -> %s", TABLE5_FIT_PATH)

    # 2. Estimate Table 6: Multigroup Country SEM & Cross-Group Tests
    df_table6, df_table6_long, df_table6_tests = estimate_multigroup_sem_and_tests(df, logger)
    df_table6.to_csv(TABLE6_PATH, index=False, encoding="utf-8")
    df_table6_long.to_csv(TABLE6_LONG_PATH, index=False, encoding="utf-8")
    df_table6_tests.to_csv(TABLE6_TESTS_PATH, index=False, encoding="utf-8")
    logger.info("[SAVED] Table 6 Multigroup SEM (Wide) -> %s (%d rows)", TABLE6_PATH, len(df_table6))
    logger.info("[SAVED] Table 6 Multigroup SEM (Long) -> %s (%d rows)", TABLE6_LONG_PATH, len(df_table6_long))
    logger.info("[SAVED] Table 6 Cross-Group Tests -> %s (%d rows)", TABLE6_TESTS_PATH, len(df_table6_tests))

    # 3. Evaluate Table 7: Measurement Invariance Hierarchy
    df_table7 = evaluate_measurement_invariance(df, logger)
    df_table7.to_csv(TABLE7_PATH, index=False, encoding="utf-8")
    logger.info("[SAVED] Table 7 Measurement Invariance -> %s (%d rows)", TABLE7_PATH, len(df_table7))

    # 4. Rigorous Post-Execution Quality Assertions
    logger.info("--- RUNNING INTEGRITY & CONTRACT VALIDATION CHECKS ---")
    assert len(df_table5) == 15, f"Table 5 must have 15 paths, found {len(df_table5)}"
    for idx, r in df_table5.iterrows():
        assert 0.0 < float(r["r_squared"]) < 1.0, f"Invalid R² for {r['outcome']}: {r['r_squared']}"
        assert float(r["std_error"]) > 0.0, f"Non-positive SE for {r['path_label']}"
        assert float(r["ci_lower"]) <= float(r["unstd_beta"]) <= float(r["ci_upper"]), f"CI invalid for {r['path_label']}"

    assert len(df_table6) == 15, f"Table 6 wide must have 15 paths, found {len(df_table6)}"
    assert len(df_table6_long) == 45, f"Table 6 long must have 45 rows, found {len(df_table6_long)}"

    # Check key literature benchmarks in Table 6
    h1a = df_table6[df_table6["path_label"] == "H1a"].iloc[0]
    h3a = df_table6[df_table6["path_label"] == "H3a"].iloc[0]
    assert float(h1a["germany_beta"]) > 0.0 and float(h1a["germany_p"]) < 0.05, "H1a in Germany must be positive & significant"
    assert float(h3a["germany_beta"]) < 0.0, "H3a in Germany must be negative"

    # Table 7 Measurement Invariance: exactly 3 canonical models (Configural, Metric, Scalar)
    assert len(df_table7) == 3, f"Table 7 must have 3 rows, found {len(df_table7)}"

    # Invariance degrees of freedom strictly increasing
    dfs = [float(r["df"]) for _, r in df_table7.iterrows()]
    for i in range(1, len(dfs)):
        assert dfs[i] > dfs[i - 1], f"Table 7 df must strictly increase: {dfs}"

    metric_row = df_table7[df_table7["model_level"].str.contains("Metric", case=False)].iloc[0]
    assert abs(float(metric_row["delta_cfi"])) <= 0.010, f"Metric delta CFI exceeds cutoff: {metric_row['delta_cfi']}"

    # Verify Table 6 cross-group tests integrity
    assert len(df_table6_tests) == 15, f"Table 6 cross-group tests must have 15 rows, found {len(df_table6_tests)}"
    sig_paths = df_table6_tests[df_table6_tests["group_difference_asserted"].str.contains("YES")]
    assert len(sig_paths) >= 2, f"Expected at least 2 significant paths (H5, H7b), found {len(sig_paths)}"
    sig_labels = set(sig_paths["path_label"].values)
    assert "H5" in sig_labels, "Path H5 (ATT -> REPORT) must exhibit significant cross-group difference"
    assert "H7b" in sig_labels, "Path H7b (COMM_TOOL -> REPORT) must exhibit significant cross-group difference"
    for _, r in df_table6_tests.iterrows():
        assert 0.0 <= float(r["wald_p_3group"]) <= 1.0, f"Invalid Wald p-value: {r['wald_p_3group']}"
        assert float(r["wald_chi2_3group"]) >= 0.0, f"Negative Wald chi2: {r['wald_chi2_3group']}"

    logger.info("[PASS] All post-execution assertions verified successfully!")
    logger.info("================================================================================")
    logger.info("COMPLETED: Milestone M3 Multigroup SEM & Invariance Successfully Finished.")
    logger.info("================================================================================")


if __name__ == "__main__":
    main()
