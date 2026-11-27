"""Kiểm tra quy tắc thời gian bằng dữ liệu giả lập, không cần Sheet thật."""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "codebase"))
import tools  # noqa: E402


class AvailabilityRulesTest(unittest.TestCase):
    def setUp(self):
        self.data = {"inventory": [{"ma_ao": "AD02", "sizes": {"M": 1}}], "rentals": [], "unassigned_rentals": []}
        self.env = patch.dict(os.environ, {"RENTAL_DATA_SOURCE": "private"})
        self.env.start()
        self.source = patch.object(tools, "get_mock_data", side_effect=lambda: self.data)
        self.source.start()
        self.addCleanup(self.env.stop)
        self.addCleanup(self.source.stop)

    def check(self, start, end):
        return tools.check_availability("AD02", start, end)

    def test_khong_ket_luan_truoc_moc_nguon(self):
        result = self.check("2026-10-30T09:00:00", "2026-10-30T21:00:00")
        self.assertEqual(result["trang_thai"], "can_xac_minh")

    def test_lich_cu_thang_10_khong_chan_thang_11(self):
        self.data["rentals"] = [{"ma_ao": "AD02", "size": "M", "nhan_luc": "2026-10-20T09:00:00", "tra_luc": "2026-10-21T22:00:00", "trang_thai": "Đã hoàn tất"}]
        result = self.check("2026-11-01T09:00:00", "2026-11-01T21:00:00")
        self.assertEqual(result["sizes"]["M"]["con_lai"], 1)

    def test_giat_31_10_den_9h_1_11(self):
        self.data["rentals"] = [{"ma_ao": "AD02", "size": "M", "nhan_luc": "2026-10-30T09:00:00", "tra_luc": "2026-10-31T21:00:00", "trang_thai": "Đã hoàn tất"}]
        before = self.check("2026-11-01T08:59:00", "2026-11-01T21:00:00")
        at_nine = self.check("2026-11-01T09:00:00", "2026-11-01T21:00:00")
        self.assertEqual(before["sizes"]["M"]["con_lai"], 0)
        self.assertEqual(at_nine["sizes"]["M"]["con_lai"], 1)

    def test_don_trung_thieu_size_khong_doan(self):
        self.data["rentals"] = [{"ma_ao": "AD02", "size": "", "nhan_luc": "2026-11-10T09:00:00", "tra_luc": "2026-11-10T21:00:00", "trang_thai": "Khách đặt trước"}]
        result = self.check("2026-11-10T09:00:00", "2026-11-10T21:00:00")
        self.assertEqual(result["trang_thai"], "can_xac_minh")

    def test_trang_thai_thieu_ngoai_khoang_khong_chan(self):
        self.data["rentals"] = [{"ma_ao": "AD02", "size": "M", "nhan_luc": "2026-11-05T09:00:00", "tra_luc": "2026-11-05T21:00:00", "trang_thai": ""}]
        result = self.check("2026-11-10T09:00:00", "2026-11-10T21:00:00")
        self.assertEqual(result["sizes"]["M"]["con_lai"], 1)

    def test_lich_thieu_ma_va_ngay_phai_canh_bao(self):
        self.data["unassigned_rentals"] = [{"size": "M", "nhan_luc": "", "tra_luc": "", "trang_thai": "Đã hoàn tất"}]
        result = self.check("2026-11-10T09:00:00", "2026-11-10T21:00:00")
        self.assertEqual(result["trang_thai"], "can_xac_minh")

    def test_lich_thieu_ma_cu_hon_pham_vi_khong_chan(self):
        self.data["unassigned_rentals"] = [{"size": "M", "nhan_luc": "2026-10-26T09:00:00", "tra_luc": "2026-10-28T21:00:00", "trang_thai": "Đã hoàn tất"}]
        result = self.check("2026-11-10T09:00:00", "2026-11-10T21:00:00")
        self.assertEqual(result["sizes"]["M"]["con_lai"], 1)


if __name__ == "__main__":
    unittest.main()
