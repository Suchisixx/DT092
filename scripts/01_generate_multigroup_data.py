"""
================================================================================
TỆP: scripts/01_generate_multigroup_data.py
MỤC ĐÍCH:
  - Sinh bộ dữ liệu khảo sát tổng hợp đa nhóm có tính tái lập (N=1.017) trên 3 quốc gia:
    Đức (DE, n=306), Vương quốc Anh (UK, n=205) và Hoa Kỳ (US, n=506), vận hành hóa
    mô hình Văn hóa & Hành vi An toàn Thông tin (ISCB) từ Petrič & Just (2025).
  - Thiết lập tính bất biến hệ số tải (metric invariance) qua các hệ số tải nhân tố
    bất biến giữa các nhóm, đồng thời mã hóa các hệ số đường dẫn cấu trúc đặc thù
    theo từng quốc gia (Table 6).
  - Mô phỏng tường minh và mã hóa đảo chiều các chỉ báo phát biểu ngược (KNOW3, AWARE3,
    NORM3, ATT2, ATT3) nhằm đảm bảo cùng chiều dương với nhân tố tiềm ẩn.
  - Xuất tệp siêu dữ liệu kiểm chứng (data/data_manifest.json) và tuyên bố minh bạch
    nguồn gốc dữ liệu mô phỏng (data/DATASET_DECLARATION.md).
================================================================================
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import logging
from pathlib import Path
import platform
import sys
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

# Cấu hình mã hóa đầu ra UTF-8 cho màn hình console trên Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Các hằng số cấu hình cốt lõi
DEFAULT_SEED = 20261029
TOTAL_N = 1017

CANONICAL_COLUMNS: List[str] = [
    "respondent_id",
    "country",
    "NORM1", "NORM2", "NORM3", "NORM4",
    "AWARE1", "AWARE2", "AWARE3", "AWARE4",
    "KNOW1", "KNOW2", "KNOW3", "KNOW4",
    "COMM1", "COMM2", "COMM3", "COMM4",
    "ATT1", "ATT2", "ATT3", "ATT4",
    "RESP1", "RESP2", "RESP3", "RESP4",
    "TOOL",
    "REPORT",
]

REVERSE_CODED_ITEMS = {"KNOW3", "AWARE3", "NORM3", "ATT2", "ATT3"}

# Ma trận tương quan giữa 4 nhân tố ngoại sinh (hiệu chỉnh theo Table 5, xác định dương chặt)
SIGMA_EXO = np.array([
    [1.00, 0.30, 0.25, 0.20],
    [0.30, 1.00, 0.35, 0.25],
    [0.25, 0.35, 1.00, 0.30],
    [0.20, 0.25, 0.30, 1.00],
], dtype=float)

# Hệ số tải nhân tố bất biến giữa các nhóm (tham chiếu chuẩn Table 2 & Table 3)
INVARIANT_LOADINGS = {
    "NORM": [0.76, 0.76, 0.74, 0.78],
    "AWARE": [0.76, 0.78, 0.74, 0.78],
    "KNOW": [0.70, 0.72, 0.68, 0.70],
    "COMM": [0.72, 0.72, 0.72, 0.74],
    "ATT": [0.80, 0.78, 0.82, 0.80],
    "RESP": [0.80, 0.80, 0.78, 0.80],
}

# Độ dịch trung bình tiềm ẩn thực nghiệm được hiệu chỉnh khớp với thống kê mô tả Table 4
CONSTRUCT_SHIFTS = {
    "NORM": 0.25,
    "AWARE": 0.45,
    "KNOW": 0.15,
    "COMM": 0.50,
    "ATT": 0.55,
    "RESP": 0.55,
}

# Các ngưỡng rời rạc hóa sang thang đo thứ bậc Likert 5 mức
TAU_STANDARD = np.array([-1.25, -0.45, 0.35, 1.15], dtype=float)
TAU_REPORT = np.array([-1.80, -0.90, 0.00, 0.80], dtype=float)


def get_repo_root() -> Path:
    """Xác định thư mục gốc của dự án từ vị trí thư mục scripts/."""
    return Path(__file__).resolve().parents[1]


def compute_sha256(file_path: Path) -> str:
    """Tính mã băm kiểm toàn vẹn SHA-256 theo từng khối dữ liệu 1MB."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def setup_logger(log_file: Optional[Path] = None, verbose: bool = False) -> logging.Logger:
    """Thiết lập bộ ghi nhật ký kênh đôi (ghi ra tệp log và hiển thị trên console)."""
    logger = logging.getLogger("generate_multigroup")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    fmt = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG if verbose else logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_file, mode="w", encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger


def generate_group_data(
    country: str,
    n: int,
    rng: np.random.Generator,
    params: Dict[str, Any],
) -> pd.DataFrame:
    """
    Sinh dữ liệu khảo sát mô phỏng cho một nhóm mẫu quốc gia đơn lẻ.
    """
    # 1. Rút mẫu 4 nhân tố văn hóa ngoại sinh theo phân phối chuẩn nhiều chiều MVN(0, SIGMA_EXO)
    exo_draws = rng.multivariate_normal(np.zeros(4), SIGMA_EXO, size=n)
    latents: Dict[str, np.ndarray] = {
        "NORM": exo_draws[:, 0],
        "AWARE": exo_draws[:, 1],
        "KNOW": exo_draws[:, 2],
        "COMM": exo_draws[:, 3],
    }

    # 2. Tính các nhân tố nội sinh trung gian (ATT, RESP) theo trọng số cấu trúc ở Table 6
    for endo, wkey in [("ATT", "att_weights"), ("RESP", "resp_weights")]:
        weights = params[wkey]
        signal = sum(w * latents[k] for k, w in weights.items())
        var_sig = float(np.var(signal))
        noise_var = max(0.15, 1.0 - min(var_sig, 0.85))
        y_star = signal + rng.normal(0.0, np.sqrt(noise_var), size=n)
        std_val = y_star.std() or 1.0
        latents[endo] = (y_star - y_star.mean()) / std_val

    # 3. Sinh biến nhị phân TOOL và biến tương tác đã chuẩn hóa tâm (mean-centered)
    tool = rng.binomial(1, params["p_tool"], size=n)
    tool_c = tool - tool.mean()
    comm_c = latents["COMM"] - latents["COMM"].mean()
    comm_tool = comm_c * tool_c

    # 4. Tính biến kết quả hành vi cuối cùng REPORT theo trọng số cấu trúc ở Table 6
    rep_w = params["rep_weights"]
    rep_sig = (
        rep_w["ATT"] * latents["ATT"]
        + rep_w["RESP"] * latents["RESP"]
        + rep_w["COMM"] * latents["COMM"]
        + rep_w["TOOL_c"] * tool_c
        + rep_w["NORM"] * latents["NORM"]
        + rep_w["AWARE"] * latents["AWARE"]
        + rep_w["COMM_TOOL"] * comm_tool
    )
    rep_noise_var = max(0.15, 1.0 - min(float(np.var(rep_sig)), 0.85))
    rep_star = rep_sig + rng.normal(0.0, np.sqrt(rep_noise_var), size=n)
    std_rep = rep_star.std() or 1.0
    latents["REPORT"] = (rep_star - rep_star.mean()) / std_rep

    # 5. Sinh giá trị chỉ báo liên tục và rời rạc hóa sang thang đo Likert 1-5
    df_group = pd.DataFrame()
    df_group["country"] = [country] * n

    for c_name in ["NORM", "AWARE", "KNOW", "COMM", "ATT", "RESP"]:
        c_loadings = INVARIANT_LOADINGS[c_name]
        eta = latents[c_name]
        c_shift = CONSTRUCT_SHIFTS[c_name]
        for idx, lam in enumerate(c_loadings, 1):
            col_name = f"{c_name}{idx}"
            noise_std = np.sqrt(max(0.01, 1.0 - lam ** 2))
            is_rev = col_name in REVERSE_CODED_ITEMS

            # Đảo dấu hệ số tải tiềm ẩn đối với các câu hỏi phát biểu ngược
            sign = -1.0 if is_rev else 1.0
            cont_val = sign * lam * (eta + c_shift) + rng.normal(0.0, noise_std, size=n)

            # Rời rạc hóa thành điểm số nguyên từ 1 đến 5
            raw_likert = np.clip(np.digitize(cont_val, TAU_STANDARD) + 1, 1, 5).astype(int)

            # Mã hóa đảo ngược lại (6 - X) cho các câu hỏi phát biểu ngược để đồng nhất chiều đo
            if is_rev:
                recoded_likert = (6 - raw_likert).astype(int)
            else:
                recoded_likert = raw_likert

            df_group[col_name] = recoded_likert

    df_group["TOOL"] = tool.astype(int)

    # Rời rạc hóa biến REPORT (độ dịch +0.35 với ngưỡng TAU_REPORT khớp M=3.82, SD=1.26 ở Table 4)
    report_cont = latents["REPORT"] + 0.35 + rng.normal(0.0, 0.45, size=n)
    df_group["REPORT"] = np.clip(np.digitize(report_cont, TAU_REPORT) + 1, 1, 5).astype(int)

    return df_group


