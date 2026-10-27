"""
================================================================================
TÊN FILE: scripts/00_run_all_pipeline.py
MỤC TIÊU:
  - Chạy tự động toàn bộ 11 bước thực nghiệm của đề tài DT092 theo đúng trình tự
    chuẩn từ kiểm kê dữ liệu, sinh dữ liệu mô phỏng, kiểm tra chất lượng, CFA/SEM,
    kiểm định tương tác H7b, độ nhạy OLS-HC3, độ tin cậy/giá trị thang đo,
    độ ổn định 5 seeds + 5-Fold CV đến kiểm thử lỗi và đo chi phí tính toán.
QUY TRÌNH THỰC HIỆN:
  - Thực thi tuần tự từ `01_inspect_public_data.py` đến `11_negative_tests_and_benchmark.py`
    và tổng hợp bảng trạng thái toàn bộ pipeline.
================================================================================
"""

from pathlib import Path
import os
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]

DANH_SACH_BUOC = [
    ("Bước 01: Kiểm kê dữ liệu khảo sát công khai", "scripts/01_inspect_public_data.py"),
    ("Bước 02: Sinh dữ liệu mô phỏng (N=1017, seed=20261016)", "scripts/02_generate_synthetic.py"),
    ("Bước 03: Kiểm tra chất lượng dữ liệu (7 tiêu chí kỹ thuật)", "scripts/03_validate_data.py"),
    ("Bước 04: Ước lượng CFA và Mô hình SEM Cơ sở (Baseline)", "scripts/04_run_baseline_sem.py"),
    ("Bước 05: Ước lượng SEM Mở rộng có tương tác COMM x TOOL (H7b)", "scripts/05_run_interaction_sem.py"),
    ("Bước 06: Đối chiếu hệ số giữa SEM Baseline và SEM Interaction", "scripts/06_compare_models.py"),
    ("Bước 07: Phân tích độ nhạy bằng hồi quy OLS với sai số chuẩn vững HC3", "scripts/07_sensitivity_hc3.py"),
    ("Bước 09: Tính Độ tin cậy (Alpha, CR) và Giá trị (AVE, Fornell-Larcker)", "scripts/09_reliability_validity.py"),
    ("Bước 10: Chạy lặp 5 Seeds, Ablation 3 mô hình & 5-Fold CV chống rò rỉ", "scripts/10_repeated_runs_and_cv.py"),
    ("Bước 11: Chạy 8 Negative Tests & Benchmark chi phí tính toán", "scripts/11_negative_tests_and_benchmark.py"),
]


def main():
    print("=" * 80)
    print("BẮT ĐẦU CHẠY TOÀN BỘ PIPELINE THỰC NGHIỆM ĐỀ TÀI DT092 (BƯỚC 01 -> BƯỚC 11)")
    print("=" * 80)
    t_bat_dau = time.perf_counter()

    for ten_buoc, duong_dan_script in DANH_SACH_BUOC:
        print(f"\n>>> Đang thực thi {ten_buoc} ({duong_dan_script})...")
        t0 = time.perf_counter()
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        ket_qua = subprocess.run(
            [sys.executable, str(ROOT / duong_dan_script)],
            cwd=str(ROOT),
            env=env,
            check=True,
        )
        thoi_gian_s = time.perf_counter() - t0
        print(f"    [ĐẠT] Hoàn thành {ten_buoc} trong {thoi_gian_s:.2f} giây (Exit code = {ket_qua.returncode}).")

    tong_thoi_gian = time.perf_counter() - t_bat_dau
    print("\n" + "=" * 80)
    print(f"HOÀN TẤT TOÀN BỘ 11/11 BƯỚC PIPELINE TRONG {tong_thoi_gian:.2f} GIÂY!")
    print("=" * 80)


if __name__ == "__main__":
    main()
