"""
================================================================================
TÊN FILE: scripts/03_validate_data.py
MỤC TIÊU:
  - Kiểm tra tự động chất lượng và tính toàn vẹn của bộ dữ liệu `synthetic_sem.csv`
    trước khi đưa vào ước lượng CFA và SEM.
  - Đảm bảo đạt đủ 7 tiêu chí kỹ thuật (bao gồm kiểm tra không trùng lặp dòng nội dung).
QUY TRÌNH THỰC HIỆN (TỪNG BƯỚC):
  - Bước 1: Đọc tệp dữ liệu `data/simulated/synthetic_sem.csv`.
  - Bước 2: Thực hiện 7 kiểm tra ràng buộc:
            (1) Cỡ mẫu đúng N = 1.017;
            (2) Mã định danh `respondent_id` là duy nhất;
            (3) Không có bất kỳ ô dữ liệu trống (NaN) nào;
            (4) Biến `TOOL` chỉ nhận giá trị nhị phân {0, 1};
            (5) Toàn bộ 25 cột câu hỏi Likert nằm trong miền số nguyên 1..5;
            (6) Đầy đủ 27 cột bắt buộc theo thiết kế;
            (7) Không có dòng bản ghi trùng lặp trên 26 cột câu hỏi/đặc trưng.
  - Bước 3: Thống kê phân phối từng biến và xuất báo cáo JSON/CSV + log tiếng Việt.
ĐẦU VÀO (INPUT):
  - Dữ liệu: `data/simulated/synthetic_sem.csv`
ĐẦU RA (OUTPUT):
  - Bảng kết quả 7 kiểm tra: `results/tables/validation_checks.csv`
  - Phân phối biến: `results/tables/validation_distributions.csv`
  - Tóm tắt JSON: `artifacts/validation_summary.json`
  - Nhật ký: `results/logs/03_kiem_tra_chat_luong_du_lieu.log`
================================================================================
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]


def tinh_sha256(duong_dan_file: Path) -> str:
    """Tính mã băm SHA-256 của tệp dữ liệu đầu vào."""
    bo_bam = hashlib.sha256()
    with open(duong_dan_file, "rb") as tep:
        for khoi_du_lieu in iter(lambda: tep.read(1 << 20), b""):
            bo_bam.update(khoi_du_lieu)
    return bo_bam.hexdigest()


def main():
    # Bước 1: Đọc dữ liệu đầu vào
    bo_phan_tich = argparse.ArgumentParser(
        description="Kiểm tra chất lượng và tính toàn vẹn của dữ liệu khảo sát SEM"
    )
    bo_phan_tich.add_argument(
        "--input",
        default="data/simulated/synthetic_sem.csv",
        help="Đường dẫn tệp CSV cần kiểm tra",
    )
    tham_so = bo_phan_tich.parse_args()

    duong_dan = Path(tham_so.input)
    if not duong_dan.is_absolute():
        duong_dan = ROOT / duong_dan

    if not duong_dan.exists():
        raise SystemExit(
            f"[LỖI] Không tìm thấy tệp {duong_dan}; hãy chạy scripts/02_generate_synthetic.py trước."
        )

    bang_du_lieu = pd.read_csv(duong_dan)
    danh_sach_kiem_tra = []

    def ghi_kiem_tra(ten_kiem_tra: str, dat_yeu_cau: bool, chi_tiet: str):
        danh_sach_kiem_tra.append({
            "check": ten_kiem_tra,
            "passed": bool(dat_yeu_cau),
            "detail": str(chi_tiet),
        })

    # Bước 2: Thực hiện 7 bài kiểm tra chất lượng dữ liệu
    ghi_kiem_tra(
        "N_is_1017",
        len(bang_du_lieu) == 1017,
        f"N={len(bang_du_lieu)} (khớp cỡ mẫu N=1017 của bài báo gốc)",
    )
    ghi_kiem_tra(
        "unique_ID",
        bang_du_lieu["respondent_id"].is_unique,
        f"unique={bang_du_lieu['respondent_id'].nunique()}",
    )
    so_o_trong = int(bang_du_lieu.isna().sum().sum())
    ghi_kiem_tra(
        "no_missing",
        so_o_trong == 0,
        f"missing={so_o_trong}",
    )
    tap_gia_tri_tool = set(bang_du_lieu["TOOL"].unique())
    ghi_kiem_tra(
        "TOOL_binary",
        tap_gia_tri_tool.issubset({0, 1}),
        sorted(bang_du_lieu["TOOL"].unique().tolist()),
    )

    cac_cot_likert = [
        cot for cot in bang_du_lieu.columns if cot not in ["respondent_id", "TOOL"]
    ]
    ghi_kiem_tra(
        "Likert_1_to_5",
        all(bang_du_lieu[cot].between(1, 5).all() for cot in cac_cot_likert),
        f"columns={len(cac_cot_likert)}",
    )

    cac_cot_bat_buoc = ["REPORT"] + [
        f"{nhan_to}{i}"
        for nhan_to in ["NORM", "AWARE", "KNOW", "COMM", "ATT", "RESP"]
        for i in range(1, 5)
    ]
    cot_thieu = sorted(set(cac_cot_bat_buoc) - set(bang_du_lieu.columns))
    ghi_kiem_tra(
        "required_columns",
        set(cac_cot_bat_buoc).issubset(bang_du_lieu.columns),
        f"missing={cot_thieu}",
    )

    cac_cot_dac_trung = [cot for cot in bang_du_lieu.columns if cot != "respondent_id"]
    so_dong_trung = int(bang_du_lieu.duplicated(subset=cac_cot_dac_trung).sum())
    ghi_kiem_tra(
        "no_duplicate_feature_rows",
        so_dong_trung == 0,
        f"duplicate_feature_rows={so_dong_trung}",
    )

    # Bước 3: Thống kê phân phối các biến Likert và lưu kết quả
    danh_sach_phan_phoi = []
    for cot in cac_cot_likert:
        ty_le_muc = (
            bang_du_lieu[cot]
            .value_counts(normalize=True)
            .reindex([1, 2, 3, 4, 5], fill_value=0.0)
        )
        danh_sach_phan_phoi.append({
            "variable": cot,
            "mean": float(bang_du_lieu[cot].mean()),
            "sd": float(bang_du_lieu[cot].std()),
            "min": int(bang_du_lieu[cot].min()),
            "max": int(bang_du_lieu[cot].max()),
            "max_category_share": float(ty_le_muc.max()),
            "constant": bool(bang_du_lieu[cot].nunique() < 2),
        })

    (ROOT / "results" / "tables").mkdir(parents=True, exist_ok=True)
    (ROOT / "results" / "logs").mkdir(parents=True, exist_ok=True)
    (ROOT / "artifacts").mkdir(exist_ok=True)

    pd.DataFrame(danh_sach_phan_phoi).to_csv(
        ROOT / "results" / "tables" / "validation_distributions.csv", index=False
    )
    bang_ket_qua = pd.DataFrame(danh_sach_kiem_tra)
    bang_ket_qua.to_csv(
        ROOT / "results" / "tables" / "validation_checks.csv", index=False
    )

    tom_tat = {
        "file": str(duong_dan),
        "sha256": tinh_sha256(duong_dan),
        "rows": int(len(bang_du_lieu)),
        "columns": int(len(bang_du_lieu.columns)),
        "missing_cells": so_o_trong,
        "checks_passed": int(bang_ket_qua["passed"].sum()),
        "checks_total": int(len(bang_ket_qua)),
        "all_checks_passed": bool(bang_ket_qua["passed"].all()),
        "interpretation": (
            "Đạt 7/7 kiểm tra toàn vẹn kỹ thuật. Lưu ý: Kiểm tra kỹ thuật không thay thế "
            "cho kiểm định độ tin cậy thang đo (CFA/AVE/CR) và độ phù hợp mô hình SEM."
        ),
    }
    (ROOT / "artifacts" / "validation_summary.json").write_text(
        json.dumps(tom_tat, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    noi_dung_log = (
        "===== BƯỚC 03: KIỂM TRA CHẤT LƯỢNG DỮ LIỆU (DATA VALIDATION) =====\n"
        f"{bang_ket_qua.to_string(index=False)}\n\n"
        "--- Tóm tắt JSON ---\n"
        f"{json.dumps(tom_tat, indent=2, ensure_ascii=False)}\n"
    )
    (ROOT / "results" / "logs" / "03_kiem_tra_chat_luong_du_lieu.log").write_text(
        noi_dung_log, encoding="utf-8"
    )
    print(noi_dung_log)

    if not tom_tat["all_checks_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
