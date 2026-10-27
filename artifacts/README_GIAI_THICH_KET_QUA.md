# HƯỚNG DẪN ĐỌC HIỂU CÁC TẬP KẾT QUẢ & ĐỐI CHIẾU VỚI BÀI BÁO GỐC (PETRIČ & JUST, 2025)

Tài liệu này giải thích chi tiết toàn bộ các tệp kết quả trong thư mục `artifacts/` và `results/`, được sắp xếp thành **6 Tập kết quả theo đúng trình tự chạy từ Bước 01 đến Bước 11**, kèm giải thích ý nghĩa từng chỉ số và bảng đối chiếu trực tiếp với bài báo Q1 gốc (**Gregor Petrič & John N. Just, 2025**, DOI: `10.1093/cybsec/tyaf011`).

---

## SƠ ĐỒ ÁNH XẠ TRÌNH TỰ CODE $\rightarrow$ TẬP KẾT QUẢ

| Tập kết quả | Các file code tạo ra (`scripts/`) | Thư mục / Tệp kết quả đầu ra trong `artifacts/` | Nội dung cốt lõi |
| :--- | :--- | :--- | :--- |
| **TẬP 1: Hồ sơ Dữ liệu & Kiểm tra chất lượng** | `01_inspect_public_data.py`<br/>`02_generate_synthetic.py`<br/>`03_validate_data.py` | `artifacts/data_manifest.csv`<br/>`artifacts/synthetic_manifest.json`<br/>`artifacts/validation_summary.json` | Hồ sơ kiểm kê dữ liệu, thông số sinh dữ liệu mô phỏng ($N=1.017$, SHA-256) và kết quả 7/7 kiểm tra toàn vẹn. |
| **TẬP 2: Độ tin cậy & Giá trị thang đo** | `09_reliability_validity.py` | `artifacts/reliability_validity/reliability_validity.csv`<br/>`artifacts/reliability_validity/fornell_larcker_matrix.csv`<br/>`artifacts/reliability_validity/construct_correlation_matrix.csv` | Cronbach's Alpha ($\alpha$), Composite Reliability ($\text{CR}$), phương sai trích ($\text{AVE}$), ma trận Fornell-Larcker và ma trận tương quan. |
| **TẬP 3: Mô hình CFA & SEM Cơ sở (Baseline)** | `04_run_baseline_sem.py` | `artifacts/baseline/cfa_fit_indices.csv`<br/>`artifacts/baseline/cfa_estimates.csv`<br/>`artifacts/baseline/sem_fit_indices.csv`<br/>`artifacts/baseline/sem_estimates.csv`<br/>`artifacts/baseline/sem_structural_paths.csv` | Chỉ số độ phù hợp CFA/SEM, hệ số tải nhân tố chuẩn hóa và 14 đường dẫn cấu trúc từ Văn hóa ATTT đến `ATT`, `RESP` và `REPORT`. |
| **TẬP 4: Biến thể tương tác `COMM × TOOL` (H7b)** | `05_run_interaction_sem.py` | `artifacts/interaction/H7b_interaction_result.csv`<br/>`artifacts/interaction/interaction_fit_indices.csv`<br/>`artifacts/interaction/interaction_estimates.csv` | Kiểm định giả thuyết tương tác điều tiết H7b (`COMM × TOOL -> REPORT`) và chỉ số độ phù hợp của mô hình mở rộng. |
| **TẬP 5: Độ nhạy `OLS-HC3` & So sánh đặc tả** | `06_compare_models.py`<br/>`07_sensitivity_hc3.py` | `artifacts/sensitivity/baseline_vs_interaction.csv`<br/>`artifacts/sensitivity/hc3_sensitivity_results.csv` | So sánh độ lệch $\Delta\beta$ giữa Baseline và Interaction; hồi quy độ nhạy OLS với sai số chuẩn vững HC3 trên điểm trung bình thang đo. |
| **TẬP 6: Độ ổn định 5 Seeds, Ablation & 5-Fold CV** | `10_repeated_runs_and_cv.py` | `artifacts/repeated_runs/multiseed_stability_summary.csv`<br/>`artifacts/repeated_runs/ablation_model_comparison.csv`<br/>`artifacts/repeated_runs/cv_5fold_summary.csv`<br/>`artifacts/repeated_runs/residual_error_by_report_level.csv` | Chạy lặp 5 seeds độc lập, so sánh Ablation 3 mô hình (`M1`, `M2`, `M3`), kiểm định chéo 5-Fold chống rò rỉ dữ liệu và phân tích phần dư. |

