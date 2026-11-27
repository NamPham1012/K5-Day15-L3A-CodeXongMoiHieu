# Tổng hợp bằng chứng pain

> Điền ở guide bước 1.2, xong trước **CP3 10:00 Thứ Bảy 28/11**. Chấm ở rubric R1.
> Ba nguồn ngang nhau — tối thiểu **≥1 nguồn đạt ngưỡng**. Mạnh nhất: đào data ra insight → hỏi người dùng để kiểm lại (hoặc ngược lại).

## 1. Nguồn đã dùng

| Nguồn | Đạt ngưỡng? | File |
|---|---|---|
| Đào data (x/N, %, cách đếm chạy lại được, ≥5 ví dụ) | ☑ | `evidence/data-mining.md` · `evidence/count.py` |
| Phỏng vấn (≥3 người ngoài nhóm, đúng người dùng) | ☐ *(1/3 — dùng kiểm chéo)* | `evidence/interviews/P1.md` |
| Khảo sát (≥20 người ngoài nhóm, đúng người dùng) | ☐ *(không dùng)* | `evidence/survey/TEMPLATE.md` |

## 2. Số chính

- **Đào data (`evidence/count.py` trên 85 mã danh mục, N = 261 dòng lịch hiệu lực sau khi loại dòng 206 "Chỉ quần" và 2 đơn hủy):**
  - **99/261 (37.9%)** dòng lịch hiệu lực có ≥ 1 bất thường dữ liệu (43/261 = 16.5% thiếu ngày/giờ; 33/261 = 12.6% thiếu/không rõ size; 22/261 = 8.4% size lệch danh mục; 14/261 = 5.4% thiếu/lạ trạng thái; 4/261 = 1.5% trả sau 21:00; 2/261 = 0.8% ngày trả ≤ ngày nhận; chưa kể dòng 89 `AD09` trước đó bị gõ nhầm trả `02/10` và vừa được xác nhận sửa thành `02/11`).
  - **31/85 (36.5%)** mã áo có ≥ 2 size và **21/85 (24.7%)** mã có ≥ 5 dòng lịch (cao nhất: `AD50` 13 đơn, `AD26` 12 đơn, `AD51H` 11 đơn, `AD02` 10 đơn, `AD09` 10 đơn).
  - **6 nhóm `(mã áo, size)`** có lịch vượt tồn kho khi áp quy tắc giặt đến 09:00 hôm sau (**5/6 nhóm rơi vào tháng 11/2026**) và **18 cặp đơn liên tiếp** cách nhau ≤ 24h sau mốc giặt 09:00.
- **Phỏng vấn kiểm chéo (`P1.md`):** 1/1 chủ cửa hàng gặp pain (chưa đạt ngưỡng ≥ 3 người của riêng kênh phỏng vấn, dùng để kiểm chéo nguyên nhân). Chủ quán cho biết có **3 đơn bị nhầm lịch trong tuần phỏng vấn (tuần 27/11/2026)**, phải xin lỗi và chọn bộ khác cho khách; chưa đo được số phút/lần hay số lần hỏi/tháng.

| | Vai | Gặp pain? | Số lần / 1 tháng qua | Lần gần nhất mất | Đang xoay xở bằng |
|---|---|---|---|---|---|
| P1 | Chủ cửa hàng cho thuê áo dài (Hòa Lạc) | Có | 3 đơn nhầm trong tuần 27/11 (chưa có tổng tháng) | Chưa đo phút; phải xin lỗi và đổi bộ khác cho khách | Dò thủ công trên Google Sheets |

## 3. ≥5 trích dẫn hoặc ví dụ nguyên văn (có nguồn, bỏ tên)

