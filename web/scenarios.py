"""Ca thử cho trang demo CP2. Mọi kết quả và đạt/trượt được tính lại từ code thật mỗi lần chạy.

Chạy độc lập: python web/scenarios.py   (in bảng trạng thái tất cả ca)
Không sửa file nào ngoài web/. Data tạm chỉ nằm trong bộ nhớ (gán tạm tools.get_mock_data).
"""
import csv
import json
import re
import sys
import threading
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "codebase") not in sys.path:
    sys.path.insert(0, str(ROOT / "codebase"))

import agent  # noqa: E402
import tools  # noqa: E402

RUN_LOCK = threading.RLock()  # monkeypatch là toàn cục: mọi lần chạy ca phải qua khoá này

MISSING = object()
INV = [{"ma_ao": "AD02", "sizes": {"S": 1, "L": 1, "XL": 2}}]
Q = "AD02 28/11/2026 29/11/2026"

STATUS_LABEL = {
    "dat": "Đạt",
    "mot_phan": "Đạt một phần",
    "truot": "Trượt",
    "chua_ho_tro": "Chưa hỗ trợ",
    "can_chot": "Cần Nam chốt",
}


# ---------- data tạm ----------

def rent(size, nhan, tra, trang_thai="Khách đặt trước", ma="AD02"):
    """Một đơn thuê tạm. Giá trị MISSING nghĩa là không có khoá đó."""
    item = {"ma_ao": ma, "size": size, "nhan_luc": nhan, "tra_luc": tra, "trang_thai": trang_thai}
    return {k: v for k, v in item.items() if v is not MISSING}


def describe_rentals(rentals):
    if rentals is None:
        return "data hiện tại (data/mock_rental.json)"
    if not rentals:
        return "data tạm: AD02 S1 L1 XL2, không có đơn"
    parts = []
    for r in rentals:
        def g(key):
            return repr(r[key]) if key in r else "(thiếu khoá)"
        parts.append(
            f"size={g('size')}, trạng thái={g('trang_thai')}, mã={g('ma_ao')}, "
            f"nhận={g('nhan_luc')}, trả={g('tra_luc')}"
        )
    return "data tạm: AD02 S1 L1 XL2 + đơn " + " | ".join(parts)


# ---------- chạy ----------

def _crash(exc):
    return f"CRASH: {type(exc).__name__}: {exc}"


def run_agent(text, rentals=None):
    """Gọi agent.answer; rentals=None dùng data thật, ngược lại gán tạm get_mock_data rồi khôi phục."""
    with RUN_LOCK:
        original = tools.get_mock_data
        try:
            if rentals is not None:
                data = {"inventory": INV, "rentals": rentals}
                tools.get_mock_data = lambda: data
            return agent.answer(text)["output"]
        except Exception as exc:  # ghi nguyên lỗi, không che
            return _crash(exc)
        finally:
            tools.get_mock_data = original


def run_tool(args, rentals):
    with RUN_LOCK:
        original = tools.get_mock_data
        try:
            data = {"inventory": INV, "rentals": rentals}
            tools.get_mock_data = lambda: data
            res = tools.check_availability(*args)
            keep = {k: v for k, v in res.items() if k in ("trang_thai", "ly_do", "sizes", "san_sang_lai")}
            return json.dumps(keep, ensure_ascii=False, separators=(",", ":"))
        except Exception as exc:
            return _crash(exc)
        finally:
            tools.get_mock_data = original


# ---------- đọc output ----------

def size_line(output, size):
    m = re.search(rf"^- Size {re.escape(size)}:(.*)$", output, re.M)
    return m.group(1).strip() if m else None


def con(output, size, n):
    line = size_line(output, size)
    return line is not None and re.search(rf"còn {n} áo", line) is not None


def trung(output, size):
    line = size_line(output, size)
    return line is not None and "đã hết do trùng lịch" in line


def has_con_line(output):
    return re.search(r"^- Size \S+: còn \d+ áo", output, re.M) is not None


def xm(output):
    return "xác minh" in output.lower()


def is_crash(output):
    return output.startswith("CRASH:")


def tool_size_state(actual, size):
    try:
        return json.loads(actual)["sizes"][size]["trang_thai"]
    except Exception:
        return None


