# SPEC — Trang web "Trợ lý kiểm tra lịch thuê áo dài" (bản giao diện cho chủ cửa hàng)

> Người viết spec: Opus. Người code: Sonnet. Người review: Opus. Người duyệt spec: Toàn.
> Trạng thái: **ĐÃ DUYỆT** (28/11/2026, xem §12). Giao Sonnet code.
> Mục tiêu đợt này: **giao diện đẹp, dễ dùng**. **Không sửa lỗi** của agent hay công cụ. Lỗi đã biết vẫn hiện đúng như code trả về.

---

## 1. Code hiện có (đọc từ nhánh `toanv2`, trùng với `origin/main` `e9c903f`)

| Thành phần | Đã có gì | Trang web dùng thế nào |
|---|---|---|
| `codebase/tools.py` · `get_mock_data()` | Đọc `data/rental.private.json` (mặc định: 85 mã, 263 dòng lịch, đã ẩn danh, không có tên hay số điện thoại). Đổi sang `data/mock_rental.json` bằng `RENTAL_DATA_SOURCE=mock` | Lấy danh mục mã và size để gợi ý khi gõ mã |
| `codebase/tools.py` · `check_availability(ma_ao, nhan_luc, tra_luc)` | Tính từng size theo tồn kho và các đơn giữ áo, áp quy tắc giặt (sẵn sàng 09:00 hôm sau), bỏ qua HỦY, chặn trả sau 21:00 và dữ liệu trước 01/11. Trả về `trang_thai` là `da_kiem_tra` hoặc `can_xac_minh`, kèm `sizes{tong_so, con_lai, trang_thai}`, `san_sang_lai`, `don_lien_quan[]`, `ly_do`, `luu_y` | **Cách 1 — form nhanh.** Gọi thẳng công cụ: kết quả tất định, không tốn token, chạy được cả khi chưa có API key |
| `codebase/agent.py` · `answer(text)` | Có model thật (`MODEL_PROVIDER=openai`): AI tách câu tiếng Việt thành JSON, code kiểm tra, AI viết câu trả lời. Không có model (`fake`): chỉ nhận cú pháp `MA DD/MM/YYYY DD/MM/YYYY` | **Cách 2 — hỏi bằng câu.** Trả về văn bản AI viết |
| `codebase/ai.py` | Gọi gpt-4o-mini qua `.env` (`API_KEY`, `MODEL_NAME`) | Hiện nhãn model đang dùng; báo rõ khi đang ở chế độ `fake` |
| `codebase/tracing.py` (khung, **không sửa**) | `begin()`/`end()` gom các lần gọi model, công cụ và số token | Sau mỗi câu hỏi AI, hiện số lần gọi model, số lần gọi công cụ, token và thời gian. Lấy từ trace thật, không ước lượng |

**Lỗi đã biết, đợt này KHÔNG sửa** (ghi lại để người xem không bất ngờ, xem phiếu chấm run-1):
- Ngày trả trước ngày nhận bị AI tự đổi ngày (B05).
- Ngày trước 01/11 luôn ra "cần xác minh" (B08–B11).
- Câu tấn công "bỏ qua lịch" không gọi công cụ kiểm tra (B18).
- Giờ khách tự nói bị ghi là "giả định" (B07).

Trang chỉ hiển thị trung thực những gì code trả về. Form ở cách 1 có kiểm tra đầu vào ngay khi nhập (xem §5), nhưng đó là UX của form, không phải sửa agent.

## 2. Người dùng và bối cảnh

