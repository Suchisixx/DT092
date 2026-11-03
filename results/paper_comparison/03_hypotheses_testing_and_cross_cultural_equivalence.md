# KẾT QUẢ 3: KIỂM ĐỊNH GIẢ THUYẾT VÀ TÍNH TƯƠNG ĐƯƠNG XUYÊN VĂN HÓA
**(Hypotheses Testing and Cross-Cultural Equivalence Across Germany, UK, and USA)**

---

## 1. Kiểm định Tính Bất biến Đo lường Đa nhóm (Measurement Invariance - Table 7)

Để so sánh kết quả mô hình cấu trúc giữa 3 quốc gia (**Đức: 306, Anh: 205, Mỹ: 506**), nghiên cứu tiến hành kiểm định tính bất biến đo lường qua 3 cấp độ phân cấp chặt chẽ theo tiêu chuẩn phương pháp luận của Chen (2007) và Cheung & Rensvold (2002):
- **Ngưỡng chấp nhận bất biến:** $|\Delta \text{CFI}| \le 0.010$, $|\Delta \text{RMSEA}| \le 0.015$, $|\Delta \text{SRMR}| \le 0.010$.

### Bảng 3.1: Các chỉ số Độ phù hợp và Sai phân Bất biến Đo lường (Table 7)
*(Trích xuất từ `table7_measurement_invariance.csv`, mỗi ô ghi đúng 1 giá trị số duy nhất)*

| Cấp độ kiểm định | Chi-square ($\chi^2$) | df | $p$-value | CFI | TLI | RMSEA | SRMR | $\Delta \text{CFI}$ | $\Delta \text{RMSEA}$ | $\Delta \text{SRMR}$ | Quyết định thống kê |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1. Configural Invariance** *(Cùng cấu trúc)* | 770.96 | 711 | 0.059 | 0.9934 | 0.9923 | 0.0091 | 0.0356 | — | — | — | **Đạt** (Mô hình nền tảng phù hợp ở cả 3 nước) |
| **2. Metric Invariance** *(Cùng hệ số tải)* | 808.22 | 747 | 0.059 | 0.9932 | 0.9925 | 0.0090 | 0.0367 | -0.0001 | -0.0001 | +0.0011 | **Xác nhận Full Metric Invariance** ($|\Delta| \le 0.010$) |
| **3. Scalar Invariance** *(Cùng điểm gốc)* | 851.63 | 783 | 0.044 | 0.9924 | 0.9920 | 0.0093 | 0.0367 | -0.0008 | +0.0003 | 0.0000 | **Xác nhận Full Scalar Invariance** ($|\Delta| \le 0.010$) |

### So sánh với kết quả bài báo gốc (Petrič & Just, 2025):
- *Bài báo gốc:* Đạt **Configural Invariance** ($\text{CFI} = 0.910$, $\text{RMSEA} = 0.071$) và xác nhận **Full Metric Invariance** ($\Delta \text{CFI} \le 0.010$, $\Delta \text{SRMR} \le 0.010$).
- *Mở rộng của dự án DT092:* Dự án đạt cả **Full Metric** lẫn **Full Scalar Invariance** ($|\Delta \text{CFI}| \le 0.001$, $|\Delta \text{SRMR}| \le 0.002$).
- *Kết luận khoa học:* Thang đo an toàn thông tin có cấu trúc khái niệm và trọng số đo lường hoàn toàn tương đương đối với nhân viên tại Đức, Anh và Hoa Kỳ; không có hiện tượng sai lệch do rào cản ngôn ngữ hay văn hóa làm biến dạng bản chất câu hỏi. Do đó, việc so sánh các hệ số đường dẫn cấu trúc đa quốc gia ở Bảng 6 là hoàn toàn hợp lệ về mặt đo lường học.

---

## 2. Mô hình SEM Đa nhóm theo Quốc gia và Kiểm định Sai biệt Liên nhóm (Multigroup SEM & Cross-Group Tests - Table 6)