---

## TẬP KẾT QUẢ 1: DỮ LIỆU, THỐNG KÊ MÔ TẢ & KIỂM TRA CHẤT LƯỢNG (BƯỚC 01 $\rightarrow$ 03)

### 1.1. Các tệp trong Tập 1
- `artifacts/synthetic_manifest.json`: Lưu hồ sơ gốc của tệp dữ liệu mô phỏng `synthetic_sem.csv` ($N = 1.017$ dòng, 27 cột, `seed = 20261016`, mã băm SHA-256: `2cae044842247f21563e4c73abf63f8b26be6b4499dcea4160f61249e714c6bb`).
- `artifacts/data_manifest.csv` & `results/tables/public_data_inventory.csv`: Hồ sơ kiểm kê tất cả tệp dữ liệu trong dự án (bao gồm dữ liệu công khai `Generated_Survey_Responses.csv` gồm 80 dòng × 25 cột).
- `artifacts/variable_mapping_template.csv`: Bảng ánh xạ từng câu hỏi tiếng Việt trong `Survey_Question.md` với 26 câu hỏi tiếng Anh trong Table 2 của bài báo gốc.
- `results/tables/synthetic_item_descriptives.csv`: Điểm trung bình (`mean`), độ lệch chuẩn (`std`), giá trị nhỏ nhất/lớn nhất (`min`/`max`) của từng câu hỏi.
- `results/tables/validation_checks.csv` & `artifacts/validation_summary.json`: Kết quả **7/7 kiểm tra chất lượng kỹ thuật** (tất cả đều `passed = True`).

### 1.2. So sánh Thống kê mô tả với Bài báo gốc (Table 1 & Table 4, trang 7 & 10)

| Biến / Thang đo | Bài báo gốc (Petrič & Just, 2025) — Khảo sát thật ($N=1.017$) | Đề tài DT092 — Dữ liệu mô phỏng ($N=1.017$) | Giải thích sự giống và khác nhau |
| :--- | :---: | :---: | :--- |
| **Cỡ mẫu ($N$)** | **$1.017$** (Đức 306, Anh 205, Mỹ 506) | **$1.017$** (Mẫu gộp tổng hợp) | Giữ nguyên cỡ mẫu $N=1.017$ để đảm bảo cùng bậc tự do và lực thống kê (statistical power). |
| **Tỷ lệ có công cụ báo cáo (`TOOL = 1`)** | **75,5%** | **65,4%** ($M = 0,654, SD = 0,476$) | Trong `model_config.yml`, xác suất Bernoulli đặt là `0.65`. Cả hai đều phản ánh đa số tổ chức có trang bị công cụ. |
| **Tần suất báo cáo (`REPORT`, Likert 1–5)** | $M = 3,82$ ($SD = 1,26$) | $M = 3,041$ ($SD = 1,254$) | Khảo sát tự khai thực tế bị lệch trái (nhân viên có xu hướng tự nhận mình báo cáo nhiều, $M=3,82$); dữ liệu mô phỏng dùng ngưỡng cắt đối xứng nên tâm nằm quanh $3,04$, nhưng **độ lệch chuẩn ($SD \approx 1,25$) khớp gần như tuyệt đối**. |
| **6 thang đo Văn hóa ATTT (`ATT`, `RESP`, `KNOW`, `COMM`, `NORM`, `AWARE`)** | $M \in [3,20; 3,68]$<br/>$SD \in [0,67; 1,10]$ | $M \in [2,991; 3,084]$<br/>$SD \in [0,897; 0,995]$ | Dữ liệu mô phỏng chuẩn hóa biến tiềm ẩn về $\mathcal{N}(0,1)$ trước khi cắt ngưỡng đối xứng `[-1.25, -0.45, 0.35, 1.15]` nên trung bình các thang đo đều xoay quanh mức $3,0$. |

