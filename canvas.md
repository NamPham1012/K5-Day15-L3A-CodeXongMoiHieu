# Canvas — CodeXongMoiHieu · Track F




| #   | Dòng                         | Nhóm điền                                                                                                                                                                                                              |
| --- | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Track + lát cắt dự kiến      | Track F — hỗ trợ chủ cửa hàng kiểm tra lịch thuê áo dài theo từng size.                                                                                                                                                |
| 2   | Người dùng chính             | Chủ cửa hàng cho thuê áo dài ở Hòa Lạc, trực tiếp tiếp khách và quản lý lịch thuê bằng Google Sheets.                                                                                                                  |
| 3   | Pain                         | Khi khách hỏi thuê một mẫu áo theo khoảng ngày, chủ cửa hàng phải đối chiếu danh mục, size và lịch thuê thủ công; việc kiểm tra mất thời gian và có thể dẫn đến nhận trùng lịch.                                       |
| 4 | Bằng chứng đầu | Phạm Văn Nam phỏng vấn 1 chủ cửa hàng lúc 10:00 ngày 27/11/2026; theo lời chủ quán do Nam thuật lại, trong tuần phỏng vấn có 3 đơn bị nhầm lịch và quán phải xin lỗi, chọn áo khác cho khách. Chưa đối chiếu dữ liệu hoặc có trích dẫn nguyên văn: `evidence/interviews/P1.md`. |
| 5   | Lát cắt MỘT CÂU              | Chủ cửa hàng hỏi mã áo và khoảng ngày thuê; trợ lý diễn giải yêu cầu và dựa trên kết quả kiểm tra lịch để báo từng size còn, trùng hoặc cần xác minh, giúp chủ cửa hàng tư vấn khách.                                  |
| 6   | AI tự làm đến đâu            | AI diễn giải câu hỏi và trình bày kết quả; code xác định lịch, thiếu dữ liệu thì báo cần kiểm tra; chủ cửa hàng tự quyết định, xác nhận và cập nhật đơn.                                                               |
| 7   | Phân công có tên             | Nguyễn Bá Quảng: product, bằng chứng và spec · Vũ Thanh Toàn: tích hợp, giao diện, QA và demo · Sỹ Tùng: data, benchmark, đánh giá và chi phí · Phạm Văn Nam: đội trưởng, điều phối, checkpoint, AI engineering, model, truy xuất và an toàn. |
| — | *(CP2)* Đã đổi gì so với CP1 | Đã chốt quy tắc theo size và mốc 09:00–21:00; có công cụ tra lịch, 20 câu thử và 4 metric. Model thật và kết nối Sheet tự động chưa triển khai; benchmark cần đối chiếu nguồn. |


# Track F · Trợ lý kiểm tra lịch thuê áo dài

**Lĩnh vực:** Vận hành cửa hàng cho thuê áo dài tại Hòa Lạc.

**Pain:** Chủ cửa hàng phải dò danh mục và lịch thuê khi tư vấn khách; có thể mất thời gian và bỏ sót lịch trùng.

**Insight từ người dùng thật:** Qua phỏng vấn trực tiếp một chủ cửa hàng áo dài ở Hòa Lạc, nhóm ghi nhận chủ quán phải dò Sheet để kiểm tra mẫu áo còn hay đã có khách thuê; việc này khá lâu và dễ nhầm khi lịch cùng ngày. Theo lời chủ quán do Phạm Văn Nam thuật lại, trong tuần phỏng vấn có 3 đơn bị nhầm, quán phải xin lỗi và chọn bộ khác cho khách. Chủ quán cần biết nhanh tình trạng từng size để tư vấn. Đây là diễn giải, chưa đối chiếu dữ liệu và không phải trích dẫn nguyên văn; chi tiết tại `evidence/interviews/P1.md`.

**Người dùng:** Chủ cửa hàng / người trực tiếp tiếp khách. Phạm Văn Nam trực tiếp phỏng vấn và ghi chép 1 chủ cửa hàng lúc 10:00 ngày 27/11/2026; nhóm cần thêm nguồn bằng chứng đạt ngưỡng BTC.

**Kênh cửa hàng:** [TikTok MIÊN](https://www.tiktok.com/@mien.chothuedo) — link do nhóm cung cấp, không thay cho bằng chứng phỏng vấn.

**Data:**Danh mục và lịch quản lý trên Sheets giúp hiểu cấu trúc và, nếu được phép, đào số tổng hợp không định danh. Bản chạy thử và benchmark dùng dữ liệu giả lập theo luật BTC; không commit tên, số điện thoại, giao dịch thật hay nguyên Sheet.

**Lát cắt:**Chủ cửa hàng hỏi mã áo và khoảng ngày thuê; trợ lý diễn giải yêu cầu, dùng kết quả kiểm tra lịch để báo từng size còn, trùng hoặc cần xác minh, giúp chủ cửa hàng tư vấn khách.

**Công cụ của agent:** `get_mock_data()` đọc nguồn cục bộ đã chọn; `check_availability(...)` tính trạng thái từng size hoặc báo cần xác minh. Công cụ chỉ đọc; code tính xung đột.

**Bộ câu thử:** 20 câu và 4 metric có trong `eval/`; cần đối chiếu đáp án với nguồn được chọn. Chưa có kết quả chấm chính thức.

**Persona chi phí:**Chủ cửa hàng hỏi ít / vừa / nhiều; số lần theo bằng chứng hoặc ghi rõ tự ước tính, hiện chưa có số.

**Bẫy:**Nhầm số lượng với size; bỏ sót lịch sau và thời gian giặt; nhầm lịch thiếu size thành còn áo.

**An toàn:** Không tự chốt đơn, thu tiền, nhắn khách hay sửa Sheet; không cung cấp thông tin nhận diện khách; thiếu dữ liệu thì báo chủ cửa hàng xác minh.
