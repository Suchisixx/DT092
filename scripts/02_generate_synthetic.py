"""
================================================================================
TÊN FILE: scripts/02_generate_synthetic.py
MỤC TIÊU:
  - Sinh bộ dữ liệu khảo sát tổng hợp (Synthetic Data, N = 1.017 dòng, 27 cột)
    theo cấu trúc mô hình Văn hóa An toàn thông tin (ISCB) của Petrič & Just (2025).
  - Cố định seed (`20261016`) để đảm bảo tái lập chính xác 100% cùng mã băm SHA-256.
QUY TRÌNH THỰC HIỆN (TỪNG BƯỚC):
  - Bước 1: Đọc thông số cấu hình từ `config/model_config.yml` (cỡ mẫu N=1.017, seed,
            ngưỡng Likert, hệ số tải nhân tố và hệ số đường dẫn cấu trúc).
  - Bước 2: Sinh 4 biến tiềm ẩn ngoại sinh (`NORM`, `AWARE`, `KNOW`, `COMM`) từ
            phân phối chuẩn đa biến với ma trận tương quan xác định dương.
  - Bước 3: Tính 2 biến tiềm ẩn trung gian (`ATT`, `RESP`), biến nhị phân `TOOL`
            và biến kết quả tiềm ẩn `REPORT` (có thành phần `COMMxTOOL`).
  - Bước 4: Rời rạc hóa (cắt ngưỡng) thành 24 câu hỏi Likert 1–5 (`NORM1..4` đến
            `RESP1..4`) và biến hành vi `REPORT` (Likert 1–5).
  - Bước 5: Xuất CSV, bảng thống kê mô tả, bảng tần suất, manifest JSON (kèm SHA-256)
            và nhật ký thực thi tiếng Việt.
ĐẦU VÀO (INPUT):
  - Cấu hình: `config/model_config.yml`
ĐẦU RA (OUTPUT):
  - Dữ liệu mô phỏng: `data/simulated/synthetic_sem.csv`
  - Manifest & SHA-256: `artifacts/synthetic_manifest.json`
  - Thống kê mô tả & tần suất: `results/tables/synthetic_item_descriptives.csv`,
                               `results/tables/synthetic_value_frequencies.csv`
  - Nhật ký: `results/logs/02_sinh_du_lieu_mo_phong.log` & `generate_synthetic.log`
================================================================================
"""

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]


def tinh_sha256(duong_dan_file: Path) -> str:
    """Tính mã băm SHA-256 của tệp cấu hình hoặc tệp dữ liệu xuất ra."""
    bo_bam = hashlib.sha256()
    with open(duong_dan_file, "rb") as tep:
        for khoi_du_lieu in iter(lambda: tep.read(1 << 20), b""):
            bo_bam.update(khoi_du_lieu)
    return bo_bam.hexdigest()


