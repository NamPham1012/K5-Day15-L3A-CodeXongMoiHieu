"""Máy chủ cục bộ cho trang "Trợ lý kiểm tra lịch thuê áo dài".

Chạy:  python webapp/server.py   ->  http://127.0.0.1:8770
Chỉ dùng thư viện chuẩn. Không ghi file nào. Chỉ nghe 127.0.0.1.
Không sửa codebase/: chỉ import tools, agent, tracing, ai và gọi hàm có sẵn.
"""

import json
import mimetypes
import os
import re
import socket
import sys
import threading
import time
import urllib.error
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

WEBAPP_DIR = Path(__file__).resolve().parent
ROOT_DIR = WEBAPP_DIR.parent
STATIC_DIR = (WEBAPP_DIR / "static").resolve()
sys.path.insert(0, str(ROOT_DIR / "codebase"))

import ai  # noqa: E402  (đọc .env như hiện tại)
import agent  # noqa: E402
import tools  # noqa: E402
import tracing  # noqa: E402

HOST = "127.0.0.1"
PORT = 8770
MAX_BODY = 16 * 1024
MAX_ASK_CHARS = 500

# tracing dùng biến toàn cục nên mọi lần gọi công cụ/agent đi qua một khoá.
LOCK = threading.Lock()

ERROR_MESSAGES = {
    "chua_co_key": (
        "Chưa có API key — AI chưa hoạt động. Hiện chỉ hiểu cú pháp "
        "MÃ DD/MM/YYYY DD/MM/YYYY. Dùng Form nhanh để kiểm tra đầy đủ."
    ),
    "het_token": (
        "AI đã hết token / hết hạn mức. Báo người quản lý tài khoản nạp thêm. "
        "Trong lúc chờ, dùng Form nhanh (không cần AI)."
    ),
    "gioi_han_toc_do": "AI đang bị giới hạn tốc độ, thử lại sau ít giây.",
    "key_loi": "API key không hợp lệ — kiểm tra file .env.",
    "mang": "Không gọi được AI (mạng hoặc máy chủ AI). Thử lại hoặc dùng Form nhanh.",
}
ERROR_STATUS = {
    "chua_co_key": 503,
    "het_token": 402,
    "gioi_han_toc_do": 429,
    "key_loi": 401,
    "mang": 504,
    "khac": 502,
}


def ai_status() -> str:
    """'that' khi có provider thật cùng key và model; ngược lại 'chua_co_key'."""
    if ai.MODEL_PROVIDER == "fake" or not ai.API_KEY or not ai.MODEL_NAME:
        return "chua_co_key"
    return "that"


def data_source() -> str:
    return os.environ.get("RENTAL_DATA_SOURCE", "private").strip().lower()


def classify_error(exc: Exception) -> tuple:
    """Trả (loai, thông điệp tiếng Việt) theo bảng ở SPEC §9."""
    msg = str(exc)
    low = msg.lower()
    code_match = re.match(r"\s*HTTP (\d{3})", msg)
    code = int(code_match.group(1)) if code_match else None
    if "Thiếu MODEL_NAME hoặc API_KEY" in msg:
        loai = "chua_co_key"
    elif code == 402 or (
        code == 429 and any(k in low for k in ("insufficient_quota", "quota", "credit"))
    ):
        loai = "het_token"
    elif code == 429:
        loai = "gioi_han_toc_do"
    elif code in (401, 403):
        loai = "key_loi"
    elif isinstance(exc, (urllib.error.URLError, TimeoutError, socket.timeout)):
        loai = "mang"
    else:
        loai = "khac"
    if loai == "khac":
        if code is not None:
            short = f"máy chủ AI trả mã HTTP {code}."
        else:
            short = " ".join(msg.split())
            if ai.API_KEY:
                short = short.replace(ai.API_KEY, "***")
            short = short[:160] or type(exc).__name__
        return loai, f"AI gặp lỗi: {short}"
    return loai, ERROR_MESSAGES[loai]