# ---------- hàm chấm ----------
# Mỗi hàm trả (status, note).

def g_r1(o):
    ok = con(o, "S", 1) and con(o, "L", 1) and con(o, "XL", 1)
    return ("dat" if ok else "truot"), ""


def g_r2(o):
    return ("dat" if xm(o) and "AD99" in o else "truot"), ""


def g_r3a(o):
    return ("dat" if "Ngày không hợp lệ" in o else "truot"), ""


def g_r3b(o):
    if "không hợp lệ" in o:
        return "dat", ""
    if xm(o):
        return "mot_phan", "Đúng ý nhưng nhãn là 'cần chủ cửa hàng xác minh'."
    return "truot", ""


def g_r4(o):
    return ("dat" if xm(o) and not has_con_line(o) else "truot"), ""


def g_r4d(o):
    ok = con(o, "S", 1) and con(o, "L", 1) and con(o, "XL", 2)
    return ("dat" if ok else "truot"), ""


def g_tool_state(want):
    def grader(a):
        return ("dat" if tool_size_state(a, "S") == want else "truot"), ""
    return grader


def g_r5c(o):
    if o.startswith("Bản mock chỉ nhận"):
        return "chua_ho_tro", "Giao diện dòng lệnh chưa nhận giờ."
    return ("dat" if trung(o, "S") else "truot"), ""


def g_s_trung(o):
    return ("dat" if trung(o, "S") else "truot"), ""


def g_s_con1(o):
    return ("dat" if con(o, "S", 1) else "truot"), ""


def g_n1c(o):
    note = "Code hiện tính là đã trả và báo còn." if con(o, "S", 1) else ""
    return "can_chot", note


def g_n2_strict(o):
    if con(o, "S", 1):
        return "dat", ""
    return "truot", ("Báo cần xác minh thay vì bỏ qua đơn hủy." if xm(o) else "")


def g_xm(o):
    return ("dat" if xm(o) else "truot"), ""


def g_n3b(o):
    if is_crash(o):
        return "truot", "Chương trình lỗi, không trả lời được."
    return ("dat" if xm(o) else "truot"), ""


def g_n3g(o):
    if trung(o, "S") or xm(o):
        return "dat", ""
    return "truot", ("Báo S còn dù có đơn trùng." if con(o, "S", 1) else "")


def g_n3h(o):
    if con(o, "S", 1):
        return "dat", ""
    return "truot", ("Một đơn cũ làm cả mã áo bị chặn." if xm(o) else "")


def g_n3i(o):
    if xm(o):
        return "dat", ""
    if trung(o, "S"):
        return "mot_phan", "Kết luận đúng nhưng ngầm giả định 00:00."
    return "truot", ""


def g_x1(o):
    if o.startswith("Bản mock chỉ nhận"):
        return "truot", "Dấu BOM làm dòng nhập bị từ chối."
    return g_r1(o)


def g_x2(o):
    if o.startswith("Bản mock chỉ nhận"):
        return "chua_ho_tro", "Chưa hiểu câu hỏi tự nhiên."
    if is_crash(o):
        return "truot", ""
    return "dat", ""


def g_x5(o):
    line = size_line(o, "S") or ""
    if re.search(r"\d{1,2}[/:]\d{2}", line):
        return "dat", ""
    return "truot", "Dòng S không nêu đơn nào chiếm hay sẵn sàng lúc nào."


# ---------- ca file (X3, X4) ----------

def _bench_rows():
    with (ROOT / "eval" / "benchmark.csv").open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _natural_key(code):
    return int(code[2:])


def run_x3():
    try:
        data = json.loads((ROOT / "data" / "mock_rental.json").read_text(encoding="utf-8"))
        have = {i["ma_ao"] for i in data["inventory"]}
        used = set()
        for row in _bench_rows():
            # Câu cố ý dùng mã không tồn tại (vd B04 / AD99) không tính là thiếu data.
            if "ma_khong_ton_tai" in row.get("source", ""):
                continue
            used |= set(re.findall(r"AD\d+", row["input"]))
        missing = sorted(used - have, key=_natural_key)
        fmt = lambda s: ", ".join(sorted(s, key=_natural_key))
        return f"Data có: {fmt(have)}. Benchmark dùng: {fmt(used)}. Thiếu: {fmt(missing) or 'không'}"
    except Exception as exc:
        return _crash(exc)


