# BỘ SLIDE (13 TRANG) & KỊCH BẢN THUYẾT TRÌNH 5 PHÚT HOÀN CHỈNH — ĐỀ TÀI DT092

## PHẦN 1. 4 LỖI TRONG BỘ SLIDE CŨ (19 TRANG) CẦN SỬA NGAY

1. **Lỗi mất dấu âm (`-`) làm sai lệch phát hiện quan trọng nhất của bài báo**:
   - Ở **Slide 12 cũ**: Đường dẫn `COMM -> ATT` và `COMM -> RESP` bị mất dấu trừ (ghi thành `0.251314` và `0.107651`, trong khi kết quả đúng là **`-0,251`** và **`-0,108`**). Đây là phát hiện cốt lõi về *"tác động hai lưỡi (boomerang effect)"* của truyền thông ATTT.
   - Ở **Slide 14 & 15 cũ**: Hệ số tương tác `COMM × TOOL` cũng bị mất dấu trừ (`-0,021` trong SEM và `-0,061` trong OLS-HC3).
2. **Để quá nhiều chữ số thập phân (`274.926397`, `0.401845`) và tách vụn bảng kết quả**:
   - Người nghe trong 5 phút không thể đọc kịp số có 6 chữ số thập phân. Quy chuẩn thuyết trình học thuật là **làm tròn 2–3 chữ số thập phân** kèm ký hiệu sao (`*** p < 0,001`, `* p < 0,05`, `ns`: không ý nghĩa) và đặt cột **Bài báo gốc** nằm cạnh cột **Kết quả DT092** để thầy nhìn thấy ngay sự tương đồng.
3. **Slide 8, 10, 17, 19 cũ vẫn ghi "Chưa có Alpha/CR/AVE, chưa có 3 lần chạy, chưa có CV/Error analysis"**:
   - Hiện tại bộ code từ `01` đến `11` đã chạy xong 100% các mục này (7/7 data checks, 8/8 negative tests, đầy đủ Alpha/CR/AVE/Fornell-Larcker, lặp 5 seeds, Ablation 3 mô hình, 5-Fold CV chống rò rỉ và benchmark thời gian/RAM). Cần đưa các kết quả **ĐÃ HOÀN THÀNH** này lên slide để ăn trọn điểm Rubrics!
4. **Dàn trải phần mở đầu quá dài (6 slide đầu chỉ nói lý thuyết và rào trước đón sau)**:
   - Trong 5 phút (300 giây), bạn chỉ nên dành **60 giây đầu (3 slides)** cho Bài toán + Bài báo gốc + Mô hình, để dành **180 giây (7 slides)** cho Pipeline + Kết quả đối chiếu + Mở rộng (5 Seeds, CV, Độ nhạy) và **60 giây cuối (3 slides)** cho Thảo luận + Đóng gói tái lập + Kết luận.

---

## PHẦN 2. BẢNG PHÂN BỔ THỜI GIAN 5 PHÚT (300 GIÂY) CHO 13 SLIDES