- **Ai dùng:** chủ cửa hàng hoặc người trực quầy. Không rành kỹ thuật, đang đứng tư vấn khách, thường **cầm điện thoại**, đôi khi dùng laptop.
- **Câu hỏi họ cần trả lời trong 10 giây:** "Mẫu AD26 ngày 20/11 còn size nào? Nếu hết thì bao giờ có lại?"
- **Họ sợ nhất:** báo "còn" nhầm, khách đến mà không có áo (pain P1: 3 đơn nhầm trong một tuần).
- **Hệ quả cho thiết kế:**
  1. Kết quả từng size phải đọc được ngay: chữ to, có icon và có chữ, không chỉ dựa vào màu.
  2. "Cần xác minh" phải nổi hơn "còn", và kèm lý do.
  3. Luôn hiện giờ nhận và trả đang dùng để tính, và ghi rõ đâu là giờ giả định.
  4. Ít bước: gõ mã, chọn ngày, bấm một nút.

## 3. Phạm vi

**Làm:**
- Thư mục mới `webapp/`. **Không sửa** file nào ngoài `webapp/`: không đụng `codebase/`, `eval/`, `data/`, `run.py` hay khung.
- Server chạy cục bộ bằng thư viện chuẩn Python, địa chỉ `http://127.0.0.1:8770`, mở bằng `python webapp/server.py`.
- Một trang, hai cách hỏi, kết quả có cấu trúc, lịch sử tra gần đây.

**Không làm:**
- Sửa lỗi agent hay công cụ.
- Đăng nhập.
- Chốt đơn, thu tiền, nhắn khách, sửa Sheet: trang **chỉ đọc**.
- Hiện tên hay số điện thoại: dữ liệu vốn không có, và trang không có ô nào để nhập.
- Đưa lên mạng: chỉ nghe `127.0.0.1`.
- Commit `.env`.

## 4. Bố cục trang

**Điện thoại (≤ 768px): một cột**
```
┌───────────────────────────────┐
│ MIÊN · Trợ lý lịch thuê   [●] │  ← thanh trên; chấm trạng thái: "AI thật · gpt-4o-mini" hoặc "Chưa nối AI"
├───────────────────────────────┤
│ [ Form nhanh ] [ Hỏi bằng câu ]│  ← 2 tab (segmented control), mặc định Form nhanh
├───────────────────────────────┤
│ Mã áo  [ AD26          ▾ ]    │  ← gõ "ad26" cũng nhận; gợi ý từ danh mục; hiện size ngay: "M · XL"
│ Nhận   [20/11/2026] [09:00]   │  ← giờ để trống = 09:00, có nhãn "giả định"
│ Trả    [20/11/2026] [21:00]   │  ← giờ để trống = 21:00, có nhãn "giả định"
│ Size khách cần (tuỳ chọn) [M][XL]  Số lượng [1]│
│ [   Kiểm tra lịch   ]         │  ← nút chính, rộng hết cột, cao ≥ 48px
├───────────────────────────────┤
│ KẾT QUẢ (§6)                  │
├───────────────────────────────┤
│ Tra gần đây: AD26 20/11 · AD09 14/11 … │ ← bấm để tra lại
└───────────────────────────────┘
```

**Máy tính (≥ 1024px): hai cột**
- Trái, rộng 400px, dính khi cuộn: form và tra gần đây.
- Phải: kết quả.
- Chiều rộng tối đa 1200px, căn giữa.

## 5. Luồng tương tác

### Cách 1 — Form nhanh (gọi `check_availability`)

1. **Mã áo:**
   - Ô gõ có gợi ý, lọc theo danh mục từ `/api/catalog`, không phân biệt hoa thường.
   - Chọn xong hiện ngay các size và số áo, ví dụ "M ×1 · XL ×1".
   - Mã không có trong danh mục **vẫn cho gửi**, để công cụ tự trả "Không tìm thấy mã…". Trang không tự chặn, để hiện đúng hành vi thật.
2. **Ngày:**
   - Dùng `input type="date"`; hiển thị và giải thích theo dạng DD/MM/YYYY.
   - Ngày trả mặc định bằng ngày nhận.
   - Có nút nhanh "Hôm nay", "Mai", "Cuối tuần này" cho ngày nhận.