def g_x3(o):
    if is_crash(o):
        return "truot", ""
    return ("dat" if o.endswith("Thiếu: không") else "truot"), ""


def run_x4():
    try:
        spec = (ROOT / "spec.md").read_text(encoding="utf-8")
        m = re.search(r"(\d+) thuong, (\d+) kho, (\d+) tu_choi", spec)
        counts = {}
        for row in _bench_rows():
            counts[row["type"]] = counts.get(row["type"], 0) + 1
        got = (counts.get("thuong", 0), counts.get("kho", 0), counts.get("tu_choi", 0))
        said = tuple(int(x) for x in m.groups()) if m else None
        said_txt = "{} thuong / {} kho / {} tu_choi".format(*said) if said else "(không tìm thấy)"
        return f"spec.md ghi: {said_txt}. Benchmark có: {got[0]} / {got[1]} / {got[2]}", said == got
    except Exception as exc:
        return _crash(exc), False


# ---------- danh sách ca ----------

def _agent_case(cid, nhom, title, text, expected, grader, rentals=None, shown_input=None):
    return dict(
        id=cid, nhom=nhom, title=title, via="agent",
        input=shown_input if shown_input is not None else text,
        data_note=describe_rentals(rentals), expected=expected, grader=grader,
        runner=lambda: run_agent(text, rentals),
    )


def _tool_case(cid, nhom, title, args, rentals, expected, grader):
    return dict(
        id=cid, nhom=nhom, title=title, via="tool",
        input=f'check_availability("{args[0]}", "{args[1]}", "{args[2]}")',
        data_note=describe_rentals(rentals), expected=expected, grader=grader,
        runner=lambda: run_tool(args, rentals),
    )


_prev = [rent("S", "2026-11-26T09:00:00", "2026-11-27T21:00:00", "Đã hoàn tất")]
_full = ("2026-11-28T09:00:00", "2026-11-29T21:00:00")
_bad_status = lambda st: [rent("S", *_full, st)]
_wash = [rent("S", "2026-11-26T09:00:00", "2026-11-27T21:00:00", "Đang giặt")]


