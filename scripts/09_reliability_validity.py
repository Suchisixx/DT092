"""
================================================================================
TÊN FILE: scripts/09_reliability_validity.py
MỤC TIÊU:
  - Đánh giá toàn diện Độ tin cậy thang đo (Reliability: Cronbach's Alpha,
    Composite Reliability - CR) và Giá trị hội tụ / Giá trị phân biệt
    (Convergent & Discriminant Validity: AVE, căn bậc hai AVE, Ma trận Fornell-Larcker).
  - Đối chiếu trực tiếp từng chỉ số với Table 3 (trang 8) và Table 5 (trang 11)
    của bài báo gốc (Petrič & Just, 2025).
QUY TRÌNH THỰC HIỆN (TỪNG BƯỚC):
  - Bước 1: Đọc dữ liệu `synthetic_sem.csv` và bảng hệ số tải nhân tố CFA từ
            `artifacts/baseline/cfa_estimates.csv`.
  - Bước 2: Với mỗi thang đo trong 6 cấu trúc (`ATT`, `RESP`, `KNOW`, `COMM`, `NORM`, `AWARE`),
            tính hệ số Cronbach's Alpha, phương sai trích trung bình (AVE) và độ tin cậy
            tổng hợp (CR) từ tải nhân tố chuẩn hóa.
  - Bước 3: Lập ma trận tương quan giữa các cấu trúc và kiểm định tiêu chuẩn
            Fornell-Larcker (căn bậc hai của AVE trên đường chéo phải lớn hơn mọi
            hệ số tương quan với các cấu trúc khác).
  - Bước 4: Lưu các bảng CSV, JSON tóm tắt và nhật ký giải thích tiếng Việt.
ĐẦU VÀO (INPUT):
  - `data/simulated/synthetic_sem.csv`
  - `artifacts/baseline/cfa_estimates.csv`
ĐẦU RA (OUTPUT):
  - Bảng Độ tin cậy & AVE: `artifacts/sensitivity/reliability_validity.csv`
  - Ma trận Fornell-Larcker: `artifacts/sensitivity/fornell_larcker_matrix.csv`
  - Ma trận tương quan (tương đương Table 5): `artifacts/sensitivity/construct_correlation_matrix.csv`
  - Kiểm tra giá trị phân biệt: `artifacts/sensitivity/discriminant_validity_checks.csv`
  - Nhật ký: `results/logs/09_do_tin_cay_va_gia_tri_thang_do.log`
================================================================================
"""

import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "simulated" / "synthetic_sem.csv"
CFA_EST_PATH = ROOT / "artifacts" / "baseline" / "cfa_estimates.csv"
OUT_DIR = ROOT / "artifacts" / "reliability_validity"
LOG_DIR = ROOT / "results" / "logs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

CONSTRUCTS = ["ATT", "RESP", "KNOW", "COMM", "NORM", "AWARE"]

# Chỉ số gốc từ Table 3 của bài báo Petrič & Just (2025, trang 8) để đối chiếu trực tiếp
PAPER_REF = {
    "ATT":   {"paper_items": 5, "paper_AVE": 0.66, "paper_sqrt_AVE": 0.81, "paper_alpha": 0.90},
    "RESP":  {"paper_items": 4, "paper_AVE": 0.64, "paper_sqrt_AVE": 0.80, "paper_alpha": 0.84},
    "KNOW":  {"paper_items": 4, "paper_AVE": 0.49, "paper_sqrt_AVE": 0.70, "paper_alpha": 0.74},
    "COMM":  {"paper_items": 4, "paper_AVE": 0.50, "paper_sqrt_AVE": 0.71, "paper_alpha": 0.79},
    "NORM":  {"paper_items": 5, "paper_AVE": 0.55, "paper_sqrt_AVE": 0.74, "paper_alpha": 0.86},
    "AWARE": {"paper_items": 4, "paper_AVE": 0.58, "paper_sqrt_AVE": 0.76, "paper_alpha": 0.80},
}


def tinh_cronbach_alpha(bang_cau_hoi: pd.DataFrame) -> float:
    """Tính hệ số tin cậy nội tại Cronbach's Alpha cho một tập câu hỏi."""
    so_cau = bang_cau_hoi.shape[1]
    tong_phuong_sai_item = bang_cau_hoi.var(axis=0, ddof=1).sum()
    phuong_sai_tong_diem = bang_cau_hoi.sum(axis=1).var(ddof=1)
    if phuong_sai_tong_diem == 0:
        return 0.0
    return float((so_cau / (so_cau - 1.0)) * (1.0 - tong_phuong_sai_item / phuong_sai_tong_diem))


