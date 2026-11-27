"""Luồng chính của bản chạy thử — NHÓM VIẾT. Điền ở guide bước 3.2.

`python run.py`, `python run.py eval` và `python run.py simulate` đều gọi answer(text).

Hợp đồng:
    answer(text: str) -> dict có khoá "output" (str): kết quả đưa cho người dùng.
    Token, tên model, số lần gọi model / công cụ: khung tự đếm qua call_model và @tool — không cần trả.
    Bộ chạy gửi NGUYÊN ô input của câu thử vào text. Dữ liệu nền (bài học, thông báo, lịch…)
    do luồng của nhóm tự đọc qua công cụ trong tools.py.

Hình dạng: đúng như sơ đồ ở spec.md §4 (guide bước 2.2) — workflow cố định, một agent, hay nhiều agent.
Khung dưới đây là một workflow 2 bước VÍ DỤ, chỉ để luồng chạy hết từ trước CP2. Thay bằng luồng của nhóm.
Nếu viết vòng lặp agent (AI tự chọn bước tiếp): đặt giới hạn MAX_STEPS và ghi lý do dừng bằng note("dừng: …").
"""


import re
from datetime import datetime, time
from ai import call_model
from tools import check_availability
from tracing import note 

SYSTEM = ("Bạn là MiênAI - trợ lý hỗ trợ chủ cửa hàng kiểm tra lịch thuê áo dài. "
    "Chỉ sử dụng kết quả kiểm tra được cung cấp. "
    "Không tự chốt đơn, sửa dữ liệu hoặc tiết lộ thông tin khách." )    




def answer(text: str) -> dict:
    """Nhận câu hỏi mock và trả kết quả qua khóa output."""

    # CP2: dùng định dạng cố định; chưa hiểu câu hỏi tự nhiên.
    match = re.fullmatch(
        r"\s*([A-Za-z0-9]+)\s+"
        r"(\d{2}/\d{2}/\d{4})\s+"
        r"(\d{2}/\d{2}/\d{4})\s*",
        text,
    )

    if not match:
        return {
            "output": (
                "Bản mock chỉ nhận: MA_AO DD/MM/YYYY DD/MM/YYYY\n"
                "Ví dụ: AD02 28/11/2026 29/11/2026"
            )
        }

    ma_ao, ngay_nhan_text, ngay_tra_text = match.groups()
    ma_ao = ma_ao.upper()

    try:
        ngay_nhan = datetime.strptime(ngay_nhan_text, "%d/%m/%Y").date()
        ngay_tra = datetime.strptime(ngay_tra_text, "%d/%m/%Y").date()
    except ValueError:
        return {"output": "Ngày không hợp lệ. Hãy dùng định dạng DD/MM/YYYY."}

    nhan_luc = datetime.combine(ngay_nhan, time(9, 0))
    tra_luc = datetime.combine(ngay_tra, time(21, 0))

    result = check_availability(
        ma_ao,
        nhan_luc.isoformat(),
        tra_luc.isoformat(),
    )

    if result["trang_thai"] != "da_kiem_tra":
        return {
            "output": (
                "Cần chủ cửa hàng xác minh: "
                + result.get("ly_do", "Không đủ dữ liệu.")
            )
        }

    # Gọi model giả để kiểm tra luồng và trace của khung BTC.
    # Không dùng câu trả lời giả để quyết định số lượng.
    call_model(SYSTEM, "Đã kiểm tra dữ liệu giả lập.")

    lines = [
        f"Mã áo: {result['ma_ao']}",
        f"Nhận: {nhan_luc.strftime('%d/%m/%Y %H:%M')} (giả định)",
        f"Trả: {tra_luc.strftime('%d/%m/%Y %H:%M')} (giả định)",
        (
            "Sẵn sàng lại: "
            + datetime.fromisoformat(result["san_sang_lai"]).strftime(
                "%d/%m/%Y %H:%M"
            )
        ),
        "Kết quả theo size:",
    ]

    for size, item in result["sizes"].items():
        if item["trang_thai"] == "can_xac_minh":
            lines.append(f"- Size {size}: cần xác minh — {item['ly_do']}")
        elif item["trang_thai"] == "trung_lich":
            lines.append(f"- Size {size}: đã hết do trùng lịch.")
        else:
            lines.append(f"- Size {size}: còn {item['con_lai']} áo.")

    lines.append(
        "Dữ liệu giả lập; chủ cửa hàng kiểm tra trước khi xác nhận."
    )

    return {"output": "\n".join(lines)}
