# Spec — trang demo CP2 "Kiểm tra lịch thuê" (web/)

Người viết spec: Opus. Người code: Sonnet. Người review: Opus.
Ngày: 27/11/2026. Repo ở commit main `79ab4b5`.

## 0. Mục tiêu

Một trang web chạy trên máy (localhost) để nhóm làm 5 việc của checklist CP2 trên giao diện thay vì terminal:

1. Thấy bản code đang chạy là commit nào, có khớp `origin/main` không, và tra lịch giống `python run.py`.
2. Chạy 6 nhóm ca thử yêu cầu, thấy input / kỳ vọng / kết quả thực tế / đạt-trượt.
3. Chạy các ca kiểm 3 quy tắc với Nam.
4. Xem và sao chép danh sách lỗi theo mẫu Input / Kỳ vọng / Kết quả thực tế / Mức độ ảnh hưởng.
5. Bấm chạy 2 ca demo CP2 (1 ca thường, 1 ca cần xác minh) kèm lời nói rõ giới hạn.

**Nguyên tắc cứng: mọi "Kết quả thực tế" và mọi "Đạt/Trượt" được TÍNH LẠI mỗi lần chạy, từ code thật** (`codebase/agent.py`, `codebase/tools.py`). Không có kết quả nào viết sẵn trong HTML/JS. Nếu sau này code được sửa, trang tự đổi kết quả. Đây là cách thực hiện "không sửa kết quả để che lỗi".

## 1. Ràng buộc (bắt buộc)

- **Không sửa** bất kỳ file nào ngoài thư mục `web/`. Đặc biệt không sửa `codebase/*`, `data/*`, `run.py`, `eval/*`, `cost/*`, `spec.md`, `AGENTS.md`. Không sửa lỗi trong agent/tools — trang chỉ báo lỗi.
- Không sửa `data/mock_rental.json`. Ca cần data khác dùng data tạm **trong bộ nhớ**: gán tạm `tools.get_mock_data = lambda: data`, chạy, rồi **luôn khôi phục** hàm gốc trong `finally`.
- Chỉ thư viện chuẩn Python (`http.server`, `json`, `subprocess`, `csv`, `re`, `pathlib`, `threading`). Không thêm `requirements.txt`.
- Server chỉ nghe `127.0.0.1`, cổng mặc định `8765` (cho đổi bằng `--port`). Dùng `ThreadingHTTPServer` nhưng giữ một `threading.Lock` quanh mọi lần chạy ca (vì monkeypatch là toàn cục).
- Không gửi gì ra ngoài. Ngoại lệ duy nhất: trang tải Google Fonts (Geist, Geist Mono). Lệnh git chỉ đọc local (`git rev-parse`, `git rev-list --count HEAD..origin/main`), **không** `git fetch`.
- Không ghi file trace/eval: không gọi `tracing.begin()`. (Đã thử: gọi `answer()` ngoài `begin` không ghi file.)
- Tiếng Việt có dấu đầy đủ trên toàn trang, `<html lang="vi">`.

## 2. Cấu trúc file

```
web/
  SPEC.md            (file này)
  server.py          HTTP server + API
  scenarios.py       định nghĩa ca thử, data tạm, hàm chấm; chạy được độc lập: python web/scenarios.py (in bảng ra terminal)
  index.html         trang
  app.js             logic trang (gọi API, vẽ bảng)
  page.css           CSS riêng của trang (chỉ phần kit không có: bảng kết quả, nhãn trạng thái, khối output)
  assets/            bản sao kit taste-skill (chỉ những file dùng): system.css, system.js, motion/motion.css, motion/motion.js
  README.md          cách chạy (3-5 dòng)
```

Chạy: `python web/server.py` rồi mở `http://127.0.0.1:8765`. In URL ra terminal khi khởi động.

Kit nằm ở `C:/Users/Admin/.claude/skills/design-taste-frontend/assets/`. Copy `system.css`, `system.js`, `motion/motion.css`, `motion/motion.js` vào `web/assets/` (giữ nguyên nội dung, không sửa file kit).