---

## TẬP KẾT QUẢ 2: MÔ HÌNH ĐO LƯỜNG (CFA), ĐỘ TIN CẬY & GIÁ TRỊ THANG ĐO (BƯỚC 04a & 09)

### 2.1. Ý nghĩa các chỉ số trong Tập 2
- Trong `artifacts/baseline/cfa_fit_indices.csv`:
  - **`chi2` ($\chi^2$) và `DoF` ($df$)**: Thống kê Chi-bình phương và bậc tự do kiểm định sự khác biệt giữa ma trận hiệp phương sai mẫu và ma trận của mô hình. Tỷ lệ $\chi^2 / df < 3$ (hoặc $p > 0,05$) là rất tốt.
  - **`CFI` (Comparative Fit Index) & `TLI` (Tucker-Lewis Index)**: Chỉ số phù hợp so sánh; ngưỡng tốt là **$\ge 0,90$** (lý tưởng $\ge 0,95$).
  - **`RMSEA` (Root Mean Square Error of Approximation)**: Sai số xấp xỉ; ngưỡng tốt là **$< 0,08$** (lý tưởng $< 0,05$).
- Trong `artifacts/sensitivity/reliability_validity.csv` và `fornell_larcker_matrix.csv`:
  - **`cronbach_alpha_dt092` ($\alpha$) & `CR_dt092` (Composite Reliability)**: Đo độ tin cậy nội tại (các câu hỏi trong cùng 1 nhóm có nhất quán với nhau không). Ngưỡng đạt: **$\ge 0,70$**.
  - **`AVE_dt092` (Average Variance Extracted)**: Phương sai trích trung bình = trung bình bình phương các hệ số tải nhân tố chuẩn hóa ($\frac{1}{k}\sum \lambda_i^2$), đo **giá trị hội tụ**. Ngưỡng chuẩn: **$\ge 0,50$** (hoặc $\ge 0,45$ nếu $\text{CR} > 0,70$ theo Fornell & Larcker, 1981).
  - **`sqrt_AVE_dt092` ($\sqrt{\text{AVE}}$) & Tiêu chuẩn Fornell-Larcker**: Để các thang đo không bị trùng lặp khái niệm (**giá trị phân biệt**), $\sqrt{\text{AVE}}$ của mỗi biến (nằm trên đường chéo của `fornell_larcker_matrix.csv`) phải **lớn hơn** hệ số tương quan của biến đó với mọi biến khác.

### 2.2. So sánh CFA, Độ tin cậy & Giá trị hội tụ với Bài báo gốc (Trang 7–8, Table 3)

