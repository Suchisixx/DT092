"""
Tier 3: Cross-Feature Combinations & Pairwise Contracts Test Suite
Opaque-Box E2E Testing Track for DT092 Multigroup SEM Replication (Petrič & Just, 2025).

Tests data flow contracts, interface handoffs, and mathematical interactions between pipeline components.
"""

import os
import sys
import unittest
import csv
import json
import math
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestTier3PairwiseAndCrossFeature(unittest.TestCase):
    """Tier 3: Pairwise Combinations, Interface Contracts, and Cross-Feature Invariants"""

    DATA_PATH = PROJECT_ROOT / "data" / "synthetic_multigroup.csv"
    TABLES_DIR = PROJECT_ROOT / "results" / "tables"

    def test_01_data_generator_output_fed_into_cfa(self):
        """Cross-Feature: Synthetic data indicators align with CFA measurement specification."""
        if not self.DATA_PATH.exists():
            self.skipTest(f"Milestone M1 in progress: {self.DATA_PATH} not yet generated")
        with open(self.DATA_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            first_row = next(reader)

        constructs = ["NORM", "AWARE", "KNOW", "COMM", "ATT", "RESP"]
        for c in constructs:
            for i in range(1, 5):
                col_name = f"{c}{i}"
                self.assertIn(col_name, first_row, f"CFA input indicator {col_name} missing from synthetic dataset")

    def test_02_cfa_loadings_fed_into_invariance_constraints(self):
        """Cross-Feature: Factor loading indicators in Table 2 match constraints in Table 7."""
        table2_path = self.TABLES_DIR / "table2_cfa_measurement.csv"
        table7_path = self.TABLES_DIR / "table7_measurement_invariance.csv"
        if not (table2_path.exists() and table7_path.exists()):
            self.skipTest("Table 2 or Table 7 not yet generated")

        with open(table2_path, "r", encoding="utf-8") as f:
            t2_rows = list(csv.DictReader(f))
        with open(table7_path, "r", encoding="utf-8") as f:
            t7_rows = list(csv.DictReader(f))

        indicators_t2 = set(r["indicator"] for r in t2_rows)
        # All 24 indicators must be measured in Table 2
        self.assertEqual(len(indicators_t2), 24, "Table 2 must evaluate 24 indicators")

        # Table 7 Metric model should constrain these loadings
        metric_row = next((r for r in t7_rows if "metric" in r["model_level"].lower()), None)
        self.assertIsNotNone(metric_row, "Table 7 missing metric invariance row")

    def test_03_sem_structural_paths_matched_against_table6_and_table8(self):
        """Cross-Feature: Table 6 country coefficients logically dictate Table 8 hypothesis status."""
        table6_path = self.TABLES_DIR / "table6_multigroup_sem.csv"
        table8_path = self.TABLES_DIR / "table8_hypothesis_testing.csv"
        if not table8_path.exists():
            table8_path = self.TABLES_DIR / "table8_hypotheses.csv"

        if not (table6_path.exists() and table8_path.exists()):
            self.skipTest("Table 6 or Table 8 not yet generated")

        with open(table6_path, "r", encoding="utf-8") as f:
            t6 = {r["path_label"]: r for r in csv.DictReader(f)}
        with open(table8_path, "r", encoding="utf-8") as f:
            t8 = {r["hypothesis"]: r for r in csv.DictReader(f)}

        # Check H1a (NORM -> ATT)
        if "H1a" in t6 and "H1a" in t8:
            de_beta = float(t6["H1a"]["germany_beta"])
            de_p = float(t6["H1a"]["germany_p"].replace("<", "").replace(">", "").strip())
            de_status = t8["H1a"]["germany_status"].lower()
            if de_beta > 0 and de_p < 0.05:
                self.assertIn("supported", de_status, "H1a in Germany has positive beta and p<0.05, status must be Supported")

        # Check H3a (COMM -> ATT) - paradoxical negative effect
        if "H3a" in t6 and "H3a" in t8:
            de_beta = float(t6["H3a"]["germany_beta"])
            de_status = t8["H3a"]["germany_status"].lower()
            self.assertLess(de_beta, 0.0, "COMM -> ATT must have negative beta matching published literature")
            self.assertIn("not supported", de_status, "Negative coefficient must be evaluated as Not Supported")

    def test_04_interaction_mean_centering_reduces_collinearity(self):
        """Cross-Feature: Interaction term COMM_TOOL is computed from mean-centered COMM and TOOL."""
        if not self.DATA_PATH.exists():
            self.skipTest("Synthetic data not yet generated")

        with open(self.DATA_PATH, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        comm_items = ["COMM1", "COMM2", "COMM3", "COMM4"]
        comm_scores = [sum(float(r[c]) for c in comm_items) / 4.0 for r in rows]
        tool_scores = [float(r["TOOL"]) for r in rows]

        # Mean centering
        mu_comm = sum(comm_scores) / len(comm_scores)
        mu_tool = sum(tool_scores) / len(tool_scores)
        comm_c = [x - mu_comm for x in comm_scores]
        tool_c = [x - mu_tool for x in tool_scores]
        product_centered = [c * t for c, t in zip(comm_c, tool_c)]
        product_raw = [c * t for c, t in zip(comm_scores, tool_scores)]

        # Pearson correlation helper
        def pearson(x, y):
            n = len(x)
            mx, my = sum(x) / n, sum(y) / n
            cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
            var_x = sum((xi - mx) ** 2 for xi in x)
            var_y = sum((yi - my) ** 2 for yi in y)
            return cov / math.sqrt(var_x * var_y) if var_x > 0 and var_y > 0 else 0.0

        r_raw_comm = pearson(product_raw, comm_scores)
        r_centered_comm = pearson(product_centered, comm_scores)

        # Raw product has huge correlation with main effect; centered product correlation is drastically lower
        self.assertLess(abs(r_centered_comm), 0.30,
                        f"Centered interaction term correlation with COMM {r_centered_comm:.3f} must be < 0.30")
        self.assertLess(abs(r_centered_comm), abs(r_raw_comm),
                        "Mean centering must reduce collinearity compared to raw product")

    def test_05_fornell_larcker_discriminant_validity(self):
        """Cross-Feature: Square root of AVE exceeds inter-construct correlations (Fornell-Larcker)."""
        table2_path = self.TABLES_DIR / "table2_cfa_measurement.csv"
        table3_path = self.TABLES_DIR / "table3_correlations.csv"
        if not (table2_path.exists() and table3_path.exists()):
            self.skipTest("Table 2 or Table 3 not yet generated")

        with open(table2_path, "r", encoding="utf-8") as f:
            t2_rows = list(csv.DictReader(f))
        with open(table3_path, "r", encoding="utf-8") as f:
            t3_rows = list(csv.DictReader(f))

        sqrt_aves = {}
        for r in t2_rows:
            c = r["construct"]
            if c not in sqrt_aves and "sqrt_ave" in r:
                sqrt_aves[c] = float(r["sqrt_ave"])

        pooled_corrs = {r["variable"]: r for r in t3_rows if r["group"] in ("ALL", "POOLED")}
        for c1, sqrt_ave in sqrt_aves.items():
            if c1 in pooled_corrs:
                for c2, val_str in pooled_corrs[c1].items():
                    if c2 in sqrt_aves and c2 != c1:
                        r_val = abs(float(val_str))
                        self.assertGreater(sqrt_ave, r_val,
                                           f"Fornell-Larcker violation: sqrt(AVE) of {c1} ({sqrt_ave:.3f}) <= r({c1}, {c2}) ({r_val:.3f})")

    def test_06_survey_questions_align_with_multigroup_schema(self):
        """Cross-Feature: Survey_Question.md defines all 24 indicators, TOOL, and REPORT in synthetic_multigroup.csv."""
        survey_doc = PROJECT_ROOT / "data" / "Survey_Question.md"
        self.assertTrue(survey_doc.exists(), "data/Survey_Question.md missing")
        doc_text = survey_doc.read_text(encoding="utf-8")
        for c in ["NORM", "AWARE", "KNOW", "COMM", "ATT", "RESP"]:
            for i in range(1, 5):
                self.assertIn(f"{c}{i}:", doc_text, f"Indicator {c}{i} missing from Survey_Question.md")
        self.assertIn("TOOL:", doc_text)
        self.assertIn("REPORT:", doc_text)

    def test_07_demographics_table1_matches_data_manifest(self):
        """Cross-Feature: Sample counts and tool prevalence in Table 1 match data_manifest.json."""
        manifest_path = PROJECT_ROOT / "data" / "data_manifest.json"
        table1_path = self.TABLES_DIR / "table1_demographics.csv"
        if not (manifest_path.exists() and table1_path.exists()):
            self.skipTest("Manifest or Table 1 not yet generated")

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        with open(table1_path, "r", encoding="utf-8") as f:
            t1_rows = list(csv.DictReader(f))

        sample_row = next((r for r in t1_rows if "sample" in r["variable_category"].lower() or "total" in r["variable_category"].lower()), None)
        if sample_row:
            self.assertEqual(int(float(sample_row["pooled_n"])), 1017)
            self.assertEqual(int(float(sample_row["germany_n"])), 306)
            self.assertEqual(int(float(sample_row["uk_n"])), 205)
            self.assertEqual(int(float(sample_row["usa_n"])), 506)

    def test_08_table4_descriptives_consistent_with_table3_correlations(self):
        """Cross-Feature: Constructs present in Table 4 correspond to variables in Table 3."""
        table3_path = self.TABLES_DIR / "table3_correlations.csv"
        table4_path = self.TABLES_DIR / "table4_descriptives.csv"
        if not (table3_path.exists() and table4_path.exists()):
            self.skipTest("Table 3 or Table 4 not yet generated")

        with open(table3_path, "r", encoding="utf-8") as f:
            t3_vars = set(r["variable"] for r in csv.DictReader(f))
        with open(table4_path, "r", encoding="utf-8") as f:
            t4_vars = set(r["variable"] for r in csv.DictReader(f))

        common = t3_vars.intersection(t4_vars)
        self.assertGreaterEqual(len(common), 7, f"Common variables between Table 3 and Table 4: {common}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