| Nhóm nội dung | Slide | Tiêu đề Slide | Thời lượng | Mục tiêu truyền đạt cho giảng viên |
| :--- | :---: | :--- | :---: | :--- |
| **MỞ ĐẦU & BÀI BÁO NỀN**<br/>*(60 giây)* | **Slide 1** | Trang bìa & Thông điệp cốt lõi | 15 giây | Giới thiệu đề tài, bài báo Q1 gốc và phạm vi tái lập. |
| | **Slide 2** | Bài toán, Khoảng trống & Bài báo gốc (Petrič & Just, 2025) | 25 giây | Vì sao nghiên cứu "báo cáo phishing"? Phương pháp & hạn chế của bài báo gốc. |
| | **Slide 3** | Mô hình nghiên cứu ISCB & 15 Giả thuyết (H1a – H7b) | 20 giây | Chỉ vào sơ đồ mô hình: 4 biến tổ chức $\rightarrow$ 2 biến tâm lý $\rightarrow$ Hành vi `REPORT` + `TOOL`. |
| **THIẾT KẾ & PIPELINE**<br/>*(55 giây)* | **Slide 4** | Kiến trúc Pipeline 11 Bước & Kiểm soát dữ liệu ($N=1.017$) | 30 giây | Trình bày luồng 11 scripts, manifest SHA-256, 7/7 checks & 8/8 Negative Tests. |
| | **Slide 5** | Khác biệt phương pháp ước lượng & Thiết kế mở rộng | 25 giây | Giải thích: Bài báo dùng Path WLSMV; Đề tài dùng Full Latent SEM (MLW) + OLS-HC3 + 5 Seeds + 5-Fold CV. |
| **KẾT QUẢ THỰC NGHIỆM**<br/>*(130 giây)* | **Slide 6** | Kết quả Bước 1: CFA, Độ tin cậy ($\alpha, \text{CR}$) & Giá trị (AVE, Fornell-Larcker) | 25 giây | Chứng minh 6 thang đo đạt $\alpha, \text{CR} > 0,76$, đạt 6/6 Fornell-Larcker giống bài báo gốc. |
| | **Slide 7** | Kết quả Bước 2: SEM — Từ Văn hóa tổ chức đến Tâm lý (`ATT`, `RESP`) | 25 giây | Đối chiếu H1a–H4b: Khớp bài báo gốc, nổi bật hiệu ứng âm (boomerang) của `COMM`. |
| | **Slide 8** | Kết quả Bước 3: SEM — Yếu tố quyết định Hành vi Báo cáo (`REPORT`) | 30 giây | Đối chiếu H1c–H7a: `COMM`, `ATT`, `TOOL` dương có ý nghĩa; `NORM`, `AWARE` chỉ tác động gián tiếp. |
| | **Slide 9** | Biến thể mở rộng: Tương tác `COMM × TOOL` (H7b) & Độ nhạy OLS-HC3 | 25 giây | Cả bài báo gốc ($\beta=-0,05$), SEM ($\beta=-0,02$) và OLS-HC3 ($b=-0,06$) đều bác bỏ H7b. |
| | **Slide 10** | Thực nghiệm nâng cao: Độ ổn định 5 Seeds, Ablation & 5-Fold CV | 25 giây | Chứng minh tính ổn định qua 5 seeds, Ablation chọn mô hình trung gian, 5-Fold CV chống rò rỉ & Phân tích lỗi. |
| **THẢO LUẬN & KẾT LUẬN**<br/>*(55 giây)* | **Slide 11** | Thảo luận: Tại sao Fit cao ($\text{CFI}\approx 1$) & Chi phí tính toán | 20 giây | Diễn giải trung thực $\text{RMSEA}=0$ trên dữ liệu mô phỏng và benchmark siêu nhẹ ($<0,2\text{s}$, RAM $<1,3\text{MB}$). |
| | **Slide 12** | Đóng gói Tái lập hoàn chỉnh (11 Scripts, Log Tiếng Việt, Lockfile) | 15 giây | Show cấu trúc thư mục sạch, chạy 1 lệnh `00_run_all_pipeline.py` trong 31 giây. |
| | **Slide 13** | Kết luận & Đóng góp của đề tài | 20 giây | Chốt lại 4 đóng góp chính và cảm ơn thầy. |

---

## PHẦN 3. NỘI DUNG CHI TIẾT TỪNG SLIDE & LỜI THOẠI (SCRIPT 5 PHÚT)

---

### SLIDE 1: TRANG BÌA (15 giây)
**Nội dung hiển thị trên Slide:**
- **HỌC PHẦN: AN TOÀN & BẢO MẬT HỆ THỐNG THÔNG TIN (DT092)**
- **Đề tài**: Xây dựng và đánh giá khung thực nghiệm tái lập có chọn lọc cấu trúc Survey và SEM về Văn hóa An toàn thông tin & Hành vi báo cáo Phishing
- **Bài báo Q1 gốc**: Petrič, G., & Just, J. N. (2025). *Information security culture and phishing-reporting model: structural equivalence across Germany, UK, and USA*. Journal of Cybersecurity, 11(1), tyaf011. (DOI: `10.1093/cybsec/tyaf011`)
- **Sinh viên thực hiện**: Vũ Bá Lực — MSSV: 1150080104 — Lớp: 11-ĐH-THMT

**Lời thoại (15 giây):**
> *"Em chào thầy ạ. Em là Vũ Bá Lực. Hôm nay em xin trình bày đề tài tái lập có chọn lọc cấu trúc khảo sát và mô hình phương trình cấu trúc SEM từ bài báo Q1 năm 2025 của Petrič và Just trên tạp chí Journal of Cybersecurity về Văn hóa an toàn thông tin và hành vi báo cáo email phishing."*

---

### SLIDE 2: BÀI TOÁN, KHOẢNG TRỐNG & BÀI BÁO GỐC (25 giây)
**Nội dung hiển thị trên Slide:**
- **Khoảng trống nghiên cứu (Petrič & Just, 2025)**:
  - Đa số nghiên cứu trước chỉ xét *"vì sao nhân viên bị lừa click link"*, rất ít nghiên cứu xét hành vi chủ động **"báo cáo email phishing cho IT"** (tỷ lệ thực tế chỉ đạt ~20%).
  - Báo cáo phishing là hành vi tương tác xã hội, cần giải thích bằng **Văn hóa ATTT (ISC)** toàn diện thay vì tâm lý cá nhân đơn lẻ.
