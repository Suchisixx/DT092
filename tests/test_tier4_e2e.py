"""
Tầng 4: Bộ kiểm thử kịch bản thực tế & tích hợp toàn bộ pipeline (Full Pipeline Integration)
Luồng kiểm thử hộp đen E2E cho thí nghiệm tái tạo SEM đa nhóm DT092 (Petrič & Just, 2025).

Kiểm tra tính đầy đủ của các sản phẩm đầu ra, hợp đồng thực thi đầu-cuối, tính tất định và tính toàn vẹn hệ thống.
"""

import os
import sys
import unittest
import csv
import json
import hashlib
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestTier4RealWorldScenariosAndIntegration(unittest.TestCase):
    """Tầng 4: Tích hợp toàn trình pipeline, kiểm toán sản phẩm đầu ra và xác minh khả năng tái lập"""

    TABLES_DIR = PROJECT_ROOT / "results" / "tables"
    REPORTS_DIR = PROJECT_ROOT / "reports"
    DATA_DIR = PROJECT_ROOT / "data"

    def test_01_full_deliverable_table_inventory(self):
        """Kịch bản: Đủ 18 bảng CSV đầu ra chuẩn tồn tại và không còn bất kỳ tệp CSV trùng lặp nào."""
        if not self.TABLES_DIR.exists():
            self.skipTest(f"Pipeline tables directory {self.TABLES_DIR} not yet generated")

        expected_tables = {
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
        }

        found_files = {f.name for f in self.TABLES_DIR.glob("*.csv")}
        self.assertEqual(found_files, expected_tables,
                         f"Mismatch in results/tables/: missing={expected_tables - found_files}, extra={found_files - expected_tables}")

    def test_02_full_deliverable_report_inventory(self):
        """Kịch bản: Cả 3 báo cáo tổng hợp Markdown đều tồn tại và có nội dung đầy đủ."""
        if not self.REPORTS_DIR.exists():
            self.skipTest(f"Pipeline reports directory {self.REPORTS_DIR} not yet generated")

        expected_reports = [
            "results_summary.md",
            "methodology_and_assumptions.md",
            "limitations.md",
        ]
        for rep in expected_reports:
            rep_path = self.REPORTS_DIR / rep
            self.assertTrue(rep_path.exists(), f"Deliverable report missing: {rep}")
            self.assertGreater(rep_path.stat().st_size, 500, f"Report {rep} is unexpectedly small")

    def test_03_automated_verification_script_execution(self):
        """Kịch bản: Thực thi trực tiếp scripts/05_verify_all.py và xác nhận mã thoát bằng 0."""
        verify_script = PROJECT_ROOT / "scripts" / "05_verify_all.py"
        self.assertTrue(verify_script.exists(), f"Verification script missing: {verify_script}")

        python_exe = sys.executable
        res = subprocess.run([python_exe, str(verify_script)], capture_output=True, text=True, cwd=str(PROJECT_ROOT))
        self.assertEqual(res.returncode, 0,
                         f"Verification script failed with exit code {res.returncode}.\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}")

    def test_04_pipeline_reproducibility_and_checksum_stability(self):
        """Kịch bản: Xác minh mã băm SHA-256 trong data_manifest.json khớp tuyệt đối với tập dữ liệu hiện tại."""
        manifest_path = self.DATA_DIR / "data_manifest.json"
        dataset_path = self.DATA_DIR / "synthetic_multigroup.csv"
        if not (manifest_path.exists() and dataset_path.exists()):
            self.skipTest("Synthetic data or manifest not yet generated")

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        manifest_sha = manifest.get("sha256") or manifest.get("dataset_sha256") or manifest.get("checksum")

        with open(dataset_path, "rb") as f:
            current_sha = hashlib.sha256(f.read()).hexdigest()

        self.assertEqual(manifest_sha.lower(), current_sha.lower(),
                         "Synthetic dataset has diverged from recorded manifest checksum!")

    def test_05_workspace_cleanliness_and_boundary_isolation(self):
        """Kịch bản: Xác minh không còn thư mục cũ hoặc tệp CSV rác nằm ở thư mục gốc hay thư mục tests/."""
        root_csvs = list(PROJECT_ROOT.glob("*.csv"))
        self.assertEqual(len(root_csvs), 0, f"Leaked CSV files in project root: {[f.name for f in root_csvs]}")

        test_dir = PROJECT_ROOT / "tests"
        test_csvs = list(test_dir.glob("*.csv"))
        self.assertEqual(len(test_csvs), 0, f"Leaked CSV files in tests directory: {[f.name for f in test_csvs]}")

        for legacy in ["artifacts", "config", "report", ".agents", "TEST_READY.md"]:
            self.assertFalse((PROJECT_ROOT / legacy).exists(), f"Legacy path still present: {legacy}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
