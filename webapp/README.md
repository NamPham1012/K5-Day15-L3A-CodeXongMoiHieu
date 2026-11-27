# Trợ lý kiểm tra lịch thuê áo dài (bản web cục bộ)

Trang web cho chủ cửa hàng: gõ mã áo và ngày, xem ngay size nào còn, size nào hết và bao giờ áo sẵn sàng lại. Trang **chỉ đọc**: không chốt đơn, không nhắn khách, không ghi file.

## Chạy

```
python webapp/server.py
```

Mở http://127.0.0.1:8770. Chỉ nghe `127.0.0.1`, chỉ dùng thư viện chuẩn của Python. Dừng bằng Ctrl+C.

## Hai cách hỏi

1. **Form nhanh**: gọi thẳng `check_availability`. Kết quả tất định, không tốn token, chạy được cả khi chưa có API key. Giờ để trống thì dùng 09:00 (nhận) và 21:00 (trả) và được ghi rõ là "giả định".
2. **Hỏi bằng câu**: gọi `agent.answer`. Cần `.env` có `MODEL_PROVIDER`, `MODEL_NAME`, `API_KEY` (xem `.env.example`). Mỗi câu hỏi tốn token thật; dòng nhỏ dưới câu trả lời hiện số lần gọi model, công cụ, token và thời gian lấy từ trace.

## Trạng thái AI (chấm trên thanh trên)

| Chấm | Ý nghĩa |
|---|---|
| Xanh, "AI thật · <model>" | Có provider thật, key và model |
| Vàng, "Chưa có API key" | `MODEL_PROVIDER=fake` hoặc thiếu key/model. Chỉ hiểu cú pháp `MÃ DD/MM/YYYY DD/MM/YYYY` |
| Đỏ, "AI hết token" | API trả 402 hoặc 429 có `insufficient_quota`. Giữ tới khi tải lại trang |
| Đỏ, "API key lỗi" | API trả 401/403 |

Trang không gọi API để thử trạng thái (tránh tốn token), nên "hết token" và "key lỗi" chỉ biết sau lần hỏi đầu tiên bị lỗi.

## API

- `GET /api/info`, `GET /api/catalog`
- `POST /api/check`: `{ma_ao, ngay_nhan, gio_nhan, ngay_tra, gio_tra}`
- `POST /api/ask`: `{text}` (tối đa 500 ký tự)

Body POST tối đa 16KB. Chỉ phục vụ file trong `webapp/static/`. Lỗi AI được phân loại (`chua_co_key`, `het_token`, `gioi_han_toc_do`, `key_loi`, `mang`, `khac`) và trả câu tiếng Việt, không kèm nội dung thô của API và không lộ key.

## Giới hạn

- Một `threading.Lock` bao quanh mọi lần gọi công cụ và agent (vì `tracing` dùng biến toàn cục), nên trong lúc một câu hỏi AI đang chờ, các yêu cầu khác phải đợi.
- Chưa có chế độ tối (để dành).
- Không sửa lỗi của agent hay công cụ: các lỗi đã biết (xem `SPEC.md` §1) vẫn hiện đúng như code trả về.
- Dòng thời gian chỉ là phần hỗ trợ nhìn; danh sách chữ bên dưới luôn có. Trên màn hẹp, dòng thời gian cuộn ngang trong khung của nó.
- Lịch sử "Tra gần đây" lưu trong `localStorage` của trình duyệt (mã và ngày giờ, tối đa 8 lần).