`server.py` thêm `ROOT/codebase` vào `sys.path` rồi `import tools, agent`.

## 3. API

Tất cả trả JSON UTF-8 (`ensure_ascii=False`).

| Route | Trả về |
|---|---|
| `GET /` và file tĩnh trong `web/` | phục vụ file; chặn `..` ra ngoài `web/` |
| `GET /api/info` | `{"branch", "commit" (7 ký tự), "commit_subject", "behind_main": int hoặc null, "dirty": bool}` — `dirty` từ `git status --porcelain` có dòng nào ngoài `web/` và `.taste-skill/` |
| `POST /api/answer` body `{"text": str}` | `{"input": text, "output": agent.answer(text)["output"]}`; exception → `{"input", "error": "TênLỗi: thông điệp"}` (HTTP 200) |
| `GET /api/cases` | chạy TOÀN BỘ ca, trả `{"ran_at": ISO, "groups": [...], "bugs": [...]}` (xem §4, §5) |
| `GET /api/demo` | chạy 2 ca demo (§6), cùng hình dạng một ca |

Một ca trả về:
```json
{"id": "R1", "title": "...", "input": "chuỗi input hiển thị", "data_note": "data dùng (vd 'data hiện tại' hoặc mô tả đơn tạm)",
 "via": "agent" | "tool" | "file", "expected": "...", "actual": "chuỗi kết quả thực tế", "status": "dat|mot_phan|truot|chua_ho_tro|can_chot",
 "note": "ghi chú ngắn, có thể rỗng"}
```
`actual` với `via: "agent"` = nguyên văn `output` (giữ xuống dòng). Với `via: "tool"` = JSON gọn của `{trang_thai, ly_do?, sizes?, san_sang_lai?}`. Exception → `actual = "CRASH: TênLỗi: thông điệp"`, và hàm chấm nhận được chuỗi đó.

Nhãn trạng thái tiếng Việt: dat → "Đạt", mot_phan → "Đạt một phần", truot → "Trượt", chua_ho_tro → "Chưa hỗ trợ", can_chot → "Cần Nam chốt".

## 4. Ca thử (`scenarios.py`)

Inventory tạm cho mọi ca dùng data tạm: `[{"ma_ao": "AD02", "sizes": {"S": 1, "L": 1, "XL": 2}}]`.
Hàm tạo đơn: `rent(size, nhan, tra, trang_thai="Khách đặt trước", ma="AD02")`; `size=MISSING` nghĩa là không có khoá `size`.
Q = `"AD02 28/11/2026 29/11/2026"`.

"Còn N" trong output agent = dòng `- Size X: còn N áo.`; "trùng" = dòng `- Size X: đã hết do trùng lịch.`. Viết hàm `size_line(output, size)` trả nội dung dòng size đó. Hàm chấm phải đọc output, **không** so khớp cả chuỗi.

### Nhóm 1 — "Ca thử yêu cầu" (mục 2 checklist)