def parse_date(value) -> "datetime.date":
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("Ngày phải có dạng YYYY-MM-DD.")
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_time(value, default: str):
    """Giờ HH:MM; trống/None thì dùng mặc định. Trả (time, là_giả_định)."""
    if value is None or value == "":
        return datetime.strptime(default, "%H:%M").time(), True
    if not isinstance(value, str) or not re.fullmatch(r"\d{2}:\d{2}", value):
        raise ValueError("Giờ phải có dạng HH:MM.")
    return datetime.strptime(value, "%H:%M").time(), False


def api_info() -> dict:
    with LOCK:
        data = tools.get_mock_data()
    return {
        "model_provider": ai.MODEL_PROVIDER,
        "model_name": ai.MODEL_NAME,
        "ai_that": ai_status() == "that",
        "ai_trang_thai": ai_status(),
        "data_source": data_source(),
        "so_ma": len(data.get("inventory", [])),
        "so_dong_lich": len(data.get("rentals", [])),
    }


def api_catalog() -> list:
    with LOCK:
        data = tools.get_mock_data()
    items = [
        {"ma_ao": item.get("ma_ao", ""), "sizes": item.get("sizes") or {}}
        for item in data.get("inventory", [])
    ]
    return sorted(items, key=lambda item: item["ma_ao"])


def api_check(body: dict) -> dict:
    ma_ao = body.get("ma_ao")
    if not isinstance(ma_ao, str) or not ma_ao.strip() or len(ma_ao.strip()) > 32:
        raise ValueError("Thiếu mã áo.")
    ma_ao = ma_ao.strip().upper()
    ngay_nhan = parse_date(body.get("ngay_nhan"))
    ngay_tra = parse_date(body.get("ngay_tra"))
    gio_nhan, gia_dinh_nhan = parse_time(body.get("gio_nhan"), "09:00")
    gio_tra, gia_dinh_tra = parse_time(body.get("gio_tra"), "21:00")
    nhan_luc = datetime.combine(ngay_nhan, gio_nhan)
    tra_luc = datetime.combine(ngay_tra, gio_tra)
    with LOCK:
        ket_qua = tools.check_availability(ma_ao, nhan_luc.isoformat(), tra_luc.isoformat())
    return {
        "ket_qua": ket_qua,
        "gia_dinh_gio_nhan": gia_dinh_nhan,
        "gia_dinh_gio_tra": gia_dinh_tra,
        "nhan_luc": nhan_luc.isoformat(),
        "tra_luc": tra_luc.isoformat(),
    }