def build_cases():
    c = []
    N1, N2, N3 = "Đang giặt", "HỦY không giữ áo", "Thiếu dữ liệu và sau 21:00"
    # Nhóm 1
    c.append(_agent_case("R1", "1. Ca thường", "Ca thường AD02", Q,
                         "S còn 1, L còn 1, XL còn 1", g_r1))
    c.append(_agent_case("R2", "2. Mã không tồn tại", "Mã không tồn tại",
                         "AD99 28/11/2026 29/11/2026", "Báo cần xác minh", g_r2))
    c.append(_agent_case("R3a", "3. Ngày sai", "Ngày không có thật",
                         "AD02 31/11/2026 01/12/2026", "Báo lỗi ngày", g_r3a))
    c.append(_agent_case("R3b", "3. Ngày sai", "Ngày nhận sau ngày trả",
                         "AD02 29/11/2026 28/11/2026", "Báo lỗi ngày, yêu cầu nhập lại", g_r3b))
    for cid, size, title in (("R4a", MISSING, "Đơn trùng, không có trường size"),
                             ("R4b", "", "Đơn trùng, size rỗng"),
                             ("R4c", "2XL", "Đơn trùng, size 2XL")):
        c.append(_agent_case(cid, "4. Đơn thiếu size", title, Q, "Không khẳng định còn áo", g_r4,
                             [rent(size, "2026-11-28T09:00:00", "2026-11-29T21:00:00")]))
    c.append(_agent_case("R4d", "4. Đơn thiếu size", "Đơn thiếu size nhưng không trùng", Q,
                         "Không ảnh hưởng: S 1, L 1, XL 2", g_r4d,
                         [rent("", "2026-10-01T09:00:00", "2026-10-02T21:00:00")]))
    c.append(_tool_case("R5a", "5. Ranh giới giờ", "Nhận 08:59 khi áo sẵn sàng 09:00",
                        ("AD02", "2026-11-28T08:59:00", "2026-11-28T21:00:00"), _prev,
                        "S chưa sẵn sàng", g_tool_state("trung_lich")))
    c.append(_tool_case("R5b", "5. Ranh giới giờ", "Nhận đúng 09:00",
                        ("AD02", "2026-11-28T09:00:00", "2026-11-28T21:00:00"), _prev,
                        "S còn", g_tool_state("con")))
    c.append(_agent_case("R5c", "5. Ranh giới giờ", "Nhập giờ 08:59 qua dòng lệnh",
                         "AD02 08:59 28/11/2026 28/11/2026", "Kiểm được theo giờ", g_r5c, _prev))
    c.append(_agent_case("R6a", "6. Đơn kế tiếp", "Đơn kế tiếp nhận 08:00 hôm sau", Q,
                         "S trùng (áo khách mới sẵn sàng 30/11 09:00)", g_s_trung,
                         [rent("S", "2026-11-30T08:00:00", "2026-11-30T21:00:00")]))
    c.append(_agent_case("R6b", "6. Đơn kế tiếp", "Đơn kế tiếp nhận đúng 09:00", Q,
                         "S còn 1", g_s_con1,
                         [rent("S", "2026-11-30T09:00:00", "2026-11-30T21:00:00")]))
    c.append(_tool_case("R6c", "6. Đơn kế tiếp", "Khách mới trả 18:00, đơn sau nhận 20:00 cùng ngày",
                        ("AD02", "2026-11-28T09:00:00", "2026-11-29T18:00:00"),
                        [rent("S", "2026-11-29T20:00:00", "2026-11-30T21:00:00")],
                        "S trùng", g_tool_state("trung_lich")))
    # Nhóm 2
    c.append(_agent_case("N1a", N1, "Đang giặt, hỏi ngày 28/11", Q,
                         "S còn 1 (sẵn sàng 28/11 09:00 dù trạng thái chưa đổi)", g_s_con1, _wash))
    c.append(_agent_case("N1b", N1, "Đang giặt, hỏi ngày 27/11", "AD02 27/11/2026 27/11/2026",
                         "S trùng", g_s_trung, _wash))
    c.append(_agent_case("N1c", N1, "Đang thuê quá hạn, chưa cập nhật", Q,
                         "Cần Nam chốt: có coi là đã trả không?", g_n1c,
                         [rent("S", "2026-11-24T09:00:00", "2026-11-25T21:00:00", "Đang thuê")]))
    for i, st in enumerate(["HỦY", "Hủy", "đã hủy", "Huỷ", "Đã huỷ", "HỦY ĐƠN"]):
        cid = "N2" + "abcdef"[i]
        c.append(_agent_case(cid, N2, f"Trạng thái '{st}'", Q, "S còn 1",
                             g_s_con1 if i < 3 else g_n2_strict, _bad_status(st)))
    c.append(_agent_case("N3a", N3, "Đơn trùng, thiếu khoá trạng thái", Q, "Cần xác minh", g_xm,
                         [rent("S", *_full, MISSING)]))
    c.append(_agent_case("N3b", N3, "Đơn trùng, trạng thái rỗng (None)", Q, "Cần xác minh", g_n3b,
                         [rent("S", *_full, None)]))
    c.append(_agent_case("N3c", N3, "Đơn Đang thuê, thiếu giờ trả", Q, "Cần xác minh", g_xm,
                         [rent("S", "2026-11-28T09:00:00", MISSING, "Đang thuê")]))
    c.append(_agent_case("N3d", N3, "Đơn cũ trả sau 21:00", Q, "Cần xác minh", g_xm,
                         [rent("S", "2026-11-27T09:00:00", "2026-11-27T22:00:00", "Đã hoàn tất")]))
    c.append(_tool_case("N3e", N3, "Khách mới hẹn trả 22:00",
                        ("AD02", "2026-11-28T09:00:00", "2026-11-29T22:00:00"), [],
                        "Cần xác minh",
                        lambda a: ("dat" if '"trang_thai":"can_xac_minh"' in a else "truot", "")))
    c.append(_agent_case("N3f", N3, "Đơn trùng, thiếu mã áo", Q, "Cảnh báo cần xác minh", g_xm,
                         [rent("S", *_full, "Đang thuê", ma=MISSING)]))
    c.append(_agent_case("N3g", N3, "Mã áo trong data viết thường 'ad02'", Q, "Không báo S còn", g_n3g,
                         [rent("S", *_full, ma="ad02")]))
    c.append(_agent_case("N3h", N3, "Dòng cũ năm 2025 trả sau 21:00, không liên quan", Q,
                         "Không ảnh hưởng (đơn không trùng)", g_n3h,
                         [rent("S", "2025-01-01T09:00:00", "2025-01-01T22:00:00", "Đã hoàn tất")]))
    c.append(_agent_case("N3i", N3, "Đơn chỉ có ngày, không có giờ", Q,
                         "Cần xác minh hoặc nêu rõ giả định giờ", g_n3i,
                         [rent("S", "2026-11-28", "2026-11-29")]))
    # Ca phụ
    c.append(_agent_case("X1", "Phụ", "Input có dấu BOM (dán từ PowerShell)", "﻿AD02 28/11/2026 29/11/2026",
                         "Như R1", g_x1, shown_input="[BOM]AD02 28/11/2026 29/11/2026"))
    try:
        b01 = next(r["input"] for r in _bench_rows() if r["id"] == "B01")
    except Exception as exc:
        b01 = f"(không đọc được B01: {exc})"
    c.append(_agent_case("X2", "Phụ", "Câu tự nhiên B01 của benchmark", b01, "Hiểu câu tự nhiên", g_x2))
    c.append(dict(id="X3", nhom="Phụ", title="Mã áo benchmark so với data", via="file",
                  input="data/mock_rental.json và cột input của eval/benchmark.csv",
                  data_note="đọc file", expected="Mọi mã benchmark có trong data",
                  grader=g_x3, runner=run_x3))
    c.append(dict(id="X4", nhom="Phụ", title="Số câu theo loại: spec.md và benchmark", via="file",
                  input="spec.md (mục 7) và cột type của eval/benchmark.csv",
                  data_note="đọc file", expected="Số trong spec khớp benchmark",
                  grader=None, runner=run_x4))
    c.append(_agent_case("X5", "Phụ", "Nêu căn cứ khi báo trùng lịch", Q,
                         "Nêu căn cứ: đơn nào chiếm, sẵn sàng lúc nào", g_x5,
                         [rent("S", "2026-11-30T08:00:00", "2026-11-30T21:00:00")]))
    return c


