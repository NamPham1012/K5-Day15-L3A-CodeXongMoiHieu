# Báo cáo đánh giá — lượt 1 → một cải tiến → lượt 2

> Điền ở guide bước 4.1. Lượt 1 trước **CP3 10:00 Thứ Bảy 28/11**, lượt 2 trước **CP4 14:30 Thứ Bảy 28/11**, cùng bộ câu thử, cùng cách chấm. Chấm ở rubric R5.
> Số lấy từ `python run.py score eval/run-1.csv` (và `run-2.csv`) sau khi điền cột `pass`. **Kết quả thấp ghi thật vẫn đủ điểm.**
> Không được: sửa chuẩn "đạt", bỏ câu thử trượt, sửa `expected` cho khớp output, sửa kết quả lượt đã chạy.

## 1. Kết quả

| Lượt | Run ID | Đạt / tổng | % | thuong | kho | tu_choi | So với chuẩn "đạt" |
|---|---|---|---|---|---|---|---|
| 1 | run-1@20261127-203557 | 15/20 | 75% | 5/5 | 7/12 | 3/3 | **chưa đạt** (cần ≥18/20) |
| 2 | | __/__ | | __/__ | __/__ | __/__ | đạt / chưa |

Kết quả từng câu: `eval/run-1.csv`, `eval/run-2.csv`. Trace: `traces/run-1.jsonl`, `traces/run-2.jsonl`.

## 2. Lỗi lượt 1 — gom thành nhóm có tên

| Nhóm lỗi | Số câu | Câu |
|---|---|---|
| Giới hạn dữ liệu trước 01/11 — không phân tích lịch | 4 | B08, B09, B10, B11 |
| Không validate đầu vào ngày bắt đầu > ngày kết thúc | 1 | B05 |

**≥3 lỗi cụ thể:**

| Câu | Input | Output | Vì sao sai |
|---|---|---|---|
| B05 | AD02 25/11/2026 20/11/2026 | Báo còn hàng (S, L, XL) và sẵn sàng lại 09:00 ngày 26/11 | Không phát hiện ngày bắt đầu 25/11 > ngày kết thúc 20/11 → phải báo "khoảng ngày không hợp lệ" |
| B08 | Khách hỏi thuê mẫu AD26 ngày 28/10/2026 từ 15:00 đến 19:00 | Báo "cần xác minh" do dữ liệu chỉ từ 01/11/2026 | Expected yêu cầu phân tích cụ thể: M trùng lịch 13:00 28/10, XL trùng lịch trả 21:00 28/10; output bỏ qua hoàn toàn vì giới hạn date |
| B09 | AD09 từ 24/10 đến 25/10/2026 khách muốn thuê 1 áo size S | Báo "cần xác minh" do date < 01/11 | Expected yêu cầu báo size S trùng lịch cụ thể (đơn từ 15:00 24/10 đến 17:00 25/10); output không phân tích lịch vì chặn date |
| B10 | Kiểm tra lịch mẫu AD02 từ ngày 19/10 đến 20/10/2026 | Báo không thể kết luận do date < 01/11 | Sai lý do: expected yêu cầu gắn cờ cần xác minh vì đơn thiếu thông tin size, không phải vì ngày trước 01/11 |
| B11 | Mẫu AD50 ngày 16/10/2026 lúc 14:00 khách muốn thuê size M | Báo không thể kết luận do date < 01/11 | Không nhận diện đơn thuê liên quan size M (ghi chú có size M nhưng cột size trống); expected yêu cầu báo trùng hoặc cần xác minh |

## 3. Một lần cải tiến

- Nhắm vào nhóm lỗi: __ — vì sao là nhóm **đau nhất với người dùng**: __
- Đã sửa gì (có thể vài thay đổi cùng nhắm nhóm lỗi đó): __
- Kết quả: nhóm lỗi đó __/__ → __/__ · tổng __% → __%
- Câu nào **tệ đi** sau khi sửa: __

## 4. Còn lại

- Lỗi chưa sửa + nguy hiểm thế nào: __
- Nếu có thêm 1 tuần: __