| id | title | via | input / data | expected | chấm |
|---|---|---|---|---|---|
| R1 | Ca thường AD02 | agent | Q, data hiện tại (file thật) | S còn 1, L còn 1, XL còn 1 | dat nếu cả 3 dòng đúng, else truot |
| R2 | Mã không tồn tại | agent | `AD99 28/11/2026 29/11/2026`, data hiện tại | Báo cần xác minh | dat nếu có "xác minh" (không phân biệt hoa) và "AD99" |
| R3a | Ngày không có thật | agent | `AD02 31/11/2026 01/12/2026` | Báo lỗi ngày | dat nếu có "Ngày không hợp lệ" |
| R3b | Ngày nhận sau ngày trả | agent | `AD02 29/11/2026 28/11/2026` | Báo lỗi ngày, yêu cầu nhập lại | dat nếu có "không hợp lệ"; mot_phan nếu có "xác minh"; else truot |
| R4a | Đơn trùng, không có trường size | agent | Q; đơn `rent(MISSING, 28/11 09:00, 29/11 21:00)` | Không khẳng định còn áo | dat nếu có "xác minh" và không có dòng "còn" nào |
| R4b | Đơn trùng, size rỗng | agent | Q; `rent("", …)` | như R4a | như R4a |
| R4c | Đơn trùng, size "2XL" | agent | Q; `rent("2XL", …)` | như R4a | như R4a |
| R4d | Đơn thiếu size nhưng không trùng | agent | Q; `rent("", 01/10 09:00, 02/10 21:00)` | Không ảnh hưởng: S 1, L 1, XL 2 | dat nếu S còn 1, L còn 1, XL còn 2 |
| R5a | Nhận 08:59 khi áo sẵn sàng 09:00 | tool | `check_availability("AD02","2026-11-28T08:59:00","2026-11-28T21:00:00")`; đơn S "Đã hoàn tất" 26/11 09:00 → 27/11 21:00 | S chưa sẵn sàng | dat nếu sizes.S.trang_thai == "trung_lich" |
| R5b | Nhận đúng 09:00 | tool | như R5a, nhận 09:00 | S còn | dat nếu sizes.S.trang_thai == "con" |
| R5c | Nhập giờ 08:59 qua giao diện dòng lệnh | agent | `AD02 08:59 28/11/2026 28/11/2026`, cùng data R5a | Kiểm được theo giờ | chua_ho_tro nếu output bắt đầu "Bản mock chỉ nhận"; dat nếu S trùng |
| R6a | Đơn kế tiếp nhận 08:00 hôm sau | agent | Q; đơn S nhận 30/11 08:00 → 30/11 21:00 | S trùng (áo khách mới sẵn sàng 30/11 09:00) | dat nếu dòng S là "trùng" |
| R6b | Đơn kế tiếp nhận đúng 09:00 | agent | Q; đơn S nhận 30/11 09:00 | S còn 1 | dat nếu S còn 1 |
| R6c | Khách mới trả 18:00, đơn sau nhận 20:00 cùng ngày | tool | `check_availability("AD02","2026-11-28T09:00:00","2026-11-29T18:00:00")`; đơn S 29/11 20:00 → 30/11 21:00 | S trùng | dat nếu S "trung_lich" |

### Nhóm 2 — "Quy tắc kiểm với Nam" (mục 3)

| id | quy tắc | via | input / data | expected | chấm |
|---|---|---|---|---|---|
| N1a | Đang giặt | agent | Q; đơn S "Đang giặt" 26/11 09:00 → 27/11 21:00 | S còn 1 (sẵn sàng 28/11 09:00 dù trạng thái chưa đổi) | dat nếu S còn 1 |
| N1b | Đang giặt | agent | `AD02 27/11/2026 27/11/2026`; cùng đơn | S trùng | dat nếu S trùng |
| N1c | Đang thuê quá hạn chưa cập nhật | agent | Q; đơn S "Đang thuê" 24/11 09:00 → 25/11 21:00 | Cần Nam chốt: có coi là đã trả không? | luôn can_chot; note: "Code hiện tính là đã trả và báo còn." nếu S còn 1 |
| N2a–c | HỦY không giữ áo | agent | Q; đơn S trùng 28–29/11 với trạng thái lần lượt `HỦY`, `Hủy`, `đã hủy` | S còn 1 | dat nếu S còn 1 |
| N2d–f | HỦY không giữ áo | agent | như trên với `Huỷ`, `Đã huỷ`, `HỦY ĐƠN` | S còn 1 | dat nếu S còn 1; truot nếu có "xác minh" hoặc khác |
| N3a | Thiếu dữ liệu | agent | Q; đơn S trùng, không có khoá `trang_thai` | Cần xác minh | dat nếu có "xác minh" |
| N3b | Thiếu dữ liệu | agent | Q; đơn S trùng, `trang_thai: None` | Cần xác minh | dat nếu có "xác minh"; truot nếu CRASH |
| N3c | Thiếu dữ liệu | agent | Q; đơn S "Đang thuê" không có `tra_luc` | Cần xác minh | dat nếu có "xác minh" |
| N3d | Sau 21:00 | agent | Q; đơn S "Đã hoàn tất" 27/11 09:00 → 27/11 22:00 | Cần xác minh | dat nếu có "xác minh" |
| N3e | Sau 21:00 | tool | `check_availability("AD02","2026-11-28T09:00:00","2026-11-29T22:00:00")`, không đơn | Cần xác minh | dat nếu trang_thai == "can_xac_minh" |
| N3f | Thiếu dữ liệu | agent | Q; đơn S "Đang thuê" trùng, không có khoá `ma_ao` | Cảnh báo cần xác minh | dat nếu có "xác minh"; else truot |
| N3g | Thiếu/sai dữ liệu | agent | Q; đơn S trùng với `ma_ao: "ad02"` | Không báo S còn | dat nếu S trùng hoặc có "xác minh"; truot nếu S còn 1 |
| N3h | Dữ liệu bất thường không liên quan | agent | Q; đơn S "Đã hoàn tất" 01/01/2025 09:00 → 01/01/2025 22:00 | Không ảnh hưởng (đơn không trùng) | dat nếu S còn 1; truot nếu có "xác minh" |
| N3i | Đơn chỉ có ngày | agent | Q; `rent("S", "2026-11-28", "2026-11-29")` | Cần xác minh hoặc nêu rõ giả định giờ | dat nếu có "xác minh"; mot_phan nếu S trùng (kết luận đúng nhưng giả định ẩn 00:00) |

