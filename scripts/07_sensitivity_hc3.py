"""
================================================================================
TÊN FILE: scripts/07_sensitivity_hc3.py
MỤC TIÊU:
  - Thực hiện phân tích độ nhạy (Sensitivity Analysis) bằng phương pháp hồi quy
    Bình phương tối thiểu thông thường (OLS) với sai số chuẩn vững kháng phương sai
    thay đổi loại 3 (HC3 Robust Standard Errors) trên điểm trung bình của các thang đo.
  - Lý do thực hiện: Ở Bước 2 của bài báo gốc (Petrič & Just, 2025, trang 9),
    tác giả tính điểm trung bình cộng (`arithmetic mean`) của các câu hỏi cho từng
    thang đo rồi chạy Path Model với WLSMV. Do `semopy` dùng ước lượng MLW cho biến
    liên tục, việc chạy thêm `OLS-HC3` trên điểm trung bình giúp kiểm chứng xem
    các kết luận định tính (đặc biệt là tương tác H7b) có bị nhạy cảm với sai số
    chuẩn hay phương pháp ước lượng không.
QUY TRÌNH THỰC HIỆN (TỪNG BƯỚC):
  - Bước 1: Đọc dữ liệu `data/simulated/synthetic_sem.csv`.
  - Bước 2: Tính điểm trung bình cộng của 4 items cho từng cấu trúc (`NORM`, `AWARE`,
            `KNOW`, `COMM`, `ATT`, `RESP`).
  - Bước 3: Chuẩn hóa tâm `COMM` và `TOOL`, sau đó nhân tạo biến tương tác `COMM_TOOL`.
  - Bước 4: Ước lượng 3 phương trình OLS với `cov_type="HC3"` cho `ATT`, `RESP`, `REPORT`.
  - Bước 5: Lưu bảng hệ số, SE vững HC3, khoảng tin cậy 95%, R2 và nhật ký tiếng Việt.
ĐẦU VÀO (INPUT):
  - Dữ liệu: `data/simulated/synthetic_sem.csv`
ĐẦU RA (OUTPUT):
  - Kết quả hồi quy HC3: `artifacts/sensitivity/hc3_sensitivity_results.csv`
  - Metadata: `artifacts/sensitivity/hc3_run_info.json`
  - Nhật ký: `results/logs/07_phan_tich_do_nhay_ols_hc3.log`
================================================================================
"""

import json
from pathlib import Path
import sys
import pandas as pd
import statsmodels.api as sm

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "simulated" / "synthetic_sem.csv"
OUT_DIR = ROOT / "artifacts" / "sensitivity"
LOG_DIR = ROOT / "results" / "logs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


