"""Nối model — chỗ DUY NHẤT trong bản chạy thử gọi model AI. NHÓM VIẾT phần gọi model thật.

Hợp đồng (giữ nguyên để khung đo được token):
    call_model(system: str, user: str) -> dict với 4 khoá
        "text":       str   chữ model trả về
        "model":      str   tên model đã gọi (để tra giá ở bảng giá model)
        "tokens_in":  int   số token vào, lấy từ trường usage trong phản hồi API — KHÔNG ước lượng
        "tokens_out": int   số token ra, gồm cả token suy luận / suy nghĩ nếu API tính riêng
    @model_call (từ tracing.py) tự ghi mỗi lần gọi vào trace; agent.py gọi call_model bao nhiêu lần
    cũng được, khung tự cộng token.
    Lỗi gọi model (hết lượt, sai key, mất mạng): cứ để exception bay ra — khung ghi lỗi vào cột error.
"""
import json
import os
import urllib.error
import urllib.request

from tracing import model_call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOW_RAW = False
URL_OPENAI = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions").strip()


def load_env(path=os.path.join(ROOT, ".env")):
    """Đọc file .env (KEY=VALUE mỗi dòng) vào biến môi trường, không ghi đè biến đã có. Khung — không cần sửa."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()
MODEL_PROVIDER = (os.environ.get("MODEL_PROVIDER") or "fake").strip().lower()
MODEL_NAME = (os.environ.get("MODEL_NAME") or "").strip()
API_KEY = (os.environ.get("API_KEY") or "").strip()
URL_OPENAI = (os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1/chat/completions").strip()


def post_json(url: str, headers: dict, body: dict, timeout: int = 60) -> dict:
    """Gửi POST JSON, trả về JSON phản hồi. Chỉ dùng thư viện chuẩn (urllib)."""
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers=dict({"Content-Type": "application/json"}, **headers),
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "replace")[:400]
        raise RuntimeError(f"HTTP {err.code}: {detail}") from err
    if SHOW_RAW:
        print(json.dumps(data, ensure_ascii=False, indent=2)[:3000])
    return data


URL_OPENAI_DEFAULT = "https://api.openai.com/v1/chat/completions"
URL_OPENROUTER = "https://openrouter.ai/api/v1/chat/completions"


def call_openai(system: str, user: str) -> dict:
    """Gọi Chat Completions API của OpenAI hoặc OpenRouter (tương thích OpenAI)."""
    if not MODEL_NAME or not API_KEY:
        raise RuntimeError("Thiếu MODEL_NAME hoặc API_KEY trong .env.")

    is_openrouter = MODEL_PROVIDER == "openrouter" or API_KEY.startswith("sk-or-")
    url = os.environ.get("OPENAI_BASE_URL", "").strip() or (
        URL_OPENROUTER if is_openrouter else URL_OPENAI_DEFAULT
    )
    request_model = MODEL_NAME
    if is_openrouter and "/" not in request_model and MODEL_PROVIDER == "openai":
        request_model = f"openai/{request_model}"

    messages = ([{"role": "system", "content": system}] if system else []) + [
        {"role": "user", "content": user}
    ]
    data = post_json(
        url,
        {"Authorization": "Bearer " + API_KEY},
        {"model": request_model, "messages": messages},
    )
    usage = data["usage"]
    return {
        "text": data["choices"][0]["message"]["content"] or "",
        "tokens_in": int(usage["prompt_tokens"]),
        "tokens_out": int(usage["completion_tokens"]),
    }


@model_call
def call_model(system: str, user: str) -> dict:
    if MODEL_PROVIDER == "fake":
        last = (user.strip().splitlines() or [""])[-1]
        return {
            "text": "[câu trả lời giả — chưa nối model] " + last[:60],
            "model": "fake",
            "tokens_in": 0,
            "tokens_out": 0,
        }

    if MODEL_PROVIDER in {"openai", "openrouter"}:
        result = call_openai(system, user)
        return {
            "text": result["text"],
            "model": MODEL_NAME,
            "tokens_in": result["tokens_in"],
            "tokens_out": result["tokens_out"],
        }

    raise NotImplementedError(
        "chưa viết phần gọi model thật cho MODEL_PROVIDER=%s trong codebase/ai.py — xem docs/connect-model.md"
        % MODEL_PROVIDER
    )
