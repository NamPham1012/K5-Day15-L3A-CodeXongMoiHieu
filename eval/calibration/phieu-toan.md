# Phiếu chấm độc lập — Toàn hoặc Nam

Chấm đầu ra B01–B05 trong `cp2-output.csv` theo `expected` và `pass_criterion`; không xem phiếu người chấm khác trước khi hoàn thành. Điền 1 nếu đạt, 0 nếu không đạt; ghi lý do ngắn. B02 cần ghi thêm lưu ý nguồn chưa được xác minh.

| Câu | Pass (1/0) | Lý do |
|---|---|---|
| B01 | 0 | Chỉ thông báo cú pháp, không báo size hoặc giờ giả định. |
| B02 | 0 | Chỉ thông báo cú pháp, không báo size hoặc giờ; nguồn đáp án còn cần xác minh. |
| B03 | 0 | Chỉ thông báo cú pháp, không báo size S hoặc giờ giả định. |
| B04 | 1 | Báo không tìm thấy mã AD99. |
| B05 | 0 | Báo thứ tự giờ không hợp lệ nhưng chưa yêu cầu cung cấp lại ngày như tiêu chí. |