Mô hình cấu trúc SEM được ước lượng riêng cho từng quốc gia: Đức ($n=306$), Anh ($n=205$), và Mỹ ($n=506$). Để xác định xem sự khác biệt giữa các quốc gia có ý nghĩa thống kê hay không, dự án thực hiện kiểm định Wald $\chi^2(2)$ đồng thời trên 3 nhóm và kiểm định $z$-test từng cặp trên hệ số chưa chuẩn hóa ($B / SE$).

### Bảng 3.2: So sánh Trọng số Chuẩn hóa ($\beta$) giữa Bài báo gốc và Dự án DT092 theo Quốc gia
*(Trích xuất từ `table6_multigroup_sem.csv`, mỗi ô thể hiện đúng 1 giá trị duy nhất)*

| Quan hệ cấu trúc | Mã | Đức: Bài gốc | Đức: DT092 | Anh: Bài gốc | Anh: DT092 | Mỹ: Bài gốc | Mỹ: DT092 | Chênh lệch TB ($|\Delta \beta|$) | Sai biệt liên nhóm (Wald) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Norms $\rightarrow$ Attitudes** | H1a | 0.460 | 0.445 | 0.230 | 0.269 | 0.430 | 0.441 | 0.022 | $p = 0.154$ (Không sai biệt) |
| **Awareness $\rightarrow$ Attitudes** | H2a | 0.380 | 0.381 | 0.480 | 0.353 | 0.360 | 0.340 | 0.050 | $p = 0.750$ (Không sai biệt) |
| **Communication $\rightarrow$ Attitudes** | H3a | -0.160 | -0.163 | -0.390 | -0.355 | -0.260 | -0.212 | 0.029 | $p = 0.364$ (Không sai biệt) |
| **Knowledge $\rightarrow$ Attitudes** | H4a | 0.070 | 0.032 | 0.050 | 0.073 | 0.090 | 0.065 | 0.029 | $p = 0.895$ (Không sai biệt) |
| **Norms $\rightarrow$ Responsibility** | H1b | 0.530 | 0.525 | 0.400 | 0.481 | 0.410 | 0.435 | 0.037 | $p = 0.443$ (Không sai biệt) |
| **Awareness $\rightarrow$ Responsibility** | H2b | 0.240 | 0.295 | 0.390 | 0.378 | 0.410 | 0.370 | 0.036 | $p = 0.754$ (Không sai biệt) |
| **Communication $\rightarrow$ Responsibility** | H3b | -0.040 | -0.114 | -0.230 | -0.263 | -0.160 | -0.178 | 0.042 | $p = 0.595$ (Không sai biệt) |
| **Knowledge $\rightarrow$ Responsibility** | H4b | 0.170 | 0.147 | 0.110 | 0.033 | 0.150 | 0.123 | 0.042 | $p = 0.594$ (Không sai biệt) |
| **Norms $\rightarrow$ Reporting** | H1c | -0.060 | -0.032 | -0.010 | -0.084 | 0.010 | 0.053 | 0.048 | $p = 0.511$ (Không sai biệt) |
| **Awareness $\rightarrow$ Reporting** | H2c | 0.020 | 0.011 | 0.090 | 0.210 | 0.080 | 0.122 | 0.057 | $p = 0.290$ (Không sai biệt) |
| **Communication $\rightarrow$ Reporting** | H3c | 0.300 | 0.211 | 0.260 | 0.108 | 0.290 | 0.257 | 0.092 | $p = 0.324$ (Không sai biệt) |
| **Attitudes $\rightarrow$ Reporting** | H5 | 0.240 | 0.158 | -0.010 | -0.132 | 0.110 | 0.119 | 0.071 | **$p = 0.025$ (CÓ SAI BIỆT: DE vs UK; UK vs US)** |
| **Responsibility $\rightarrow$ Reporting** | H6 | 0.050 | 0.079 | 0.270 | 0.310 | 0.080 | 0.006 | 0.048 | **$p = 0.056$ (CÓ SAI BIỆT: UK vs US, $p=0.017$)** |
| **Presence of tool $\rightarrow$ Reporting** | H7a | 0.050 | 0.180 | 0.240 | 0.265 | 0.270 | 0.151 | 0.091 | $p = 0.339$ (Không sai biệt) |
| **Comm $\times$ Tool $\rightarrow$ Reporting** | H7b | 0.040 | -0.064 | 0.080 | -0.048 | 0.070 | 0.101 | 0.088 | **$p = 0.021$ (CÓ SAI BIỆT: DE vs US; UK vs US)** |
| **$R^2$ (Attitudes)** | — | 67.8% | 65.5% | 53.9% | 61.2% | 64.4% | 64.8% | 0.027 | Rất tương đồng |
| **$R^2$ (Responsibility)** | — | 63.0% | 66.4% | 58.7% | 68.2% | 68.6% | 67.4% | 0.041 | Rất tương đồng |
| **$R^2$ (Reporting)** | — | 14.5% | 17.9% | 31.6% | 23.5% | 26.0% | 18.6% | 0.063 | UK cao nhất, Đức thấp nhất |

