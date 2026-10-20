
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

BASELINE = ROOT / "artifacts" / "baseline" / "sem_estimates.csv"
INTERACTION = ROOT / "artifacts" / "interaction" / "interaction_estimates.csv"
OUT = ROOT / "artifacts" / "sensitivity"
OUT.mkdir(parents=True, exist_ok=True)

base = pd.read_csv(BASELINE)
inter = pd.read_csv(INTERACTION)

# Chi giu cac duong dan cau truc de so sanh
paths = [
    ("ATT", "NORM"),
    ("ATT", "AWARE"),
    ("ATT", "COMM"),
    ("ATT", "KNOW"),
    ("RESP", "NORM"),
    ("RESP", "AWARE"),
    ("RESP", "COMM"),
    ("RESP", "KNOW"),
    ("REPORT", "NORM"),
    ("REPORT", "AWARE"),
    ("REPORT", "COMM"),
    ("REPORT", "ATT"),
    ("REPORT", "RESP"),
    ("REPORT", "TOOL"),
]

def extract_paths(df):
    required = {"lval", "op", "rval", "Estimate", "Est. Std", "p-value"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Thieu cot {missing}. Cac cot hien co: {list(df.columns)}"
        )

    df = df[df["op"] == "~"].copy()
    rows = []

    for outcome, predictor in paths:
        match = df[
            (df["lval"] == outcome) &
            (df["rval"] == predictor)
        ]

        if match.empty:
            rows.append({
                "outcome": outcome,
                "predictor": predictor,
                "beta_baseline": None,
                "p_baseline": None,
            })
        else:
            r = match.iloc[0]
            rows.append({
                "outcome": outcome,
                "predictor": predictor,
                "beta_baseline": r["Est. Std"],
                "p_baseline": r["p-value"],
            })

    return pd.DataFrame(rows)

b = extract_paths(base)
i = extract_paths(inter)

# Doi ten cot mo hinh tuong tac
i = i.rename(columns={
    "beta_baseline": "beta_interaction_model",
    "p_baseline": "p_interaction_model",
})

out = b.merge(i, on=["outcome", "predictor"], how="left")
out["delta_beta"] = (
    out["beta_interaction_model"] - out["beta_baseline"]
)

def classify(p):
    p = float(p)

    if pd.isna(p):
        return "Khong co ket qua"
    
    return "Co y nghia" if p < 0.05 else "Chua co y nghia"

out["conclusion_baseline"] = out["p_baseline"].apply(classify)
out["conclusion_interaction"] = out["p_interaction_model"].apply(classify)

out.to_csv(
    OUT / "baseline_vs_interaction.csv",
    index=False,
    encoding="utf-8-sig",
)

print(out.to_string(index=False))
print(f"\nDa luu: {OUT / 'baseline_vs_interaction.csv'}")
