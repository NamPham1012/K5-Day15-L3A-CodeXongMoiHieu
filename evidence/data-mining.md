# Đào data — cách đếm và kết quả

> Điền ở guide bước 1.2. Ôn lại: ngày 2, ngày 6 · lab ngày 2, lab ngày 6.
> Script đếm để trong repo (`evidence/count.py`); chạy `python evidence/count.py` trên bản trích cục bộ `data/rental.private.json` sẽ ra đúng cùng con số.
> Repo chỉ chứa số đã tổng hợp và các ví dụ đã ẩn danh (không chứa tên, SĐT hay bản gốc Sheet).

## 1. Cách đếm — viết TRƯỚC khi chạy

- **Data dùng:** `data/rental.private.json` — bản trích cục bộ từ 2 Google Sheet danh mục & lịch thuê của cửa hàng áo dài MIÊN (cập nhật ngày 27/11/2026), đã loại bỏ toàn bộ tên khách, SĐT, tiền cọc và phụ kiện (`PK*`). Phạm vi lịch trải từ tháng 10/2026 đến cuối tháng 11/2026 (chủ quán xác nhận dữ liệu đầy đủ từ 01/11/2026).
- **Đếm gì:**
  1. Tỷ lệ dòng lịch hiệu lực (không tính đơn `HỦY` / `Đã hủy`) có bất thường dữ liệu gây rủi ro nhầm khi dò tay: thiếu/không rõ size (`trống`/`KHONG_RO`), size lệch danh mục, thiếu ngày giờ, ngày trả ≤ ngày nhận, trả sau 21:00, hoặc thiếu/lạ trạng thái.
  2. Áp lực dò lịch thủ công: tỷ lệ mã áo có nhiều size (`≥ 2` size), mã áo có nhiều đơn (`≥ 5` dòng lịch), số cặp đơn sát ngày (`≤ 24h` sau mốc giặt 09:00 hôm sau) và số nhóm `(mã áo, size)` có lịch vượt tồn kho khi áp đúng quy tắc giặt đến 09:00 ngày hôm sau.
- **Mẫu số là gì:**
  - Với chỉ số bất thường lịch thuê: **N_active = 261** dòng lịch áo dài hiệu lực (tổng 263 dòng lịch áo dài sau khi loại dòng 206 `AD09` "Chỉ quần" không giữ áo dài theo xác nhận chủ quán, trừ đi 2 đơn `HỦY`/`Đã hủy`).
  - Với chỉ số danh mục mẫu áo: **N_inv = 85** mã áo dài trong danh mục.
- **Script / công thức:** [`evidence/count.py`](count.py) — chạy lệnh `python evidence/count.py`.

## 2. Đọc trước, đếm sau

Đã kiểm tra schema (`inventory`: 85 mã, `rentals`: 263 dòng, `unassigned_rentals`: 0 dòng sau khi phân loại) và rà các dòng mẫu đầu tiên. Các kiểu hành vi / lỗi ghi chép thấy được trên sổ Sheet:
- Nhiều dòng bị bỏ trống size hoặc ghi ghi chú lẫn vào ô size (được chuẩn hóa thành `KHONG_RO` khi trích xuất).
- Một số dòng ghi size không khớp với size khai báo trong bảng danh mục (vd `AD15` ghi `L` trong lịch).
- Một số dòng thiếu ngày/giờ hoặc bị gõ nhầm tháng (như `AD09` dòng 89 trên Sheet: nhận `01/11/2026`, trả `02/10/2026` → công thức Sheet tự tính giờ sẵn sàng thành `03/10/2026 09:00`).
- Các mẫu bán chạy (`AD50`, `AD26`, `AD09`, `AD51H`, `AD02`) có 10–13 dòng lịch rải rác theo nhiều size và nhiều ngày, dễ bỏ sót khoảng giặt qua đêm (đến 09:00 sáng hôm sau) khi dò bằng mắt.

## 3. Kết quả

