"""
================================================================================
TÊN FILE: scripts/01_inspect_public_data.py
MỤC TIÊU:
  - Kiểm kê các tệp dữ liệu khảo sát công khai (ứng viên tham khảo) được lưu trong
    thư mục `data/raw/public/`.
  - Tính mã băm SHA-256, kích thước tệp, số dòng, số cột, kiểu dữ liệu và tỷ lệ
    khuyết thiếu (missing rate) mà không tự ý gán ghép hay trộn lẫn vào dữ liệu SEM.
QUY TRÌNH THỰC HIỆN (TỪNG BƯỚC):
  - Bước 1: Đọc tham số đường dẫn thư mục chứa dữ liệu công khai (`--input`).
  - Bước 2: Duyệt qua từng tệp `.csv`, `.xlsx`, `.xlsm` trong thư mục, tính SHA-256.
  - Bước 3: Thống kê số dòng, danh sách cột, kiểu dữ liệu và tỷ lệ ô trống.
  - Bước 4: Xuất bảng kiểm kê ra `results/tables/public_data_inventory.csv` và
            lưu nhật ký tiếng Việt tại `results/logs/01_kiem_ke_du_lieu_cong_khai.log`.
ĐẦU VÀO (INPUT):
  - Thư mục: `data/raw/public/` (gồm `Generated_Survey_Responses.csv`, `Questions.docx`)
ĐẦU RA (OUTPUT):
  - Bảng kiểm kê: `results/tables/public_data_inventory.csv`
  - Nhật ký: `results/logs/01_kiem_ke_du_lieu_cong_khai.log`
================================================================================
"""

import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path
import sys
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Xác định thư mục gốc của dự án
ROOT = Path(__file__).resolve().parents[1]


def tinh_sha256(duong_dan_file: Path) -> str:
    """Tính mã băm SHA-256 của một tệp để đảm bảo tính toàn vẹn dữ liệu."""
    bo_bam = hashlib.sha256()
    with open(duong_dan_file, "rb") as tep:
        for khoi_du_lieu in iter(lambda: tep.read(1 << 20), b""):
            bo_bam.update(khoi_du_lieu)
    return bo_bam.hexdigest()


def main():
    # Bước 1: Nhận tham số dòng lệnh
    bo_phan_tich = argparse.ArgumentParser(
        description="Kiểm kê dữ liệu khảo sát công khai trong data/raw/public"
    )
    bo_phan_tich.add_argument(
        "--input",
        default="data/raw/public",
        help="Đường dẫn thư mục chứa dữ liệu công khai cần kiểm kê",
    )
    tham_so = bo_phan_tich.parse_args()

    thu_muc_dau_vao = Path(tham_so.input)
    if not thu_muc_dau_vao.is_absolute():
        thu_muc_dau_vao = ROOT / thu_muc_dau_vao

    if not thu_muc_dau_vao.exists():
        raise SystemExit(f"[LỖI] Không tìm thấy thư mục: {thu_muc_dau_vao}")

    # Bước 2 & 3: Duyệt từng tệp và trích xuất thông tin metadata + cấu trúc cột
    danh_sach_ket_qua = []
    for duong_dan in sorted(thu_muc_dau_vao.rglob("*")):
        # Bỏ qua thư mục, tệp tạm của Office (~$) hoặc tệp ẩn (.gitkeep)
        if not duong_dan.is_file() or duong_dan.name.startswith("~$") or duong_dan.name.startswith("."):
            continue

        thong_tin_chung = {
            "file": str(duong_dan),
            "bytes": duong_dan.stat().st_size,
            "sha256": tinh_sha256(duong_dan),
            "inspected_utc": datetime.now(timezone.utc).isoformat(),
        }

        try:
            duoi_tep = duong_dan.suffix.lower()
            if duoi_tep == ".csv":
                bang_du_lieu = pd.read_csv(duong_dan, nrows=100000, low_memory=False)
                danh_sach_ket_qua.append({
                    **thong_tin_chung,
                    "sheet": "",
                    "rows_inspected": len(bang_du_lieu),
                    "columns_n": len(bang_du_lieu.columns),
                    "columns": " | ".join(map(str, bang_du_lieu.columns)),
                    "dtypes": str(bang_du_lieu.dtypes.to_dict()),
                    "missing_rate": float(bang_du_lieu.isna().mean().mean()),
                })
            elif duoi_tep in [".xlsx", ".xlsm"]:
                tep_excel = pd.ExcelFile(duong_dan)
                for ten_sheet in tep_excel.sheet_names:
                    bang_du_lieu = pd.read_excel(duong_dan, sheet_name=ten_sheet, nrows=100000)
                    danh_sach_ket_qua.append({
                        **thong_tin_chung,
                        "sheet": ten_sheet,
                        "rows_inspected": len(bang_du_lieu),
                        "columns_n": len(bang_du_lieu.columns),
                        "columns": " | ".join(map(str, bang_du_lieu.columns)),
                        "dtypes": str(bang_du_lieu.dtypes.to_dict()),
                        "missing_rate": float(bang_du_lieu.isna().mean().mean()),
                    })
        except Exception as loi:
            danh_sach_ket_qua.append({
                **thong_tin_chung,
                "error": repr(loi),
            })

    # Bước 4: Lưu bảng kiểm kê và ghi nhật ký tiếng Việt
    tep_xuat = ROOT / "results" / "tables" / "public_data_inventory.csv"
    tep_xuat.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(danh_sach_ket_qua).to_csv(tep_xuat, index=False, encoding="utf-8-sig")

    thu_muc_log = ROOT / "results" / "logs"
    thu_muc_log.mkdir(parents=True, exist_ok=True)
    noi_dung_log = (
        "===== BƯỚC 01: KIỂM KÊ DỮ LIỆU CÔNG KHAI =====\n"
        f"- Thư mục kiểm tra: {thu_muc_dau_vao}\n"
        f"- Số bảng/sheet dữ liệu đã kiểm kê: {len(danh_sach_ket_qua)}\n"
        f"- Đã lưu bảng kiểm kê tại: {tep_xuat}\n"
        "- Lưu ý học thuật: Dữ liệu công khai chỉ dùng để đối chiếu cấu trúc câu hỏi, "
        "không tự động ghép nối vào dữ liệu mô phỏng SEM để tránh sai lệch thang đo.\n"
    )
    (thu_muc_log / "01_kiem_ke_du_lieu_cong_khai.log").write_text(
        noi_dung_log, encoding="utf-8"
    )
    print(noi_dung_log)


if __name__ == "__main__":
    main()
