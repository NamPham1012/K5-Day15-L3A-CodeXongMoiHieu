"""Chuyển danh mục và lịch Excel sang dữ liệu riêng, không trích tên khách.

Chạy: python scripts/import_rental_excel.py "duong-dan-danh-muc.xlsx" "duong-dan-lich.xlsx" [--replace]
Không ghi đè file đích trừ khi truyền --replace; không sửa Excel nguồn.
"""

import json
import os
import re
import sys
import tempfile
import zipfile
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "p": "http://schemas.openxmlformats.org/package/2006/relationships"}
ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "data" / "rental.private.json"
SIZE_RE = re.compile(r"(?<![A-Za-z0-9])(\d*)(XXXXL|XXXL|XXL|XL|L|M|S)(?![A-Za-z0-9])", re.I)


def read_sheet(path, title, allowed_columns):
    with zipfile.ZipFile(path) as z:
        workbook = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        targets = {r.attrib["Id"]: r.attrib["Target"] for r in rels}
        sheet = next((s for s in workbook.findall("m:sheets/m:sheet", NS)
                      if s.attrib.get("name") == title), None)
        if sheet is None:
            raise ValueError("Không tìm thấy tab: " + title)
        rel = sheet.attrib["{" + NS["r"] + "}id"]
        target = targets[rel].lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        strings = []
        if "xl/sharedStrings.xml" in z.namelist():
            shared = ET.fromstring(z.read("xl/sharedStrings.xml"))
            strings = ["".join(t.text or "" for t in si.findall(".//m:t", NS))
                       for si in shared.findall("m:si", NS)]
        xml = ET.fromstring(z.read(target))
        rows = []
        for row in xml.findall("m:sheetData/m:row", NS):
            cells = {}
            for cell in row.findall("m:c", NS):
                ref = cell.attrib.get("r", "")
                col = re.match(r"[A-Z]+", ref)
                if not col or col.group() not in allowed_columns:
                    continue
                val = cell.find("m:v", NS)
                if cell.attrib.get("t") == "inlineStr":
                    value = "".join(t.text or "" for t in cell.findall(".//m:t", NS))
                elif val is None or val.text is None:
                    value = ""
                elif cell.attrib.get("t") == "s":
                    value = strings[int(val.text)]
                elif cell.attrib.get("t") == "e":
                    value = ""
                else:
                    value = val.text
                cells[col.group()] = value
            rows.append(cells)
        return rows


def excel_datetime(value):
    if value in (None, ""):
        return ""
    try:
        result = datetime(1899, 12, 30) + timedelta(days=float(value))
        return result.replace(microsecond=0).isoformat()
    except (ValueError, OverflowError):
        return ""


def main():
    if len(sys.argv) not in {3, 4} or (len(sys.argv) == 4 and sys.argv[3] != "--replace"):
        raise SystemExit(__doc__)
    if TARGET.exists() and len(sys.argv) != 4:
        raise SystemExit("File đích đã tồn tại; không ghi đè: " + str(TARGET))
    catalog = read_sheet(Path(sys.argv[1]), "Áo dài", {"A", "C"})
    ledger = read_sheet(Path(sys.argv[2]), "Lịch thuê", {"B", "E", "I", "J", "L"})
    if not catalog or catalog[0].get("A", "").strip() != "Mã áo":
        raise SystemExit("Không nhận diện được cột mã áo danh mục.")
    if not ledger or ledger[0].get("B", "").strip() != "Mã áo":
        raise SystemExit("Không nhận diện được cấu trúc lịch thuê.")
    inventory, rentals, unassigned, warnings = [], [], [], Counter()
    seen = set()
    for row in catalog[1:]:
        code = str(row.get("A", "")).strip().upper()
        if not code:
            continue
        placeholder = re.fullmatch(r"M(\d+)", code)
        if placeholder and 56 <= int(placeholder.group(1)) <= 100 and not str(row.get("C", "")).strip():
            warnings["bo_qua_ma_du_phong_trong"] += 1
            continue
        if code in seen:
            raise SystemExit("Mã áo trùng trong danh mục, cần kiểm tra: " + code)
        seen.add(code)
        sizes = {}
        description = str(row.get("C", ""))
        # Hỗ trợ cách ghi màu liền size như "hồngM", không thay đổi Excel nguồn.
        description = re.sub(
            r"(?<=[a-zà-ỹ])(?=(?:XXXXL|XXXL|XXL|XL|L|M|S)(?:\s|[,;/]|$))",
            " ",
            description,
        )
        for count, size in SIZE_RE.findall(description):
            size = size.upper()
            sizes[size] = sizes.get(size, 0) + (int(count) if count else 1)
        if not sizes:
            warnings["danh_muc_khong_doc_duoc_size"] += 1
        inventory.append({"ma_ao": code, "sizes": sizes})
    for row in ledger[1:]:
        code = str(row.get("B", "")).strip().upper()
        if not code:
            # Không có mã áo nhưng có thông tin đơn: lưu riêng để không âm thầm
            # coi là áo còn. Không đọc tên, ghi chú hay thông tin liên hệ.
            if any(row.get(k, "") for k in ("E", "I", "J", "L")):
                unassigned.append({
                    "size": str(row.get("E", "")).strip().upper(),
                    "nhan_luc": excel_datetime(row.get("I")),
                    "tra_luc": excel_datetime(row.get("J")),
                    "trang_thai": str(row.get("L", "")).strip(),
                })
                warnings["lich_khong_co_ma"] += 1
            continue
        size = str(row.get("E", "")).strip().upper()
        begin, end = excel_datetime(row.get("I")), excel_datetime(row.get("J"))
        status = str(row.get("L", "")).strip()
        if not size:
            warnings["lich_thieu_size"] += 1
        if not begin or not end:
            warnings["lich_thieu_ngay_gio"] += 1
        if not status:
            warnings["lich_thieu_trang_thai"] += 1
        # Không đọc hoặc lưu cột A (tên khách), giá, tiền cọc hay ghi chú.
        rentals.append({"ma_ao": code, "size": size, "nhan_luc": begin,
                        "tra_luc": end, "trang_thai": status})
    payload = {"inventory": inventory, "rentals": rentals, "unassigned_rentals": unassigned}
    # Ghi file tạm cùng ổ rồi thay thế nguyên tử sau khi xử lý thành công.
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=TARGET.parent,
                                     prefix=".rental-update-", suffix=".tmp", delete=False) as out:
        temporary = Path(out.name)
        json.dump(payload, out, ensure_ascii=False, indent=2)
    try:
        os.replace(temporary, TARGET)
    finally:
        if temporary.exists():
            temporary.unlink()
    print("Đã tạo file dữ liệu riêng được Git ignore:", TARGET)
    print("Số mẫu:", len(inventory), "· Số dòng lịch:", len(rentals))
    print("Cảnh báo:", dict(warnings))
    print("Cần kiểm tra size không đọc được và lịch thiếu thông tin trước khi sử dụng.")


if __name__ == "__main__":
    main()
