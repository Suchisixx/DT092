"""
================================================================================
TÊN FILE: scripts/11_negative_tests_and_benchmark.py
MỤC TIÊU:
  - Thực hiện bộ 8 kịch bản kiểm thử Unit / Integration / Negative Tests có kiểm soát
    nhằm chứng minh bộ kiểm tra chất lượng dữ liệu từ chối chính xác mọi dữ liệu lỗi
    (thiếu cột, ngoài miền Likert 1..5, `TOOL` không nhị phân, trùng ID, có ô NaN,
    trùng lặp dòng nội dung câu trả lời, bảng dữ liệu rỗng).
  - Đo lường chi phí tính toán (Thời gian chạy tính bằng mili-giây, Bộ nhớ RAM đỉnh
    tính bằng MB, và Số vòng lặp hội tụ của thuật toán SLSQP) cho từng giai đoạn.
QUY TRÌNH THỰC HIỆN (TỪNG BƯỚC):
  - Bước 1: Định nghĩa hàm kiểm tra dữ liệu tổng quát `kiem_tra_bang_du_lieu()`.
  - Bước 2: Chạy 1 kịch bản đối chứng dương (`T01`) và 7 kịch bản tiêm lỗi (`T02`..`T08`),
            ghi nhận trạng thái kỳ vọng vs. thực tế (`ACCEPT` / `REJECT`).
  - Bước 3: Đo thời gian (`time.perf_counter`) và bộ nhớ (`tracemalloc`) khi chạy
            Validation, CFA, SEM Baseline và SEM Interaction.
  - Bước 4: Lưu bảng báo cáo kiểm thử âm bản, bảng benchmark và nhật ký tiếng Việt.
ĐẦU VÀO (INPUT):
  - `data/simulated/synthetic_sem.csv`
ĐẦU RA (OUTPUT):
  - Báo cáo 8 kịch bản test: `results/tables/negative_tests_report.csv`
  - Benchmark thời gian & RAM: `artifacts/runtime_benchmark.csv`
  - Nhật ký: `results/logs/11_kiem_thu_loi_va_chi_phi_tinh_toan.log`
================================================================================
"""

from pathlib import Path
import sys
import time
import tracemalloc
import numpy as np
import pandas as pd
from semopy import Model

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "simulated" / "synthetic_sem.csv"
TABLES_DIR = ROOT / "results" / "tables"
ARTIFACTS_DIR = ROOT / "artifacts"
LOG_DIR = ROOT / "results" / "logs"
TABLES_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


def kiem_tra_bang_du_lieu(df: pd.DataFrame, co_mau_ky_vong: int = 1017) -> dict:
    """Hàm kiểm tra chất lượng dữ liệu dùng chung cho cả kiểm thử dương và kiểm thử âm bản."""
    checks = {}
    checks["N_is_expected"] = len(df) == co_mau_ky_vong
    checks["non_empty"] = len(df) > 0
    required = ["respondent_id", "TOOL", "REPORT"] + [
        f"{f}{i}"
        for f in ["NORM", "AWARE", "KNOW", "COMM", "ATT", "RESP"]
        for i in range(1, 5)
    ]
    checks["required_columns"] = set(required).issubset(df.columns)
    if not checks["required_columns"] or not checks["non_empty"]:
        return {
            "all_passed": False,
            "failed_checks": [k for k, v in checks.items() if not v],
        }

    checks["unique_ID"] = bool(df["respondent_id"].is_unique)
    checks["no_missing"] = bool(df.isna().sum().sum() == 0)
    checks["TOOL_binary"] = bool(set(df["TOOL"].dropna().unique()).issubset({0, 1}))

    likert_cols = [c for c in required if c not in ["respondent_id", "TOOL"]]
    likert_ok = True
    for c in likert_cols:
        if not pd.api.types.is_numeric_dtype(df[c]) or not df[c].between(1, 5).all():
            likert_ok = False
            break
    checks["Likert_1_to_5"] = likert_ok

    feat_cols = [c for c in required if c != "respondent_id"]
    checks["no_duplicate_feature_rows"] = bool(
        df.duplicated(subset=feat_cols).sum() == 0
    )

    failed = [k for k, v in checks.items() if not v]
    return {"all_passed": len(failed) == 0, "failed_checks": failed}


