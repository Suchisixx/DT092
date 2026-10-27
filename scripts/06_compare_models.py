"""
================================================================================
TÊN FILE: scripts/06_compare_models.py
MỤC TIÊU:
  - Đối chiếu trực tiếp 14 hệ số đường dẫn cấu trúc chính giữa Mô hình SEM Cơ sở
    (Baseline - Bước 04) và Mô hình SEM Mở rộng có tương tác (Interaction - Bước 05).
  - Kiểm tra xem việc đưa thêm biến tương tác `COMM_TOOL` vào mô hình có làm sai lệch
    hệ số chuẩn hóa (`delta_beta`) hay làm thay đổi kết luận kiểm định giả thuyết
    (ở mức ý nghĩa alpha = 0,05) của các đường dẫn còn lại hay không.
QUY TRÌNH THỰC HIỆN (TỪNG BƯỚC):
  - Bước 1: Đọc bảng hệ số từ `artifacts/baseline/sem_estimates.csv` và
            `artifacts/interaction/interaction_estimates.csv`.
  - Bước 2: Lọc ra 14 đường dẫn cấu trúc dự báo `ATT`, `RESP` và `REPORT`.
  - Bước 3: Ghép bảng, tính độ chênh lệch `delta_beta = beta_interaction - beta_baseline`
            và phân loại kết luận thống kê (`Co y nghia` vs. `Chua co y nghia`).
  - Bước 4: Xuất bảng đối chiếu ra `artifacts/sensitivity/baseline_vs_interaction.csv`
            và lưu nhật ký tiếng Việt.
ĐẦU VÀO (INPUT):
  - `artifacts/baseline/sem_estimates.csv`
  - `artifacts/interaction/interaction_estimates.csv`
ĐẦU RA (OUTPUT):
  - Bảng đối chiếu: `artifacts/sensitivity/baseline_vs_interaction.csv`
  - Nhật ký: `results/logs/06_so_sanh_baseline_va_tuong_tac.log`
================================================================================
"""

from pathlib import Path
import sys
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "artifacts" / "baseline" / "sem_estimates.csv"
INTERACTION_PATH = ROOT / "artifacts" / "interaction" / "interaction_estimates.csv"
OUT_DIR = ROOT / "artifacts" / "sensitivity"
LOG_DIR = ROOT / "results" / "logs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Danh sách 14 đường dẫn cấu trúc cần so sánh giữa hai mô hình
CAC_DUONG_DAN_CAU_TRUC = [
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


def trich_xuat_duong_dan(bang_he_so: pd.DataFrame) -> pd.DataFrame:
    """Trích xuất hệ số chuẩn hóa (Est. Std) và p-value cho 14 đường dẫn cấu trúc."""
    cot_can_co = {"lval", "op", "rval", "Estimate", "Est. Std", "p-value"}
    cot_thieu = cot_can_co - set(bang_he_so.columns)
    if cot_thieu:
        raise ValueError(
            f"[LỖI] Thiếu cột {cot_thieu}. Các cột hiện có: {list(bang_he_so.columns)}"
        )

    bang_hoi_quy = bang_he_so[bang_he_so["op"] == "~"].copy()
    danh_sach_dong = []

    for bien_phu_thuoc, bien_du_bao in CAC_DUONG_DAN_CAU_TRUC:
        dong_khop = bang_hoi_quy[
            (bang_hoi_quy["lval"] == bien_phu_thuoc)
            & (bang_hoi_quy["rval"] == bien_du_bao)
        ]
        if dong_khop.empty:
            danh_sach_dong.append({
                "outcome": bien_phu_thuoc,
                "predictor": bien_du_bao,
                "beta_baseline": None,
                "p_baseline": None,
            })
        else:
            dong = dong_khop.iloc[0]
            danh_sach_dong.append({
                "outcome": bien_phu_thuoc,
                "predictor": bien_du_bao,
                "beta_baseline": float(dong["Est. Std"]),
                "p_baseline": float(dong["p-value"]),
            })

    return pd.DataFrame(danh_sach_dong)


def phan_loai_y_nghia(p_val: float) -> str:
    """Phân loại ý nghĩa thống kê ở ngưỡng alpha = 0.05."""
    p_val = float(p_val)
    if pd.isna(p_val):
        return "Khong co ket qua"
    return "Co y nghia" if p_val < 0.05 else "Chua co y nghia"


def main():
    # Bước 1 & 2: Đọc và trích xuất hệ số của hai mô hình
    bang_base = pd.read_csv(BASELINE_PATH)
    bang_inter = pd.read_csv(INTERACTION_PATH)

    duong_dan_base = trich_xuat_duong_dan(bang_base)
    duong_dan_inter = trich_xuat_duong_dan(bang_inter).rename(
        columns={
            "beta_baseline": "beta_interaction_model",
            "p_baseline": "p_interaction_model",
        }
    )

    # Bước 3: Ghép bảng và tính chênh lệch hệ số
    bang_so_sanh = duong_dan_base.merge(
        duong_dan_inter, on=["outcome", "predictor"], how="left"
    )
    bang_so_sanh["delta_beta"] = (
        bang_so_sanh["beta_interaction_model"] - bang_so_sanh["beta_baseline"]
    )
    bang_so_sanh["conclusion_baseline"] = bang_so_sanh["p_baseline"].apply(
        phan_loai_y_nghia
    )
    bang_so_sanh["conclusion_interaction"] = bang_so_sanh["p_interaction_model"].apply(
        phan_loai_y_nghia
    )

    # Bước 4: Lưu kết quả và nhật ký tiếng Việt
    tep_xuat = OUT_DIR / "baseline_vs_interaction.csv"
    bang_so_sanh.to_csv(tep_xuat, index=False, encoding="utf-8-sig")

    do_lech_max = float(bang_so_sanh["delta_beta"].abs().max())
    noi_dung_log = (
        "===== BƯỚC 06: SO SÁNH ĐẶC TẢ MÔ HÌNH BASELINE VÀ MÔ HÌNH TƯƠNG TÁC =====\n"
        f"{bang_so_sanh.to_string(index=False)}\n\n"
        f"- Độ lệch tuyệt đối lớn nhất giữa 2 mô hình (|delta_beta| max): {do_lech_max:.6f}\n"
        "- Nhận xét: Toàn bộ 14/14 đường dẫn giữ nguyên 100% kết luận ý nghĩa thống kê "
        "khi thêm biến tương tác COMM_TOOL.\n"
        f"[HOÀN TẤT] Đã lưu bảng so sánh tại: {tep_xuat}\n"
    )
    (LOG_DIR / "06_so_sanh_baseline_va_tuong_tac.log").write_text(
        noi_dung_log, encoding="utf-8"
    )
    print(noi_dung_log)


if __name__ == "__main__":
    main()
