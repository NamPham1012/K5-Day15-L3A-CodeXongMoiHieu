# Đối chiếu benchmark và nguồn dữ liệu — 27/11/2026

Đây là rà soát nguồn và khả năng chạy, **không phải kết quả chấm benchmark**. Bản chạy mặc định dùng `data/mock_rental.json` (chỉ AD02, AD03); benchmark phần lớn tham chiếu dữ liệu cửa hàng. Bản trích riêng cập nhật từ Sheet có thể chọn bằng `RENTAL_DATA_SOURCE=private`, nhưng không được commit; từ ngày 01/11 là phạm vi chủ quán xác nhận dữ liệu đầy đủ. Các câu trước mốc đó cần xác minh độc lập, không coi là đúng chỉ vì có trong lịch cũ. Ảnh chụp đầu ra 5 câu mock trong `eval/calibration/cp2-output.csv` không phải một lượt chính thức và chưa có kết quả hai người chấm.

## Đối chiếu từng câu

Kết quả dưới đây dựa trên bản trích riêng tại thời điểm rà soát và công cụ `scripts/audit_benchmark_data.py`, không chứng minh dữ liệu cửa hàng không còn thiếu sót. `Khớp` là khớp về dữ liệu đầu vào của công cụ, không phải AI đã trả lời đúng.

| Câu | Đối chiếu | Việc cần làm |
|---|---|---|
| B01 | AD26 ngày 10/11: công cụ cho M 1, XL 1, khớp expected. | Rà output thực tế khi đánh giá. |
| B02 | AD09 có dòng ngày bất thường; công cụ báo cần xác minh. Expected khẳng định đủ ba size. | Chủ quán xác minh dòng lịch bất thường rồi Tùng duyệt đáp án. |
| B03 | AD01 ngày 15/11: công cụ cho S 1, khớp expected. | Rà output thực tế. |
| B04 | AD99 không có trong danh mục. | Giữ; phân biệt mã không có với không còn hàng. |
| B05 | Ngày trả trước ngày nhận. | Giữ; cần báo lỗi ngày. |
| B06 | AD26 ngày 20/11: công cụ cho M 1, XL 0, khớp expected. | Rà output thực tế. |
| B07 | AD09: công cụ báo cần xác minh do dòng ngày bất thường, expected khẳng định các size. | Xác minh dữ liệu AD09 trước khi chấm. |
| B08 | Ngày 28/10 nằm trước phạm vi đáng tin. | Tùng xác minh bằng nguồn khác hoặc thay ca tháng 11 có căn cứ, không đoán. |
| B09 | Ngày 24–25/10 nằm trước phạm vi đáng tin. | Xác minh hoặc thay ca có căn cứ. |
| B10 | Ngày 19–20/10 nằm trước phạm vi đáng tin; ô size của đơn cũ đã được cập nhật L theo chủ quán. | Expected thiếu size không còn khớp Sheet; cần viết ca mới có dữ liệu thiếu thật hoặc synthetic ghi rõ. |
| B11 | Ngày 16/10 nằm trước phạm vi đáng tin; ô size của đơn cũ đã được cập nhật L. | Expected thiếu size không còn khớp Sheet; cần ca khác có căn cứ. |
| B12 | Đã chuyển sang 21/11: AD26 XL chưa sẵn sàng lúc 08:00 theo bản trích. | Đã đối chiếu công cụ; cần chấm output thật. |
| B13 | Đã chuyển sang 21/11: AD26 XL còn lúc 09:00 theo bản trích. | Đã đối chiếu công cụ; cần chấm output thật. |
| B14 | AD01 ngày 24/11: công cụ cho S 0, khớp expected. | Rà output thực tế. |
| B15 | Công cụ cho S/L/XL đều 1. Bản trích không có đơn AD02 trạng thái HỦY; expected đã sửa để không bịa đơn hủy. | Nếu muốn kiểm thử việc bỏ qua đơn hủy, tạo thêm ca có đơn hủy thật hoặc synthetic gắn nguồn. |
| B16 | Trả 22:00 bị từ chối theo quy tắc, không phụ thuộc tồn kho. | Đã chuyển ngày sang 28/11; giữ. |
| B17 | Danh mục hiện ghi S/L/XL mỗi size 1; không đủ 2 XL. Expected đã sửa tổng 2 thành 3. | Nhóm xác nhận danh mục mới là nguồn chuẩn. |
| B18 | Đã đổi sang 20/11: theo bản trích AD26 size XL trùng, size M còn. | Kiểm tra hành vi từ chối khi chạy AI. |
| B19 | Yêu cầu tiết lộ dữ liệu cá nhân; đã chuyển sang tháng 11, không cần biết tên khách. | Giữ tiêu chí từ chối. |
| B20 | Yêu cầu chốt đơn và thu tiền ngoài phạm vi. | Giữ tiêu chí từ chối. |

## Tình trạng chấm thử

- `eval/calibration/cp2-output.csv` lưu nguyên đầu ra B01–B05 của `python run.py eval --try 5`, chế độ mock; cột chấm còn trống.
- Tùng và Toàn (hoặc Nam) cần tự chấm độc lập theo `expected` và `pass_criterion`, điền hai phiếu `phieu-tung.md`, `phieu-toan.md`, sau đó so sánh. B02 có bất đồng nguồn phải ghi chú, không dùng nó làm bằng chứng chất lượng nguồn cho tới khi xác minh.
- Chưa có phiếu chấm đã hoàn thành, chưa tính tỷ lệ đồng thuận. Không đánh dấu đã đạt 4/5.
- Kết quả mock chỉ nhận đầu vào cố định và chưa gọi model thật. `run.py check` chỉ kiểm cấu trúc, không chứng minh benchmark đúng hoặc sản phẩm đạt chuẩn.

## Xác minh bổ sung AD09 trên Sheet

- Dòng 89: AD09 size L, nhận 01/11/2026, trả 02/10/2026; ngày trả trước ngày nhận. Cần chủ cửa hàng xác nhận, không tự sửa thành tháng 11.
- Dòng 206: AD09, cột size ghi `Chỉ quần`, không có ngày nhận/trả. Cần xác nhận ý nghĩa trước khi loại khỏi nguồn áo dài.
