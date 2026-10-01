"""Test hình vẽ nét (tabler-outline) và ảnh thật cho video giải thích.

Không cần Chromium, FFmpeg hay mạng, trừ test JPEG (tự bỏ qua khi máy không có ffmpeg).
"""

import json
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))

from video_ma_parts import anh, hinh, kiem, parse  # noqa: E402

META = "tieu-de: T\nmon: Toán\nlop: 8\n"
HAS_FFMPEG = shutil.which("ffmpeg") is not None


def doc(canh: str, meta: str = META) -> str:
    return f"---\n{meta}---\n\n{canh}"


def line_of(text: str, needle: str) -> int:
    for number, line in enumerate(text.splitlines(), 1):
        if needle in line:
            return number
    raise AssertionError(needle)


def _png(path: Path, width: int = 1, height: int = 1) -> None:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + b"\xff\x00\x00" * width for _ in range(height))
    idat = zlib.compress(raw)
    path.write_bytes(sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b""))


def _jpeg(path: Path, width: int = 4, height: int = 3) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
         "-i", f"color=c=red:s={width}x{height}", "-frames:v", "1", str(path)],
        check=True, timeout=60,
    )


def _webp_vp8x(path: Path, width: int, height: int) -> None:
    data = b"\x00\x00\x00\x00" + (width - 1).to_bytes(3, "little") + (height - 1).to_bytes(3, "little")
    chunk = b"VP8X" + struct.pack("<I", len(data)) + data
    payload = b"WEBP" + chunk
    path.write_bytes(b"RIFF" + struct.pack("<I", len(payload)) + payload)


def _webp_vp8l(path: Path, width: int, height: int) -> None:
    bits = (width - 1) | ((height - 1) << 14)
    data = b"\x2f" + struct.pack("<I", bits)
    chunk = b"VP8L" + struct.pack("<I", len(data)) + data
    payload = b"WEBP" + chunk
    path.write_bytes(b"RIFF" + struct.pack("<I", len(payload)) + payload)


def _exif(orientation: int, thu_tu: bytes = b"II") -> bytes:
    """Đoạn APP1 Exif chỉ có thẻ Orientation (0x0112), thứ tự byte II (little) hoặc MM (big)."""
    f = "<" if thu_tu == b"II" else ">"
    tiff = (thu_tu + struct.pack(f + "HI", 42, 8) + struct.pack(f + "H", 1)
            + struct.pack(f + "HHIHH", 0x0112, 3, 1, orientation, 0) + struct.pack(f + "I", 0))
    du = b"Exif\x00\x00" + tiff
    return b"\xff\xe1" + struct.pack(">H", len(du) + 2) + du


def _jpeg_byte(width: int, height: int, exif: bytes = b"") -> bytes:
    """JPEG tự dựng bằng byte: SOI, (APP1 Exif), SOF0, EOI. Đủ để đọc kích thước, không giải mã được."""
    sof = b"\xff\xc0" + struct.pack(">HBHHB", 11, 8, height, width, 1) + b"\x01\x11\x00"
    return b"\xff\xd8" + exif + sof + b"\xff\xd9"


def _webp_vp8(path: Path, width: int, height: int) -> None:
    data = b"\x10\x02\x00" + b"\x9d\x01\x2a" + struct.pack("<HH", width, height) + b"\x00" * 4
    chunk = b"VP8 " + struct.pack("<I", len(data)) + data
    payload = b"WEBP" + chunk
    path.write_bytes(b"RIFF" + struct.pack("<I", len(payload)) + payload)


class ChuanTenTest(unittest.TestCase):
    def test_strips_prefix_suffix_case_and_spaces(self):
        self.assertEqual(hinh.chuan_ten("  tabler-outline/Flask.svg  "), "flask")
        self.assertEqual(hinh.chuan_ten("Flask"), "flask")
        self.assertEqual(hinh.chuan_ten("flask.svg"), "flask")
        self.assertEqual(hinh.chuan_ten("tabler-outline/flask"), "flask")


