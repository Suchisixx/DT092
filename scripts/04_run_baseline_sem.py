"""
================================================================================
TÊN FILE: scripts/04_run_baseline_sem.py
MỤC TIÊU:
  - Ước lượng Mô hình đo lường CFA (Confirmatory Factor Analysis) cho 6 cấu trúc
    tiềm ẩn của Văn hóa An toàn thông tin (`NORM`, `AWARE`, `KNOW`, `COMM`, `ATT`, `RESP`).
  - Ước lượng Mô hình cấu trúc SEM cơ sở (Baseline SEM, chưa có tương tác) để
    kiểm định các đường dẫn từ văn hóa ATTT đến thái độ (`ATT`), trách nhiệm (`RESP`)
    và tần suất báo cáo phishing (`REPORT`).
QUY TRÌNH THỰC HIỆN (TỪNG BƯỚC):
  - Bước 1: Đọc bộ dữ liệu đã qua kiểm định `data/simulated/synthetic_sem.csv`.
  - Bước 2: Khai báo cú pháp mô hình đo lường CFA (6 nhân tố × 4 chỉ báo = 24 biến)
            và khớp mô hình bằng `semopy` (phương pháp hợp lý cực đại MLW).
  - Bước 3: Khai báo cú pháp mô hình cấu trúc SEM cơ sở (gồm phương trình dự báo
            `ATT`, `RESP` và `REPORT`) và ước lượng hệ số chuẩn hóa (`Est. Std`).
  - Bước 4: Lưu các bảng Fit Indices, bảng hệ số ước lượng và nhật ký tiếng Việt.
ĐẦU VÀO (INPUT):
  - Dữ liệu: `data/simulated/synthetic_sem.csv`
ĐẦU RA (OUTPUT):
  - Chỉ số phù hợp & Hệ số CFA: `artifacts/baseline/cfa_fit_indices.csv`,
                                `artifacts/baseline/cfa_estimates.csv`
  - Chỉ số phù hợp & Hệ số SEM: `artifacts/baseline/sem_fit_indices.csv`,
                                `artifacts/baseline/sem_estimates.csv`
  - Metadata: `artifacts/baseline/run_info.json`
  - Nhật ký: `results/logs/04_cfa_va_sem_baseline.log`
================================================================================
"""

import json
from pathlib import Path
import sys
import pandas as pd
from semopy import Model, calc_stats

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Xác định đường dẫn gốc và thư mục lưu kết quả
ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "simulated" / "synthetic_sem.csv"
OUT_DIR = ROOT / "artifacts" / "baseline"
LOG_DIR = ROOT / "results" / "logs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 1. Đọc dữ liệu mô phỏng
data = pd.read_csv(DATA_PATH)

# 2. Định nghĩa Mô hình đo lường CFA: 6 cấu trúc tiềm ẩn (mỗi cấu trúc 4 câu hỏi Likert)
# Toán tử `=~` trong semopy biểu diễn biến tiềm ẩn (bên trái) được đo bởi các biến quan sát (bên phải)
measurement_model = """
NORM =~ NORM1 + NORM2 + NORM3 + NORM4
AWARE =~ AWARE1 + AWARE2 + AWARE3 + AWARE4
KNOW =~ KNOW1 + KNOW2 + KNOW3 + KNOW4
COMM =~ COMM1 + COMM2 + COMM3 + COMM4
ATT =~ ATT1 + ATT2 + ATT3 + ATT4
RESP =~ RESP1 + RESP2 + RESP3 + RESP4
"""

# 3. Định nghĩa Mô hình cấu trúc SEM cơ sở (Baseline SEM)
# Toán tử `~` biểu diễn phương trình hồi quy cấu trúc (biến phụ thuộc bên trái, các biến dự báo bên phải)
structural_model = measurement_model + """
ATT ~ NORM + AWARE + COMM + KNOW
RESP ~ NORM + AWARE + COMM + KNOW
REPORT ~ NORM + AWARE + COMM + ATT + RESP + TOOL
"""


