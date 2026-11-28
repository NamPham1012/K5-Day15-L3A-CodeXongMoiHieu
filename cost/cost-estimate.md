# Chi phí khi dùng thật

> Điền ở guide bước 4.2, nộp ở CP4 14:30 Thứ Bảy 28/11. Ôn lại: ngày 13, ngày 1, ngày 14 · lab ngày 13, lab ngày 14. Chấm ở rubric R6.
> Số lấy trực tiếp từ `python run.py simulate --rate-from eval/run-3.csv` (`cost/simulate-1-summary.md`), tính theo giá gói trả phí.

## 1. Đầu vào

- **Persona** (`cost/personas.yaml`): 3 kiểu cửa hàng theo mùa/lưu lượng hỏi (tổng tỉ lệ = 1.0):
  - `cua_hang_nho_ngay_thuong` (40%): 30 phiên/tháng × 2 lượt/phiên = 60 lượt/tháng *(tự ước tính)*
  - `cua_hang_vua_mua_chup_anh` (40%): 60 phiên/tháng × 3 lượt/phiên = 180 lượt/tháng *(đối chiếu data 261 đơn/2 tháng ≈ 130 đơn/tháng và `spec.md` §2; số lượt hỏi là tự ước tính)*
  - `cua_hang_cao_diem_cuoi_tuan` (20%): 90 phiên/tháng × 4 lượt/phiên = 360 lượt/tháng *(tự ước tính)*
- **Số người dùng thật** 3 kịch bản: thấp **5** cửa hàng · cơ sở **20** cửa hàng · cao **50** cửa hàng. Nguồn: hiện tại 1 chủ cửa hàng trực tiếp (`P1.md`); quy mô mở rộng 5 / 20 / 50 là *(tự ước tính)* cho các tiệm cho thuê trang phục quản lý bằng Google Sheets tại Hòa Lạc & Hà Nội.
- **Giá** 2 mức model (USD / 1 triệu token, nguồn `https://openai.com/api/pricing/`, xem ngày 27/11/2026):
  - `gpt-4o-mini`: vào `$0.15` · ra `$0.60`
  - `gpt-4o`: vào `$2.50` · ra `$10.00`
- **Tỉ lệ đạt** dùng để tính: **12/20 (60%)** — lượt `run-3@20261128-095513` (`eval/run-3.csv`)
- **Đo token trên model `gpt-4o-mini`, tính giá cho cả `gpt-4o-mini` và `gpt-4o`** *(cùng họ tokenizer OpenAI)*. Tỷ giá tham khảo: `1 USD = 25.500 ₫` *(tự ước tính)*.

## 2. Kết quả mô phỏng

Lượt mô phỏng: [`cost/simulate-1.csv`](simulate-1.csv) · Run ID: `simulate-1@20261128-103625` · **50 phiên** (0 phiên lỗi) · `seed = 42` · trace: [`traces/simulate-1.jsonl`](../traces/simulate-1.jsonl)

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| `cua_hang_nho_ngay_thuong` | 20 | 2 | 3.997 | 551 | 4.0 | 3.1 |
| `cua_hang_vua_mua_chup_anh` | 19 | 3 | 6.087 | 873 | 6.0 | 5.1 |
| `cua_hang_cao_diem_cuoi_tuan` | 11 | 4 | 7.776 | 1.149 | 8.0 | 6.1 |

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | / tháng — thấp (5 tiệm) | / tháng — cơ sở (20 tiệm) | / tháng — cao (50 tiệm) | / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| `gpt-4o-mini` ($0.15 / $0.60) | $0.0013 (≈ 34 ₫) | **$0.0022 (≈ 56 ₫)** | $0.00078 (≈ 20 ₫) | $0.3953 (≈ 10.080 ₫) | **$1.58 (≈ 40.318 ₫)** | $3.95 (≈ 100.795 ₫) | **$0.0791 (≈ 2.016 ₫)** |
| `gpt-4o` ($2.50 / $10.00) | $0.0221 (≈ 564 ₫) | **$0.0368 (≈ 940 ₫)** | $0.0131 (≈ 333 ₫) | $6.59 (≈ 167.992 ₫) | **$26.35 (≈ 671.968 ₫)** | $65.88 (≈ 1.679.921 ₫) | **$1.32 (≈ 33.598 ₫)** |

*Chi phí / task thành công = chi phí trung bình mỗi phiên ÷ tỉ lệ đạt (60%) — không coi như đạt 100%.*

## 3. So với impact

- **Impact / người / tháng (`spec.md` §2):** tiết kiệm **~450 phút (~7,5 giờ/tháng)** *(tự ước tính)* dò Sheet thủ công + giảm rủi ro nhận nhầm lịch (P1: 3 đơn nhầm/tuần, data: 5 nhóm vượt tồn kho tháng 11).
- **Chi phí / người / tháng (cơ sở, model `gpt-4o-mini`):** **$0.0791 (≈ 2.016 ₫ / cửa hàng / tháng)** — kể cả ở kịch bản cao 50 cửa hàng cũng chỉ tốn **~$3.95/tháng (≈ 100.795 ₫)**.
- **Kết luận một dòng — đáng làm không:** **Rất đáng làm về mặt chi phí** — chỉ tốn ~2.000 ₫/cửa hàng/tháng (~56 ₫/task thành công) để đổi lấy ~7,5 giờ tiết kiệm và tránh mất uy tín do trùng lịch; cần tiếp tục nâng độ chính xác từ 60% lên ≥ 90% (Iterate) để tối ưu hơn nữa.

## 4. Tối ưu & chi phí ngoài model

- **Cần gạt giảm chi phí token:** Nếu áp dụng template Python cố định ở bước trình bày (thay vì để LLM viết dài ~272 token ra/câu), có thể giảm ~35–40% token đầu ra; nếu nâng tỉ lệ đạt từ 60% lên 90%, chi phí / task thành công giảm thêm ~33% (xuống còn ~$0.0014 ≈ 37 ₫).
- **Chi phí ngoài model:** Bản chạy thử web (`webapp/server.py`) chạy cục bộ bằng thư viện chuẩn Python (0 ₫ hosting); nếu đưa lên cloud cho 20–50 tiệm, một VPS nhỏ ~$5–10/tháng (~130.000–255.000 ₫/tháng) lớn hơn nhiều lần tiền API model.