### Ca phụ cho danh sách lỗi

| id | via | input | expected | chấm |
|---|---|---|---|---|
| X1 | agent | `"\ufeffAD02 28/11/2026 29/11/2026"` (input dán từ PowerShell, có BOM) — hiển thị input là `[BOM]AD02 28/11/2026 29/11/2026` | Như R1 | dat nếu như R1; truot nếu "Bản mock chỉ nhận" |
| X2 | agent | câu benchmark B01 đọc từ `eval/benchmark.csv` (cột input của id B01, `encoding="utf-8-sig"`) | Hiểu câu tự nhiên | chua_ho_tro nếu "Bản mock chỉ nhận" |
| X3 | file | so mã áo trong `data/mock_rental.json` với mọi mã `AD\d+` trong cột input của benchmark | Mọi mã benchmark có trong data | actual = "Data có: AD02, AD03. Benchmark dùng: AD01, AD02, … Thiếu: …"; dat nếu không thiếu |
| X4 | file | đếm cột `type` trong benchmark; so với chuỗi trong `spec.md` §7 (tìm bằng regex `(\d+) thuong, (\d+) kho, (\d+) tu_choi`) | Số trong spec khớp benchmark | actual = "spec.md ghi: 7 thuong / 10 kho / 3 tu_choi. Benchmark có: 5 / 12 / 3"; dat nếu khớp |
| X5 | agent | đơn S "Khách đặt trước" 30/11 08:00 (như R6a) | Nêu căn cứ: đơn nào chiếm, sẵn sàng lúc nào | truot nếu dòng S chỉ là "đã hết do trùng lịch." không có giờ/ngày; dat nếu dòng S có ngày giờ |

## 5. Danh sách lỗi (`bugs`)

Mỗi lỗi trỏ tới một ca. Trường `input`, `expected`, `actual` lấy từ ca đó (actual là kết quả vừa chạy). `severity` và `impact` viết cố định trong `scenarios.py`. Trường `status`: "Còn lỗi" nếu ca chưa dat, "Đã hết lỗi" nếu ca đã dat (trang vẫn hiện dòng đó, gạch xanh).