3. **Giờ:**
   - Dùng `input type="time"`, để trống được.
   - Trống thì gửi 09:00 cho giờ nhận và 21:00 cho giờ trả, và hiện nhãn "giả định" cạnh giờ trong kết quả.
4. **Kiểm tra ngay khi nhập** (lỗi hiện **ngay dưới ô**, không chặn cứng):
   - Ngày hoặc giờ trả không sau giờ nhận: "Giờ trả phải sau giờ nhận." Nút gửi bị khoá cho tới khi sửa.
   - Giờ trả sau 21:00: cảnh báo màu vàng "Cửa hàng yêu cầu trả trước 21:00 — kết quả sẽ là cần xác minh". **Vẫn cho gửi**, để thấy công cụ báo.
   - Ngày nhận trước 01/11/2026 khi đang dùng dữ liệu riêng: gợi ý "Dữ liệu chỉ tin cậy từ 01/11/2026". Vẫn cho gửi.
5. **Size khách cần và số lượng** (tuỳ chọn): chỉ dùng để **làm nổi** thẻ size đó và so `con_lai` với số lượng: đủ hoặc không đủ. Công cụ không nhận tham số này, trang tự so trên kết quả.
6. **Khi bấm gửi:**
   - Nút chuyển sang trạng thái đang tải (spinner kèm chữ "Đang kiểm tra…") và bị khoá để không bấm hai lần.
   - Kết quả chen vào với chuyển động mờ dần và trượt lên 8px trong 200ms. Tắt chuyển động khi người dùng bật `prefers-reduced-motion`.
   - Vùng kết quả có `aria-live="polite"`.
   - Trên điện thoại, tự cuộn tới kết quả.
7. Lưu lần tra vào **Tra gần đây** (`localStorage`, tối đa 8 lần, chỉ lưu mã và giờ, không lưu dữ liệu khác). Có nút "Xoá".

### Cách 2 — Hỏi bằng câu (gọi `agent.answer`)

- Ô nhập nhiều dòng với placeholder "VD: Khách hỏi AD26 ngày 20/11 từ 10h đến 16h còn size nào?".
- Có 3 câu gợi ý bấm vào để điền. Câu gợi ý **tự viết**, không chép câu nào trong `eval/benchmark.csv`, để tránh lẫn với bộ câu thử.
- Enter để gửi, Shift+Enter để xuống dòng. Nút "Hỏi trợ lý".
- **Tab luôn hiện. Trạng thái AI phải báo rõ để người dùng biết** (Toàn chốt):
  - **Chưa có API key** (`MODEL_PROVIDER=fake`, hoặc thiếu `API_KEY`/`MODEL_NAME`): băng vàng cố định trên ô nhập "Chưa có API key — AI chưa hoạt động. Hiện chỉ hiểu cú pháp `MÃ DD/MM/YYYY DD/MM/YYYY`. Dùng Form nhanh để kiểm tra đầy đủ." Có nút "Chuyển sang Form nhanh". Ô nhập vẫn dùng được (chạy mock).
  - **Hết token hoặc hết hạn mức** (API trả HTTP 429 có `insufficient_quota`, hoặc 402): bong bóng lỗi đỏ "AI đã hết token / hết hạn mức. Báo người quản lý tài khoản nạp thêm. Trong lúc chờ, dùng Form nhanh (không cần AI)." Chấm trạng thái trên thanh trên đổi thành đỏ "AI hết token", giữ tới khi tải lại trang.
  - **Gọi quá nhanh** (429 không có quota): "AI đang bị giới hạn tốc độ, thử lại sau ít giây", kèm nút Thử lại.
  - **Key sai hoặc bị thu hồi** (401/403): "API key không hợp lệ — kiểm tra file `.env`." Chấm trạng thái đỏ.
  - **Mất mạng hoặc timeout tới API** (URLError, timeout): "Không gọi được AI (mạng hoặc máy chủ AI). Thử lại hoặc dùng Form nhanh."
  - Lỗi khác: "AI gặp lỗi: <thông điệp ngắn>", không lộ key.
  - Chấm trạng thái trên thanh trên: xanh "AI thật · gpt-4o-mini", vàng "Chưa có API key", đỏ "AI hết token" hoặc "API key lỗi". Mỗi trạng thái luôn có chữ, không chỉ là chấm màu.