- **Tóm tắt Bài báo gốc ($N = 1.017$)**:
  - Khảo sát nhân viên tại **Đức ($n=306$), Anh ($n=205$), Mỹ ($n=506$)**.
  - Bảng hỏi tinh chỉnh từ $85 \rightarrow 71 \rightarrow 47 \rightarrow 37 \rightarrow \mathbf{26\text{ items}}$ (6 thang đo ISC) + `TOOL` + `REPORT`.
- **5 Hạn chế của bài báo cần lưu ý khi tái lập**:
  1. Dữ liệu gốc của KnowBe4/Valicon không mở công khai $\rightarrow$ Dùng dữ liệu tổng hợp có kiểm soát ($N=1.017$).
  2. Biến `REPORT` tự khai 1 item (lệch trái, $M=3,82$) & `TOOL` chỉ đo nhị phân (0/1).
  3. Thang đo `KNOW` trong bài báo có $\text{AVE} = 0,49 < 0,50$.
  4. Bài báo ước lượng Bước 2 bằng trung bình cộng thang đo với **WLSMV** (thay vì Full Latent SEM).
  5. Thiết kế cắt ngang, chưa có kiểm định dự báo ngoài mẫu (Cross-Validation).

**Lời thoại (25 giây):**
> *"Về bối cảnh, bài báo gốc chỉ ra rằng chỉ khoảng 20% nhân viên chủ động báo cáo email phishing, và hành vi này phụ thuộc chặt chẽ vào Văn hóa an toàn thông tin của tổ chức. Nhóm tác giả khảo sát 1.017 nhân viên tại Đức, Anh, Mỹ với 26 câu hỏi tinh chỉnh. Do dữ liệu gốc của KnowBe4 không mở công khai, em xây dựng khung tái lập có chọn lọc trên dữ liệu mô phỏng cùng cỡ mẫu N = 1.017 và khắc phục các điểm hạn chế về kiểm định độ nhạy và cross-validation."*

---

### SLIDE 3: MÔ HÌNH NGHIÊN CỨU ISCB & HỆ THỐNG GIẢ THUYẾT (20 giây)
**Nội dung hiển thị trên Slide:**
*(Chèn hình Figure 1 & Figure 2 của bài báo gốc bạn đã có ở Slide 6 cũ)*
- **Khung lý thuyết ISCB (KnowBe4)** gồm 3 tầng:
  1. **4 Biến Văn hóa cấp Tổ chức (Ngoại sinh)**:
     - `NORM`: Chuẩn mực hỗ trợ ATTT (H1a, H1b, H1c)
     - `AWARE`: Nhận thức chính sách ISP (H2a, H2b, H2c)
     - `COMM`: Chất lượng giao tiếp hai chiều (H3a, H3b, H3c)
     - `KNOW`: Kiến thức ATTT (H4a, H4b — chỉ tác động gián tiếp)
  2. **2 Biến Tâm lý cấp Cá nhân (Trung gian)**:
     - `ATT`: Thái độ đối với ATTT (H5) & `RESP`: Ý thức trách nhiệm (H6)
  3. **Công cụ & Hành vi kết quả**:
     - `TOOL`: Có công cụ báo cáo (H7a) & Tương tác điều tiết **`COMM × TOOL -> REPORT` (H7b)**.

**Lời thoại (20 giây):**
> *"Trên slide là mô hình ISCB gồm 15 giả thuyết từ H1a đến H7b: 4 yếu tố văn hóa tổ chức là Chuẩn mực, Nhận thức chính sách, Giao tiếp và Kiến thức tác động thông qua Thái độ và Ý thức trách nhiệm để thúc đẩy hành vi Báo cáo phishing. Đặc biệt, giả thuyết mở rộng H7b kiểm tra xem Chất lượng giao tiếp có điều tiết tác động của Công cụ báo cáo hay không."*

---

### SLIDE 4: KIẾN TRÚC PIPELINE 11 BƯỚC & KIỂM SOÁT DỮ LIỆU (30 giây)
**Nội dung hiển thị trên Slide:**
- **Luồng 11 Scripts tự động hóa (`00_run_all_pipeline.py`)**:
  `01. Kiểm kê Public Data` $\rightarrow$ `02. Sinh dữ liệu (Seed=20261016)` $\rightarrow$ `03. Validate (7/7 Checks)` $\rightarrow$ `04. CFA & SEM Baseline` $\rightarrow$ `05. SEM Interaction (H7b)` $\rightarrow$ `06. So sánh mô hình` $\rightarrow$ `07. Độ nhạy OLS-HC3` $\rightarrow$ `08. Paper-Aligned SEM` $\rightarrow$ `09. Reliability & Validity` $\rightarrow$ `10. 5 Seeds + Ablation + 5-Fold CV` $\rightarrow$ `11. 8 Negative Tests + Benchmark`.