| Thang đo / Chỉ số | Bài báo gốc (Petrič & Just, 2025) | Kết quả của bạn (DT092) | Giải thích dễ hiểu |
| :--- | :---: | :---: | :--- |
| **Độ phù hợp CFA** | $\chi^2 = 1493,2$ ($df = 284$)<br/>$\text{CFI} = 0,92$; $\text{TLI} = 0,90$<br/>$\text{RMSEA} = 0,065$ | $\chi^2 = 229,80$ ($df = 237, p = 0,619$)<br/>$\text{CFI} = 1,0008$; $\text{TLI} = 1,0009$<br/>$\text{RMSEA} = 0,0000$ | Dữ liệu mô phỏng được sinh từ đúng 6 nhân tố chuẩn nên $\chi^2 < df$, dẫn tới $\text{RMSEA} = 0$ và $\text{CFI} \approx 1$. Trong báo cáo cần nêu rõ đây là dấu hiệu pipeline khớp đúng cơ chế sinh dữ liệu, không phải chứng minh lý thuyết hoàn hảo. |
| **ATT (Thái độ)** | $\alpha = 0,90$; $\text{AVE} = 0,66$; $\sqrt{\text{AVE}} = 0,81$ | $\alpha = 0,854$; $\text{CR} = 0,855$; $\text{AVE} = 0,595$; $\sqrt{\text{AVE}} = 0,772$ | Đạt rất tốt ($\alpha > 0,85$, $\text{AVE} > 0,59$). |
| **RESP (Trách nhiệm)** | $\alpha = 0,84$; $\text{AVE} = 0,64$; $\sqrt{\text{AVE}} = 0,80$ | $\alpha = 0,858$; $\text{CR} = 0,858$; $\text{AVE} = 0,601$; $\sqrt{\text{AVE}} = 0,776$ | Rất sát với bài báo gốc. |
| **NORM (Chuẩn mực)** | $\alpha = 0,86$; $\text{AVE} = 0,55$; $\sqrt{\text{AVE}} = 0,74$ | $\alpha = 0,834$; $\text{CR} = 0,834$; $\text{AVE} = 0,558$; $\sqrt{\text{AVE}} = 0,747$ | Khớp gần như tuyệt đối với bài báo gốc ($\text{AVE} = 0,558$ vs. $0,55$). |
| **AWARE (Nhận thức ISP)** | $\alpha = 0,80$; $\text{AVE} = 0,58$; $\sqrt{\text{AVE}} = 0,76$ | $\alpha = 0,835$; $\text{CR} = 0,835$; $\text{AVE} = 0,559$; $\sqrt{\text{AVE}} = 0,748$ | Khớp rất sát với bài báo gốc. |
| **COMM (Giao tiếp)** | $\alpha = 0,79$; $\text{AVE} = 0,50$; $\sqrt{\text{AVE}} = 0,71$ | $\alpha = 0,782$; $\text{CR} = 0,782$; $\text{AVE} = 0,473$; $\sqrt{\text{AVE}} = 0,688$ | $\alpha = 0,782$ sát với $0,79$ của bài báo; $\text{AVE} = 0,473$ hơi dưới $0,50$ do rời rạc hóa Likert nhưng $\text{CR} = 0,782 > 0,70$ nên vẫn đạt. |
| **KNOW (Kiến thức)** | $\alpha = 0,74$; **$\text{AVE} = 0,49$**; $\sqrt{\text{AVE}} = 0,70$ | $\alpha = 0,768$; $\text{CR} = 0,768$; **$\text{AVE} = 0,453$**; $\sqrt{\text{AVE}} = 0,673$ | Điểm thú vị: **Cả bài báo gốc ($\text{AVE}=0,49$) và bài của bạn ($\text{AVE}=0,453$) đều có AVE của `KNOW` thấp nhất và hơi dưới 0,50**, nhưng $\alpha$ và $\text{CR}$ đều $> 0,74$ nên đều hợp lệ. |
| **Giá trị phân biệt (Fornell-Larcker)** | Đạt cho cả 6 thang đo | **Đạt 6/6 thang đo** (`discriminant_validity_checks.csv`) | Trong bài của bạn, $\sqrt{\text{AVE}}$ nhỏ nhất là $0,673$ lớn hơn hẳn tương quan lớn nhất giữa các cấu trúc là $0,466$ (`NORM` – `RESP`). |

---

## TẬP KẾT QUẢ 3 & 4: MÔ HÌNH CẤU TRÚC SEM, BIẾN THỂ TƯƠNG TÁC H7b & ĐỘ NHẠY OLS-HC3 (BƯỚC 04b, 05, 06, 07, 08)

