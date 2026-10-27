# DT092 — Khung Thực Nghiệm Tái Lập Có Chọn Lọc Cấu Trúc Khảo Sát & SEM Về Văn Hóa An Toàn Thông Tin Và Hành Vi Báo Cáo Phishing - Lần 3

## 1. Giới thiệu & Tài liệu nền
Dự án xây dựng khung thực nghiệm tái lập có chọn lọc cấu trúc khảo sát (Survey Instrument) và mô hình phương trình cấu trúc (CFA/SEM) dựa trên bài báo Q1:
> **Petrič, G., & Just, J. N. (2025).** *Information security culture and phishing-reporting model: structural equivalence across Germany, UK, and USA*. Journal of Cybersecurity, 11(1), tyaf011, 1–17. https://doi.org/10.1093/cybsec/tyaf011

- **Dữ liệu thực nghiệm**: Bộ dữ liệu `data/simulated/synthetic_sem.csv` ($N = 1.017$ dòng, 27 cột, `seed = 20261016`, SHA-256: `2cae044842247f21563e4c73abf63f8b26be6b4499dcea4160f61249e714c6bb`) là **dữ liệu tổng hợp (synthetic data)** dùng để kiểm chứng toàn diện quy trình chuẩn bị dữ liệu, CFA, SEM (`semopy`), tương tác `COMM × TOOL`, hồi quy độ nhạy `OLS-HC3` (`statsmodels`), độ tin cậy/giá trị thang đo, độ ổn định đa seed và 5-Fold Cross-Validation chống rò rỉ dữ liệu.

---

## 2. Trình tự 11 File Code (`scripts/`) & Chức năng từng File

| Thứ tự | File Code (`scripts/`) | Mục tiêu ngắn gọn | File Log Tiếng Việt (`results/logs/`) | Tập kết quả xuất ra |
| :---: | :--- | :--- | :--- | :--- |
| **00** | `00_run_all_pipeline.py` | **Chạy tự động toàn bộ Bước 01 $\rightarrow$ Bước 11** chỉ bằng 1 lệnh duy nhất. | In tổng hợp trên màn hình console | Toàn bộ `artifacts/` & `results/` |
| **01** | `01_inspect_public_data.py` | Kiểm kê tệp khảo sát công khai trong `data/raw/public/`, tính SHA-256, đếm dòng/cột/tỷ lệ thiếu. | `01_kiem_ke_du_lieu_cong_khai.log` | `results/tables/public_data_inventory.csv` |
| **02** | `02_generate_synthetic.py` | Sinh dữ liệu mô phỏng $N=1.017$ (`seed=20261016`) theo tham số `config/model_config.yml`. | `02_sinh_du_lieu_mo_phong.log` | `data/simulated/synthetic_sem.csv`<br/>`artifacts/synthetic_manifest.json` |
| **03** | `03_validate_data.py` | Kiểm tra 7 tiêu chí chất lượng kỹ thuật (cỡ mẫu, ID duy nhất, không trống, miền Likert 1–5, không trùng dòng). | `03_kiem_tra_chat_luong_du_lieu.log` | `results/tables/validation_checks.csv`<br/>`artifacts/validation_summary.json` |
| **04** | `04_run_baseline_sem.py` | Ước lượng mô hình đo lường **CFA** (6 nhân tố) và mô hình **SEM cơ sở (Baseline)**. | `04_cfa_va_sem_baseline.log` | `artifacts/baseline/cfa_*.csv`<br/>`artifacts/baseline/sem_*.csv` |
| **05** | `05_run_interaction_sem.py` | Chuẩn hóa tâm `COMM`, `TOOL` và ước lượng **SEM mở rộng có tương tác `COMM × TOOL`** (kiểm định H7b). | `05_sem_tuong_tac_H7b.log` | `artifacts/interaction/H7b_interaction_result.csv`<br/>`interaction_*.csv` |
| **06** | `06_compare_models.py` | Đối chiếu 14 hệ số đường dẫn giữa SEM Baseline và SEM Interaction ($\Delta\beta$ và kết luận ý nghĩa). | `06_so_sanh_baseline_va_tuong_tac.log` | `artifacts/sensitivity/baseline_vs_interaction.csv` |
| **07** | `07_sensitivity_hc3.py` | Phân tích độ nhạy bằng **hồi quy OLS với sai số chuẩn vững HC3** trên điểm trung bình thang đo. | `07_phan_tich_do_nhay_ols_hc3.log` | `artifacts/sensitivity/hc3_sensitivity_results.csv` |
| **08** | `08_run_paper_aligned_sem.py` | Ước lượng mô hình SEM đối chiếu cấu trúc bài báo (E02) và lưu thông tin hội tụ SLSQP. | `08_sem_doi_chieu_bai_bao.log` | `artifacts/paper_aligned/paper_aligned_*.csv` |
| **09** | `09_reliability_validity.py` | Tính **Cronbach's Alpha, Composite Reliability (CR), AVE** và **Ma trận Fornell-Larcker** đối chiếu Table 3 & 5 của bài báo. | `09_do_tin_cay_va_gia_tri_thang_do.log` | `artifacts/sensitivity/reliability_validity.csv`<br/>`fornell_larcker_matrix.csv` |
| **10** | `10_repeated_runs_and_cv.py` | Chạy lặp **5 Seeds độc lập**, **Ablation 3 mô hình** (`M1, M2, M3`), **5-Fold CV chống rò rỉ** & **Phân tích lỗi**. | `10_do_on_dinh_5seeds_va_5fold_cv.log` | `artifacts/repeated_runs/*.csv` |
| **11** | `11_negative_tests_and_benchmark.py` | Chạy **8 kịch bản Negative Tests** (tiêm lỗi dữ liệu) & đo **Thời gian chạy (ms), RAM đỉnh (MB), số vòng lặp hội tụ**. | `11_kiem_thu_loi_va_chi_phi_tinh_toan.log` | `results/tables/negative_tests_report.csv`<br/>`artifacts/runtime_benchmark.csv` |

---

## 3. Hướng dẫn cài đặt và chạy lại từ đầu (Windows PowerShell)

```powershell
# 1. Tạo và kích hoạt môi trường ảo
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

# 2. Chạy toàn bộ 11 bước thực nghiệm chỉ bằng 1 lệnh duy nhất:
python scripts/00_run_all_pipeline.py
```

---

## 4. Tài liệu giải thích kết quả & Báo cáo hoàn chỉnh

- **Giải thích chi tiết 6 Tập kết quả & So sánh trực tiếp với bài báo gốc**: Xem tại [`artifacts/README_GIAI_THICH_KET_QUA.md`](artifacts/README_GIAI_THICH_KET_QUA.md).
- **Danh mục bảng thống kê & 11 file log Tiếng Việt**: Xem tại [`results/README_BANG_VA_LOG.md`](results/README_BANG_VA_LOG.md).
- **Bảng đối chiếu tổng hợp 15 giả thuyết Paper $\leftrightarrow$ DT092**: Xem tại [`report/paper_to_results_mapping.csv`](report/paper_to_results_mapping.csv).
- **Báo cáo đề tài hoàn chỉnh (20–30 trang)**: Xem tại [`report/BAO_CAO_DT092_HOAN_CHINH.md`](report/BAO_CAO_DT092_HOAN_CHINH.md).
