"""
================================================================================
TÊN FILE: scripts/10_repeated_runs_and_cv.py
MỤC TIÊU:
  - Đáp ứng yêu cầu thực nghiệm nâng cao của đề bài:
    (1) Chạy lặp trên 5 hạt giống ngẫu nhiên độc lập (5 Seeds: `20261016`..`20261020`)
        để đánh giá độ ổn định (Stability) của các hệ số đường dẫn và chỉ số Fit.
    (2) Phân tích Ablation trên 3 biến thể cấu trúc (`M1_Mediation_Only`,
        `M2_Full_Direct_Paths`, `M3_Full_With_Interaction`).
    (3) Thực hiện 5-Fold Cross-Validation chống rò rỉ dữ liệu (`Train-Test Leakage
        Prevention`: chỉ tính trung bình chuẩn hóa tâm và ước lượng tham số trên
        tập `train`, sau đó dự báo trên tập `test`) với bộ đa chỉ số (`Out-of-sample R2`,
        `RMSE`, `MAE`, `Spearman rho`).
    (4) Phân tích lỗi và phần dư (Error / Residual Analysis) theo từng mức Likert 1–5
        và trích xuất 10 bản ghi có sai số dự báo lớn nhất.
QUY TRÌNH THỰC HIỆN (TỪNG BƯỚC):
  - Bước 1: Chạy vòng lặp 5 seeds độc lập, lưu kết quả thô và bảng tổng hợp Mean/SD.
  - Bước 2: Chạy so sánh Ablation 3 mô hình SEM (`M1`, `M2`, `M3`).
  - Bước 3: Chia 5-Fold CV không rò rỉ dữ liệu, tính chỉ số dự báo ngoài mẫu.
  - Bước 4: Tổng hợp bảng phân tích lỗi theo bậc Likert và ghi nhật ký tiếng Việt.
ĐẦU VÀO (INPUT):
  - `config/model_config.yml`
  - `data/simulated/synthetic_sem.csv`
ĐẦU RA (OUTPUT):
  - Độ ổn định 5 seeds: `artifacts/repeated_runs/multiseed_stability_summary.csv`,
                        `artifacts/repeated_runs/multiseed_raw_paths.csv`,
                        `artifacts/repeated_runs/multiseed_fit_indices.csv`
  - Ablation 3 mô hình: `artifacts/repeated_runs/ablation_model_comparison.csv`
  - 5-Fold CV: `artifacts/repeated_runs/cv_5fold_summary.csv`, `cv_5fold_raw.csv`
  - Phân tích lỗi: `artifacts/repeated_runs/residual_error_by_report_level.csv`,
                   `artifacts/repeated_runs/top10_largest_errors.csv`
  - Nhật ký: `results/logs/10_do_on_dinh_5seeds_va_5fold_cv.log`
================================================================================
"""

from pathlib import Path
import sys
import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from scipy.stats import spearmanr
from semopy import Model, calc_stats
import statsmodels.api as sm
import yaml

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config" / "model_config.yml"
DATA_PATH = ROOT / "data" / "simulated" / "synthetic_sem.csv"
OUT_DIR = ROOT / "artifacts" / "repeated_runs"
LOG_DIR = ROOT / "results" / "logs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

SEEDS = [20261016, 20261017, 20261018, 20261019, 20261020]

SEM_SYNTAX_INTERACTION = """
NORM =~ NORM1 + NORM2 + NORM3 + NORM4
AWARE =~ AWARE1 + AWARE2 + AWARE3 + AWARE4
KNOW =~ KNOW1 + KNOW2 + KNOW3 + KNOW4
COMM =~ COMM1 + COMM2 + COMM3 + COMM4
ATT =~ ATT1 + ATT2 + ATT3 + ATT4
RESP =~ RESP1 + RESP2 + RESP3 + RESP4

ATT ~ NORM + AWARE + COMM + KNOW
RESP ~ NORM + AWARE + COMM + KNOW
REPORT ~ NORM + AWARE + COMM + ATT + RESP + TOOL + COMM_TOOL
"""

