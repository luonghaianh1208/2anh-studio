"""Test font đóng gói (Itim; Be Vietnam Pro của phong cách `cat-dan`): đủ 134 chữ tiếng Việt có dấu; khối @font-face
theo chủ đề; bộ biến chủ đề."""

import struct
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))

from video_ma_parts import phong  # noqa: E402

SEGOE_PRINT = Path("C:/Windows/Fonts/segoepr.ttf")


def _dung_font_gia(cac_bang: dict) -> bytes:
    """Ghép một font TrueType tối giản chỉ đủ cho `bang_ma` đọc: bảng offset + các bảng cho trước."""
    so_bang = len(cac_bang)
    offset = 12 + 16 * so_bang
    header = struct.pack(">IHHHH", 0x00010000, so_bang, 0, 0, 0)
    records = b""
    data = b""
    for tag, payload in cac_bang.items():
        records += struct.pack(">4sIII", tag, 0, offset, len(payload))
        data += payload
        offset += len(payload)
    return header + records + data


def _cmap(subtables: dict) -> bytes:
    """subtables: {(platform, encoding): bytes_cua_subtable}."""
    so = len(subtables)
    header = struct.pack(">HH", 0, so)
    records = b""
    body = b""
    offset = 4 + 8 * so
    for (platform, encoding), payload in subtables.items():
        records += struct.pack(">HHI", platform, encoding, offset)
        body += payload
        offset += len(payload)
    return header + records + body


def _dinh_dang_4(doan) -> bytes:
    """doan: list các (start, end, idDelta, idRangeOffset). Segment cuối nên là (0xFFFF, 0xFFFF, 1, 0)."""
    seg_count_x2 = len(doan) * 2
    end_codes = b"".join(struct.pack(">H", d[1]) for d in doan)
    start_codes = b"".join(struct.pack(">H", d[0]) for d in doan)
    id_deltas = b"".join(struct.pack(">h", d[2]) for d in doan)
    id_range_offsets = b"".join(struct.pack(">H", d[3]) for d in doan)
    glyph_ids = struct.pack(">H", 7)
    body = end_codes + struct.pack(">H", 0) + start_codes + id_deltas + id_range_offsets + glyph_ids
    header = struct.pack(">HHHHHHH", 4, 14 + len(body), 0, seg_count_x2, 0, 0, 0)
    return header + body


def _dinh_dang_12(nhom) -> bytes:
    """nhom: list các (startCharCode, endCharCode, startGlyphID)."""
    header = struct.pack(">HHIII", 12, 0, 0, 0, len(nhom))
    body = b"".join(struct.pack(">III", start, end, glyph) for start, end, glyph in nhom)
    return header + body


class ChuVietTest(unittest.TestCase):
    def test_chu_viet_has_134_distinct_characters(self):
        self.assertEqual(len(phong.CHU_VIET), 134)
        self.assertEqual(len(set(phong.CHU_VIET)), 134)


class BangMaTest(unittest.TestCase):
    def test_itim_covers_every_vietnamese_letter(self):
        ma = phong.bang_ma(phong.FONT)
        thieu = [c for c in phong.CHU_VIET if ord(c) not in ma]
        self.assertEqual(thieu, [])
        for c in "ĐƯƠ":
            self.assertIn(ord(c), ma)

    @unittest.skipUnless(SEGOE_PRINT.is_file(), "máy không có segoepr.ttf")
    def test_reader_really_distinguishes_a_font_missing_letters(self):
        ma = phong.bang_ma(SEGOE_PRINT)
        self.assertNotIn(ord("ề"), ma)


class SyntheticCmapTest(unittest.TestCase):
    def _ghi(self, tmp: Path, ten: str, du_lieu: bytes) -> Path:
        path = Path(tmp) / ten
        path.write_bytes(du_lieu)
        return path

    def test_format4_id_range_offset_branch_reads_the_indirect_glyph_id_array(self):
        c = ord("ạ")
        doan = [(c, c, 0, 4), (0xFFFF, 0xFFFF, 1, 0)]
        cmap = _cmap({(3, 1): _dinh_dang_4(doan)})
        font = _dung_font_gia({b"cmap": cmap})
        with tempfile.TemporaryDirectory() as tmp:
            path = self._ghi(tmp, "gia-dinh-dang-4.ttf", font)
            self.assertEqual(phong.bang_ma(path), {c})

    def test_format12_covers_supplementary_plane_and_multiple_groups(self):
        nhom = [(0x1F600, 0x1F602, 100), (ord("ề"), ord("ề"), 200)]
        cmap = _cmap({(3, 10): _dinh_dang_12(nhom)})
        font = _dung_font_gia({b"cmap": cmap})
        with tempfile.TemporaryDirectory() as tmp:
            path = self._ghi(tmp, "gia-dinh-dang-12.ttf", font)
            self.assertEqual(phong.bang_ma(path), {0x1F600, 0x1F601, 0x1F602, ord("ề")})