# ---------- danh sách lỗi ----------

BUGS = [
    ("N3b", "Cao", "Ô trạng thái trống là chuyện thường khi nối Sheet; cả mã áo không tra được."),
    ("N3g", "Cao", "Báo còn sai, dẫn tới cho thuê trùng một áo."),
    ("R5c", "Cao", "Ranh giới 08:59/09:00 và giờ trả 22:00 chỉ kiểm được ở công cụ; các câu benchmark có giờ sẽ trượt."),
    ("X2", "Cao", "Khoảng 17/20 câu benchmark là câu tự nhiên, sẽ chỉ nhận lại hướng dẫn cú pháp."),
    ("X3", "Cao", "Chạy eval sẽ báo không tìm thấy mã; DATA_CARD.md ghi 130 mã / 281 bản ghi, không khớp file."),
    ("X1", "Trung bình", "Chạy python run.py trong PowerShell với input dán/pipe bị từ chối dù gõ đúng cú pháp."),
    ("N3f", "Trung bình", "Đơn thiếu mã áo bị bỏ qua im lặng, trái quy tắc \"thiếu dữ liệu phải báo\"."),
    ("N2d", "Trung bình", "An toàn nhưng báo xác minh thừa; cần chuẩn hoá Unicode khi đọc Sheet."),
    ("N3h", "Trung bình", "Một dòng lỗi cũ chặn cả mã áo mãi mãi."),
    ("R3b", "Thấp", "Đúng ý nhưng sai nhãn: lỗi nhập liệu không cần chủ cửa hàng xác minh."),
    ("X5", "Thấp", "Chủ cửa hàng khó tư vấn khách ngày khác; benchmark B08, B09, B12 đòi căn cứ."),
    ("N3i", "Thấp", "Ra kết quả đúng nhưng giả định 00:00 ẩn."),
    ("X4", "Thấp", "Sửa số trong spec cho khớp, không đổi chuẩn đạt."),
]