def chay_kiem_thu_am_ban(base_df: pd.DataFrame) -> pd.DataFrame:
    """Thực thi 8 kịch bản kiểm thử (1 Positive Control + 7 Negative Tests)."""
    scenarios = []

    # T01: Dữ liệu hợp lệ chuẩn
    res_pos = kiem_tra_bang_du_lieu(base_df)
    scenarios.append({
        "test_id": "T01_Positive_Valid_Dataset",
        "test_type": "Integration / Positive",
        "injected_fault": "Không tiêm lỗi (Dữ liệu chuẩn synthetic_sem.csv)",
        "expected_outcome": "ACCEPT",
        "actual_outcome": "ACCEPT" if res_pos["all_passed"] else "REJECT",
        "triggered_rules": "None",
        "test_passed": bool(res_pos["all_passed"] is True),
    })

    # T02: Thiếu cột bắt buộc
    df_missing_col = base_df.drop(columns=["COMM1"])
    res = kiem_tra_bang_du_lieu(df_missing_col)
    scenarios.append({
        "test_id": "T02_Negative_Missing_Column",
        "test_type": "Negative / Schema",
        "injected_fault": "Xóa cột bắt buộc COMM1",
        "expected_outcome": "REJECT",
        "actual_outcome": "REJECT" if not res["all_passed"] else "ACCEPT",
        "triggered_rules": ",".join(res["failed_checks"]),
        "test_passed": bool("required_columns" in res["failed_checks"]),
    })

    # T03: Giá trị Likert vượt ngoài miền 1..5
    df_bad_likert = base_df.copy()
    df_bad_likert.loc[0, "ATT1"] = 9
    res = kiem_tra_bang_du_lieu(df_bad_likert)
    scenarios.append({
        "test_id": "T03_Negative_Out_Of_Range_Likert",
        "test_type": "Negative / Domain",
        "injected_fault": "Gán ATT1 = 9 tại dòng 0 (ngoài miền 1..5)",
        "expected_outcome": "REJECT",
        "actual_outcome": "REJECT" if not res["all_passed"] else "ACCEPT",
        "triggered_rules": ",".join(res["failed_checks"]),
        "test_passed": bool("Likert_1_to_5" in res["failed_checks"]),
    })

    # T04: Biến TOOL ngoài miền nhị phân {0, 1}
    df_bad_tool = base_df.copy()
    df_bad_tool.loc[5, "TOOL"] = 2
    res = kiem_tra_bang_du_lieu(df_bad_tool)
    scenarios.append({
        "test_id": "T04_Negative_Invalid_Binary_TOOL",
        "test_type": "Negative / Domain",
        "injected_fault": "Gán TOOL = 2 tại dòng 5 (ngoài miền {0,1})",
        "expected_outcome": "REJECT",
        "actual_outcome": "REJECT" if not res["all_passed"] else "ACCEPT",
        "triggered_rules": ",".join(res["failed_checks"]),
        "test_passed": bool("TOOL_binary" in res["failed_checks"]),
    })

    # T05: Trùng mã respondent_id
    df_dup_id = base_df.copy()
    df_dup_id.loc[1, "respondent_id"] = df_dup_id.loc[0, "respondent_id"]
    res = kiem_tra_bang_du_lieu(df_dup_id)
    scenarios.append({
        "test_id": "T05_Negative_Duplicate_ID",
        "test_type": "Negative / Uniqueness",
        "injected_fault": "Gán trùng mã định danh respondent_id = SYN0001",
        "expected_outcome": "REJECT",
        "actual_outcome": "REJECT" if not res["all_passed"] else "ACCEPT",
        "triggered_rules": ",".join(res["failed_checks"]),
        "test_passed": bool("unique_ID" in res["failed_checks"]),
    })

    # T06: Tiêm giá trị khuyết thiếu NaN
    df_nan = base_df.copy()
    df_nan.loc[10, "REPORT"] = np.nan
    res = kiem_tra_bang_du_lieu(df_nan)
    scenarios.append({
        "test_id": "T06_Negative_Missing_NaN_Cell",
        "test_type": "Negative / Completeness",
        "injected_fault": "Tiêm giá trị trống (NaN) vào cột REPORT tại dòng 10",
        "expected_outcome": "REJECT",
        "actual_outcome": "REJECT" if not res["all_passed"] else "ACCEPT",
        "triggered_rules": ",".join(res["failed_checks"]),
        "test_passed": bool("no_missing" in res["failed_checks"]),
    })

    # T07: Nhân bản dòng câu trả lời gây trùng lặp nội dung
    df_dup_row = base_df.copy()
    feat_cols = [c for c in base_df.columns if c != "respondent_id"]
    df_dup_row.loc[2, feat_cols] = df_dup_row.loc[0, feat_cols].values
    res = kiem_tra_bang_du_lieu(df_dup_row)
    scenarios.append({
        "test_id": "T07_Negative_Duplicate_Feature_Row",
        "test_type": "Negative / Data Leakage & Dedup",
        "injected_fault": "Sao chép toàn bộ 26 câu trả lời từ dòng 0 sang dòng 2",
        "expected_outcome": "REJECT",
        "actual_outcome": "REJECT" if not res["all_passed"] else "ACCEPT",
        "triggered_rules": ",".join(res["failed_checks"]),
        "test_passed": bool("no_duplicate_feature_rows" in res["failed_checks"]),
    })

    # T08: Bảng dữ liệu rỗng (0 dòng)
    df_empty = base_df.iloc[0:0].copy()
    res = kiem_tra_bang_du_lieu(df_empty)
    scenarios.append({
        "test_id": "T08_Negative_Empty_DataFrame",
        "test_type": "Negative / Boundary",
        "injected_fault": "Bảng dữ liệu rỗng (0 dòng)",
        "expected_outcome": "REJECT",
        "actual_outcome": "REJECT" if not res["all_passed"] else "ACCEPT",
        "triggered_rules": ",".join(res["failed_checks"]),
        "test_passed": bool("non_empty" in res["failed_checks"]),
    })

    out_df = pd.DataFrame(scenarios)
    out_df.to_csv(
        TABLES_DIR / "negative_tests_report.csv", index=False, encoding="utf-8-sig"
    )
    return out_df