class FontCssTest(unittest.TestCase):
    def test_font_css_embeds_the_font_as_base64_data_url(self):
        css = phong.font_css()
        self.assertIn("@font-face", css)
        self.assertIn(f"font-family:'{phong.TEN}'", css)
        self.assertIn("url(data:font/ttf;base64,", css)
        self.assertNotIn("http://", css)
        self.assertNotIn("https://", css)


class BeVietnamProTest(unittest.TestCase):
    def test_hai_do_dam_du_chu_viet(self):
        self.assertEqual(sorted(phong.FONT_CAT_DAN), [400, 800])
        for dam, path in phong.FONT_CAT_DAN.items():
            with self.subTest(dam=dam):
                self.assertTrue(path.is_file(), path)
                ma = phong.bang_ma(path)
                self.assertEqual([c for c in phong.CHU_VIET if ord(c) not in ma], [])
                for c in "ĐƯƠ":
                    self.assertIn(ord(c), ma)

    def test_font_css_cat_dan_nhung_hai_do_dam_va_itim(self):
        css = phong.font_css("cat-dan")
        self.assertEqual(css.count("@font-face"), 3)
        self.assertEqual(css.count("font-family:'BeVietnamPro'"), 2)
        self.assertIn("font-weight:400", css)
        self.assertIn("font-weight:800", css)
        self.assertIn(f"font-family:'{phong.TEN}'", css)
        self.assertNotIn("http", css)

    def test_font_css_viet_tay_nhu_cu(self):
        self.assertEqual(phong.font_css("viet-tay"), phong.font_css())
        self.assertEqual(phong.font_css().count("@font-face"), 1)
        self.assertNotIn("BeVietnamPro", phong.font_css())

    def test_giay_phep_va_nguon_font(self):
        thu_muc = phong.FONT.parent
        self.assertIn("SIL OPEN FONT LICENSE", (thu_muc / "OFL-BeVietnamPro.txt").read_text(encoding="utf-8").upper())
        readme = (thu_muc / "README.md").read_text(encoding="utf-8")
        for tep, dam in (("BeVietnamPro-Regular.ttf", 400), ("BeVietnamPro-ExtraBold.ttf", 800)):
            import hashlib
            so = hashlib.sha256(phong.FONT_CAT_DAN[dam].read_bytes()).hexdigest()
            self.assertIn(tep, readme)
            self.assertIn(so, readme)


class ChuDeTest(unittest.TestCase):
    def test_hai_chu_de(self):
        self.assertEqual(phong.CHU_DE["viet-tay"], {"ten": "viet-tay", "font": "Itim", "hienChu": "viet", "net": "ve"})
        self.assertEqual(phong.CHU_DE["cat-dan"], {
            "ten": "cat-dan", "font": "BeVietnamPro", "hienChu": "truot", "net": "nhanh",
            "mauNhan": ["#b07419", "#1f6f78", "#c8452f", "#2f4f9e"], "giay": "#f3ead7"})

    def test_mau_nhan_doc_duoc_tren_giay_va_the(self):
        # Nhãn nhỏ chữ hoa (nhãn thẻ, số loạt "01/03") tô màu nhãn trên giấy nền và giấy thẻ #fffaf0: tương phản ≥ 3:1.
        def sang(mau):
            c = [int(mau[i:i + 2], 16) / 255 for i in (1, 3, 5)]
            c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
            return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

        def tuong_phan(a, b):
            lo, hi = sorted((sang(a), sang(b)))
            return (hi + 0.05) / (lo + 0.05)

        cd = phong.CHU_DE["cat-dan"]
        self.assertEqual(len(cd["mauNhan"]), 4)
        for mau in cd["mauNhan"]:
            for nen in (cd["giay"], "#fffaf0"):
                self.assertGreaterEqual(tuong_phan(mau, nen), 3.0, (mau, nen))

    def test_chu_de_la_ban_sao(self):
        a = phong.chu_de("cat-dan")
        a["mauNhan"].append("#000000")
        self.assertEqual(len(phong.chu_de("cat-dan")["mauNhan"]), 4)
        self.assertEqual(phong.chu_de(None), phong.CHU_DE["viet-tay"])


if __name__ == "__main__":
    unittest.main()
