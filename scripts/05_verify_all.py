"""
05_verify_all.py

Cổng Kiểm toán & Xác minh Tự động Toàn tuyến (End-to-End Verification Gate) cho thực nghiệm
SEM Đa nhóm & Tính bất biến Đo lường của dự án DT092 (Petrič & Just, 2025).

Kiểm định độc lập các hạng mục:
1. Cấu trúc thư mục dự án sạch sẽ (không còn thư mục cũ hay tệp CSV nhân bản trùng lặp;
   bảo toàn tệp tham chiếu câu hỏi khảo sát Tiếng Việt `data/Survey_Question.md`).
2. Kiểm kê đầy đủ danh mục đầu ra: bộ dữ liệu tổng hợp đa nhóm, manifest, bảng phân bổ mẫu,
   đúng 18 bảng CSV chuẩn (Bảng 1 đến Bảng 9 + `paper_comparison.csv`), tệp log và 3 báo cáo Markdown.
3. Độ chặt chẽ của dữ liệu: N = 1.017 (DE=306, UK=205, US=506), mã ID duy nhất SYN0001..SYN1017,
   0 giá trị khuyết, miền giá trị Likert [1, 5] & nhị phân {0, 1}, khớp mã băm SHA-256 với manifest.
4. Tính toàn vẹn thống kê: kiểm tra `math.isfinite` (không có NaN/Inf) trên mọi trường số,
   ràng buộc xác suất `0.0 <= p_value <= 1.0` trên mọi cột p-value, không lấy trung bình cộng
   p-value qua nhiều seed, bậc tự do df & Chi-square của Bảng 7 tăng đơn điệu chặt,
   và xác nhận hội tụ sạch trong toàn bộ nhật ký chạy mô hình.

Thoát với mã `sys.exit(0)` khi đạt 100%, hoặc `sys.exit(1)` nếu bất kỳ kiểm định nào thất bại.
"""

from __future__ import annotations

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import csv
import hashlib
import json
import logging
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DATA_DIR = REPO_ROOT / "data"
RESULTS_DIR = REPO_ROOT / "results"
TABLES_DIR = RESULTS_DIR / "tables"
LOGS_DIR = RESULTS_DIR / "logs"
REPORTS_DIR = REPO_ROOT / "reports"

# Danh sách các đường dẫn của phiên bản cũ không được phép tồn tại trong dự án mới
FORBIDDEN_LEGACY_PATHS = [
    "artifacts",
    "config",
    "report",
    ".agents",
    "TEST_READY.md",
    "data/raw",
    "data/simulated",
    "scripts/multigroup",
    "tests/multigroup",
]

# Danh sách đúng 18 bảng CSV chuẩn duy nhất phải có trong results/tables/
REQUIRED_CANONICAL_TABLES = [
    "table1_demographics.csv",
    "table1_country_summary.csv",
    "table2_cfa_measurement.csv",
    "table2_cfa_fit_indices.csv",
    "table3_correlations.csv",
    "table4_descriptives.csv",
    "table5_pooled_sem.csv",
    "table5_sem_fit_indices.csv",
    "table6_multigroup_sem.csv",
    "table6_multigroup_sem_long.csv",
    "table6_multigroup_fit.csv",
    "table6_cross_group_tests.csv",
    "table7_measurement_invariance.csv",
    "table8_hypothesis_testing.csv",
    "table9_robustness_hc3.csv",
    "table9_country_ols_hc3.csv",
    "table9_multiseed_raw_runs.csv",
    "paper_comparison.csv",
]

REQUIRED_REPORTS = [
    "results_summary.md",
    "methodology_and_assumptions.md",
    "limitations.md",
]

REQUIRED_LOGS = [
    "01_generate_multigroup_data.log",
    "02_cfa_and_descriptives.log",
    "03_multigroup_sem_invariance.log",
    "04_hypothesis_and_robustness.log",
]

# Tập tên cột chứa giá trị xác suất p-value cần kiểm tra miền [0, 1]
P_VALUE_COLS = {
    "p",
    "p_val",
    "p_value",
    "p_delta_chi2",
    "delta_p",
    "germany_p",
    "uk_p",
    "usa_p",
    "pooled_p",
    "sem_p_val",
    "ols_hc3_p_val",
    "p_de_uk",
    "p_de_us",
    "p_uk_us",
    "wald_p_3group",
    "multiseed_min_p",
    "multiseed_median_p",
    "multiseed_max_p",
}


