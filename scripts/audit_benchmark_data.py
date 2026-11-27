"""Kiểm tra nguồn riêng cho các câu benchmark có khoảng thời gian rõ ràng.

Không chấm điểm và không in thông tin nhận diện khách. Chạy:
RENTAL_DATA_SOURCE=private PYTHONPATH=codebase python scripts/audit_benchmark_data.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "codebase"))
from tools import check_availability  # noqa: E402


CASES = {
    "B01": ("AD26", "2026-11-10T09:00", "2026-11-10T21:00"),
    "B02": ("AD09", "2026-11-03T14:00", "2026-11-04T18:00"),
    "B03": ("AD01", "2026-11-15T09:00", "2026-11-15T21:00"),
    "B04": ("AD99", "2026-11-05T09:00", "2026-11-06T21:00"),
    "B05": ("AD02", "2026-11-25T09:00", "2026-11-20T21:00"),
    "B06": ("AD26", "2026-11-20T10:00", "2026-11-20T16:00"),
    "B07": ("AD09", "2026-11-14T09:00", "2026-11-14T21:00"),
    "B14": ("AD01", "2026-11-24T09:00", "2026-11-24T21:00"),
    "B15": ("AD02", "2026-11-10T09:00", "2026-11-10T21:00"),
    "B16": ("AD02", "2026-11-28T09:00", "2026-11-28T22:00"),
    "B17": ("AD02", "2026-11-02T09:00", "2026-11-02T21:00"),
}


def main():
    if os.environ.get("RENTAL_DATA_SOURCE") != "private":
        raise SystemExit("Chỉ dùng khi đã chọn RENTAL_DATA_SOURCE=private.")
    for case_id, args in CASES.items():
        result = check_availability(*args)
        sizes = result.get("sizes", {})
        brief = {size: item.get("con_lai", item.get("trang_thai"))
                 for size, item in sizes.items()}
        print(case_id, result["trang_thai"], result.get("ly_do", ""), brief)


if __name__ == "__main__":
    main()