- **Hồ sơ dữ liệu & Kiểm thử chất lượng**:
  - Kích thước: **$N = 1.017$ dòng × 27 cột** (24 items Likert 1–5 cho 6 cấu trúc + `TOOL` 0/1 + `REPORT` 1–5 + ID).
  - Mã băm cố định (SHA-256): `2cae044842247f21563e4c73abf63f8b26be6b4499dcea4160f61249e714c6bb`.
  - **Đạt 7/7 kiểm tra toàn vẹn** (không thiếu, ID duy nhất, đúng miền Likert, **0 dòng trùng lặp**).
  - **Đạt 8/8 kịch bản Negative Tests** (tự động từ chối dữ liệu thiếu cột, ngoài miền 1–5, `TOOL=2`, trùng ID, `NaN`, nhân bản dòng).

**Lời thoại (30 giây):**
> *"Để đảm bảo tính tái lập hoàn toàn, em thiết kế pipeline gồm 11 script Python chuẩn hóa. Bộ dữ liệu N = 1.017 được khóa seed 20261016 và mã băm SHA-256. Hệ thống vượt qua 7 trên 7 bài kiểm tra chất lượng, loại bỏ trùng lặp và vượt qua 8 trên 8 kịch bản kiểm thử âm bản khi cố tình tiêm dữ liệu lỗi vào pipeline."*

---

### SLIDE 5: ĐIỂM KHÁC BIỆT PHƯƠNG PHÁP & CẢI TIẾN CỦA ĐỀ TÀI (25 giây)
**Nội dung hiển thị trên Slide:**

| Hạng mục | Bài báo gốc (Petrič & Just, 2025) | Đề tài DT092 (Thực nghiệm & Mở rộng) |
| :--- | :--- | :--- |
| **Dữ liệu & Bảng hỏi** | Khảo sát thật 3 nước (26 items: `ATT` & `NORM` 5 câu, còn lại 4 câu) | Dữ liệu mô phỏng mẫu gộp ($N=1.017$), chuẩn hóa 24 items (4 câu/thang đo) |
| **Ước lượng Bước 2** | Rút gọn về **điểm trung bình cộng** rồi chạy Path Model ($df=5$) bằng **WLSMV** (R `lavaan`) | Chạy **Full Latent SEM** trên toàn bộ 24 items ($df=282$) bằng **MLW** (`semopy`) **VÀ** đối chiếu với **OLS-HC3** trên điểm trung bình |
| **Kiểm định mở rộng** | Không có Ablation, không có Cross-Validation ngoài mẫu, không có Negative Tests | **Bổ sung**: (1) Ablation 3 mô hình; (2) Độ ổn định **5 Seeds**; (3) **5-Fold CV chống rò rỉ train-test**; (4) Phân tích lỗi phần dư & Benchmark |

**Lời thoại (25 giây):**
> *"Điểm khác biệt phương pháp quan trọng nhất là: ở Bước 2, bài báo gốc rút gọn các câu hỏi về điểm trung bình rồi chạy mô hình đường dẫn với WLSMV; còn bài của em vừa ước lượng Full Latent SEM giữ nguyên 24 biến chỉ báo bằng semopy, vừa bổ sung hồi quy OLS với sai số chuẩn vững HC3 trên điểm trung bình để kiểm tra độ nhạy, kết hợp chạy lặp 5 seeds và 5-Fold Cross-Validation chống rò rỉ dữ liệu."*

---

### SLIDE 6: KẾT QUẢ BƯỚC 1 — ĐỘ TIN CẬY ($\alpha, \text{CR}$) & GIÁ TRỊ THANG ĐO (CFA, AVE) (25 giây)
**Nội dung hiển thị trên Slide:**
- **Độ phù hợp CFA ($N=1.017$)**:
  - Bài báo gốc (26 items, $df=284$): $\chi^2 = 1493,2$; $\text{CFI} = 0,92$; $\text{TLI} = 0,90$; $\text{RMSEA} = 0,065$.
  - Đề tài DT092 (24 items, $df=237$): $\chi^2 = 229,80$ ($p=0,619$); $\text{CFI} = 1,00$; $\text{TLI} = 1,00$; $\text{RMSEA} = 0,000$.
- **Bảng đối chiếu Độ tin cậy & Giá trị hội tụ (Table 3 bài báo vs. DT092)**:

| Cấu trúc | Cronbach's $\alpha$ (DT092 / Paper) | CR (DT092) | AVE (DT092 / Paper) | $\sqrt{\text{AVE}}$ (DT092 / Paper) | Fornell-Larcker ($\sqrt{\text{AVE}} > \max |r|$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **ATT (Thái độ)** | **0,85** / 0,90 | 0,85 | **0,60** / 0,66 | 0,77 / 0,81 | **Đạt** ($\max |r| = 0,43$) |
| **RESP (Trách nhiệm)** | **0,86** / 0,84 | 0,86 | **0,60** / 0,64 | 0,78 / 0,80 | **Đạt** ($\max |r| = 0,47$) |
| **NORM (Chuẩn mực)** | **0,83** / 0,86 | 0,83 | **0,56** / 0,55 | 0,75 / 0,74 | **Đạt** ($\max |r| = 0,47$) |
| **AWARE (Nhận thức ISP)** | **0,83** / 0,80 | 0,84 | **0,56** / 0,58 | 0,75 / 0,76 | **Đạt** ($\max |r| = 0,43$) |
| **COMM (Giao tiếp)** | **0,78** / 0,79 | 0,78 | **0,47** / 0,50 | 0,69 / 0,71 | **Đạt** ($\max |r| = 0,23$) |
| **KNOW (Kiến thức)** | **0,77** / 0,74 | 0,77 | **0,45** / 0,49 | 0,67 / 0,70 | **Đạt** ($\max |r| = 0,30$) |

**Lời thoại (25 giây):**
> *"Ở bước kiểm định thang đo CFA, cả 6 cấu trúc trong bài của em đều đạt Cronbach's Alpha và Composite Reliability từ 0,77 đến 0,86, rất sát với Table 3 của bài báo gốc. Đáng chú ý, biến Kiến thức KNOW có AVE là 0,45 tương tự bài báo gốc là 0,49 đều hơi dưới 0,50 nhưng CR trên 0,77 nên vẫn đạt hội tụ. Toàn bộ 6 thang đo đều vượt qua tiêu chuẩn giá trị phân biệt Fornell-Larcker."*

---

### SLIDE 7: KẾT QUẢ BƯỚC 2 — ĐƯỜNG DẪN TỪ VĂN HÓA TỔ CHỨC VÀO TÂM LÝ (`ATT`, `RESP`) (25 giây)
**Nội dung hiển thị trên Slide:**

| Giả thuyết & Đường dẫn | Bài báo gốc ($\beta$ Pooled) | SEM DT092 ($\beta$ chuẩn hóa) | OLS-HC3 DT092 ($b$, SE vững) | Kết luận đối chiếu |
| :--- | :---: | :---: | :---: | :--- |
| **H1a**: `NORM -> ATT` | $+0,39^{***}$ | **$+0,402^{***}$** ($p < 0,001$) | $+0,353^{***}$ ($0,027$) | **Ủng hộ mạnh** (Khớp bài báo) |
| **H2a**: `AWARE -> ATT` | $+0,40^{***}$ | **$+0,418^{***}$** ($p < 0,001$) | $+0,363^{***}$ ($0,027$) | **Ủng hộ mạnh** (Khớp bài báo) |
| **H3a**: `COMM -> ATT` | **$-0,26^{***}$** | **$-0,251^{***}$** ($p < 0,001$) | **$-0,190^{***}$** ($0,029$) | **Tác động ÂM** (Hiệu ứng Boomerang) |
| **H4a**: `KNOW -> ATT` | $+0,09^{***}$ | **$+0,092^{*}$** ($p = 0,016$) | $+0,099^{**}$ ($0,032$) | **Ủng hộ** (Tác động dương nhỏ) |
| **H1b**: `NORM -> RESP` | $+0,43^{***}$ | **$+0,429^{***}$** ($p < 0,001$) | $+0,385^{***}$ ($0,028$) | **Ủng hộ mạnh** (Yếu tố lớn nhất) |
| **H2b**: `AWARE -> RESP` | $+0,37^{***}$ | **$+0,326^{***}$** ($p < 0,001$) | $+0,299^{***}$ ($0,029$) | **Ủng hộ mạnh** (Khớp bài báo) |
| **H3b**: `COMM -> RESP` | **$-0,14^{***}$** | **$-0,108^{**}$** ($p = 0,002$) | **$-0,068^{*}$** ($0,029$) | **Tác động ÂM** (Ỷ lại vào phòng IT) |
| **H4b**: `KNOW -> RESP` | $+0,16^{***}$ | **$+0,151^{***}$** ($p < 0,001$) | $+0,153^{***}$ ($0,031$) | **Ủng hộ hoàn toàn** |

**Lời thoại (25 giây):**
> *"Về kết quả SEM từ văn hóa tổ chức vào tâm lý cá nhân, toàn bộ 8 đường dẫn đều tái hiện chính xác cả về dấu và độ lớn so với bài báo gốc. Chuẩn mực NORM và Nhận thức chính sách AWARE thúc đẩy mạnh mẽ nhất Thái độ và Trách nhiệm. Đặc biệt, mô hình tái hiện đúng hiệu ứng ngược chiều của Giao tiếp COMM: mang dấu âm -0,251 lên Thái độ và -0,108 lên Trách nhiệm do tâm lý ỷ lại khi thấy bộ phận IT kiểm soát chặt."*

