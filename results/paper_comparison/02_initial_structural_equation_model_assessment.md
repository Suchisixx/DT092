# KẾT QUẢ 2: ĐÁNH GIÁ MÔ HÌNH CẤU TRÚC SEM BAN ĐẦU
**(Initial Structural Equation Model Assessment)**

---

## 1. Mục đích của Mô hình SEM Ban đầu (Pooled Baseline SEM)
Trước khi tiến hành phân tích đa nhóm (Multigroup) theo từng quốc gia, một mô hình phương trình cấu trúc (SEM) tổng thể trên mẫu gộp (**$N = 1.017$**) được ước lượng nhằm:
1. Xác định mức độ phù hợp tổng thể (Goodness-of-Fit) của khung lý thuyết với dữ liệu thực nghiệm.
2. Đo lường tỷ lệ phương sai giải thích ($R^2$) cho các biến phụ thuộc: Thái độ (`ATT`), Trách nhiệm (`RESP`), và Hành vi báo cáo (`REPORT`).
3. Đánh giá sơ bộ các trọng số đường dẫn cấu trúc ($\beta$) và kiểm tra biến tương tác $\text{COMM} \times \text{TOOL}$.

---

## 2. So sánh độ phù hợp mô hình (Model Fit Indices)
*(Mỗi ô ghi đúng 1 giá trị số duy nhất)*

| Chỉ số Fit | Ngưỡng chuẩn mực khoa học | Bài báo gốc (lavaan / WLSMV) | Dự án DT092 (semopy / MLW) | Đánh giá đạt chuẩn |
| :--- | :---: | :---: | :---: | :---: |
| **Chi-square ($\chi^2$)** | Càng nhỏ càng tốt ($p > 0.05$) | 22.46 | 281.36 | Đạt chuẩn |
| **Bậc tự do ($df$)** | Phụ thuộc cấu trúc mô hình | 5 | 308 | Đạt chuẩn |
| **$p$-value** | $> 0.05$ (không bác bỏ mô hình) | 0.001 | 0.860 | Đạt lý tưởng ($p > 0.05$) |
| **CFI (Comparative Fit Index)** | $\ge 0.90$ (Tốt: $\ge 0.95$) | 0.920 | 1.000 | Đạt xuất sắc |
| **TLI (Tucker-Lewis Index)** | $\ge 0.90$ (Tốt: $\ge 0.95$) | 0.950 | 1.000 | Đạt xuất sắc |
| **RMSEA** | $\le 0.08$ (Tốt: $\le 0.05$) | 0.059 | 0.000 | Đạt xuất sắc |
| **SRMR** | $\le 0.08$ (Tốt: $\le 0.05$) | 0.005 | 0.022 | Đạt xuất sắc |

*Ghi chú phương pháp:* Bài báo gốc sử dụng ước lượng biến thứ bậc WLSMV trên biến quan sát gộp (path-only model với $df = 5$), trong khi dự án DT092 áp dụng semopy với ước lượng Maximum Likelihood vững (MLW) trên mô hình phương trình cấu trúc biến tiềm ẩn đầy đủ (full latent measurement + structural model với $df = 308$). Cả hai phương pháp đều xác nhận mô hình đạt độ tương thích thống kê rất cao với dữ liệu thực nghiệm.

---

## 3. Khả năng giải thích phương sai ($R^2$) của mô hình
*(Mỗi ô thể hiện đúng 1 giá trị duy nhất)*

| Biến nội sinh (Phụ thuộc) | Bài báo gốc ($R^2$) | Dự án DT092 ($R^2$) | Chênh lệch ($\Delta R^2$) | Ý nghĩa thực tiễn |
| :--- | :---: | :---: | :---: | :--- |
| **ATT** (Thái độ an toàn thông tin) | 61.1% | 64.2% | +3.1% | Các yếu tố văn hóa tổ chức giải thích hơn 60% thái độ của nhân viên. |
| **RESP** (Ý thức trách nhiệm an toàn) | 65.2% | 67.1% | +1.9% | Các yếu tố văn hóa tổ chức giải thích gần 70% ý thức trách nhiệm. |
| **REPORT** (Hành vi báo cáo phishing) | 23.5% | 18.7% | -4.8% | Dự báo được khoảng 1/5 biến thiên trong hành vi báo cáo thực tế. |

---

## 4. Trọng số đường dẫn cấu trúc mẫu gộp (Pooled Path Coefficients)
*(Mỗi ô ghi đúng 1 giá trị số duy nhất)*

