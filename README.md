# DT092 — Mô Hình Văn Hóa Báo Cáo Phishing Trong Tổ Chức Giả Lập (SEM Đa Nhóm & Bất Biến Đo Lường: Đức, Anh, Mỹ)

## 1. Giới thiệu & Nghiên cứu Tham khảo
Dự án xây dựng khung thực nghiệm mô phỏng định lượng **Phân tích Nhân tố Khẳng định (CFA)**, **Kiểm định Tính Bất biến Đo lường (Measurement Invariance)** và **Mô hình Phương trình Cấu trúc Đa nhóm (Multigroup SEM)** trên 3 quốc gia (**Germany `N = 306`**, **United Kingdom `N = 205`**, **United States `N = 506`**; tổng **`N = 1,017`**) bám sát cấu trúc nghiên cứu của bài báo Q1:

> **Petrič, G., & Just, J. N. (2025).** *Information security culture and phishing-reporting model: structural equivalence across Germany, UK, and USA*. Journal of Cybersecurity, 11(1), tyaf011, 1–17. DOI: [10.1093/cybsec/tyaf011](https://academic.oup.com/cybersecurity/article/11/1/tyaf011/8128837)

- **Tuyên bố minh bạch dữ liệu**: Bộ dữ liệu `data/synthetic_multigroup.csv` (`N = 1,017`, 28 cột, `seed = 20261029`, `SHA-256: 52c161dcd96ff568228e74c9c6517f2c2423f4bb2bee0860b511912d4aae5cbe`) là **dữ liệu tổng hợp mô phỏng bằng máy tính (synthetic data)** được tham số hóa từ các thống kê công bố của bài báo gốc; tuyệt đối không phải phản hồi khảo sát thực tế từ người tham gia tại Đức, Anh và Mỹ (xem `data/DATASET_DECLARATION.md`).

---

## 2. Cấu trúc Thư mục Dự án

```text
DT092_Phishing_Culture/
├── data/
│   ├── synthetic_multigroup.csv        # Dữ liệu mô phỏng đa nhóm N=1,017 (DE=306, UK=205, US=506)
│   ├── sample_allocation.csv           # Thống kê phân bổ mẫu & tỷ lệ TOOL / REPORT theo quốc gia
│   ├── data_manifest.json              # Siêu dữ liệu seed, tham số DGP & mã băm SHA-256
│   ├── DATASET_DECLARATION.md          # Tuyên bố đạo đức & nguồn gốc dữ liệu tổng hợp
│   └── Survey_Question.md              # Bộ 26 câu hỏi khảo sát Tiếng Việt (6 thang đo + TOOL + REPORT)
├── scripts/
│   ├── 00_run_pipeline.py              # Chạy trọn gói Bước 01 -> Bước 05 bằng 1 lệnh duy nhất
│   ├── 01_generate_multigroup_data.py  # Sinh dữ liệu đa nhóm & kiểm tra 8 tiêu chí kỹ thuật
│   ├── 02_cfa_and_descriptives.py      # Xuất Bảng 1, Bảng 2 (CFA), Bảng 3 (Tương quan), Bảng 4 (Mô tả)
│   ├── 03_multigroup_sem_invariance.py # Xuất Bảng 5 (Pooled SEM), Bảng 6 (Multigroup + Wald), Bảng 7 (Invariance)
│   ├── 04_hypothesis_and_robustness.py # Xuất Bảng 8, Bảng 9 (OLS-HC3 + 5 Seeds), paper_comparison.csv & báo cáo
│   └── 05_verify_all.py                # Kiểm toán tự động toàn bộ đầu ra, miền p-value [0,1] & hội tụ
├── results/
│   ├── tables/                         # 18 bảng CSV kết quả chuẩn hóa (Bảng 1 -> Bảng 9 + paper_comparison.csv)
│   ├── logs/                           # 5 nhật ký thực thi tương ứng Bước 01 -> Bước 05
│   └── verification_report.json        # Báo cáo kiểm toán tự động
├── reports/
│   ├── results_summary.md              # Tổng hợp kết quả thực nghiệm & đối chiếu bài báo gốc
│   ├── methodology_and_assumptions.md  # Cơ sở toán học (MLW vs WLSMV, OLS-HC3, Invariance, RMSEA)
│   └── limitations.md                  # Các giới hạn phương pháp luận & hướng dẫn trình bày báo cáo
└── tests/
    ├── run_e2e_tests.py                # Trình chạy 120 bài kiểm thử tự động 4 tầng (Opaque-Box E2E)
    ├── test_tier1_feature_coverage.py  # Tier 1: Kiểm thử 19 nhóm tính năng (95 tests)
    ├── test_tier2_boundaries.py        # Tier 2: Kiểm thử biên & trường hợp suy biến (12 tests)
    ├── test_tier3_pairwise.py          # Tier 3: Kiểm thử liên kết chéo giữa các bảng/mô hình (8 tests)
    └── test_tier4_e2e.py               # Tier 4: Kiểm thử tích hợp toàn tuyến & độ sạch thư mục (5 tests)
```

---

## 3. Đối chiếu 18 Bảng Kết quả (`results/tables/`) với Bài báo Gốc

| Thành phần trong Petrič & Just (2025) | Tệp CSV trong `results/tables/` | Nội dung chính |
| :--- | :--- | :--- |
| **Table 1** (p. 7 — Mẫu & Công cụ) | `table1_demographics.csv`<br/>`table1_country_summary.csv` | Cỡ mẫu `DE=306, UK=205, US=506` (`N=1,017`), tỷ lệ `TOOL=1` (`75.32%` vs. bài báo `75.5%`), tần suất báo cáo `REPORT` |
| **Tables 2 & 3** (pp. 7–8 — CFA, $\alpha$, AVE) | `table2_cfa_measurement.csv`<br/>`table2_cfa_fit_indices.csv` | Hệ số tải chuẩn hóa 24 biến quan sát, $\chi^2, df, \text{CFI}, \text{TLI}, \text{RMSEA}, \text{SRMR}$, Cronbach's $\alpha$, CR, AVE, $\sqrt{\text{AVE}}$ |
| **Invariance** (pp. 7–8 — Bất biến đo lường) | `table7_measurement_invariance.csv` | Kiểm định lồng nhau 3 cấp: **Configural** ($df=711$), **Metric** ($df=747, \Delta\text{CFI}=-0.0001$), **Scalar** ($df=783, \Delta\text{CFI}=-0.0008$) |
| **Table 4** (p. 10 — Thống kê mô tả) | `table4_descriptives.csv` | Mean, SD, Min, Max, Skewness, Kurtosis cho mẫu gộp (`POOLED`) và từng quốc gia (`DE`, `UK`, `US`) |
| **Table 5** (p. 11 — Tương quan) | `table3_correlations.csv` | Ma trận tương quan Pearson điểm trung bình cộng thang đo trên mẫu gộp và từng quốc gia (đạt 100% Fornell-Larcker) |
| **Figure 2** (p. 11 — SEM Mẫu gộp) | `table5_pooled_sem.csv`<br/>`table5_sem_fit_indices.csv` | Ước lượng 15 đường dẫn cấu trúc (`H1a`–`H7b`, bao gồm `COMM × TOOL -> REPORT`) và chỉ số độ phù hợp trên `N=1,017` |
| **Table 6** (p. 11 — SEM Đa nhóm) | `table6_multigroup_sem.csv`<br/>`table6_multigroup_sem_long.csv`<br/>`table6_multigroup_fit.csv`<br/>`table6_cross_group_tests.csv` | Hệ số đường dẫn & $R^2$ theo từng nước (`DE`, `UK`, `US`), kèm kiểm định **Wald $\chi^2(2)$** và **$Z$-test từng cặp nước** trên hệ số chưa chuẩn hóa $B/\text{SE}(B)$ |
| **Table 7** (p. 13 — Kiểm định giả thuyết) | `table8_hypothesis_testing.csv` | Kết luận `Supported` / `Partially supported` / `Not supported` cho 15 giả thuyết trên mẫu gộp và 3 quốc gia |
| **Độ vững & So sánh trực tiếp bài báo** | `table9_robustness_hc3.csv`<br/>`table9_country_ols_hc3.csv`<br/>`table9_multiseed_raw_runs.csv`<br/>`paper_comparison.csv` | Hồi quy sai số chuẩn vững **OLS-HC3**, 300 dòng kết quả thô qua **5 seeds độc lập** (không trung bình cộng $p$-value) và sai số $|\beta_{\text{sim}} - \beta_{\text{paper}}|$ |

---

## 4. Hướng dẫn Chạy Tái lập & Kiểm thử (Windows PowerShell)

```powershell
# Thiết lập đường dẫn thư viện môi trường ảo .venv
$env:PYTHONPATH = "d:\Download\DT092_Phishing_Culture\.venv\Lib\site-packages"

# 1. Chạy toàn bộ 5 bước thực nghiệm từ đầu đến cuối (~20 giây)
python scripts/00_run_pipeline.py

# 2. Chạy bộ 120 bài kiểm thử tự động 4 tầng (Opaque-Box E2E Test Suite)
python tests/run_e2e_tests.py
```