| Đếm gì | x / N | % | Ghi chú |
|---|---|---|---|
| Dòng lịch hiệu lực có **≥ 1 bất thường dữ liệu** | 99 / 261 | 37.9% | Hợp của các lỗi dưới đây (sau khi sửa dòng 89 `AD09` và loại dòng 206 "Chỉ quần") |
| Thiếu ngày/giờ nhận hoặc trả | 43 / 261 | 16.5% | Không thể tự kết luận lịch trống nếu không xác minh |
| Thiếu hoặc không rõ size (`trống` / `KHONG_RO`) | 33 / 261 | 12.6% | Rủi ro lớn nhất khi dò tay: dễ tưởng size khác còn áo |
| Size trong lịch không khớp danh mục | 22 / 261 | 8.4% | Cần đối chiếu lại danh mục thực tế của cửa hàng |
| Thiếu hoặc trạng thái ngoài 5 chuẩn | 14 / 261 | 5.4% | Không rõ đơn còn giữ áo hay đã hủy |
| Giờ trả sau 21:00 | 4 / 261 | 1.5% | Vi phạm mốc giờ cửa hàng chốt (không muộn hơn 21:00) |
| Ngày/giờ trả ≤ ngày/giờ nhận | 2 / 261 | 0.8% | Lỗi nhập trùng/nhầm mốc ngày giờ trên Sheet (`R#171`, `R#253`) |
| Mã áo dài có ≥ 2 size trong danh mục | 31 / 85 | 36.5% | Phải dò lịch theo từng size riêng thay vì chỉ theo mã |
| Mã áo dài có ≥ 5 dòng lịch | 21 / 85 | 24.7% | Top 5: AD50 (13), AD26 (12), AD51H (11), AD02 (10), AD09 (10) |
| Nhóm `(mã áo, size)` vượt tồn kho (tính cả giặt đến 09:00 hôm sau) | 6 nhóm | — | 5/6 nhóm rơi vào tháng 11/2026 (`AD06 XL`, `AD26 M`, `AD45H M`, `AD51H L`, `AD51X XL`) |
| Cặp đơn liên tiếp cùng `(mã, size)` cách nhau ≤ 24h sau mốc giặt 09:00 | 18 cặp | — | Bao gồm cả các cặp trùng và sát nút ranh giới giặt |

## 4. ≥5 ví dụ cụ thể (đã ẩn danh theo mã bản ghi `R#`, không tên khách)

1. **`R#253` — Ngày trả bằng ngày nhận (`00:00` → `00:00`):** `AD42`, size `M`, `26/11/2026 00:00` → `26/11/2026 00:00`, trạng thái `Đang giặt` (trước đó bản trích gốc còn có dòng 89 `AD09` gõ nhầm trả `02/10` trước nhận `01/11`, đã được chủ quán xác nhận sửa thành `02/11`).
2. **`R#171` — Ngày trả bằng ngày nhận & thiếu size:** `AD59H`, size `KHONG_RO`, `15/11/2026 00:00` → `15/11/2026 00:00`, trạng thái `Đã hoàn tất`.
3. **`R#042` — Thiếu cả ngày nhận và ngày trả:** `AD51H`, size `S`, ngày nhận/trả trống, trạng thái `Đã hoàn tất`.
4. **`R#064` — Thiếu/không rõ size ở mẫu nhiều đơn nhất (`AD50`):** `AD50`, size `KHONG_RO`, `24/10/2026 22:00` → `25/10/2026 21:00`, trạng thái `Đã hoàn tất`.
5. **`R#030` — Giờ trả sau 21:00:** `AD23`, size `M`, `24/10/2026 20:00` → `25/10/2026 22:00`, trạng thái `Đã hoàn tất` (trả lúc 22:00, vượt mốc 21:00).
6. **`R#001` — Size trong lịch lệch danh mục:** `AD15`, size `L`, `19/10/2026 19:00` → `21/10/2026 20:00`, trạng thái `Đã hoàn tất`.
7. **Trùng lịch vượt tồn kho thực tế cuối tháng 11:** `AD26` size `M` (tồn kho 1 áo) có đỉnh giữ **3 đơn cùng thời điểm lúc 25/11/2026 00:00**; `AD06` size `XL` (tồn kho 1 áo) có đỉnh giữ **2 đơn lúc 26/11/2026 00:00** — trùng khớp thời điểm tuần phỏng vấn (27/11/2026) mà chủ quán kể có 3 đơn bị nhầm lịch.

## 5. Giới hạn của data

- Data lịch cho biết **tình trạng sổ sách bẩn và có vượt tồn kho trên lịch**, nhưng **không cho biết trực tiếp nguyên nhân vận hành** (vd: liệu các đơn vượt tồn kho có phải do khách đổi áo phút chót nhưng chủ quán quên cập nhật trạng thái `HỦY`, hay do nhận trùng thật; và không đo được số phút mỗi lần dò Sheet).
- Dữ liệu tháng 10/2026 có thể chưa đầy đủ theo xác nhận của chủ quán (mốc đáng tin từ 01/11/2026); tuy nhiên riêng các ca vượt tồn kho có tới 5/6 nhóm rơi vào tháng 11/2026.
- → Kiểm lại bằng phỏng vấn chủ cửa hàng ([`interviews/P1.md`](interviews/P1.md)): lời kể chủ quán về việc dò Sheet lâu và bị nhầm 3 đơn trong tuần phỏng vấn khớp trực tiếp với các ca vượt tồn kho cuối tháng 11/2026 trong data.