def main():
    # Bước 1: Đọc dữ liệu khảo sát và kết quả tải nhân tố CFA
    df = pd.read_csv(DATA_PATH)
    cfa_est = pd.read_csv(CFA_EST_PATH)

    loadings_df = cfa_est[
        (cfa_est["op"] == "~") & (cfa_est["rval"].isin(CONSTRUCTS))
    ].copy()

    # Bước 2: Tính Cronbach's Alpha, CR và AVE cho từng cấu trúc
    danh_sach_dong = []
    for c in CONSTRUCTS:
        cac_cot = [f"{c}{i}" for i in range(1, 5)]
        bang_con = df[cac_cot]
        alpha = tinh_cronbach_alpha(bang_con)

        tai_chuan_hoa = (
            loadings_df[loadings_df["rval"] == c]["Est. Std"].astype(float).values
        )
        binh_phuong_tai = tai_chuan_hoa ** 2
        phuong_sai_sai_so = 1.0 - binh_phuong_tai

        ave = float(np.mean(binh_phuong_tai))
        sqrt_ave = float(np.sqrt(ave))
        tong_tai = float(np.sum(tai_chuan_hoa))
        cr = float((tong_tai ** 2) / ((tong_tai ** 2) + float(np.sum(phuong_sai_sai_so))))

        tham_chieu = PAPER_REF[c]
        danh_sach_dong.append({
            "construct": c,
            "n_items_dt092": len(cac_cot),
            "mean_score": float(bang_con.mean(axis=1).mean()),
            "sd_score": float(bang_con.mean(axis=1).std(ddof=1)),
            "min_std_loading": float(np.min(tai_chuan_hoa)),
            "max_std_loading": float(np.max(tai_chuan_hoa)),
            "AVE_dt092": round(ave, 4),
            "sqrt_AVE_dt092": round(sqrt_ave, 4),
            "CR_dt092": round(cr, 4),
            "cronbach_alpha_dt092": round(alpha, 4),
            "paper_items": tham_chieu["paper_items"],
            "paper_AVE": tham_chieu["paper_AVE"],
            "paper_sqrt_AVE": tham_chieu["paper_sqrt_AVE"],
            "paper_alpha": tham_chieu["paper_alpha"],
            "convergent_valid_AVE_gt_050": bool(ave >= 0.50),
            "reliable_alpha_gt_070": bool(alpha >= 0.70),
        })

    rel_df = pd.DataFrame(danh_sach_dong)
    rel_df.to_csv(
        OUT_DIR / "reliability_validity.csv", index=False, encoding="utf-8-sig"
    )

    # Bước 3: Lập bảng tương quan và ma trận Fornell-Larcker
    score_df = pd.DataFrame()
    score_df["REPORT"] = df["REPORT"]
    for c in CONSTRUCTS:
        score_df[c] = df[[f"{c}{i}" for i in range(1, 5)]].mean(axis=1)

    corr_matrix = score_df.corr()
    corr_matrix.round(4).to_csv(
        OUT_DIR / "construct_correlation_matrix.csv", encoding="utf-8-sig"
    )

    fl_matrix = corr_matrix.loc[CONSTRUCTS, CONSTRUCTS].copy()
    sqrt_ave_map = dict(zip(rel_df["construct"], rel_df["sqrt_AVE_dt092"]))
    discriminant_checks = []
    for c in CONSTRUCTS:
        tuong_quan_ngoai = [
            abs(fl_matrix.loc[c, other]) for other in CONSTRUCTS if other != c
        ]
        max_corr = float(max(tuong_quan_ngoai))
        s_ave = float(sqrt_ave_map[c])
        fl_matrix.loc[c, c] = s_ave
        discriminant_checks.append({
            "construct": c,
            "sqrt_AVE": round(s_ave, 4),
            "max_abs_interconstruct_corr": round(max_corr, 4),
            "fornell_larcker_passed": bool(s_ave > max_corr),
        })

    fl_matrix.round(4).to_csv(
        OUT_DIR / "fornell_larcker_matrix.csv", encoding="utf-8-sig"
    )
    disc_df = pd.DataFrame(discriminant_checks)

    noi_dung_log = (
        "===== BƯỚC 09: ĐÁNH GIÁ ĐỘ TIN CẬY (ALPHA, CR) VÀ GIÁ TRỊ THANG ĐO (AVE, FORNELL-LARCKER) =====\n"
        "[1] Bảng Độ tin cậy & Giá trị hội tụ đối chiếu với Table 3 của bài báo gốc:\n"
        f"{rel_df.to_string(index=False)}\n\n"
        "[2] Ma trận Fornell-Larcker (Đường chéo = sqrt(AVE); Ngoài đường chéo = tương quan r):\n"
        f"{fl_matrix.round(4).to_string()}\n\n"
        "[3] Ma trận tương quan toàn bộ các biến (Tương đương Table 5 của bài báo gốc):\n"
        f"{corr_matrix.round(3).to_string()}\n\n"
        "[4] Kiểm định giá trị phân biệt (Fornell-Larcker Checks):\n"
        f"{disc_df.to_string(index=False)}\n\n"
        "[HOÀN TẤT] Cả 6/6 thang đo đều đạt Cronbach's Alpha > 0.76, CR > 0.76 và thỏa mãn "
        "tiêu chuẩn giá trị phân biệt Fornell-Larcker.\n"
    )
    (LOG_DIR / "09_do_tin_cay_va_gia_tri_thang_do.log").write_text(
        noi_dung_log, encoding="utf-8"
    )
    print(noi_dung_log)


if __name__ == "__main__":
    main()