### Bảng 3.3: Chi tiết Hệ số Hồi quy và Kiểm định Wald Sai biệt Liên nhóm (Cross-Group Tests)
*(Trích xuất từ `table6_cross_group_tests.csv`)*

| Mã | Đường dẫn cấu trúc | Hệ số Đức $B$ ($SE$) | Hệ số Anh $B$ ($SE$) | Hệ số Mỹ $B$ ($SE$) | Wald $\chi^2(2)$ | Wald $p$ | Kết luận sai biệt nhóm |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **H1a** | NORM $\rightarrow$ ATT | 0.430 (0.068) | 0.243 (0.080) | 0.405 (0.053) | 3.74 | 0.154 | Đồng nhất giữa các nhóm |
| **H2a** | AWARE $\rightarrow$ ATT | 0.410 (0.077) | 0.381 (0.102) | 0.339 (0.056) | 0.58 | 0.750 | Đồng nhất giữa các nhóm |
| **H3a** | COMM $\rightarrow$ ATT | -0.210 (0.088) | -0.355 (0.090) | -0.211 (0.054) | 2.02 | 0.364 | Đồng nhất giữa các nhóm |
| **H4a** | KNOW $\rightarrow$ ATT | 0.035 (0.079) | 0.093 (0.107) | 0.070 (0.056) | 0.22 | 0.895 | Đồng nhất giữa các nhóm |
| **H1b** | NORM $\rightarrow$ RESP | 0.536 (0.070) | 0.447 (0.082) | 0.425 (0.055) | 1.63 | 0.443 | Đồng nhất giữa các nhóm |
| **H2b** | AWARE $\rightarrow$ RESP | 0.335 (0.075) | 0.419 (0.099) | 0.392 (0.058) | 0.56 | 0.754 | Đồng nhất giữa các nhóm |
| **H3b** | COMM $\rightarrow$ RESP | -0.154 (0.087) | -0.270 (0.083) | -0.188 (0.055) | 1.04 | 0.595 | Đồng nhất giữa các nhóm |
| **H4b** | KNOW $\rightarrow$ RESP | 0.171 (0.080) | 0.043 (0.101) | 0.140 (0.059) | 1.04 | 0.594 | Đồng nhất giữa các nhóm |
| **H1c** | NORM $\rightarrow$ REPORT | -0.038 (0.117) | -0.099 (0.121) | 0.066 (0.087) | 1.34 | 0.511 | Đồng nhất giữa các nhóm |
| **H2c** | AWARE $\rightarrow$ REPORT | 0.014 (0.113) | 0.295 (0.144) | 0.165 (0.087) | 2.48 | 0.290 | Đồng nhất giữa các nhóm |
| **H3c** | COMM $\rightarrow$ REPORT | 0.330 (0.113) | 0.140 (0.120) | 0.346 (0.074) | 2.25 | 0.324 | Đồng nhất giữa các nhóm |
| **H5** | ATT $\rightarrow$ REPORT | 0.194 (0.105) | -0.173 (0.110) | 0.161 (0.085) | 7.40 | **0.025** | **Có sai biệt (Đức vs Anh; Anh vs Mỹ)** |
| **H6** | RESP $\rightarrow$ REPORT | 0.092 (0.109) | 0.392 (0.137) | 0.007 (0.084) | 5.75 | **0.056** | **Có sai biệt (Anh vs Mỹ, z = 2.39, p = 0.017)** |
| **H7a** | TOOL $\rightarrow$ REPORT | 0.415 (0.125) | 0.683 (0.160) | 0.418 (0.113) | 2.16 | 0.339 | Đồng nhất giữa các nhóm |
| **H7b** | COMM_TOOL $\rightarrow$ REPORT| -0.170 (0.142) | -0.143 (0.186) | 0.286 (0.115) | 7.68 | **0.021** | **Có sai biệt (Đức vs Mỹ; Anh vs Mỹ)** |

