"""Script đào data trên bản trích lịch thuê cục bộ (data/rental.private.json).

Mục đích: tái lập các con số x/N (%) và ví dụ ẩn danh trong evidence/data-mining.md.
Không đọc hoặc in thông tin định danh khách hàng (file bản trích đã loại bỏ PII).

Cách chạy:
    python evidence/count.py
"""

from collections import defaultdict
from datetime import datetime, time, timedelta
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "rental.private.json"

VALID_STATUSES = {
    "khách đặt trước",
    "đang thuê",
    "đã hoàn tất",
    "đang giặt",
    "hủy",
    "đã hủy",
}


def pct(x: int, n: int) -> str:
    return f"{x}/{n} ({(x / n * 100):.1f}%)" if n else "0/0 (0.0%)"


def parse_dt(value: str):
    if not value or not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def main() -> None:
    if not DATA_PATH.exists():
        raise SystemExit(
            f"Không tìm thấy {DATA_PATH}. File dữ liệu riêng không commit lên repo công khai."
        )

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    inventory = {item["ma_ao"]: item.get("sizes", {}) for item in data.get("inventory", [])}
    rentals = data.get("rentals", [])

    n_inv = len(inventory)
    n_rentals = len(rentals)

    missing_or_unknown_size = []
    size_not_in_inventory = []
    missing_time = []
    reversed_time = []
    late_return = []
    bad_status = []
    any_issue_non_cancelled = []

    cancelled_count = 0
    valid_active_by_item_size = defaultdict(list)
    by_ma_ao = defaultdict(list)

    for idx, r in enumerate(rentals, start=1):
        ma = r.get("ma_ao", "")
        size = (r.get("size") or "").strip()
        status_raw = (r.get("trang_thai") or "").strip()
        status = status_raw.casefold()
        start = parse_dt(r.get("nhan_luc"))
        end = parse_dt(r.get("tra_luc"))

        by_ma_ao[ma].append(idx)

        if status in {"hủy", "đã hủy"}:
            cancelled_count += 1
            continue

        issues = []

        if not size or size == "KHONG_RO":
            missing_or_unknown_size.append((idx, r))
            issues.append("thiếu/không rõ size")
        elif ma in inventory and size not in inventory[ma]:
            size_not_in_inventory.append((idx, r))
            issues.append(f"size '{size}' không khớp danh mục {list(inventory[ma].keys())}")

        if start is None or end is None:
            missing_time.append((idx, r))
            issues.append("thiếu ngày giờ nhận/trả")
        else:
            if end <= start:
                reversed_time.append((idx, r))
                issues.append("ngày/giờ trả <= nhận")
            if end.time() > time(21, 0):
                late_return.append((idx, r))
                issues.append(f"trả sau 21:00 ({end.strftime('%H:%M')})")

        if status not in VALID_STATUSES:
            bad_status.append((idx, r))
            issues.append(f"trạng thái trống/lạ ('{status_raw}')")

        if issues:
            any_issue_non_cancelled.append((idx, r, issues))

        if (
            start is not None
            and end is not None
            and end > start
            and size
            and size != "KHONG_RO"
            and ma in inventory
            and size in inventory[ma]
        ):
            ready = datetime.combine(end.date() + timedelta(days=1), time(9, 0))
            valid_active_by_item_size[(ma, size)].append((idx, start, end, ready, status_raw))

    n_active = n_rentals - cancelled_count

    # Đếm cặp đơn cùng mã + cùng size bị trùng (có xét giặt đến 09:00 hôm sau) hoặc sát nút (<= 24h sau ready)
    over_capacity_events = []
    tight_turnaround_pairs = []

    for (ma, size), rows in sorted(valid_active_by_item_size.items()):
        stock = inventory[ma][size]
        rows.sort(key=lambda x: x[1])

        # Sweep-line tìm thời điểm vượt tồn kho (trùng lịch thực tế trong sổ)
        events = []
        for idx, start, end, ready, status_raw in rows:
            events.append((start, 1, idx))
            events.append((ready, -1, idx))
        events.sort(key=lambda e: (e[0], e[1]))
        cur = 0
        max_cur = 0
        peak_time = None
        for t, delta, _ in events:
            cur += delta
            if cur > max_cur:
                max_cur = cur
                peak_time = t
        if max_cur > stock:
            over_capacity_events.append((ma, size, stock, max_cur, peak_time, len(rows)))

        # Đếm cặp đơn liên tiếp có khoảng nghỉ giữa ready đơn trước và start đơn sau <= 24h (kể cả trùng)
        for i in range(len(rows) - 1):
            r1 = rows[i]
            r2 = rows[i + 1]
            gap_hours = (r2[1] - r1[3]).total_seconds() / 3600.0
            if gap_hours <= 24.0:
                tight_turnaround_pairs.append((ma, size, stock, r1, r2, gap_hours))

    # Mã áo có nhiều đơn (>= 5 đơn)
    busy_models = sorted(
        [(ma, len(idxs)) for ma, idxs in by_ma_ao.items() if len(idxs) >= 5],
        key=lambda x: (-x[1], x[0]),
    )
    multi_size_models = sum(1 for sizes in inventory.values() if len(sizes) >= 2)
    multi_qty_models = sum(
        1 for sizes in inventory.values() if any(qty >= 2 for qty in sizes.values())
    )

    print("=== TỔNG QUAN TẬP DỮ LIỆU (data/rental.private.json) ===")
    print(f"- Số mã danh mục áo dài (inventory): {n_inv}")
    print(f"  + Mã có >= 2 size: {pct(multi_size_models, n_inv)}")
    print(f"  + Mã có ít nhất 1 size số lượng >= 2 áo: {pct(multi_qty_models, n_inv)}")
    print(f"- Tổng số dòng lịch áo dài (rentals): {n_rentals}")
    print(f"  + Đơn HỦY / Đã hủy: {pct(cancelled_count, n_rentals)}")
    print(f"  + Đơn hiệu lực (không hủy, mẫu số N_active): {n_active}")
    print()

    print("=== CHẤT LƯỢNG DỮ LIỆU & BẤT THƯỜNG (trên N_active =", n_active, ") ===")
    print(f"- Thiếu hoặc không rõ size (trống / KHONG_RO): {pct(len(missing_or_unknown_size), n_active)}")
    print(f"- Size ghi trong lịch không khớp danh mục: {pct(len(size_not_in_inventory), n_active)}")
    print(f"- Thiếu ngày/giờ nhận hoặc trả: {pct(len(missing_time), n_active)}")
    print(f"- Ngày/giờ trả <= ngày/giờ nhận: {pct(len(reversed_time), n_active)}")
    print(f"- Giờ trả sau 21:00: {pct(len(late_return), n_active)}")
    print(f"- Thiếu hoặc trạng thái ngoài 5 chuẩn: {pct(len(bad_status), n_active)}")
    print(f"- Tổng dòng hiệu lực có >= 1 bất thường: {pct(len(any_issue_non_cancelled), n_active)}")
    print()

    print("=== ÁP LỰC DÒ LỊCH & TRÙNG LỊCH THỰC TẾ ===")
    print(f"- Số mã áo có >= 5 dòng lịch: {pct(len(busy_models), n_inv)} (top 5: {busy_models[:5]})")
    print(f"- Số nhóm (mã áo, size) có lịch vượt tồn kho (tính cả giặt đến 09:00 hôm sau): {len(over_capacity_events)}")
    for ma, size, stock, max_cur, peak_time, total_rows in over_capacity_events[:10]:
        print(f"  * {ma} size {size}: tồn {stock}, đỉnh giữ {max_cur} lúc {peak_time.strftime('%d/%m/%Y %H:%M')} (tổng {total_rows} đơn)")
    print(f"- Số cặp đơn liên tiếp cùng (mã, size) cách nhau <= 24h sau mốc giặt 09:00 (gồm cả trùng): {len(tight_turnaround_pairs)}")
    print()

    print("=== MẪU VÍ DỤ ẨN DANH (KHÔNG PII) ===")
    shown = 0
    for label, bucket in [
        ("Ngày trả <= nhận", reversed_time),
        ("Thiếu ngày/giờ", missing_time),
        ("Thiếu/không rõ size", missing_or_unknown_size),
        ("Size lệch danh mục", size_not_in_inventory),
        ("Trả sau 21:00", late_return),
    ]:
        for idx, r in bucket[:2]:
            print(
                f"  - [{label}] Bản ghi R#{idx:03d} | {r.get('ma_ao')} | size={r.get('size')!r} | "
                f"{r.get('nhan_luc')} -> {r.get('tra_luc')} | tt={r.get('trang_thai')!r}"
            )
            shown += 1


if __name__ == "__main__":
    main()