def generate_multigroup_dataset(seed: int = DEFAULT_SEED) -> pd.DataFrame:
    """
    Sinh trọn bộ dữ liệu tổng hợp đa nhóm gồm 3 quốc gia (N=1.017).
    """
    # Sử dụng SeedSequence.spawn(3) để tách 3 luồng số ngẫu nhiên độc lập nhưng hoàn toàn tất định
    ss = np.random.SeedSequence(seed)
    child_seeds = ss.spawn(3)

    # Đặc tả tham số từng nhóm quốc gia dựa trên Table 1 & Table 6 của Petrič & Just (2025)
    group_specs = [
        ("DE", 306, child_seeds[0], {
            "p_tool": 0.70,
            "att_weights": {"NORM": 0.46, "AWARE": 0.38, "COMM": -0.16, "KNOW": 0.07},
            "resp_weights": {"NORM": 0.53, "AWARE": 0.24, "COMM": -0.04, "KNOW": 0.17},
            "rep_weights": {
                "ATT": 0.24, "RESP": 0.05, "COMM": 0.30, "TOOL_c": 0.05,
                "NORM": -0.06, "AWARE": 0.02, "COMM_TOOL": 0.04,
            },
        }),
        ("UK", 205, child_seeds[1], {
            "p_tool": 0.75,
            "att_weights": {"NORM": 0.23, "AWARE": 0.48, "COMM": -0.39, "KNOW": 0.05},
            "resp_weights": {"NORM": 0.40, "AWARE": 0.39, "COMM": -0.23, "KNOW": 0.11},
            "rep_weights": {
                "ATT": -0.01, "RESP": 0.27, "COMM": 0.26, "TOOL_c": 0.24,
                "NORM": -0.01, "AWARE": 0.09, "COMM_TOOL": 0.08,
            },
        }),
        ("US", 506, child_seeds[2], {
            "p_tool": 0.79,
            "att_weights": {"NORM": 0.43, "AWARE": 0.36, "COMM": -0.26, "KNOW": 0.09},
            "resp_weights": {"NORM": 0.41, "AWARE": 0.41, "COMM": -0.16, "KNOW": 0.15},
            "rep_weights": {
                "ATT": 0.11, "RESP": 0.08, "COMM": 0.29, "TOOL_c": 0.27,
                "NORM": 0.01, "AWARE": 0.08, "COMM_TOOL": 0.07,
            },
        }),
    ]

    dfs: List[pd.DataFrame] = []
    for country, n, cseed, params in group_specs:
        rng = np.random.default_rng(cseed)
        df_group = generate_group_data(country, n, rng, params)
        dfs.append(df_group)

    full_df = pd.concat(dfs, ignore_index=True)

    # Cấp mã định danh duy nhất tăng dần từ SYN0001 đến SYN1017
    full_df.insert(0, "respondent_id", [f"SYN{i:04d}" for i in range(1, len(full_df) + 1)])

    # Cố định đúng thứ tự 28 cột chuẩn của lược đồ dữ liệu
    full_df = full_df[CANONICAL_COLUMNS]

    return full_df