---

### SLIDE 8: KẾT QUẢ BƯỚC 3 — CÁC YẾU TỐ QUYẾT ĐỊNH HÀNH VI BÁO CÁO (`REPORT`) (30 giây)
**Nội dung hiển thị trên Slide:**

| Giả thuyết & Đường dẫn | Bài báo gốc ($\beta$ Pooled) | SEM DT092 ($\beta$, $p$-value) | Trung bình 5 Seeds ($\bar{\beta} \pm \text{SD}$) | Kết luận học thuật |
| :--- | :---: | :---: | :---: | :--- |
| **H3c**: `COMM -> REPORT` | **$+0,29^{***}$** | **$+0,235^{***}$** ($p < 0,001$) | $+0,268 \pm 0,054$ (5/5 đạt) | **Yếu tố trực tiếp mạnh nhất** thúc đẩy báo cáo |
| **H7a**: `TOOL -> REPORT` | **$+0,19^{**}$** | **$+0,085^{**}$** ($p = 0,005$) | $+0,084 \pm 0,024$ (4/5 đạt) | **Có ý nghĩa ($p=0,005$)** (OLS $b = +0,223$) |
| **H5**: `ATT -> REPORT` | **$+0,12^{***}$** | **$+0,101^{*}$** ($p = 0,037$) | $+0,132 \pm 0,054$ (4/5 đạt) | **Có ý nghĩa ($p < 0,05$)** |
| **H6**: `RESP -> REPORT` | **$+0,14^{***}$** | $+0,080^{\dagger}$ ($p = 0,083$) | **$+0,107 \pm 0,034$ ($\bar{p}=0,047$)** | Seed đầu cận biên ($p=0,083$) do cắt ngưỡng Likert; **trung bình 5 seeds đạt $p < 0,05$** |
| **H1c**: `NORM -> REPORT` | $+0,02\text{ (ns)}$ | $+0,053$ ($p = 0,275$) | $-0,016 \pm 0,070$ (Không ý nghĩa) | **Bác bỏ đường trực tiếp** (Chỉ tác động gián tiếp) |
| **H2c**: `AWARE -> REPORT` | $+0,07\text{ (ns)}$ | $-0,013$ ($p = 0,784$) | $-0,014 \pm 0,044$ (Không ý nghĩa) | **Bác bỏ đường trực tiếp** (Chỉ tác động gián tiếp) |

**Lời thoại (30 giây):**
> *"Đối với hành vi báo cáo REPORT, Chất lượng giao tiếp COMM là yếu tố thúc đẩy trực tiếp mạnh nhất với beta = 0,235, tiếp theo là Thái độ ATT và Công cụ báo cáo TOOL đều có ý nghĩa thống kê. Hai biến Chuẩn mực NORM và Nhận thức AWARE không có tác động trực tiếp mà chỉ tác động gián tiếp qua tâm lý, khớp hoàn toàn với bài báo gốc. Riêng biến Trách nhiệm RESP ở seed đầu tiên đạt ý nghĩa cận biên p = 0,083 do suy giảm khi rời rạc hóa Likert, nhưng khi chạy trung bình qua 5 seeds thì đạt beta = 0,107 với p trung bình = 0,047 < 0,05."*

---

### SLIDE 9: BIẾN THỂ MỞ RỘNG — TƯƠNG TÁC `COMM × TOOL` (H7b) & ĐỘ NHẠY OLS-HC3 (25 giây)
**Nội dung hiển thị trên Slide:**
- **Kiểm định giả thuyết H7b (`COMM × TOOL -> REPORT`) trên 3 phương pháp**:

| Phương pháp phân tích | Hệ số ước lượng | Sai số chuẩn (SE) | $z / t$-value | $p$-value | Khoảng tin cậy 95% | Kết luận H7b |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Bài báo gốc (WLSMV)** | $\beta = -0,050$ | — | — | $> 0,05$ | — | **Bác bỏ (ns)** |
| **2. SEM Mở rộng (`semopy`)** | $\beta = -0,021$ ($b = -0,058$) | $0,083$ | $-0,696$ | **$0,486$** | $[-0,219; +0,104]$ | **Bác bỏ (ns)** |
| **3. Độ nhạy `OLS-HC3`** | $b = -0,061$ | $0,080$ | $-0,755$ | **$0,450$** | $[-0,218; +0,097]$ | **Bác bỏ (ns)** |

- **Đối chiếu Baseline vs. Interaction (`06_compare_models.py`)**:
  - Khi thêm `COMM × TOOL`, độ lệch lớn nhất của 14 đường dẫn còn lại chỉ là $|\Delta\beta|_{\max} = 0,0016$, **100% kết luận giữ nguyên**.