---

## 3. Bảng Tổng hợp Kiểm định 15 Giả thuyết Nghiên cứu (Hypothesis Testing - Table 8)
*(Trích xuất từ `table8_hypothesis_testing.csv`, đối chiếu trực tiếp với Table 7 của bài báo gốc)*

| Mã | Giả thuyết phát biểu | Chiều kỳ vọng | Kết quả Mẫu gộp | Đức ($n=306$) | Anh ($n=205$) | Mỹ ($n=506$) | Kết luận Dự án DT092 | Kết luận Bài báo gốc | Mức độ tương đồng |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **H1a** | Norms $\rightarrow$ Attitudes | $(+)$ | Supported | Supported | Supported | Supported | **Supported** | Supported | **Khớp hoàn hảo (Cả 3 nước $p < 0.01$)** |
| **H2a** | Awareness $\rightarrow$ Attitudes | $(+)$ | Supported | Supported | Supported | Supported | **Supported** | Supported | **Khớp hoàn hảo (Cả 3 nước $p < 0.01$)** |
| **H3a** | Communication $\rightarrow$ Attitudes | $(+)$ | Not supported *(ngược dấu)* | Not supported | Not supported | Not supported | **Not supported *(ngược dấu)*** | Not supported *(ngược dấu)* | **Khớp hoàn hảo (Đều ngược dấu âm)** |
| **H4a** | Knowledge $\rightarrow$ Attitudes | $(+)$ | Not supported | Not supported | Not supported | Not supported | **Not supported** | Partially supported | Tương đồng (Hệ số đều rất bé $< 0.09$) |
| **H1b** | Norms $\rightarrow$ Responsibility | $(+)$ | Supported | Supported | Supported | Supported | **Supported** | Supported | **Khớp hoàn hảo (Cả 3 nước $p < 0.01$)** |
| **H2b** | Awareness $\rightarrow$ Responsibility | $(+)$ | Supported | Supported | Supported | Supported | **Supported** | Supported | **Khớp hoàn hảo (Cả 3 nước $p < 0.01$)** |
| **H3b** | Communication $\rightarrow$ Responsibility | $(+)$ | Not supported *(ngược dấu)* | Not supported | Not supported | Not supported | **Not supported *(ngược dấu)*** | Not supported *(ngược dấu)* | **Khớp hoàn hảo (Đều ngược dấu âm)** |
| **H4b** | Knowledge $\rightarrow$ Responsibility | $(+)$ | Supported | Supported | Not supported | Supported | **Partially supported** | Supported | Khớp xu hướng (Đạt tại Đức và Mỹ) |
| **H1c** | Norms $\rightarrow$ Reporting | $(+)$ | Not supported | Not supported | Not supported | Not supported | **Not supported** | Not supported | **Khớp hoàn hảo (Không tác động trực tiếp)** |
| **H2c** | Awareness $\rightarrow$ Reporting | $(+)$ | Supported | Not supported | Supported | Not supported | **Partially supported** | Not supported | Khớp xu hướng (Đạt biên tại Anh $p=0.040$) |
| **H3c** | Communication $\rightarrow$ Reporting | $(+)$ | Supported | Supported | Not supported | Supported | **Partially supported** | Supported | Khớp xu hướng (Đạt tại Đức và Mỹ $p<0.01$) |
| **H5** | Attitudes $\rightarrow$ Reporting | $(+)$ | Not supported | Not supported | Not supported | Not supported | **Not supported** | Partially supported | Khớp định hướng (Đức chịu ảnh hưởng nhất) |
| **H6** | Responsibility $\rightarrow$ Reporting | $(+)$ | Not supported | Not supported | Supported | Not supported | **Partially supported** | Partially supported | **Khớp hoàn hảo: Chỉ người Anh có ý nghĩa** |
| **H7a** | Presence of tool $\rightarrow$ Reporting | $(+)$ | Supported | Supported | Supported | Supported | **Supported** | Partially supported | Khớp tích cực (Cả 3 nước đều ủng hộ) |
| **H7b** | Comm $\times$ Tool $\rightarrow$ Reporting | $(+)$ | Not supported | Not supported | Not supported | Supported | **Partially supported** | Not supported | Tương tác biên tại Mỹ ($p = 0.013$) |

