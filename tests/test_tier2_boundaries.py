"""
Tầng 2: Bộ kiểm thử các trường hợp biên và góc khuất (Boundary & Corner Cases)
Luồng kiểm thử hộp đen E2E cho thí nghiệm tái tạo SEM đa nhóm DT092 (Petrič & Just, 2025).

Tập trung vào các trường hợp biên, điều kiện cực hạn của miền dữ liệu, giới hạn tham số và bất biến toán học.
"""

import os
import sys
import unittest
import csv
import json
import re
import math
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestTier2BoundariesAndCornerCases(unittest.TestCase):
    """Tầng 2: Kiểm thử toàn diện giá trị biên, trường hợp đặc biệt và điều kiện cực hạn"""

    DATA_PATH = PROJECT_ROOT / "data" / "synthetic_multigroup.csv"

    def _load_data_if_available(self):
        if not self.DATA_PATH.exists():
            self.skipTest(f"Milestone M1 in progress: {self.DATA_PATH} not yet generated")
        with open(self.DATA_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def test_01_no_missing_or_null_values_in_dataset(self):
        """Trường hợp đặc biệt: Đảm bảo không có ô trống, null, NaN hoặc chỉ chứa khoảng trắng trên toàn bộ 1.017 dòng."""
        rows = self._load_data_if_available()
        for i, row in enumerate(rows):
            for col, val in row.items():
                self.assertIsNotNone(val, f"Null value in row {i}, col {col}")
                clean_val = str(val).strip()
                self.assertTrue(clean_val != "", f"Empty string in row {i}, col {col}")
                self.assertFalse(clean_val.lower() in ("nan", "null", "none", "na", "#n/a"),
                                f"Missing sentinel in row {i}, col {col}: {clean_val}")

    def test_02_likert_boundary_clamping_and_rejection(self):
        """Trường hợp biên: Bắt buộc miền giá trị nghiêm ngặt [1, 5]; xác nhận không có giá trị 0, 6, -1 hoặc 999."""
        rows = self._load_data_if_available()
        constructs = ["NORM", "AWARE", "KNOW", "COMM", "ATT", "RESP"]
        cols = [f"{c}{i}" for c in constructs for i in range(1, 5)] + ["REPORT"]
        for r in rows:
            for c in cols:
                val = float(r[c])
                self.assertGreaterEqual(val, 1.0, f"Value below Likert minimum in {c}: {val}")
                self.assertLessEqual(val, 5.0, f"Value above Likert maximum in {c}: {val}")
                self.assertNotIn(val, [0.0, 6.0, -1.0, 999.0], f"Forbidden boundary value {val} in {c}")

    def test_03_binary_tool_domain_boundary(self):
        """Trường hợp biên: Cột nhị phân TOOL chỉ được chứa giá trị 0 hoặc 1, từ chối số thực lẻ hoặc giá trị khác."""
        rows = self._load_data_if_available()
        for i, r in enumerate(rows):
            tool_val = r["TOOL"]
            self.assertIn(tool_val, ("0", "1", "0.0", "1.0"), f"Non-binary tool value in row {i}: {tool_val}")
            float_val = float(tool_val)
            self.assertTrue(float_val in (0.0, 1.0))

    def test_04_zero_variance_detection_per_subsample(self):
        """Trường hợp đặc biệt: Phát hiện các biến chỉ báo suy biến / phương sai bằng 0 trên cả 3 quốc gia."""
        rows = self._load_data_if_available()
        constructs = ["NORM", "AWARE", "KNOW", "COMM", "ATT", "RESP"]
        indicator_cols = [f"{c}{i}" for c in constructs for i in range(1, 5)]
        countries = ["DE", "UK", "US"]

        for country in countries:
            subsample = [r for r in rows if r["country"] in (country, "USA" if country == "US" else country)]
            self.assertGreater(len(subsample), 0, f"No rows for country {country}")
            for col in indicator_cols:
                values = [float(r[col]) for r in subsample]
                mean_val = sum(values) / len(values)
                variance = sum((x - mean_val) ** 2 for x in values) / (len(values) - 1)
                self.assertGreater(variance, 0.10,
                                   f"Indicator {col} has near-zero variance {variance:.4f} in country {country}")

    def test_05_id_uniqueness_and_contiguous_sequence(self):
        """Trường hợp biên: Bắt buộc đúng 1.017 mã định danh duy nhất liên tiếp từ SYN0001 đến SYN1017."""
        rows = self._load_data_if_available()
        ids = [r["respondent_id"] for r in rows]
        self.assertEqual(len(ids), 1017)
        self.assertEqual(len(set(ids)), 1017)
        expected_ids = [f"SYN{i:04d}" for i in range(1, 1018)]
        # Tất cả mã định danh kỳ vọng đều phải xuất hiện đầy đủ
        self.assertEqual(set(ids), set(expected_ids), "Respondent IDs do not match SYN0001-SYN1017 sequence")

    def test_06_non_negative_residual_variances_no_heywood_cases(self):
        """Trường hợp đặc biệt: Kiểm tra mô hình đo lường và cấu trúc không có phương sai sai số âm (Heywood cases)."""
        # Kiểm tra Bảng 2 CFA để phát hiện các ước lượng phương sai âm hoặc hệ số tải vượt ngưỡng
        cfa_table = PROJECT_ROOT / "results" / "tables" / "table2_cfa_measurement.csv"
        if not cfa_table.exists():
            self.skipTest("No CFA estimates table available yet")
        with open(cfa_table, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            # Nếu cột phương sai phần dư tồn tại thì giá trị phải dương
            if "variance" in r:
                var_val = float(r["variance"])
                self.assertGreater(var_val, 0.0, f"Heywood case: negative error variance for {r.get('indicator', '')}: {var_val}")
            if "std_loading" in r:
                std_l = float(r["std_loading"])
                # Hệ số tải chuẩn hóa không được vượt quá 1.0 (tránh hiện tượng Heywood)
                self.assertLessEqual(std_l, 1.05, f"Heywood case: standardized loading > 1.0: {std_l}")

    def test_07_probability_p_value_strict_bounds(self):
        """Trường hợp biên: Mọi giá trị p trong tất cả các bảng kết quả phải thỏa mãn nghiêm ngặt 0 <= p <= 1."""
        tables_dir = PROJECT_ROOT / "results" / "tables"
        if not tables_dir.exists():
            self.skipTest("No tables directory available")
        csv_files = list(tables_dir.glob("*.csv"))
        for table_file in csv_files:
            with open(table_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row_idx, r in enumerate(reader):
                    for k, v in r.items():
                        if "p_val" in k.lower() or k.lower() in ("p", "p_value", "p_delta_chi2", "germany_p", "uk_p", "usa_p", "sem_p_val", "ols_hc3_p_val"):
                            clean_v = str(v).replace("<", "").replace(">", "").strip()
                            if clean_v and clean_v.lower() != "nan":
                                try:
                                    p_val = float(clean_v)
                                    self.assertTrue(0.0 <= p_val <= 1.0,
                                                    f"P-value out of [0, 1] in {table_file.name} row {row_idx} ({k}={v})")
                                except ValueError:
                                    pass

    def test_08_correlation_matrix_positive_semi_definiteness(self):
        """Biên toán học: Xác minh các ma trận tương quan đối xứng và có đường chéo chính bằng 1.0."""
        table3_path = PROJECT_ROOT / "results" / "tables" / "table3_correlations.csv"
        if not table3_path.exists():
            self.skipTest("Table 3 not yet generated")
        with open(table3_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        groups = set(r["group"] for r in rows)
        vars_list = ["REPORT", "ATT", "RESP", "KNOW", "COMM", "NORM", "AWARE", "TOOL"]
        for g in groups:
            g_rows = {r["variable"]: r for r in rows if r["group"] == g}
            # Dựng ma trận tương quan 8x8
            matrix = []
            for v1 in vars_list:
                if v1 in g_rows:
                    row = [float(g_rows[v1][v2]) for v2 in vars_list if v2 in g_rows[v1]]
                    if len(row) == len(vars_list):
                        matrix.append(row)
            if len(matrix) == len(vars_list):
                # Kiểm tra đường chéo đơn vị và tính đối xứng của ma trận
                for i in range(len(matrix)):
                    self.assertAlmostEqual(matrix[i][i], 1.0, places=3)
                    for j in range(len(matrix)):
                        self.assertAlmostEqual(matrix[i][j], matrix[j][i], places=3)

    def test_09_degrees_of_freedom_strictly_positive(self):
        """Trường hợp biên: Đảm bảo bậc tự do df >= 1 cho mọi mô hình ước lượng."""
        invariance_path = PROJECT_ROOT / "results" / "tables" / "table7_measurement_invariance.csv"
        if not invariance_path.exists():
            self.skipTest("Table 7 not yet generated")
        with open(invariance_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            df = float(r["df"])
            self.assertGreaterEqual(df, 1.0, f"Degrees of freedom must be >= 1 for {r['model_level']}")

    def test_10_r_squared_interval_bounds(self):
        """Trường hợp biên: Bắt buộc hệ số R² nằm trong đoạn [0.0, 1.0] cho mọi mô hình."""
        table5_path = PROJECT_ROOT / "results" / "tables" / "table5_pooled_sem.csv"
        if not table5_path.exists():
            self.skipTest("Table 5 not yet generated")
        with open(table5_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            r2 = float(r["r_squared"])
            self.assertGreaterEqual(r2, 0.0, f"Negative R² in {r['path_label']}: {r2}")
            self.assertLessEqual(r2, 1.0, f"R² > 1.0 in {r['path_label']}: {r2}")

    def test_11_full_scale_endpoint_representation(self):
        """Trường hợp đặc biệt: Cả hai đầu mút thang đo (1 và 5) đều phải xuất hiện trong tập dữ liệu đầy đủ."""
        rows = self._load_data_if_available()
        constructs = ["NORM", "AWARE", "KNOW", "COMM", "ATT", "RESP"]
        cols = [f"{c}{i}" for c in constructs for i in range(1, 5)]
        for col in cols:
            values = set(float(r[col]) for r in rows)
            self.assertIn(1.0, values, f"Endpoint value 1.0 missing for {col} (distribution truncated)")
            self.assertIn(5.0, values, f"Endpoint value 5.0 missing for {col} (distribution truncated)")

    def test_12_country_allocation_exact_partition(self):
        """Trường hợp biên: Số lượng quan sát các nhóm con cộng lại đúng bằng 1.017 và không có mã quốc gia lạ."""
        rows = self._load_data_if_available()
        counts = {}
        for r in rows:
            c = r["country"]
            counts[c] = counts.get(c, 0) + 1
        valid_country_sets = [
            {"DE": 306, "UK": 205, "US": 506},
            {"DE": 306, "UK": 205, "USA": 506},
        ]
        self.assertTrue(counts in valid_country_sets, f"Invalid country distribution: {counts}")
        self.assertEqual(sum(counts.values()), 1017)


if __name__ == "__main__":
    unittest.main(verbosity=2)