SEM_SYNTAX_MEDIATION_ONLY = """
NORM =~ NORM1 + NORM2 + NORM3 + NORM4
AWARE =~ AWARE1 + AWARE2 + AWARE3 + AWARE4
KNOW =~ KNOW1 + KNOW2 + KNOW3 + KNOW4
COMM =~ COMM1 + COMM2 + COMM3 + COMM4
ATT =~ ATT1 + ATT2 + ATT3 + ATT4
RESP =~ RESP1 + RESP2 + RESP3 + RESP4

ATT ~ NORM + AWARE + COMM + KNOW
RESP ~ NORM + AWARE + COMM + KNOW
REPORT ~ COMM + ATT + RESP + TOOL
"""


def sinh_du_lieu_theo_seed(cfg: dict, seed: int) -> pd.DataFrame:
    """Sinh bộ dữ liệu tổng hợp N=1017 cho một hạt giống seed bất kỳ."""
    n = int(cfg["project"]["n"])
    rng = np.random.default_rng(seed)
    exo_names = ["NORM", "AWARE", "KNOW", "COMM"]
    corr = np.array([
        [1.0, 0.30, 0.25, 0.20],
        [0.30, 1.0, 0.35, 0.25],
        [0.25, 0.35, 1.0, 0.30],
        [0.20, 0.25, 0.30, 1.0],
    ])
    exo = rng.multivariate_normal(np.zeros(4), corr, size=n)
    lat = {k: exo[:, i] for i, k in enumerate(exo_names)}

    def make_latent(betas):
        signal = sum(float(b) * lat[k] for k, b in betas.items())
        y = signal + rng.normal(
            0, np.sqrt(max(0.15, 1.0 - min(float(np.var(signal)), 0.85))), n
        )
        return (y - y.mean()) / (y.std() or 1.0)

    st = cfg["structural"]
    lat["ATT"] = make_latent(st["ATT"]["predictors"])
    lat["RESP"] = make_latent(st["RESP"]["predictors"])
    tool = rng.binomial(1, float(st.get("tool_probability", 0.65)), n)
    lat["TOOL"] = tool.astype(float)
    lat["COMMxTOOL"] = (lat["COMM"] - lat["COMM"].mean()) * (tool - tool.mean())
    lat["REPORT"] = make_latent(st["REPORT"]["predictors"])

    df = pd.DataFrame({"respondent_id": [f"SYN{i:04d}" for i in range(1, n + 1)]})
    th = np.array(cfg["ordinal"]["thresholds"], float)
    lo = int(cfg["ordinal"]["likert_min"])
    hi = int(cfg["ordinal"]["likert_max"])
    for factor, spec in cfg["measurement"].items():
        loading = float(spec["loading"])
        for j in range(1, int(spec["items"]) + 1):
            x = loading * lat[factor] + rng.normal(
                0, np.sqrt(max(0.01, 1.0 - loading ** 2)), n
            )
            df[f"{factor}{j}"] = np.clip(np.digitize(x, th) + lo, lo, hi).astype(int)
    df["TOOL"] = tool.astype(int)
    df["REPORT"] = np.clip(
        np.digitize(lat["REPORT"] + rng.normal(0, 0.45, n), th) + lo, lo, hi
    ).astype(int)
    return df


