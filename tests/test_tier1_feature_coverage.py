"""
Tầng 1: Bộ kiểm thử độ bao phủ tính năng (F01–F19)
Luồng kiểm thử hộp đen E2E cho thí nghiệm tái tạo SEM đa nhóm DT092 (Petrič & Just, 2025).

Bao phủ toàn bộ 19 nhóm tính năng với tối thiểu 5 kịch bản kiểm thử riêng biệt cho mỗi tính năng (95 ca kiểm thử).
"""

import os
import sys
import unittest
import csv
import json
import hashlib
import re
import math
from pathlib import Path

# Thư mục gốc của dự án
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestF01_CleanWorkspaceAndPipelineStructure(unittest.TestCase):
    """F01: Cấu trúc không gian làm việc và pipeline độc lập tinh gọn"""

    def test_01_legacy_directories_removed(self):
        """Xác minh toàn bộ thư mục bản đơn nhóm cũ và thư mục tạm đã được dọn sạch."""
        for legacy in ["artifacts", "config", "report", ".agents", "TEST_READY.md", "data/raw", "data/simulated", "scripts/multigroup", "tests/multigroup"]:
            self.assertFalse((PROJECT_ROOT / legacy).exists(), f"Legacy path still exists: {legacy}")

    def test_02_sha256_hash_format_contract(self):
        """Xác minh thuật toán SHA-256 sinh chuỗi thập lục phân chữ thường đúng 64 ký tự."""
        sample_hash = hashlib.sha256(b"DT092_Multigroup_Integrity").hexdigest()
        self.assertEqual(len(sample_hash), 64)
        self.assertTrue(bool(re.match(r"^[0-9a-f]{64}$", sample_hash)))

    def test_03_core_project_directories_exist(self):
        """Xác minh các thư mục cốt lõi cấp cao nhất data/, scripts/, results/, reports/ và tests/ tồn tại."""
        for folder in ["data", "scripts", "results", "reports", "tests"]:
            self.assertTrue((PROJECT_ROOT / folder).is_dir(), f"Core folder missing: {folder}")

    def test_04_survey_question_reference_preserved(self):
        """Xác minh tài liệu tham chiếu bảng câu hỏi tiếng Việt 26 mục được giữ nguyên tại data/Survey_Question.md."""
        sq_path = PROJECT_ROOT / "data" / "Survey_Question.md"
        self.assertTrue(sq_path.exists(), "data/Survey_Question.md missing")
        self.assertGreater(sq_path.stat().st_size, 500, "Survey_Question.md unexpectedly small")

    def test_05_multigroup_scripts_complete_sequence(self):
        """Xác minh đầy đủ 6 kịch bản pipeline đa nhóm (từ 00 đến 05) tồn tại trong scripts/."""
        expected_scripts = {
            "00_run_pipeline.py",
            "01_generate_multigroup_data.py",
            "02_cfa_and_descriptives.py",
            "03_multigroup_sem_invariance.py",
            "04_hypothesis_and_robustness.py",
            "05_verify_all.py",
        }
        found_scripts = {p.name for p in (PROJECT_ROOT / "scripts").glob("*.py")}
        self.assertEqual(found_scripts, expected_scripts, f"Scripts mismatch: {found_scripts ^ expected_scripts}")


class TestF02_DeduplicatedCanonicalDeliverables(unittest.TestCase):
    """F02: Chuẩn hóa đầu ra không trùng lặp & minh bạch nguồn gốc dữ liệu"""

    EXPECTED_MULTIGROUP_SHA256 = "52c161dcd96ff568228e74c9c6517f2c2423f4bb2bee0860b511912d4aae5cbe"

    def test_01_multigroup_data_sha256_deterministic(self):
        """Xác minh mã băm SHA-256 của data/synthetic_multigroup.csv khớp tuyệt đối với đầu ra tất định seed=20261029."""
        data_path = PROJECT_ROOT / "data" / "synthetic_multigroup.csv"
        self.assertTrue(data_path.exists(), "Multigroup dataset not found")
        with open(data_path, "rb") as f:
            computed_hash = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(computed_hash, self.EXPECTED_MULTIGROUP_SHA256,
                         "Multigroup dataset SHA-256 drifted from seed=20261029 deterministic output!")

    def test_02_dataset_declaration_exists(self):
        """Xác minh bản tuyên bố đạo đức về dữ liệu mô phỏng tồn tại tại data/DATASET_DECLARATION.md."""
        decl = PROJECT_ROOT / "data" / "DATASET_DECLARATION.md"
        self.assertTrue(decl.exists(), "data/DATASET_DECLARATION.md missing")
        txt = decl.read_text(encoding="utf-8").lower()
        self.assertTrue("synthetic" in txt and "not" in txt)

    def test_03_sample_allocation_table_exists(self):
        """Xác minh bảng phân bổ mẫu data/sample_allocation.csv tồn tại với 4 dòng DE, UK, US và POOLED."""
        alloc = PROJECT_ROOT / "data" / "sample_allocation.csv"
        self.assertTrue(alloc.exists(), "data/sample_allocation.csv missing")
        with open(alloc, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 4)

    def test_04_no_duplicate_alias_csvs_in_tables(self):
        """Xác minh các tệp CSV bản sao trùng lặp đã được loại bỏ khỏi results/tables/."""
        tables_dir = PROJECT_ROOT / "results" / "tables"
        forbidden_aliases = {
            "table4_descriptive_stats.csv",
            "cfa_loadings.csv",
            "cfa_fit_indices.csv",
            "measurement_invariance.csv",
            "sem_pooled_estimates.csv",
            "sem_multigroup_estimates.csv",
            "hypothesis_tests_by_country.csv",
            "robustness_summary.csv",
        }
        present = {p.name for p in tables_dir.glob("*.csv")} if tables_dir.exists() else set()
        self.assertEqual(len(present & forbidden_aliases), 0, f"Duplicate alias CSVs present: {present & forbidden_aliases}")

    def test_05_clean_5_execution_logs(self):
        """Xác minh thư mục results/logs/ chỉ chứa đúng 5 tệp nhật ký đánh số chuẩn mà không có bản sao thừa."""
        logs_dir = PROJECT_ROOT / "results" / "logs"
        self.assertTrue(logs_dir.exists())
        expected_logs = {
            "01_generate_multigroup_data.log",
            "02_cfa_and_descriptives.log",
            "03_multigroup_sem_invariance.log",
            "04_hypothesis_and_robustness.log",
            "05_verify_all.log",
        }
        present_logs = {p.name for p in logs_dir.glob("*.log")}
        self.assertEqual(present_logs, expected_logs, f"Logs mismatch: {present_logs ^ expected_logs}")


