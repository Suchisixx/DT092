
from pathlib import Path
import json

import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "simulated" / "synthetic_sem.csv"
OUT = ROOT / "artifacts" / "sensitivity"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA)

# Tinh diem trung binh cho tung thang do
constructs = ["NORM", "AWARE", "KNOW", "COMM", "ATT", "RESP"]

for name in constructs:
    cols = [f"{name}{i}" for i in range(1, 5)]
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Thieu cot {missing}")
    df[name] = df[cols].mean(axis=1)

# Trung tam hoa COMM va TOOL, sau do tao tuong tac
df["COMM_c"] = df["COMM"] - df["COMM"].mean()
df["TOOL_c"] = df["TOOL"] - df["TOOL"].mean()
df["COMM_TOOL"] = df["COMM_c"] * df["TOOL_c"]

# Ba phuong trinh tuong ung voi mo hinh nghien cuu
models = {
    "ATT": ["NORM", "AWARE", "COMM", "KNOW"],
    "RESP": ["NORM", "AWARE", "COMM", "KNOW"],
    "REPORT": [
        "NORM", "AWARE", "COMM", "ATT", "RESP",
        "TOOL", "COMM_TOOL"
    ],
}

results = []

for outcome, predictors in models.items():
    X = sm.add_constant(df[predictors])
    y = df[outcome]

    # OLS voi sai so chuan vung HC3
    fit = sm.OLS(y, X).fit(cov_type="HC3")

    for predictor in predictors:
        results.append({
            "outcome": outcome,
            "predictor": predictor,
            "coefficient": fit.params[predictor],
            "robust_se_HC3": fit.bse[predictor],
            "t_value": fit.tvalues[predictor],
            "p_value": fit.pvalues[predictor],
            "ci_lower": fit.conf_int().loc[predictor, 0],
            "ci_upper": fit.conf_int().loc[predictor, 1],
            "significant_005": bool(fit.pvalues[predictor] < 0.05),
            "r_squared": fit.rsquared,
            "n": int(fit.nobs),
        })

    print(f"\n=== {outcome} ===")
    print(fit.summary())

result_df = pd.DataFrame(results)
result_df.to_csv(
    OUT / "hc3_sensitivity_results.csv",
    index=False,
    encoding="utf-8-sig"
)

info = {
    "data": str(DATA),
    "method": "OLS on construct mean scores with HC3 robust SE",
    "n": int(len(df)),
    "synthetic_data": True,
    "interpretation": (
        "Sensitivity analysis only; coefficients are not directly "
        "comparable to standardized latent SEM coefficients."
    ),
}

with open(OUT / "hc3_run_info.json", "w", encoding="utf-8") as f:
    json.dump(info, f, ensure_ascii=False, indent=2)

print("\nDa luu:", OUT / "hc3_sensitivity_results.csv")
