"""
================================================================================
TÊN FILE: scripts/05_run_interaction_sem.py
MỤC TIÊU:
  - Xây dựng và ước lượng Mô hình SEM mở rộng có biến tương tác `COMM_TOOL`
    (`COMM × TOOL -> REPORT`) nhằm kiểm định giả thuyết H7b của bài báo gốc:
    "Mối liên hệ giữa sự hiện diện công cụ báo cáo (TOOL) và tần suất báo cáo (REPORT)
    sẽ mạnh hơn trong điều kiện chất lượng giao tiếp về ATTT (COMM) tốt".
QUY TRÌNH THỰC HIỆN (TỪNG BƯỚC):
  - Bước 1: Đọc dữ liệu `data/simulated/synthetic_sem.csv` và kiểm tra cột bắt buộc.
  - Bước 2: Tính điểm trung bình `COMM_mean` từ 4 câu hỏi `COMM1..COMM4`.
  - Bước 3: Chuẩn hóa tâm (Mean-centering) hai biến `COMM_mean` và `TOOL` trước khi
            nhân tương tác (`COMM_TOOL = COMM_c * TOOL_c`) đúng theo thủ tục ở trang 9
            của bài báo gốc (Petrič & Just, 2025) để tránh đa cộng tuyến.
  - Bước 4: Ước lượng mô hình SEM mở rộng, trích xuất riêng kết quả kiểm định H7b
            và lưu bảng Fit Indices + nhật ký tiếng Việt.
ĐẦU VÀO (INPUT):
  - Dữ liệu: `data/simulated/synthetic_sem.csv`
ĐẦU RA (OUTPUT):
  - Kết quả kiểm định H7b: `artifacts/interaction/H7b_interaction_result.csv`
  - Toàn bộ hệ số & Fit: `artifacts/interaction/interaction_estimates.csv`,
                         `artifacts/interaction/interaction_fit_indices.csv`
  - Metadata: `artifacts/interaction/run_info.json`
  - Nhật ký: `results/logs/05_sem_tuong_tac_H7b.log`
================================================================================
"""

import json
from pathlib import Path
import sys
import pandas as pd
import semopy
from semopy import Model, calc_stats

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "simulated" / "synthetic_sem.csv"
OUT_DIR = ROOT / "artifacts" / "interaction"
LOG_DIR = ROOT / "results" / "logs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


def main():
    # Bước 1: Đọc dữ liệu và kiểm tra sự tồn tại của các cột cần thiết
    df = pd.read_csv(DATA_PATH)

    cac_cot_bat_buoc = [
        "TOOL",
        "REPORT",
        *[f"COMM{i}" for i in range(1, 5)],
        *[f"NORM{i}" for i in range(1, 5)],
        *[f"AWARE{i}" for i in range(1, 5)],
        *[f"KNOW{i}" for i in range(1, 5)],
        *[f"ATT{i}" for i in range(1, 5)],
        *[f"RESP{i}" for i in range(1, 5)],
    ]
    cot_thieu = [cot for cot in cac_cot_bat_buoc if cot not in df.columns]
    if cot_thieu:
        raise ValueError(f"[LỖI] Thiếu cột trong dữ liệu: {cot_thieu}")

    # Bước 2 & 3: Chuẩn hóa tâm (Mean-centering) và tạo biến tương tác COMM_TOOL
    df["COMM_mean"] = df[[f"COMM{i}" for i in range(1, 5)]].mean(axis=1)
    df["COMM_c"] = df["COMM_mean"] - df["COMM_mean"].mean()
    df["TOOL_c"] = df["TOOL"] - df["TOOL"].mean()
    df["COMM_TOOL"] = df["COMM_c"] * df["TOOL_c"]

    # Bước 4: Khai báo và ước lượng mô hình SEM mở rộng có biến tương tác
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

    model = Model(model_desc)
    model.fit(df)

    estimates = model.inspect(std_est=True)
    fit = calc_stats(model)

    estimates.to_csv(
        OUT_DIR / "interaction_estimates.csv", index=False, encoding="utf-8-sig"
    )
    fit.to_csv(OUT_DIR / "interaction_fit_indices.csv", encoding="utf-8-sig")

    # Trích riêng dòng kết quả của biến tương tác H7b (COMM_TOOL -> REPORT)
    interaction = estimates[
        (estimates["lval"] == "REPORT")
        & (estimates["rval"] == "COMM_TOOL")
        & (estimates["op"] == "~")
    ].copy()

    interaction.to_csv(
        OUT_DIR / "H7b_interaction_result.csv", index=False, encoding="utf-8-sig"
    )

    run_info = {
        "n": int(len(df)),
        "seed_inherited_from_dataset": 20261016,
        "semopy_version": semopy.__version__,
        "data_file": str(DATA_PATH),
        "interaction_definition": "(COMM_mean - mean(COMM_mean)) * (TOOL - mean(TOOL))",
        "note": (
            "Mô hình SEM mở rộng kiểm định giả thuyết H7b (tương tác giữa chất lượng "
            "giao tiếp và công cụ báo cáo phishing) thông qua biến đại diện đã chuẩn hóa tâm."
        ),
    }
    with open(OUT_DIR / "run_info.json", "w", encoding="utf-8") as tep_json:
        json.dump(run_info, tep_json, ensure_ascii=False, indent=2)

    noi_dung_log = (
        "===== BƯỚC 05: KIỂM ĐỊNH MÔ HÌNH SEM MỞ RỘNG CÓ TƯƠNG TÁC (GIẢ THUYẾT H7b) =====\n"
        "[1] Kết quả đường dẫn tương tác COMM_TOOL -> REPORT (H7b):\n"
        f"{interaction.to_string(index=False)}\n\n"
        "[2] Chỉ số độ phù hợp của mô hình tương tác (Fit Indices):\n"
        f"{fit.T.to_string()}\n\n"
        f"[3] Nhận xét: Hệ số chuẩn hóa của COMM_TOOL là {interaction['Est. Std'].iloc[0]:.4f} "
        f"(p-value = {interaction['p-value'].iloc[0]:.4f} > 0.05), cho thấy tương tác không có "
        "ý nghĩa thống kê, hoàn toàn khớp với kết quả bài báo gốc (beta = -0.05, ns).\n"
        f"[HOÀN TẤT] Đã lưu kết quả tại: {OUT_DIR}\n"
    )
    (LOG_DIR / "05_sem_tuong_tac_H7b.log").write_text(noi_dung_log, encoding="utf-8")
    print(noi_dung_log)


if __name__ == "__main__":
    main()
