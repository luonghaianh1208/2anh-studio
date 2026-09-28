"""Ảnh do AI vẽ cho video giải thích (spec Q7, Q10, Q11): đường `ai/<file>` trong anh/, nguồn từ anh/ai/nguon.json,
kênh trong suốt của ảnh nhân vật, lỗi liệt kê mọi file AI còn thiếu, dòng "Hình minh hoạ tạo bằng AI" cuối video.

Không cần Chromium, FFmpeg hay mạng."""

import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))

import video_ma  # noqa: E402
from video_ma_parts import anh, kiem, lich, parse  # noqa: E402

META = "tieu-de: T\nmon: Toán\nlop: 8\n"


def png(path: Path, rong: int = 2, cao: int = 2, kieu: int = 6, trns: bool = False) -> Path:
    """PNG nhỏ: `kieu` 6 = RGBA, 2 = RGB (thêm khối tRNS khi `trns`)."""
    def khoi(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    kenh = 4 if kieu == 6 else 3
    tho = b"".join(b"\x00" + b"\x10" * kenh * rong for _ in range(cao))
    than = khoi(b"IHDR", struct.pack(">IIBBBBB", rong, cao, 8, kieu, 0, 0, 0))
    if trns:
        than += khoi(b"tRNS", b"\x00\x00\x00\x00\x00\x00")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + than + khoi(b"IDAT", zlib.compress(tho)) + khoi(b"IEND", b""))
    return path


def jpeg(path: Path, rong: int = 4, cao: int = 3) -> Path:
    """JPEG tối thiểu đủ để đọc kích thước (SOI, SOF0, EOI)."""
    sof = b"\xff\xc0" + struct.pack(">HBHHB", 11, 8, cao, rong, 1) + b"\x01\x11\x00"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\xff\xd8" + sof + b"\xff\xd9")
    return path


def nguon_ai(thu_muc: Path, *cac_file: tuple) -> None:
    """anh/ai/nguon.json theo khuôn Task 12: [{file, cong_cu, mo_hinh, prompt, ngay}]; `file` là tên trần trong anh/ai/."""
    ds = [{"file": f, "cong_cu": "Antigravity", "mo_hinh": m, "prompt": "vẽ", "ngay": "2026-09-28"} for f, m in cac_file]
    (thu_muc / "anh" / "ai").mkdir(parents=True, exist_ok=True)
    (thu_muc / "anh" / "ai" / "nguon.json").write_text(json.dumps(ds, ensure_ascii=False), encoding="utf-8")


def ke(so: int, nen: str, them: str = "") -> str:
    return f"## Cảnh {so}\nloai: ke-chuyen\ntieu-de: Cảnh {so}\nnen: {nen}\n{them}loi: Xin chào.\n\n"


class AnhAiDocTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.thu_muc = Path(self.tmp.name)

    def test_doc_ai_nen_co_nguon_ai(self):
        jpeg(self.thu_muc / "anh" / "ai" / "nen-2.jpg", 1920, 1080)
        nguon_ai(self.thu_muc, ("nen-2.jpg", "Imagen 4"))
        info = anh.doc(self.thu_muc, "ai/nen-2.jpg", None)
        self.assertEqual((info["rong"], info["cao"]), (1920, 1080))
        self.assertEqual(info["nguon"], "Hình minh hoạ tạo bằng AI (Imagen 4)")
        self.assertEqual(info["moHinh"], "Imagen 4")
        self.assertTrue(info["ai"])
        self.assertTrue(info["dataUrl"].startswith("data:image/jpeg;base64,"))
        # Ảnh thường không có khoá AI (dữ liệu cảnh cũ giữ nguyên).
        png(self.thu_muc / "anh" / "x.png")
        self.assertNotIn("ai", anh.doc(self.thu_muc, "x.png", "Ảnh tự chụp"))

    def test_thieu_nguon_ai_bao_chay_anh_ai_nhan(self):
        jpeg(self.thu_muc / "anh" / "ai" / "nen-2.jpg")
        for co_file in (False, True):
            with self.subTest(co_file=co_file):
                if co_file:
                    nguon_ai(self.thu_muc, ("nen-3.jpg", "Imagen 4"))
                with self.assertRaises(anh.AnhError) as caught:
                    anh.doc(self.thu_muc, "ai/nen-2.jpg", "nguồn tay không thay được nguồn AI")
                self.assertIn("python tools/vi/anh_ai.py <thư_mục> nhan", str(caught.exception))
                self.assertIn("anh/ai/nguon.json", str(caught.exception))

    def test_nguon_ai_sai_cau_truc(self):
        jpeg(self.thu_muc / "anh" / "ai" / "nen-2.jpg")
        (self.thu_muc / "anh" / "ai" / "nguon.json").write_text('{"items": []}', encoding="utf-8")
        with self.assertRaises(anh.AnhError) as caught:
            anh.doc(self.thu_muc, "ai/nen-2.jpg", None)
        self.assertIn("nguon.json", str(caught.exception))

    def test_duong_dan_ai_bi_chan(self):
        png(self.thu_muc / "x.png")
        png(self.thu_muc / "anh" / "ai" / "ai" / "x.png")
        for ten in ("ai/../x.png", "ai/../../x.png", "ai/ai/x.png", "../ai/x.png", "ai\\x.png", "ai/", "b/x.png",
                    "/ai/x.png", "AI/x.png"):
            with self.subTest(ten=ten):
                with self.assertRaises(anh.AnhError) as caught:
                    anh.doc(self.thu_muc, ten, "nguồn")
                self.assertIn("không hợp lệ", str(caught.exception))

    def test_kenh_trong_suot(self):
        self.assertTrue(anh.co_alpha(png(self.thu_muc / "a.png", kieu=6).read_bytes(), ".png"))
        self.assertFalse(anh.co_alpha(png(self.thu_muc / "b.png", kieu=2).read_bytes(), ".png"))
        self.assertTrue(anh.co_alpha(png(self.thu_muc / "c.png", kieu=2, trns=True).read_bytes(), ".png"))
        self.assertFalse(anh.co_alpha(jpeg(self.thu_muc / "d.jpg").read_bytes(), ".jpg"))
        png(self.thu_muc / "anh" / "ai" / "tu-the-chao.png", kieu=6)
        nguon_ai(self.thu_muc, ("tu-the-chao.png", "Imagen 4"))
        self.assertTrue(anh.doc(self.thu_muc, "ai/tu-the-chao.png", None)["alpha"])


