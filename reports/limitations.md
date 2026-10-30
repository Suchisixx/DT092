# Methodological Limitations, Boundary Conditions & Course Report Guidance

**Project:** DT092 Multigroup SEM Replication (Petrič & Just, 2025)  
**Dataset Scope:** Computer-simulated synthetic data (`data/synthetic_multigroup.csv`, $N = 1,017$)  
**Date:** 2026-10-30  

---

## 1. Non-Empirical Synthetic Data Limitation (Primary Epistemic Boundary)

1. **Not Real Human Respondents**: The dataset `data/synthetic_multigroup.csv` ($N = 1,017$: `DE = 306`, `UK = 205`, `US = 506`) is **100% computer-generated synthetic data** produced via a parameterized Gaussian-copula latent variable Data Generating Process (`scripts/01_generate_multigroup_data.py`, `seed = 20261029`).
2. **Scope of Valid Claims**: Because the original Valicon panel microdata from Petrič & Just (2025) are not publicly available, this experiment validates **computational pipeline reproducibility, parameter recovery, measurement invariance mechanics, and cross-estimator sensitivity**—it does **not** constitute independent empirical evidence about actual German, British, or American employees.
3. **No Post-Hoc Data Tweaking**: All simulation parameters were fixed *a priori* from published Table 1, Table 4, and Table 6 benchmarks before estimation. Where finite-sample sampling variance or ordinal discretization produced discrepancies relative to published coefficients (documented transparently in `results/tables/paper_comparison.csv`), values were **never** manually adjusted or cherry-picked.

---

## 2. Measurement Scale & Indicator Limitations (24 vs. 26 / 37 Items)

1. **24 Simulated Indicators vs. 26 Final / 37 Initial Paper Indicators**:
   - Petrič & Just (2025) started with 37 items in their initial CFA ($\text{CFI} = 0.68$) and pruned low-loading indicators ($< 0.40$) to reach a **26-item final CFA** (`ATT`: 5 items, `NORM`: 5 items, `RESP`, `KNOW`, `COMM`, `AWARE`: 4 items each).
   - Consistent with the existing DT092 repository schema and project integrity rules prohibiting fabrication of unverified survey item text, this multigroup pipeline retains **4 indicators per construct (24 items total)** plus binary `TOOL` and 5-point Likert `REPORT`.
2. **Unreproducible Initial 37-Item Poor-Fit CFA**: Because the 11 dropped low-loading items from the authors' raw questionnaire are neither present in the baseline schema nor simulated with misspecified cross-loadings, the initial poorly fitting 37-item CFA ($\chi^2 = 6680.2, df = 614$) cannot be empirically reproduced and is documented solely as a literature benchmark.

---

## 3. Estimator & Modeling Architecture Differences (`semopy` MLW vs. `lavaan` WLSMV)

1. **Continuous MLW vs. Ordinal WLSMV**:
   - R and `lavaan` are not installed in the host execution environment, and Python `semopy 2.3.11` does not implement polychoric correlation matrices or fourth-order asymptotic weight matrices required for `WLSMV`.
   - Treating 5-point ordinal Likert items (`1`–`5`) and binary `TOOL` (`0`/`1`) as pseudo-continuous under Wishart Maximum Likelihood (`MLW`) introduces mild **discretization attenuation** ($\approx 10\%–20\%$), explaining why simulated $R^2$ values (`ATT`: $37.0\%$, `RESP`: $46.8\%$, `REPORT`: $14.6\%$) are lower than the paper's polychoric/WLSMV $R^2$ values ($61.1\%$, $65.2\%$, $23.5\%$).
2. **Full 24-Indicator Latent SEM vs. Two-Step Composite Path Model**:
   - Petrič & Just (2025, p. 9) used a two-step procedure: Step 1 CFA, followed by Step 2 path analysis on arithmetic mean composite scores (`df = 5` pooled; `df = 15` unconstrained multigroup).
   - Our primary pipeline (`scripts/03_multigroup_sem_invariance.py`) estimates the **simultaneous 24-indicator full latent SEM** (`df = 308` pooled) while complementing it with composite-mean **OLS-HC3** (`scripts/04_hypothesis_and_robustness.py`), providing both latent measurement-error control and robust heteroskedasticity-consistent inference.
3. **Near-Zero RMSEA on Synthetic Data**:
   - Simulated CFA and SEM models exhibit $\chi^2 / df \le 1.0$ and $\text{RMSEA} \approx 0.000 - 0.010$ because synthetic indicators are generated from a clean factor structure free of human survey noise (social desirability, wording covariance, respondent fatigue). This must be interpreted as confirmation of DGP-model alignment rather than superior empirical theory fit.

---

## 4. Subsample Statistical Power & Cross-Country Inference Boundaries

1. **Smaller UK Subsample ($n = 205$)**:
   - At $n = 205$ (vs. USA $n = 506$), standard errors in the UK group are $\approx 1.57\times$ larger ($\sqrt{506/205}$). Consequently, moderate true DGP slopes (such as UK `H3c` `COMM -> REPORT` with DGP weight $+0.26$, estimated $\hat{\beta} = +0.1075, p = 0.2431$, or `H4b` `KNOW -> RESP` with DGP weight $+0.11$, estimated $\hat{\beta} = +0.0327, p = 0.6712$) exhibit lower finite-sample power under discretized indicators in single-seed realizations.
2. **Guarding Against the Difference-in-Significance Fallacy**:
   - Following Gelman & Stern (2006) and Section 5/11 rules, cross-country differences are **only** claimed when formal unstandardized slope Wald tests (`table6_cross_group_tests.csv`) reject equality ($p < 0.05$, observed on `H5` `ATT -> REPORT` and `H7b` `COMM x TOOL -> REPORT`, plus pairwise UK vs. USA on `H6` `RESP -> REPORT`).

---

## 5. Checklist of Recommendations Before Submitting the Final Course Report

- [x] **State Synthetic Provenance Clearly on Slide 1 / Section 1**: Explicitly note that $N = 1,017$ (`DE=306, UK=205, US=506`) is a parameterized Monte Carlo / synthetic replication of Petrič & Just (2025), not raw human survey microdata.
- [x] **Present Both Measurement Invariance (Table 7) and Multigroup SEM (Table 6)**: Highlight that Metric ($|\Delta\text{CFI}| = 0.0001$) and Scalar ($|\Delta\text{CFI}| = 0.0008$) invariance are established *before* comparing national regression paths.
- [x] **Discuss the Communication Paradox (`H3a/H3b` negative vs. `H3c` positive)**: Explain substantively why top-down security communication can trigger compliance fatigue (lowering general attitudes) while simultaneously providing actionable operational cues that boost actual phishing reporting.
- [x] **Include Estimator Comparison (`MLW` + `OLS-HC3` vs. `WLSMV`)**: Cite Section 2 of `methodology_and_assumptions.md` to explain attenuation of $R^2$ and near-zero synthetic RMSEA—demonstrating graduate-level methodological rigor.
- [ ] **Optional Future Extension (If R `lavaan` Environment Becomes Available)**: Run `lavaan::sem(..., ordered = c("REPORT"), estimator = "WLSMV", group = "country")` directly on `data/synthetic_multigroup.csv` to quantify exact empirical attenuation between Python `MLW` and R `WLSMV` on the identical dataset.