def api_ask(body: dict) -> tuple:
    """Trả (HTTP status, payload)."""
    text = body.get("text")
    if not isinstance(text, str) or not text.strip():
        return 400, {"error": "Hãy nhập câu hỏi.", "loai": "dau_vao"}
    if len(text) > MAX_ASK_CHARS:
        return 400, {"error": f"Câu hỏi tối đa {MAX_ASK_CHARS} ký tự.", "loai": "dau_vao"}
    started = time.perf_counter()
    summary = None
    seen = {}
    original = agent.check_availability

    def watch(*args, **kwargs):
        # Chỉ ghi lại kết quả công cụ để vẽ thẻ size; không đổi input/output.
        out = original(*args, **kwargs)
        seen["ket_qua"] = out
        return out

    try:
        with LOCK:
            tracing.begin("web")
            agent.check_availability = watch
            try:
                result = agent.answer(text.strip())
            finally:
                agent.check_availability = original
                summary, _events = tracing.end()
    except Exception as exc:  # noqa: BLE001 - phân loại rồi trả thông điệp an toàn
        loai, message = classify_error(exc)
        return ERROR_STATUS[loai], {"error": message, "loai": loai}
    models = summary["models"]
    model = models[0] if models else ("fake" if ai.MODEL_PROVIDER == "fake" else "")
    return 200, {
        "output": str(result.get("output", "")),
        "ket_qua": seen.get("ket_qua"),
        "trace": {
            "model_calls": summary["model_calls"],
            "tool_calls": summary["tool_calls"],
            "tokens_in": summary["tokens_in"],
            "tokens_out": summary["tokens_out"],
            "latency_s": round(time.perf_counter() - started, 1),
            "model": model,
        },
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "MienWebapp/1.0"

    def _send(self, status: int, body: bytes, content_type: str, extra=None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; style-src 'self' https://fonts.googleapis.com; "
            "font-src https://fonts.gstatic.com; img-src 'self' data:; "
            "connect-src 'self'; base-uri 'none'; form-action 'self'",
        )
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def _error(self, status: int, message: str) -> None:
        self._json(status, {"error": message})

    def do_GET(self) -> None:  # noqa: N802
        path = unquote(urlsplit(self.path).path)
        host = (self.headers.get("Host") or "").lower()
        if host not in (f"127.0.0.1:{PORT}", f"localhost:{PORT}"):
            return self._error(403, "Chỉ nhận yêu cầu từ trang cục bộ.")
        try:
            if path == "/api/info":
                return self._json(200, api_info())
            if path == "/api/catalog":
                return self._json(200, api_catalog())
            if path.startswith("/api/"):
                return self._error(404, "Không có đường dẫn này.")
            return self._static(path)
        except Exception as exc:  # noqa: BLE001
            return self._error(500, f"Lỗi máy chủ: {type(exc).__name__}")

    def do_POST(self) -> None:  # noqa: N802
        path = urlsplit(self.path).path
        if path not in ("/api/check", "/api/ask"):
            return self._error(404, "Không có đường dẫn này.")
        # Chặn trang web lạ gọi thẳng vào máy chủ cục bộ (tốn token, DNS rebinding):
        # chỉ nhận Host cục bộ và JSON (trình duyệt buộc preflight CORS, máy chủ không cho).
        host = (self.headers.get("Host") or "").lower()
        if host not in (f"127.0.0.1:{PORT}", f"localhost:{PORT}"):
            return self._error(403, "Chỉ nhận yêu cầu từ trang cục bộ.")
        ctype = (self.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        if ctype != "application/json":
            return self._error(415, "Nội dung phải là application/json.")
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            return self._error(411, "Thiếu độ dài nội dung.")
        if length < 0:
            return self._error(400, "Độ dài nội dung không hợp lệ.")
        if length > MAX_BODY:
            self.close_connection = True
            return self._error(413, "Nội dung gửi lên quá lớn (tối đa 16KB).")
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(body, dict):
                raise ValueError("Nội dung phải là một đối tượng JSON.")
        except (ValueError, UnicodeDecodeError):
            return self._error(400, "Nội dung gửi lên không phải JSON hợp lệ.")
        try:
            if path == "/api/check":
                return self._json(200, api_check(body))
            status, payload = api_ask(body)
            return self._json(status, payload)
        except ValueError as exc:
            return self._error(400, str(exc))
        except Exception as exc:  # noqa: BLE001
            return self._error(500, f"Lỗi máy chủ: {type(exc).__name__}")

    def _static(self, path: str) -> None:
        if "\x00" in path:
            return self._error(404, "Không tìm thấy.")
        rel = "index.html" if path in ("", "/") else path.lstrip("/")
        target = (STATIC_DIR / rel).resolve()
        if STATIC_DIR not in target.parents or not target.is_file():
            return self._error(404, "Không tìm thấy.")
        ctype = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript", "image/svg+xml"):
            ctype += "; charset=utf-8"
        self._send(200, target.read_bytes(), ctype)

    def log_message(self, fmt, *args) -> None:  # noqa: D102
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    mimetypes.add_type("image/svg+xml", ".svg")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    server.daemon_threads = True
    print(f"Trợ lý lịch thuê áo dài: http://{HOST}:{PORT}  (Ctrl+C để dừng)")
    print(f"Trạng thái AI: {ai_status()} · nguồn dữ liệu: {data_source()}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