| # | ca | severity | impact (câu ngắn) |
|---|---|---|---|
| 1 | N3b | Cao | Ô trạng thái trống là chuyện thường khi nối Sheet; cả mã áo không tra được. |
| 2 | N3g | Cao | Báo còn sai, dẫn tới cho thuê trùng một áo. |
| 3 | R5c | Cao | Ranh giới 08:59/09:00 và giờ trả 22:00 chỉ kiểm được ở công cụ; các câu benchmark có giờ sẽ trượt. |
| 4 | X2 | Cao | Khoảng 17/20 câu benchmark là câu tự nhiên, sẽ chỉ nhận lại hướng dẫn cú pháp. |
| 5 | X3 | Cao | Chạy eval sẽ báo không tìm thấy mã; DATA_CARD.md ghi 130 mã / 281 bản ghi, không khớp file. |
| 6 | X1 | Trung bình | Chạy python run.py trong PowerShell với input dán/pipe bị từ chối dù gõ đúng cú pháp. |
| 7 | N3f | Trung bình | Đơn thiếu mã áo bị bỏ qua im lặng, trái quy tắc "thiếu dữ liệu phải báo". |
| 8 | N2d | Trung bình | An toàn nhưng báo xác minh thừa; cần chuẩn hoá Unicode khi đọc Sheet. |
| 9 | N3h | Trung bình | Một dòng lỗi cũ chặn cả mã áo mãi mãi. |
| 10 | R3b | Thấp | Đúng ý nhưng sai nhãn: lỗi nhập liệu không cần chủ cửa hàng xác minh. |
| 11 | X5 | Thấp | Chủ cửa hàng khó tư vấn khách ngày khác; benchmark B08, B09, B12 đòi căn cứ. |
| 12 | N3i | Thấp | Ra kết quả đúng nhưng giả định 00:00 ẩn. |
| 13 | X4 | Thấp | Sửa số trong spec cho khớp, không đổi chuẩn đạt. |

Thứ tự hiển thị: Cao → Trung bình → Thấp (như bảng). Đánh số lại theo thứ tự hiển thị.

## 6. Demo CP2

- Ca thường: agent, `AD02 28/11/2026 29/11/2026`, data hiện tại. Lời nói (cố định): "XL có 2 áo, 1 đơn Khách đặt trước đúng ngày nên còn 1. L có đơn HỦY nên vẫn còn 1. Chỉ có ngày nên mặc định nhận 09:00, trả 21:00 và hiện rõ giả định."
- Ca cần xác minh: agent, `AD99 28/11/2026 29/11/2026`. Lời nói: "Không đủ căn cứ thì hệ thống không đoán, trả quyền quyết định cho chủ cửa hàng."
- Lời mở đầu (luôn hiện ở đầu khối demo VÀ trong hero): "Bản này dùng data giả lập và model fake, chưa gọi model thật. Kết quả do code tính, không phải AI sinh. Chưa hiểu câu hỏi tự nhiên, chỉ nhận MÃ_ÁO DD/MM/YYYY DD/MM/YYYY. Chưa kết nối Google Sheet thật."

## 7. Trang (index.html)

Dùng kit taste-skill: `assets/system.css`, `assets/system.js`, `assets/motion/*`. Đọc `C:/Users/Admin/.claude/skills/design-taste-frontend/assets/starter.html` để lấy đúng markup header/nav/footer/skip-link/btn/form và `references/system.md` cho quy tắc. Không viết grid, nút, card, spacing riêng — dùng class và token của kit. `page.css` chỉ cho bảng, nhãn trạng thái, khối `<pre>` output.

Head:
```html
<html lang="vi" data-type="software" data-radius="soft" data-buttons="solid" data-motion>
<meta name="page-type" content="software"><meta name="site-kind" content="software">
<title>MiênAI: kiểm tra lịch thuê áo dài cho chủ cửa hàng</title>
<meta name="description" content="Trang chạy thử CP2: tra lịch thuê theo size, chạy ca thử và xem danh sách lỗi từ code thật.">
<meta name="theme-color" content="#f7f7f7">
```
Font: `<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400..700&family=Geist+Mono:wght@400..500&display=swap" rel="stylesheet">` (Funnel bị loại vì không có bộ ký tự tiếng Việt).