class HinhDocTest(unittest.TestCase):
    def test_flask_has_three_path_elements(self):
        h = hinh.doc("flask")
        self.assertEqual(h["ten"], "flask")
        self.assertEqual(h["viewBox"], "0 0 24 24")
        self.assertEqual([p["the"] for p in h["phanTu"]], ["path", "path", "path"])

    def test_atom_has_no_frame_path(self):
        h = hinh.doc("atom")
        self.assertTrue(h["phanTu"])
        for p in h["phanTu"]:
            self.assertNotEqual(p["thuocTinh"].get("d"), "M0 0h24v24H0z")
            self.assertNotEqual(p["thuocTinh"].get("stroke"), "none")

    def test_accepts_prefixed_and_suffixed_names(self):
        self.assertEqual(hinh.doc("tabler-outline/Flask.svg")["ten"], "flask")

    def test_unknown_name_raises_with_suggestions(self):
        with self.assertRaises(hinh.HinhError) as caught:
            hinh.doc("binh-thi-nghiem")
        self.assertIn("Có thể bạn muốn", str(caught.exception))


class TachMinhHoaTest(unittest.TestCase):
    def test_splits_name_and_label(self):
        self.assertEqual(hinh.tach_minh_hoa("clock | Đồng hồ bấm giây"), ("clock", "Đồng hồ bấm giây"))

    def test_missing_bar_raises(self):
        with self.assertRaises(hinh.HinhError) as caught:
            hinh.tach_minh_hoa("clock")
        self.assertIn("tên | nhãn", str(caught.exception))

    def test_missing_label_raises(self):
        with self.assertRaises(hinh.HinhError) as caught:
            hinh.tach_minh_hoa("clock | ")
        self.assertIn("tên | nhãn", str(caught.exception))

    def test_label_over_thirty_characters_raises(self):
        with self.assertRaises(hinh.HinhError):
            hinh.tach_minh_hoa("clock | " + "a" * 31)

    def test_label_at_thirty_characters_is_fine(self):
        ten, nhan = hinh.tach_minh_hoa("clock | " + "a" * 30)
        self.assertEqual((ten, nhan), ("clock", "a" * 30))


class KiemHinhTest(unittest.TestCase):
    def test_prefixed_name_passes_kiem(self):
        text = doc("## Cảnh 1\nloai: tieu-de\nchu: A\nhinh: tabler-outline/Flask.svg\nloi: Xin chào.\n")
        self.assertEqual(kiem.kiem(parse.parse(text), Path(".")), [])

    def test_unknown_icon_is_a_canh_error_with_line_number(self):
        text = doc("## Cảnh 1\nloai: tieu-de\nchu: A\nhinh: binh-thi-nghiem\nloi: Xin chào.\n")
        with self.assertRaises(kiem.CanhError) as caught:
            kiem.kiem(parse.parse(text), Path("."))
        self.assertEqual(caught.exception.so, 1)
        self.assertIn(f"dòng {line_of(text, 'binh-thi-nghiem')}", str(caught.exception))

    def test_minh_hoa_picture_starts_at_its_own_line(self):
        text = doc("## Cảnh 1\nloai: minh-hoa\ntieu-de: A\nhinh: clock | Đồng hồ\nhinh: binh-thi-nghiem | Xấu\nloi: Xin chào.\n")
        with self.assertRaises(kiem.CanhError) as caught:
            kiem.kiem(parse.parse(text), Path("."))
        self.assertIn(f"dòng {line_of(text, 'binh-thi-nghiem')}", str(caught.exception))

    def test_minh_hoa_label_over_limit_is_a_canh_error(self):
        text = doc(f"## Cảnh 1\nloai: minh-hoa\ntieu-de: A\nhinh: clock | {'a' * 31}\nloi: Xin chào.\n")
        with self.assertRaises(kiem.CanhError):
            kiem.kiem(parse.parse(text), Path("."))

    def test_minh_hoa_missing_bar_is_a_canh_error_naming_the_shape(self):
        text = doc("## Cảnh 1\nloai: minh-hoa\ntieu-de: A\nhinh: clock\nloi: Xin chào.\n")
        with self.assertRaises(kiem.CanhError) as caught:
            kiem.kiem(parse.parse(text), Path("."))
        self.assertIn("tên | nhãn", str(caught.exception))


class AnhDocTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.thu_muc = Path(self.tmp.name)
        (self.thu_muc / "anh").mkdir()

    def test_reads_png_dimensions(self):
        _png(self.thu_muc / "anh" / "x.png", 3, 2)
        info = anh.doc(self.thu_muc, "x.png", "Ảnh tự chụp")
        self.assertEqual((info["rong"], info["cao"]), (3, 2))
        self.assertTrue(info["dataUrl"].startswith("data:image/png;base64,"))
        self.assertEqual(info["nguon"], "Ảnh tự chụp")

    def test_missing_file_raises(self):
        with self.assertRaises(anh.AnhError):
            anh.doc(self.thu_muc, "khong-co.png", "nguồn")

    def test_bad_extension_raises(self):
        (self.thu_muc / "anh" / "x.gif").write_bytes(b"GIF89a")
        with self.assertRaises(anh.AnhError):
            anh.doc(self.thu_muc, "x.gif", "nguồn")

    def test_oversized_file_raises(self):
        path = self.thu_muc / "anh" / "to.png"
        path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * anh.TOI_DA)
        with self.assertRaises(anh.AnhError):
            anh.doc(self.thu_muc, "to.png", "nguồn")

    def test_missing_source_raises(self):
        _png(self.thu_muc / "anh" / "x.png")
        with self.assertRaises(anh.AnhError):
            anh.doc(self.thu_muc, "x.png", None)

    def test_manifest_source_has_author_and_license(self):
        _png(self.thu_muc / "anh" / "x.png")
        (self.thu_muc / "anh" / "image_sources.json").write_text(
            json.dumps({"items": [{"filename": "x.png", "author": "Nguyễn Văn A",
                                    "license_name": "CC BY 4.0", "provider": "openverse"}]}),
            encoding="utf-8",
        )
        info = anh.doc(self.thu_muc, "x.png", None)
        self.assertIn("Nguyễn Văn A", info["nguon"])
        self.assertIn("CC BY 4.0", info["nguon"])

    def test_hand_written_source_wins_over_manifest(self):
        _png(self.thu_muc / "anh" / "x.png")
        (self.thu_muc / "anh" / "image_sources.json").write_text(
            json.dumps({"items": [{"filename": "x.png", "author": "Manifest", "license_name": "CC0", "provider": "p"}]}),
            encoding="utf-8",
        )
        info = anh.doc(self.thu_muc, "x.png", "Ảnh tự chụp")
        self.assertEqual(info["nguon"], "Ảnh tự chụp")

    def test_filename_with_vietnamese_accents_and_spaces(self):
        _png(self.thu_muc / "anh" / "ảnh con lắc.png")
        info = anh.doc(self.thu_muc, "ảnh con lắc.png", "nguồn")
        self.assertEqual((info["rong"], info["cao"]), (1, 1))

    @unittest.skipUnless(HAS_FFMPEG, "máy không có ffmpeg")
    def test_reads_jpeg_dimensions(self):
        _jpeg(self.thu_muc / "anh" / "x.jpg", 4, 3)
        info = anh.doc(self.thu_muc, "x.jpg", "nguồn")
        self.assertEqual((info["rong"], info["cao"]), (4, 3))


class WebpDocTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.thu_muc = Path(self.tmp.name)
        (self.thu_muc / "anh").mkdir()

    def test_reads_vp8x_dimensions(self):
        _webp_vp8x(self.thu_muc / "anh" / "x.webp", 5, 7)
        info = anh.doc(self.thu_muc, "x.webp", "nguồn")
        self.assertEqual((info["rong"], info["cao"]), (5, 7))
        self.assertTrue(info["dataUrl"].startswith("data:image/webp;base64,"))

    def test_reads_vp8l_dimensions(self):
        _webp_vp8l(self.thu_muc / "anh" / "x.webp", 9, 2)
        info = anh.doc(self.thu_muc, "x.webp", "nguồn")
        self.assertEqual((info["rong"], info["cao"]), (9, 2))

    def test_reads_vp8_lossy_dimensions(self):
        _webp_vp8(self.thu_muc / "anh" / "x.webp", 640, 427)
        info = anh.doc(self.thu_muc, "x.webp", "nguồn")
        self.assertEqual((info["rong"], info["cao"]), (640, 427))


