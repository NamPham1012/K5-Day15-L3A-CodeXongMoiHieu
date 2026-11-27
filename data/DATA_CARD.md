# Data card — nguồn dữ liệu và giới hạn

## Dataset 1 · Mock cho bản chạy thử

| Thuộc tính | Chi tiết |
|---|---|
| File | `data/mock_rental.json` trong repo |
| Mục đích | `get_mock_data` và `check_availability` đọc để chạy bản mock và kiểm thử. |
| Nguồn / nhãn | Nhóm tự dựng thủ công, `synthetic`. Không phải bằng chứng pain. |
| Số lượng | 2 mẫu áo và 2 bản ghi lịch giả lập. |
| Cách tạo | Dựng tay theo cấu trúc mã áo, size, số lượng, thời gian và trạng thái; không dùng sinh ngẫu nhiên nên không có seed. |
| Giới hạn | Mẫu nhỏ, không đại diện lịch thực tế; không chứa các mã khác trong benchmark như AD26, AD09. Người kiểm và số dòng đã kiểm tay: nhóm bổ sung sau khi xác nhận. |

## Nguồn tham chiếu cho benchmark

Theo thông tin nhóm cung cấp, Tùng đã tham chiếu Sheet/Excel danh mục và lịch của cửa hàng khi xây dựng `eval/benchmark.csv`. Nhóm đã tạo bộ chuyển đổi `scripts/import_rental_excel.py` đọc hai file Excel do Nam cung cấp và lưu một bản trích cục bộ `data/rental.private.json`; file này không được commit. Bộ chuyển đổi dùng danh mục Excel mới và lịch từ `MIÊN.xlsx`, bỏ cột tên khách, tiền cọc, giá và ghi chú; dữ liệu lịch trích xuất vẫn là **dữ liệu thực**, không phải synthetic.

Ngày 27/11/2026, bản trích riêng được cập nhật từ hai Google Sheet: 85 mã trong danh mục và 263 dòng lịch mã AD (sau khi xác nhận sửa dòng 89 `AD09` ngày trả `02/10` → `02/11` và loại dòng 206 `AD09` ghi `"Chỉ quần"` do khách chỉ thuê lẻ quần, không giữ áo dài). Đã bỏ qua mã phụ kiện PK, ba dòng phụ kiện không mã theo xác nhận của Nam và các mã dự phòng trống. Ba dòng size M, M, XL thuộc nhóm ô gộp AD50 ở dòng 180–183 được bổ sung thông tin từ ô đầu nhóm theo ảnh Nam cung cấp; Nam xác nhận ngày 15–16/11. Có 33 dòng AD hiệu lực thiếu size hoặc nội dung size phức tạp được đánh dấu `KHONG_RO`; cần xác minh khi liên quan. Bản trích không tự đồng bộ khi Sheet thay đổi.

Dữ liệu lịch thật và tên khách là dữ liệu nhạy cảm; chỉ sử dụng theo phạm vi BTC/coach chấp thuận, không đưa tên hoặc bản gốc dữ liệu khách vào repo công khai hay prompt model. Việc xác nhận quyền và xử lý các dữ liệu đã xuất hiện trong benchmark cần được nhóm kiểm tra.

**Phạm vi và dữ liệu thiếu:** chủ cửa hàng cho biết dữ liệu đáng tin từ 01/11/2026. Bộ kiểm tra nguồn riêng không kết luận cho truy vấn trước mốc đó và vẫn xét đơn cuối tháng 10 nếu thời gian giặt có thể kéo sang 01/11. Sáu dòng thiếu mã đã được Nam phân loại: ba dòng phụ kiện và ba dòng tiếp nối đơn AD50. Các dòng áo dài thiếu size hoặc ngày vẫn phải kiểm tra riêng.

**Ghi chú:** Chế độ mặc định vẫn dùng mock giả lập; `RENTAL_DATA_SOURCE=private` chọn bản trích cục bộ khi đã được phép. Trước khi đánh giá, cần thống nhất tập dữ liệu, bảo đảm người chạy có quyền dùng và đối chiếu từng đáp án; không sửa kết quả đã chạy hoặc đánh tráo nguồn. Không ghi trace/đầu ra chứa dữ liệu riêng lên repo công khai.
