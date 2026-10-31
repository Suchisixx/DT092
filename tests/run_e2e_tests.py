"""
Trình chạy kiểm thử độc lập cho bộ kiểm thử hộp đen đầu-cuối (Opaque-Box E2E) dự án DT092 Multigroup SEM.
Thực thi từ Tầng 1 đến Tầng 4, tổng hợp kết quả và hiển thị báo cáo trạng thái định dạng chuẩn.

Cách sử dụng:
    python tests/run_e2e_tests.py
    python tests/run_e2e_tests.py --tier 1
    python tests/run_e2e_tests.py --verbose
"""

import os
import sys
import time
import unittest
import argparse
from pathlib import Path

# Đảm bảo stdout và stderr xử lý mã hóa UTF-8 an toàn trên Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Đảm bảo thư mục gốc của dự án nằm trong sys.path
TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


TIERS = {
    1: ("Tier 1: Feature Coverage (F01-F19)", "test_tier1_feature_coverage"),
    2: ("Tier 2: Boundary & Corner Cases", "test_tier2_boundaries"),
    3: ("Tier 3: Pairwise & Cross-Feature Contracts", "test_tier3_pairwise"),
    4: ("Tier 4: Real-World Scenarios & Full Pipeline", "test_tier4_e2e"),
}


class TierResultTracker:
    def __init__(self, tier_num, tier_title):
        self.tier_num = tier_num
        self.tier_title = tier_title
        self.total = 0
        self.passed = 0
        self.skipped = 0
        self.failed = 0
        self.errors = 0
        self.duration = 0.0


def run_tier(tier_num, verbose=False):
    tier_title, module_name = TIERS[tier_num]
    tracker = TierResultTracker(tier_num, tier_title)

    loader = unittest.TestLoader()
    try:
        suite = loader.loadTestsFromName(f"tests.{module_name}")
    except Exception as e:
        print(f"Error loading {module_name}: {e}")
        tracker.errors = 1
        return tracker, unittest.TestResult()

    tracker.total = suite.countTestCases()

    start_time = time.time()
    stream = sys.stdout if verbose else None
    runner = unittest.TextTestRunner(stream=stream, verbosity=2 if verbose else 0)
    result = runner.run(suite)
    tracker.duration = time.time() - start_time

    tracker.failed = len(result.failures)
    tracker.errors = len(result.errors)
    tracker.skipped = len(result.skipped)
    tracker.passed = tracker.total - (tracker.failed + tracker.errors + tracker.skipped)

    return tracker, result


def main():
    parser = argparse.ArgumentParser(description="Run DT092 Multigroup SEM Opaque-Box E2E Test Suite")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3, 4], help="Run only specific tier (1, 2, 3, or 4)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose test execution output")
    args = parser.parse_args()

    selected_tiers = [args.tier] if args.tier else [1, 2, 3, 4]

    print("=" * 80)
    print(" DT092 MULTIGROUP SEM REPLICATION -- OPAQUE-BOX E2E TEST RUNNER")
    print(" Target Reference: Petric & Just (2025) | Project: DT092_Phishing_Culture")
    print(f" Time: {time.strftime('%Y-%m-%d %H:%M:%SZ', time.gmtime())}")
    print("=" * 80)

    trackers = []
    all_failures = []
    all_errors = []

    for t_num in selected_tiers:
        title, mod = TIERS[t_num]
        print(f"\n>> Executing {title}...")
        tracker, result = run_tier(t_num, verbose=args.verbose)
        trackers.append(tracker)

        status_str = "PASS" if tracker.failed == 0 and tracker.errors == 0 else "FAIL"
        print(f"  [{status_str}] Total: {tracker.total:2d} | Passed: {tracker.passed:2d} | Skipped: {tracker.skipped:2d} | Failed: {tracker.failed:2d} | Errors: {tracker.errors:2d} ({tracker.duration:.2f}s)")

        for test, trace in result.failures:
            all_failures.append((title, str(test), trace))
        for test, trace in result.errors:
            all_errors.append((title, str(test), trace))

    # In bảng tóm tắt kết quả kiểm thử
    print("\n" + "=" * 80)
    print(" E2E TEST EXECUTION SUMMARY")
    print("=" * 80)
    print(f" {'Tier':<42} {'Total':>7} {'Pass':>7} {'Skip':>7} {'Fail':>7} {'Error':>7}")
    print("-" * 80)

    grand_total = grand_passed = grand_skipped = grand_failed = grand_errors = 0
    total_duration = 0.0

    for t in trackers:
        print(f" {t.tier_title:<42} {t.total:>7} {t.passed:>7} {t.skipped:>7} {t.failed:>7} {t.errors:>7}")
        grand_total += t.total
        grand_passed += t.passed
        grand_skipped += t.skipped
        grand_failed += t.failed
        grand_errors += t.errors
        total_duration += t.duration

    print("-" * 80)
    print(f" {'TOTAL':<42} {grand_total:>7} {grand_passed:>7} {grand_skipped:>7} {grand_failed:>7} {grand_errors:>7}")
    print("=" * 80)
    print(f" Total Runtime: {total_duration:.2f} seconds")

    if all_failures or all_errors:
        print("\n" + "!" * 80)
        print(" TEST FAILURES / ERRORS DETAILS")
        print("!" * 80)
        for tier_title, test_name, trace in all_failures:
            print(f"\n[FAILURE] in {tier_title} :: {test_name}")
            print(trace)
        for tier_title, test_name, trace in all_errors:
            print(f"\n[ERROR] in {tier_title} :: {test_name}")
            print(trace)
        print("!" * 80)
        sys.exit(1)
    else:
        print("\n[OK] All active test assertions passed cleanly. Suite status: HEALTHY")
        sys.exit(0)


if __name__ == "__main__":
    main()
