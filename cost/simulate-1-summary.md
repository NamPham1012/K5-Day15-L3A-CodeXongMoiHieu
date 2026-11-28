# Tóm tắt mô phỏng simulate-1@20261128-103625

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| cua_hang_nho_ngay_thuong | 20 | 2 | 3997 | 551 | 4.0 | 3.1 |
| cua_hang_vua_mua_chup_anh | 19 | 3 | 6087 | 873 | 6.0 | 5.1 |
| cua_hang_cao_diem_cuoi_tuan | 11 | 4 | 7776 | 1149 | 8.0 | 6.1 |

Tỉ lệ đạt dùng để tính: 12/20 (60%) — lượt run-3@20261128-095513

- Tỉ lệ đạt lấy từ lượt nhóm chọn: eval/run-3.csv (--rate-from).

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (5 người) | Chi phí / tháng — cơ sở (20 người) | Chi phí / tháng — cao (50 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt-4o-mini (vào 0.15 · ra 0.6 $/1M) | $0.0013 (≈ 34 ₫) | $0.0022 (≈ 56 ₫) | $0.00078 (≈ 20 ₫) | $0.3953 (≈ 10.080 ₫) | $1.58 (≈ 40.318 ₫) | $3.95 (≈ 100.795 ₫) | $0.0791 (≈ 2.016 ₫) |
| gpt-4o (vào 2.5 · ra 10.0 $/1M) | $0.0221 (≈ 564 ₫) | $0.0368 (≈ 940 ₫) | $0.0131 (≈ 333 ₫) | $6.59 (≈ 167.992 ₫) | $26.35 (≈ 671.968 ₫) | $65.88 (≈ 1.679.921 ₫) | $1.32 (≈ 33.598 ₫) |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (2.8) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: gpt-4o-mini. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 0/50.
- Tỷ giá: 1 USD = 25.500 ₫ (Tỷ giá tham khảo (tự ước tính), tháng 11/2026).