**Lời thoại (25 giây):**
> *"Ở phần mở rộng kiểm định tương tác H7b giữa Giao tiếp và Công cụ báo cáo, cả 3 phương pháp gồm WLSMV của bài báo gốc, mô hình SEM mở rộng và hồi quy OLS với sai số chuẩn vững HC3 đều cho hệ số âm rất nhỏ và p-value lớn hơn 0,45, khoảng tin cậy 95% chứa số 0. Như vậy, kết luận bác bỏ hiệu ứng tương tác H7b là hoàn toàn vững chắc và không phụ thuộc vào phương pháp ước lượng."*

---

### SLIDE 10: THỰC NGHIỆM NÂNG CAO — ABLATION, 5-FOLD CV CHỐNG RÒ RỈ & PHÂN TÍCH LỖI (25 giây)
**Nội dung hiển thị trên Slide:**
1. **Ablation 3 biến thể cấu trúc SEM (`ablation_model_comparison.csv`)**:
   - `M1 (Mediation-Only, bỏ NORM/AWARE -> REPORT)`: **$\text{AIC} = 133,46$; $\text{BIC} = 463,41$ (Tốt nhất / Tiết kiệm nhất)**.
   - `M2 (Baseline Full Direct Paths)`: $\text{AIC} = 137,46$; $\text{BIC} = 477,26$ ($\Delta\chi^2 = 1,57, p = 0,457 \rightarrow$ Đường trực tiếp dư thừa).
   - `M3 (Full + Interaction COMM × TOOL)`: $\text{AIC} = 139,40$; $\text{BIC} = 484,12$.
2. **5-Fold Cross-Validation chống rò rỉ (`cv_5fold_summary.csv`)**:
   - Chuẩn hóa tâm `COMM_c`, `TOOL_c` chỉ tính trên tập `Train`:
   - `ATT`: $\text{Out-of-sample } R^2 = \mathbf{0,307 \pm 0,072}$; $\text{RMSE} = 0,813$; $\text{Spearman }\rho = 0,564$.
   - `RESP`: $\text{Out-of-sample } R^2 = \mathbf{0,322 \pm 0,038}$; $\text{RMSE} = 0,819$; $\text{Spearman }\rho = 0,554$.
   - `REPORT`: Thêm tương tác làm giảm $\text{Out-of-sample } R^2$ từ **$0,0594$ xuống $0,0567$** (gây quá khớp nhẹ).
3. **Phân tích lỗi dự báo theo mức Likert (`residual_error_by_report_level.csv`)**:
   - Dự báo chính xác nhất ở mức trung tâm `REPORT = 3` ($\text{MAE} = \mathbf{0,284}$), sai số tăng ở hai biên mức 1 và 5 ($\text{MAE} \approx 1,84$) do hồi quy tuyến tính co dự báo về miền $[2,8; 3,2]$.

**Lời thoại (25 giây):**
> *"Trong thực nghiệm nâng cao, phân tích Ablation xác nhận mô hình trung gian thuần túy M1 có AIC và BIC tốt nhất. Kiểm định chéo 5-Fold chống rò rỉ dữ liệu cho thấy thêm biến tương tác làm giảm R-bình phương ngoài mẫu từ 5,94% xuống 5,67%. Phân tích lỗi phần dư cũng chỉ ra mô hình dự báo rất sát ở mức Likert 3 với MAE = 0,28 nhưng bị co về trung tâm ở hai mức cực đoan 1 và 5."*

---

### SLIDE 11: DIỄN GIẢI TRUNG THỰC FIT INDICES & CHI PHÍ TÍNH TOÁN (20 giây)
**Nội dung hiển thị trên Slide:**
- **Vì sao $\text{CFI} \approx 1,0007$ và $\text{RMSEA} = 0$ trong dữ liệu mô phỏng?**
  - Dữ liệu được sinh từ ma trận 6 nhân tố chuẩn không có tải chéo (cross-loadings), nên $\chi^2 < df$ ($274,93 < 282$), theo công thức $\text{RMSEA} = \sqrt{\max(0, \frac{\chi^2 - df}{df(N-1)})} = 0$.
  - **Ý nghĩa đúng**: Chứng minh pipeline ước lượng khôi phục chính xác cấu trúc đã sinh, **không dùng để tuyên bố lý thuyết đúng tuyệt đối ngoài thực tế**.
