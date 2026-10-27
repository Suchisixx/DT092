# DANH MỤC BẢNG THỐNG KÊ (`results/tables/`) & NHẬT KÝ THỰC THI (`results/logs/`)

Thư mục `results/` lưu trữ hai nhóm đầu ra phục vụ kiểm tra chéo và truy vết từng bước thực thi của pipeline:

---

## 1. Thư mục `results/tables/` — Các bảng kiểm kê, mô tả và kiểm định dữ liệu

| Tên tệp CSV | Được tạo bởi Script | Ý nghĩa chi tiết |
| :--- | :--- | :--- |
| `public_data_inventory.csv` | `scripts/01_inspect_public_data.py` | Kiểm kê tệp dữ liệu công khai trong `data/raw/public/` (mã băm SHA-256, số dòng, số cột, danh sách câu hỏi và tỷ lệ khuyết thiếu). |
| `synthetic_item_descriptives.csv` | `scripts/02_generate_synthetic.py` | Thống kê mô tả (`count`, `mean`, `std`, `min`, `25%`, `50%`, `75%`, `max`, `missing_n`) cho toàn bộ 26 biến khảo sát trong `synthetic_sem.csv`. |
| `synthetic_value_frequencies.csv` | `scripts/02_generate_synthetic.py` | Tần suất (`count`) và tỷ lệ (`proportion`) của từng mức điểm (1..5 hoặc 0..1) cho mỗi biến. |
| `validation_checks.csv` | `scripts/03_validate_data.py` | Kết quả kiểm tra 7 tiêu chí chất lượng kỹ thuật (`N_is_1017`, `unique_ID`, `no_missing`, `TOOL_binary`, `Likert_1_to_5`, `required_columns`, `no_duplicate_feature_rows`). |
| `validation_distributions.csv` | `scripts/03_validate_data.py` | Kiểm tra độ lệch phân phối và tỷ lệ tập trung cao nhất vào 1 mức điểm (`max_category_share`) để phát hiện biến hằng số (`constant`). |
| `negative_tests_report.csv` | `scripts/11_negative_tests_and_benchmark.py` | Báo cáo kết quả chạy 8 kịch bản kiểm thử Unit / Integration / Negative Tests (`T01` $\rightarrow$ `T08`, đạt 8/8 `test_passed = True`). |

---

## 2. Thư mục `results/logs/` — Nhật ký thực thi Tiếng Việt theo đúng trình tự 11 bước

Mỗi khi chạy `python scripts/00_run_all_pipeline.py` (hoặc chạy lẻ từng script), hệ thống tự động xuất 11 tệp nhật ký Tiếng Việt tương ứng với 11 bước:

1. `01_kiem_ke_du_lieu_cong_khai.log`: Nhật ký kiểm kê dữ liệu công khai (`Bước 01`).
2. `02_sinh_du_lieu_mo_phong.log` (và `generate_synthetic.log`): Nhật ký sinh dữ liệu mô phỏng $N=1.017$, `seed=20261016` và mã băm SHA-256 (`Bước 02`).
3. `03_kiem_tra_chat_luong_du_lieu.log`: Nhật ký kiểm tra 7/7 tiêu chí toàn vẹn dữ liệu (`Bước 03`).
4. `04_cfa_va_sem_baseline.log`: Nhật ký ước lượng mô hình đo lường CFA và mô hình SEM cơ sở (`Bước 04`).
5. `05_sem_tuong_tac_H7b.log`: Nhật ký kiểm định giả thuyết tương tác `H7b: COMM × TOOL -> REPORT` (`Bước 05`).
6. `06_so_sanh_baseline_va_tuong_tac.log`: Nhật ký đối chiếu độ lệch $\Delta\beta$ giữa mô hình cơ sở và mô hình tương tác (`Bước 06`).
7. `07_phan_tich_do_nhay_ols_hc3.log`: Nhật ký hồi quy OLS với sai số chuẩn vững HC3 trên điểm trung bình thang đo (`Bước 07`).
8. `08_sem_doi_chieu_bai_bao.log`: Nhật ký mô hình SEM đối chiếu cấu trúc bài báo gốc E02 (`Bước 08`).
9. `09_do_tin_cay_va_gia_tri_thang_do.log`: Nhật ký tính Cronbach's Alpha, CR, AVE và ma trận Fornell-Larcker (`Bước 09`).
10. `10_do_on_dinh_5seeds_va_5fold_cv.log`: Nhật ký chạy lặp 5 seeds độc lập, Ablation 3 biến thể cấu trúc, 5-Fold CV chống rò rỉ và phân tích lỗi (`Bước 10`).
11. `11_kiem_thu_loi_va_chi_phi_tinh_toan.log`: Nhật ký chạy 8 Negative Tests và đo thời gian/bộ nhớ RAM (`Bước 11`).