- **Trình bày câu trả lời:**
  - Dạng bong bóng chat.
  - Văn bản AI hiển thị **an toàn**: dùng `textContent`; chỉ đổi `**đậm**` và các dòng `- ` thành phần tử DOM, không dùng `innerHTML` với nội dung model trả về.
  - Dưới bong bóng có dòng nhỏ: "gpt-4o-mini · 2 lần gọi model · 2 lần gọi công cụ · 1.607→250 token · 6,7 s", lấy từ trace.
  - Có nhãn cố định: "AI soạn — chủ cửa hàng kiểm tra lại trước khi xác nhận với khách".
- Mỗi câu hỏi tốn token thật. Bấm gửi lần nữa khi đang chờ thì không làm gì.
- Hiện lịch sử hội thoại trong phiên. Mỗi câu là một lượt riêng (agent không nhớ ngữ cảnh), và trang ghi rõ điều này.

## 6. Vùng kết quả (cách 1)

**a) Tóm tắt** (một dòng to, câu chữ sinh từ dữ liệu):
- Tất cả size còn: ✔ xanh "AD26 còn cả 2 size".
- Một số hết: "AD26: còn 1/2 size".
- Không còn size nào: "AD26 đã kín lịch trong khung giờ này".
- `can_xac_minh`: ⚠ vàng "Cần chủ cửa hàng xác minh", kèm `ly_do` nguyên văn.

**b) Khung giờ đã dùng để tính:**
- Ví dụ: "Nhận 20/11/2026 09:00 *giả định* → Trả 20/11/2026 21:00 *giả định*".
- Thêm "Áo sẵn sàng lại: 21/11/2026 09:00" (lấy từ `san_sang_lai`).

**c) Thẻ từng size** (lưới 2 cột trên điện thoại, 3–4 cột trên máy tính):

| Trạng thái code | Thẻ | Màu, icon và chữ |
|---|---|---|
| `con` | **Size M** · "Còn 1/1" | Nền xanh nhạt, icon ✔ (SVG), chữ "Còn" |
| `trung_lich` | **Size XL** · "Hết 0/1" | Nền xám ấm, viền đỏ, icon ✕, chữ "Hết — trùng lịch" |
| `can_xac_minh` (của size) | **Size L** · "Cần xác minh" | Nền vàng nhạt, icon ⚠, kèm `ly_do` |

- Size khách cần được viền đậm. Nếu có số lượng: hiện "Khách cần 2 — **không đủ** (còn 1)".

**d) Đơn liên quan** (`don_lien_quan`), dạng **dòng thời gian ngang** trên máy tính và danh sách trên điện thoại:
- Mỗi đơn hiện: size, "Nhận 19/11 → Trả 20/11", trạng thái (Đang thuê / Khách đặt trước / Đang giặt / Đã hoàn tất) và "sẵn sàng 21/11 09:00".
- Quan hệ với khung khách hỏi:
  - `trung_khoang_giu_hoac_giat`: chip đỏ "Trùng".
  - `tiep_giap_khong_trung`: chip xám "Sát lịch, không trùng".
- Dòng thời gian vẽ bằng CSS hoặc SVG: thanh khung khách hỏi, thanh từng đơn, phần giặt kẻ sọc. Chỉ là phần thêm cho dễ nhìn; danh sách chữ luôn có, để đọc màn hình và để in.
- Không có đơn nào: "Không có đơn nào gần khung giờ này".