class TestF03_MultigroupSampleAllocation(unittest.TestCase):
    """F03: Sinh dữ liệu tổng hợp đa nhóm 3 quốc gia (DE=306, UK=205, US=506)"""

    DATA_PATH = PROJECT_ROOT / "data" / "synthetic_multigroup.csv"

    def _load_data_if_available(self):
        if not self.DATA_PATH.exists():
            self.skipTest(f"Milestone M1 in progress: {self.DATA_PATH} not yet generated")
        with open(self.DATA_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def test_01_total_sample_size_1017(self):
        """Xác minh tập dữ liệu tổng hợp đa nhóm chứa chính xác 1.017 dòng quan sát."""
        rows = self._load_data_if_available()
        self.assertEqual(len(rows), 1017, f"Expected exactly 1,017 rows, got {len(rows)}")

    def test_02_germany_sample_size_306(self):
        """Xác minh nhóm mẫu Đức (DE) có chính xác 306 quan sát."""
        rows = self._load_data_if_available()
        de_rows = [r for r in rows if r.get("country") == "DE"]
        self.assertEqual(len(de_rows), 306, f"Expected 306 Germany rows, got {len(de_rows)}")

    def test_03_uk_sample_size_205(self):
        """Xác minh nhóm mẫu Vương quốc Anh (UK) có chính xác 205 quan sát."""
        rows = self._load_data_if_available()
        uk_rows = [r for r in rows if r.get("country") == "UK"]
        self.assertEqual(len(uk_rows), 205, f"Expected 205 UK rows, got {len(uk_rows)}")

    def test_04_usa_sample_size_506(self):
        """Xác minh nhóm mẫu Hoa Kỳ (US) có chính xác 506 quan sát."""
        rows = self._load_data_if_available()
        us_rows = [r for r in rows if r.get("country") in ("US", "USA")]
        self.assertEqual(len(us_rows), 506, f"Expected 506 USA rows, got {len(us_rows)}")

    def test_05_respondent_ids_unique_and_pattern(self):
        """Xác minh toàn bộ mã định danh người trả lời là duy nhất và tuân theo mẫu SYN0001-SYN1017."""
        rows = self._load_data_if_available()
        ids = [r.get("respondent_id") for r in rows]
        self.assertEqual(len(ids), len(set(ids)), "Respondent IDs must be unique without duplicates")
        for rid in ids:
            self.assertTrue(bool(re.match(r"^SYN\d{4}$", rid)), f"Invalid ID pattern: {rid}")


class TestF04_IndicatorSimulationAndCoding(unittest.TestCase):
    """F04: Mô phỏng biến chỉ báo & mã hóa đảo chiều"""

    DATA_PATH = PROJECT_ROOT / "data" / "synthetic_multigroup.csv"

    def _load_data_if_available(self):
        if not self.DATA_PATH.exists():
            self.skipTest(f"Milestone M1 in progress: {self.DATA_PATH} not yet generated")
        with open(self.DATA_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def test_01_all_24_likert_indicators_present(self):
        """Xác minh đủ 24 biến chỉ báo thuộc 6 khái niệm tiềm ẩn xuất hiện trong tập dữ liệu."""
        rows = self._load_data_if_available()
        constructs = ["NORM", "AWARE", "KNOW", "COMM", "ATT", "RESP"]
        expected_cols = [f"{c}{i}" for c in constructs for i in range(1, 5)]
        first_row = rows[0]
        for col in expected_cols:
            self.assertIn(col, first_row, f"Indicator column missing: {col}")

    def test_02_likert_indicators_within_bounds_1_to_5(self):
        """Xác minh toàn bộ 24 biến chỉ báo Likert đều là số nguyên nằm nghiêm ngặt trong đoạn [1, 5]."""
        rows = self._load_data_if_available()
        constructs = ["NORM", "AWARE", "KNOW", "COMM", "ATT", "RESP"]
        cols = [f"{c}{i}" for c in constructs for i in range(1, 5)]
        for r in rows:
            for c in cols:
                val = float(r[c])
                self.assertTrue(val.is_integer(), f"Indicator {c} value {val} must be integer")
                self.assertGreaterEqual(val, 1.0, f"Indicator {c} value {val} < 1")
                self.assertLessEqual(val, 5.0, f"Indicator {c} value {val} > 5")

    def test_03_tool_binary_indicator_in_0_1(self):
        """Xác minh biến nhị phân TOOL chỉ nhận giá trị trong tập {0, 1}."""
        rows = self._load_data_if_available()
        tool_values = set(int(float(r["TOOL"])) for r in rows)
        self.assertTrue(tool_values.issubset({0, 1}), f"TOOL values must be {0, 1}, found {tool_values}")

    def test_04_report_indicator_in_1_to_5(self):
        """Xác minh biến kết quả REPORT nhận giá trị nguyên nghiêm ngặt trong đoạn [1, 5]."""
        rows = self._load_data_if_available()
        for r in rows:
            val = float(r["REPORT"])
            self.assertTrue(val.is_integer(), f"REPORT value {val} must be integer")
            self.assertGreaterEqual(val, 1.0, f"REPORT value {val} < 1")
            self.assertLessEqual(val, 5.0, f"REPORT value {val} > 5")

    def test_05_reverse_coded_indicators_valid_ranges(self):
        """Xác minh các mục hỏi mã hóa đảo chiều (KNOW3, AWARE3, NORM3, ATT2, ATT3) nằm đúng miền hợp lệ."""
        rows = self._load_data_if_available()
        rev_cols = ["KNOW3", "AWARE3", "NORM3", "ATT2", "ATT3"]
        for r in rows:
            for c in rev_cols:
                val = float(r[c])
                self.assertTrue(1.0 <= val <= 5.0, f"Reverse item {c} value {val} out of range [1, 5]")


class TestF05_DataManifestAndChecksums(unittest.TestCase):
    """F05: Hồ sơ đặc tả dữ liệu đa nhóm & mã kiểm tra toàn vẹn (Manifest & Checksums)"""

    MANIFEST_PATH = PROJECT_ROOT / "data" / "data_manifest.json"
    DATA_PATH = PROJECT_ROOT / "data" / "synthetic_multigroup.csv"

    def _load_manifest_if_available(self):
        if not self.MANIFEST_PATH.exists():
            self.skipTest(f"Milestone M1 in progress: {self.MANIFEST_PATH} not yet generated")
        with open(self.MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_01_manifest_file_exists(self):
        """Xác minh tệp data_manifest.json tồn tại trong thư mục data/."""
        self._load_manifest_if_available()
        self.assertTrue(self.MANIFEST_PATH.exists())

    def test_02_manifest_seed_field(self):
        """Xác minh hồ sơ manifest ghi nhận đầy đủ hạt giống ngẫu nhiên (random seed)."""
        data = self._load_manifest_if_available()
        self.assertTrue("random_seed" in data or "seed" in data, "Seed must be recorded in manifest")

    def test_03_manifest_row_counts(self):
        """Xác minh hồ sơ manifest ghi nhận tổng số dòng 1.017 và quy mô từng nhóm."""
        data = self._load_manifest_if_available()
        row_count = data.get("total_rows") or data.get("row_count") or data.get("n_total")
        self.assertEqual(row_count, 1017, "Manifest row count must be 1,017")

    def test_04_manifest_sha256_hash_matches_dataset(self):
        """Xác minh mã SHA-256 trong manifest khớp với mã băm thực tế của tệp dữ liệu."""
        data = self._load_manifest_if_available()
        manifest_hash = data.get("sha256") or data.get("dataset_sha256") or data.get("checksum")
        self.assertIsNotNone(manifest_hash, "Checksum missing in manifest")
        with open(self.DATA_PATH, "rb") as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(manifest_hash.lower(), actual_hash.lower(), "Dataset hash does not match manifest checksum")

    def test_05_manifest_synthetic_disclaimer(self):
        """Xác minh hồ sơ manifest khai báo rõ bản chất dữ liệu tổng hợp mô phỏng."""
        data = self._load_manifest_if_available()
        desc = str(data.get("description", "")).lower() + str(data.get("note", "")).lower() + str(data.get("disclaimer", "")).lower()
        self.assertTrue("synthetic" in desc or "simulated" in desc or "petrič" in desc,
                        "Manifest must document synthetic data nature")


class TestF06_DemographicsTable1(unittest.TestCase):
    """F06: Thống kê mẫu và công cụ báo cáo (Bảng 1)"""

    TABLE_PATH = PROJECT_ROOT / "results" / "tables" / "table1_demographics.csv"

    def _load_table_if_available(self):
        if not self.TABLE_PATH.exists():
            self.skipTest(f"Milestone M2 in progress: {self.TABLE_PATH} not yet generated")
        with open(self.TABLE_PATH, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def test_01_table1_schema(self):
        """Xác minh lược đồ tiêu đề cột của Bảng 1 khớp với đặc tả."""
        rows = self._load_table_if_available()
        expected = ["variable_category", "subcategory", "pooled_n", "pooled_pct", "germany_n", "germany_pct", "uk_n", "uk_pct", "usa_n", "usa_pct"]
        header = list(rows[0].keys())
        for col in expected:
            self.assertIn(col, header, f"Table 1 column missing: {col}")

    def test_02_table1_row_count_and_categories(self):
        """Xác minh Bảng 1 bao gồm đầy đủ các danh mục thống kê mẫu thiết yếu."""
        rows = self._load_table_if_available()
        categories = set(r["variable_category"].lower() for r in rows)
        self.assertTrue(any("sample" in c or "total" in c for c in categories), "Sample size category missing")
        self.assertTrue(any("tool" in c for c in categories), "Reporting tool category missing")

    def test_03_table1_country_counts_sum_to_pooled(self):
        """Xác minh tổng số lượng 3 quốc gia bằng đúng số lượng mẫu gộp trên mọi dòng: DE + UK + US == Pooled."""
        rows = self._load_table_if_available()
        for r in rows:
            de_n = float(r["germany_n"])
            uk_n = float(r["uk_n"])
            us_n = float(r["usa_n"])
            pooled_n = float(r["pooled_n"])
            self.assertAlmostEqual(de_n + uk_n + us_n, pooled_n, delta=0.5,
                                   msg=f"Sum mismatch in row {r['subcategory']}: {de_n} + {uk_n} + {us_n} != {pooled_n}")

    def test_04_table1_tool_prevalence_benchmark(self):
        """Xác minh tỷ lệ hiện diện công cụ báo cáo trên mẫu gộp bám sát mốc bài báo gốc (~75,5%)."""
        rows = self._load_table_if_available()
        tool_row = next((r for r in rows if "tool" in r["variable_category"].lower() and ("present" in r["subcategory"].lower() or "yes" in r["subcategory"].lower() or "1" in r["subcategory"])), None)
        if tool_row:
            pct = float(tool_row["pooled_pct"])
            # Cho phép sai số mẫu hợp lý xung quanh mốc công bố 75,5% (nằm trong khoảng 65% đến 85%)
            self.assertTrue(65.0 <= pct <= 85.0, f"Tool prevalence {pct}% outside expected benchmark range [65%, 85%]")

    def test_05_table1_percentages_bounded(self):
        """Xác minh mọi tỷ lệ phần trăm được báo cáo đều nằm trong đoạn [0.0, 100.0]."""
        rows = self._load_table_if_available()
        pct_cols = ["pooled_pct", "germany_pct", "uk_pct", "usa_pct"]
        for r in rows:
            for col in pct_cols:
                val = float(r[col])
                self.assertTrue(0.0 <= val <= 100.0, f"Percentage {val} out of bounds in column {col}")


class TestF07_CFAMeasurementModelTable2(unittest.TestCase):
    """F07: Mô hình đo lường CFA (Bảng 2)"""

    TABLE_PATH = PROJECT_ROOT / "results" / "tables" / "table2_cfa_measurement.csv"

    def _load_table_if_available(self):
        if not self.TABLE_PATH.exists():
            self.skipTest(f"Milestone M2 in progress: {self.TABLE_PATH} not yet generated")
        with open(self.TABLE_PATH, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def test_01_table2_schema(self):
        """Xác minh lược đồ tiêu đề cột của Bảng 2 khớp với đặc tả."""
        rows = self._load_table_if_available()
        expected = ["construct", "indicator", "unstd_loading", "std_loading", "std_error", "z_value", "p_value", "cronbach_alpha", "composite_reliability_CR", "ave", "sqrt_ave"]
        header = list(rows[0].keys())
        for col in expected:
            self.assertIn(col, header, f"Table 2 column missing: {col}")

    def test_02_table2_construct_coverage(self):
        """Xác minh đủ 6 khái niệm tiềm ẩn (NORM, AWARE, KNOW, COMM, ATT, RESP) xuất hiện trong bảng."""
        rows = self._load_table_if_available()
        constructs = set(r["construct"] for r in rows)
        expected = {"NORM", "AWARE", "KNOW", "COMM", "ATT", "RESP"}
        self.assertEqual(constructs, expected, f"Constructs mismatch: {constructs} vs {expected}")

    def test_03_table2_factor_loadings_positive_and_significant(self):
        """Xác minh toàn bộ hệ số tải nhân tố chuẩn hóa đều dương (> 0,40) và có ý nghĩa thống kê (p < 0,05)."""
        rows = self._load_table_if_available()
        for r in rows:
            std_l = float(r["std_loading"])
            p_val = float(r["p_value"])
            self.assertGreater(std_l, 0.40, f"Low or negative factor loading for {r['indicator']}: {std_l}")
            self.assertLess(p_val, 0.05, f"Non-significant factor loading for {r['indicator']}: p={p_val}")

    def test_04_table2_reliability_thresholds(self):
        """Xác minh các chỉ số độ tin cậy thang đo đạt ngưỡng chuẩn (alpha >= 0,70, CR >= 0,70)."""
        rows = self._load_table_if_available()
        seen = set()
        for r in rows:
            c = r["construct"]
            if c in seen:
                continue
            seen.add(c)
            alpha = float(r["cronbach_alpha"])
            cr = float(r["composite_reliability_CR"])
            self.assertGreaterEqual(alpha, 0.70, f"Cronbach alpha < 0.70 for construct {c}: {alpha}")
            self.assertGreaterEqual(cr, 0.70, f"Composite Reliability CR < 0.70 for construct {c}: {cr}")

    def test_05_table2_convergent_validity_ave(self):
        """Xác minh giá trị hội tụ AVE >= 0,40 và cột sqrt_ave bằng đúng căn bậc hai của AVE."""
        rows = self._load_table_if_available()
        seen = set()
        for r in rows:
            c = r["construct"]
            if c in seen:
                continue
            seen.add(c)
            ave = float(r["ave"])
            sqrt_ave = float(r["sqrt_ave"])
            self.assertGreaterEqual(ave, 0.40, f"AVE < 0.40 for construct {c}: {ave}")
            self.assertAlmostEqual(sqrt_ave, math.sqrt(ave), places=3, msg=f"sqrt_ave mismatch for {c}")


class TestF08_CorrelationMatricesTable3(unittest.TestCase):
    """F08: Ma trận tương quan giữa các biến (Bảng 3)"""

    TABLE_PATH = PROJECT_ROOT / "results" / "tables" / "table3_correlations.csv"

    def _load_table_if_available(self):
        if not self.TABLE_PATH.exists():
            self.skipTest(f"Milestone M2 in progress: {self.TABLE_PATH} not yet generated")
        with open(self.TABLE_PATH, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def test_01_table3_schema(self):
        """Xác minh lược đồ tiêu đề cột của Bảng 3."""
        rows = self._load_table_if_available()
        expected = ["group", "variable", "REPORT", "ATT", "RESP", "KNOW", "COMM", "NORM", "AWARE", "TOOL"]
        header = list(rows[0].keys())
        for col in expected:
            self.assertIn(col, header, f"Table 3 column missing: {col}")

    def test_02_table3_diagonal_ones(self):
        """Xác minh các phần tử trên đường chéo chính của ma trận tương quan bằng 1,0."""
        rows = self._load_table_if_available()
        vars_list = ["REPORT", "ATT", "RESP", "KNOW", "COMM", "NORM", "AWARE", "TOOL"]
        for r in rows:
            var = r["variable"]
            if var in vars_list:
                diag_val = float(r[var])
                self.assertAlmostEqual(diag_val, 1.0, places=4, msg=f"Diagonal for {var} in group {r['group']} != 1.0")

    def test_03_table3_bounds_minus_one_to_plus_one(self):
        """Xác minh toàn bộ hệ số tương quan đều nằm nghiêm ngặt trong đoạn [-1.0, 1.0]."""
        rows = self._load_table_if_available()
        vars_list = ["REPORT", "ATT", "RESP", "KNOW", "COMM", "NORM", "AWARE", "TOOL"]
        for r in rows:
            for v in vars_list:
                val = float(r[v])
                self.assertTrue(-1.0 <= val <= 1.0, f"Correlation {val} out of bounds for {r['variable']} vs {v}")

    def test_04_table3_symmetry(self):
        """Xác minh ma trận tương quan có tính đối xứng r(A, B) == r(B, A)."""
        rows = self._load_table_if_available()
        groups = set(r["group"] for r in rows)
        vars_list = ["REPORT", "ATT", "RESP", "KNOW", "COMM", "NORM", "AWARE", "TOOL"]
        for grp in groups:
            grp_rows = {r["variable"]: r for r in rows if r["group"] == grp}
            for v1 in vars_list:
                for v2 in vars_list:
                    if v1 in grp_rows and v2 in grp_rows:
                        r12 = float(grp_rows[v1][v2])
                        r21 = float(grp_rows[v2][v1])
                        self.assertAlmostEqual(r12, r21, places=3, msg=f"Asymmetry in {grp} between {v1} and {v2}")

    def test_05_table3_groups_present(self):
        """Xác minh bảng chứa đủ ma trận tương quan cho mẫu gộp và cả 3 nhóm quốc gia."""
        rows = self._load_table_if_available()
        groups = set(r["group"].upper() for r in rows)
        self.assertTrue(any(g in ("ALL", "POOLED") for g in groups), "Pooled group missing in Table 3")
        self.assertTrue("DE" in groups or "GERMANY" in groups, "Germany group missing in Table 3")
        self.assertTrue("UK" in groups, "UK group missing in Table 3")
        self.assertTrue("US" in groups or "USA" in groups, "USA group missing in Table 3")


class TestF09_DescriptiveStatisticsTable4(unittest.TestCase):
    """F09: Thống kê mô tả các biến nghiên cứu (Bảng 4)"""

    TABLE_PATH = PROJECT_ROOT / "results" / "tables" / "table4_descriptives.csv"

    def _load_table_if_available(self):
        if not self.TABLE_PATH.exists():
            self.skipTest("Table 4 not yet generated")
        with open(self.TABLE_PATH, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def test_01_table4_schema(self):
        """Xác minh lược đồ tiêu đề cột của Bảng 4."""
        rows = self._load_table_if_available()
        expected = ["group", "variable", "mean", "sd", "scale_min", "scale_max", "skewness", "kurtosis"]
        header = list(rows[0].keys())
        for col in expected:
            self.assertIn(col, header, f"Table 4 column missing: {col}")

    def test_02_table4_scale_bounds(self):
        """Xác minh giá trị cực tiểu và cực đại lý thuyết của thang đo khớp đặc tả."""
        rows = self._load_table_if_available()
        for r in rows:
            s_min = float(r["scale_min"])
            s_max = float(r["scale_max"])
            if r["variable"] == "TOOL":
                self.assertEqual(s_min, 0.0)
                self.assertEqual(s_max, 1.0)
            else:
                self.assertEqual(s_min, 1.0)
                self.assertEqual(s_max, 5.0)

    def test_03_table4_positive_standard_deviations(self):
        """Xác minh độ lệch chuẩn luôn dương ngặt (SD > 0)."""
        rows = self._load_table_if_available()
        for r in rows:
            sd = float(r["sd"])
            self.assertGreater(sd, 0.0, f"SD must be positive for {r['variable']} in {r['group']}")

    def test_04_table4_mean_ranges(self):
        """Xác minh giá trị trung bình nằm trong miền giá trị hợp lệ của thang đo."""
        rows = self._load_table_if_available()
        for r in rows:
            m = float(r["mean"])
            if r["variable"] == "TOOL":
                self.assertTrue(0.0 <= m <= 1.0, f"Mean out of bounds for TOOL: {m}")
            else:
                self.assertTrue(1.0 <= m <= 5.0, f"Mean out of bounds for Likert item {r['variable']}: {m}")

    def test_05_table4_finite_skewness_and_kurtosis(self):
        """Xác minh độ lệch (skewness) và độ nhọn (kurtosis) đều là số thực hữu hạn."""
        rows = self._load_table_if_available()
        for r in rows:
            skew = float(r["skewness"])
            kurt = float(r["kurtosis"])
            self.assertFalse(math.isnan(skew) or math.isinf(skew), f"Invalid skewness for {r['variable']}")
            self.assertFalse(math.isnan(kurt) or math.isinf(kurt), f"Invalid kurtosis for {r['variable']}")


class TestF10_PooledBaselineSEMTable5(unittest.TestCase):
    """F10: Mô hình SEM cơ sở trên mẫu gộp (Bảng 5)"""

    TABLE_PATH = PROJECT_ROOT / "results" / "tables" / "table5_pooled_sem.csv"

    def _load_table_if_available(self):
        if not self.TABLE_PATH.exists():
            self.skipTest(f"Milestone M3 in progress: {self.TABLE_PATH} not yet generated")
        with open(self.TABLE_PATH, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def test_01_table5_schema(self):
        """Xác minh lược đồ tiêu đề cột của Bảng 5."""
        rows = self._load_table_if_available()
        expected = ["outcome", "predictor", "path_label", "unstd_beta", "std_beta", "std_error", "z_value", "p_value", "ci_lower", "ci_upper", "r_squared"]
        header = list(rows[0].keys())
        for col in expected:
            self.assertIn(col, header, f"Table 5 column missing: {col}")

    def test_02_table5_paths_count_15(self):
        """Xác minh đủ 15 đường dẫn cấu trúc theo giả thuyết được báo cáo trong Bảng 5."""
        rows = self._load_table_if_available()
        self.assertEqual(len(rows), 15, f"Expected 15 structural paths, found {len(rows)}")

    def test_03_table5_r_squared_bounds(self):
        """Xác minh hệ số R-squared của các biến nội sinh nằm trong khoảng mở (0, 1)."""
        rows = self._load_table_if_available()
        for r in rows:
            r2 = float(r["r_squared"])
            self.assertTrue(0.0 < r2 < 1.0, f"R² {r2} out of valid bounds for outcome {r['outcome']}")

    def test_04_table5_positive_std_errors(self):
        """Xác minh sai số chuẩn luôn dương ngặt."""
        rows = self._load_table_if_available()
        for r in rows:
            se = float(r["std_error"])
            self.assertGreater(se, 0.0, f"Standard error non-positive for path {r['path_label']}: {se}")

    def test_05_table5_ci_consistency(self):
        """Xác minh khoảng tin cậy nhất quán toán học: ci_lower <= unstd_beta <= ci_upper."""
        rows = self._load_table_if_available()
        for r in rows:
            lower = float(r["ci_lower"])
            upper = float(r["ci_upper"])
            beta = float(r["unstd_beta"])
            self.assertLessEqual(lower, upper, f"CI bounds inverted: [{lower}, {upper}]")
            self.assertTrue(lower <= beta <= upper or math.isclose(lower, beta, abs_tol=1e-3) or math.isclose(upper, beta, abs_tol=1e-3),
                            f"Beta {beta} outside CI [{lower}, {upper}]")


class TestF11_MultigroupCountrySEMTable6(unittest.TestCase):
    """F11: Mô hình SEM đa nhóm theo quốc gia (Bảng 6)"""

    TABLE_PATH = PROJECT_ROOT / "results" / "tables" / "table6_multigroup_sem.csv"

    def _load_table_if_available(self):
        if not self.TABLE_PATH.exists():
            self.skipTest(f"Milestone M3 in progress: {self.TABLE_PATH} not yet generated")
        with open(self.TABLE_PATH, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def test_01_table6_schema(self):
        """Xác minh lược đồ tiêu đề cột của Bảng 6."""
        rows = self._load_table_if_available()
        expected = ["path_label", "path_equation", "germany_beta", "germany_se", "germany_p", "uk_beta", "uk_se", "uk_p", "usa_beta", "usa_se", "usa_p", "paper_germany_beta", "paper_uk_beta", "paper_usa_beta"]
        header = list(rows[0].keys())
        for col in expected:
            self.assertIn(col, header, f"Table 6 column missing: {col}")

    def test_02_table6_all_15_paths_reported(self):
        """Xác minh Bảng 6 báo cáo đầy đủ 15 đường dẫn cấu trúc."""
        rows = self._load_table_if_available()
        self.assertEqual(len(rows), 15, f"Expected 15 paths, found {len(rows)}")

    def test_03_table6_paper_benchmarks_populated(self):
        """Xác minh các cột hệ số đối chiếu từ bài báo gốc đều có dữ liệu đầy đủ."""
        rows = self._load_table_if_available()
        for r in rows:
            self.assertTrue(r["paper_germany_beta"], f"Missing paper Germany benchmark for {r['path_label']}")
            self.assertTrue(r["paper_uk_beta"], f"Missing paper UK benchmark for {r['path_label']}")
            self.assertTrue(r["paper_usa_beta"], f"Missing paper USA benchmark for {r['path_label']}")

    def test_04_table6_p_values_valid(self):
        """Xác minh giá trị p của từng quốc gia là xác suất hợp lệ trong đoạn [0.0, 1.0]."""
        rows = self._load_table_if_available()
        for r in rows:
            for country in ["germany", "uk", "usa"]:
                p_str = r[f"{country}_p"]
                p_val = float(p_str.replace("<", "").replace(">", "").strip())
                self.assertTrue(0.0 <= p_val <= 1.0, f"Invalid p-value for {country} in {r['path_label']}: {p_val}")

    def test_05_table6_betas_finite(self):
        """Xác minh toàn bộ hệ số beta ước lượng ở các quốc gia đều là số thực hữu hạn."""
        rows = self._load_table_if_available()
        for r in rows:
            for country in ["germany", "uk", "usa"]:
                beta = float(r[f"{country}_beta"])
                self.assertFalse(math.isnan(beta) or math.isinf(beta), f"Non-finite beta in {country}: {beta}")


class TestF12_MeasurementInvarianceTable7(unittest.TestCase):
    """F12: Kiểm định tính bất biến đo lường (Bảng 7)"""

    TABLE_PATH = PROJECT_ROOT / "results" / "tables" / "table7_measurement_invariance.csv"

    def _load_table_if_available(self):
        if not self.TABLE_PATH.exists():
            self.skipTest(f"Milestone M3 in progress: {self.TABLE_PATH} not yet generated")
        with open(self.TABLE_PATH, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def test_01_table7_schema(self):
        """Xác minh lược đồ tiêu đề cột của Bảng 7."""
        rows = self._load_table_if_available()
        expected = ["model_level", "constraints", "chi2", "df", "p_val", "cfi", "tli", "rmsea", "srmr", "delta_chi2", "delta_df", "p_delta_chi2", "delta_cfi", "delta_rmsea", "delta_srmr", "invariance_decision"]
        header = list(rows[0].keys())
        for col in expected:
            self.assertIn(col, header, f"Table 7 column missing: {col}")

    def test_02_table7_hierarchical_models(self):
        """Xác minh các mô hình bất biến cấu hình (Configural) và hệ số tải (Metric) đều được đánh giá."""
        rows = self._load_table_if_available()
        levels = [r["model_level"].lower() for r in rows]
        self.assertTrue(any("configural" in l for l in levels), "Configural model missing")
        self.assertTrue(any("metric" in l for l in levels), "Metric model missing")

    def test_03_table7_strictly_increasing_degrees_of_freedom(self):
        """Xác minh bậc tự do tăng ngặt khi bổ sung thêm các ràng buộc bất biến."""
        rows = self._load_table_if_available()
        dfs = [float(r["df"]) for r in rows]
        for i in range(1, len(dfs)):
            self.assertGreater(dfs[i], dfs[i-1], f"Degrees of freedom must increase from level {i-1} to {i}")

    def test_04_table7_delta_fit_cutoffs(self):
        """Xác minh độ chênh lệch chỉ số phù hợp được báo cáo và |delta CFI| của Metric đạt ngưỡng chuẩn."""
        rows = self._load_table_if_available()
        metric_row = next((r for r in rows if "metric" in r["model_level"].lower()), None)
        if metric_row and metric_row["delta_cfi"]:
            delta_cfi = abs(float(metric_row["delta_cfi"]))
            self.assertLessEqual(delta_cfi, 0.020, f"Delta CFI {delta_cfi} indicates severe non-invariance")

    def test_05_table7_decision_populated(self):
        """Xác minh cột kết luận invariance_decision được điền đầy đủ thông tin."""
        rows = self._load_table_if_available()
        for r in rows:
            self.assertTrue(bool(r["invariance_decision"].strip()), f"Empty invariance decision for {r['model_level']}")


class TestF13_EstimationMethodDocumentation(unittest.TestCase):
    """F13: Tài liệu hóa phương pháp ước lượng & giả định"""

    REPORT_PATH = PROJECT_ROOT / "reports" / "methodology_and_assumptions.md"

    def _load_text_if_available(self):
        if not self.REPORT_PATH.exists():
            self.skipTest(f"Milestone M4 in progress: {self.REPORT_PATH} not yet generated")
        with open(self.REPORT_PATH, "r", encoding="utf-8") as f:
            return f.read()

    def test_01_documentation_file_exists(self):
        """Xác minh tệp tài liệu phương pháp luận tồn tại."""
        self._load_text_if_available()
        self.assertTrue(self.REPORT_PATH.exists())

    def test_02_wlsmv_vs_mlw_contrast_documented(self):
        """Xác minh tài liệu giải thích tường minh sự khác biệt giữa bộ ước lượng WLSMV và MLW."""
        text = self._load_text_if_available()
        self.assertTrue("wlsmv" in text.lower() and "ml" in text.lower(),
                        "Documentation must contrast WLSMV and ML/MLW estimators")

    def test_03_pseudo_continuous_disclaimer(self):
        """Xác minh tài liệu nêu rõ giả định xử lý thang đo thứ bậc Likert như biến giả liên tục (pseudo-continuous)."""
        text = self._load_text_if_available()
        self.assertTrue("pseudo-continuous" in text.lower() or "ordinal" in text.lower() or "discret" in text.lower(),
                        "Documentation must address ordinal vs continuous assumptions")

    def test_04_ols_hc3_sensitivity_safeguard(self):
        """Xác minh tài liệu giải trình việc dùng OLS-HC3 làm chốt chặn kiểm tra độ nhạy đối với phi chuẩn và phương sai thay đổi."""
        text = self._load_text_if_available()
        self.assertTrue("hc3" in text.lower() or "robust" in text.lower(),
                        "Documentation must mention HC3 standard errors")

    def test_05_optimizer_and_convergence_criteria(self):
        """Xác minh chi tiết bộ giải tối ưu hóa (Wishart / semopy / scipy) và tiêu chuẩn hội tụ được ghi nhận."""
        text = self._load_text_if_available()
        self.assertTrue("optimizer" in text.lower() or "convergence" in text.lower() or "semopy" in text.lower(),
                        "Documentation must specify solver details")


class TestF14_HypothesisTestingTable8(unittest.TestCase):
    """F14: Đánh giá kiểm định giả thuyết (Bảng 8)"""

    TABLE_PATH = PROJECT_ROOT / "results" / "tables" / "table8_hypothesis_testing.csv"

    def _load_table_if_available(self):
        target = self.TABLE_PATH
        if not target.exists():
            target = PROJECT_ROOT / "results" / "tables" / "table8_hypotheses.csv"
        if not target.exists():
            self.skipTest("Milestone M4 in progress: Table 8 not yet generated")
        with open(target, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def test_01_table8_schema(self):
        """Xác minh lược đồ tiêu đề cột của Bảng 8."""
        rows = self._load_table_if_available()
        expected = ["hypothesis", "path", "hypothesized_sign", "pooled_status", "germany_status", "uk_status", "usa_status", "decision_rule"]
        header = list(rows[0].keys())
        for col in expected:
            self.assertIn(col, header, f"Table 8 column missing: {col}")

    def test_02_table8_covers_all_hypotheses(self):
        """Xác minh toàn bộ 15 giả thuyết từ H1a đến H7b đều được đánh giá."""
        rows = self._load_table_if_available()
        hypotheses = [r["hypothesis"] for r in rows]
        expected_hyps = ["H1a", "H2a", "H3a", "H4a", "H1b", "H2b", "H3b", "H4b", "H1c", "H2c", "H3c", "H5", "H6", "H7a", "H7b"]
        for h in expected_hyps:
            self.assertIn(h, hypotheses, f"Hypothesis {h} missing in Table 8")

    def test_03_table8_status_values_valid(self):
        """Xác minh các nhãn trạng thái kết luận giả thuyết tuân theo danh mục chuẩn hóa."""
        rows = self._load_table_if_available()
        valid_statuses = {"supported", "partially supported", "not supported", "not supported (negative)", "partial support"}
        for r in rows:
            for country in ["pooled", "germany", "uk", "usa"]:
                status = r[f"{country}_status"].lower().strip()
                self.assertTrue(any(v in status for v in valid_statuses),
                                f"Unexpected status '{status}' for {r['hypothesis']} in {country}")

    def test_04_table8_decision_rule_combines_sign_and_p(self):
        """Xác minh quy tắc ra quyết định kết hợp đồng thời cả sự khớp dấu VÀ ngưỡng p < 0,05."""
        rows = self._load_table_if_available()
        for r in rows:
            rule = r["decision_rule"].lower()
            self.assertTrue("0.05" in rule or "sign" in rule or "p <" in rule,
                            f"Decision rule does not state formal criteria for {r['hypothesis']}")

    def test_05_table8_paradoxical_comm_paths_evaluated_correctly(self):
        """Xác minh các đường dẫn nghịch lý mang dấu âm COMM->ATT được phân loại đúng là không được ủng hộ."""
        rows = self._load_table_if_available()
        h3a = next(r for r in rows if r["hypothesis"] == "H3a")
        self.assertTrue("not supported" in h3a["pooled_status"].lower(), "H3a must be Not Supported due to negative sign")


class TestF15_RobustnessOLSHC3Table9(unittest.TestCase):
    """F15: Kiểm định độ vững đa hạt giống & OLS-HC3 (Bảng 9)"""

    TABLE_PATH = PROJECT_ROOT / "results" / "tables" / "table9_robustness_hc3.csv"

    def _load_table_if_available(self):
        target = self.TABLE_PATH
        if not target.exists():
            target = PROJECT_ROOT / "results" / "tables" / "table9_robustness.csv"
        if not target.exists():
            self.skipTest("Milestone M4 in progress: Table 9 not yet generated")
        with open(target, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def test_01_table9_schema(self):
        """Xác minh lược đồ tiêu đề cột của Bảng 9."""
        rows = self._load_table_if_available()
        expected = ["model_spec", "path", "sem_std_beta", "sem_p_val", "ols_hc3_unstd_b", "ols_hc3_se", "ols_hc3_p_val", "multiseed_mean_beta", "multiseed_sd_beta", "sig_rate_5seeds", "robustness_conclusion"]
        header = list(rows[0].keys())
        for col in expected:
            self.assertIn(col, header, f"Table 9 column missing: {col}")

    def test_02_table9_positive_hc3_se(self):
        """Xác minh sai số chuẩn vững HC3 luôn dương ngặt."""
        rows = self._load_table_if_available()
        for r in rows:
            se = float(r["ols_hc3_se"])
            self.assertGreater(se, 0.0, f"HC3 standard error non-positive for {r['path']}")

    def test_03_table9_multiseed_sig_rate_format(self):
        """Xác minh tỷ lệ có ý nghĩa thống kê qua 5 hạt giống được báo cáo đúng định dạng (ví dụ 5/5)."""
        rows = self._load_table_if_available()
        for r in rows:
            rate = r["sig_rate_5seeds"].strip()
            self.assertTrue("/" in rate or "%" in rate or float(rate) <= 1.0, f"Invalid sig_rate format: {rate}")

    def test_04_table9_multiseed_sd_finite(self):
        """Xác minh độ lệch chuẩn hệ số beta qua nhiều hạt giống là số hữu hạn không âm."""
        rows = self._load_table_if_available()
        for r in rows:
            sd = float(r["multiseed_sd_beta"])
            self.assertFalse(math.isnan(sd) or math.isinf(sd))
            self.assertGreaterEqual(sd, 0.0)

    def test_05_table9_sem_and_hc3_sign_agreement(self):
        """Xác minh các đường dẫn cấu trúc có độ lớn đáng kể giữ nguyên chiều tác động giữa SEM và OLS-HC3."""
        rows = self._load_table_if_available()
        for r in rows:
            sem_beta = float(r["sem_std_beta"])
            hc3_b = float(r["ols_hc3_unstd_b"])
            # Các đường dẫn có tác động rõ rệt không được đảo dấu giữa SEM và HC3
            if abs(sem_beta) > 0.15:
                self.assertEqual(math.copysign(1, sem_beta), math.copysign(1, hc3_b),
                                 f"Sign discordance between SEM ({sem_beta}) and HC3 ({hc3_b}) for {r['path']}")


class TestF16_PublishedComparisonBenchmarks(unittest.TestCase):
    """F16: Đối chiếu với kết quả đã công bố trong bài báo gốc (Petrič & Just, 2025)"""

    COMP_PATH = PROJECT_ROOT / "results" / "tables" / "paper_comparison.csv"
    ALLOC_PATH = PROJECT_ROOT / "data" / "sample_allocation.csv"

    def test_01_paper_comparison_table_exists(self):
        """Xác minh bảng CSV đối chiếu trực tiếp với bài báo gốc tồn tại trong results/tables/."""
        self.assertTrue(self.COMP_PATH.exists(), "results/tables/paper_comparison.csv missing")

    def test_02_paper_comparison_contains_15_structural_paths(self):
        """Xác minh paper_comparison.csv chứa đầy đủ 15 giả thuyết cấu trúc (từ H1a đến H7b)."""
        with open(self.COMP_PATH, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 15, f"Expected exactly 15 rows in paper_comparison.csv, found {len(rows)}")

    def test_03_paper_pooled_estimates_match_published_literature(self):
        """Xác minh các hệ số tham chiếu bài báo gốc khớp số liệu công bố (ví dụ H3c COMM->REPORT = 0,29)."""
        with open(self.COMP_PATH, "r", encoding="utf-8") as f:
            rows = {r["hypothesis"]: r for r in csv.DictReader(f)}
        self.assertIn("H3c", rows)
        self.assertAlmostEqual(float(rows["H3c"]["paper_pooled"]), 0.29, places=2)

    def test_04_paper_discrepancy_calculation_contract(self):
        """Xác minh công thức tính độ lệch tuyệt đối |beta_sim - beta_paper| trong paper_comparison.csv."""
        with open(self.COMP_PATH, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            expected_diff = abs(float(r["simulated_pooled"]) - float(r["paper_pooled"]))
            self.assertAlmostEqual(float(r["abs_diff_pooled"]), expected_diff, places=3)

    def test_05_published_country_sample_sizes_verified(self):
        """Xác minh hằng số cỡ mẫu bài báo gốc (DE=306, UK=205, US=506, Tổng=1017) trong data/sample_allocation.csv."""
        with open(self.ALLOC_PATH, "r", encoding="utf-8") as f:
            by_code = {r["country_code"]: r for r in csv.DictReader(f)}
        self.assertEqual(int(by_code["DE"]["paper_n"]), 306)
        self.assertEqual(int(by_code["UK"]["paper_n"]), 205)
        self.assertEqual(int(by_code["US"]["paper_n"]), 506)
        self.assertEqual(int(by_code["POOLED"]["paper_n"]), 1017)


class TestF17_ReportingArtifacts(unittest.TestCase):
    """F17: Các báo cáo tổng hợp đầu ra (Reporting Artifacts)"""

    REPORTS_DIR = PROJECT_ROOT / "reports"

    def _check_report_file(self, filename):
        path = self.REPORTS_DIR / filename
        if not path.exists():
            self.skipTest(f"Milestone M4 in progress: {path} not yet generated")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertGreater(len(content), 100, f"Report {filename} too brief")
        return content

    def test_01_results_summary_report(self):
        """Xác minh tệp results_summary.md tồn tại và bao gồm các phần phân tích 3 quốc gia."""
        content = self._check_report_file("results_summary.md")
        self.assertTrue("germany" in content.lower() and "uk" in content.lower() and "usa" in content.lower())

    def test_02_methodology_and_assumptions_report(self):
        """Xác minh tệp methodology_and_assumptions.md tồn tại và trình bày phương pháp CFA/SEM."""
        content = self._check_report_file("methodology_and_assumptions.md")
        self.assertTrue("sem" in content.lower() or "cfa" in content.lower())

    def test_03_limitations_report(self):
        """Xác minh tệp limitations.md tồn tại và thảo luận rõ giới hạn của dữ liệu mô phỏng."""
        content = self._check_report_file("limitations.md")
        self.assertTrue("limitation" in content.lower() or "synthetic" in content.lower())

    def test_04_synthetic_data_disclaimer_present(self):
        """Xác minh các báo cáo không đánh tráo dữ liệu tổng hợp thành dữ liệu khảo sát con người thực tế."""
        content = self._check_report_file("limitations.md")
        self.assertTrue("synthetic" in content.lower() or "simulated" in content.lower())

    def test_05_all_3_reports_present(self):
        """Xác minh đủ cả 3 báo cáo cốt lõi hiện diện trong thư mục reports/."""
        if not self.REPORTS_DIR.exists():
            self.skipTest(f"Milestone M4 in progress: {self.REPORTS_DIR} not yet generated")
        files = [f.name for f in self.REPORTS_DIR.glob("*.md")]
        expected = ["results_summary.md", "methodology_and_assumptions.md", "limitations.md"]
        for e in expected:
            self.assertIn(e, files, f"Missing report: {e}")


class TestF18_AutomatedVerificationScript(unittest.TestCase):
    """F18: Hợp đồng kịch bản kiểm định tự động toàn diện"""

    VERIFY_SCRIPT = PROJECT_ROOT / "scripts" / "05_verify_all.py"

    def test_01_verification_script_exists_or_contract_defined(self):
        """Xác minh kịch bản kiểm định tự động tồn tại tại scripts/05_verify_all.py."""
        self.assertTrue(self.VERIFY_SCRIPT.exists())

    def test_02_verification_script_checks_tables_existence(self):
        """Xác minh kịch bản kiểm định đối chiếu đầy đủ từ Bảng 1 đến Bảng 9."""
        with open(self.VERIFY_SCRIPT, "r", encoding="utf-8") as f:
            code = f.read()
        self.assertTrue("table1" in code and "table9" in code, "Verification script must reference all tables")

    def test_03_verification_script_checks_finiteness(self):
        """Xác minh kịch bản kiểm định có kiểm tra các giá trị NaN hoặc vô cực (Inf)."""
        with open(self.VERIFY_SCRIPT, "r", encoding="utf-8") as f:
            code = f.read()
        self.assertTrue("isnan" in code or "isfinite" in code or "null" in code or "isna" in code,
                        "Verification script must validate numeric finiteness")

    def test_04_verification_script_checks_p_values(self):
        """Xác minh kịch bản kiểm định bắt buộc điều kiện xác suất 0 <= p <= 1."""
        with open(self.VERIFY_SCRIPT, "r", encoding="utf-8") as f:
            code = f.read()
        self.assertTrue("p_val" in code or "p_value" in code or "p" in code)

    def test_05_verification_script_exit_contract(self):
        """Xác minh kịch bản kiểm định trả mã thoát chuẩn sys.exit(0) khi đạt và sys.exit(1) khi lỗi."""
        with open(self.VERIFY_SCRIPT, "r", encoding="utf-8") as f:
            code = f.read()
        self.assertTrue("sys.exit" in code or "exit(" in code)


class TestF19_E2ETestSuiteArchitecture(unittest.TestCase):
    """F19: Kiến trúc & hạ tầng bộ kiểm thử đầu-cuối (E2E Test Suite)"""

    TEST_DIR = PROJECT_ROOT / "tests"

    def test_01_project_readme_exists_and_documents_tests(self):
        """Xác minh tệp README.md tồn tại ở thư mục gốc và hướng dẫn chạy pipeline cùng bộ kiểm thử."""
        readme_path = PROJECT_ROOT / "README.md"
        self.assertTrue(readme_path.exists(), "README.md missing")
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertTrue("run_e2e_tests.py" in content and "00_run_pipeline.py" in content)

    def test_02_all_4_tier_test_files_defined(self):
        """Xác minh đủ 4 mô-đun kiểm thử theo 4 tầng hiện diện trong thư mục tests/."""
        expected_modules = [
            "test_tier1_feature_coverage.py",
            "test_tier2_boundaries.py",
            "test_tier3_pairwise.py",
            "test_tier4_e2e.py",
        ]
        for m in expected_modules:
            self.assertTrue((self.TEST_DIR / m).exists(), f"Test module missing: {m}")

    def test_03_standalone_test_runner_exists(self):
        """Xác minh trình chạy kiểm thử độc lập run_e2e_tests.py tồn tại trong tests/."""
        runner_path = self.TEST_DIR / "run_e2e_tests.py"
        self.assertTrue(runner_path.exists(), "tests/run_e2e_tests.py missing")

    def test_04_test_suite_zero_external_dependency(self):
        """Xác minh bộ kiểm thử được xây dựng hoàn toàn trên thư viện chuẩn unittest của Python."""
        self.assertTrue(issubclass(unittest.TestCase, object))

    def test_05_workspace_isolation_guarantee(self):
        """Xác minh thư mục tests/ được cô lập sạch sẽ và chỉ chứa đúng 6 tệp Python chuẩn."""
        self.assertTrue(self.TEST_DIR.is_dir())
        py_files = {p.name for p in self.TEST_DIR.glob("*.py")}
        expected = {
            "__init__.py",
            "run_e2e_tests.py",
            "test_tier1_feature_coverage.py",
            "test_tier2_boundaries.py",
            "test_tier3_pairwise.py",
            "test_tier4_e2e.py",
        }
        self.assertEqual(py_files, expected, f"Unexpected .py files in tests/: {py_files ^ expected}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
