# DT092 — Phishing-reporting culture: Giai đoạn 2

## Mục đích
Bộ công cụ này tạo dữ liệu **tổng hợp, không phải phản hồi của người thật** (N=1.017) để kiểm thử quy trình chuẩn bị dữ liệu và làm đầu vào cho CFA/SEM với Python + semopy. Dữ liệu công khai được kiểm kê/đối chiếu riêng; không tự động ghép các dòng của dữ liệu công khai với dữ liệu tổng hợp.

Mô hình trong YAML là **giả định mô phỏng ban đầu**, cần đối chiếu với phiếu tái lập Giai đoạn 1 và bài báo gốc trước khi coi là bản tái lập chính xác. Hệ số là tham số sinh dữ liệu, không phải kết quả ước lượng thực nghiệm.

## Cài đặt (Windows PowerShell)
Khuyến nghị Python 3.11:
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/02_generate_synthetic.py --config config/model_config.yml
python scripts/03_validate_data.py --input data/simulated/synthetic_sem.csv
```
Nếu `py -3.11` không có, dùng Python đã cài và ghi phiên bản thực tế vào manifest/log.

## Dữ liệu công khai
Ứng viên để đánh giá phù hợp: https://zenodo.org/records/7443048 (DOI 10.5281/zenodo.7443048). Đây không mặc định là dataset thay thế trực tiếp cho mô hình. Tải từ trang nguồn, đọc giấy phép và bảng hỏi; lưu nguyên bản vào `data/raw/public/`, không ghi đè. Sau đó:
```powershell
python scripts/01_inspect_public_data.py --input data/raw/public
```
Script chỉ kiểm kê file, sheet, cột, kiểu dữ liệu, kích thước và tỷ lệ thiếu; không tự suy luận ý nghĩa biến. Hoàn thiện `artifacts/variable_mapping_template.csv` sau khi đọc nội dung từng câu hỏi. Ghi URL/DOI, ngày tải, giấy phép, phiên bản và SHA-256 vào `artifacts/data_manifest.csv`.

## Cấu trúc mô phỏng
- NORM: chuẩn mực hỗ trợ an toàn thông tin.
- AWARE: nhận thức chính sách an toàn thông tin.
- KNOW: kiến thức an toàn thông tin.
- COMM: chất lượng giao tiếp.
- ATT: thái độ đối với an toàn thông tin.
- RESP: ý thức trách nhiệm.
- TOOL: biến nhị phân giả lập về công cụ báo cáo.
- REPORT: tần suất báo cáo phishing Likert 1–5.

Mặc định: NORM/AWARE/COMM/KNOW dự báo ATT và RESP; COMM, TOOL, RESP, ATT và tương tác COMMxTOOL dùng trong phương trình REPORT. NORM/AWARE không có đường dẫn trực tiếp đến REPORT trong cấu hình này. Các đường dẫn và item là bản mô phỏng đề xuất, không phải khẳng định số item chính xác của bài báo. Cần chốt lại với phiếu tái lập.

## Kiểm soát chất lượng
Validator kiểm tra N, ID duy nhất, giá trị Likert 1–5, TOOL 0/1, missingness, cột bắt buộc, phân phối item và checksum. Đạt các kiểm tra kỹ thuật không chứng minh được giá trị cấu trúc hay độ phù hợp SEM.

## Tái lập
- Seed cố định trong YAML.
- Lưu YAML cùng CSV, manifest và log.
- Không sửa CSV đầu ra bằng tay; sửa cấu hình/logic thì lưu phiên bản mới.
- Dữ liệu tổng hợp dùng để kiểm thử khả năng khôi phục cấu trúc đã sinh, không chứng minh mô hình đúng trong nhân viên thật.