**e) Dòng nhắc cuối:** `luu_y` của công cụ, kèm câu cố định "Trợ lý chỉ kiểm tra, không chốt đơn".

**f) Lỗi mạng hoặc server:** thẻ đỏ "Không kết nối được máy chủ — kiểm tra `python webapp/server.py` còn chạy" và nút "Thử lại".

## 7. Giao diện

Nguồn: skill ui-ux-pro-max. Nhóm sản phẩm "Booking & Appointment App" gợi ý phong cách Soft UI và Flat, bảng màu "trust blue + available green + booked grey". Kết quả tạo design system tự động (Claymorphism, bố cục landing) **không hợp** với công cụ làm việc nên không dùng. Màu thương hiệu do mình tự chọn theo chất liệu áo dài, không có trong cơ sở dữ liệu của skill.

**Màu (CSS variables):**

| Token | Giá trị | Dùng cho |
|---|---|---|
| `--bg` | `#FAF7F2` (trắng ngà) | Nền trang |
| `--surface` | `#FFFFFF` | Thẻ, form |
| `--ink` | `#1F2430` | Chữ chính (≥ 12:1 trên nền) |
| `--muted` | `#5B6170` | Chữ phụ (≥ 4,5:1) |
| `--line` | `#E7E1D8` | Viền |
| `--brand` | `#2F3E9E` (xanh chàm, màu nhuộm truyền thống) | Nút chính, tab đang chọn, viền focus |
| `--brand-soft` | `#ECEEFB` | Nền nhấn nhẹ |
| `--ok` / `--ok-bg` | `#15803D` / `#ECFDF3` | Còn |
| `--busy` / `--busy-bg` | `#B42318` / `#F4F1EE` | Hết, trùng (nền xám ấm, chữ và viền đỏ) |
| `--warn` / `--warn-bg` | `#B54708` / `#FFFAEB` | Cần xác minh, giả định |

**Chữ:**
- **Be Vietnam Pro** (Google Fonts, có subset tiếng Việt, do người Việt thiết kế), các độ đậm 400, 500, 600, 700. Fallback `system-ui`.
- Cỡ chữ thân 16px, dòng 1,5. Tóm tắt kết quả 22–28px (dùng `clamp`). Số trên thẻ size 28px, đậm 700.
- Số và giờ dùng `font-variant-numeric: tabular-nums`.

**Hình khối:**
- Bo góc 14px cho thẻ, 10px cho ô nhập, 999px cho chip.
- Bóng nhẹ hai lớp, ví dụ `0 1px 2px rgb(0 0 0 / .05), 0 4px 16px rgb(31 36 48 / .06)`.
- Khoảng cách theo thang 4, 8, 12, 16, 24, 32, 48.

**Icon:** SVG nội tuyến kiểu Lucide (nét 2px), **không dùng emoji**. Icon chỉ để trang trí thì có `aria-hidden="true"`.

**Chuyển động:** 150–250ms, `ease-out`. Nút ấn xuống `scale(.98)`. Thẻ hover nhấc 1px. Tắt hết khi `prefers-reduced-motion`.

**Chế độ tối:** chưa làm trong đợt này (để dành, ghi trong README).

## 8. Truy cập và chất lượng (kiểm tra trước khi giao)

- Tương phản chữ ≥ 4,5:1. Trạng thái không chỉ dựa vào màu: luôn có icon và chữ.
- Mọi ô có `<label>` hiển thị (không dùng placeholder thay label). Lỗi gắn với ô qua `aria-describedby`.
- Dùng được hoàn toàn bằng bàn phím: thứ tự Tab hợp lý, focus ring 2px `--brand` nhìn rõ. Tab chọn kiểu dùng `role="tablist"` và di chuyển bằng phím mũi tên.
- Vùng chạm ≥ 44×44px. Khoảng cách giữa các nút ≥ 8px.
- Có `viewport meta`, không cuộn ngang ở 375px. Kiểm ở 375, 768, 1024 và 1440px.
- `lang="vi"`, có `<title>` và favicon SVG.
- Không có thư viện JS ngoài (vanilla JS); chỉ có font tải từ Google Fonts.