def chay_do_on_dinh_5_seeds(cfg: dict):
    """Bước 1: Chạy SEM qua 5 seeds độc lập và tính Mean, SD, Min, Max, tỷ lệ p < 0.05."""
    raw_rows = []
    fit_rows = []
    for run_idx, seed in enumerate(SEEDS, start=1):
        df = sinh_du_lieu_theo_seed(cfg, seed)
        df["COMM_mean"] = df[[f"COMM{i}" for i in range(1, 5)]].mean(axis=1)
        df["COMM_c"] = df["COMM_mean"] - df["COMM_mean"].mean()
        df["TOOL_c"] = df["TOOL"] - df["TOOL"].mean()
        df["COMM_TOOL"] = df["COMM_c"] * df["TOOL_c"]

        model = Model(SEM_SYNTAX_INTERACTION)
        model.fit(df)
        est = model.inspect(std_est=True)
        stats = calc_stats(model)

        fit_rows.append({
            "run": run_idx,
            "seed": seed,
            "chi2": float(stats["chi2"].iloc[0]),
            "dof": int(stats["DoF"].iloc[0]),
            "chi2_p": float(stats["chi2 p-value"].iloc[0]),
            "CFI": float(stats["CFI"].iloc[0]),
            "TLI": float(stats["TLI"].iloc[0]),
            "RMSEA": float(stats["RMSEA"].iloc[0]),
            "GFI": float(stats["GFI"].iloc[0]),
            "AIC": float(stats["AIC"].iloc[0]),
            "BIC": float(stats["BIC"].iloc[0]),
        })

        struct = est[
            (est["op"] == "~") & (est["lval"].isin(["ATT", "RESP", "REPORT"]))
        ].copy()
        for _, r in struct.iterrows():
            raw_rows.append({
                "run": run_idx,
                "seed": seed,
                "path": f"{r['rval']} -> {r['lval']}",
                "outcome": r["lval"],
                "predictor": r["rval"],
                "est_unstd": float(r["Estimate"]),
                "beta_std": float(r["Est. Std"]),
                "se": float(r["Std. Err"]),
                "z_val": float(r["z-value"]),
                "p_val": float(r["p-value"]),
                "sig_005": bool(float(r["p-value"]) < 0.05),
            })

    raw_df = pd.DataFrame(raw_rows)
    fit_df = pd.DataFrame(fit_rows)
    raw_df.to_csv(OUT_DIR / "multiseed_raw_paths.csv", index=False, encoding="utf-8-sig")
    fit_df.to_csv(OUT_DIR / "multiseed_fit_indices.csv", index=False, encoding="utf-8-sig")

    summary_rows = []
    for path_name, grp in raw_df.groupby("path", sort=False):
        betas = grp["beta_std"].values
        summary_rows.append({
            "path": path_name,
            "n_runs": len(betas),
            "mean_beta_std": round(float(np.mean(betas)), 4),
            "sd_beta_std": round(float(np.std(betas, ddof=1)), 4),
            "min_beta_std": round(float(np.min(betas)), 4),
            "max_beta_std": round(float(np.max(betas)), 4),
            "sig_rate_005": f"{int(grp['sig_005'].sum())}/{len(betas)}",
            "mean_p_val": round(float(grp["p_val"].mean()), 4),
        })
    sum_df = pd.DataFrame(summary_rows)
    sum_df.to_csv(
        OUT_DIR / "multiseed_stability_summary.csv", index=False, encoding="utf-8-sig"
    )
    return fit_df, sum_df


def chay_ablation_ba_mo_hinh(df: pd.DataFrame):
    """Bước 2: So sánh Ablation giữa 3 biến thể cấu trúc M1 (Mediation), M2 (Baseline), M3 (Interaction)."""
    df = df.copy()
    df["COMM_mean"] = df[[f"COMM{i}" for i in range(1, 5)]].mean(axis=1)
    df["COMM_c"] = df["COMM_mean"] - df["COMM_mean"].mean()
    df["TOOL_c"] = df["TOOL"] - df["TOOL"].mean()
    df["COMM_TOOL"] = df["COMM_c"] * df["TOOL_c"]

    specs = [
        ("M1_Mediation_Only (No NORM/AWARE->REPORT)", SEM_SYNTAX_MEDIATION_ONLY),
        ("M2_Full_Direct_Paths (Baseline/Paper-Aligned)", SEM_SYNTAX_INTERACTION.replace(" + COMM_TOOL", "")),
        ("M3_Full_With_Interaction (COMM x TOOL)", SEM_SYNTAX_INTERACTION),
    ]
    ablation_rows = []
    for name, syntax in specs:
        m = Model(syntax)
        m.fit(df)
        st = calc_stats(m)
        ablation_rows.append({
            "model_variant": name,
            "DoF": int(st["DoF"].iloc[0]),
            "chi2": round(float(st["chi2"].iloc[0]), 4),
            "chi2_p": round(float(st["chi2 p-value"].iloc[0]), 4),
            "CFI": round(float(st["CFI"].iloc[0]), 4),
            "TLI": round(float(st["TLI"].iloc[0]), 4),
            "RMSEA": round(float(st["RMSEA"].iloc[0]), 4),
            "AIC": round(float(st["AIC"].iloc[0]), 4),
            "BIC": round(float(st["BIC"].iloc[0]), 4),
        })
    abl_df = pd.DataFrame(ablation_rows)
    abl_df.to_csv(
        OUT_DIR / "ablation_model_comparison.csv", index=False, encoding="utf-8-sig"
    )
    return abl_df


