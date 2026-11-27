"""Server local cho trang demo CP2. Chỉ thư viện chuẩn. Chỉ nghe 127.0.0.1.

Chạy: python web/server.py [--port 8765]
"""
import argparse
import json
import mimetypes
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

WEB = Path(__file__).resolve().parent
ROOT = WEB.parent
sys.path.insert(0, str(WEB))

import scenarios  # noqa: E402  (đã thêm ROOT/codebase vào sys.path)

MAX_BODY = 64 * 1024


def git(*args):
    """Chạy lệnh git chỉ đọc, local. Lỗi thì trả None."""
    try:
        res = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True,
                             encoding="utf-8", timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return res.stdout.strip() if res.returncode == 0 else None


def api_info():
    commit = git("rev-parse", "--short=7", "HEAD")
    behind = git("rev-list", "--count", "HEAD..origin/main")
    status = git("status", "--porcelain")
    dirty = False
    for line in (status or "").splitlines():
        path = line[3:].strip().strip('"').replace("\\", "/")
        if " -> " in path:
            path = path.split(" -> ")[-1]
        if not (path.startswith("web/") or path.startswith(".taste-skill/")):
            dirty = True
            break
    return {
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "commit": commit[:7] if commit else None,
        "commit_subject": git("log", "-1", "--format=%s"),
        "behind_main": int(behind) if behind and behind.isdigit() else None,
        "dirty": dirty,
    }


def api_answer(payload):
    text = payload.get("text")
    if not isinstance(text, str):
        return {"input": text, "error": "ValueError: thiếu trường text kiểu chuỗi"}
    out = scenarios.run_agent(text)
    if out.startswith("CRASH: "):
        return {"input": text, "error": out[len("CRASH: "):]}
    return {"input": text, "output": out}


class Handler(BaseHTTPRequestHandler):
    server_version = "CP2Demo"

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))

    def send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        route = url.path
        if route == "/api/info":
            return self.send_json(api_info())
        if route == "/api/cases":
            groups, bugs = scenarios.run_all()
            return self.send_json({"ran_at": scenarios.now_iso(), "groups": groups, "bugs": bugs})
        if route == "/api/demo":
            which = parse_qs(url.query).get("which", [None])[0]
            return self.send_json({"ran_at": scenarios.now_iso(), "opening": scenarios.OPENING,
                                   "cases": scenarios.run_demo(which)})
        if route.startswith("/api/"):
            return self.send_json({"error": "Không có route này."}, 404)
        self.serve_static(route)

    def do_POST(self):
        if urlparse(self.path).path != "/api/answer":
            return self.send_json({"error": "Không có route này."}, 404)
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length > MAX_BODY:
                return self.send_json({"error": "Nội dung quá lớn."}, 413)
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            if not isinstance(payload, dict):
                raise ValueError("body phải là object")
        except (ValueError, UnicodeDecodeError) as exc:
            return self.send_json({"error": f"{type(exc).__name__}: {exc}"}, 400)
        self.send_json(api_answer(payload))

    def serve_static(self, route):
        rel = unquote(route).lstrip("/") or "index.html"
        target = (WEB / rel).resolve()
        if target.is_dir():
            target = target / "index.html"
        try:
            target.relative_to(WEB)
        except ValueError:
            return self.send_json({"error": "Không được phép."}, 403)
        if target.suffix == ".py" or not target.is_file() or "shots" in target.relative_to(WEB).parts[:1]:
            return self.send_json({"error": "Không tìm thấy."}, 404)
        ctype = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript", "application/json"):
            ctype += "; charset=utf-8"
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    mimetypes.add_type("text/javascript", ".js")
    mimetypes.add_type("text/javascript", ".mjs")
    httpd = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Mở http://127.0.0.1:{args.port}/ (Ctrl+C để tắt)", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
