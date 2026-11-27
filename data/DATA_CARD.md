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

Theo thông tin nhóm cung cấp, Tùng đã tham chiếu Sheet/Excel danh mục và lịch của cửa hàng khi xây dựng `eval/benchmark.csv`. Nhóm đã tạo bộ chuyển đổi `scripts/import_rental_excel.py` đọc hai file Excel do Nam cung cấp và lưu bản trích đã ẩn danh `data/rental.private.json`. Bộ chuyển đổi dùng danh mục Excel mới và lịch từ `MIÊN.xlsx`, loại bỏ hoàn toàn cột tên khách, SĐT, tiền cọc, giá và ghi chú (chỉ giữ 5 trường: `ma_ao`, `size`, `nhan_luc`, `tra_luc`, `trang_thai`); dữ liệu lịch trích xuất là **dữ liệu thực đã ẩn danh**, không phải synthetic.

Ngày 27/11/2026, bản trích được cập nhật từ hai Google Sheet: 85 mã trong danh mục và 263 dòng lịch mã AD (sau khi xác nhận sửa dòng 89 `AD09` ngày trả `02/10` → `02/11` và loại dòng 206 `AD09` ghi `"Chỉ quần"` do khách chỉ thuê lẻ quần, không giữ áo dài). Đã bỏ qua mã phụ kiện PK, ba dòng phụ kiện không mã theo xác nhận của Nam và các mã dự phòng trống. Ba dòng size M, M, XL thuộc nhóm ô gộp AD50 ở dòng 180–183 được bổ sung thông tin từ ô đầu nhóm theo ảnh Nam cung cấp; Nam xác nhận ngày 15–16/11. Có 33 dòng AD hiệu lực thiếu size hoặc nội dung size phức tạp được đánh dấu `KHONG_RO`; cần xác minh khi liên quan. Bản trích không tự đồng bộ khi Sheet thay đổi.

**Quyền sử dụng & bảo mật:** Chủ cửa hàng đã đồng ý cho nhóm đưa bản trích lịch **đã ẩn danh** (`data/rental.private.json`, không chứa tên khách, SĐT hay thông tin tài chính) vào repo để cả nhóm và giám khảo tái lập kết quả. File Excel/Sheet gốc chứa thông tin khách hàng tuyệt đối không commit lên repo (đã chặn `*.xlsx`, `*.xls` trong `.gitignore`).

**Phạm vi và dữ liệu thiếu:** chủ cửa hàng cho biết dữ liệu đáng tin từ 01/11/2026. Bộ kiểm tra không kết luận cho truy vấn trước mốc đó và vẫn xét đơn cuối tháng 10 nếu thời gian giặt có thể kéo sang 01/11. Sáu dòng thiếu mã đã được Nam phân loại: ba dòng phụ kiện và ba dòng tiếp nối đơn AD50. Các dòng áo dài thiếu size hoặc ngày vẫn phải kiểm tra riêng.

**Ghi chú:** Bản chạy thử mặc định đọc `data/rental.private.json` (`RENTAL_DATA_SOURCE=private`); có thể chuyển sang dữ liệu giả lập bằng `RENTAL_DATA_SOURCE=mock`.