def main():
    # Bước 1: Đọc tệp cấu hình YAML và khởi tạo bộ sinh số ngẫu nhiên cố định seed
    bo_phan_tich = argparse.ArgumentParser(
        description="Sinh dữ liệu tổng hợp phục vụ thực nghiệm CFA/SEM"
    )
    bo_phan_tich.add_argument(
        "--config",
        default="config/model_config.yml",
        help="Đường dẫn tệp cấu hình YAML",
    )
    tham_so = bo_phan_tich.parse_args()

    duong_dan_cfg = Path(tham_so.config)
    if not duong_dan_cfg.is_absolute():
        duong_dan_cfg = ROOT / duong_dan_cfg

    cau_hinh = yaml.safe_load(duong_dan_cfg.read_text(encoding="utf-8"))
    thong_tin_du_an = cau_hinh["project"]
    co_mau_n = int(thong_tin_du_an["n"])
    hat_giong_seed = int(thong_tin_du_an["seed"])
    rng = np.random.default_rng(hat_giong_seed)

    duong_dan_xuat = Path(thong_tin_du_an["output_csv"])
    if not duong_dan_xuat.is_absolute():
        duong_dan_xuat = ROOT / duong_dan_xuat
    duong_dan_xuat.parent.mkdir(parents=True, exist_ok=True)

    (ROOT / "results" / "logs").mkdir(parents=True, exist_ok=True)
    (ROOT / "results" / "tables").mkdir(parents=True, exist_ok=True)
    (ROOT / "artifacts").mkdir(exist_ok=True)

    # Bước 2: Sinh 4 biến tiềm ẩn ngoại sinh (NORM, AWARE, KNOW, COMM)
    ten_bien_ngoai_sinh = ["NORM", "AWARE", "KNOW", "COMM"]
    ma_tran_tuong_quan = np.array([
        [1.00, 0.30, 0.25, 0.20],
        [0.30, 1.00, 0.35, 0.25],
        [0.25, 0.35, 1.00, 0.30],
        [0.20, 0.25, 0.30, 1.00],
    ])
    if np.linalg.eigvalsh(ma_tran_tuong_quan).min() <= 0:
        raise ValueError("Ma trận tương quan ngoại sinh không xác định dương!")

    mau_ngoai_sinh = rng.multivariate_normal(
        np.zeros(4), ma_tran_tuong_quan, size=co_mau_n
    )
    bien_tiem_an = {
        ten: mau_ngoai_sinh[:, chi_so]
        for chi_so, ten in enumerate(ten_bien_ngoai_sinh)
    }

    # Bước 3: Hàm tạo biến tiềm ẩn nội sinh chuẩn hóa (ATT, RESP, REPORT)
    def tao_bien_tiem_an_noi_sinh(he_so_beta: dict) -> np.ndarray:
        tin_hieu = sum(float(b) * bien_tiem_an[k] for k, b in he_so_beta.items())
        phuong_sai_nhieu = max(0.15, 1.0 - min(float(np.var(tin_hieu)), 0.85))
        gia_tri = tin_hieu + rng.normal(0.0, np.sqrt(phuong_sai_nhieu), co_mau_n)
        do_lech_chuan = gia_tri.std() or 1.0
        return (gia_tri - gia_tri.mean()) / do_lech_chuan

    cau_truc = cau_hinh["structural"]
    bien_tiem_an["ATT"] = tao_bien_tiem_an_noi_sinh(cau_truc["ATT"]["predictors"])
    bien_tiem_an["RESP"] = tao_bien_tiem_an_noi_sinh(cau_truc["RESP"]["predictors"])

    xac_suat_tool = float(cau_truc.get("tool_probability", 0.65))
    cong_cu_tool = rng.binomial(1, xac_suat_tool, co_mau_n)
    bien_tiem_an["TOOL"] = cong_cu_tool.astype(float)
    bien_tiem_an["COMMxTOOL"] = (
        (bien_tiem_an["COMM"] - bien_tiem_an["COMM"].mean())
        * (cong_cu_tool - cong_cu_tool.mean())
    )
    bien_tiem_an["REPORT"] = tao_bien_tiem_an_noi_sinh(
        cau_truc["REPORT"]["predictors"]
    )

    # Bước 4: Rời rạc hóa thành các chỉ báo quan sát thang đo Likert 1–5
    bang_du_lieu = pd.DataFrame({
        "respondent_id": [f"SYN{i:04d}" for i in range(1, co_mau_n + 1)]
    })
    nguong_cat = np.array(cau_hinh["ordinal"]["thresholds"], dtype=float)
    muc_thap_nhat = int(cau_hinh["ordinal"]["likert_min"])
    muc_cao_nhat = int(cau_hinh["ordinal"]["likert_max"])

    for ten_nhan_to, thong_so in cau_hinh["measurement"].items():
        he_so_tai = float(thong_so["loading"])
        so_cau_hoi = int(thong_so["items"])
        for chi_so_cau in range(1, so_cau_hoi + 1):
            do_lech_nhieu_item = np.sqrt(max(0.01, 1.0 - he_so_tai ** 2))
            gia_tri_lien_tuc = (
                he_so_tai * bien_tiem_an[ten_nhan_to]
                + rng.normal(0.0, do_lech_nhieu_item, co_mau_n)
            )
            diem_likert = np.clip(
                np.digitize(gia_tri_lien_tuc, nguong_cat) + muc_thap_nhat,
                muc_thap_nhat,
                muc_cao_nhat,
            ).astype(int)
            bang_du_lieu[f"{ten_nhan_to}{chi_so_cau}"] = diem_likert

    bang_du_lieu["TOOL"] = cong_cu_tool.astype(int)
    bang_du_lieu["REPORT"] = np.clip(
        np.digitize(
            bien_tiem_an["REPORT"] + rng.normal(0.0, 0.45, co_mau_n),
            nguong_cat,
        ) + muc_thap_nhat,
        muc_thap_nhat,
        muc_cao_nhat,
    ).astype(int)

    # Bước 5: Lưu dữ liệu CSV, thống kê mô tả, tần suất và manifest
    bang_du_lieu.to_csv(duong_dan_xuat, index=False, encoding="utf-8")

    thong_ke_mo_ta = bang_du_lieu.drop(columns=["respondent_id"]).describe().T
    thong_ke_mo_ta["missing_n"] = bang_du_lieu.isna().sum()
    thong_ke_mo_ta.to_csv(
        ROOT / "results" / "tables" / "synthetic_item_descriptives.csv",
        encoding="utf-8",
    )

    bang_tan_suat = []
    for ten_cot in bang_du_lieu.columns[1:]:
        dem_gia_tri = bang_du_lieu[ten_cot].value_counts().sort_index()
        for gia_tri, so_luong in dem_gia_tri.items():
            bang_tan_suat.append({
                "variable": ten_cot,
                "value": gia_tri,
                "count": int(so_luong),
                "proportion": so_luong / co_mau_n,
            })
    pd.DataFrame(bang_tan_suat).to_csv(
        ROOT / "results" / "tables" / "synthetic_value_frequencies.csv",
        index=False,
    )

    manifest = {
        "dataset_name": duong_dan_xuat.name,
        "dataset_type": "SYNTHETIC_SIMULATED_NOT_REAL_RESPONDENTS",
        "n_rows": len(bang_du_lieu),
        "n_columns": len(bang_du_lieu.columns),
        "source": "scripts/02_generate_synthetic.py",
        "source_url": None,
        "license": "Project-generated synthetic data",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "seed": hat_giong_seed,
        "simulation_version": thong_tin_du_an["simulation_version"],
        "config_sha256": tinh_sha256(duong_dan_cfg),
        "output_sha256": tinh_sha256(duong_dan_xuat),
        "python_version": sys.version,
        "platform": platform.platform(),
        "missing_cells": int(bang_du_lieu.isna().sum().sum()),
        "notes": "Dữ liệu giả lập theo tham số cấu hình; không phải phản hồi của người thật.",
    }
    (ROOT / "artifacts" / "synthetic_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    noi_dung_log = (
        "===== BƯỚC 02: SINH DỮ LIỆU MÔ PHỎNG (SYNTHETIC DATA) =====\n"
        f"- Tệp dữ liệu xuất ra: {duong_dan_xuat}\n"
        f"- Kích thước: N = {len(bang_du_lieu)} dòng, {len(bang_du_lieu.columns)} cột\n"
        f"- Hạt giống ngẫu nhiên (Seed): {hat_giong_seed}\n"
        f"- Mã băm SHA-256: {manifest['output_sha256']}\n"
        "- Ghi chú: Đây là dữ liệu tổng hợp phục vụ kiểm thử pipeline CFA/SEM.\n"
    )
    (ROOT / "results" / "logs" / "02_sinh_du_lieu_mo_phong.log").write_text(
        noi_dung_log, encoding="utf-8"
    )
    print(noi_dung_log)


if __name__ == "__main__":
    main()