Token (dán nguyên sau các link CSS):
```css
:root {
  --p-bg: #f7f7f7; --p-surface: #ebebeb; --p-ink: #0d2a1c; --p-muted: #5f6b64;
  --p-accent: #f6e016; --p-accent-ink: #0d2a1c; --p-action: #0d2a1c; --p-action-ink: #f7f7f7;
  --p-inv-bg: #0d2a1c; --p-inv-surface: #1c3629; --p-inv-ink: #f7f7f7; --p-inv-muted: #97a39c;
  --p-inv-accent: #f6e016; --p-inv-accent-ink: #0d2a1c; --p-inv-action: #f6e016; --p-inv-action-ink: #0d2a1c;
  --font-display: "Geist", system-ui, sans-serif;
  --font-text: "Geist", system-ui, sans-serif;
  --font-mono: "Geist Mono", ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
  --display-weight: 500; --display-tracking: -0.035em; --display-tracking-xl: -0.045em;
}
```
Đã bốc: nav-mega (ở đây không cần panel mega, chỉ nav thường của kit), footer-columns, nút solid, logo `<span class="mark mark--initial">M</span>` + "MiênAI". Màu vàng `--p-accent` chỉ dùng cho điểm nhấn nhỏ (dấu chấm trạng thái "Còn lỗi"/hạng Cao không dùng vàng — xem dưới). Không violet.

Nav: skip link "Bỏ qua đến nội dung"; logo; 5 mục: "Tra lịch", "Ca thử", "Quy tắc", "Lỗi", "Demo" (mỗi mục một anchor); nút chính "Chạy bộ ca thử" (gọi `/api/cases` và cuộn tới "Ca thử").

Các section (`main id="top" > section`, mỗi section một `.wrap`, h2 đầu tiên):

1. **Hero `#tra-lich`** (`data-enter`): h1 "Kiểm tra lịch thuê áo dài theo size". Dòng fact: "Bản chạy thử CP2 · nhánh {branch} · commit {commit} · {khớp main | chậm N commit so với main | có thay đổi chưa commit}" (từ `/api/info`). Khối lời mở đầu §6 (một đoạn, không phải box trong box). Form tra lịch: 3 field text có `<label>` nhìn thấy: "Mã áo" (mặc định AD02), "Ngày nhận" (28/11/2026), "Ngày trả" (29/11/2026); dưới form hiện dòng "Gửi vào hệ thống: `AD02 28/11/2026 29/11/2026`" cập nhật khi gõ; nút "Tra lịch thuê". Kèm một field phụ "Hoặc gõ nguyên dòng như python run.py" (gửi thẳng text). Kết quả: `<pre>` output nguyên văn + nếu parse được dòng size thì hiện danh sách size dạng `.rows` (Size · trạng thái). Lỗi mạng/exception: hiện dưới form trong `role="status"`.
2. **`#ca-thu` "Kết quả 6 ca thử yêu cầu"**: một dòng tổng "N/M đạt · chạy lúc HH:MM:SS". Bảng: # · Ca · Input · Kỳ vọng · Kết quả thực tế · Đánh giá. Input và kết quả thực tế dùng `<code>`/`<pre>` font mono, giữ xuống dòng, cắt gọn tối đa ~6 dòng với nút "Xem đủ" (details/summary). Cột "Qua" nhỏ dưới Input: "qua agent" / "gọi thẳng công cụ" + data_note.
3. **`#quy-tac` "Ba quy tắc kiểm với Nam"**: cùng bảng, nhóm theo quy tắc (Đang giặt / HỦY / Thiếu dữ liệu và sau 21:00) bằng một hàng tiêu đề nhóm. Ca `can_chot` hiển thị nổi bật kèm câu hỏi.
4. **`#loi` "Danh sách lỗi gửi Nam"**: dòng tổng "X lỗi còn mở: a Cao, b Trung bình, c Thấp". Bảng: # · Input · Kỳ vọng · Kết quả thực tế · Mức độ ảnh hưởng (hạng + câu impact) · Trạng thái. Nút "Sao chép bảng lỗi" → clipboard dạng bảng Markdown đúng 4 cột mẫu (Input | Kỳ vọng | Kết quả thực tế | Mức độ ảnh hưởng), xuống dòng trong ô thay bằng `<br>`, `|` escape. Sau khi chép, status "Đã chép N dòng". Ghi chú một dòng: "Kết quả thực tế được chạy lại từ code mỗi lần tải trang, không chỉnh tay."
5. **`#demo` "Demo CP2: hai ca"**: lời mở đầu §6; 2 cột (một cột mỗi ca): tiêu đề "Ca thường" / "Ca cần xác minh", input mono, nút "Chạy ca thường" / "Chạy ca cần xác minh" (secondary), output `<pre>`, lời nói §6 bên dưới.
6. **Footer** (footer-columns, rút gọn): "MiênAI · bản chạy thử nhóm CodeXongMoiHieu · 2026"; dòng "Data giả lập · model fake · chạy trên máy". Không link Privacy/Terms giả, không địa chỉ, không SĐT.