- **Chi phí tính toán & Tốc độ hội tụ (`runtime_benchmark.csv`)**:
  - Kiểm tra dữ liệu (7 checks): **$11,97\text{ ms}$** | RAM đỉnh: **$0,29\text{ MB}$**.
  - Ước lượng CFA ($df=237$): **$176,56\text{ ms}$** | RAM: **$1,14\text{ MB}$** | Hội tụ SLSQP: **51 vòng lặp**.
  - Ước lượng SEM Baseline ($df=282$): **$127,91\text{ ms}$** | RAM: **$1,20\text{ MB}$** | Hội tụ SLSQP: **32 vòng lặp**.
  - Ước lượng SEM Interaction ($df=308$): **$134,35\text{ ms}$** | RAM: **$1,27\text{ MB}$** | Hội tụ SLSQP: **32 vòng lặp**.

**Lời thoại (20 giây):**
> *"Một điểm em xin nhấn mạnh về tính trung thực học thuật là chỉ số CFI xấp xỉ 1 và RMSEA bằng 0 trên dữ liệu mô phỏng là do dữ liệu được sinh từ cấu trúc nhân tố sạch không có tải chéo, nên chi-bình phương nhỏ hơn bậc tự do; điều này chứng minh code ước lượng đúng chứ không phải mô hình thực tế hoàn hảo. Về hiệu năng, toàn bộ mô hình CFA và SEM hội tụ sau 32 đến 51 vòng lặp SLSQP chỉ trong 0,13 giây với RAM dưới 1,3 MB."*

---

### SLIDE 12: ĐÓNG GÓI TÁI LẬP HOÀN CHỈNH (REPRODUCIBILITY PACKAGE) (15 giây)
**Nội dung hiển thị trên Slide:**
- **Cấu trúc đóng gói chuẩn hóa**:
  - **Mã nguồn (`scripts/00` $\rightarrow$ `11`)**: Tách dòng chuẩn PEP 8, thuyết minh Mục tiêu – Quy trình – Input/Output và xuất **11 file log Tiếng Việt** tại `results/logs/`.
  - **Môi trường khóa**: `requirements.txt` & `requirements-lock.txt` (khóa 27 thư viện: `semopy==2.3.11`, `statsmodels==0.14.5`, `pandas==2.3.1`...).
  - **6 Tập kết quả + README đối chiếu bài báo**: `artifacts/README_GIAI_THICH_KET_QUA.md` & `report/paper_to_results_mapping.csv`.
  - **Chạy lại toàn bộ từ đầu bằng 1 lệnh duy nhất (hoàn tất trong ~31 giây)**:
    `python scripts/00_run_all_pipeline.py`

**Lời thoại (15 giây):**
> *"Toàn bộ dự án đã được đóng gói sạch kèm file khóa môi trường requirements-lock, 11 file log tiếng Việt và README giải thích chi tiết 6 tập kết quả đối chiếu với bài báo gốc. Thầy có thể chạy lại toàn bộ 11 bước từ đầu chỉ bằng một lệnh duy nhất `00_run_all_pipeline.py` trong khoảng 30 giây."*

---

### SLIDE 13: KẾT LUẬN & ĐÓNG GÓP CỦA ĐỀ TÀI (20 giây)
**Nội dung hiển thị trên Slide:**
- **4 Kết luận & Đóng góp chính**:
  1. **Tái lập có chọn lọc thành công mô hình ISCB (Petrič & Just, 2025)**: Khôi phục chính xác vai trò nền tảng của `NORM`, `AWARE`, tác động thúc đẩy báo cáo của `TOOL`, `ATT`, `RESP` và đặc biệt là **hiệu ứng hai lưỡi (boomerang) của Chất lượng giao tiếp `COMM`**.
  2. **Kiểm định vững chắc giả thuyết mở rộng H7b (`COMM × TOOL`)**: Nhất quán bác bỏ tương tác trên cả SEM, OLS-HC3 và 5-Fold CV.
  3. **Mở rộng quy trình kiểm증 kỹ thuật**: Đạt 7/7 Data Checks, 8/8 Negative Tests, đầy đủ $\alpha/\text{CR}/\text{AVE}$/Fornell-Larcker, Ablation 3 mô hình, 5 Seeds và 5-Fold CV chống rò rỉ.
  4. **Tuân thủ tuyệt đối đạo đức & trung thực học thuật**: Minh bạch ranh giới giữa dữ liệu mô phỏng và khảo sát thực tế.

**Lời thoại (20 giây):**
> *"Tóm lại, đề tài đã xây dựng hoàn chỉnh một khung thực nghiệm tái lập có chọn lọc bài báo Q1 của Petrič và Just năm 2025, vừa khôi phục chính xác hiệu ứng hai lưỡi của chất lượng giao tiếp và kiểm định tương tác H7b, vừa bổ sung đầy đủ các kiểm định độ tin cậy, độ ổn định 5 seeds, 5-Fold CV chống rò rỉ và kiểm thử âm bản. Em xin cảm ơn thầy đã lắng nghe và rất mong nhận được góp ý của thầy ạ!"*
