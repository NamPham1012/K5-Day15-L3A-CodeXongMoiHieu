"""Công cụ của bài toán — NHÓM VIẾT. Điền ở guide bước 2.2 (thiết kế) và 3.2 (code).

Mỗi công cụ là một hàm Python có @tool. Docstring ghi đúng 4 ý như sơ đồ ở spec.md §4:
    tên · input · output · có tác động ra ngoài không (gửi tin, sửa dữ liệu, chấm điểm…)
Khung tự ghi mỗi lần gọi công cụ vào trace (tên, input, output rút gọn, thời gian, lỗi).

Số công cụ, kiểu công cụ do thiết kế của nhóm quyết định — có bài chỉ cần một công cụ tra cứu.
Công cụ có tác động ra ngoài: KHÔNG tự làm. Trả về bản nháp chờ người duyệt (guide bước 2.2, "chỗ người duyệt").
Dữ liệu công cụ đọc (bài mẫu, thông báo mẫu, lịch…): để trong data/ và mô tả ở data/DATA_CARD.md.
"""

import json
import os

from pathlib import Path
from datetime import datetime, time, timedelta
from tracing import tool, TOOLS  # noqa: F401  (TOOLS: danh sách công cụ đã đăng ký, dùng khi viết vòng lặp agent)


@tool
def search_example(query: str) -> list:
    """(ví dụ — thay bằng công cụ của nhóm) Tra dữ liệu mẫu theo câu hỏi.
    Input: câu hỏi (str). Output: danh sách đoạn {"code", "text"}. Không tác động ra ngoài."""
    return [{"code": "VD-1", "text": "(ví dụ) đoạn dữ liệu giả — thay bằng dữ liệu thật của bài toán"}]


@tool
def get_mock_data() -> dict:
    """Đọc danh mục và lịch theo nguồn được chọn.

    Input: không có.
    Output: dict gồm inventory và rentals; mặc định là dữ liệu giả lập.
    Tác động ra ngoài: không; chỉ đọc file cục bộ.
    """
    root = Path(__file__).resolve().parent.parent
    source = os.environ.get("RENTAL_DATA_SOURCE", "mock").strip().lower()
    if source not in {"mock", "private"}:
        raise ValueError("RENTAL_DATA_SOURCE phải là mock hoặc private")
    data_path = root / "data" / (
        "rental.private.json" if source == "private" else "mock_rental.json"
    )

    with data_path.open("r", encoding="utf-8") as file:
        return json.load(file)