def luu_ket_qua_mo_hinh(mo_hinh: Model, tien_to: str, tieu_de: str):
    """Tính toán chỉ số độ phù hợp (Fit Indices), trích xuất hệ số chuẩn hóa và lưu CSV."""
    bang_fit = calc_stats(mo_hinh)
    bang_fit.to_csv(OUT_DIR / f"{tien_to}_fit_indices.csv")

    bang_he_so = mo_hinh.inspect(std_est=True)
    bang_he_so.to_csv(OUT_DIR / f"{tien_to}_estimates.csv", index=False)

    chuoi_ket_qua = (
        f"\n===== {tieu_de} ({tien_to.upper()}) =====\n"
        f"[1] Chỉ số độ phù hợp mô hình (Fit Indices):\n{bang_fit.T.to_string()}\n\n"
        f"[2] Các hệ số ước lượng (Estimates):\n{bang_he_so.to_string(index=False)}\n"
    )
    print(chuoi_ket_qua)
    return bang_fit, bang_he_so, chuoi_ket_qua


def main():
    nhat_ky = ["===== BƯỚC 04: ƯỚC LƯỢNG MÔ HÌNH ĐO LƯỜNG CFA VÀ SEM CƠ SỞ ====="]

    # Bước 4a: Ước lượng CFA
    print("Đang ước lượng mô hình đo lường CFA (6 nhân tố, 24 biến chỉ báo)...")
    cfa = Model(measurement_model)
    cfa.fit(data)
    _, _, log_cfa = luu_ket_qua_mo_hinh(cfa, "cfa", "MÔ HÌNH ĐO LƯỜNG CFA")
    nhat_ky.append(log_cfa)

    # Bước 4b: Ước lượng SEM Baseline
    print("\nĐang ước lượng mô hình phương trình cấu trúc SEM cơ sở (Baseline)...")
    sem = Model(structural_model)
    sem.fit(data)
    _, sem_est, log_sem = luu_ket_qua_mo_hinh(sem, "sem", "MÔ HÌNH CẤU TRÚC SEM CƠ SỞ")
    nhat_ky.append(log_sem)

    # Trích riêng 14 đường dẫn cấu trúc (Structural Paths) để dễ tra cứu
    structural_paths = sem_est[
        (sem_est["op"] == "~") & (sem_est["lval"].isin(["ATT", "RESP", "REPORT"]))
    ].copy()
    structural_paths.to_csv(
        OUT_DIR / "sem_structural_paths.csv", index=False, encoding="utf-8-sig"
    )

    # Lưu thông tin metadata của lần chạy
    run_info = {
        "dataset": str(DATA_PATH),
        "n_rows": int(data.shape[0]),
        "n_columns": int(data.shape[1]),
        "data_type": "Dữ liệu mô phỏng (synthetic); không phải người trả lời thật",
        "estimator": "semopy default MLW (Maximum Likelihood Wishart)",
        "cfa_model": measurement_model,
        "sem_model": structural_model,
        "note": (
            "Mô hình SEM cơ sở (Baseline) kiểm định các đường dẫn trực tiếp và gián tiếp "
            "chưa có biến tương tác COMM x TOOL."
        ),
    }
    with open(OUT_DIR / "run_info.json", "w", encoding="utf-8") as tep_json:
        json.dump(run_info, tep_json, ensure_ascii=False, indent=2)

    thong_bao_cuoi = f"\n[HOÀN TẤT] Kết quả CFA và SEM cơ sở đã được lưu tại: {OUT_DIR}\n"
    nhat_ky.append(thong_bao_cuoi)
    (LOG_DIR / "04_cfa_va_sem_baseline.log").write_text(
        "\n".join(nhat_ky), encoding="utf-8"
    )
    print(thong_bao_cuoi)


if __name__ == "__main__":
    main()
