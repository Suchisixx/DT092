"""
00_run_pipeline.py

Trình điều phối chạy trọn gói từ đầu đến cuối có tính tất định (deterministic) cho thực nghiệm
SEM Đa nhóm & Kiểm định Tính bất biến Đo lường của dự án DT092 (Germany N=306, UK N=205,
USA N=506; Tổng N=1.017) theo cấu trúc nghiên cứu của Petrič & Just (2025).

Thực thi tuần tự toàn bộ 5 giai đoạn từ bước sinh dữ liệu đến bước kiểm toán độc lập
và xác nhận khả năng tái lập chính xác tuyệt đối về mặt số học.
"""

from __future__ import annotations

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import os
import subprocess
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
VENV_SITE = REPO_ROOT / ".venv" / "Lib" / "site-packages"

PIPELINE_STEPS = [
    ("Stage 1: Multigroup Synthetic Data Generation", ["scripts/01_generate_multigroup_data.py", "--seed", "20261029"]),
    ("Stage 2: CFA, Reliability & Descriptives (Tables 1-4)", ["scripts/02_cfa_and_descriptives.py"]),
    ("Stage 3: Pooled/Multigroup SEM & Invariance (Tables 5-7)", ["scripts/03_multigroup_sem_invariance.py"]),
    ("Stage 4: Hypotheses, OLS-HC3/5-Seed Robustness & Paper Comparison (Tables 8-9)", ["scripts/04_hypothesis_and_robustness.py"]),
    ("Stage 5: Automated Forensic Verification Gate", ["scripts/05_verify_all.py"]),
]


def main() -> None:
    """Thiết lập môi trường Python (.venv) và kích hoạt tuần tự 5 giai đoạn của pipeline."""
    env = os.environ.copy()
    existing_pp = env.get("PYTHONPATH", "")
    if VENV_SITE.exists():
        env["PYTHONPATH"] = f"{VENV_SITE}{os.pathsep}{existing_pp}" if existing_pp else str(VENV_SITE)
    env["PYTHONIOENCODING"] = "utf-8"

    print("================================================================================")
    print(" DT092 MULTIGROUP SEM & MEASUREMENT INVARIANCE — FULL PIPELINE EXECUTION")
    print("================================================================================")
    t0 = time.perf_counter()

    for label, cmd_args in PIPELINE_STEPS:
        step_t0 = time.perf_counter()
        print(f"\n>>> Running {label}: {' '.join(cmd_args)}")
        res = subprocess.run(
            [sys.executable, *cmd_args],
            cwd=str(REPO_ROOT),
            env=env,
            text=True,
        )
        dt = time.perf_counter() - step_t0
        if res.returncode != 0:
            print(f"[FAIL] {label} exited with code {res.returncode} after {dt:.2f}s")
            sys.exit(res.returncode)
        print(f"[OK] {label} completed in {dt:.2f}s")

    total_dt = time.perf_counter() - t0
    print("\n================================================================================")
    print(f" ALL 5 MULTIGROUP PIPELINE STAGES SUCCEEDED IN {total_dt:.2f}s")
    print("================================================================================")


if __name__ == "__main__":
    main()