def compute_sha256(path: Path) -> str:
    """Tính mã băm SHA-256 của tệp để đối chiếu tính toàn vẹn."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def setup_logger() -> logging.Logger:
    """Khởi tạo bộ ghi nhật ký cho bước kiểm toán 05_verify_all.py."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("verify_all")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    fh = logging.FileHandler(LOGS_DIR / "05_verify_all.log", mode="w", encoding="utf-8")
    fh.setFormatter(fmt)
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def run_all_verifications(logger: logging.Logger) -> Tuple[bool, List[Dict[str, Any]]]:
    """Thực thi tuần tự toàn bộ 17 hạng mục kiểm toán độc lập và xuất verification_report.json."""
    results: List[Dict[str, Any]] = []

    def record(name: str, passed: bool, detail: str) -> None:
        status = "PASS" if passed else "FAIL"
        logger.info("[%s] %s — %s", status, name, detail)
        results.append({"check": name, "passed": bool(passed), "detail": detail})

    # 1. Kiểm tra cấu trúc thư mục sạch (không còn sót thư mục/tệp của phiên bản cũ)
    leftover_legacy = [rel for rel in FORBIDDEN_LEGACY_PATHS if (REPO_ROOT / rel).exists()]
    record(
        "clean_workspace_no_legacy_artifacts",
        len(leftover_legacy) == 0,
        f"leftover_legacy={leftover_legacy}",
    )

    survey_q = DATA_DIR / "Survey_Question.md"
    record(
        "survey_question_reference_preserved",
        survey_q.exists() and survey_q.stat().st_size > 500,
        str(survey_q.relative_to(REPO_ROOT)),
    )

    # 2. Xác minh bộ dữ liệu tổng hợp đa nhóm và tệp siêu dữ liệu manifest
    mg_csv = DATA_DIR / "synthetic_multigroup.csv"
    mg_manifest = DATA_DIR / "data_manifest.json"
    mg_alloc = DATA_DIR / "sample_allocation.csv"
    mg_decl = DATA_DIR / "DATASET_DECLARATION.md"
    for p, label in [
        (mg_csv, "multigroup_dataset_exists"),
        (mg_manifest, "multigroup_manifest_exists"),
        (mg_alloc, "sample_allocation_exists"),
        (mg_decl, "dataset_declaration_exists"),
    ]:
        record(label, p.exists() and p.stat().st_size > 0, str(p.relative_to(REPO_ROOT)))

    if mg_csv.exists() and mg_manifest.exists():
        m_data = json.loads(mg_manifest.read_text(encoding="utf-8"))
        exp_mg_sha = m_data.get("sha256") or m_data.get("dataset_sha256") or m_data.get("checksum")
        obs_mg_sha = compute_sha256(mg_csv)
        record("multigroup_dataset_sha256_matches_manifest", obs_mg_sha == exp_mg_sha, f"SHA-256={obs_mg_sha}")

        with open(mg_csv, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        n_rows = len(rows)
        ids = [r["respondent_id"] for r in rows]
        c_counts: Dict[str, int] = {}
        missing_cells = 0
        likert_ok = True
        tool_ok = True
        likert_cols = [f"{c}{i}" for c in ["NORM", "AWARE", "KNOW", "COMM", "ATT", "RESP"] for i in range(1, 5)] + ["REPORT"]

        for r in rows:
            c_counts[r["country"]] = c_counts.get(r["country"], 0) + 1
            for k, v in r.items():
                if v is None or str(v).strip() == "" or str(v).strip().lower() in ("nan", "null", "na"):
                    missing_cells += 1
            for lc in likert_cols:
                fv = float(r[lc])
                if not (1.0 <= fv <= 5.0 and fv.is_integer()):
                    likert_ok = False
            if r["TOOL"] not in ("0", "1"):
                tool_ok = False

        record("multigroup_N_1017_and_unique_IDs", n_rows == 1017 and len(set(ids)) == 1017, f"N={n_rows}, unique_IDs={len(set(ids))}")
        record(
            "multigroup_country_allocation_306_205_506",
            c_counts == {"DE": 306, "UK": 205, "US": 506},
            f"counts={c_counts}",
        )
        record("multigroup_zero_missing_and_valid_domains", missing_cells == 0 and likert_ok and tool_ok, f"missing={missing_cells}, likert_ok={likert_ok}, tool_ok={tool_ok}")

    # 3. Xác minh có đúng 18 bảng CSV chuẩn và không có bất kỳ tệp CSV nhân bản nào
    missing_tables = []
    for tbl_name in REQUIRED_CANONICAL_TABLES:
        tp = TABLES_DIR / tbl_name
        if not tp.exists() or tp.stat().st_size == 0:
            missing_tables.append(tbl_name)
    actual_csvs = sorted(p.name for p in TABLES_DIR.glob("*.csv")) if TABLES_DIR.exists() else []
    extra_csvs = sorted(set(actual_csvs) - set(REQUIRED_CANONICAL_TABLES))
    record(
        "exact_18_canonical_tables_no_duplicates",
        len(missing_tables) == 0 and len(extra_csvs) == 0,
        f"found={len(actual_csvs)}/18, missing={missing_tables}, extra_duplicates={extra_csvs}",
    )

    # 4. Kiểm tra tính hữu hạn số học (không có NaN/Inf) và miền giá trị p-value [0, 1] trên mọi bảng CSV
    non_finite_errors = []
    invalid_p_errors = []
    averaged_p_columns = []

    for csv_path in sorted(TABLES_DIR.glob("*.csv")):
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            for h in headers:
                hl = h.lower()
                if "mean_p" in hl or "avg_p" in hl or "average_p" in hl:
                    averaged_p_columns.append(f"{csv_path.name}:{h}")
            table_rows = list(reader)
            if len(table_rows) == 0:
                non_finite_errors.append(f"{csv_path.name}:empty_table")

            for r_idx, row in enumerate(table_rows):
                for col, raw_val in row.items():
                    if raw_val is None:
                        non_finite_errors.append(f"{csv_path.name}[{r_idx}].{col}=None")
                        continue
                    sval = str(raw_val).strip()
                    if sval.lower() in ("nan", "inf", "-inf", "+inf", "infinity", "-infinity", "null"):
                        non_finite_errors.append(f"{csv_path.name}[{r_idx}].{col}={sval}")
                        continue

                    if sval not in ("", "-"):
                        try:
                            num = float(sval)
                            if math.isnan(num) or not math.isfinite(num):
                                non_finite_errors.append(f"{csv_path.name}[{r_idx}].{col}={sval}")
                            if col.lower() in P_VALUE_COLS:
                                if not (0.0 <= num <= 1.0):
                                    invalid_p_errors.append(f"{csv_path.name}[{r_idx}].{col}={num}")
                        except ValueError:
                            if col.lower() in P_VALUE_COLS:
                                invalid_p_errors.append(f"{csv_path.name}[{r_idx}].{col}={sval}")

    record(
        "all_csv_estimates_finite_no_nan_or_inf",
        len(non_finite_errors) == 0,
        f"non_finite_count={len(non_finite_errors)} {non_finite_errors[:5]}",
    )
    record(
        "all_p_values_strictly_in_0_1",
        len(invalid_p_errors) == 0,
        f"invalid_p_count={len(invalid_p_errors)} {invalid_p_errors[:5]}",
    )
    record(
        "no_averaged_p_values_in_multiseed_tables",
        len(averaged_p_columns) == 0,
        f"averaged_p_cols={averaged_p_columns}",
    )

    # 5. Kiểm tra tính đơn điệu toán học của bậc tự do df và Chi-square trong Bảng 7 (Bất biến đo lường)
    t7_path = TABLES_DIR / "table7_measurement_invariance.csv"
    if t7_path.exists():
        with open(t7_path, "r", encoding="utf-8") as f:
            t7_rows = list(csv.DictReader(f))
        dfs = [int(float(r["df"])) for r in t7_rows]
        chi2s = [float(r["chi2"]) for r in t7_rows]
        df_inc = len(dfs) == 3 and dfs[0] < dfs[1] < dfs[2]
        chi2_inc = len(chi2s) == 3 and chi2s[0] <= chi2s[1] + 1e-6 and chi2s[1] <= chi2s[2] + 1e-6
        record(
            "measurement_invariance_nested_df_and_chi2_monotonic",
            df_inc and chi2_inc,
            f"dfs={dfs}, chi2={[round(c, 2) for c in chi2s]}",
        )

    # 6. Xác minh đầy đủ 3 báo cáo Markdown và 4 tệp nhật ký chạy mô hình hội tụ không lỗi
    missing_reports = [r for r in REQUIRED_REPORTS if not (REPORTS_DIR / r).exists() or (REPORTS_DIR / r).stat().st_size < 500]
    record("all_3_markdown_reports_present", len(missing_reports) == 0, f"missing={missing_reports}")

    missing_logs = [lg for lg in REQUIRED_LOGS if not (LOGS_DIR / lg).exists() or (LOGS_DIR / lg).stat().st_size == 0]
    log_errors = []
    for lg in REQUIRED_LOGS:
        lp = LOGS_DIR / lg
        if lp.exists():
            full_txt = lp.read_text(encoding="utf-8", errors="replace")
            if "[ERROR]" in full_txt or "Traceback (most recent call last)" in full_txt or "converged=False" in full_txt:
                log_errors.append(lg)
    record(
        "execution_logs_present_and_converged_cleanly",
        len(missing_logs) == 0 and len(log_errors) == 0,
        f"missing_logs={missing_logs}, log_errors={log_errors}",
    )

    all_passed = all(r["passed"] for r in results)
    report_payload = {
        "verified_utc": datetime.now(timezone.utc).isoformat(),
        "all_checks_passed": all_passed,
        "checks_passed": sum(1 for r in results if r["passed"]),
        "checks_total": len(results),
        "checks": results,
    }
    (RESULTS_DIR / "verification_report.json").write_text(
        json.dumps(report_payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return all_passed, results


def main() -> None:
    """Điểm vào thực thi cổng kiểm toán tự động và trả về mã thoát tương ứng."""
    logger = setup_logger()
    logger.info("================================================================================")
    logger.info("START: Automated End-to-End Verification (05_verify_all.py)")
    logger.info("================================================================================")

    all_passed, results = run_all_verifications(logger)
    n_pass = sum(1 for r in results if r["passed"])
    logger.info("================================================================================")
    logger.info("VERIFICATION SUMMARY: %d / %d checks PASSED", n_pass, len(results))
    logger.info("================================================================================")

    if not all_passed:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