Trạng thái (nhãn chữ + chấm màu, không chỉ màu): Đạt = xanh lá đậm (ink trên nền #e5f4e4), Trượt = đỏ (#8a1c1c trên #fbebeb), Đạt một phần / Cần Nam chốt = cam (#7a4a00 trên #f9eeda), Chưa hỗ trợ = xám (muted trên surface). Hạng Cao/Trung bình/Thấp dùng cùng bảng màu đỏ/cam/xám. Tương phản chữ ≥ 4.5:1.

Bảng: `<table>` thật, `<th scope="col">`, có `<caption class="visually-hidden">`. Ở ≤ 767px mỗi hàng thành một khối dọc (label từ `data-label` qua CSS `::before`), không cuộn ngang trang. Không nội dung nào tràn ở 390 và 320.

Tải trang: tự gọi `/api/info` và `/api/cases` một lần; trong lúc chờ hiện "Đang chạy ca thử…" trong `role="status"`. Nút "Chạy lại" cạnh mỗi dòng tổng. Không animation khi cuộn; hover/press theo motion layer của kit. Tôn trọng `prefers-reduced-motion`.

Copy: câu thường, rõ, không quảng cáo. Nút = động từ + vật ("Tra lịch thuê", "Chạy bộ ca thử", "Sao chép bảng lỗi"). Không "Tìm hiểu thêm".

## 8. Kiểm tra trước khi giao (người code tự làm)

1. `python web/scenarios.py` in bảng tất cả ca + trạng thái; đối chiếu với kỳ vọng ở cuối spec này.
2. `python web/server.py`, rồi gọi `curl` cả 5 route; `/api/cases` trả JSON hợp lệ.
3. Sau khi chạy: `git status --short` chỉ có `web/` và `.taste-skill/` là mới; không file nào khác đổi.
4. Chụp màn hình bằng script của kit (không mở trình duyệt tay):
   `node C:/Users/Admin/.claude/skills/design-taste-frontend/scripts/shoot.mjs --url http://127.0.0.1:8765/ --w 1440 --out web/shots/1440.png --profile .taste-skill/chrome-check` và `--w 390`. (Nếu script không nhận URL http, báo lại, đừng sửa kit.) Thư mục `web/shots/` không commit — liệt kê trong báo cáo.
5. `node C:/Users/Admin/.claude/skills/design-taste-frontend/scripts/copy-lint.mjs web/index.html --kind software` — báo FAIL/WARN, sửa cái nào hợp lý; copy-lint viết cho tiếng Anh nên WARN về từ tiếng Việt có thể bỏ qua, ghi lý do.

### Trạng thái kỳ vọng với code hiện tại (commit 79ab4b5) — để tự kiểm hàm chấm

dat: R1 R2 R3a R4a R4b R4c R4d R5a R5b R6a R6b R6c N1a N1b N2a N2b N2c N3a N3c N3d N3e
mot_phan: R3b N3i
chua_ho_tro: R5c X2
can_chot: N1c
truot: N2d N2e N2f N3b N3f N3g N3h X1 X3 X4 X5

Nếu hàm chấm cho kết quả khác danh sách này, **xem lại hàm chấm hoặc data tạm, KHÔNG chỉnh hàm chấm cho khớp nếu output thật khác** — báo lại sự khác biệt.
