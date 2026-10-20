
from pathlib import Path
import json
import pandas as pd
from semopy import Model, calc_stats

# Project root: thư mục chứa file script này
ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "simulated" / "synthetic_sem.csv"
OUT_DIR = ROOT / "artifacts" / "baseline"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Đọc dữ liệu
data = pd.read_csv(DATA_PATH)

# 2. Mô hình đo lường CFA: 6 cấu trúc tiềm ẩn
# =~ là ký hiệu cho biến ẩn bên trái được đo lường bởi các câu hỏi bên phải.
measurement_model = """
NORM =~ NORM1 + NORM2 + NORM3 + NORM4
AWARE =~ AWARE1 + AWARE2 + AWARE3 + AWARE4
KNOW =~ KNOW1 + KNOW2 + KNOW3 + KNOW4
COMM =~ COMM1 + COMM2 + COMM3 + COMM4
ATT =~ ATT1 + ATT2 + ATT3 + ATT4
RESP =~ RESP1 + RESP2 + RESP3 + RESP4
"""

# 3. Mô hình SEM cơ sở
# Các đường dẫn được xây dựng theo cấu trúc nghiên cứu.
# Cần đối chiếu lại bảng giả thuyết của bài báo trước khi xem đây là bản tái lập chính thức.
# ~ là ký hiệu cho biến ẩn bên trái bị tác động bởi các biến bên phải.

structural_model = measurement_model + """
ATT ~ NORM + AWARE + COMM + KNOW
RESP ~ NORM + AWARE + COMM + KNOW
REPORT ~ NORM + AWARE + COMM + ATT + RESP + TOOL
"""

def save_fit(model, dataset, prefix):
    """Ước lượng mô hình và lưu chỉ số phù hợp."""
    stats = calc_stats(model)
    stats.to_csv(OUT_DIR / f"{prefix}_fit_indices.csv")

    estimates = model.inspect(std_est=True)
    estimates.to_csv(
        OUT_DIR / f"{prefix}_estimates.csv",
        index=False
    )

    print(f"\n===== {prefix.upper()} =====")
    print(stats.T.to_string())
    print("\nCác hệ số ước lượng:")
    print(estimates.to_string(index=False))

    return stats, estimates

# 4. CFA
print("Đang chạy CFA...")
cfa = Model(measurement_model)
cfa.fit(data)
cfa_stats, cfa_estimates = save_fit(cfa, data, "cfa")

# 5. SEM baseline
print("\nĐang chạy SEM baseline...")
sem = Model(structural_model)
sem.fit(data)
sem_stats, sem_estimates = save_fit(sem, data, "sem")

# 6. Lưu thông tin chạy để tái lập
run_info = {
    "dataset": str(DATA_PATH),
    "n_rows": int(data.shape[0]),
    "n_columns": int(data.shape[1]),
    "data_type": "synthetic; not real respondents",
    "estimator": "semopy default ML",
    "cfa_model": measurement_model,
    "sem_model": structural_model,
    "note": (
        "Exploratory baseline. Verify model paths and estimator "
        "against the original paper before claiming replication."
    ),
}

with open(OUT_DIR / "run_info.json", "w", encoding="utf-8") as f:
    json.dump(run_info, f, ensure_ascii=False, indent=2)

print("\nHoàn tất. Kết quả được lưu tại:")
print(OUT_DIR)