### 3.1. Ý nghĩa các cột trong bảng ước lượng SEM (`sem_estimates.csv`, `paper_aligned_structural_paths.csv`) và OLS-HC3 (`hc3_sensitivity_results.csv`)
- **`lval` (Left value)**: Biến phụ thuộc (biến nhận mũi tên tác động: `ATT`, `RESP`, `REPORT`).
- **`rval` (Right value)**: Biến độc lập / biến dự báo (biến phát mũi tên: `NORM`, `AWARE`, `COMM`, `KNOW`, `TOOL`, `COMM_TOOL`).
- **`Estimate` (hoặc `coefficient` trong OLS)**: Hệ số hồi quy **chưa chuẩn hóa** ($b$).
- **`Est. Std`**: Hệ số đường dẫn **đã chuẩn hóa** ($\beta \in [-1, 1]$). **Đây là cột quan trọng nhất** dùng để so sánh độ mạnh yếu giữa các biến và đối chiếu với Figure 2 của bài báo gốc.
- **`Std. Err` / `robust_se_HC3`**: Sai số chuẩn của ước lượng.
- **`z-value` / `t_value` & `p-value`**: Thống kê kiểm định và giá trị xác suất $p$. Nếu **`p-value < 0.05`**, đường dẫn đó **có ý nghĩa thống kê** ở mức $5\%$.

### 3.2. Bảng đối chiếu trực tiếp 15 Giả thuyết: Kết quả của bạn vs. Bài báo gốc (Figure 2 & Table 6–7)

*(Xem đầy đủ trong tệp `report/paper_to_results_mapping.csv`)*