def chay_5fold_cv_va_phan_tich_loi(df: pd.DataFrame):
    """Bước 3 & 4: Chạy 5-Fold Cross-Validation chống rò rỉ dữ liệu và phân tích phần dư."""
    n = len(df)
    rng = np.random.default_rng(20261016)
    indices = np.arange(n)
    rng.shuffle(indices)
    folds = np.array_split(indices, 5)

    constructs = ["NORM", "AWARE", "KNOW", "COMM", "ATT", "RESP"]
    work = df.copy()
    for c in constructs:
        work[c] = work[[f"{c}{i}" for i in range(1, 5)]].mean(axis=1)

    cv_rows = []
    oof_preds = np.zeros(n)

    for fold_idx in range(5):
        test_idx = folds[fold_idx]
        train_idx = np.setdiff1d(indices, test_idx)

        train_df = work.iloc[train_idx].copy()
        test_df = work.iloc[test_idx].copy()

        # NGĂN RÒ RỈ TRAIN-TEST: Chỉ tính giá trị trung bình để chuẩn hóa tâm trên tập TRAIN
        comm_train_mean = float(train_df["COMM"].mean())
        tool_train_mean = float(train_df["TOOL"].mean())

        for part in (train_df, test_df):
            part["COMM_c"] = part["COMM"] - comm_train_mean
            part["TOOL_c"] = part["TOOL"] - tool_train_mean
            part["COMM_TOOL"] = part["COMM_c"] * part["TOOL_c"]

        model_specs = {
            "ATT": ["NORM", "AWARE", "COMM", "KNOW"],
            "RESP": ["NORM", "AWARE", "COMM", "KNOW"],
            "REPORT_Baseline": ["NORM", "AWARE", "COMM", "ATT", "RESP", "TOOL"],
            "REPORT_Interaction": ["NORM", "AWARE", "COMM", "ATT", "RESP", "TOOL", "COMM_TOOL"],
        }

        for target_name, preds in model_specs.items():
            outcome_col = "REPORT" if target_name.startswith("REPORT") else target_name
            X_tr = sm.add_constant(train_df[preds], has_constant="add")
            y_tr = train_df[outcome_col]
            X_te = sm.add_constant(test_df[preds], has_constant="add")
            y_te = test_df[outcome_col]

            fit = sm.OLS(y_tr, X_tr).fit(cov_type="HC3")
            y_hat = fit.predict(X_te)

            if target_name == "REPORT_Baseline":
                oof_preds[test_idx] = y_hat

            err = y_te - y_hat
            rmse = float(np.sqrt(np.mean(err ** 2)))
            mae = float(np.mean(np.abs(err)))
            ss_res = float(np.sum(err ** 2))
            ss_tot = float(np.sum((y_te - y_te.mean()) ** 2))
            oos_r2 = float(1.0 - ss_res / ss_tot) if ss_tot > 0 else 0.0
            rho, _ = spearmanr(y_te, y_hat)

            cv_rows.append({
                "fold": fold_idx + 1,
                "model": target_name,
                "n_train": len(train_df),
                "n_test": len(test_df),
                "in_sample_R2": round(float(fit.rsquared), 4),
                "out_of_sample_R2": round(oos_r2, 4),
                "RMSE": round(rmse, 4),
                "MAE": round(mae, 4),
                "Spearman_rho": round(float(rho), 4),
            })

    cv_df = pd.DataFrame(cv_rows)
    cv_df.to_csv(OUT_DIR / "cv_5fold_raw.csv", index=False, encoding="utf-8-sig")

    cv_sum = (
        cv_df.groupby("model", sort=False)[
            ["in_sample_R2", "out_of_sample_R2", "RMSE", "MAE", "Spearman_rho"]
        ]
        .agg(["mean", "std"])
    )
    cv_sum.columns = [f"{col}_{stat}" for col, stat in cv_sum.columns]
    cv_sum = cv_sum.reset_index().round(4)
    cv_sum.to_csv(OUT_DIR / "cv_5fold_summary.csv", index=False, encoding="utf-8-sig")

    # Phân tích phần dư theo từng mức thang đo Likert của REPORT
    work["REPORT_oof_pred"] = oof_preds
    work["residual"] = work["REPORT"] - work["REPORT_oof_pred"]
    work["abs_error"] = work["residual"].abs()

    err_by_level = (
        work.groupby("REPORT", as_index=False)
        .agg(
            count=("REPORT", "count"),
            mean_pred=("REPORT_oof_pred", "mean"),
            mean_residual=("residual", "mean"),
            RMSE=("residual", lambda x: float(np.sqrt(np.mean(x ** 2)))),
            MAE=("abs_error", "mean"),
        )
        .round(4)
    )
    err_by_level.to_csv(
        OUT_DIR / "residual_error_by_report_level.csv", index=False, encoding="utf-8-sig"
    )

    top_errors = (
        work.sort_values("abs_error", ascending=False)[
            [
                "respondent_id",
                "NORM",
                "AWARE",
                "KNOW",
                "COMM",
                "ATT",
                "RESP",
                "TOOL",
                "REPORT",
                "REPORT_oof_pred",
                "residual",
                "abs_error",
            ]
        ]
        .head(10)
        .round(4)
    )
    top_errors.to_csv(
        OUT_DIR / "top10_largest_errors.csv", index=False, encoding="utf-8-sig"
    )

    return cv_sum, err_by_level


