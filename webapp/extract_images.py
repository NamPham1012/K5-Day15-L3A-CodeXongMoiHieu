"""Tách vài ảnh áo (không có mặt người, không watermark) từ file mẫu của cửa hàng để trang trí.

Chạy: python webapp/extract_images.py
Ảnh ra webapp/static/img/ (đã .gitignore: ảnh của cửa hàng, chỉ dùng cục bộ, không commit).
"""
import io
import zipfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / "data" / "MIÊN - MẪU - GIÁ THUÊ ÁO DÀI.xlsx"
OUT = Path(__file__).resolve().parent / "static" / "img"
# Chỉ các ảnh chụp riêng áo, đã xem tay: không có mặt người, không logo shop khác.
PICKED = [33, 45, 62, 73, 76, 81]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(XLSX) as book:
        for i, number in enumerate(PICKED, start=1):
            data = book.read(f"xl/media/image{number}.jpg")
            image = Image.open(io.BytesIO(data)).convert("RGB")
            image.thumbnail((640, 860))
            image.save(OUT / f"ao-{i}.jpg", quality=80, optimize=True, progressive=True)
            print(f"ao-{i}.jpg  <- image{number}.jpg  {image.size}")


if __name__ == "__main__":
    main()
