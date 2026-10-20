
from pathlib import Path
import json

import pandas as pd
import semopy
from semopy import Model, calc_stats

# --------------------------------------------------
# 1. Duong dan du lieu va thu muc ket qua
# --------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "simulated" / "synthetic_sem.csv"
OUT_DIR = ROOT / "artifacts" / "interaction"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 2. Doc du lieu
# --------------------------------------------------
df = pd.read_csv(DATA_PATH)

required = [
    "TOOL", "REPORT",
    *[f"COMM{i}" for i in range(1, 5)],
    *[f"NORM{i}" for i in range(1, 5)],
    *[f"AWARE{i}" for i in range(1, 5)],
    *[f"KNOW{i}" for i in range(1, 5)],
    *[f"ATT{i}" for i in range(1, 5)],
    *[f"RESP{i}" for i in range(1, 5)],
]

missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError(f"Thieu cot trong du lieu: {missing}")

# --------------------------------------------------
# 3. Tao bien tuong tac
# Dung diem trung binh COMM1-COMM4 lam dai dien
# cho COMM de tao bien tuong tac quan sat.
# --------------------------------------------------
df["COMM_mean"] = df[[f"COMM{i}" for i in range(1, 5)]].mean(axis=1)

df["COMM_c"] = df["COMM_mean"] - df["COMM_mean"].mean()
df["TOOL_c"] = df["TOOL"] - df["TOOL"].mean()
df["COMM_TOOL"] = df["COMM_c"] * df["TOOL_c"]

# --------------------------------------------------
# 4. Mo hinh CFA + SEM mo rong
# --------------------------------------------------
model_desc = """
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

# --------------------------------------------------
# 5. Uoc luong mo hinh
# --------------------------------------------------
model = Model(model_desc)
model.fit(df)

estimates = model.inspect(std_est=True)
fit = calc_stats(model)

estimates.to_csv(
    OUT_DIR / "interaction_estimates.csv",
    index=False,
    encoding="utf-8-sig"
)
fit.to_csv(
    OUT_DIR / "interaction_fit_indices.csv",
    encoding="utf-8-sig"
)

# --------------------------------------------------
# 6. Trich rieng ket qua bien tuong tac
# --------------------------------------------------
interaction = estimates[
    (estimates["lval"] == "REPORT")
    & (estimates["rval"] == "COMM_TOOL")
    & (estimates["op"] == "~")
].copy()

interaction.to_csv(
    OUT_DIR / "H7b_interaction_result.csv",
    index=False,
    encoding="utf-8-sig"
)

# Luu thong tin chay de tai lap
run_info = {
    "n": int(len(df)),
    "seed_inherited_from_dataset": 20261016,
    "semopy_version": semopy.__version__,
    "data_file": str(DATA_PATH),
    "interaction_definition": "(COMM_mean - mean(COMM_mean)) * "
                              "(TOOL - mean(TOOL))",
    "note": (
        "Synthetic data. Observed composite interaction proxy; "
        "not a full latent interaction estimator."
    )
}

with open(OUT_DIR / "run_info.json", "w", encoding="utf-8") as f:
    json.dump(run_info, f, ensure_ascii=False, indent=2)

print("\n=== INTERACTION MODEL: H7b ===")
print(interaction.to_string(index=False))
print("\n=== FIT INDICES ===")
print(fit.to_string())
print(f"\nDa luu ket qua tai: {OUT_DIR}")