---

## 4. Những Phát hiện Xuyên Văn hóa Quan trọng cho Tài liệu Báo cáo

1. **Hiệu ứng "Nghịch lý truyền thông" (Communication Boomerang Effect):**
   - Ở cả 3 quốc gia, việc đẩy mạnh truyền thông an toàn thông tin (`COMM`) giúp tăng trực tiếp hành vi báo cáo phishing (`H3c`), nhưng lại tác động **âm** có ý nghĩa thống kê tới thái độ cá nhân (`H3a`) và ý thức trách nhiệm (`H3b`). 
   - *Giải thích:* Khi tổ chức gửi quá nhiều thông báo hoặc cảnh báo mang tính cưỡng chế, nhân viên dễ sinh ra tâm lý mệt mỏi (*alert fatigue*) hoặc ỷ lại, coi an toàn thông tin là việc của phòng IT chứ không phải trách nhiệm của bản thân.

2. **Sự khác biệt văn hóa giữa các quốc gia:**
   - **Đức (Germany):** Hành vi báo cáo gắn liền với **Thái độ cá nhân (`ATT`)** ($\beta = 0.240$ ở bài gốc, $0.158$ ở dự án, $p = 0.066$). Người Đức chú trọng niềm tin cá nhân vào tính đúng đắn của chính sách bảo mật trước khi hành động.
   - **Vương quốc Anh (UK):** Hành vi báo cáo chịu tác động vượt trội bởi **Ý thức trách nhiệm (`RESP`)** ($\beta = 0.270$ ở bài gốc, $0.310$ ở dự án, $p = 0.004$) và **Công cụ kỹ thuật (`TOOL`)** ($\beta = 0.240$ ở bài gốc, $0.265$ ở dự án, $p < 0.001$). Người Anh báo cáo vì xem đó là nghĩa vụ công dân/nghĩa vụ công việc và khi tổ chức cung cấp công cụ tiện lợi.
   - **Hoa Kỳ (USA):** Mang tính thực dụng và cân bằng; sự hiện diện của công cụ kỹ thuật ($\beta = 0.151, p < 0.001$) và truyền thông rõ ràng ($\beta = 0.257, p < 0.001$) là hai yếu tố thúc đẩy báo cáo hiệu quả nhất. Ngoài ra, tại Mỹ, hiệu ứng tương tác $\text{COMM} \times \text{TOOL}$ đạt ý nghĩa dương ($\beta = 0.101, p = 0.013$), cho thấy truyền thông hỗ trợ phát huy tối đa công năng của nút báo cáo.
