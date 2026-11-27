# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Khởi tạo repo và bản nháp CP1–CP2 | Codex | Chép starter, đối chiếu cấu trúc BTC, tạo bản nháp Canvas/spec cho Track F | Kiểm lại giả thuyết, lát cắt, chuẩn đánh giá và mọi nội dung trước khi nộp | Đội trưởng |
| Code bản chạy thử | Codex / Coding agent | Hỗ trợ viết khung bản mock `codebase/agent.py`, `codebase/tools.py`, unit test và script đối chiếu dữ liệu | Đội trưởng và người sở hữu chạy `run.py check`, unit test và kiểm tra quy tắc nghiệp vụ | Phạm Văn Nam, Vũ Thanh Toàn |
| Prompt / thiết kế lời gọi mô hình | Coding agent | Hỗ trợ viết nhánh gọi OpenAI trong `codebase/ai.py` và workflow 3 bước (parse JSON → tool → trình bày) trong `codebase/agent.py` | Đội trưởng nối API key thật, chạy `eval --try` kiểm tra token và chất lượng câu trả lời | Phạm Văn Nam |
| Đào data (viết script đếm, gợi ý nhãn) | Coding agent | Viết script `evidence/count.py` đếm tỷ lệ bất thường & vượt tồn kho trên `data/rental.private.json` và tổng hợp `evidence/data-mining.md` | Nhóm chạy lại `python evidence/count.py`, đối chiếu ví dụ dòng 89 trên ảnh Sheet thật | Phạm Văn Nam, Nguyễn Bá Quảng |
| Rà câu hỏi phỏng vấn / khảo sát | | Chỉ rà câu dẫn dắt | | |
| Viết câu thử (benchmark) | Codex / Coding agent | Hỗ trợ rà cấu trúc, chuẩn hóa định dạng và đối chiếu nguồn trong `eval/doi-chieu-cp2.md` | Mỗi câu thử có `source`; nhóm rà lại với dữ liệu cửa hàng trước khi chốt | Sỹ Tùng |
| Sinh data `synthetic` (nếu có) | | | Dữ liệu `data/mock_rental.json` dựng tay (không sinh ngẫu nhiên) | Sỹ Tùng |
| Chấm cột `pass` bằng LLM (nếu có) | | Không dùng LLM chấm | Toàn bộ chấm bằng người (2 người chấm độc lập) | Sỹ Tùng, Vũ Thanh Toàn |
| Slide, văn bản | Coding agent | Hỗ trợ audit, review CP2 và đồng bộ tài liệu repo | Đội trưởng duyệt trước khi commit | Phạm Văn Nam |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).