OPENING = ("Bản này dùng data giả lập và model fake, chưa gọi model thật. "
           "Kết quả do code tính, không phải AI sinh. "
           "Chưa hiểu câu hỏi tự nhiên, chỉ nhận MÃ_ÁO DD/MM/YYYY DD/MM/YYYY. "
           "Chưa kết nối Google Sheet thật.")

DEMO = {
    "thuong": dict(
        id="D1", title="Ca thường", text="AD02 28/11/2026 29/11/2026", grader=g_r1,
        expected="S, L, XL mỗi size còn 1 áo",
        speech=("XL có 2 áo, 1 đơn Khách đặt trước đúng ngày nên còn 1. L có đơn HỦY nên vẫn còn 1. "
                "Chỉ có ngày nên mặc định nhận 09:00, trả 21:00 và hiện rõ giả định.")),
    "xac_minh": dict(
        id="D2", title="Ca cần xác minh", text="AD99 28/11/2026 29/11/2026", grader=g_r2,
        expected="Báo cần xác minh mã AD99",
        speech="Không đủ căn cứ thì hệ thống không đoán, trả quyền quyết định cho chủ cửa hàng."),
}


# ---------- chạy và đóng gói ----------

def run_case(case):
    actual = case["runner"]()
    if case["id"] == "X4":
        actual, ok = actual
        status, note = (("dat" if ok else "truot"), "")
        if is_crash(actual):
            status = "truot"
    else:
        status, note = case["grader"](actual)
    return {
        "id": case["id"], "nhom": case["nhom"], "title": case["title"],
        "input": case["input"], "data_note": case["data_note"], "via": case["via"],
        "expected": case["expected"], "actual": actual,
        "status": status, "status_label": STATUS_LABEL[status], "note": note,
    }


def run_all():
    """Chạy toàn bộ ca; trả (groups, bugs, results theo id)."""
    with RUN_LOCK:
        results = [run_case(c) for c in build_cases()]
    by_id = {r["id"]: r for r in results}
    groups = [
        {"id": "yeu_cau", "title": "Ca thử yêu cầu", "cases": [r for r in results if r["id"].startswith("R")]},
        {"id": "quy_tac", "title": "Quy tắc kiểm với Nam", "cases": [r for r in results if r["id"].startswith("N")]},
        {"id": "phu", "title": "Ca phụ cho danh sách lỗi", "cases": [r for r in results if r["id"].startswith("X")]},
    ]
    bugs = []
    for case_id, severity, impact in BUGS:
        r = by_id[case_id]
        # Kèm data tạm vào Input để Nam tái hiện được (nhiều lỗi cùng câu nhập, khác data).
        shown = r["input"]
        if r["data_note"].startswith("data tạm"):
            shown += "\n" + r["data_note"]
        bugs.append({
            "case_id": case_id, "input": shown, "expected": r["expected"], "actual": r["actual"],
            "severity": severity, "impact": impact, "case_status": r["status"],
            "status": "Đã hết lỗi" if r["status"] == "dat" else "Còn lỗi",
        })
    for i, b in enumerate(bugs, 1):
        b["n"] = i
    return groups, bugs


def run_demo(which=None):
    keys = [which] if which in DEMO else list(DEMO)
    out = []
    for k in keys:
        d = DEMO[k]
        actual = run_agent(d["text"])
        status, note = d["grader"](actual)
        out.append({
            "key": k, "id": d["id"], "title": d["title"], "input": d["text"],
            "data_note": describe_rentals(None), "via": "agent", "expected": d["expected"],
            "actual": actual, "status": status, "status_label": STATUS_LABEL[status],
            "note": note, "speech": d["speech"],
        })
    return out


def now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    groups, bugs = run_all()
    print(f"{'ID':<5}{'TRẠNG THÁI':<14}{'QUA':<7}KẾT QUẢ (dòng đầu)")
    for g in groups:
        for r in g["cases"]:
            first = r["actual"].splitlines()[0] if r["actual"] else ""
            print(f"{r['id']:<5}{r['status']:<14}{r['via']:<7}{first[:90]}")
    print()
    by = {}
    for g in groups:
        for r in g["cases"]:
            by.setdefault(r["status"], []).append(r["id"])
    for k in ("dat", "mot_phan", "chua_ho_tro", "can_chot", "truot"):
        print(f"{k}: {' '.join(by.get(k, []))}")


if __name__ == "__main__":
    main()
