"""Test danh mục giọng: mọi giọng VieNeu và sắc giọng edge-tts dùng được trong `giong:`, lùi về edge-tts cùng giới
khi máy không có VieNeu, cao độ đi kèm tới edge-tts. Không bao giờ gọi giọng thật."""

import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))

from video_ma_parts import giong, parse, thoi_luong  # noqa: E402
from video_ma_parts.giong_ds import VIENEU  # noqa: E402

KICH_BAN = """---
tieu-de: Thử giọng
mon: Hoá học
lop: 10
giong: {giong}
---

## Cảnh 1
loai: tieu-de
chu: Thử giọng
loi: Xin chào các bạn.
"""


class DanhMucTest(unittest.TestCase):
    def test_moi_giong_vieneu_qua_parse(self):
        for khoa in list(VIENEU) + ["nu", "nam", "nu-tuoi", "nam-tram"]:
            video = parse.parse(KICH_BAN.format(giong=khoa))
            self.assertEqual(video.meta["giong"], khoa)

    def test_giong_la_bi_tu_choi(self):
        with self.assertRaises(parse.ParseError):
            parse.parse(KICH_BAN.format(giong="giong-la"))

    def test_danh_muc_du_truong(self):
        self.assertGreaterEqual(len(VIENEU), 20)
        for khoa, (ten, gioi, vung, chat) in VIENEU.items():
            self.assertIn(gioi, ("nu", "nam"), khoa)
            self.assertIn(vung, ("Bắc", "Trung", "Nam"), khoa)
            self.assertTrue(ten and chat, khoa)
        self.assertEqual(giong.VIENEU_GIONG["thu-giang"], "Thu Giang")

    def test_du_phong_cung_gioi(self):
        for khoa, (_ten, gioi, _vung, _chat) in VIENEU.items():
            thay = giong.giong_du_phong(khoa)
            self.assertIn(thay, giong.VOICES)
            self.assertTrue(thay.startswith(gioi), (khoa, thay))
        self.assertEqual(giong.giong_du_phong("thai-son"), "nam-tram")
        self.assertEqual(giong.giong_du_phong("minh-duc"), "nam")
        self.assertEqual(giong.giong_du_phong("thu-giang"), "nu-tuoi")

    def test_toc_do_vieneu_cho_moi_giong(self):
        self.assertEqual(thoi_luong.toc("vua", "minh-duc"), thoi_luong.toc("vua", "thu-giang"))
        self.assertNotEqual(thoi_luong.toc("vua", "nu-tuoi"), thoi_luong.toc("vua", "thu-giang"))


class SacEdgeTest(unittest.TestCase):
    def test_voice_rate(self):
        self.assertEqual(giong.voice_rate("nu", "vua"), ("vi-VN-HoaiMyNeural", "+0%", "+0Hz"))
        self.assertEqual(giong.voice_rate("nu-tuoi", "nhanh"), ("vi-VN-HoaiMyNeural", "+21%", "+8Hz"))
        self.assertEqual(giong.voice_rate("nam-tram", "cham"), ("vi-VN-NamMinhNeural", "-14%", "-6Hz"))

    def test_lay_giong_gui_cao_do(self):
        goi = []

        def gia(text, voice, rate, out_path):
            goi.append((voice, rate))
            Path(out_path).write_bytes(b"x" * 100)
            return {"cau": [0.0], "tu": []}

        with tempfile.TemporaryDirectory() as tmp:
            giong.lay_giong(1, "Xin chào.", Path(tmp), "nu-tuoi", "vua", tong_hop=gia, do_dai=lambda p: 1.0)
            giong.lay_giong(2, "Xin chào.", Path(tmp), "nu", "vua", tong_hop=gia, do_dai=lambda p: 1.0)
        self.assertEqual(goi, [("vi-VN-HoaiMyNeural|+8Hz", "+6%"), ("vi-VN-HoaiMyNeural", "+0%")])


if __name__ == "__main__":
    unittest.main()
