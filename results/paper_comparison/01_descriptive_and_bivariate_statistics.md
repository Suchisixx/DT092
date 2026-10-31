# KẾT QUẢ 1: THỐNG KÊ MÔ TẢ VÀ TƯƠNG QUAN HAI BIẾN
**(Descriptive and Bivariate Statistics)**

---

## 1. Tổng quan mẫu nghiên cứu (Sample Characteristics)
Nghiên cứu được tiến hành trên tập dữ liệu khảo sát đa nhóm gồm **1.017 nhân viên** thuộc 3 quốc gia:
- **Đức (Germany - DE):** $N = 306$ ($30.1\%$)
- **Vương quốc Anh (United Kingdom - UK):** $N = 205$ ($20.2\%$)
- **Hoa Kỳ (United States - USA):** $N = 506$ ($49.8\%$)

Cơ cấu mẫu đại diện cho nhiều ngành nghề (Công nghệ, Y tế, Giáo dục, Sản xuất, Tài chính), các quy mô tổ chức (vừa, lớn, rất lớn) và các bậc học vấn khác nhau, hoàn toàn tương thích với **Table 1** trong bài báo gốc của *Petrič & Just (2025)*.

---

## 2. Thống kê mô tả các biến đo lường (Table 4)

Các biến tiềm ẩn về văn hóa và tâm lý được đo bằng thang đo Likert 5 mức độ ($1$: Hoàn toàn không đồng ý đến $5$: Hoàn toàn đồng ý). Biến `TOOL` là biến nhị phân ($0$: Không có, $1$: Có công cụ/nút báo cáo phishing chuyên dụng).

### Bảng đối chiếu Mẫu gộp (Pooled Sample, N = 1.017)

| Biến | Tên đầy đủ | Bài báo gốc: Mean (SD) | Dự án DT092: Mean (SD) | Chênh lệch ($\Delta$) | Thang điểm |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **REPORT** | Tần suất báo cáo email phishing | **3.82** (1.26) | **3.81** (1.10) | $-0.01$ | 1.0 – 5.0 |
| **ATT** | Thái độ đối với an toàn thông tin | **3.67** (1.10) | **3.48** (0.95) | $-0.19$ | 1.0 – 5.0 |
| **RESP** | Ý thức trách nhiệm an toàn thông tin | **3.68** (0.95) | **3.54** (0.95) | $-0.14$ | 1.0 – 5.0 |
| **KNOW** | Kiến thức an toàn thông tin | **3.20** (0.67) | **3.15** (0.88) | $-0.05$ | 1.0 – 5.0 |
| **COMM** | Chất lượng truyền thông an toàn thông tin | **3.60** (0.82) | **3.48** (0.89) | $-0.12$ | 1.0 – 5.0 |
| **NORM** | Chuẩn mực ủng hộ an toàn thông tin | **3.29** (0.99) | **3.25** (0.95) | $-0.04$ | 1.0 – 5.0 |
| **AWARE** | Nhận thức & hiểu biết chính sách | **3.55** (0.88) | **3.39** (0.91) | $-0.16$ | 1.0 – 5.0 |
| **TOOL** | Tỷ lệ tổ chức có nút/công cụ báo cáo | **75.5%** | **75.3%** | $-0.2\%$ | 0.0 – 1.0 |

### Bảng chi tiết theo từng Quốc gia trong Dự án DT092

| Quốc gia | REPORT (SD) | ATT (SD) | RESP (SD) | KNOW (SD) | COMM (SD) | NORM (SD) | AWARE (SD) | TOOL (%) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Đức (DE)** | 3.79 (1.09) | 3.47 (0.96) | 3.52 (0.95) | 3.17 (0.85) | 3.48 (0.87) | 3.29 (0.93) | 3.35 (0.91) | **66.7%** |
| **Anh (UK)** | 3.84 (1.10) | 3.49 (0.97) | 3.59 (0.98) | 3.08 (0.87) | 3.44 (0.88) | 3.32 (0.98) | 3.45 (0.94) | **76.6%** |
| **Mỹ (US)** | 3.81 (1.11) | 3.48 (0.94) | 3.53 (0.94) | 3.17 (0.90) | 3.49 (0.90) | 3.21 (0.95) | 3.39 (0.91) | **80.0%** |

---

## 3. Ma trận tương quan hai biến (Table 5 bài báo gốc vs Table 3 dự án)

Hệ số tương quan Pearson giữa các cặp biến chính trong nghiên cứu:

| Cặp biến tương quan | Bài báo gốc ($r$) | Dự án DT092 ($r$) | Ý nghĩa thống kê ($p$) | Đánh giá so sánh |
| :--- | :---: | :---: | :---: | :--- |
| **COMM — REPORT** | **0.34** | **0.22** | $p < 0.001$ | Tương quan dương mạnh nhất với hành vi báo cáo. |
| **AWARE — REPORT** | **0.27** | **0.22** | $p < 0.001$ | Khớp định hướng: Nhận thức tốt thúc đẩy báo cáo. |
| **RESP — REPORT** | **0.21** | **0.19** | $p < 0.001$ | Tương quan dương mức độ trung bình. |
| **KNOW — REPORT** | **0.21** | **0.12** | $p < 0.001$ | Tương quan dương nhẹ. |
| **ATT — REPORT** | **0.17** | **0.15** | $p < 0.001$ | Khớp sát sao ($\Delta = 0.02$). |
| **TOOL — REPORT** | **~0.19** | **0.19** | $p < 0.001$ | Khớp tuyệt đối: Có tool giúp tăng tần suất báo cáo. |
| **ATT — RESP** | **0.76** | **0.36 – 0.49** | $p < 0.001$ | Cặp biến tâm lý có tương quan nội tại mạnh nhất. |
| **NORM — ATT** | **0.67** | **0.41** | $p < 0.001$ | Chuẩn mực tổ chức gắn kết chặt chẽ với thái độ cá nhân. |

---

## 4. Những điểm rút ra cốt lõi cho tài liệu / báo cáo
1. **Xu hướng báo cáo tích cực:** Điểm trung bình `REPORT` đạt xấp xỉ **$3.81/5.0$**, và có hơn $60\%$ người tham gia cho biết họ thường xuyên hoặc rất thường xuyên báo cáo các email đáng ngờ.
2. **Sự phổ biến của công cụ kỹ thuật:** Khoảng **$75\%$** tổ chức đã trang bị nút bấm hoặc plugin báo cáo phishing tiện lợi trên giao diện email của nhân viên.
3. **Mối liên kết giữa truyền thông và hành vi:** Chất lượng truyền thông nội bộ (`COMM`) là yếu tố có tương quan cao nhất tới việc nhân viên chủ động gửi cảnh báo về email độc hại cho phòng IT.