1. **`R#086` (dòng 89 Sheet — `data-mining.md`):** `AD09` size `L` ghi nhận `01/11/2026` nhưng trả `02/10/2026` (gõ nhầm tháng 10 thay vì tháng 11), khiến công thức Sheet tự tính giờ sẵn sàng thành `03/10/2026 09:00`.
2. **`R#064` (`data-mining.md`):** `AD50` (mẫu nhiều đơn nhất với 13 dòng lịch) có đơn ngày `24–25/10/2026` để trống/không rõ size (`KHONG_RO`), trạng thái `Đã hoàn tất`.
3. **`R#042` (`data-mining.md`):** `AD51H` size `S`, trạng thái `Đã hoàn tất` nhưng trống hoàn toàn ngày nhận và ngày trả.
4. **`R#030` (`data-mining.md`):** `AD23` size `M`, ghi giờ trả `22:00` ngày `25/10/2026` (vượt quy định trả không muộn hơn 21:00).
5. **Vượt tồn kho thực tế cuối tháng 11 (`data-mining.md`):** `AD26` size `M` (tồn kho 1 áo) có đỉnh giữ 3 đơn lúc `25/11/2026 00:00`; `AD06` size `XL` (tồn kho 1 áo) có đỉnh giữ 2 đơn lúc `26/11/2026 00:00`.
6. **Ghi chép phỏng vấn `P1` (diễn giải bởi Phạm Văn Nam, không phải trích nguyên văn):** trong tuần 27/11/2026, cửa hàng bị nhầm 3 đơn do dò lịch trên Sheet lâu và trùng lịch cùng ngày, phải xin lỗi và đổi bộ khác cho khách.

## 4. Các nguồn có khớp nhau không

- **Data nói:** 37.9% dòng lịch hiệu lực có bất thường dữ liệu (thiếu size, thiếu/sai ngày, lệch danh mục), nhiều mẫu có 10–13 dòng lịch rải rác và xuất hiện tới 5 nhóm `(mã áo, size)` vượt tồn kho ngay trong tháng 11/2026 (trong đó có `AD26 M` ngày 25/11 và `AD06 XL` ngày 26/11).
- **Người dùng (`P1`) nói:** dò lịch trên Google Sheets mất thời gian, dễ trùng lịch cùng ngày và thực tế vừa bị nhầm 3 đơn ngay trong tuần 27/11/2026.
- **Khớp / lệch:** Hai nguồn **khớp trực tiếp về thời điểm và bản chất pain** (đều chỉ ra nguy cơ trùng lịch cao khi dò thủ công trên Sheet có dữ liệu thiếu/sai). Điểm còn thiếu là chưa đo trực tiếp số phút trung bình mỗi lần dò lịch và số lượt hỏi/ngày (khi tính Impact ở `spec.md` §2 cần hỏi lại chủ quán hoặc ghi rõ *(tự ước tính)*).

## 5. Kết luận

- **Bằng chứng pain đã đạt ngưỡng R1** qua nguồn **Đào data** (`evidence/data-mining.md` + `evidence/count.py` chạy lại được, kèm ≥ 5 ví dụ ẩn danh) và được kiểm chéo thực tế bởi phỏng vấn `P1`.
- **Hệ quả cho thiết kế giải pháp:** AI không chỉ cần tính lịch trùng chính xác theo từng size và mốc giặt 09:00, mà **bắt buộc phải gắn cờ "cần chủ cửa hàng xác minh"** khi gặp 37.9% dòng lịch có dữ liệu thiếu/lỗi — tuyệt đối không tự suy đoán là còn áo.
- **Điều vẫn chưa biết:** tần suất câu hỏi khách/ngày và thời gian trung bình mỗi lần dò lịch của chủ quán.

## Lịch hẹn (dùng cho CP2 — chỉ ghi vai và giờ, không tên)

Đã thực hiện 1 buổi phỏng vấn trực tiếp chủ cửa hàng lúc 10:00 ngày 27/11/2026 (`interviews/P1.md`) và hoàn tất đào data trên bản trích 264 dòng lịch thật của cửa hàng (`data-mining.md`).

| Vai | Giờ hẹn | Đã xong? |
|---|---|---|
| Chủ cửa hàng cho thuê áo dài (Hòa Lạc) | 10:00 ngày 27/11/2026 | Đã xong (`P1.md`) |