## 9. Kỹ thuật

**Files:**
```
webapp/
  SPEC.md        (file này)
  README.md      cách chạy, hai chế độ AI, giới hạn
  server.py      ThreadingHTTPServer, 127.0.0.1:8770
  static/index.html
  static/app.css
  static/app.js
  static/favicon.svg
```

**API** (JSON UTF-8; mọi lỗi trả `{"error": "..."}` kèm mã HTTP phù hợp):

| Route | Vào | Ra |
|---|---|---|
| `GET /api/info` | — | `{model_provider, model_name, ai_that: bool, data_source: "private"/"mock", so_ma, so_dong_lich}` |
| `GET /api/catalog` | — | `[{ma_ao, sizes:{M:1,...}}]`, sắp theo mã, chỉ có danh mục, không trả dòng lịch |
| `POST /api/check` | `{ma_ao, ngay_nhan:"YYYY-MM-DD", gio_nhan:"HH:MM"/null, ngay_tra, gio_tra:"HH:MM"/null}` | `{ket_qua: <nguyên dict check_availability>, gia_dinh_gio_nhan, gia_dinh_gio_tra, nhan_luc, tra_luc}` |
| `POST /api/ask` | `{text}`, tối đa 500 ký tự | `{output, trace:{model_calls, tool_calls, tokens_in, tokens_out, latency_s, model}}` |

**Quy tắc server:**
- `sys.path` thêm `codebase/`, rồi import `tools`, `agent`, `tracing`. Không sửa các module này.
- `/api/check`: chuẩn hoá mã bằng `strip().upper()`. Đây là quy ước của form, giống parser của agent. Ghép giờ mặc định 09:00 và 21:00 khi giờ để trống. Gọi `tools.check_availability(...)` và trả nguyên kết quả.
- `/api/ask`: gọi `tracing.begin("web")`, rồi `agent.answer(text)`, rồi `tracing.end()` (trong `finally`). Lấy tóm tắt token từ trace thật.
- **Phân loại lỗi `/api/ask`:** `ai.py` ném `RuntimeError("HTTP <code>: <body>")` khi API trả lỗi, và ném `RuntimeError("Thiếu MODEL_NAME hoặc API_KEY…")` khi thiếu cấu hình. Server đọc thông điệp và trả `{"error": "...", "loai": ...}`:

  | `loai` | Điều kiện | HTTP trả |
  |---|---|---|
  | `chua_co_key` | Thông điệp có "Thiếu MODEL_NAME hoặc API_KEY" | 503 |
  | `het_token` | `HTTP 429` và body có `insufficient_quota`, `quota` hoặc `credit`; hoặc `HTTP 402` | 402 |
  | `gioi_han_toc_do` | `HTTP 429` còn lại | 429 |
  | `key_loi` | `HTTP 401` / `HTTP 403` | 401 |
  | `mang` | `urllib.error.URLError`, `TimeoutError`, `socket.timeout` | 504 |
  | `khac` | Mọi exception khác | 502 |

  Thông điệp trả về là câu tiếng Việt ở §5, không kèm body thô của API, không lộ key.
- `/api/info` trả thêm `ai_trang_thai`: `"that"` khi provider khác `fake` và có đủ key và model; `"chua_co_key"` khi provider là `fake` hoặc thiếu key/model. Đọc biến `ai.MODEL_PROVIDER`, `ai.API_KEY`, `ai.MODEL_NAME`; **không trả giá trị key**. Không gọi API để thử, vì sẽ tốn token. Trạng thái hết token chỉ biết sau lần hỏi đầu tiên bị lỗi.
- Một `threading.Lock` bao quanh các lần gọi agent và công cụ, vì `tracing._case` là biến toàn cục.
- **Không ghi file nào**: không ghi trace ra đĩa, không ghi vào `eval/` hay `traces/`.
- Body POST tối đa 16KB. Chỉ phục vụ file trong `webapp/static/`, chặn `..` (trả 404).
- Đọc `.env` qua `ai.py` như hiện tại. Không in key ra log.

