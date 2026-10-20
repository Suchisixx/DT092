
from pathlib import Path
import json
import hashlib
import platform
from datetime import datetime, timezone

import pandas as pd
import semopy
from semopy import Model, calc_stats


# ============================================================
# E02: PAPER-ALIGNED SEM
# Giữ nguyên dữ liệu và baseline hiện có.
# Bổ sung NORM -> REPORT và AWARE -> REPORT.
# ============================================================

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "simulated" / "synthetic_sem.csv"
OUT_DIR = ROOT / "artifacts" / "paper_aligned"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_DESC = """
# Measurement model
NORM  =~ NORM1 + NORM2 + NORM3 + NORM4
AWARE =~ AWARE1 + AWARE2 + AWARE3 + AWARE4
KNOW  =~ KNOW1 + KNOW2 + KNOW3 + KNOW4
COMM  =~ COMM1 + COMM2 + COMM3 + COMM4
ATT   =~ ATT1 + ATT2 + ATT3 + ATT4
RESP  =~ RESP1 + RESP2 + RESP3 + RESP4

# Structural model: ATT and RESP
ATT  ~ NORM + AWARE + COMM + KNOW
RESP ~ NORM + AWARE + COMM + KNOW

# Structural model: REPORT
# Hai đường dẫn được bổ sung cho E02:
REPORT ~ NORM + AWARE + COMM + ATT + RESP + TOOL
"""


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Không tìm thấy dữ liệu: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    required = (
        [f"{c}{i}" for c in
         ["NORM", "AWARE", "KNOW", "COMM", "ATT", "RESP"]
         for i in range(1, 5)]
        + ["TOOL", "REPORT"]
    )

    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Thiếu cột dữ liệu: {missing}")

    if df[required].isnull().any().any():
        raise ValueError(
            "Dữ liệu có giá trị thiếu trong các biến của mô hình."
        )

    # Fit SEM
    model = Model(MODEL_DESC)
    fit_result = model.fit(df)

    # Parameter estimates
    estimates = model.inspect(std_est=True)
    estimates.to_csv(
        OUT_DIR / "paper_aligned_estimates.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Fit indices
    stats = calc_stats(model)
    stats.to_csv(
        OUT_DIR / "paper_aligned_fit_indices.csv",
        index=True,
        encoding="utf-8-sig"
    )

    # Lưu riêng các đường dẫn cấu trúc để thuận tiện đọc kết quả.
    structural = estimates[
        (estimates["op"] == "~")
        & (estimates["lval"].isin(["ATT", "RESP", "REPORT"]))
    ].copy()

    structural.to_csv(
        OUT_DIR / "paper_aligned_structural_paths.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Run metadata
    metadata = {
        "experiment_id": "E02",
        "model_name": "paper_aligned_sem",
        "data_file": str(DATA_PATH),
        "data_sha256": sha256_file(DATA_PATH),
        "n_rows": int(len(df)),
        "n_columns": int(len(df.columns)),
        "seed_used_for_data_generation": 20261016,
        "data_type": "synthetic",
        "estimator": "semopy default ML",
        "semopy_version": getattr(semopy, "__version__", "unknown"),
        "pandas_version": pd.__version__,
        "python_version": platform.python_version(),
        "fit_status": str(fit_result),
        "model_syntax": MODEL_DESC,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "note": (
            "Structural comparison model; not an exact replication "
            "of the original study."
        ),
    }

    with open(
        OUT_DIR / "paper_aligned_run_info.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print("\n===== E02: PAPER-ALIGNED SEM =====")
    print(f"So dong du lieu: {len(df)}")
    print(f"Ket qua fit: {fit_result}")
    print("\n===== FIT INDICES =====")
    print(stats.to_string())
    print("\n===== STRUCTURAL PATHS =====")
    print(structural.to_string(index=False))
    print(f"\nDa luu ket qua tai: {OUT_DIR}")


if __name__ == "__main__":
    main()