class JpegExifTest(unittest.TestCase):
    """Ảnh điện thoại lưu điểm ảnh nằm ngang kèm thẻ Orientation; Chromium xoay theo thẻ nên khung phải xoay theo."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.thu_muc = Path(self.tmp.name)
        (self.thu_muc / "anh").mkdir()

    def kich(self, du_lieu: bytes) -> tuple:
        (self.thu_muc / "anh" / "x.jpg").write_bytes(du_lieu)
        info = anh.doc(self.thu_muc, "x.jpg", "nguồn")
        return info["rong"], info["cao"]

    def test_orientation_6_swaps_width_and_height(self):
        self.assertEqual(self.kich(_jpeg_byte(400, 300, _exif(6))), (300, 400))

    def test_orientation_5_to_8_swap_in_both_byte_orders(self):
        for thu_tu in (b"II", b"MM"):
            for huong in (5, 6, 7, 8):
                with self.subTest(thu_tu=thu_tu, huong=huong):
                    self.assertEqual(self.kich(_jpeg_byte(400, 300, _exif(huong, thu_tu))), (300, 400))

    def test_orientation_1_to_4_and_no_exif_keep_the_size(self):
        self.assertEqual(self.kich(_jpeg_byte(400, 300)), (400, 300))
        for huong in (1, 2, 3, 4):
            with self.subTest(huong=huong):
                self.assertEqual(self.kich(_jpeg_byte(400, 300, _exif(huong, b"MM"))), (400, 300))

    def test_broken_exif_is_ignored(self):
        hong = b"\xff\xe1" + struct.pack(">H", 10) + b"Exif\x00\x00MM"
        self.assertEqual(self.kich(_jpeg_byte(400, 300, hong)), (400, 300))


class ManifestTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.thu_muc = Path(self.tmp.name)
        (self.thu_muc / "anh").mkdir()
        _png(self.thu_muc / "anh" / "x.png")
        self.manifest = self.thu_muc / "anh" / "image_sources.json"

    def test_web_addresses_are_stripped_from_the_credit(self):
        self.manifest.write_text(json.dumps({"items": [{
            "filename": "x.png", "author": "Nguyễn Văn A (https://example.org/u/a)",
            "license_name": "CC BY 4.0", "provider": "www.flickr.com/photos/x"}]}), encoding="utf-8")
        self.assertEqual(anh.doc(self.thu_muc, "x.png", None)["nguon"], "Ảnh: Nguyễn Văn A · CC BY 4.0")

    def test_manifest_that_is_a_list_is_an_anh_error(self):
        self.manifest.write_text(json.dumps([{"filename": "x.png", "author": "A"}]), encoding="utf-8")
        with self.assertRaises(anh.AnhError) as caught:
            anh.doc(self.thu_muc, "x.png", None)
        self.assertIn("image_sources.json", str(caught.exception))

    def test_manifest_with_non_dict_items_is_an_anh_error(self):
        for items in (["x.png"], "x.png", [None]):
            with self.subTest(items=items):
                self.manifest.write_text(json.dumps({"items": items}), encoding="utf-8")
                with self.assertRaises(anh.AnhError) as caught:
                    anh.doc(self.thu_muc, "x.png", None)
                self.assertIn("image_sources.json", str(caught.exception))

    def test_manifest_that_is_not_json_is_an_anh_error(self):
        self.manifest.write_text("{items: [", encoding="utf-8")
        with self.assertRaises(anh.AnhError) as caught:
            anh.doc(self.thu_muc, "x.png", None)
        self.assertIn("image_sources.json", str(caught.exception))

    def test_malformed_manifest_through_the_tool_is_a_canh_error_not_internal(self):
        self.manifest.write_text(json.dumps([1, 2]), encoding="utf-8")
        text = doc("## Cảnh 1\nloai: anh\nanh: x.png\nchu-thich: Chú thích\nloi: Xin chào.\n")
        with self.assertRaises(kiem.CanhError):
            kiem.kiem(parse.parse(text), self.thu_muc)


class TenFileUnicodeTest(unittest.TestCase):
    def test_nfd_file_on_disk_is_found_by_its_nfc_name(self):
        import unicodedata

        with tempfile.TemporaryDirectory() as tmp:
            thu_muc = Path(tmp)
            (thu_muc / "anh").mkdir()
            nfd = unicodedata.normalize("NFD", "đồng hồ quả lắc.png")
            _png(thu_muc / "anh" / nfd, 3, 2)
            info = anh.doc(thu_muc, unicodedata.normalize("NFC", "đồng hồ quả lắc.png"), "nguồn")
            self.assertEqual((info["rong"], info["cao"]), (3, 2))


class DiacriticIconNameTest(unittest.TestCase):
    def test_literal_vietnamese_name_is_a_canh_error_with_suggestions(self):
        text = doc("## Cảnh 1\nloai: tieu-de\nchu: A\nhinh: bình thí nghiệm\nloi: Xin chào.\n")
        with self.assertRaises(kiem.CanhError) as caught:
            kiem.kiem(parse.parse(text), Path("."))
        self.assertIn(f"dòng {line_of(text, 'bình thí nghiệm')}", str(caught.exception))

    def test_hinh_doc_literal_vietnamese_name_raises_with_suggestions(self):
        with self.assertRaises(hinh.HinhError) as caught:
            hinh.doc("bình thí nghiệm")
        self.assertIn("Có thể bạn muốn", str(caught.exception))


def _goi_y(ten: str) -> list:
    with unittest.TestCase().assertRaises(hinh.HinhError) as caught:
        hinh.doc(ten)
    thong_bao = str(caught.exception)
    if "Có thể bạn muốn: " not in thong_bao:
        return []
    return [t.strip() for t in thong_bao.split("Có thể bạn muốn: ", 1)[1].rstrip(".").split(",")]


class VietnameseIconSuggestionTest(unittest.TestCase):
    def test_error_says_names_are_english_and_points_to_the_lookup_table(self):
        with self.assertRaises(hinh.HinhError) as caught:
            hinh.doc("nam châm")
        thong_bao = str(caught.exception)
        self.assertIn("tiếng Anh", thong_bao)
        self.assertIn("Bảng tra biểu tượng", thong_bao)
        self.assertIn("docs/vi/tham-khao/canh-video.md", thong_bao)

    def test_nam_cham_suggests_magnet_first(self):
        self.assertEqual(_goi_y("nam châm")[0], "magnet")
        self.assertEqual(_goi_y("Nam cham")[0], "magnet")

    def test_dong_ho_suggests_a_clock(self):
        goi_y = _goi_y("đồng hồ")
        self.assertEqual(goi_y[0], "clock")
        self.assertIn("stopwatch", goi_y)

    def test_brand_icons_are_never_suggested(self):
        for ten in ("githu", "facebok", "youtub", "tiktok-logo", "brand", "đồng hồ", "bình thí nghiệm", "twiter"):
            with self.subTest(ten=ten):
                self.assertFalse([t for t in _goi_y(ten) if t.startswith("brand-")], _goi_y(ten))

    def test_at_most_five_suggestions(self):
        for ten in ("đồng hồ", "bình", "flaks"):
            with self.subTest(ten=ten):
                self.assertLessEqual(len(_goi_y(ten)), 5)


class HinhPathEscapeTest(unittest.TestCase):
    def test_rejects_absolute_windows_path(self):
        with self.assertRaises(hinh.HinhError):
            hinh.doc("C:/Windows/win.ini")

    def test_rejects_dot_dot_traversal_reaching_a_real_file(self):
        secret = hinh.THU_MUC.parent / "secret-icon.svg"
        secret.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke="currentColor">'
            '<path d="M1 1 2 2" /></svg>',
            encoding="utf-8",
        )
        self.addCleanup(secret.unlink)
        with self.assertRaises(hinh.HinhError):
            hinh.doc("../secret-icon")

    def test_rejects_backslash_traversal(self):
        with self.assertRaises(hinh.HinhError):
            hinh.doc("..\\..\\windows\\win.ini")

    def test_prefixed_svg_name_still_works(self):
        self.assertEqual(hinh.doc("tabler-outline/flask.svg")["ten"], "flask")


class AnhPathEscapeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.thu_muc = Path(self.tmp.name)
        (self.thu_muc / "anh").mkdir()

    def test_rejects_absolute_windows_path(self):
        with self.assertRaises(anh.AnhError):
            anh.doc(self.thu_muc, "C:/Windows/win.ini", "nguồn")

    def test_rejects_dot_dot_traversal_reaching_a_real_file(self):
        secret = self.thu_muc / "secret.png"
        _png(secret)
        with self.assertRaises(anh.AnhError):
            anh.doc(self.thu_muc, "../secret.png", "nguồn")

    def test_rejects_backslash_traversal_reaching_a_real_file(self):
        secret = self.thu_muc / "secret.png"
        _png(secret)
        with self.assertRaises(anh.AnhError):
            anh.doc(self.thu_muc, "..\\secret.png", "nguồn")

    def test_vietnamese_filename_with_spaces_still_works(self):
        _png(self.thu_muc / "anh" / "ảnh con lắc.png")
        info = anh.doc(self.thu_muc, "ảnh con lắc.png", "nguồn")
        self.assertEqual((info["rong"], info["cao"]), (1, 1))


class KiemAnhSceneTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.thu_muc = Path(self.tmp.name)
        (self.thu_muc / "anh").mkdir()
        _png(self.thu_muc / "anh" / "x.png")

    def test_anh_scene_with_its_own_source_passes(self):
        text = doc("## Cảnh 1\nloai: anh\nanh: x.png\nchu-thich: Chú thích\nnguon: Ảnh tự chụp\nloi: Xin chào.\n")
        self.assertEqual(kiem.kiem(parse.parse(text), self.thu_muc), [])

    def test_anh_scene_missing_source_is_a_canh_error(self):
        text = doc("## Cảnh 1\nloai: anh\nanh: x.png\nchu-thich: Chú thích\nloi: Xin chào.\n")
        with self.assertRaises(kiem.CanhError):
            kiem.kiem(parse.parse(text), self.thu_muc)

    def test_column_scenes_accept_a_hand_written_source_with_a_photo(self):
        dau = {"tieu-de": "chu: A\n", "khai-niem": "thuat-ngu: A\ndinh-nghia: B\n",
               "cong-thuc": "bieu-thuc: a = b\n", "y-tung-y": "tieu-de: A\ny: B\n"}
        for loai, truong in dau.items():
            with self.subTest(loai=loai):
                text = doc(f"## Cảnh 1\nloai: {loai}\n{truong}anh: x.png\nnguon: Ảnh: cô Lan chụp\nloi: Xin chào.\n")
                video = parse.parse(text)
                self.assertEqual(video.canh[0].truong["nguon"], ["Ảnh: cô Lan chụp"])
                self.assertEqual(kiem.kiem(video, self.thu_muc), [])

    def test_source_without_a_photo_is_a_parse_error_on_its_line(self):
        for loai, truong in (("tieu-de", "chu: A\n"), ("y-tung-y", "tieu-de: A\ny: B\nhinh: flask\n")):
            with self.subTest(loai=loai):
                text = doc(f"## Cảnh 1\nloai: {loai}\n{truong}nguon: Ảnh: cô Lan chụp\nloi: Xin chào.\n")
                with self.assertRaises(parse.ParseError) as caught:
                    parse.parse(text)
                self.assertEqual(caught.exception.line_no, line_of(text, "nguon:"))
                self.assertIn("`anh`", caught.exception.message)


if __name__ == "__main__":
    unittest.main()


class GoiYThuTuTest(unittest.TestCase):
    def test_english_typo_gets_the_english_name_first(self):
        from video_ma_parts import hinh as h
        self.assertEqual(h.goi_y("magnt")[0], "magnet")

    def test_vietnamese_input_still_uses_the_table_first(self):
        from video_ma_parts import hinh as h
        self.assertEqual(h.goi_y("nam châm")[0], "magnet")
        self.assertIn("flask", h.goi_y("binh-thi-nghiem"))

    def test_unreadable_table_gives_no_table_suggestions(self):
        from unittest import mock
        from video_ma_parts import hinh as h
        with mock.patch.object(h.BANG_TRA.__class__, "read_text", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "x")):
            self.assertEqual(h.bang_tra(), [])