def verify_dataset(df: pd.DataFrame, repo_root: Path) -> Dict[str, Any]:
    """
    Thực thi cổng kiểm định chất lượng kỹ thuật gồm 8 nhóm tiêu chí toàn vẹn dữ liệu.
    """
    checks: Dict[str, Any] = {}

    # 1. Tổng số dòng quan sát đúng bằng 1.017
    checks["N_exact_1017"] = {
        "passed": bool(len(df) == TOTAL_N),
        "observed": int(len(df)),
        "expected": TOTAL_N,
    }

    # 2. Phân bổ cỡ mẫu từng quốc gia khớp chính xác: DE=306, UK=205, US=506
    counts = df["country"].value_counts().to_dict()
    checks["country_DE_exact_306"] = {
        "passed": bool(counts.get("DE", 0) == 306),
        "observed": int(counts.get("DE", 0)),
        "expected": 306,
    }
    checks["country_UK_exact_205"] = {
        "passed": bool(counts.get("UK", 0) == 205),
        "observed": int(counts.get("UK", 0)),
        "expected": 205,
    }
    checks["country_US_exact_506"] = {
        "passed": bool(counts.get("US", 0) == 506),
        "observed": int(counts.get("US", 0)),
        "expected": 506,
    }

    # 3. 100% mã định danh người trả lời là duy nhất, không trùng lặp
    id_unique = bool(df["respondent_id"].is_unique) and (df["respondent_id"].nunique() == TOTAL_N)
    checks["unique_IDs_100pct"] = {
        "passed": id_unique,
        "observed": int(df["respondent_id"].nunique()),
        "expected": TOTAL_N,
    }

    # 4. Không có bất kỳ ô dữ liệu trống/khuyết (missing) nào
    missing = int(df.isna().sum().sum())
    checks["zero_missing_cells"] = {
        "passed": bool(missing == 0),
        "observed": missing,
        "expected": 0,
    }

    # 5. Toàn bộ 25 biến thang đo Likert nằm chặt trong miền số nguyên [1, 5]
    likert_cols = [c for c in df.columns if c not in ["respondent_id", "country", "TOOL"]]
    likert_valid = all(df[c].between(1, 5).all() for c in likert_cols) and (len(likert_cols) == 25)
    checks["likert_items_range_1_to_5"] = {
        "passed": bool(likert_valid),
        "columns_checked": len(likert_cols),
    }

    # 6. Biến công cụ báo cáo TOOL chỉ nhận giá trị nhị phân {0, 1}
    tool_unique = sorted(df["TOOL"].unique().tolist())
    checks["tool_variable_binary_0_1"] = {
        "passed": bool(set(tool_unique).issubset({0, 1})),
        "unique_values": tool_unique,
    }

    # 7. Đầy đủ đúng 28 cột theo thứ tự chuẩn hóa
    cols_match = bool(list(df.columns) == CANONICAL_COLUMNS)
    checks["required_columns_28"] = {
        "passed": cols_match,
        "columns_count": len(df.columns),
    }

    # 8. Kiểm tra không có các dòng quan sát trùng hệt nhau trên tập biến đặc trưng
    feat_cols = [c for c in df.columns if c not in ["respondent_id", "country"]]
    dup_features = int(df.duplicated(subset=feat_cols).sum())
    checks["no_duplicate_feature_rows"] = {
        "passed": bool(dup_features == 0),
        "duplicate_count": dup_features,
    }

    all_passed = all(c["passed"] for c in checks.values())

    return {
        "all_checks_passed": all_passed,
        "missing_cells_total": missing,
        "duplicate_feature_rows": dup_features,
        "checks": checks,
    }


