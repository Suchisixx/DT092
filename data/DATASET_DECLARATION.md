# DATASET DECLARATION: ETHICAL DISCLOSURE & SYNTHETIC DATA NOTICE

**Project:** DT092 Information Security Culture & Phishing-Reporting Multigroup SEM Replication  
**Reference Paper:** Petrič, G., & Just, J. N. (2025). *Information security culture and phishing-reporting model: structural equivalence across Germany, UK, and USA*. *Journal of Cybersecurity*, 11(1), tyaf011. DOI: [10.1093/cybsec/tyaf011](https://academic.oup.com/cybersecurity/article/11/1/tyaf011/8128837)  
**File Associated:** `data/synthetic_multigroup.csv`  

---

## 1. Non-Misrepresentation Guarantee
This dataset comprises **entirely synthetic, computer-simulated records** generated via a two-layer hierarchical Gaussian-copula latent variable model.

- **NOT Empirical Survey Data:** This dataset does **NOT** contain genuine empirical survey responses from actual human participants in Germany, the United Kingdom, or the United States.
- **No Human Subjects / Telemetry:** No individual privacy, organizational IT infrastructure, or corporate telemetry was sampled, collected, or exposed.
- **Academic Simulation Purpose:** The dataset was constructed solely to evaluate structural equation modeling (SEM), confirmatory factor analysis (CFA), and measurement invariance algorithms against published statistical benchmarks.

---

## 2. Sample Structure & Provenance
- **Total Sample Size:** $N = 1,017$ respondents
  - **Germany (`DE`):** $n = 306$ ($30.09\%$)
  - **United Kingdom (`UK`):** $n = 205$ ($20.16\%$)
  - **United States (`US`):** $n = 506$ ($49.75\%$)
- **Indicator Dimensions:** 24 survey indicators across 6 latent constructs (`NORM`, `AWARE`, `KNOW`, `COMM`, `ATT`, `RESP`), 1 binary tool presence indicator (`TOOL`), and 1 terminal phishing-reporting frequency indicator (`REPORT`).
- **Reverse Coding Recoding:** Items `KNOW3`, `AWARE3`, `NORM3`, `ATT2`, and `ATT3` were reverse-worded in the operational questionnaire and recoded ($X_{\text{recoded}} = 6 - X_{\text{raw}}$) to ensure uniform positive alignment with theoretical constructs.