def main():
    cfg = yaml.safe_load(CFG_PATH.read_text(encoding="utf-8"))
    df = pd.read_csv(DATA_PATH)

    _, sum_df = chay_do_on_dinh_5_seeds(cfg)
    abl_df = chay_ablation_ba_mo_hinh(df)
    cv_sum, err_by_level = chay_5fold_cv_va_phan_tich_loi(df)

    noi_dung_log = (
        "===== BƯỚC 10: ĐỘ ỔN ĐỊNH 5 SEEDS, ABLATION CẤU TRÚC & 5-FOLD CV CHỐNG RÒ RỈ =====\n"
        "[1] Tổng hợp độ ổn định của các hệ số đường dẫn qua 5 seeds độc lập:\n"
        f"{sum_df.to_string(index=False)}\n\n"
        "[2] So sánh Ablation 3 biến thể cấu trúc SEM (M1 vs. M2 vs. M3):\n"
        f"{abl_df.to_string(index=False)}\n\n"
        "[3] Kết quả 5-Fold Cross-Validation không rò rỉ dữ liệu (Leakage-Free CV):\n"
        f"{cv_sum.to_string(index=False)}\n\n"
        "[4] Phân tích phần dư và lỗi dự báo theo từng mức Likert của REPORT (1..5):\n"
        f"{err_by_level.to_string(index=False)}\n\n"
        f"[HOÀN TẤT] Đã lưu toàn bộ kết quả thực nghiệm lặp tại: {OUT_DIR}\n"
    )
    (LOG_DIR / "10_do_on_dinh_5seeds_va_5fold_cv.log").write_text(
        noi_dung_log, encoding="utf-8"
    )
    print(noi_dung_log)


if __name__ == "__main__":
    main()