@tool
def check_availability(ma_ao: str, nhan_luc: str, tra_luc: str) -> dict:
    """Kiểm tra số áo còn theo từng size từ nguồn dữ liệu được chọn.

    Input: mã áo, thời gian nhận và trả dạng ISO YYYY-MM-DDTHH:MM:SS.
    Output: kết quả từng size hoặc thông báo cần xác minh.
    Tác động ra ngoài: không; chỉ đọc dữ liệu giả lập.
    """
    try:
        start = datetime.fromisoformat(nhan_luc)
        returned = datetime.fromisoformat(tra_luc)
    except (TypeError, ValueError):
        return {"trang_thai": "can_xac_minh", "ly_do": "Ngày giờ không hợp lệ."}

    if start.tzinfo is not None or returned.tzinfo is not None:
        return {"trang_thai": "can_xac_minh", "ly_do": "Bản mock dùng giờ Việt Nam không kèm múi giờ."}

    if returned <= start:
        return {"trang_thai": "can_xac_minh", "ly_do": "Giờ trả phải sau giờ nhận."}

    if returned.time() > time(21, 0):
        return {"trang_thai": "can_xac_minh", "ly_do": "Khách phải trả không muộn hơn 21:00."}

    source = os.environ.get("RENTAL_DATA_SOURCE", "mock").strip().lower()
    if source == "private" and start.date() < datetime(2026, 11, 1).date():
        return {
            "trang_thai": "can_xac_minh",
            "ly_do": "Dữ liệu cửa hàng chỉ được xác nhận từ 01/11/2026; không thể kết luận cho ngày trước đó.",
        }

    # Áo chỉ sẵn sàng trở lại lúc 09:00 ngày sau ngày trả.
    ready = datetime.combine(returned.date() + timedelta(days=1), time(9, 0))

    data = get_mock_data()

    if source == "private":
        if "unassigned_rentals" not in data:
            return {"trang_thai": "can_xac_minh", "ly_do": "Dữ liệu riêng chưa được kiểm tra các dòng thiếu mã áo."}
        for item in data["unassigned_rentals"]:
            status = item.get("trang_thai", "").strip().casefold()
            if status in {"hủy", "đã hủy"}:
                continue
            # Thiếu mã: không thể biết đơn thuộc áo nào. Chỉ bỏ qua khi
            # cả hai mốc thời gian đủ rõ và chắc chắn không ảnh hưởng kỳ hỏi.
            try:
                unknown_start = datetime.fromisoformat(item["nhan_luc"])
                unknown_return = datetime.fromisoformat(item["tra_luc"])
            except (KeyError, TypeError, ValueError):
                return {"trang_thai": "can_xac_minh", "ly_do": "Có dòng lịch thiếu mã áo và ngày giờ; cần kiểm tra với chủ cửa hàng."}
            if unknown_start.tzinfo is not None or unknown_return.tzinfo is not None or unknown_return <= unknown_start:
                return {"trang_thai": "can_xac_minh", "ly_do": "Có dòng lịch thiếu mã áo với thời gian bất thường; cần kiểm tra."}
            if unknown_start < datetime(2026, 10, 31) and unknown_return < datetime(2026, 10, 31):
                continue
            if unknown_return.time() > time(21, 0):
                return {"trang_thai": "can_xac_minh", "ly_do": "Có dòng lịch thiếu mã áo và trả sau 21:00; cần kiểm tra."}
            unknown_ready = datetime.combine(unknown_return.date() + timedelta(days=1), time(9, 0))
            if start < unknown_ready and unknown_start < ready:
                return {"trang_thai": "can_xac_minh", "ly_do": "Có lịch trùng thời gian nhưng thiếu mã áo; cần kiểm tra."}

    inventory = next(
        (item for item in data["inventory"] if item["ma_ao"] == ma_ao),
        None,
    )

    if inventory is None:
        return {"trang_thai": "can_xac_minh", "ly_do": f"Không tìm thấy mã áo {ma_ao}."}

    if not inventory.get("sizes"):
        return {"trang_thai": "can_xac_minh", "ly_do": "Chưa đọc được size trong danh mục; cần xác minh."}

    # Lưu các khoảng thời gian đã được giữ cho từng size.
    intervals = {size: [] for size in inventory["sizes"]}

    for rental in data["rentals"]:
        if rental.get("ma_ao") != ma_ao:
            continue

        status = rental.get("trang_thai", "").strip()

        if status.casefold() in {"hủy", "đã hủy"}:
            continue

        try:
            old_start = datetime.fromisoformat(rental["nhan_luc"])
            old_return = datetime.fromisoformat(rental["tra_luc"])
        except (KeyError, TypeError, ValueError):
            return {
                "trang_thai": "can_xac_minh",
                "ly_do": "Có đơn liên quan thiếu ngày giờ hợp lệ.",
            }

        if old_start.tzinfo is None and old_return.tzinfo is None and source == "private":
            # Dữ liệu cũ trước 31/10 không ảnh hưởng kỳ dữ liệu từ 01/11.
            # Giữ 31/10 vì thời gian giặt có thể kéo sang 01/11.
            cutoff_buffer = datetime(2026, 10, 31)
            if old_start < cutoff_buffer and old_return < cutoff_buffer:
                continue

        if (
            old_start.tzinfo is not None
            or old_return.tzinfo is not None
            or old_return <= old_start
            or old_return.time() > time(21, 0)
        ):
            return {
                "trang_thai": "can_xac_minh",
                "ly_do": "Có đơn liên quan có thời gian bất thường.",
            }

        old_ready = datetime.combine(
            old_return.date() + timedelta(days=1),
            time(9, 0),
        )

        # Hai khoảng tiếp giáp đúng thời điểm không bị coi là trùng.
        if not (start < old_ready and old_start < ready):
            continue

        if status.casefold() not in {
            "khách đặt trước",
            "đang thuê",
            "đã hoàn tất",
            "đang giặt",
        }:
            return {
                "trang_thai": "can_xac_minh",
                "ly_do": "Có đơn trùng lịch có trạng thái chưa rõ.",
            }

        size = rental.get("size")
        if size not in intervals:
            return {
                "trang_thai": "can_xac_minh",
                "ly_do": "Có đơn trùng lịch nhưng thiếu hoặc sai size.",
            }

        intervals[size].append((old_start, old_ready))

    results = {}

    for size, total in inventory["sizes"].items():
        events = []

        for old_start, old_ready in intervals[size]:
            # Chỉ tính phần giao với khoảng khách mới giữ áo.
            events.append((max(start, old_start), 1))
            events.append((min(ready, old_ready), -1))

        # Khi cùng thời điểm: giải phóng (-1) trước khi giữ (+1).
        events.sort(key=lambda event: (event[0], event[1]))

        current = 0
        maximum = 0

        for _, change in events:
            current += change
            maximum = max(maximum, current)

        if maximum > total:
            results[size] = {
                "trang_thai": "can_xac_minh",
                "ly_do": "Số đơn trùng vượt số áo trong danh mục.",
            }
            continue

        available = total - maximum
        results[size] = {
            "tong_so": total,
            "con_lai": available,
            "trang_thai": "con" if available > 0 else "trung_lich",
        }

    return {
        "trang_thai": "da_kiem_tra",
        "ma_ao": ma_ao,
        "nhan_luc": start.isoformat(timespec="minutes"),
        "tra_luc": returned.isoformat(timespec="minutes"),
        "san_sang_lai": ready.isoformat(timespec="minutes"),
        "sizes": results,
        "luu_y": (
            "Dữ liệu lịch riêng; chủ cửa hàng kiểm tra trước khi xác nhận."
            if os.environ.get("RENTAL_DATA_SOURCE", "mock").strip().lower() == "private"
            else "Dữ liệu giả lập; chủ cửa hàng kiểm tra trước khi xác nhận."
        ),
    }
