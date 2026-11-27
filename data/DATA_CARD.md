# Data card — dữ liệu bản chạy thử dùng

> Điền ở guide bước 2.4 (bản đầu ở CP2, đủ ở CP3). Ôn lại: ngày 6 · lab ngày 6. Chấm ở rubric R4.
> Một trang. Mỗi dataset một mục. Dữ liệu chạy thử để trong thư mục `data/` này.
> Không commit nguyên tài liệu khoá, dữ liệu cá nhân thật hay nguyên file data BTC cấp — chỉ đoạn trích ngắn, bản viết lại, hoặc số đã tổng hợp.

## Dataset 1 · Dữ liệu danh mục áo dài và lịch thuê giả lập (synthetic)

| Thuộc tính | Chi tiết |
|---|---|
| **Dùng để làm gì** | Cung cấp dữ liệu nền giả lập cho các công cụ của bản chạy thử (`get_inventory`, `get_rentals`, `check_availability`) để tra cứu tồn kho theo size, kiểm tra lịch trùng và thời gian sẵn sàng; cung cấp ngữ cảnh thực nghiệm để sinh bộ câu thử `eval/benchmark.csv`. |
| **Từ đâu** | Nhóm tự dựng (`synthetic`) dựa trên cấu trúc mô hình hóa từ thực tế hoạt động của cửa hàng cho thuê áo dài tại Hòa Lạc (được trích xuất mẫu từ phỏng vấn và sổ sách ghi chép, đã loại bỏ toàn bộ dữ liệu cá nhân thật). |
| **Xử lý & Cách tạo** | 1. **Cách tạo (Synthetic Pipeline)**: Khởi tạo danh mục áo dài mẫu và sinh các bản ghi lịch thuê mô phỏng các tình huống thực tế (trùng lịch, lệch size, giặt ủi, đơn hủy, đơn đặt trước).<br>2. **Chuẩn hóa trường dữ liệu**: Chuyển đổi định dạng ngày giờ thập phân sang ISO chuẩn giờ Việt Nam (UTC+7); quy chuẩn hóa cú pháp size/số lượng (`2XL` là 2 áo XL, `XXL` là 1 áo XXL).<br>3. **Loại bỏ PII**: Thay thế toàn bộ tên khách hàng, số điện thoại, số tiền đặt cọc bằng mã định danh ẩn danh hoặc nhãn giả lập (`KH_01`, `Khách đặt trước`), tuyệt đối không lưu thông tin cá nhân khách thật.<br>4. **Gán nhãn trạng thái nghiệp vụ**: `Đã hoàn tất` (xét thời gian giặt đến 09:00 hôm sau), `Đang thuê`, `Khách đặt trước`, `Đang giặt`, `HỦY`. |
| **Số dòng / số bản ghi** | - **Danh mục áo dài**: 130 mã áo kèm phân loại size và số lượng tồn kho.<br>- **Bản ghi lịch thuê**: 281 bản ghi lịch thuê giả lập (gồm 196 bản ghi hoàn tất, 31 đặt trước, 15 đang thuê, 13 đang giặt, 2 đơn hủy, 24 đơn edge-case thiếu thông tin size để thử nghiệm). |
| **Phiên bản / ngày lấy** | Phiên bản synthetic v1.0 — ngày 27/11/2026. |
| **Nhãn** | `synthetic` (nhóm tự dựng và chuẩn hóa làm sạch). |
| **Giới hạn** | - Dữ liệu tập trung vào tháng 10–11/2026 (mô phỏng mùa kỷ yếu học sinh, sinh viên).<br>- Có chủ đích đưa vào các bản ghi khuyết thiếu (như 24 dòng thiếu size trong đơn, đơn trả sau 21:00) nhằm phục vụ việc kiểm thử khả năng gắn cờ cảnh báo của AI. |

**Data `synthetic` (nhóm tự dựng):** Dữ liệu được nhóm tổng hợp và làm sạch qua script chuẩn hóa; đã được kiểm duyệt thủ công 100% các trường để đảm bảo không chứa bất kỳ dữ liệu cá nhân thật nào của khách hàng. Data tự dựng phục vụ cho bản chạy thử và benchmark, không thay thế cho bằng chứng pain tại `evidence/`.