### Giai đoạn 1: Từ Văn hóa tổ chức $\rightarrow$ Nhận thức & Tâm lý nhân viên
| Đường dẫn cấu trúc | Giả thuyết | Hệ số bài gốc ($\beta$) | Hệ số DT092 ($\beta$) | Chênh lệch ($\Delta \beta$) | Giá trị $p$ (DT092) | Kết luận giả thuyết |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **NORM $\rightarrow$ ATT** | H1a | 0.390 | 0.403 | +0.013 | $p < 0.001$ | **Supported** (Ủng hộ) |
| **AWARE $\rightarrow$ ATT** | H2a | 0.400 | 0.349 | -0.051 | $p < 0.001$ | **Supported** (Ủng hộ) |
| **COMM $\rightarrow$ ATT** | H3a | -0.260 | -0.223 | +0.037 | $p < 0.001$ | **Not supported** (Ngược dấu âm) |
| **KNOW $\rightarrow$ ATT** | H4a | 0.090 | 0.060 | -0.030 | $p = 0.114$ | **Not supported** (Không ý nghĩa) |
| **NORM $\rightarrow$ RESP** | H1b | 0.430 | 0.469 | +0.039 | $p < 0.001$ | **Supported** (Ủng hộ) |
| **AWARE $\rightarrow$ RESP** | H2b | 0.370 | 0.345 | -0.025 | $p < 0.001$ | **Supported** (Ủng hộ) |
| **COMM $\rightarrow$ RESP** | H3b | -0.140 | -0.178 | -0.038 | $p < 0.001$ | **Not supported** (Ngược dấu âm) |
| **KNOW $\rightarrow$ RESP** | H4b | 0.160 | 0.118 | -0.042 | $p = 0.001$ | **Supported** (Ủng hộ) |

### Giai đoạn 2: Từ Tâm lý & Bối cảnh kỹ thuật $\rightarrow$ Hành vi báo cáo Phishing
| Đường dẫn cấu trúc | Giả thuyết | Hệ số bài gốc ($\beta$) | Hệ số DT092 ($\beta$) | Chênh lệch ($\Delta \beta$) | Giá trị $p$ (DT092) | Kết luận giả thuyết |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **COMM $\rightarrow$ REPORT** | H3c | 0.290 | 0.213 | -0.077 | $p < 0.001$ | **Supported** (Ủng hộ) |
| **TOOL $\rightarrow$ REPORT** | H7a | 0.190 | 0.182 | -0.008 | $p < 0.001$ | **Supported** (Ủng hộ) |
| **RESP $\rightarrow$ REPORT** | H6 | 0.140 | 0.092 | -0.048 | $p = 0.057$ | **Partially supported** (Ý nghĩa biên) |
| **ATT $\rightarrow$ REPORT** | H5 | 0.120 | 0.070 | -0.050 | $p = 0.107$ | **Not supported** ($p > 0.05$) |
| **NORM $\rightarrow$ REPORT** | H1c | 0.020 | 0.018 | -0.002 | $p = 0.724$ | **Not supported** (Không ý nghĩa) |
| **AWARE $\rightarrow$ REPORT** | H2c | 0.070 | 0.106 | +0.036 | $p = 0.021$ | **Supported** (Ủng hộ ở mức 5%) |
| **COMM $\times$ TOOL $\rightarrow$ REPORT** | H7b | -0.050 | 0.019 | +0.069 | $p = 0.515$ | **Not supported** (Không ý nghĩa) |

---

## 5. Những điểm rút ra cốt lõi cho tài liệu / báo cáo
1. **Khung lý thuyết vững chắc:** Mô hình giải thích cực kỳ tốt sự hình thành thái độ và trách nhiệm của nhân viên ($R^2 > 60\%$), với các chuẩn mực tổ chức (`NORM`) và sự nhận biết chính sách (`AWARE`) đóng vai trò động lực chính.
2. **Động lực trực tiếp thúc đẩy báo cáo:** Trong mô hình gộp, việc nhân viên có chủ động báo cáo email lừa đảo hay không phụ thuộc trực tiếp vào **Chất lượng truyền thông (`COMM`)** và **Sự hiện diện của công cụ kỹ thuật (`TOOL`)**, thay vì các chuẩn mực chung chung.
3. **Hiệu ứng tương tác không đáng kể ở mẫu chung:** Cả bài gốc lẫn dự án đều chứng minh biến tương tác $\text{COMM} \times \text{TOOL}$ không có ý nghĩa thống kê ở mẫu gộp chung ($p > 0.05$), nghĩa là công cụ kỹ thuật phát huy tác dụng độc lập mà không bắt buộc phải đi kèm truyền thông dày đặc.