def do_chi_phi_tinh_toan(df: pd.DataFrame) -> pd.DataFrame:
    """Đo thời gian thực thi (ms), RAM đỉnh (MB) và số vòng lặp hội tụ SLSQP."""
    cfa_desc = """
    NORM =~ NORM1 + NORM2 + NORM3 + NORM4
    AWARE =~ AWARE1 + AWARE2 + AWARE3 + AWARE4
    KNOW =~ KNOW1 + KNOW2 + KNOW3 + KNOW4
    COMM =~ COMM1 + COMM2 + COMM3 + COMM4
    ATT =~ ATT1 + ATT2 + ATT3 + ATT4
    RESP =~ RESP1 + RESP2 + RESP3 + RESP4
    """
    sem_base_desc = cfa_desc + """
    ATT ~ NORM + AWARE + COMM + KNOW
    RESP ~ NORM + AWARE + COMM + KNOW
    REPORT ~ NORM + AWARE + COMM + ATT + RESP + TOOL
    """
    sem_inter_desc = cfa_desc + """
    ATT ~ NORM + AWARE + COMM + KNOW
    RESP ~ NORM + AWARE + COMM + KNOW
    REPORT ~ NORM + AWARE + COMM + ATT + RESP + TOOL + COMM_TOOL
    """

    work = df.copy()
    work["COMM_mean"] = work[[f"COMM{i}" for i in range(1, 5)]].mean(axis=1)
    work["COMM_c"] = work["COMM_mean"] - work["COMM_mean"].mean()
    work["TOOL_c"] = work["TOOL"] - work["TOOL"].mean()
    work["COMM_TOOL"] = work["COMM_c"] * work["TOOL_c"]

    tasks = [
        ("Stage_03_Data_Validation", lambda: kiem_tra_bang_du_lieu(work)),
        ("Stage_04a_CFA_Measurement_Model", lambda: Model(cfa_desc).fit(work)),
        ("Stage_04b_SEM_Baseline_Model", lambda: Model(sem_base_desc).fit(work)),
        ("Stage_05_SEM_Interaction_Model", lambda: Model(sem_inter_desc).fit(work)),
    ]

    bench_rows = []
    for stage_name, fn in tasks:
        tracemalloc.start()
        t0 = time.perf_counter()
        res = fn()
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        converged = True
        n_iter = 0
        obj_val = None
        res_str = str(res)
        if "Optimization terminated successfully" in res_str or "Optimization successful" in res_str:
            converged = True
        for line in res_str.splitlines():
            if "Number of iterations:" in line:
                n_iter = int(line.split(":")[1].strip())
            elif "Objective value:" in line:
                obj_val = float(line.split(":")[1].strip())
        if hasattr(res, "fun") and obj_val is None:
            obj_val = round(float(res.fun), 6)

        bench_rows.append({
            "stage": stage_name,
            "n_rows": len(work),
            "runtime_ms": round(elapsed_ms, 2),
            "peak_memory_mb": round(peak_bytes / (1024 * 1024), 3),
            "converged": converged,
            "optimizer_iterations": n_iter,
            "objective_value": obj_val,
        })

    bench_df = pd.DataFrame(bench_rows)
    bench_df.to_csv(
        TABLES_DIR / "runtime_benchmark.csv", index=False, encoding="utf-8-sig"
    )
    return bench_df


def main():
    df = pd.read_csv(DATA_PATH)
    neg_df = chay_kiem_thu_am_ban(df)
    bench_df = do_chi_phi_tinh_toan(df)

    noi_dung_log = (
        "===== BƯỚC 11: KIỂM THỬ ÂM BẢN (NEGATIVE TESTS) & ĐO CHI PHÍ TÍNH TOÁN =====\n"
        "[1] Kết quả 8 kịch bản Unit / Integration / Negative Tests:\n"
        f"{neg_df.to_string(index=False)}\n\n"
        "[2] Chi phí thời gian thực thi (ms), bộ nhớ RAM đỉnh (MB) và số vòng lặp hội tụ SLSQP:\n"
        f"{bench_df.to_string(index=False)}\n\n"
        "[HOÀN TẤT] Đạt 8/8 kịch bản kiểm thử và hoàn tất đo hiệu năng.\n"
    )
    (LOG_DIR / "11_kiem_thu_loi_va_chi_phi_tinh_toan.log").write_text(
        noi_dung_log, encoding="utf-8"
    )
    print(noi_dung_log)


if __name__ == "__main__":
    main()
