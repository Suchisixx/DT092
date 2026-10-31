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

| Chỉ số Fit | Ngưỡng chuẩn mực khoa học | Bài báo gốc (lavaan / WLSMV) | Dự án DT092 (semopy / MLW) | Đánh giá đạt chuẩn |
| :--- | :---: | :---: | :---: | :---: |
| **Chi-square ($\chi^2$)** | Càng nhỏ càng tốt ($p > 0.05$) | $\chi^2 = 22.46$ | $\chi^2 = 281.36$ | Đạt |
| **Bậc tự do ($df$)** | Phụ thuộc cấu trúc mô hình | $df = 5$ *(chỉ xét path)* | $df = 308$ *(full latent SEM)* | Đạt |
| **$p$-value** | $> 0.05$ (không bác bỏ mô hình) | $p < 0.001$ | $p = 0.860$ | Đạt lý tưởng |
| **CFI (Comparative Fit Index)** | $\ge 0.90$ (Tốt: $\ge 0.95$) | **0.92** | **1.00** | Đạt xuất sắc |
| **TLI (Tucker-Lewis Index)** | $\ge 0.90$ (Tốt: $\ge 0.95$) | **0.95** | **1.00** | Đạt xuất sắc |
| **RMSEA** | $\le 0.08$ (Tốt: $\le 0.05$) | **0.059** | **0.000** | Đạt xuất sắc |
| **SRMR** | $\le 0.08$ (Tốt: $\le 0.05$) | **0.005** | **0.022** | Đạt xuất sắc |

*Ghi chú phương pháp:* Bài báo gốc sử dụng ước lượng biến thứ bậc WLSMV trên biến quan sát gộp, trong khi dự án DT092 áp dụng semopy với ước lượng Maximum Likelihood vững (MLW) trên mô hình biến tiềm ẩn đầy đủ (full latent measurement + structural). Cả hai phương pháp đều xác nhận mô hình đạt độ tương thích thống kê rất cao với dữ liệu.

---

## 3. Khả năng giải thích phương sai ($R^2$) của mô hình

| Biến nội sinh (Phụ thuộc) | Bài báo gốc ($R^2$) | Dự án DT092 ($R^2$) | Ý nghĩa thực tiễn |
| :--- | :---: | :---: | :--- |
| **ATT** (Thái độ an toàn thông tin) | **61.1%** | **64.2%** | Các yếu tố văn hóa tổ chức giải thích hơn 60% thái độ của nhân viên. |
| **RESP** (Ý thức trách nhiệm an toàn) | **65.2%** | **67.1%** | Các yếu tố văn hóa tổ chức giải thích gần 70% ý thức trách nhiệm. |
| **REPORT** (Hành vi báo cáo phishing) | **23.5%** | **18.7%** | Dự báo được khoảng 1/5 đến 1/4 biến thiên trong hành vi thực tế. |

---

## 4. Trọng số đường dẫn cấu trúc mẫu gộp (Pooled Path Coefficients)

### Giai đoạn 1: Từ Văn hóa tổ chức $\rightarrow$ Nhận thức & Tâm lý nhân viên
| Đường dẫn cấu trúc | Giả thuyết | Hệ số bài gốc ($\beta$) | Hệ số DT092 ($\beta$) | Mức chênh lệch | Mức ý nghĩa ($p$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **NORM $\rightarrow$ ATT** | H1a | **0.39** | **0.403** | $+0.013$ | $p < 0.001$ |
| **AWARE $\rightarrow$ ATT** | H2a | **0.40** | **0.349** | $-0.051$ | $p < 0.001$ |
| **COMM $\rightarrow$ ATT** | H3a | **-0.26** | **-0.223** | $+0.037$ | $p < 0.001$ |
| **KNOW $\rightarrow$ ATT** | H4a | **0.09** | **0.060** | $-0.030$ | $p = 0.114$ |
| **NORM $\rightarrow$ RESP** | H1b | **0.43** | **0.469** | $+0.039$ | $p < 0.001$ |
| **AWARE $\rightarrow$ RESP** | H2b | **0.37** | **0.345** | $-0.025$ | $p < 0.001$ |
| **COMM $\rightarrow$ RESP** | H3b | **-0.14** | **-0.178** | $-0.038$ | $p < 0.001$ |
| **KNOW $\rightarrow$ RESP** | H4b | **0.16** | **0.118** | $-0.042$ | $p = 0.001$ |

### Giai đoạn 2: Từ Tâm lý & Bối cảnh kỹ thuật $\rightarrow$ Hành vi báo cáo Phishing
| Đường dẫn cấu trúc | Giả thuyết | Hệ số bài gốc ($\beta$) | Hệ số DT092 ($\beta$) | Mức chênh lệch | Mức ý nghĩa ($p$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **COMM $\rightarrow$ REPORT** | H3c | **0.29** | **0.213** | $-0.077$ | $p < 0.001$ |
| **TOOL $\rightarrow$ REPORT** | H7a | **0.19** | **0.182** | $-0.008$ | $p < 0.001$ |
| **RESP $\rightarrow$ REPORT** | H6 | **0.14** | **0.092** | $-0.048$ | $p = 0.057$ |
| **ATT $\rightarrow$ REPORT** | H5 | **0.12** | **0.070** | $-0.050$ | $p = 0.107$ |
| **NORM $\rightarrow$ REPORT** | H1c | **0.02** | **0.018** | $-0.002$ | $p = 0.724$ (Không ý nghĩa) |
| **AWARE $\rightarrow$ REPORT** | H2c | **0.07** | **0.106** | $+0.036$ | $p = 0.021$ |
| **COMM $\times$ TOOL $\rightarrow$ REPORT** | H7b | **-0.05** | **0.019** | $+0.069$ | $p = 0.515$ (Không ý nghĩa) |

---

## 5. Những điểm rút ra cốt lõi cho tài liệu / báo cáo
1. **Khung lý thuyết vững chắc:** Mô hình giải thích cực kỳ tốt sự hình thành thái độ và trách nhiệm của nhân viên ($R^2 > 60\%$), với các chuẩn mực tổ chức (`NORM`) và sự nhận biết chính sách (`AWARE`) đóng vai trò động lực chính.
2. **Động lực trực tiếp thúc đẩy báo cáo:** Trong mô hình gộp, việc nhân viên có chủ động báo cáo email lừa đảo hay không phụ thuộc trực tiếp vào **Chất lượng truyền thông (`COMM`)** và **Sự hiện diện của công cụ kỹ thuật (`TOOL`)**, thay vì các chuẩn mực chung chung.
3. **Hiệu ứng tương tác không đáng kể:** Cả bài gốc lẫn dự án đều chứng minh biến tương tác $\text{COMM} \times \text{TOOL}$ không có ý nghĩa thống kê ở mẫu chung ($p > 0.05$), nghĩa là công cụ kỹ thuật phát huy tác dụng độc lập mà không bắt buộc phải đi kèm truyền thông dày đặc.