| Giả thuyết | Đường dẫn | Bài báo gốc ($\beta$ Mẫu gộp) | Kết quả SEM của bạn ($\beta$ chuẩn hóa, $p$) | Kết quả OLS-HC3 của bạn ($b$, $p$) | Kết luận so sánh giữa bài bạn và bài báo gốc |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **H1a** | `NORM -> ATT` | $+0,39^{***}$ | **$+0,402$** ($p < 0,001$) | $+0,353$ ($p < 0,001$) | **Trùng khớp hoàn toàn**: Chuẩn mực thúc đẩy mạnh thái độ tích cực. |
| **H2a** | `AWARE -> ATT` | $+0,40^{***}$ | **$+0,418$** ($p < 0,001$) | $+0,363$ ($p < 0,001$) | **Trùng khớp hoàn toàn**: Hiểu rõ chính sách thúc đẩy mạnh thái độ. |
| **H3a** | `COMM -> ATT` | $-0,26^{***}$ | **$-0,251$** ($p < 0,001$) | $-0,190$ ($p < 0,001$) | **Trùng khớp hoàn toàn**: Tái hiện chính xác hiệu ứng ngược chiều (âm) của giao tiếp lên thái độ. |
| **H4a** | `KNOW -> ATT` | $+0,09^{***}$ | **$+0,092$** ($p = 0,016$) | $+0,099$ ($p = 0,002$) | **Trùng khớp hoàn toàn**: Kiến thức có tác động dương nhưng nhỏ ($\approx 0,09$) lên thái độ. |
| **H1b** | `NORM -> RESP` | $+0,43^{***}$ | **$+0,429$** ($p < 0,001$) | $+0,385$ ($p < 0,001$) | **Trùng khớp hoàn toàn**: Chuẩn mực là yếu tố mạnh nhất tạo nên ý thức trách nhiệm. |
| **H2b** | `AWARE -> RESP` | $+0,37^{***}$ | **$+0,326$** ($p < 0,001$) | $+0,299$ ($p < 0,001$) | **Trùng khớp hoàn toàn**: Nhận thức chính sách thúc đẩy mạnh trách nhiệm. |
| **H3b** | `COMM -> RESP` | $-0,14^{***}$ | **$-0,108$** ($p = 0,002$) | $-0,068$ ($p = 0,019$) | **Trùng khớp hoàn toàn**: Tái hiện hiệu ứng boomerang (âm) của giao tiếp làm giảm trách nhiệm cá nhân. |
| **H4b** | `KNOW -> RESP` | $+0,16^{***}$ | **$+0,151$** ($p < 0,001$) | $+0,153$ ($p < 0,001$) | **Trùng khớp hoàn toàn**: Kiến thức thúc đẩy ý thức trách nhiệm mạnh hơn so với thái độ. |
| **H1c** | `NORM -> REPORT` | $+0,02\text{ (ns)}$ | $+0,053$ ($p = 0,275$) | $+0,094$ ($p = 0,053$) | **Trùng khớp hoàn toàn**: Không có tác động trực tiếp có ý nghĩa ở mức $5\%$ (chỉ tác động gián tiếp). |
| **H2c** | `AWARE -> REPORT` | $+0,07\text{ (ns)}$ | $-0,013$ ($p = 0,784$) | $+0,021$ ($p = 0,657$) | **Trùng khớp hoàn toàn**: Không có tác động trực tiếp có ý nghĩa thống kê. |
| **H3c** | `COMM -> REPORT` | $+0,29^{***}$ | **$+0,235$** ($p < 0,001$) | $+0,264$ ($p < 0,001$) | **Trùng khớp hoàn toàn**: Chất lượng giao tiếp là yếu tố trực tiếp mạnh nhất thúc đẩy báo cáo phishing. |
| **H5** | `ATT -> REPORT` | $+0,12^{***}$ | **$+0,101$** ($p = 0,037$) | $+0,101$ ($p = 0,029$) | **Trùng khớp hoàn toàn**: Thái độ tích cực thúc đẩy hành vi báo cáo ($\beta \approx 0,10–0,12$). |
| **H6** | `RESP -> REPORT` | $+0,14^{***}$ | $+0,080$ ($p = 0,083$) | $+0,091$ ($p = 0,051$) | **Có ý nghĩa cận biên ở mức 10% ($p \approx 0,051–0,083$)** ở seed đầu tiên do suy giảm khi cắt ngưỡng Likert; khi chạy trung bình 5 seeds đạt $\bar{\beta}=0,107, p=0,047 < 0,05$. |
| **H7a** | `TOOL -> REPORT` | $+0,19^{**}$ | **$+0,085$** ($p = 0,005$) | **$+0,223$** ($p = 0,005$) | **Trùng khớp về ý nghĩa thống kê ($p = 0,005 < 0,01$)**: Có công cụ báo cáo giúp tăng tần suất báo cáo. |
| **H7b** | `COMM × TOOL -> REPORT` | $-0,05\text{ (ns)}$ | $-0,021$ ($p = 0,486$) | $-0,061$ ($p = 0,450$) | **Trùng khớp hoàn toàn**: Cả bài báo gốc, SEM mở rộng và OLS-HC3 đều bác bỏ hiệu ứng tương tác H7b. |

---

## TẬP KẾT QUẢ 5: ĐỘ ỔN ĐỊNH 5 SEEDS, ABLATION, 5-FOLD CV & PHÂN TÍCH LỖI (BƯỚC 10)

Các tệp trong thư mục `artifacts/repeated_runs/`:
1. **`multiseed_stability_summary.csv`**:
   - Chạy lại toàn bộ quá trình sinh dữ liệu và ước lượng SEM trên 5 hạt giống ngẫu nhiên độc lập (`20261016` $\rightarrow$ `20261020`).
   - Kết quả cho thấy các đường dẫn chính (`NORM -> ATT`, `AWARE -> ATT`, `COMM -> ATT`, `NORM -> RESP`, `AWARE -> RESP`, `KNOW -> RESP`, `COMM -> REPORT`) đều đạt ý nghĩa thống kê ở **5/5 lần chạy (100%)** với độ lệch chuẩn rất nhỏ ($\text{SD} \le 0,054$).