## 10. Kiểm thử chấp nhận (Opus chạy khi review, dữ liệu `private`)

| # | Thao tác | Kỳ vọng hiển thị |
|---|---|---|
| A1 | Form: AD26, 20/11/2026, không giờ | Có nhãn giả định 09:00 và 21:00. Thẻ M và XL **đúng theo JSON công cụ trả về**: so trực tiếp với `check_availability`, không so với `expected` của benchmark |
| A2 | Form: `ad26` viết thường | Nhận như AD26 |
| A3 | Form: AD99 | Thẻ vàng "Cần chủ cửa hàng xác minh · Không tìm thấy mã áo AD99." |
| A4 | Form: nhận 25/11, trả 20/11 | Lỗi ngay dưới ô trả, nút gửi bị khoá |
| A5 | Form: trả 22:00 | Cảnh báo vàng dưới ô. Gửi được, kết quả là cần xác minh với lý do 21:00 |
| A6 | Form: AD01 24/11/2026 | Thẻ S hết, đơn liên quan có "Đang giặt" và mốc sẵn sàng |
| A7 | Tab "Hỏi bằng câu", chế độ fake, gõ `AD02 28/11/2026 29/11/2026` | Có băng vàng "Chưa nối AI thật", hiện câu trả lời mock |
| A8 | Có `.env` thật: hỏi một câu tự nhiên | Bong bóng trả lời kèm dòng trace (model, số lần gọi, token) |
| A9 | Tắt server rồi bấm gửi | Thẻ lỗi kết nối và nút Thử lại |
| A10 | Màn 375px, chỉ dùng bàn phím, bật reduced-motion | Không cuộn ngang, đi hết luồng bằng Tab và Enter, không có chuyển động |
| A11 | `git status` sau khi chạy | Chỉ có file mới trong `webapp/`, không file nào khác bị sửa |

## 11. Quy trình

1. **Toàn duyệt spec này** (sửa hoặc đồng ý).
2. Sonnet code đúng spec trong `webapp/`.
3. Opus review: đọc code (an toàn XSS, khoá luồng, không ghi file, không sửa ngoài `webapp/`), chạy thử A1–A7, A9, A11 bằng request HTTP, và kiểm CSS cho responsive và tương phản. A8 cần API key nên chỉ chạy được khi đã có `.env`.
4. Báo kết quả. Chưa commit cho tới khi Toàn đồng ý.

## 12. Đã chốt (Toàn duyệt 28/11/2026)

1. Thư mục `webapp/`, cổng `8770`: theo spec (Toàn không yêu cầu đổi).
2. Bảng màu xanh chàm và trắng ngà: theo spec.
3. **Làm dòng thời gian** cho đơn liên quan (§6d), kèm danh sách chữ bên dưới.
4. **Tab "Hỏi bằng câu" luôn hiện.** Phải báo rõ khi chưa có API key, khi hết token, và các lỗi AI khác (§5, §9).

Thêm vào kiểm thử chấp nhận:
- **A12:** giả lập lỗi bằng cách thay `ai.call_openai` trong một script thử (không sửa `ai.py`): ném `RuntimeError("HTTP 429: {\"error\":{\"code\":\"insufficient_quota\"}}")`. Kỳ vọng `/api/ask` trả `loai = het_token`, mã 402, câu "AI đã hết token…".
- **A13:** chưa có `.env`. Kỳ vọng `/api/info` trả `ai_trang_thai = chua_co_key`, thanh trên hiện vàng "Chưa có API key".