def main():
    # Bước 1: Đọc dữ liệu
    df = pd.read_csv(DATA_PATH)

    # Bước 2: Tính điểm trung bình số học cho 6 cấu trúc tiềm ẩn (giống Bước 2 của bài báo gốc)
    cac_cau_truc = ["NORM", "AWARE", "KNOW", "COMM", "ATT", "RESP"]
    for ten_cau_truc in cac_cau_truc:
        cac_cot = [f"{ten_cau_truc}{i}" for i in range(1, 5)]
        cot_thieu = [cot for cot in cac_cot if cot not in df.columns]
        if cot_thieu:
            raise ValueError(f"[LỖI] Thiếu cột {cot_thieu}")
        df[ten_cau_truc] = df[cac_cot].mean(axis=1)

    # Bước 3: Chuẩn hóa tâm (Mean-centering) COMM và TOOL rồi tạo tương tác COMM_TOOL
    df["COMM_c"] = df["COMM"] - df["COMM"].mean()
    df["TOOL_c"] = df["TOOL"] - df["TOOL"].mean()
    df["COMM_TOOL"] = df["COMM_c"] * df["TOOL_c"]

    # Bước 4: Định nghĩa 3 phương trình hồi quy tương ứng với mô hình nghiên cứu
    cac_phuong_trinh = {
        "ATT": ["NORM", "AWARE", "COMM", "KNOW"],
        "RESP": ["NORM", "AWARE", "COMM", "KNOW"],
        "REPORT": [
            "NORM",
            "AWARE",
            "COMM",
            "ATT",
            "RESP",
            "TOOL",
            "COMM_TOOL",
        ],
    }

    danh_sach_ket_qua = []
    nhat_ky = ["===== BƯỚC 07: PHÂN TÍCH ĐỘ NHẠY BẰNG HỒI QUY OLS VỚI SAI SỐ CHUẨN VỮNG HC3 ====="]

    for bien_phu_thuoc, danh_sach_du_bao in cac_phuong_trinh.items():
        ma_tran_x = sm.add_constant(df[danh_sach_du_bao])
        vecto_y = df[bien_phu_thuoc]

        # Ước lượng OLS với ma trận hiệp phương sai vững HC3
        mo_hinh_fit = sm.OLS(vecto_y, ma_tran_x).fit(cov_type="HC3")
        khoang_tin_cay = mo_hinh_fit.conf_int()

        for bien_du_bao in danh_sach_du_bao:
            danh_sach_ket_qua.append({
                "outcome": bien_phu_thuoc,
                "predictor": bien_du_bao,
                "coefficient": float(mo_hinh_fit.params[bien_du_bao]),
                "robust_se_HC3": float(mo_hinh_fit.bse[bien_du_bao]),
                "t_value": float(mo_hinh_fit.tvalues[bien_du_bao]),
                "p_value": float(mo_hinh_fit.pvalues[bien_du_bao]),
                "ci_lower": float(khoang_tin_cay.loc[bien_du_bao, 0]),
                "ci_upper": float(khoang_tin_cay.loc[bien_du_bao, 1]),
                "significant_005": bool(mo_hinh_fit.pvalues[bien_du_bao] < 0.05),
                "r_squared": float(mo_hinh_fit.rsquared),
                "n": int(mo_hinh_fit.nobs),
            })

        nhat_ky.append(f"\n--- Phương trình hồi quy OLS-HC3 cho biến {bien_phu_thuoc} (R2 = {mo_hinh_fit.rsquared:.4f}) ---")
        nhat_ky.append(str(mo_hinh_fit.summary()))

    # Bước 5: Lưu bảng kết quả và nhật ký tiếng Việt
    bang_ket_qua = pd.DataFrame(danh_sach_ket_qua)
    tep_xuat = OUT_DIR / "hc3_sensitivity_results.csv"
    bang_ket_qua.to_csv(tep_xuat, index=False, encoding="utf-8-sig")

    thong_tin_chay = {
        "data": str(DATA_PATH),
        "method": "OLS trên điểm trung bình thang đo với sai số chuẩn vững HC3 (statsmodels)",
        "n": int(len(df)),
        "synthetic_data": True,
        "interpretation": (
            "Phân tích độ nhạy cấp độ điểm trung bình thang đo; hệ số hồi quy chưa chuẩn hóa "
            "được dùng để kiểm tra tính nhất quán về dấu và ý nghĩa thống kê so với SEM."
        ),
    }
    with open(OUT_DIR / "hc3_run_info.json", "w", encoding="utf-8") as tep_json:
        json.dump(thong_tin_chay, tep_json, ensure_ascii=False, indent=2)

    tom_tat_log = (
        "\n=== TÓM TẮT KẾT QUẢ ĐỘ NHẠY OLS-HC3 ===\n"
        f"{bang_ket_qua.to_string(index=False)}\n"
        f"\n[HOÀN TẤT] Đã lưu kết quả OLS-HC3 tại: {tep_xuat}\n"
    )
    nhat_ky.append(tom_tat_log)
    (LOG_DIR / "07_phan_tich_do_nhay_ols_hc3.log").write_text(
        "\n".join(nhat_ky), encoding="utf-8"
    )
    print(tom_tat_log)


if __name__ == "__main__":
    main()