class AnhAiKiemTest(unittest.TestCase):
    """kiem.kiem: file AI thiếu của cả video báo một lần; ảnh nhân vật không có kênh trong suốt là lỗi `canh`."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.thu_muc = Path(self.tmp.name)

    def video(self, canh: str, meta: str = META + "nhan-vat: ve: cô giáo trẻ áo dài xanh\n"):
        return parse.parse(f"---\n{meta}---\n\n{canh}")

    CANH = (ke(1, "ve: ruộng bậc thang buổi sáng", "tu-the: chao\n") + ke(2, "nhu-canh 1", "tu-the: chao\n")
            + ke(3, "mau/giay", "tu-the: buon\n")
            + "## Cảnh 4\nloai: khai-niem\nthuat-ngu: A\ndinh-nghia: B\ntu-the: chao\nloi: Xin chào.\n")

    def test_can_ai_liet_ke_file_theo_thu_tu_khong_lap(self):
        self.assertEqual(kiem.can_ai(self.video(self.CANH)),
                         [(1, "ai/nen-1.jpg"), (1, "ai/tu-the-chao.png"), (3, "ai/tu-the-buon.png")])
        # Người que: chỉ nền AI; không nhân vật: không ảnh nhân vật.
        self.assertEqual(kiem.can_ai(self.video(self.CANH, META + "nhan-vat: nguoi-que\n")), [(1, "ai/nen-1.jpg")])
        self.assertEqual(kiem.can_ai(self.video(ke(1, "mau/giay"), META)), [])
        # Cảnh kể chuyện không ghi `tu-the` dùng tư thế đứng.
        self.assertEqual(kiem.can_ai(self.video(ke(1, "mau/giay"))), [(1, "ai/tu-the-dung.png")])

    def test_thieu_ba_file_ai_mot_loi_liet_ke_du_ba(self):
        with self.assertRaises(kiem.CanhError) as caught:
            kiem.kiem(self.video(self.CANH), self.thu_muc)
        msg = str(caught.exception)
        self.assertTrue(msg.startswith("Cảnh 1: "), msg)
        for f in ("anh/ai/nen-1.jpg", "anh/ai/tu-the-chao.png", "anh/ai/tu-the-buon.png"):
            self.assertIn(f, msg)
        self.assertIn("3 ảnh", msg)
        fix = caught.exception.fix
        for phrase in ("anh_ai.py", "ke-hoach", "nen: mau/", "nhan-vat: nguoi-que"):
            self.assertIn(phrase, fix)

    def test_du_file_thi_qua_nen_png_cung_nhan(self):
        png(self.thu_muc / "anh" / "ai" / "nen-1.png", 16, 9, kieu=2)
        png(self.thu_muc / "anh" / "ai" / "tu-the-chao.png")
        png(self.thu_muc / "anh" / "ai" / "tu-the-buon.png")
        nguon_ai(self.thu_muc, ("nen-1.png", "Imagen 4"), ("tu-the-chao.png", "Imagen 4"), ("tu-the-buon.png", "Imagen 4"))
        self.assertEqual(kiem.kiem(self.video(self.CANH), self.thu_muc), [])
        self.assertEqual(kiem.file_ai(self.thu_muc, "ai/nen-1.jpg"), "ai/nen-1.png")

    def test_nhan_vat_khong_trong_suot_la_loi_chua_tach_nen(self):
        jpeg(self.thu_muc / "anh" / "ai" / "nen-1.jpg")
        png(self.thu_muc / "anh" / "ai" / "tu-the-buon.png")
        for ten, tao in (("tu-the-chao.png", lambda p: png(p, kieu=2)), ("tu-the-chao.jpg", jpeg)):
            with self.subTest(ten=ten):
                for cu in (self.thu_muc / "anh" / "ai").glob("tu-the-chao.*"):
                    cu.unlink()
                tao(self.thu_muc / "anh" / "ai" / ten)
                nguon_ai(self.thu_muc, ("nen-1.jpg", "Imagen 4"), (ten, "Imagen 4"), ("tu-the-buon.png", "Imagen 4"))
                with self.assertRaises(kiem.CanhError) as caught:
                    kiem.kiem(self.video(self.CANH), self.thu_muc)
                self.assertIn("chưa tách nền", str(caught.exception))
                self.assertIn(ten, str(caught.exception))
                self.assertIn("anh_ai.py", caught.exception.fix)

    def test_nen_file_thuong_can_nguon(self):
        png(self.thu_muc / "anh" / "ruong.png", 4, 3, kieu=2)
        video = self.video(ke(1, "ruong.png"), META)
        with self.assertRaises(kiem.CanhError) as caught:
            kiem.kiem(video, self.thu_muc)
        self.assertIn("chưa có nguồn", str(caught.exception))
        self.assertIn(f"dòng {video.canh[0].dong_truong['nen'][0]}", str(caught.exception))
        with self.assertRaises(kiem.CanhError):
            kiem.kiem(self.video(ke(1, "khong-co.jpg"), META), self.thu_muc)


class DongAiCuoiVideoTest(unittest.TestCase):
    def test_dong_ai_gop_mo_hinh(self):
        self.assertEqual(lich.dong_ai(["Imagen 4", "Imagen 4", "GPT Image 1"]),
                         "Hình minh hoạ tạo bằng AI (Imagen 4, GPT Image 1)")

    def test_du_lieu_cuoi_video_hai_dong_ai_o_tren(self):
        with tempfile.TemporaryDirectory() as tmp:
            thu_muc = Path(tmp)
            jpeg(thu_muc / "anh" / "ai" / "nen-1.jpg", 1920, 1080)
            png(thu_muc / "anh" / "ai" / "tu-the-dung.png")
            nguon_ai(thu_muc, ("nen-1.jpg", "Imagen 4"), ("tu-the-dung.png", "Nano Banana"))
            video = parse.parse(f"---\n{META}nhan-vat: ve: cô giáo\n---\n\n" + ke(1, "ve: ruộng") + ke(2, "nhu-canh 1"))
            cac_lich, _ = lich.dung_lich(video.canh, video_ma._giong_tam(video), kiem_moc=False)
            cac_du = video_ma._cac_du(video, cac_lich, {}, thu_muc, {"nguon": "Nhạc: Êm · An · CC0"})
            self.assertNotIn("dongNguon", cac_du[0])
            tu = round(cac_lich[-1].thoi_luong - lich.NGUON_NHAC_GIAY, 3)
            self.assertEqual(cac_du[-1]["dongNguon"], [
                {"chu": "Hình minh hoạ tạo bằng AI (Imagen 4, Nano Banana)", "tu": tu},
                {"chu": "Nhạc: Êm · An · CC0", "tu": tu}])
            # Cảnh 2 dùng lại nền AI của cảnh 1; nhân vật là ảnh có kênh trong suốt.
            self.assertEqual(cac_du[1]["nen"]["dataUrl"], cac_du[0]["nen"]["dataUrl"])
            self.assertEqual(cac_du[1]["nhanVat"]["kieu"], "anh")
            self.assertTrue(cac_du[1]["nhanVat"]["anh"]["dataUrl"].startswith("data:image/png"))
            # Nền AI không có dòng nguồn riêng trong cảnh (đã có dòng AI cuối video).
            self.assertIsNone(cac_du[0]["nen"]["nguon"])

    def test_khong_anh_ai_chi_dong_nhac(self):
        with tempfile.TemporaryDirectory() as tmp:
            video = parse.parse(f"---\n{META}---\n\n" + ke(1, "mau/giay"))
            cac_lich, _ = lich.dung_lich(video.canh, video_ma._giong_tam(video), kiem_moc=False)
            du = video_ma._cac_du(video, cac_lich, {}, Path(tmp), {"nguon": "Nhạc: A"})[-1]
            self.assertEqual([d["chu"] for d in du["dongNguon"]], ["Nhạc: A"])
            self.assertEqual(du["nen"], {"kieu": "mau", "ten": "giay", "hat": 1})
            du = video_ma._cac_du(video, cac_lich, {}, Path(tmp))[-1]
            self.assertNotIn("dongNguon", du)

    def test_nhu_canh_dung_hat_giong_cua_canh_goc(self):
        with tempfile.TemporaryDirectory() as tmp:
            video = parse.parse(f"---\n{META}---\n\n" + ke(1, "mau/giay") + ke(2, "nhu-canh 1") + ke(3, "nhu-canh 2")
                                + ke(4, "mau/giay"))
            cac_lich, _ = lich.dung_lich(video.canh, video_ma._giong_tam(video), kiem_moc=False)
            cac_du = video_ma._cac_du(video, cac_lich, {}, Path(tmp))
            self.assertEqual([d["nen"]["hat"] for d in cac_du], [1, 1, 1, 4])


if __name__ == "__main__":
    unittest.main()