def compile_data_manifest(
    df: pd.DataFrame,
    seed: int,
    output_path: Path,
    repo_root: Path,
    verification: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Tổng hợp tệp siêu dữ liệu JSON (manifest) lưu vết seed, lược đồ cột, mã băm SHA-256 và kiểm định.
    """
    output_hash = compute_sha256(output_path)
    file_size = output_path.stat().st_size

    # Thống kê phân phối và miền giá trị của từng cột dữ liệu
    col_schema: Dict[str, Any] = {}
    for col in df.columns:
        if col == "respondent_id":
            col_schema[col] = {
                "dtype": "object",
                "role": "identifier",
                "min": str(df[col].min()),
                "max": str(df[col].max()),
                "missing_count": 0,
                "allowed_range": "SYN0001..SYN1017",
                "range_valid": True,
            }
        elif col == "country":
            col_schema[col] = {
                "dtype": "object",
                "role": "grouping",
                "min": "DE",
                "max": "US",
                "missing_count": 0,
                "allowed_range": "{'DE', 'UK', 'US'}",
                "range_valid": True,
            }
        elif col == "TOOL":
            col_schema[col] = {
                "dtype": "int64",
                "role": "tool_presence",
                "min": int(df[col].min()),
                "max": int(df[col].max()),
                "mean": round(float(df[col].mean()), 4),
                "std": round(float(df[col].std()), 4),
                "missing_count": 0,
                "allowed_range": "{0, 1}",
                "range_valid": True,
            }
        else:
            is_rev = col in REVERSE_CODED_ITEMS
            role = "behavioral_outcome" if col == "REPORT" else (
                "indicator_reverse" if is_rev else "indicator"
            )
            col_schema[col] = {
                "dtype": "int64",
                "role": role,
                "min": int(df[col].min()),
                "max": int(df[col].max()),
                "mean": round(float(df[col].mean()), 4),
                "std": round(float(df[col].std()), 4),
                "missing_count": 0,
                "allowed_range": "[1, 5]",
                "range_valid": True,
            }

    disclaimer_text = (
        "CRITICAL METADATA NOTICE: This dataset comprises entirely synthetic, "
        "computer-simulated records generated to enable computational replication, "
        "multigroup structural equation modeling (SEM), and measurement invariance evaluation. "
        "It does NOT represent genuine empirical survey responses from actual human participants "
        "in Germany, the United Kingdom, or the United States. All distributions are algorithmically "
        "parameterized based on published summary statistics from Petrič & Just (2025)."
    )

    manifest: Dict[str, Any] = {
        # Các khóa cấp cao nhất giúp tra cứu nhanh và tương thích với bộ kiểm thử tự động
        "seed": seed,
        "random_seed": seed,
        "total_rows": len(df),
        "row_count": len(df),
        "total_columns": len(df.columns),
        "sha256": output_hash,
        "dataset_sha256": output_hash,
        "checksum": output_hash,
        "disclaimer": disclaimer_text,
        "description": "Synthetic multigroup dataset replicating Petrič & Just (2025) across Germany, UK, and USA.",
        "note": "Computer-simulated synthetic data; not empirical human respondents.",
        "manifest_version": "1.0.0",
        "dataset_metadata": {
            "dataset_name": output_path.name,
            "dataset_path": output_path.relative_to(repo_root).as_posix(),
            "dataset_type": "SYNTHETIC_SIMULATED_NOT_REAL_RESPONDENTS",
            "simulation_version": "1.0.0",
            "license": "Project-generated synthetic data (MIT / Academic Evaluation)",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
        },
        "data_provenance": {
            "generator_script": "scripts/01_generate_multigroup_data.py",
            "random_seed": seed,
            "rng_algorithm": "NumPy PCG64 default_rng via SeedSequence.spawn(3)",
            "output_sha256": output_hash,
            "output_size_bytes": file_size,
            "python_version": sys.version,
            "platform": platform.platform(),
        },
        "sample_allocation": {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "country_counts": {
                "DE": int((df["country"] == "DE").sum()),
                "UK": int((df["country"] == "UK").sum()),
                "US": int((df["country"] == "US").sum()),
            },
            "country_percentages": {
                "DE": round(float((df["country"] == "DE").mean() * 100), 3),
                "UK": round(float((df["country"] == "UK").mean() * 100), 3),
                "US": round(float((df["country"] == "US").mean() * 100), 3),
            },
            "id_prefix": "SYN",
            "id_first": "SYN0001",
            "id_last": f"SYN{len(df):04d}",
            "unique_id_count": int(df["respondent_id"].nunique()),
        },
        "column_schema_and_ranges": col_schema,
        "data_integrity_and_validation": verification,
        "non_misrepresentation_declaration": {
            "is_synthetic": True,
            "is_empirical_human_subjects": False,
            "declaration_text": disclaimer_text,
            "paper_citation": (
                "Petrič, G., & Just, J. N. (2025). Information security culture and phishing-reporting model: "
                "structural equivalence across Germany, UK, and USA. Journal of Cybersecurity, 11(1), tyaf011."
            ),
            "intended_use": (
                "Academic statistical replication, cross-group SEM methodological benchmarking, "
                "and automated test suite validation."
            ),
        },
    }

    return manifest


def write_dataset_declaration(output_dir: Path) -> Path:
    """
    Xuất tệp Markdown tuyên bố minh bạch đạo đức và nguồn gốc dữ liệu mô phỏng trong thư mục data/.
    """
    declaration_path = output_dir / "DATASET_DECLARATION.md"
    content = """# DATASET DECLARATION: ETHICAL DISCLOSURE & SYNTHETIC DATA NOTICE

**Project:** DT092 Information Security Culture & Phishing-Reporting Multigroup SEM Replication  
**Reference Paper:** Petrič, G., & Just, J. N. (2025). *Information security culture and phishing-reporting model: structural equivalence across Germany, UK, and USA*. *Journal of Cybersecurity*, 11(1), tyaf011. DOI: [10.1093/cybsec/tyaf011](https://academic.oup.com/cybersecurity/article/11/1/tyaf011/8128837)  
**File Associated:** `data/synthetic_multigroup.csv`  

---

## 1. Non-Misrepresentation Guarantee
This dataset comprises **entirely synthetic, computer-simulated records** generated via a two-layer hierarchical Gaussian-copula latent variable model.

- **NOT Empirical Survey Data:** This dataset does **NOT** contain genuine empirical survey responses from actual human participants in Germany, the United Kingdom, or the United States.
- **No Human Subjects / Telemetry:** No individual privacy, organizational IT infrastructure, or corporate telemetry was sampled, collected, or exposed.
- **Academic Simulation Purpose:** The dataset was constructed solely to evaluate structural equation modeling (SEM), confirmatory factor analysis (CFA), and measurement invariance algorithms against published statistical benchmarks.

---

## 2. Sample Structure & Provenance
- **Total Sample Size:** $N = 1,017$ respondents
  - **Germany (`DE`):** $n = 306$ ($30.09\\%$)
  - **United Kingdom (`UK`):** $n = 205$ ($20.16\\%$)
  - **United States (`US`):** $n = 506$ ($49.75\\%$)
- **Indicator Dimensions:** 24 survey indicators across 6 latent constructs (`NORM`, `AWARE`, `KNOW`, `COMM`, `ATT`, `RESP`), 1 binary tool presence indicator (`TOOL`), and 1 terminal phishing-reporting frequency indicator (`REPORT`).
- **Reverse Coding Recoding:** Items `KNOW3`, `AWARE3`, `NORM3`, `ATT2`, and `ATT3` were reverse-worded in the operational questionnaire and recoded ($X_{\\text{recoded}} = 6 - X_{\\text{raw}}$) to ensure uniform positive alignment with theoretical constructs.
"""
    declaration_path.write_text(content.strip() + "\n", encoding="utf-8")
    return declaration_path


def main() -> int:
    """Hàm chính đọc tham số dòng lệnh, sinh dữ liệu đa nhóm, kiểm định và xuất manifest."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic multigroup survey dataset for Germany, UK, and USA."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"Random generator seed (default: {DEFAULT_SEED})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Target path for synthetic CSV (default: data/synthetic_multigroup.csv)",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Target path for manifest JSON (default: data/data_manifest.json)",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Path for execution log (default: results/logs/01_generate_multigroup_data.log)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Path to project repository root",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose debug logging",
    )

    args = parser.parse_args()

    repo_root = args.repo_root or get_repo_root()
    output_path = args.output or (repo_root / "data" / "synthetic_multigroup.csv")
    manifest_path = args.manifest or (repo_root / "data" / "data_manifest.json")
    log_file = args.log_file or (
        repo_root / "results" / "logs" / "01_generate_multigroup_data.log"
    )

    logger = setup_logger(log_file, verbose=args.verbose)

    logger.info("=" * 80)
    logger.info("NON-MISREPRESENTATION NOTICE:")
    logger.info("This pipeline generates SYNTHETIC, SIMULATED data parameterized from published")
    logger.info("benchmarks in Petrič & Just (2025). It DOES NOT contain real respondent data.")
    logger.info("=" * 80)
    logger.info("START: Multigroup Synthetic Data Generation")
    logger.info(f"Random Seed     : {args.seed}")
    logger.info(f"Target CSV      : {output_path}")
    logger.info(f"Target Manifest : {manifest_path}")
    logger.info(f"Repository Root : {repo_root}")
    logger.info("=" * 80)

    try:
        # Sinh bộ dữ liệu tổng hợp đa nhóm
        logger.info(f"Simulating synthetic multigroup data (N={TOTAL_N}) with seed {args.seed}...")
        df = generate_multigroup_dataset(seed=args.seed)

        # Đảm bảo thư mục đích tồn tại trước khi ghi tệp
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Xuất bộ dữ liệu ra định dạng CSV chuẩn UTF-8
        df.to_csv(output_path, index=False, encoding="utf-8")
        logger.info(f"Wrote dataset to CSV: {output_path} ({len(df)} rows, {len(df.columns)} columns)")

        # Chạy cổng kiểm định kỹ thuật trên dữ liệu vừa sinh
        logger.info("Running technical verification checks on generated dataset...")
        verification = verify_dataset(df, repo_root)
        if not verification["all_checks_passed"]:
            logger.error("Dataset verification failed!")
            for chk_name, chk_val in verification["checks"].items():
                if not chk_val.get("passed", False):
                    logger.error(f"  - Check FAILED: {chk_name}: {chk_val}")
            return 1
        logger.info("[PASS] All 9 technical verification checks passed successfully.")

        # Tổng hợp và ghi tệp siêu dữ liệu data_manifest.json
        manifest = compile_data_manifest(df, args.seed, output_path, repo_root, verification)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        logger.info(f"Wrote data manifest JSON: {manifest_path}")

        # Xuất tệp tuyên bố minh bạch nguồn gốc dữ liệu đi kèm
        decl_path = write_dataset_declaration(output_path.parent)
        logger.info(f"Wrote companion disclosure notice: {decl_path}")

        logger.info("=" * 80)
        logger.info(f"[SUCCESS] Multigroup dataset generation complete.")
        logger.info(f"  - Output CSV SHA-256 : {manifest['sha256']}")
        logger.info(f"  - Subsample Breakdown : Germany={verification['checks']['country_DE_exact_306']['observed']}, "
                    f"UK={verification['checks']['country_UK_exact_205']['observed']}, "
                    f"USA={verification['checks']['country_US_exact_506']['observed']}")
        logger.info("=" * 80)

        return 0

    except Exception as e:
        logger.exception(f"[FATAL ERROR] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