2. **`ablation_model_comparison.csv`**:
   - So sánh 3 mô hình: `M1_Mediation_Only` (không có đường trực tiếp `NORM/AWARE -> REPORT`), `M2_Full_Direct_Paths` (Baseline) và `M3_Full_With_Interaction`.
   - `M1` có chỉ số **$\text{AIC} = 133,46$ và $\text{BIC} = 463,41$ thấp nhất (tốt nhất)**, chứng minh mô hình trung gian hoàn toàn là mô hình tiết kiệm (parsimonious) nhất.
3. **`cv_5fold_summary.csv`**:
   - Đánh giá dự báo ngoài mẫu (Out-of-Sample) qua 5-Fold Cross-Validation không rò rỉ dữ liệu:
   - `ATT` đạt $\text{Out-of-sample } R^2 = 0,3068 \pm 0,0723$, $\text{Spearman } \rho = 0,5635$.
   - `RESP` đạt $\text{Out-of-sample } R^2 = 0,3217 \pm 0,0379$, $\text{Spearman } \rho = 0,5536$.
   - `REPORT_Baseline` đạt $\text{Out-of-sample } R^2 = 0,0594$, cao hơn `REPORT_Interaction` ($0,0567$), xác nhận biến tương tác không giúp ích cho dự báo ngoài mẫu.
4. **`residual_error_by_report_level.csv` & `top10_largest_errors.csv`**:
   - Chỉ ra rằng mô hình dự báo chính xác nhất ở vùng trung tâm `REPORT = 3` ($\text{MAE} = 0,284$, $\text{RMSE} = 0,348$) và có sai số lớn hơn ở hai biên `REPORT = 1` và `REPORT = 5` ($\text{MAE} \approx 1,84–1,87$) do đặc tính co về trung bình của hồi quy tuyến tính trên biến Likert rời rạc.

---

## TẬP KẾT QUẢ 6: KIỂM THỬ ÂM BẢN (NEGATIVE TESTS) & CHI PHÍ TÍNH TOÁN (BƯỚC 11)

1. **`results/tables/negative_tests_report.csv`**:
   - Chứa kết quả kiểm thử 8 kịch bản (`T01` $\rightarrow$ `T08`): 1 kịch bản dữ liệu chuẩn (`ACCEPT`) và 7 kịch bản cố tình tiêm lỗi (xóa cột `COMM1`, gán `ATT1=9`, gán `TOOL=2`, trùng `respondent_id`, chèn `NaN`, nhân bản dòng câu trả lời, truyền bảng rỗng).
   - Cả **8/8 kịch bản đều đạt `test_passed = True`**, chứng minh hệ thống phòng vệ chất lượng dữ liệu hoạt động chính xác 100%.
2. **`artifacts/runtime_benchmark.csv`**:
   - Ghi nhận chi phí tính toán cực kỳ nhẹ của toàn bộ pipeline:
     - Kiểm tra dữ liệu (`Stage_03`): **$\approx 13\text{ ms}$**, RAM đỉnh **$0,29\text{ MB}$**.
     - Ước lượng CFA (`Stage_04a`): **$\approx 168\text{ ms}$**, RAM đỉnh **$1,14\text{ MB}$**, hội tụ sau **51 vòng lặp SLSQP**.
     - Ước lượng SEM Baseline (`Stage_04b`): **$\approx 121\text{ ms}$**, RAM đỉnh **$1,20\text{ MB}$**, hội tụ sau **32 vòng lặp SLSQP**.
     - Ước lượng SEM Interaction (`Stage_05`): **$\approx 131\text{ ms}$**, RAM đỉnh **$1,27\text{ MB}$**, hội tụ sau **32 vòng lặp SLSQP**.
